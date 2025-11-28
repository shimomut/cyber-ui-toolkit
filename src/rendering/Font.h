#pragma once

#include <string>
#include <memory>

namespace CyberUI {

// Font class for text rendering
class Font {
public:
    Font();
    virtual ~Font() = default;

    // Load font from file
    bool loadFromFile(const std::string& filePath, float size = 16.0f);

    // Font properties
    void setSize(float size);
    float getSize() const { return size_; }

    const std::string& getFilePath() const { return filePath_; }
    bool isLoaded() const { return loaded_; }

    // Font style
    void setBold(bool bold) { bold_ = bold; }
    bool isBold() const { return bold_; }

    void setItalic(bool italic) { italic_ = italic; }
    bool isItalic() const { return italic_; }

private:
    std::string filePath_;
    float size_;
    bool loaded_;
    bool bold_;
    bool italic_;
};

} // namespace CyberUI
