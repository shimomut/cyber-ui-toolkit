#include "SceneRoot.h"
#include <algorithm>

namespace CyberUI {

SceneRoot::SceneRoot() 
    : camera_(std::make_shared<Camera>()) {
}

void SceneRoot::addFrame3D(std::shared_ptr<Frame3D> frame) {
    if (frame) {
        frames_.push_back(frame);
    }
}

void SceneRoot::removeFrame3D(std::shared_ptr<Frame3D> frame) {
    auto it = std::find(frames_.begin(), frames_.end(), frame);
    if (it != frames_.end()) {
        frames_.erase(it);
    }
}

} // namespace CyberUI
