#import "MetalRenderer.h"
#import "Shape2D.h"
#import "Image.h"
#import "Text.h"
#import "../core/SceneRoot.h"
#import "../core/Frame3D.h"
#import "../core/Frame2D.h"
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
      initialized_(false), shouldClose_(false), windowWidth_(800), windowHeight_(600),
      newTexturesCreatedThisFrame_(false),
      currentRenderTargetWidth_(0), currentRenderTargetHeight_(0) {
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
            // Clean up texture cache
            for (auto& pair : textureCache_) {
                if (pair.second) {
                    (void)(__bridge_transfer id<MTLTexture>)pair.second;
                }
            }
            textureCache_.clear();
            
            for (auto& pair : textTextureCache_) {
                if (pair.second) {
                    (void)(__bridge_transfer id<MTLTexture>)pair.second;
                }
            }
            textTextureCache_.clear();
            
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
    
    // Reset texture creation flag for this frame
    newTexturesCreatedThisFrame_ = false;
    
    // Clear scissor stack for new frame
    scissorStack_.clear();
    
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
        
        // Get actual drawable size (accounts for Retina scaling)
        CGSize drawableSize = [view drawableSize];
        
        // Set viewport to match drawable size
        MTLViewport viewport;
        viewport.originX = 0.0;
        viewport.originY = 0.0;
        viewport.width = drawableSize.width;
        viewport.height = drawableSize.height;
        viewport.znear = 0.0;
        viewport.zfar = 1.0;
        [renderEncoder setViewport:viewport];
        
        // Set initial scissor rect to full viewport
        MTLScissorRect scissor;
        scissor.x = 0;
        scissor.y = 0;
        scissor.width = drawableSize.width;
        scissor.height = drawableSize.height;
        [renderEncoder setScissorRect:scissor];
        
        // Store current render target dimensions for scissor rect calculations
        currentRenderTargetWidth_ = static_cast<int>(drawableSize.width);
        currentRenderTargetHeight_ = static_cast<int>(drawableSize.height);
        
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
        
        // CRITICAL: Only wait for GPU if new textures were created this frame
        // This prevents textures from being deallocated while GPU is still using them.
        // Cached textures don't need synchronization since they persist across frames.
        if (newTexturesCreatedThisFrame_) {
            [commandBuffer waitUntilCompleted];
        }
        
        commandBuffer_ = nullptr;
    }
}

void MetalRenderer::renderObject(Object2D* object) {
    if (!object || !object->isVisible()) return;
    
    // Convert to NDC space using drawable size (accounts for Retina scaling)
    @autoreleasepool {
        MTKView* view = (__bridge MTKView*)metalView_;
        CGSize drawableSize = [view drawableSize];
        
        float viewWidth = drawableSize.width;
        float viewHeight = drawableSize.height;
        
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
    
    // Check if off-screen rendering is enabled
    if (frame->isOffscreenRenderingEnabled()) {
        // First, render Frame3D content to texture (with proper clipping in 2D space)
        renderFrame3DToTexture(frame);
        
        // Then render the texture as a quad with 3D transforms
        void* texture = frame->getRenderTargetTexture();
        if (texture) {
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
            
            // Get render target size
            int rtWidth, rtHeight;
            frame->getRenderTargetSize(rtWidth, rtHeight);
            
            // Render the texture as a quad
            renderTexturedQuad(texture, rtWidth, rtHeight, mvpMatrix);
        }
    } else {
        // Direct rendering (old path)
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
    
    // Check if it's a Frame2D (needs to be checked before Rectangle since Frame2D inherits from Object2D)
    Frame2D* frame2d = dynamic_cast<Frame2D*>(object);
    if (frame2d) {
        float width, height;
        frame2d->getSize(width, height);
        
        // Frame2D position is already top-left origin (Object2D coordinate system)
        // We only need to set up the coordinate system for children:
        // - Y-axis flip (Y+ down for 2D UI)
        // - Origin at (0, 0) = Frame2D's top-left corner
        float offsetMatrix[16] = {
            1, 0, 0, 0,
            0, -1, 0, 0,  // Flip Y-axis: Y+ down for 2D UI
            0, 0, 1, 0,
            0, height, 0, 1  // Move origin to top-left with Y-flip
        };
        
        // Combine with Frame2D's MVP
        float frame2dMVP[16];
        multiplyMatrices(objectMVP, offsetMatrix, frame2dMVP);
        
        // Handle clipping for Frame2D
        bool hasClipping = frame2d->isClippingEnabled();
        
        if (hasClipping) {
            // Clipping rect in top-left origin coordinates (0, 0) to (width, height)
            pushScissorRect(0, 0, width, height, frame2dMVP);
        }
        
        // Render Frame2D children with top-left origin coordinate system
        // Child at (0, 0) will be at Frame2D's top-left corner
        // Child at (width, height) will be at Frame2D's bottom-right corner
        for (const auto& child : frame2d->getChildren()) {
            renderObject2D(child.get(), frame2dMVP);
        }
        
        if (hasClipping) {
            popScissorRect();
        }
        
        return;  // Frame2D handled, don't process as regular object
    }
    
    // Check if it's a Rectangle
    Rectangle* rect = dynamic_cast<Rectangle*>(object);
    if (rect) {
        renderRectangle(rect, objectMVP);
    }
    
    // Check if it's a Text
    Text* text = dynamic_cast<Text*>(object);
    if (text) {
        renderText(text, objectMVP);
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
        
        // Create vertices with top-left origin (position refers to top-left corner)
        // This matches the Object2D coordinate system: "Origin at top-left of parent"
        Vertex vertices[] = {
            {{0.0f, 0.0f}, {r, g, b, a}, {0.0f, 1.0f}},      // Top-left (flip V)
            {{width, 0.0f}, {r, g, b, a}, {1.0f, 1.0f}},     // Top-right (flip V)
            {{0.0f, height}, {r, g, b, a}, {0.0f, 0.0f}},    // Bottom-left (flip V)
            {{width, 0.0f}, {r, g, b, a}, {1.0f, 1.0f}},     // Top-right (flip V)
            {{width, height}, {r, g, b, a}, {1.0f, 0.0f}},   // Bottom-right (flip V)
            {{0.0f, height}, {r, g, b, a}, {0.0f, 0.0f}},    // Bottom-left (flip V)
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
        
        // Handle texture with caching
        id<MTLTexture> texture = nil;
        if (rect->hasImage()) {
            auto image = rect->getImage();
            if (image && image->isLoaded()) {
                texture = (__bridge id<MTLTexture>)getOrCreateTexture(image.get());
            }
        }
        
        if (!texture) {
            // Use white 1x1 texture for non-textured rectangles
            static void* whiteTexture = nullptr;
            if (!whiteTexture) {
                MTLTextureDescriptor* texDesc = [MTLTextureDescriptor 
                    texture2DDescriptorWithPixelFormat:MTLPixelFormatRGBA8Unorm
                    width:1
                    height:1
                    mipmapped:NO];
                texDesc.usage = MTLTextureUsageShaderRead;
                texDesc.storageMode = MTLStorageModeShared;
                
                id<MTLTexture> tex = [device newTextureWithDescriptor:texDesc];
                uint8_t whitePixel[4] = {255, 255, 255, 255};
                MTLRegion region = MTLRegionMake2D(0, 0, 1, 1);
                [tex replaceRegion:region mipmapLevel:0 withBytes:whitePixel bytesPerRow:4];
                whiteTexture = (__bridge_retained void*)tex;
            }
            texture = (__bridge id<MTLTexture>)whiteTexture;
        }
        
        MTLSamplerDescriptor* samplerDesc = [[MTLSamplerDescriptor alloc] init];
        samplerDesc.minFilter = MTLSamplerMinMagFilterLinear;
        samplerDesc.magFilter = MTLSamplerMinMagFilterLinear;
        samplerDesc.sAddressMode = MTLSamplerAddressModeClampToEdge;
        samplerDesc.tAddressMode = MTLSamplerAddressModeClampToEdge;
        id<MTLSamplerState> sampler = [device newSamplerStateWithDescriptor:samplerDesc];
        
        [renderEncoder setFragmentTexture:texture atIndex:0];
        [renderEncoder setFragmentSamplerState:sampler atIndex:0];
        
        [renderEncoder drawPrimitives:MTLPrimitiveTypeTriangle vertexStart:0 vertexCount:6];
    }
}

void MetalRenderer::renderText(Text* text, const float* mvpMatrix) {
    @autoreleasepool {
        float r, g, b, a;
        text->getColor(r, g, b, a);
        
        float fontSize = 24.0f;
        bool isBold = false;
        if (text->hasFont()) {
            fontSize = text->getFont()->getSize();
            isBold = text->getFont()->isBold();
        }
        
        // Scale font size for Retina displays
        MTKView* view = (__bridge MTKView*)metalView_;
        CGFloat scaleFactor = [view.window backingScaleFactor];
        if (scaleFactor <= 0) scaleFactor = 2.0;  // Default to 2x if window not available
        float renderFontSize = fontSize * scaleFactor;
        
        std::string textStr = text->getText();
        if (textStr.empty()) return;
        
        // Create cache key (include scale factor to cache different resolutions)
        std::string cacheKey = textStr + "|" + std::to_string(renderFontSize) + "|" + (isBold ? "B" : "R");
        
        // Check cache
        id<MTLTexture> texture = nil;
        int width = 0, height = 0;
        
        auto it = textTextureCache_.find(cacheKey);
        if (it != textTextureCache_.end()) {
            texture = (__bridge id<MTLTexture>)it->second;
            width = texture.width;
            height = texture.height;
        } else {
            // Generate new texture
            NSString* nsText = [NSString stringWithUTF8String:textStr.c_str()];
            
            // Create font at scaled size for Retina rendering
            NSFont* font = isBold ? [NSFont boldSystemFontOfSize:renderFontSize] : [NSFont systemFontOfSize:renderFontSize];
            
            // Calculate text size
            NSDictionary* attributes = @{NSFontAttributeName: font};
            NSSize textSize = [nsText sizeWithAttributes:attributes];
            
            width = (int)ceil(textSize.width) + 4;  // Add padding
            height = (int)ceil(textSize.height) + 4;
            
            if (width <= 0 || height <= 0) return;
            
            // Create bitmap context with premultiplied alpha
            CGColorSpaceRef colorSpace = CGColorSpaceCreateDeviceRGB();
            unsigned char* bitmapData = (unsigned char*)calloc(width * height * 4, sizeof(unsigned char));
            CGContextRef context = CGBitmapContextCreate(bitmapData, width, height, 8, width * 4,
                                                         colorSpace, kCGImageAlphaPremultipliedLast);
            
            // Clear to transparent
            CGContextClearRect(context, CGRectMake(0, 0, width, height));
            
            // Flip context for correct text orientation
            CGContextTranslateCTM(context, 0, height);
            CGContextScaleCTM(context, 1.0, -1.0);
            
            // Draw text in white (will be tinted by vertex color in shader)
            NSGraphicsContext* nsContext = [NSGraphicsContext graphicsContextWithCGContext:context flipped:NO];
            [NSGraphicsContext saveGraphicsState];
            [NSGraphicsContext setCurrentContext:nsContext];
            
            NSDictionary* drawAttributes = @{
                NSFontAttributeName: font,
                NSForegroundColorAttributeName: [NSColor whiteColor]
            };
            
            [nsText drawAtPoint:NSMakePoint(2, 2) withAttributes:drawAttributes];
            
            [NSGraphicsContext restoreGraphicsState];
            
            // Create Metal texture from bitmap
            id<MTLDevice> device = (__bridge id<MTLDevice>)device_;
            MTLTextureDescriptor* texDesc = [MTLTextureDescriptor 
                texture2DDescriptorWithPixelFormat:MTLPixelFormatRGBA8Unorm
                width:width
                height:height
                mipmapped:NO];
            texDesc.usage = MTLTextureUsageShaderRead;
            texDesc.storageMode = MTLStorageModeShared;
            
            texture = [device newTextureWithDescriptor:texDesc];
            MTLRegion region = MTLRegionMake2D(0, 0, width, height);
            [texture replaceRegion:region mipmapLevel:0 withBytes:bitmapData bytesPerRow:width * 4];
            
            // Cleanup bitmap
            CGContextRelease(context);
            CGColorSpaceRelease(colorSpace);
            free(bitmapData);
            
            // Cache the texture
            void* texturePtr = (__bridge_retained void*)texture;
            textTextureCache_[cacheKey] = texturePtr;
            
            // Mark that we created a new texture this frame
            newTexturesCreatedThisFrame_ = true;
        }
        
        // Create vertices for text quad with top-left origin
        // Texture is at Retina resolution, but we want logical size for rendering
        // The texture width/height are already in pixels, so we need to scale to logical points
        // Position refers to top-left corner (matches Object2D coordinate system)
        float logicalWidth = width / scaleFactor;
        float logicalHeight = height / scaleFactor;
        
        Vertex vertices[] = {
            {{0.0f, 0.0f}, {r, g, b, a}, {0.0f, 1.0f}},                    // Top-left (flip V)
            {{logicalWidth, 0.0f}, {r, g, b, a}, {1.0f, 1.0f}},            // Top-right (flip V)
            {{0.0f, logicalHeight}, {r, g, b, a}, {0.0f, 0.0f}},           // Bottom-left (flip V)
            {{logicalWidth, 0.0f}, {r, g, b, a}, {1.0f, 1.0f}},            // Top-right (flip V)
            {{logicalWidth, logicalHeight}, {r, g, b, a}, {1.0f, 0.0f}},   // Bottom-right (flip V)
            {{0.0f, logicalHeight}, {r, g, b, a}, {0.0f, 0.0f}},           // Bottom-left (flip V)
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
        
        // Set texture and sampler
        MTLSamplerDescriptor* samplerDesc = [[MTLSamplerDescriptor alloc] init];
        samplerDesc.minFilter = MTLSamplerMinMagFilterLinear;
        samplerDesc.magFilter = MTLSamplerMinMagFilterLinear;
        samplerDesc.sAddressMode = MTLSamplerAddressModeClampToEdge;
        samplerDesc.tAddressMode = MTLSamplerAddressModeClampToEdge;
        id<MTLSamplerState> sampler = [device newSamplerStateWithDescriptor:samplerDesc];
        
        [renderEncoder setFragmentTexture:texture atIndex:0];
        [renderEncoder setFragmentSamplerState:sampler atIndex:0];
        
        [renderEncoder drawPrimitives:MTLPrimitiveTypeTriangle vertexStart:0 vertexCount:6];
    }
}

void* MetalRenderer::getOrCreateTexture(Image* image) {
    if (!image || !image->isLoaded()) return nullptr;
    
    // Check cache first
    auto it = textureCache_.find(image);
    if (it != textureCache_.end()) {
        return it->second;
    }
    
    // Mark that we're creating a new texture this frame
    newTexturesCreatedThisFrame_ = true;
    
    // Create new texture
    @autoreleasepool {
        id<MTLDevice> device = (__bridge id<MTLDevice>)device_;
        MTLTextureDescriptor* texDesc = [MTLTextureDescriptor 
            texture2DDescriptorWithPixelFormat:MTLPixelFormatRGBA8Unorm
            width:image->getWidth()
            height:image->getHeight()
            mipmapped:NO];
        texDesc.usage = MTLTextureUsageShaderRead;
        texDesc.storageMode = MTLStorageModeShared;
        
        id<MTLTexture> texture = [device newTextureWithDescriptor:texDesc];
        
        MTLRegion region = MTLRegionMake2D(0, 0, image->getWidth(), image->getHeight());
        NSUInteger bytesPerRow = 4 * image->getWidth();
        [texture replaceRegion:region
                   mipmapLevel:0
                     withBytes:image->getData()
                   bytesPerRow:bytesPerRow];
        
        void* texturePtr = (__bridge_retained void*)texture;
        textureCache_[image] = texturePtr;
        return texturePtr;
    }
}

void* MetalRenderer::getOrCreateRenderTarget(Frame3D* frame) {
    if (!frame) return nullptr;
    
    // Check cache first
    auto it = renderTargetCache_.find(frame);
    if (it != renderTargetCache_.end()) {
        return it->second;
    }
    
    // Create new render target texture
    @autoreleasepool {
        id<MTLDevice> device = (__bridge id<MTLDevice>)device_;
        
        int width, height;
        frame->getRenderTargetSize(width, height);
        
        MTLTextureDescriptor* texDesc = [MTLTextureDescriptor 
            texture2DDescriptorWithPixelFormat:MTLPixelFormatBGRA8Unorm
            width:width
            height:height
            mipmapped:NO];
        texDesc.usage = MTLTextureUsageRenderTarget | MTLTextureUsageShaderRead;
        texDesc.storageMode = MTLStorageModePrivate;
        
        id<MTLTexture> texture = [device newTextureWithDescriptor:texDesc];
        
        void* texturePtr = (__bridge_retained void*)texture;
        renderTargetCache_[frame] = texturePtr;
        frame->setRenderTargetTexture(texturePtr);
        return texturePtr;
    }
}

void MetalRenderer::renderFrame3DToTexture(Frame3D* frame) {
    if (!frame) return;
    
    @autoreleasepool {
        id<MTLCommandQueue> commandQueue = (__bridge id<MTLCommandQueue>)commandQueue_;
        
        // Get or create render target
        void* renderTarget = getOrCreateRenderTarget(frame);
        if (!renderTarget) return;
        
        id<MTLTexture> targetTexture = (__bridge id<MTLTexture>)renderTarget;
        
        // Create render pass descriptor for off-screen rendering
        MTLRenderPassDescriptor* renderPassDesc = [MTLRenderPassDescriptor renderPassDescriptor];
        renderPassDesc.colorAttachments[0].texture = targetTexture;
        renderPassDesc.colorAttachments[0].loadAction = MTLLoadActionClear;
        renderPassDesc.colorAttachments[0].storeAction = MTLStoreActionStore;
        renderPassDesc.colorAttachments[0].clearColor = MTLClearColorMake(0.0, 0.0, 0.0, 0.0);  // Transparent
        
        // Create command buffer for off-screen rendering
        id<MTLCommandBuffer> offscreenCommandBuffer = [commandQueue commandBuffer];
        id<MTLRenderCommandEncoder> offscreenEncoder = [offscreenCommandBuffer renderCommandEncoderWithDescriptor:renderPassDesc];
        
        // Set pipeline state
        id<MTLRenderPipelineState> pipelineState = (__bridge id<MTLRenderPipelineState>)pipelineState_;
        [offscreenEncoder setRenderPipelineState:pipelineState];
        
        // Store current encoder, command buffer, and render target dimensions
        void* savedEncoder = renderEncoder_;
        void* savedCommandBuffer = commandBuffer_;
        int savedRenderTargetWidth = currentRenderTargetWidth_;
        int savedRenderTargetHeight = currentRenderTargetHeight_;
        
        // Get render target size
        int rtWidth, rtHeight;
        frame->getRenderTargetSize(rtWidth, rtHeight);
        
        // Use off-screen encoder and dimensions temporarily
        renderEncoder_ = (__bridge_retained void*)offscreenEncoder;
        commandBuffer_ = (__bridge_retained void*)offscreenCommandBuffer;
        currentRenderTargetWidth_ = rtWidth;
        currentRenderTargetHeight_ = rtHeight;
        
        // Create orthographic projection for 2D rendering
        // This matches the main rendering coordinate system
        float orthoMatrix[16] = {
            2.0f / rtWidth, 0, 0, 0,
            0, -2.0f / rtHeight, 0, 0,  // Negative Y for standard coordinate system
            0, 0, -1, 0,
            -1, 1, 0, 1
        };
        
        // Render all children to texture
        for (const auto& child : frame->getChildren()) {
            renderObject2D(child.get(), orthoMatrix);
        }
        
        // End encoding and commit
        [offscreenEncoder endEncoding];
        [offscreenCommandBuffer commit];
        [offscreenCommandBuffer waitUntilCompleted];
        
        // Restore original encoder, command buffer, and render target dimensions
        if (renderEncoder_) {
            CFRelease(renderEncoder_);
        }
        if (commandBuffer_) {
            CFRelease(commandBuffer_);
        }
        renderEncoder_ = savedEncoder;
        commandBuffer_ = savedCommandBuffer;
        currentRenderTargetWidth_ = savedRenderTargetWidth;
        currentRenderTargetHeight_ = savedRenderTargetHeight;
    }
}

void MetalRenderer::renderTexturedQuad(void* texture, float width, float height, const float* mvpMatrix) {
    if (!texture || !renderEncoder_) return;
    
    @autoreleasepool {
        id<MTLRenderCommandEncoder> encoder = (__bridge id<MTLRenderCommandEncoder>)renderEncoder_;
        id<MTLTexture> tex = (__bridge id<MTLTexture>)texture;
        
        // Create quad vertices (centered)
        // Flip texture V coordinates to correct vertical orientation
        float halfW = width * 0.5f;
        float halfH = height * 0.5f;
        
        Vertex vertices[6] = {
            // Triangle 1
            {{-halfW, -halfH}, {1, 1, 1, 1}, {0, 0}},  // Bottom-left (V flipped: 1->0)
            {{ halfW, -halfH}, {1, 1, 1, 1}, {1, 0}},  // Bottom-right (V flipped: 1->0)
            {{-halfW,  halfH}, {1, 1, 1, 1}, {0, 1}},  // Top-left (V flipped: 0->1)
            
            // Triangle 2
            {{ halfW, -halfH}, {1, 1, 1, 1}, {1, 0}},  // Bottom-right (V flipped: 1->0)
            {{ halfW,  halfH}, {1, 1, 1, 1}, {1, 1}},  // Top-right (V flipped: 0->1)
            {{-halfW,  halfH}, {1, 1, 1, 1}, {0, 1}}   // Top-left (V flipped: 0->1)
        };
        
        // Set MVP matrix
        [encoder setVertexBytes:mvpMatrix length:sizeof(float) * 16 atIndex:1];
        
        // Set texture
        [encoder setFragmentTexture:tex atIndex:0];
        
        // Draw quad
        [encoder setVertexBytes:vertices length:sizeof(vertices) atIndex:0];
        [encoder drawPrimitives:MTLPrimitiveTypeTriangle vertexStart:0 vertexCount:6];
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

bool MetalRenderer::captureFrame(std::vector<uint8_t>& pixelData, int& width, int& height) {
    if (!initialized_) {
        return false;
    }
    
    @autoreleasepool {
        MTKView* metalView = (__bridge MTKView*)metalView_;
        id<MTLTexture> drawable = metalView.currentDrawable.texture;
        
        if (!drawable) {
            return false;
        }
        
        width = (int)drawable.width;
        height = (int)drawable.height;
        
        // Allocate buffer for pixel data (BGRA format, 4 bytes per pixel)
        size_t bytesPerRow = width * 4;
        size_t totalBytes = bytesPerRow * height;
        pixelData.resize(totalBytes);
        
        // Create a blit command to copy texture to CPU-accessible buffer
        id<MTLDevice> device = (__bridge id<MTLDevice>)device_;
        id<MTLCommandQueue> commandQueue = (__bridge id<MTLCommandQueue>)commandQueue_;
        
        id<MTLCommandBuffer> commandBuffer = [commandQueue commandBuffer];
        id<MTLBlitCommandEncoder> blitEncoder = [commandBuffer blitCommandEncoder];
        
        [blitEncoder copyFromTexture:drawable
                         sourceSlice:0
                         sourceLevel:0
                        sourceOrigin:MTLOriginMake(0, 0, 0)
                          sourceSize:MTLSizeMake(width, height, 1)
                            toBuffer:[device newBufferWithLength:totalBytes 
                                                         options:MTLResourceStorageModeShared]
                   destinationOffset:0
              destinationBytesPerRow:bytesPerRow
            destinationBytesPerImage:totalBytes];
        
        [blitEncoder endEncoding];
        [commandBuffer commit];
        [commandBuffer waitUntilCompleted];
        
        // Get the buffer we just created
        id<MTLBuffer> buffer = [device newBufferWithLength:totalBytes 
                                                    options:MTLResourceStorageModeShared];
        
        // Copy again with proper buffer
        commandBuffer = [commandQueue commandBuffer];
        blitEncoder = [commandBuffer blitCommandEncoder];
        
        [blitEncoder copyFromTexture:drawable
                         sourceSlice:0
                         sourceLevel:0
                        sourceOrigin:MTLOriginMake(0, 0, 0)
                          sourceSize:MTLSizeMake(width, height, 1)
                            toBuffer:buffer
                   destinationOffset:0
              destinationBytesPerRow:bytesPerRow
            destinationBytesPerImage:totalBytes];
        
        [blitEncoder endEncoding];
        [commandBuffer commit];
        [commandBuffer waitUntilCompleted];
        
        // Copy data from Metal buffer to our vector
        memcpy(pixelData.data(), [buffer contents], totalBytes);
        
        return true;
    }
}

bool MetalRenderer::saveCapture(const char* filename) {
    std::vector<uint8_t> pixelData;
    int width, height;
    
    if (!captureFrame(pixelData, width, height)) {
        return false;
    }
    
    @autoreleasepool {
        // Create CGImage from pixel data
        CGColorSpaceRef colorSpace = CGColorSpaceCreateDeviceRGB();
        CGContextRef context = CGBitmapContextCreate(
            pixelData.data(),
            width,
            height,
            8,
            width * 4,
            colorSpace,
            kCGImageAlphaPremultipliedFirst | kCGBitmapByteOrder32Little
        );
        
        if (!context) {
            CGColorSpaceRelease(colorSpace);
            return false;
        }
        
        CGImageRef imageRef = CGBitmapContextCreateImage(context);
        CGContextRelease(context);
        
        if (!imageRef) {
            CGColorSpaceRelease(colorSpace);
            return false;
        }
        
        // Save to file
        NSString* path = [NSString stringWithUTF8String:filename];
        NSURL* url = [NSURL fileURLWithPath:path];
        
        // Use modern UTType API if available, fallback to kUTTypePNG
        CFStringRef imageType;
        if (@available(macOS 11.0, *)) {
            imageType = (__bridge CFStringRef)@"public.png";
        } else {
            #pragma clang diagnostic push
            #pragma clang diagnostic ignored "-Wdeprecated-declarations"
            imageType = kUTTypePNG;
            #pragma clang diagnostic pop
        }
        
        CGImageDestinationRef destination = CGImageDestinationCreateWithURL(
            (__bridge CFURLRef)url,
            imageType,
            1,
            NULL
        );
        
        if (!destination) {
            CGImageRelease(imageRef);
            CGColorSpaceRelease(colorSpace);
            return false;
        }
        
        CGImageDestinationAddImage(destination, imageRef, NULL);
        bool success = CGImageDestinationFinalize(destination);
        
        CFRelease(destination);
        CGImageRelease(imageRef);
        CGColorSpaceRelease(colorSpace);
        
        return success;
    }
}

void MetalRenderer::pushScissorRect(float x, float y, float width, float height, const float* mvpMatrix) {
    @autoreleasepool {
        // Transform the four corners of the clipping rectangle to screen space
        float corners[4][2] = {
            {x, y},                    // Top-left
            {x + width, y},            // Top-right
            {x, y + height},           // Bottom-left
            {x + width, y + height}    // Bottom-right
        };
        
        float screenCorners[4][2];
        for (int i = 0; i < 4; i++) {
            transformPointToScreen(corners[i][0], corners[i][1], mvpMatrix, 
                                  screenCorners[i][0], screenCorners[i][1]);
        }
        
        // Find bounding box in screen space
        float minX = screenCorners[0][0];
        float maxX = screenCorners[0][0];
        float minY = screenCorners[0][1];
        float maxY = screenCorners[0][1];
        
        for (int i = 1; i < 4; i++) {
            minX = std::min(minX, screenCorners[i][0]);
            maxX = std::max(maxX, screenCorners[i][0]);
            minY = std::min(minY, screenCorners[i][1]);
            maxY = std::max(maxY, screenCorners[i][1]);
        }
        
        // Use stored render target dimensions (set in beginFrame or renderFrame3DToTexture)
        float targetWidth = static_cast<float>(currentRenderTargetWidth_);
        float targetHeight = static_cast<float>(currentRenderTargetHeight_);
        
        // Convert to integer pixel coordinates
        int scissorX = static_cast<int>(std::max(0.0f, minX));
        int scissorY = static_cast<int>(std::max(0.0f, minY));
        int scissorWidth = static_cast<int>(std::min(targetWidth, maxX) - scissorX);
        int scissorHeight = static_cast<int>(std::min(targetHeight, maxY) - scissorY);
        
        // Clamp to valid ranges
        scissorWidth = std::max(0, scissorWidth);
        scissorHeight = std::max(0, scissorHeight);
        
        // If there's already a scissor rect, intersect with it
        if (!scissorStack_.empty()) {
            const ScissorRect& parent = scissorStack_.back();
            int parentRight = parent.x + parent.width;
            int parentBottom = parent.y + parent.height;
            int scissorRight = scissorX + scissorWidth;
            int scissorBottom = scissorY + scissorHeight;
            
            scissorX = std::max(scissorX, parent.x);
            scissorY = std::max(scissorY, parent.y);
            scissorRight = std::min(scissorRight, parentRight);
            scissorBottom = std::min(scissorBottom, parentBottom);
            
            scissorWidth = std::max(0, scissorRight - scissorX);
            scissorHeight = std::max(0, scissorBottom - scissorY);
        }
        
        // Push to stack
        scissorStack_.push_back({scissorX, scissorY, scissorWidth, scissorHeight});
        
        // Apply to Metal render encoder
        id<MTLRenderCommandEncoder> encoder = (__bridge id<MTLRenderCommandEncoder>)renderEncoder_;
        MTLScissorRect metalScissor;
        metalScissor.x = scissorX;
        metalScissor.y = scissorY;
        metalScissor.width = scissorWidth;
        metalScissor.height = scissorHeight;
        [encoder setScissorRect:metalScissor];
    }
}

void MetalRenderer::popScissorRect() {
    if (scissorStack_.empty()) return;
    
    @autoreleasepool {
        scissorStack_.pop_back();
        
        id<MTLRenderCommandEncoder> renderEncoder = (__bridge id<MTLRenderCommandEncoder>)renderEncoder_;
        
        if (scissorStack_.empty()) {
            // Restore to full viewport using stored render target dimensions
            MTLScissorRect metalScissor;
            metalScissor.x = 0;
            metalScissor.y = 0;
            metalScissor.width = static_cast<NSUInteger>(currentRenderTargetWidth_);
            metalScissor.height = static_cast<NSUInteger>(currentRenderTargetHeight_);
            [renderEncoder setScissorRect:metalScissor];
        } else {
            // Restore to parent scissor rect
            const ScissorRect& parent = scissorStack_.back();
            MTLScissorRect metalScissor;
            metalScissor.x = parent.x;
            metalScissor.y = parent.y;
            metalScissor.width = parent.width;
            metalScissor.height = parent.height;
            [renderEncoder setScissorRect:metalScissor];
        }
    }
}

void MetalRenderer::transformPointToScreen(float x, float y, const float* mvpMatrix, float& screenX, float& screenY) {
    // Transform point by MVP matrix
    float clipX = mvpMatrix[0] * x + mvpMatrix[4] * y + mvpMatrix[12];
    float clipY = mvpMatrix[1] * x + mvpMatrix[5] * y + mvpMatrix[13];
    float clipW = mvpMatrix[3] * x + mvpMatrix[7] * y + mvpMatrix[15];
    
    // Perspective divide
    if (clipW != 0.0f) {
        clipX /= clipW;
        clipY /= clipW;
    }
    
    // Use current render target dimensions (works for both main screen and off-screen textures)
    float targetWidth = static_cast<float>(currentRenderTargetWidth_);
    float targetHeight = static_cast<float>(currentRenderTargetHeight_);
    
    // Convert from NDC [-1, 1] to render target space [0, width/height]
    screenX = (clipX + 1.0f) * 0.5f * targetWidth;
    screenY = (1.0f - clipY) * 0.5f * targetHeight;  // Flip Y for screen coordinates
}

} // namespace CyberUI
