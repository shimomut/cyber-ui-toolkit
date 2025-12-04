#include "Frame2D.h"
#include <iostream>

namespace CyberUI {

Frame2D::Frame2D() 
    : width_(100.0f), height_(100.0f), clipping_enabled_(true) {
}

void Frame2D::setSize(float width, float height) {
    width_ = width;
    height_ = height;
}

void Frame2D::getSize(float& width, float& height) const {
    width = width_;
    height = height_;
}

void Frame2D::render() {
    if (!isVisible()) return;

    // Note: Clipping is now handled by the renderer (MetalRenderer)
    // The renderer detects Frame2D objects and applies scissor rects automatically
    // based on the clipping_enabled_ flag and size.
    
    // Render all children
    for (const auto& child : getChildren()) {
        child->render();
    }
}

} // namespace CyberUI
