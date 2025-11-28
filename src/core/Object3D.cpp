#include "Object3D.h"
#include <algorithm>

namespace CyberUI {

Object3D::Object3D() 
    : parent_(nullptr), visible_(true), name_("") {
    position_[0] = position_[1] = position_[2] = 0.0f;
}

void Object3D::addChild(std::shared_ptr<Object3D> child) {
    if (child && child->parent_ != this) {
        if (child->parent_) {
            child->parent_->removeChild(child);
        }
        child->parent_ = this;
        children_.push_back(child);
    }
}

void Object3D::removeChild(std::shared_ptr<Object3D> child) {
    auto it = std::find(children_.begin(), children_.end(), child);
    if (it != children_.end()) {
        (*it)->parent_ = nullptr;
        children_.erase(it);
    }
}

void Object3D::setPosition(float x, float y, float z) {
    position_[0] = x;
    position_[1] = y;
    position_[2] = z;
}

void Object3D::getPosition(float& x, float& y, float& z) const {
    x = position_[0];
    y = position_[1];
    z = position_[2];
}

} // namespace CyberUI
