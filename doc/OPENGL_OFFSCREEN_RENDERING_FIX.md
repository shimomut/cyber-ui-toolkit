# OpenGL Offscreen Rendering Fix

## Issue
The hierarchy demo (`make run-hierarchy-opengl`) was showing a blank window with no rendered content, while the simple visual test (`tests/test_opengl_visual.py`) worked correctly.

## Root Cause
Frame3D had offscreen rendering hardcoded to always return `true` in `isOffscreenRenderingEnabled()`. The OpenGL renderer's offscreen rendering functions (`renderFrame3DToTexture` and `renderTexturedQuad`) were not implemented - they were empty stubs. This caused all Frame3D content to be silently skipped during rendering.

## Solution
Changed `Frame3D::isOffscreenRenderingEnabled()` to return `false` to use the direct rendering path, which is fully implemented in the OpenGL renderer.

### Changes Made

1. **src/core/Frame3D.h**
   - Changed `isOffscreenRenderingEnabled()` from returning `true` to `false`
   - Updated comment to reflect that offscreen rendering is disabled for now

2. **src/rendering/OpenGLRenderer.cpp**
   - Added depth testing support (`glEnable(GL_DEPTH_TEST)`) for proper 3D rendering
   - Removed debug output statements

## Technical Details

### Rendering Paths
The OpenGL renderer has two rendering paths for Frame3D:

1. **Offscreen Rendering Path** (not implemented)
   - Renders Frame3D content to a texture via `renderFrame3DToTexture()`
   - Renders the texture as a 3D quad via `renderTexturedQuad()`
   - Allows for advanced effects and proper clipping with 3D transforms

2. **Direct Rendering Path** (fully implemented)
   - Directly renders Frame3D children with 3D transforms
   - Combines Frame3D's model matrix with view-projection matrix
   - Renders all 2D children with the combined MVP matrix

### Why Direct Rendering Works
- Frame3D's position, rotation, and scale are encoded in a model matrix
- This matrix is multiplied with the camera's view-projection matrix
- The resulting MVP matrix is passed down to all children
- Each child's local coordinates are transformed through this MVP matrix
- The vertex shader applies the final transformation: `gl_Position = uMVPMatrix * vec4(position, 0.0, 1.0)`

## Future Work
To implement offscreen rendering for OpenGL:

1. Create framebuffer objects (FBOs) for each Frame3D
2. Implement `renderFrame3DToTexture()` to render to FBO
3. Implement `renderTexturedQuad()` to render the FBO texture as a 3D quad
4. Add proper resource management for FBOs and textures
5. Make offscreen rendering configurable per Frame3D

## Testing
Both rendering modes now work:
- `python3 tests/test_opengl_visual.py` - Simple 2D rendering
- `make run-hierarchy-opengl` - Complex 3D hierarchy with Frame3D objects

## Related Files
- `src/core/Frame3D.h` - Frame3D class definition
- `src/core/Frame3D.cpp` - Frame3D implementation
- `src/rendering/OpenGLRenderer.h` - OpenGL renderer interface
- `src/rendering/OpenGLRenderer.cpp` - OpenGL renderer implementation
- `samples/basic/hierarchy_demo.py` - Demo that uses Frame3D
