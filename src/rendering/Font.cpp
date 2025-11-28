#include "Font.h"
#include <iostream>

namespace CyberUI {

Font::Font() 
    : size_(16.0f), loaded_(false), bold_(false), italic_(false) {
}

bool Font::loadFromFile(const std::string& filePath, float size) {
    filePath_ = filePath;
    size_ = size;
    
    // TODO: Implement actual font loading using FreeType or similar
    // For now, just mark as loaded if path is not empty
    loaded_ = !filePath.empty();
    
    if (loaded_) {
        std::cout << "Font loaded: " << filePath_ << " (size: " << size_ << ")" << std::endl;
    } else {
        std::cerr << "Failed to load font: " << filePath_ << std::endl;
    }
    
    return loaded_;
}

void Font::setSize(float size) {
    if (size > 0.0f) {
        size_ = size;
    }
}

} // namespace CyberUI
