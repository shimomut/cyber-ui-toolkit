#pragma once

#include <vector>
#include <memory>
#include <string>

namespace CyberUI {

// Base class for all 2D objects in the scene hierarchy
class Object2D {
public:
    Object2D();
    virtual ~Object2D() = default;

    // Hierarchy management
    void addChild(std::shared_ptr<Object2D> child);
    void removeChild(std::shared_ptr<Object2D> child);
    Object2D* getParent() const { return parent_; }
    const std::vector<std::shared_ptr<Object2D>>& getChildren() const { return children_; }

    // 2D Transform
    void setPosition(float x, float y);
    void getPosition(float& x, float& y) const;

    // Visibility
    void setVisible(bool visible) { visible_ = visible; }
    bool isVisible() const { return visible_; }

    // Name for debugging
    void setName(const std::string& name) { name_ = name; }
    const std::string& getName() const { return name_; }

    // Virtual render method
    virtual void render() = 0;

protected:
    Object2D* parent_;
    std::vector<std::shared_ptr<Object2D>> children_;
    
    float position_[2];
    bool visible_;
    std::string name_;
};

} // namespace CyberUI
