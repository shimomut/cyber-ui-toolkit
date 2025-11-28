#pragma once

#include <memory>

namespace CyberUI {

class Object3D;

// Abstract renderer interface
class Renderer {
public:
    virtual ~Renderer() = default;
    
    virtual bool initialize(int width, int height, const char* title) = 0;
    virtual void shutdown() = 0;
    virtual bool beginFrame() = 0;
    virtual void endFrame() = 0;
    virtual void renderObject(Object3D* object) = 0;
    virtual bool shouldClose() = 0;
    virtual void pollEvents() = 0;
};

// Factory function
std::unique_ptr<Renderer> createMetalRenderer();

} // namespace CyberUI
