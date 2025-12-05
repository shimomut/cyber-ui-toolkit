#include "Renderer.h"

#ifdef USE_METAL_BACKEND
#include "MetalRenderer.h"
#endif

#ifdef USE_OPENGL_BACKEND
#include "OpenGLRenderer.h"
#endif

namespace CyberUI {

#ifdef USE_METAL_BACKEND
std::unique_ptr<Renderer> createMetalRenderer() {
    return std::make_unique<MetalRenderer>();
}
#endif

#ifdef USE_OPENGL_BACKEND
std::unique_ptr<Renderer> createOpenGLRenderer() {
    return std::make_unique<OpenGLRenderer>();
}
#endif

} // namespace CyberUI
