#pragma once

#include <string>
#include <memory>
#include <vector>

namespace CyberUI {

// Image class for loading and managing textures
class Image {
public:
    enum class Format {
        JPEG,
        PNG,
        Unknown
    };

    Image();
    ~Image();

    // Load image from file (JPEG or PNG)
    bool loadFromFile(const std::string& filepath);
    
    // Get image properties
    int getWidth() const { return width_; }
    int getHeight() const { return height_; }
    int getChannels() const { return channels_; }
    Format getFormat() const { return format_; }
    
    // Get raw pixel data
    const unsigned char* getData() const { return data_.data(); }
    size_t getDataSize() const { return data_.size(); }
    
    // Check if image is loaded
    bool isLoaded() const { return !data_.empty(); }
    
    // Get file path
    const std::string& getFilePath() const { return filepath_; }

private:
    std::string filepath_;
    std::vector<unsigned char> data_;
    int width_;
    int height_;
    int channels_;
    Format format_;
    
    Format detectFormat(const std::string& filepath);
};

} // namespace CyberUI
