#pragma once

#include "Renderer.h"
#include <map>
#include <string>
#include <vector>

namespace CyberUI {

class Frame3D;
class Image;

class MetalRenderer : public Renderer {
public:
    MetalRenderer();
    ~MetalRenderer() override;
    
    bool initialize(int width, int height, const char* title) override;
    void shutdown() override;
    bool beginFrame() override;
    void endFrame() override;
    void renderObject(Object2D* object) override;
    void renderScene(SceneRoot* scene) override;
    bool shouldClose() override;
    void pollEvents() override;
    
    // Capture functionality
    bool captureFrame(std::vector<uint8_t>& pixelData, int& width, int& height) override;
    bool saveCapture(const char* filename) override;
    
    // FPS measurement
    double getFPS() const override;
    int getFrameCount() const override;

private:
    void setupShaders();
    void renderRectangle(class Rectangle* rect, const float* mvpMatrix);
    void renderText(class Text* text, const float* mvpMatrix);
    void renderFrame3D(Frame3D* frame, const float* viewProjMatrix);
    void renderObject2D(Object2D* object, const float* mvpMatrix);
    
    void* getOrCreateTexture(Image* image);
    void* getOrCreateRenderTarget(Frame3D* frame);
    void renderFrame3DToTexture(Frame3D* frame);
    void renderTexturedQuad(void* texture, float width, float height, const float* mvpMatrix);
    
    // Scissor rect management for clipping
    void pushScissorRect(float x, float y, float width, float height, const float* mvpMatrix);
    void popScissorRect();
    void transformPointToScreen(float x, float y, const float* mvpMatrix, float& screenX, float& screenY);
    
    void multiplyMatrices(const float* a, const float* b, float* result);
    void createTransformMatrix(float x, float y, float z, 
                              float pitch, float yaw, float roll,
                              float sx, float sy, float sz,
                              float* matrix);
    
    void* device_;
    void* commandQueue_;
    void* pipelineState_;
    void* depthStencilStateEnabled_;   // Depth test enabled for 3D rendering
    void* depthStencilStateDisabled_;  // Depth test disabled for 2D off-screen rendering
    void* window_;
    void* metalView_;
    void* commandBuffer_;
    void* renderEncoder_;
    void* framePacingSemaphore_;  // Semaphore for frame pacing (V-Sync)
    
    bool initialized_;
    bool shouldClose_;
    int windowWidth_;
    int windowHeight_;
    
    // Texture cache to avoid recreating textures every frame
    std::map<Image*, void*> textureCache_;
    std::map<std::string, void*> textTextureCache_;
    std::map<Frame3D*, void*> renderTargetCache_;  // Frame3D -> render target texture
    
    // Track if new textures were created this frame
    bool newTexturesCreatedThisFrame_;
    
    // Scissor rect stack for clipping
    struct ScissorRect {
        int x, y, width, height;
    };
    std::vector<ScissorRect> scissorStack_;
    
    // Current render target dimensions (for scissor rect calculation)
    int currentRenderTargetWidth_;
    int currentRenderTargetHeight_;
    
    // FPS tracking
    int frameCount_;           // Frames since last FPS update (for FPS calculation)
    int totalFrameCount_;      // Total frames rendered (never reset)
    double startTime_;
    double lastFPSUpdateTime_;
    double currentFPS_;
    double lastFrameTime_;     // Time of last frame for FPS limiting
};

} // namespace CyberUI
