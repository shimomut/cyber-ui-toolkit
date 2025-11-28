#include "Camera.h"
#include <cmath>
#include <cstring>

namespace CyberUI {

Camera::Camera() 
    : fov_(1.0472f),  // 60 degrees in radians
      aspect_(16.0f / 9.0f),
      near_(0.1f),
      far_(100.0f) {
    position_[0] = 0.0f;
    position_[1] = 0.0f;
    position_[2] = 5.0f;  // Default: camera at z=5 looking at origin
    
    rotation_[0] = 0.0f;
    rotation_[1] = 0.0f;
    rotation_[2] = 0.0f;
}

void Camera::setPosition(float x, float y, float z) {
    position_[0] = x;
    position_[1] = y;
    position_[2] = z;
}

void Camera::getPosition(float& x, float& y, float& z) const {
    x = position_[0];
    y = position_[1];
    z = position_[2];
}

void Camera::setRotation(float pitch, float yaw, float roll) {
    rotation_[0] = pitch;
    rotation_[1] = yaw;
    rotation_[2] = roll;
}

void Camera::getRotation(float& pitch, float& yaw, float& roll) const {
    pitch = rotation_[0];
    yaw = rotation_[1];
    roll = rotation_[2];
}

void Camera::setPerspective(float fov, float aspect, float near, float far) {
    fov_ = fov;
    aspect_ = aspect;
    near_ = near;
    far_ = far;
}

void Camera::getViewMatrix(float* matrix) const {
    // Create view matrix from camera position and rotation
    // This is a simplified implementation
    
    float pitch = rotation_[0];
    float yaw = rotation_[1];
    float roll = rotation_[2];
    
    float cosPitch = std::cos(pitch);
    float sinPitch = std::sin(pitch);
    float cosYaw = std::cos(yaw);
    float sinYaw = std::sin(yaw);
    float cosRoll = std::cos(roll);
    float sinRoll = std::sin(roll);
    
    // Rotation matrix (combined pitch, yaw, roll)
    float r00 = cosYaw * cosRoll;
    float r01 = cosYaw * sinRoll;
    float r02 = -sinYaw;
    
    float r10 = sinPitch * sinYaw * cosRoll - cosPitch * sinRoll;
    float r11 = sinPitch * sinYaw * sinRoll + cosPitch * cosRoll;
    float r12 = sinPitch * cosYaw;
    
    float r20 = cosPitch * sinYaw * cosRoll + sinPitch * sinRoll;
    float r21 = cosPitch * sinYaw * sinRoll - sinPitch * cosRoll;
    float r22 = cosPitch * cosYaw;
    
    // Translation
    float tx = -(r00 * position_[0] + r10 * position_[1] + r20 * position_[2]);
    float ty = -(r01 * position_[0] + r11 * position_[1] + r21 * position_[2]);
    float tz = -(r02 * position_[0] + r12 * position_[1] + r22 * position_[2]);
    
    // Column-major 4x4 matrix
    matrix[0] = r00;  matrix[4] = r01;  matrix[8]  = r02;  matrix[12] = tx;
    matrix[1] = r10;  matrix[5] = r11;  matrix[9]  = r12;  matrix[13] = ty;
    matrix[2] = r20;  matrix[6] = r21;  matrix[10] = r22;  matrix[14] = tz;
    matrix[3] = 0.0f; matrix[7] = 0.0f; matrix[11] = 0.0f; matrix[15] = 1.0f;
}

void Camera::getProjectionMatrix(float* matrix) const {
    // Perspective projection matrix
    float f = 1.0f / std::tan(fov_ / 2.0f);
    float rangeInv = 1.0f / (near_ - far_);
    
    // Column-major 4x4 matrix
    matrix[0] = f / aspect_;
    matrix[1] = 0.0f;
    matrix[2] = 0.0f;
    matrix[3] = 0.0f;
    
    matrix[4] = 0.0f;
    matrix[5] = f;
    matrix[6] = 0.0f;
    matrix[7] = 0.0f;
    
    matrix[8] = 0.0f;
    matrix[9] = 0.0f;
    matrix[10] = (near_ + far_) * rangeInv;
    matrix[11] = -1.0f;
    
    matrix[12] = 0.0f;
    matrix[13] = 0.0f;
    matrix[14] = 2.0f * near_ * far_ * rangeInv;
    matrix[15] = 0.0f;
}

} // namespace CyberUI
