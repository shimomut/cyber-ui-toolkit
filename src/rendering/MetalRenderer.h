#pragma once

#include "Renderer.h"

namespace CyberUI {

class MetalRenderer : public Renderer {
public:
    MetalRenderer();
    ~MetalRenderer() override;
    
    bool initialize(int width, int height, const char* title) override;
    void shutdown() override;
    bool beginFrame() override;
    void endFrame() override;
    void renderObject(Object2D* object) override;
    bool shouldClose() override;
    void pollEvents() override;

private:
    void setupShaders();
    void renderRectangle(class Rectangle* rect);
    
    void* device_;
    void* commandQueue_;
    void* pipelineState_;
    void* window_;
    void* metalView_;
    void* commandBuffer_;
    void* renderEncoder_;
    
    bool initialized_;
    bool shouldClose_;
};

} // namespace CyberUI
