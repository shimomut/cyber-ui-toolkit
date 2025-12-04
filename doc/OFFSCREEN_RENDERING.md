# Off-Screen Rendering for Frame3D

## Overview

Off-screen rendering (render-to-texture) has been implemented for Frame3D to enable proper clipping when 3D transformations are applied. This solves the fundamental issue where scissor-based clipping breaks when Frame3D is rotated in 3D space.

## The Problem

Previously, clipping was implemented using the GPU's scissor test, which operates in screen space. When a Frame3D was rotated in 3D space:

1. The scissor rectangle remained axis-aligned in screen space
2. The rotated Frame2D content no longer aligned with the scissor rectangle
3. Clipping appeared incorrect or broken

## The Solution

Off-screen rendering solves this by:

1. **Render to Texture**: Frame3D content is first rendered to an off-screen texture using an orthographic projection
2. **Clipping in 2D Space**: All Frame2D clipping operations work correctly in this 2D render pass
3. **Texture as Quad**: The resulting texture is then rendered as a textured quad with 3D transformations applied
4. **Correct Clipping**: Since clipping happened in 2D space before 3D transformation, it remains correct

## Coordinate System Boundary

Off-screen rendering serves as the boundary between two coordinate systems:

1. **3D Space (Scene)**: Y-up, Frame3D positioned by center
2. **2D Space (Frame3D children)**: Y-down, top-left origin

The off-screen render pass:
- Renders Frame3D's children in 2D space (orthographic, Y-down)
- Produces a texture
- This texture is then rendered as a quad in 3D space (perspective, Y-up)
- This separation allows Frame3D to exist in 3D space while its children use 2D coordinates

## Implementation Details

### Frame3D Class Changes

**New Members:**
- `renderTargetWidth_`, `renderTargetHeight_`: Size of the render target texture
- `renderTargetTexture_`: Opaque pointer to the renderer-specific texture

**New Methods:**
- `isOffscreenRenderingEnabled()`: Always returns true (off-screen rendering is always enabled)
- `setSize(int, int)`: Set the render target size
- `getSize(int&, int&)`: Get the current render target size
- `getRenderTargetSize(int&, int&)`: Legacy method (same as getSize)

**Constructors:**
- `Frame3D()`: Default constructor with 800x600 render target
- `Frame3D(int width, int height)`: Constructor with custom render target size

### MetalRenderer Changes

**New Methods:**
- `getOrCreateRenderTarget(Frame3D*)`: Creates or retrieves cached render target texture
- `renderFrame3DToTexture(Frame3D*)`: Renders Frame3D content to off-screen texture
- `renderTexturedQuad(void*, float, float, const float*)`: Renders texture as a quad

**Render Pipeline:**

```
renderFrame3D(frame, viewProjMatrix)
  ├─ if offscreen rendering enabled:
  │   ├─ renderFrame3DToTexture(frame)
  │   │   ├─ Create/get render target texture
  │   │   ├─ Create off-screen render pass
  │   │   ├─ Render all children with orthographic projection
  │   │   └─ Clipping works correctly in 2D space
  │   │
  │   └─ renderTexturedQuad(texture, width, height, mvpMatrix)
  │       └─ Apply 3D transformations to the textured quad
  │
  └─ else: direct rendering (old path)
```

## Usage

### Python API

```python
import cyber_ui_core as ui

# Create Frame3D with default size (800x600)
frame3d = ui.Frame3D()
frame3d.set_name("MainFrame3D")
frame3d.set_position(0.0, 0.0, 0.0)

# Or create with custom size
frame3d = ui.Frame3D(1024, 768)

# Set size after creation
frame3d.set_size(800, 600)

# Off-screen rendering is always enabled for Frame3D

# Add children (Frame2D with clipping, etc.)
clip_panel = ui.Frame2D(400, 300)  # Frame2D also supports size in constructor
clip_panel.set_clipping_enabled(True)
frame3d.add_child(clip_panel)

# Now 3D rotation works with proper clipping!
frame3d.set_rotation(pitch, yaw, roll)
```

### Performance Considerations

**Pros:**
- Enables correct clipping with 3D transformations
- Clipping operations remain hardware-accelerated
- Texture can be reused across frames

**Cons:**
- Additional memory for render target texture
- Extra render pass overhead
- Texture size should match content resolution

**Recommendations:**
- Off-screen rendering is always enabled for Frame3D (no configuration needed)
- Set render target size to match your content dimensions or window size
- Use constructor with size parameters for convenience: `Frame3D(800, 600)`
- The renderer manages texture creation and caching automatically

## Example: Clipping Demo

The `samples/basic/clipping_demo.py` demonstrates off-screen rendering:

```python
# Create Frame3D with render target size
frame3d = ui.Frame3D()
frame3d.set_size(800, 700)  # Match window size

# Off-screen rendering is always enabled for Frame3D

# Animate with 3D rotation
frame3d.set_rotation(
    math.sin(time * 0.01) * 0.3,  # pitch
    math.cos(time * 0.008) * 0.2,  # yaw
    0.0                             # roll
)
```

The demo shows:
- Frame2D with clipping enabled (green borders)
- Animated rectangles and text that get clipped at boundaries
- 3D rotation of the entire Frame3D
- Clipping remains correct throughout the rotation

## Technical Notes

### Render Target Format

- **Pixel Format**: BGRA8Unorm (matches main framebuffer)
- **Usage**: RenderTarget | ShaderRead
- **Storage**: Private (GPU-only memory for performance)
- **Clear Color**: Transparent (0, 0, 0, 0)

### Coordinate Systems

1. **Off-screen Pass**: Uses orthographic projection centered at (0, 0)
2. **Main Pass**: Uses perspective projection with 3D transforms
3. **Texture Coordinates**: Standard (0,0) = top-left, (1,1) = bottom-right

### Caching

Render target textures are cached per Frame3D instance to avoid recreation overhead. The cache is managed by MetalRenderer and cleaned up on shutdown.

## Render Target Sizing

The render target size is configured via constructor or `set_size()` method:

1. **Default Size**: Frame3D defaults to 800x600 if no size is specified
2. **Constructor**: Create with custom size: `Frame3D(1024, 768)`
3. **Set Method**: Change size after creation: `frame3d.set_size(800, 600)`
4. **Consistency**: Both Frame2D and Frame3D use the same sizing approach

**Best Practices:**
- Set render target size to match your window dimensions for optimal quality
- Use the same size as your viewport to avoid scaling artifacts
- Larger sizes provide better quality but use more memory

## Future Enhancements

Potential improvements:
- Automatic size calculation based on content bounds
- Dynamic resolution scaling based on distance from camera
- Multi-sample anti-aliasing (MSAA) support for render targets
- Depth buffer support for complex 3D hierarchies
- Automatic window resize handling
