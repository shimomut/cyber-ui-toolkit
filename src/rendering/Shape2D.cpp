#include "Shape2D.h"
#include <iostream>

namespace CyberUI {

Shape2D::Shape2D() {
    // Default white color
    color_[0] = color_[1] = color_[2] = color_[3] = 1.0f;
}

void Shape2D::setColor(float r, float g, float b, float a) {
    color_[0] = r;
    color_[1] = g;
    color_[2] = b;
    color_[3] = a;
}

void Shape2D::getColor(float& r, float& g, float& b, float& a) const {
    r = color_[0];
    g = color_[1];
    b = color_[2];
    a = color_[3];
}

void Shape2D::render() {
    // Base implementation - to be overridden
}

// Rectangle implementation
Rectangle::Rectangle(float width, float height) 
    : width_(width), height_(height) {
}

void Rectangle::setSize(float width, float height) {
    width_ = width;
    height_ = height;
}

void Rectangle::getSize(float& width, float& height) const {
    width = width_;
    height = height_;
}

void Rectangle::render() {
    if (!isVisible()) return;

    // Placeholder rendering - will be replaced with actual graphics API calls
    float x, y, z;
    getPosition(x, y, z);
    float r, g, b, a;
    getColor(r, g, b, a);
    
    std::cout << "Rendering Rectangle: " << getName() 
              << " at (" << x << ", " << y << ", " << z << ")"
              << " size: " << width_ << "x" << height_
              << " color: (" << r << ", " << g << ", " << b << ", " << a << ")"
              << std::endl;

    // Render children
    for (const auto& child : getChildren()) {
        child->render();
    }
}

} // namespace CyberUI
