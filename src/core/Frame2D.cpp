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

    // Apply clipping if enabled
    if (clipping_enabled_) {
        float x, y;
        getPosition(x, y);
        std::cout << "Frame2D: " << getName() 
                  << " clipping region at (" << x << ", " << y << ")"
                  << " size: " << width_ << "x" << height_ << std::endl;
        // TODO: Set up clipping rectangle in graphics API
    }

    // Render all children
    for (const auto& child : getChildren()) {
        child->render();
    }

    // Restore clipping state
    if (clipping_enabled_) {
        // TODO: Restore previous clipping state
    }
}

} // namespace CyberUI
