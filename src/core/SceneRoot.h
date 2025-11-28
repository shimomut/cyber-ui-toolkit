#pragma once

#include "Frame3D.h"
#include "Camera.h"
#include <vector>
#include <memory>

namespace CyberUI {

// Root of the scene hierarchy
class SceneRoot {
public:
    SceneRoot();
    ~SceneRoot() = default;

    // Add/remove Frame3D objects to the scene
    void addFrame3D(std::shared_ptr<Frame3D> frame);
    void removeFrame3D(std::shared_ptr<Frame3D> frame);
    const std::vector<std::shared_ptr<Frame3D>>& getFrames() const { return frames_; }

    // Camera management
    void setCamera(std::shared_ptr<Camera> camera) { camera_ = camera; }
    std::shared_ptr<Camera> getCamera() const { return camera_; }

    // Clear all frames
    void clear() { frames_.clear(); }

private:
    std::vector<std::shared_ptr<Frame3D>> frames_;
    std::shared_ptr<Camera> camera_;
};

} // namespace CyberUI
