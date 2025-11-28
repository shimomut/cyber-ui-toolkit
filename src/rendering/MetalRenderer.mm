#import "MetalRenderer.h"
#import "Shape2D.h"
#import "Image.h"
#import "../core/SceneRoot.h"
#import "../core/Frame3D.h"
#import "../core/Camera.h"
#import <Metal/Metal.h>
#import <MetalKit/MetalKit.h>
#import <Cocoa/Cocoa.h>
#import <cmath>

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
      initialized_(false), shouldClose_(false), windowWidth_(800), windowHeight_(600) {
}

MetalRenderer::~MetalRenderer() {
    shutdown();
}

bool MetalRenderer::initialize(int width, int height, const char* title) {
    windowWidth_ = width;
    windowHeight_ = height;
    
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
        [metalView setDepthStencilPixelFormat:MTLPixelFormatDepth32Float];
        [metalView setClearColor:MTLClearColorMake(0.1, 0.1, 0.1, 1.0)];
        [metalView setClearDepth:1.0];
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
            
            struct Uniforms {
                float4x4 mvpMatrix;
            };
            
            struct VertexOut {
                float4 position [[position]];
                float4 color;
                float2 texCoord;
            };
            
            vertex VertexOut vertex_main(Vertex in [[stage_in]],
                                         constant Uniforms& uniforms [[buffer(1)]]) {
                VertexOut out;
                // Transform 2D position to 3D (z=0) and apply MVP matrix
                float4 pos3D = float4(in.position.x, in.position.y, 0.0, 1.0);
                out.position = uniforms.mvpMatrix * pos3D;
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

void MetalRenderer::renderObject(Object2D* object) {
    if (!object || !object->isVisible()) return;
    
    // Legacy rendering - create identity MVP matrix for 2D rendering
    float identityMatrix[16] = {
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, 0, 1
    };
    
    // Convert to NDC space
    float viewWidth = windowWidth_;
    float viewHeight = windowHeight_;
    
    float scaleX = 2.0f / viewWidth;
    float scaleY = -2.0f / viewHeight;
    
    float orthoMatrix[16] = {
        scaleX, 0, 0, 0,
        0, scaleY, 0, 0,
        0, 0, 1, 0,
        -1, 1, 0, 1
    };
    
    renderObject2D(object, orthoMatrix);
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

void MetalRenderer::renderScene(SceneRoot* scene) {
    if (!scene) return;
    
    auto camera = scene->getCamera();
    if (!camera) return;
    
    // Get view and projection matrices
    float viewMatrix[16];
    float projMatrix[16];
    camera->getViewMatrix(viewMatrix);
    camera->getProjectionMatrix(projMatrix);
    
    // Combine view and projection
    float viewProjMatrix[16];
    multiplyMatrices(projMatrix, viewMatrix, viewProjMatrix);
    
    // Render all Frame3D objects
    for (const auto& frame : scene->getFrames()) {
        renderFrame3D(frame.get(), viewProjMatrix);
    }
}

void MetalRenderer::renderFrame3D(Frame3D* frame, const float* viewProjMatrix) {
    if (!frame || !frame->isVisible()) return;
    
    // Get Frame3D transform
    float pos[3], rot[3], scale[3];
    frame->getPosition(pos[0], pos[1], pos[2]);
    frame->getRotation(rot[0], rot[1], rot[2]);
    frame->getScale(scale[0], scale[1], scale[2]);
    
    // Create model matrix for this Frame3D
    float modelMatrix[16];
    createTransformMatrix(pos[0], pos[1], pos[2], 
                         rot[0], rot[1], rot[2],
                         scale[0], scale[1], scale[2],
                         modelMatrix);
    
    // Combine with view-projection
    float mvpMatrix[16];
    multiplyMatrices(viewProjMatrix, modelMatrix, mvpMatrix);
    
    // Render all 2D children with this MVP matrix
    for (const auto& child : frame->getChildren()) {
        renderObject2D(child.get(), mvpMatrix);
    }
}

void MetalRenderer::renderObject2D(Object2D* object, const float* mvpMatrix) {
    if (!object || !object->isVisible()) return;
    
    // Get 2D position and create translation matrix
    float x, y;
    object->getPosition(x, y);
    
    float translationMatrix[16] = {
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        x, y, 0, 1
    };
    
    // Combine with parent MVP
    float objectMVP[16];
    multiplyMatrices(mvpMatrix, translationMatrix, objectMVP);
    
    // Check if it's a Rectangle
    Rectangle* rect = dynamic_cast<Rectangle*>(object);
    if (rect) {
        renderRectangle(rect, objectMVP);
    }
    
    // Render children
    for (const auto& child : object->getChildren()) {
        renderObject2D(child.get(), objectMVP);
    }
}

void MetalRenderer::renderRectangle(Rectangle* rect, const float* mvpMatrix) {
    @autoreleasepool {
        float width, height;
        rect->getSize(width, height);
        
        float r, g, b, a;
        rect->getColor(r, g, b, a);
        
        // Create vertices in local space (centered at origin for proper rotation)
        float hw = width * 0.5f;
        float hh = height * 0.5f;
        
        Vertex vertices[] = {
            {{-hw, -hh}, {r, g, b, a}, {0.0f, 0.0f}},  // Top-left
            {{ hw, -hh}, {r, g, b, a}, {1.0f, 0.0f}},  // Top-right
            {{-hw,  hh}, {r, g, b, a}, {0.0f, 1.0f}},  // Bottom-left
            {{ hw, -hh}, {r, g, b, a}, {1.0f, 0.0f}},  // Top-right
            {{ hw,  hh}, {r, g, b, a}, {1.0f, 1.0f}},  // Bottom-right
            {{-hw,  hh}, {r, g, b, a}, {0.0f, 1.0f}},  // Bottom-left
        };
        
        // Create vertex buffer
        id<MTLDevice> device = (__bridge id<MTLDevice>)device_;
        id<MTLBuffer> vertexBuffer = [device 
            newBufferWithBytes:vertices 
            length:sizeof(vertices) 
            options:MTLResourceStorageModeShared];
        
        // Create uniform buffer with MVP matrix
        id<MTLBuffer> uniformBuffer = [device
            newBufferWithBytes:mvpMatrix
            length:sizeof(float) * 16
            options:MTLResourceStorageModeShared];
        
        id<MTLRenderCommandEncoder> renderEncoder = (__bridge id<MTLRenderCommandEncoder>)renderEncoder_;
        [renderEncoder setVertexBuffer:vertexBuffer offset:0 atIndex:0];
        [renderEncoder setVertexBuffer:uniformBuffer offset:0 atIndex:1];
        
        // Handle texture (same as before)
        if (rect->hasImage()) {
            auto image = rect->getImage();
            if (image && image->isLoaded()) {
                MTLTextureDescriptor* texDesc = [MTLTextureDescriptor 
                    texture2DDescriptorWithPixelFormat:MTLPixelFormatRGBA8Unorm
                    width:image->getWidth()
                    height:image->getHeight()
                    mipmapped:NO];
                texDesc.usage = MTLTextureUsageShaderRead;
                
                id<MTLTexture> texture = [device newTextureWithDescriptor:texDesc];
                
                MTLRegion region = MTLRegionMake2D(0, 0, image->getWidth(), image->getHeight());
                NSUInteger bytesPerRow = 4 * image->getWidth();
                [texture replaceRegion:region
                           mipmapLevel:0
                             withBytes:image->getData()
                           bytesPerRow:bytesPerRow];
                
                MTLSamplerDescriptor* samplerDesc = [[MTLSamplerDescriptor alloc] init];
                samplerDesc.minFilter = MTLSamplerMinMagFilterLinear;
                samplerDesc.magFilter = MTLSamplerMinMagFilterLinear;
                samplerDesc.sAddressMode = MTLSamplerAddressModeClampToEdge;
                samplerDesc.tAddressMode = MTLSamplerAddressModeClampToEdge;
                id<MTLSamplerState> sampler = [device newSamplerStateWithDescriptor:samplerDesc];
                
                [renderEncoder setFragmentTexture:texture atIndex:0];
                [renderEncoder setFragmentSamplerState:sampler atIndex:0];
            }
        } else {
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
        
        [renderEncoder drawPrimitives:MTLPrimitiveTypeTriangle vertexStart:0 vertexCount:6];
    }
}

void MetalRenderer::multiplyMatrices(const float* a, const float* b, float* result) {
    for (int row = 0; row < 4; row++) {
        for (int col = 0; col < 4; col++) {
            result[row + col * 4] = 0;
            for (int k = 0; k < 4; k++) {
                result[row + col * 4] += a[row + k * 4] * b[k + col * 4];
            }
        }
    }
}

void MetalRenderer::createTransformMatrix(float x, float y, float z,
                                         float pitch, float yaw, float roll,
                                         float scaleX, float scaleY, float scaleZ,
                                         float* matrix) {
    float cp = std::cos(pitch);
    float sp = std::sin(pitch);
    float cy = std::cos(yaw);
    float sy = std::sin(yaw);
    float cr = std::cos(roll);
    float sr = std::sin(roll);
    
    // Combined rotation and scale matrix (column-major)
    matrix[0] = scaleX * (cy * cr);
    matrix[1] = scaleX * (cy * sr);
    matrix[2] = scaleX * (-sy);
    matrix[3] = 0;
    
    matrix[4] = scaleY * (sp * sy * cr - cp * sr);
    matrix[5] = scaleY * (sp * sy * sr + cp * cr);
    matrix[6] = scaleY * (sp * cy);
    matrix[7] = 0;
    
    matrix[8] = scaleZ * (cp * sy * cr + sp * sr);
    matrix[9] = scaleZ * (cp * sy * sr - sp * cr);
    matrix[10] = scaleZ * (cp * cy);
    matrix[11] = 0;
    
    matrix[12] = x;
    matrix[13] = y;
    matrix[14] = z;
    matrix[15] = 1;
}

} // namespace CyberUI

// Factory function implementation
namespace CyberUI {
std::unique_ptr<Renderer> createMetalRenderer() {
    return std::make_unique<MetalRenderer>();
}
}
