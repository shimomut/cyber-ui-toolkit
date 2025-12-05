# OpenGL Off-Screen Rendering Implementation

## Overview

This document describes the implementation of off-screen rendering for Frame3D in the OpenGL backend, matching the functionality of the Metal backend.

## Implementation Date

December 4, 2024

## Purpose

Off-screen rendering is essential for Frame3D to properly handle:
- Clipping of 2D content within 3D-transformed frames
- Texture-based rendering of 2D UI elements in 3D space
- Proper depth sorting and compositing

## Architecture

### Key Components

1. **Framebuffer Objects (FBO)**
   - Used to render Frame3D content to texture
   - Created temporarily during `renderFrame3DToTexture()`
   - Cleaned up after rendering completes

2. **Render Target Textures**
   - Cached per Frame3D instance in `renderTargetCache_`
   - Created with dimensions from `Frame3D::getRenderTargetSize()`
   - Configured with GL_RGBA format and linear filtering

3. **Rendering Pipeline**
   ```
   Frame3D → renderFrame3DToTexture() → FBO + Texture
                                       ↓
                                  Render 2D children
                                       ↓
                                  Restore main framebuffer
                                       ↓
                            renderTexturedQuad() → Display in 3D space
   ```

## Implementation Details

### Frame3D.h Changes

```cpp
// Changed from:
bool isOffscreenRenderingEnabled() const { return false; }

// To:
bool isOffscreenRenderingEnabled() const { return true; }
```

### OpenGLRenderer.cpp Implementation

#### 1. getOrCreateRenderTarget()

Creates and caches render target textures:
- Generates GL texture with `glGenTextures()`
- Allocates storage with `glTexImage2D()` (GL_RGBA format)
- Sets filtering to GL_LINEAR for smooth rendering
- Caches texture ID in `renderTargetCache_`
- Stores texture pointer in Frame3D for later use

#### 2. renderFrame3DToTexture()

Renders Frame3D content to texture:
- Creates temporary FBO with `glGenFramebuffers()`
- Attaches render target texture to FBO
- Validates framebuffer completeness
- Saves current viewport and render target state
- Sets viewport to render target dimensions
- Clears to transparent (0,0,0,0)
- Creates orthographic projection for 2D rendering
- Renders all Frame3D children to texture
- Restores main framebuffer and state
- Cleans up temporary FBO

#### 3. renderTexturedQuad()

Displays the rendered texture in 3D space:
- Creates centered quad vertices (-halfW to +halfW, -halfH to +halfH)
- Sets up texture coordinates (0,0 to 1,1)
- Applies MVP matrix for 3D transformation
- Binds render target texture
- Renders quad with 6 vertices (2 triangles)

## Coordinate System

### Off-Screen Rendering Space
- Origin: Top-left (0, 0)
- X-axis: Right (positive)
- Y-axis: Down (positive)
- Matches Frame2D coordinate system

### Orthographic Projection
```cpp
float scaleX = 2.0f / rtWidth;
float scaleY = -2.0f / rtHeight;  // Negative for Y-flip

float orthoMatrix[16] = {
    scaleX, 0, 0, 0,
    0, scaleY, 0, 0,
    0, 0, 1, 0,
    -1, 1, 0, 1
};
```

Maps [0, width] × [0, height] → [-1, 1] × [1, -1] in clip space

## State Management

### Saved State During Off-Screen Rendering
- `currentRenderTargetWidth_`
- `currentRenderTargetHeight_`
- Viewport dimensions
- Scissor rectangle

### Restored After Off-Screen Rendering
- Main framebuffer binding (0)
- Original viewport dimensions
- Original scissor rectangle
- Original render target dimensions

## Performance Considerations

1. **Texture Caching**
   - Render targets created once per Frame3D
   - Reused across frames
   - Cleaned up in `shutdown()`

2. **FBO Management**
   - Created/destroyed per render call
   - Lightweight operation in modern OpenGL
   - Alternative: cache FBOs (not implemented)

3. **State Switching**
   - Minimal state changes
   - Viewport and scissor updates only
   - No shader recompilation

## Testing

### Verification Test
```python
import cyber_ui_core as ui

renderer = ui.create_opengl_renderer()
renderer.initialize(800, 600, 'Test')

scene = ui.SceneRoot()
camera = scene.get_camera()
camera.set_position(0, 0, 500)

frame3d = ui.Frame3D(400, 300)
scene.add_frame3d(frame3d)

rect = ui.Rectangle(200, 150)
rect.set_color(1.0, 0.0, 0.0, 1.0)
frame3d.add_child(rect)

renderer.begin_frame()
renderer.render_scene(scene)
renderer.end_frame()

assert frame3d.is_offscreen_rendering_enabled() == True
```

### Sample Demos
- `samples/basic/hierarchy_demo.py` - Tests Frame3D with multiple children
- `samples/basic/clipping_demo.py` - Tests clipping within Frame3D

## Comparison with Metal Backend

| Feature | Metal | OpenGL |
|---------|-------|--------|
| Off-screen rendering | ✓ | ✓ |
| Render target caching | ✓ | ✓ |
| FBO/Render pass | MTLRenderPassDescriptor | glFramebuffer |
| Texture format | MTLPixelFormatBGRA8Unorm | GL_RGBA |
| State management | Command buffer switching | Framebuffer binding |
| Coordinate system | Identical | Identical |

## Known Limitations

1. **No Depth Buffer**
   - Off-screen rendering doesn't include depth attachment
   - Not needed for 2D content rendering
   - Could be added if 3D content needed in Frame3D

2. **No Multisampling**
   - Render targets don't use MSAA
   - Could be added for higher quality

3. **Fixed Texture Format**
   - Always uses GL_RGBA
   - Could support other formats if needed

## Future Enhancements

1. **FBO Caching**
   - Cache FBOs per Frame3D to reduce creation overhead
   - Requires careful lifecycle management

2. **Depth Buffer Support**
   - Add depth attachment for 3D content in Frame3D
   - Useful for future 3D widget support

3. **Multisampling**
   - Add MSAA support for higher quality rendering
   - Requires resolve step to final texture

## References

- Metal implementation: `src/rendering/MetalRenderer.mm`
- Frame3D header: `src/core/Frame3D.h`
- OpenGL renderer: `src/rendering/OpenGLRenderer.cpp`
- Off-screen rendering overview: `doc/OFFSCREEN_RENDERING.md`
