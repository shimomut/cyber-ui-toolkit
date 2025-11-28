#include "Object2D.h"
#include <algorithm>

namespace CyberUI {

Object2D::Object2D() 
    : parent_(nullptr), visible_(true), name_("") {
    position_[0] = position_[1] = 0.0f;
}

void Object2D::addChild(std::shared_ptr<Object2D> child) {
    if (child && child->parent_ != this) {
        if (child->parent_) {
            child->parent_->removeChild(child);
        }
        child->parent_ = this;
        children_.push_back(child);
    }
}

void Object2D::removeChild(std::shared_ptr<Object2D> child) {
    auto it = std::find(children_.begin(), children_.end(), child);
    if (it != children_.end()) {
        (*it)->parent_ = nullptr;
        children_.erase(it);
    }
}

void Object2D::setPosition(float x, float y) {
    position_[0] = x;
    position_[1] = y;
}

void Object2D::getPosition(float& x, float& y) const {
    x = position_[0];
    y = position_[1];
}

} // namespace CyberUI
