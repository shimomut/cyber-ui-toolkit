#pragma once

#include "Renderer.h"

namespace CyberUI {

class Frame3D;

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

private:
    void setupShaders();
    void renderRectangle(class Rectangle* rect, const float* mvpMatrix);
    void renderText(class Text* text, const float* mvpMatrix);
    void renderFrame3D(Frame3D* frame, const float* viewProjMatrix);
    void renderObject2D(Object2D* object, const float* mvpMatrix);
    
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
};

} // namespace CyberUI
