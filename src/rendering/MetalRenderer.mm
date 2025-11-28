#import "MetalRenderer.h"
#import "Shape2D.h"
#import "Image.h"
#import <Metal/Metal.h>
#import <MetalKit/MetalKit.h>
#import <Cocoa/Cocoa.h>

namespace CyberUI {

// Vertex structure for rectangles
struct Vertex {
    float position[2];
    float color[4];
    float texCoord[2];
};

MetalRenderer::MetalRenderer() 
    : device_(nullptr), commandQueue_(nullptr), pipelineState_(nullptr),
      window_(nullptr), metalView_(nullptr), commandBuffer_(nullptr), renderEncoder_(nullptr),
      initialized_(false), shouldClose_(false) {
}

MetalRenderer::~MetalRenderer() {
    shutdown();
}

bool MetalRenderer::initialize(int width, int height, const char* title) {
    @autoreleasepool {
        // Initialize NSApplication if not already done
        [NSApplication sharedApplication];
        [NSApp setActivationPolicy:NSApplicationActivationPolicyRegular];
        [NSApp activateIgnoringOtherApps:YES];
        
        // Get default Metal device
        id<MTLDevice> device = MTLCreateSystemDefaultDevice();
        if (!device) {
            NSLog(@"Metal is not supported on this device");
            return false;
        }
        device_ = (__bridge_retained void*)device;
        
        // Create command queue
        id<MTLCommandQueue> commandQueue = [device newCommandQueue];
        commandQueue_ = (__bridge_retained void*)commandQueue;
        
        // Create window
        NSRect frame = NSMakeRect(0, 0, width, height);
        NSWindowStyleMask style = NSWindowStyleMaskTitled | 
                                  NSWindowStyleMaskClosable | 
                                  NSWindowStyleMaskResizable;
        
        NSWindow* window = [[NSWindow alloc] initWithContentRect:frame
                                                       styleMask:style
                                                         backing:NSBackingStoreBuffered
                                                           defer:NO];
        [window setTitle:[NSString stringWithUTF8String:title]];
        [window center];
        window_ = (__bridge_retained void*)window;
        
        // Create Metal view
        MTKView* metalView = [[MTKView alloc] initWithFrame:frame device:device];
        [metalView setColorPixelFormat:MTLPixelFormatBGRA8Unorm];
        [metalView setClearColor:MTLClearColorMake(0.1, 0.1, 0.1, 1.0)];
        metalView_ = (__bridge_retained void*)metalView;
        
        [window setContentView:metalView];
        [window makeKeyAndOrderFront:nil];
        
        // Setup shaders
        setupShaders();
        
        initialized_ = true;
        return true;
    }
}

void MetalRenderer::setupShaders() {
    @autoreleasepool {
        id<MTLDevice> device = (__bridge id<MTLDevice>)device_;
        
        NSString* shaderSource = @R"(
            #include <metal_stdlib>
            using namespace metal;
            
            struct Vertex {
                float2 position [[attribute(0)]];
                float4 color [[attribute(1)]];
                float2 texCoord [[attribute(2)]];
            };
            
            struct VertexOut {
                float4 position [[position]];
                float4 color;
                float2 texCoord;
            };
            
            vertex VertexOut vertex_main(Vertex in [[stage_in]]) {
                VertexOut out;
                out.position = float4(in.position, 0.0, 1.0);
                out.color = in.color;
                out.texCoord = in.texCoord;
                return out;
            }
            
            fragment float4 fragment_main(VertexOut in [[stage_in]],
                                         texture2d<float> tex [[texture(0)]],
                                         sampler texSampler [[sampler(0)]]) {
                // Sample texture if available, otherwise use vertex color
                float4 texColor = tex.sample(texSampler, in.texCoord);
                // Multiply texture color by vertex color (allows tinting)
                return texColor * in.color;
            }
        )";
        
        NSError* error = nil;
        id<MTLLibrary> library = [device newLibraryWithSource:shaderSource options:nil error:&error];
        
        if (!library) {
            NSLog(@"Failed to create shader library: %@", error);
            return;
        }
        
        id<MTLFunction> vertexFunc = [library newFunctionWithName:@"vertex_main"];
        id<MTLFunction> fragmentFunc = [library newFunctionWithName:@"fragment_main"];
        
        // Create vertex descriptor
        MTLVertexDescriptor* vertexDesc = [[MTLVertexDescriptor alloc] init];
        // Position
        vertexDesc.attributes[0].format = MTLVertexFormatFloat2;
        vertexDesc.attributes[0].offset = 0;
        vertexDesc.attributes[0].bufferIndex = 0;
        
        // Color
        vertexDesc.attributes[1].format = MTLVertexFormatFloat4;
        vertexDesc.attributes[1].offset = sizeof(float) * 2;
        vertexDesc.attributes[1].bufferIndex = 0;
        
        // TexCoord
        vertexDesc.attributes[2].format = MTLVertexFormatFloat2;
        vertexDesc.attributes[2].offset = sizeof(float) * 6;
        vertexDesc.attributes[2].bufferIndex = 0;
        
        vertexDesc.layouts[0].stride = sizeof(Vertex);
        vertexDesc.layouts[0].stepFunction = MTLVertexStepFunctionPerVertex;
        
        // Create pipeline state
        MTLRenderPipelineDescriptor* pipelineDesc = [[MTLRenderPipelineDescriptor alloc] init];
        pipelineDesc.vertexFunction = vertexFunc;
        pipelineDesc.fragmentFunction = fragmentFunc;
        pipelineDesc.vertexDescriptor = vertexDesc;
        pipelineDesc.colorAttachments[0].pixelFormat = MTLPixelFormatBGRA8Unorm;
        
        // Enable alpha blending for transparency
        pipelineDesc.colorAttachments[0].blendingEnabled = YES;
        pipelineDesc.colorAttachments[0].rgbBlendOperation = MTLBlendOperationAdd;
        pipelineDesc.colorAttachments[0].alphaBlendOperation = MTLBlendOperationAdd;
        pipelineDesc.colorAttachments[0].sourceRGBBlendFactor = MTLBlendFactorSourceAlpha;
        pipelineDesc.colorAttachments[0].sourceAlphaBlendFactor = MTLBlendFactorSourceAlpha;
        pipelineDesc.colorAttachments[0].destinationRGBBlendFactor = MTLBlendFactorOneMinusSourceAlpha;
        pipelineDesc.colorAttachments[0].destinationAlphaBlendFactor = MTLBlendFactorOneMinusSourceAlpha;
        
        id<MTLRenderPipelineState> pipelineState = [device 
            newRenderPipelineStateWithDescriptor:pipelineDesc error:&error];
        
        if (!pipelineState) {
            NSLog(@"Failed to create pipeline state: %@", error);
        }
        pipelineState_ = (__bridge_retained void*)pipelineState;
    }
}

void MetalRenderer::shutdown() {
    if (initialized_) {
        @autoreleasepool {
            if (window_) {
                NSWindow* window = (__bridge_transfer NSWindow*)window_;
                [window close];
                window_ = nullptr;
            }
            if (metalView_) {
                (void)(__bridge_transfer MTKView*)metalView_;
                metalView_ = nullptr;
            }
            if (pipelineState_) {
                (void)(__bridge_transfer id<MTLRenderPipelineState>)pipelineState_;
                pipelineState_ = nullptr;
            }
            if (commandQueue_) {
                (void)(__bridge_transfer id<MTLCommandQueue>)commandQueue_;
                commandQueue_ = nullptr;
            }
            if (device_) {
                (void)(__bridge_transfer id<MTLDevice>)device_;
                device_ = nullptr;
            }
        }
        initialized_ = false;
    }
}

bool MetalRenderer::beginFrame() {
    if (!initialized_) return false;
    
    @autoreleasepool {
        id<MTLCommandQueue> commandQueue = (__bridge id<MTLCommandQueue>)commandQueue_;
        id<MTLCommandBuffer> commandBuffer = [commandQueue commandBuffer];
        commandBuffer_ = (__bridge_retained void*)commandBuffer;
        
        MTKView* view = (__bridge MTKView*)metalView_;
        MTLRenderPassDescriptor* passDesc = [view currentRenderPassDescriptor];
        
        if (!passDesc) return false;
        
        id<MTLRenderCommandEncoder> renderEncoder = [commandBuffer 
            renderCommandEncoderWithDescriptor:passDesc];
        renderEncoder_ = (__bridge_retained void*)renderEncoder;
        
        id<MTLRenderPipelineState> pipelineState = (__bridge id<MTLRenderPipelineState>)pipelineState_;
        [renderEncoder setRenderPipelineState:pipelineState];
        
        return true;
    }
}

void MetalRenderer::endFrame() {
    @autoreleasepool {
        id<MTLRenderCommandEncoder> renderEncoder = (__bridge_transfer id<MTLRenderCommandEncoder>)renderEncoder_;
        [renderEncoder endEncoding];
        renderEncoder_ = nullptr;
        
        MTKView* view = (__bridge MTKView*)metalView_;
        id<MTLCommandBuffer> commandBuffer = (__bridge_transfer id<MTLCommandBuffer>)commandBuffer_;
        [commandBuffer presentDrawable:[view currentDrawable]];
        [commandBuffer commit];
        commandBuffer_ = nullptr;
    }
}

void MetalRenderer::renderObject(Object3D* object) {
    if (!object || !object->isVisible()) return;
    
    // Check if it's a Rectangle
    Rectangle* rect = dynamic_cast<Rectangle*>(object);
    if (rect) {
        renderRectangle(rect);
    }
    
    // Render children
    for (const auto& child : object->getChildren()) {
        renderObject(child.get());
    }
}

void MetalRenderer::renderRectangle(Rectangle* rect) {
    @autoreleasepool {
        float x, y, z;
        rect->getPosition(x, y, z);
        
        float width, height;
        rect->getSize(width, height);
        
        float r, g, b, a;
        rect->getColor(r, g, b, a);
        
        // Get view dimensions for normalization
        MTKView* view = (__bridge MTKView*)metalView_;
        float viewWidth = view.bounds.size.width;
        float viewHeight = view.bounds.size.height;
        
        // Convert to normalized device coordinates (-1 to 1)
        float x1 = (x / viewWidth) * 2.0f - 1.0f;
        float y1 = 1.0f - (y / viewHeight) * 2.0f;
        float x2 = ((x + width) / viewWidth) * 2.0f - 1.0f;
        float y2 = 1.0f - ((y + height) / viewHeight) * 2.0f;
        
        // Create vertices for rectangle (2 triangles) with texture coordinates
        Vertex vertices[] = {
            {{x1, y1}, {r, g, b, a}, {0.0f, 0.0f}},  // Top-left
            {{x2, y1}, {r, g, b, a}, {1.0f, 0.0f}},  // Top-right
            {{x1, y2}, {r, g, b, a}, {0.0f, 1.0f}},  // Bottom-left
            {{x2, y1}, {r, g, b, a}, {1.0f, 0.0f}},  // Top-right
            {{x2, y2}, {r, g, b, a}, {1.0f, 1.0f}},  // Bottom-right
            {{x1, y2}, {r, g, b, a}, {0.0f, 1.0f}},  // Bottom-left
        };
        
        // Create vertex buffer
        id<MTLDevice> device = (__bridge id<MTLDevice>)device_;
        id<MTLBuffer> vertexBuffer = [device 
            newBufferWithBytes:vertices 
            length:sizeof(vertices) 
            options:MTLResourceStorageModeShared];
        
        id<MTLRenderCommandEncoder> renderEncoder = (__bridge id<MTLRenderCommandEncoder>)renderEncoder_;
        [renderEncoder setVertexBuffer:vertexBuffer offset:0 atIndex:0];
        
        // Check if rectangle has a texture
        if (rect->hasImage()) {
            auto image = rect->getImage();
            if (image && image->isLoaded()) {
                // Create Metal texture from image data
                MTLTextureDescriptor* texDesc = [MTLTextureDescriptor 
                    texture2DDescriptorWithPixelFormat:MTLPixelFormatRGBA8Unorm
                    width:image->getWidth()
                    height:image->getHeight()
                    mipmapped:NO];
                texDesc.usage = MTLTextureUsageShaderRead;
                
                id<MTLTexture> texture = [device newTextureWithDescriptor:texDesc];
                
                // Upload image data to texture
                MTLRegion region = MTLRegionMake2D(0, 0, image->getWidth(), image->getHeight());
                NSUInteger bytesPerRow = 4 * image->getWidth();
                [texture replaceRegion:region
                           mipmapLevel:0
                             withBytes:image->getData()
                           bytesPerRow:bytesPerRow];
                
                // Create sampler
                MTLSamplerDescriptor* samplerDesc = [[MTLSamplerDescriptor alloc] init];
                samplerDesc.minFilter = MTLSamplerMinMagFilterLinear;
                samplerDesc.magFilter = MTLSamplerMinMagFilterLinear;
                samplerDesc.sAddressMode = MTLSamplerAddressModeClampToEdge;
                samplerDesc.tAddressMode = MTLSamplerAddressModeClampToEdge;
                id<MTLSamplerState> sampler = [device newSamplerStateWithDescriptor:samplerDesc];
                
                // Bind texture and sampler
                [renderEncoder setFragmentTexture:texture atIndex:0];
                [renderEncoder setFragmentSamplerState:sampler atIndex:0];
            }
        } else {
            // No texture - create a white 1x1 texture so shader works
            MTLTextureDescriptor* texDesc = [MTLTextureDescriptor 
                texture2DDescriptorWithPixelFormat:MTLPixelFormatRGBA8Unorm
                width:1
                height:1
                mipmapped:NO];
            texDesc.usage = MTLTextureUsageShaderRead;
            
            id<MTLTexture> texture = [device newTextureWithDescriptor:texDesc];
            uint8_t whitePixel[4] = {255, 255, 255, 255};
            MTLRegion region = MTLRegionMake2D(0, 0, 1, 1);
            [texture replaceRegion:region mipmapLevel:0 withBytes:whitePixel bytesPerRow:4];
            
            MTLSamplerDescriptor* samplerDesc = [[MTLSamplerDescriptor alloc] init];
            samplerDesc.minFilter = MTLSamplerMinMagFilterLinear;
            samplerDesc.magFilter = MTLSamplerMinMagFilterLinear;
            id<MTLSamplerState> sampler = [device newSamplerStateWithDescriptor:samplerDesc];
            
            [renderEncoder setFragmentTexture:texture atIndex:0];
            [renderEncoder setFragmentSamplerState:sampler atIndex:0];
        }
        
        // Draw
        [renderEncoder drawPrimitives:MTLPrimitiveTypeTriangle vertexStart:0 vertexCount:6];
    }
}

bool MetalRenderer::shouldClose() {
    return shouldClose_;
}

void MetalRenderer::pollEvents() {
    @autoreleasepool {
        NSEvent* event;
        while ((event = [NSApp nextEventMatchingMask:NSEventMaskAny
                                          untilDate:nil
                                             inMode:NSDefaultRunLoopMode
                                            dequeue:YES])) {
            if (event.type == NSEventTypeKeyDown && event.keyCode == 53) { // ESC key
                shouldClose_ = true;
            }
            [NSApp sendEvent:event];
        }
        
        // Check if window was closed
        NSWindow* window = (__bridge NSWindow*)window_;
        if (![window isVisible]) {
            shouldClose_ = true;
        }
    }
}

} // namespace CyberUI

// Factory function implementation
namespace CyberUI {
std::unique_ptr<Renderer> createMetalRenderer() {
    return std::make_unique<MetalRenderer>();
}
}
