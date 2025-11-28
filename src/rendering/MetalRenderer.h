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

private:
    void setupShaders();
    void renderRectangle(class Rectangle* rect, const float* mvpMatrix);
    void renderText(class Text* text, const float* mvpMatrix);
    void renderFrame3D(Frame3D* frame, const float* viewProjMatrix);
    void renderObject2D(Object2D* object, const float* mvpMatrix);
    
    void* getOrCreateTexture(Image* image);
    
    void multiplyMatrices(const float* a, const float* b, float* result);
    void createTransformMatrix(float x, float y, float z, 
                              float pitch, float yaw, float roll,
                              float sx, float sy, float sz,
                              float* matrix);
    
    void* device_;
    void* commandQueue_;
    void* pipelineState_;
    void* window_;
    void* metalView_;
    void* commandBuffer_;
    void* renderEncoder_;
    
    bool initialized_;
    bool shouldClose_;
    int windowWidth_;
    int windowHeight_;
    
    // Texture cache to avoid recreating textures every frame
    std::map<Image*, void*> textureCache_;
    std::map<std::string, void*> textTextureCache_;
    
    // Track if new textures were created this frame
    bool newTexturesCreatedThisFrame_;
};

} // namespace CyberUI
