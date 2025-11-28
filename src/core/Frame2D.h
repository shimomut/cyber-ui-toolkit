#pragma once

#include "Object2D.h"

namespace CyberUI {

// 2D frame that can contain other 2D objects with clipping capability
class Frame2D : public Object2D {
public:
    Frame2D();
    virtual ~Frame2D() = default;

    // Size for clipping region
    void setSize(float width, float height);
    void getSize(float& width, float& height) const;

    // Clipping control
    void setClippingEnabled(bool enabled) { clipping_enabled_ = enabled; }
    bool isClippingEnabled() const { return clipping_enabled_; }

    void render() override;

protected:
    float width_;
    float height_;
    bool clipping_enabled_;
};

} // namespace CyberUI
