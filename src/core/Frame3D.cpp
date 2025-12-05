#include "Frame3D.h"
#include <algorithm>

namespace CyberUI {

Frame3D::Frame3D(int width, int height) 
    : visible_(true), name_(""),
      renderTargetWidth_(width), renderTargetHeight_(height),
      renderTargetTexture_(nullptr) {
    position_[0] = position_[1] = position_[2] = 0.0f;
    rotation_[0] = rotation_[1] = rotation_[2] = 0.0f;
    scale_[0] = scale_[1] = scale_[2] = 1.0f;
}

void Frame3D::setPosition(float x, float y, float z) {
    position_[0] = x;
    position_[1] = y;
    position_[2] = z;
}

void Frame3D::getPosition(float& x, float& y, float& z) const {
    x = position_[0];
    y = position_[1];
    z = position_[2];
}

void Frame3D::setRotation(float pitch, float yaw, float roll) {
    rotation_[0] = pitch;
    rotation_[1] = yaw;
    rotation_[2] = roll;
}

void Frame3D::getRotation(float& pitch, float& yaw, float& roll) const {
    pitch = rotation_[0];
    yaw = rotation_[1];
    roll = rotation_[2];
}

void Frame3D::setScale(float x, float y, float z) {
    scale_[0] = x;
    scale_[1] = y;
    scale_[2] = z;
}

void Frame3D::getScale(float& x, float& y, float& z) const {
    x = scale_[0];
    y = scale_[1];
    z = scale_[2];
}

void Frame3D::addChild(std::shared_ptr<Object2D> child) {
    if (child) {
        children_.push_back(child);
    }
}

void Frame3D::removeChild(std::shared_ptr<Object2D> child) {
    auto it = std::find(children_.begin(), children_.end(), child);
    if (it != children_.end()) {
        children_.erase(it);
    }
}

void Frame3D::setSize(int width, int height) {
    renderTargetWidth_ = width;
    renderTargetHeight_ = height;
}

void Frame3D::getSize(int& width, int& height) const {
    width = renderTargetWidth_;
    height = renderTargetHeight_;
}

void Frame3D::getRenderTargetSize(int& width, int& height) const {
    width = renderTargetWidth_;
    height = renderTargetHeight_;
}

void Frame3D::render() {
    if (!visible_) return;

    // Render all 2D children
    for (const auto& child : children_) {
        child->render();
    }
}

} // namespace CyberUI
