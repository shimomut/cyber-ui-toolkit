# OpenGL Coordinate System Fix

## Problem
Objects were not visible when running `python3 tests/test_opengl_visual.py` with the OpenGL backend.

## Root Cause
The orthographic projection matrix was using framebuffer dimensions (accounting for Retina/HiDPI scaling) instead of logical window dimensions. This caused a mismatch between:
- Object positions/sizes specified in logical coordinates (e.g., 600x600 window)
- The projection matrix expecting framebuffer coordinates (e.g., 1200x1200 on Retina displays)

## Solution
Changed the `renderObject()` function in `OpenGLRenderer.cpp` to use logical window dimensions (`windowWidth_`, `windowHeight_`) instead of framebuffer dimensions for the orthographic projection matrix.

### Key Changes

1. **Matrix Format**: Switched from row-major to column-major matrices throughout OpenGL renderer to match OpenGL's native format
2. **Matrix Multiplication**: Updated `multiplyMatrices()` to use column-major multiplication
3. **Coordinate System**: Fixed orthographic projection to properly map from top-left origin (Y-down) to OpenGL clip space (Y-up)
4. **Scaling**: Use logical window dimensions for projection, not framebuffer dimensions

### Before
```cpp
// Used framebuffer size (e.g., 1200x1200 on Retina)
int fbWidth, fbHeight;
glfwGetFramebufferSize(window, &fbWidth, &fbHeight);
float viewWidth = static_cast<float>(fbWidth);
float viewHeight = static_cast<float>(fbHeight);
```

### After
```cpp
// Use logical window size (e.g., 600x600)
float viewWidth = static_cast<float>(windowWidth_);
float viewHeight = static_cast<float>(windowHeight_);
```

## Testing
Run the following tests to verify the fix:
```bash
make build-opengl
python3 tests/test_opengl_capture.py  # Automated test with pixel verification
python3 tests/test_opengl_quick.py    # Visual test with 5-second window
python3 tests/test_opengl_visual.py   # Full visual test
```

## Related Files
- `src/rendering/OpenGLRenderer.cpp` - Main fix location
- `tests/test_opengl_capture.py` - Automated verification test
- `tests/test_opengl_quick.py` - Quick visual test
- `tests/test_opengl_visual.py` - Original visual test
