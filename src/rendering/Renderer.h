#pragma once

#include <memory>

namespace CyberUI {

class Object2D;
class SceneRoot;

// Abstract renderer interface
class Renderer {
public:
    virtual ~Renderer() = default;
    
    virtual bool initialize(int width, int height, const char* title) = 0;
    virtual void shutdown() = 0;
    virtual bool beginFrame() = 0;
    virtual void endFrame() = 0;
    
    // Legacy: render individual object (deprecated, use renderScene instead)
    virtual void renderObject(Object2D* object) = 0;
    
    // New: render entire scene with camera
    virtual void renderScene(SceneRoot* scene) = 0;
    
    virtual bool shouldClose() = 0;
    virtual void pollEvents() = 0;
};

// Factory function
std::unique_ptr<Renderer> createMetalRenderer();

} // namespace CyberUI
