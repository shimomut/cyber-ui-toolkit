#pragma once

#include "../core/Object2D.h"
#include "Font.h"
#include <memory>
#include <string>

namespace CyberUI {

// Text rendering class - child of Object2D
class Text : public Object2D {
public:
    Text(const std::string& text = "");
    virtual ~Text() = default;

    // Text content
    void setText(const std::string& text);
    const std::string& getText() const { return text_; }

    // Font association
    void setFont(std::shared_ptr<Font> font);
    std::shared_ptr<Font> getFont() const { return font_; }
    bool hasFont() const { return font_ != nullptr; }

    // Text color (RGBA)
    void setColor(float r, float g, float b, float a = 1.0f);
    void getColor(float& r, float& g, float& b, float& a) const;

    // Text alignment
    enum class Alignment {
        Left,
        Center,
        Right
    };

    void setAlignment(Alignment alignment) { alignment_ = alignment; }
    Alignment getAlignment() const { return alignment_; }

    // Rendering
    void render() override;

private:
    std::string text_;
    std::shared_ptr<Font> font_;
    float color_[4];
    Alignment alignment_;
};

} // namespace CyberUI
