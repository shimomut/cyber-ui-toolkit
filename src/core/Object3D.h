#pragma once

#include <vector>
#include <memory>
#include <string>

namespace CyberUI {

// Base class for all 3D objects in the scene hierarchy
class Object3D {
public:
    Object3D();
    virtual ~Object3D() = default;

    // Hierarchy management
    void addChild(std::shared_ptr<Object3D> child);
    void removeChild(std::shared_ptr<Object3D> child);
    Object3D* getParent() const { return parent_; }
    const std::vector<std::shared_ptr<Object3D>>& getChildren() const { return children_; }

    // Transform
    void setPosition(float x, float y, float z);
    void getPosition(float& x, float& y, float& z) const;

    // Visibility
    void setVisible(bool visible) { visible_ = visible; }
    bool isVisible() const { return visible_; }

    // Name for debugging
    void setName(const std::string& name) { name_ = name; }
    const std::string& getName() const { return name_; }

    // Virtual render method
    virtual void render() = 0;

protected:
    Object3D* parent_;
    std::vector<std::shared_ptr<Object3D>> children_;
    
    float position_[3];
    bool visible_;
    std::string name_;
};

} // namespace CyberUI
