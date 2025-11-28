#include "Text.h"
#include <iostream>

namespace CyberUI {

Text::Text(const std::string& text) 
    : text_(text), font_(nullptr), alignment_(Alignment::Left) {
    // Default white color
    color_[0] = color_[1] = color_[2] = color_[3] = 1.0f;
}

void Text::setText(const std::string& text) {
    text_ = text;
}

void Text::setFont(std::shared_ptr<Font> font) {
    font_ = font;
}

void Text::setColor(float r, float g, float b, float a) {
    color_[0] = r;
    color_[1] = g;
    color_[2] = b;
    color_[3] = a;
}

void Text::getColor(float& r, float& g, float& b, float& a) const {
    r = color_[0];
    g = color_[1];
    b = color_[2];
    a = color_[3];
}

void Text::render() {
    if (!isVisible()) return;

    // Placeholder rendering - will be replaced with actual graphics API calls
    float x, y;
    getPosition(x, y);
    float r, g, b, a;
    getColor(r, g, b, a);
    
    std::cout << "Rendering Text: " << getName() 
              << " at (" << x << ", " << y << ")"
              << " text: \"" << text_ << "\""
              << " color: (" << r << ", " << g << ", " << b << ", " << a << ")";
    
    if (hasFont()) {
        std::cout << " font: " << getFont()->getFilePath() 
                  << " (size: " << getFont()->getSize() << ")";
    }
    
    std::cout << " alignment: ";
    switch (alignment_) {
        case Alignment::Left: std::cout << "Left"; break;
        case Alignment::Center: std::cout << "Center"; break;
        case Alignment::Right: std::cout << "Right"; break;
    }
    
    std::cout << std::endl;

    // Render children
    for (const auto& child : getChildren()) {
        child->render();
    }
}

} // namespace CyberUI
