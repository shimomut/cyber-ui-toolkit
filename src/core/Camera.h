#pragma once

namespace CyberUI {

// Camera class for 3D rendering
class Camera {
public:
    Camera();
    ~Camera() = default;

    // Position
    void setPosition(float x, float y, float z);
    void getPosition(float& x, float& y, float& z) const;

    // Orientation (Euler angles: pitch, yaw, roll)
    void setRotation(float pitch, float yaw, float roll);
    void getRotation(float& pitch, float& yaw, float& roll) const;

    // Perspective parameters
    void setPerspective(float fov, float aspect, float near, float far);
    void getFOV(float& fov) const { fov = fov_; }
    void getAspect(float& aspect) const { aspect = aspect_; }
    void getNearFar(float& near, float& far) const { near = near_; far = far_; }

    // Get view and projection matrices (4x4 column-major)
    void getViewMatrix(float* matrix) const;
    void getProjectionMatrix(float* matrix) const;

private:
    float position_[3];
    float rotation_[3];  // pitch, yaw, roll
    float fov_;          // Field of view in radians
    float aspect_;       // Aspect ratio (width/height)
    float near_;         // Near clipping plane
    float far_;          // Far clipping plane
};

} // namespace CyberUI
