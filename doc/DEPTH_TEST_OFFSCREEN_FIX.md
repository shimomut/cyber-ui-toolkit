# Depth Testing Fix for Off-Screen Rendering

## Issue

Depth testing was enabled globally for all rendering, including off-screen rendering of Frame3D content to textures. This caused incorrect behavior because:

1. **Off-screen rendering is 2D**: Frame3D renders its 2D children (Frame2D, Rectangle, Text) to a texture in 2D space
2. **No depth needed**: All 2D content is rendered in a single plane (z=0), so depth testing is unnecessary
3. **Depth writes pollute buffer**: Writing depth values during 2D rendering could interfere with subsequent 3D rendering

## Solution

Disable depth testing and depth buffer writes during off-screen rendering for all backends.

### Changes Made

#### 1. OpenGL Renderer (`src/rendering/OpenGLRenderer.cpp`)

**In `renderFrame3DToTexture()`:**
- Disable depth test: `glDisable(GL_DEPTH_TEST)`
- Disable depth writes: `glDepthMask(GL_FALSE)`
- Clear only color buffer: `glClear(GL_COLOR_BUFFER_BIT)` (removed `GL_DEPTH_BUFFER_BIT`)
- Re-enable after rendering: `glEnable(GL_DEPTH_TEST)` and `glDepthMask(GL_TRUE)`

#### 2. Metal Renderer (`src/rendering/MetalRenderer.h` and `.mm`)

**Added depth stencil state management:**
- `depthStencilStateEnabled_`: Depth test enabled for main 3D rendering
- `depthStencilStateDisabled_`: Depth test disabled for 2D off-screen rendering

**In `setupShaders()`:**
- Created two depth stencil states:
  - Enabled: `MTLCompareFunctionLessEqual` with `depthWriteEnabled = YES`
  - Disabled: `MTLCompareFunctionAlways` with `depthWriteEnabled = NO`

**In `beginFrame()`:**
- Set enabled depth stencil state for main rendering

**In `renderFrame3DToTexture()`:**
- Set disabled depth stencil state for off-screen rendering

## Technical Details

### Why Disable Depth Testing for Off-Screen Rendering?

1. **2D Content Only**: Frame3D's off-screen pass renders 2D children (Frame2D, shapes, text) to a texture
2. **Single Plane**: All content is at z=0 in the orthographic projection
3. **Render Order**: 2D elements are rendered in tree order, not by depth
4. **Performance**: Skipping depth test/write is faster for 2D content

### Depth Testing Behavior

| Rendering Context | Depth Test | Depth Write | Purpose |
|------------------|------------|-------------|---------|
| Main 3D scene | Enabled | Enabled | Proper 3D occlusion |
| Off-screen 2D (Frame3D) | Disabled | Disabled | 2D content to texture |
| Final textured quad | Uses main state | Uses main state | Display in 3D space |

### OpenGL State Management

```cpp
// Before off-screen rendering
glDisable(GL_DEPTH_TEST);
glDepthMask(GL_FALSE);

// Render 2D content to texture
// ...

// After off-screen rendering
glEnable(GL_DEPTH_TEST);
glDepthMask(GL_TRUE);
```

### Metal State Management

```objc
// Main rendering (beginFrame)
[renderEncoder setDepthStencilState:depthStencilStateEnabled_];

// Off-screen rendering (renderFrame3DToTexture)
[offscreenEncoder setDepthStencilState:depthStencilStateDisabled_];
```

## Impact

### Before Fix
- Depth buffer was written during 2D off-screen rendering
- Unnecessary depth comparisons for 2D content
- Potential depth buffer pollution

### After Fix
- Clean separation: depth testing only for 3D rendering
- Improved performance for 2D off-screen passes
- Correct rendering behavior for all content types

## Testing

Verify the fix by:
1. Running existing samples (hierarchy_demo.py, clipping_demo.py)
2. Checking that Frame3D content renders correctly
3. Verifying no visual regressions in 3D transformations

## Related Documentation

- [Off-Screen Rendering](OFFSCREEN_RENDERING.md) - Overview of Frame3D off-screen rendering
- [3D Rendering](3D_RENDERING.md) - 3D rendering pipeline details
- [OpenGL Backend](OPENGL_BACKEND.md) - OpenGL implementation details
