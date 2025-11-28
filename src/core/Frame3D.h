#pragma once

#include "Object2D.h"
#include <vector>
#include <memory>

namespace CyberUI {

// Top-level 3D frame that can contain 2D objects
// Has 3D position, orientation, and scale
class Frame3D {
public:
    Frame3D();
    virtual ~Frame3D() = default;

    // 3D Transform
    void setPosition(float x, float y, float z);
    void getPosition(float& x, float& y, float& z) const;
    
    void setRotation(float pitch, float yaw, float roll);
    void getRotation(float& pitch, float& yaw, float& roll) const;
    
    void setScale(float x, float y, float z);
    void getScale(float& x, float& y, float& z) const;

    // Hierarchy management - can only contain 2D objects
    void addChild(std::shared_ptr<Object2D> child);
    void removeChild(std::shared_ptr<Object2D> child);
    const std::vector<std::shared_ptr<Object2D>>& getChildren() const { return children_; }

    // Visibility
    void setVisible(bool visible) { visible_ = visible; }
    bool isVisible() const { return visible_; }

    // Name for debugging
    void setName(const std::string& name) { name_ = name; }
    const std::string& getName() const { return name_; }

    // Render all children
    virtual void render();

protected:
    std::vector<std::shared_ptr<Object2D>> children_;
    
    float position_[3];
    float rotation_[3];  // pitch, yaw, roll
    float scale_[3];
    bool visible_;
    std::string name_;
};

} // namespace CyberUI
