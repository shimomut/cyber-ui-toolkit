#pragma once

#include "Object2D.h"
#include <vector>
#include <memory>

namespace CyberUI {

// Top-level 3D frame that can contain 2D objects
// Has 3D position, orientation, and scale
// Supports off-screen rendering for proper clipping with 3D transforms
class Frame3D {
public:
    Frame3D(int width, int height);
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

    // Off-screen rendering (always enabled for proper clipping with 3D transforms)
    bool isOffscreenRenderingEnabled() const { return true; }
    
    // Size configuration for render target
    void setSize(int width, int height);
    void getSize(int& width, int& height) const;
    
    // Legacy method for compatibility
    void getRenderTargetSize(int& width, int& height) const;
    
    // Render target texture (managed by renderer)
    void setRenderTargetTexture(void* texture) { renderTargetTexture_ = texture; }
    void* getRenderTargetTexture() const { return renderTargetTexture_; }

    // Render all children
    virtual void render();

protected:
    std::vector<std::shared_ptr<Object2D>> children_;
    
    float position_[3];
    float rotation_[3];  // pitch, yaw, roll
    float scale_[3];
    bool visible_;
    std::string name_;
    
    // Off-screen rendering support (always enabled)
    int renderTargetWidth_;
    int renderTargetHeight_;
    void* renderTargetTexture_;  // Opaque pointer to renderer-specific texture
};

} // namespace CyberUI
