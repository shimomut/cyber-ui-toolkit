#pragma once

#include <memory>
#include <vector>
#include <cstdint>

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
    
    // Capture functionality for debugging and testing
    virtual bool captureFrame(std::vector<uint8_t>& pixelData, int& width, int& height) = 0;
    virtual bool saveCapture(const char* filename) = 0;
    
    // FPS measurement
    virtual double getFPS() const = 0;
    virtual int getFrameCount() const = 0;
};

// Factory functions
std::unique_ptr<Renderer> createMetalRenderer();
std::unique_ptr<Renderer> createOpenGLRenderer();

} // namespace CyberUI
