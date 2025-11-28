#pragma once

#include "../core/Object3D.h"

namespace CyberUI {

// Base class for 2D shapes
class Shape2D : public Object3D {
public:
    Shape2D();
    virtual ~Shape2D() = default;

    // Color (RGBA)
    void setColor(float r, float g, float b, float a = 1.0f);
    void getColor(float& r, float& g, float& b, float& a) const;

    void render() override;

protected:
    float color_[4];
};

// Rectangle shape
class Rectangle : public Shape2D {
public:
    Rectangle(float width = 100.0f, float height = 100.0f);
    virtual ~Rectangle() = default;

    void setSize(float width, float height);
    void getSize(float& width, float& height) const;

    void render() override;

private:
    float width_;
    float height_;
};

} // namespace CyberUI
