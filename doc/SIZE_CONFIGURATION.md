# Size Configuration for Frame2D and Frame3D

## Overview

Both Frame2D and Frame3D now support consistent size configuration via constructors and `set_size()` methods.

## Frame2D Size Configuration

Frame2D uses size for defining its clipping region.

### C++ API

```cpp
// Default constructor (100x100)
auto frame2d = std::make_shared<Frame2D>();

// Constructor with size
auto frame2d = std::make_shared<Frame2D>(400.0f, 300.0f);

// Set size after creation
frame2d->setSize(400.0f, 300.0f);

// Get size
float width, height;
frame2d->getSize(width, height);
```

### Python API

```python
import cyber_ui_core as ui

# Default constructor (100x100)
frame2d = ui.Frame2D()

# Constructor with size
frame2d = ui.Frame2D(400.0, 300.0)

# Set size after creation
frame2d.set_size(400.0, 300.0)

# Get size
width, height = frame2d.get_size()
```

## Frame3D Size Configuration

Frame3D uses size for its off-screen render target texture. Off-screen rendering is always enabled.

### C++ API

```cpp
// Default constructor (800x600)
auto frame3d = std::make_shared<Frame3D>();

// Constructor with size
auto frame3d = std::make_shared<Frame3D>(1024, 768);

// Set size after creation
frame3d->setSize(1024, 768);

// Get size
int width, height;
frame3d->getSize(width, height);

// Legacy method (same as getSize)
frame3d->getRenderTargetSize(width, height);
```

### Python API

```python
import cyber_ui_core as ui

# Default constructor (800x600)
frame3d = ui.Frame3D()

# Constructor with size
frame3d = ui.Frame3D(1024, 768)

# Set size after creation
frame3d.set_size(1024, 768)

# Get size
width, height = frame3d.get_size()

# Legacy method (same as get_size)
width, height = frame3d.get_render_target_size()
```

## Design Rationale

### Consistency

Both Frame2D and Frame3D use the same API pattern:
- Default constructor with sensible defaults
- Constructor with size parameters
- `set_size()` method for runtime changes
- `get_size()` method for querying

### Type Differences

- **Frame2D**: Uses `float` for size (supports sub-pixel positioning)
- **Frame3D**: Uses `int` for size (texture dimensions must be integers)

### Default Sizes

- **Frame2D**: 100x100 (small default for clipping regions)
- **Frame3D**: 800x600 (common window size for render targets)

## Best Practices

### Frame2D

- Set size to match your content area
- Use clipping to prevent content overflow
- Size defines the scissor rectangle boundaries

### Frame3D

- Set render target size to match your window dimensions
- Larger sizes provide better quality but use more memory
- Consider performance vs quality tradeoffs
- Update size if window is resized

## Migration Guide

### Removed Methods

The following methods have been removed from Frame3D:

- `setOffscreenRenderingEnabled(bool)` - Off-screen rendering is now always enabled
- `setRenderTargetSize(int, int)` - Use `setSize(int, int)` instead

### Code Updates

**Before:**
```python
frame3d = ui.Frame3D()
frame3d.set_offscreen_rendering_enabled(True)
frame3d.set_render_target_size(800, 600)
```

**After:**
```python
# Option 1: Constructor
frame3d = ui.Frame3D(800, 600)

# Option 2: set_size method
frame3d = ui.Frame3D()
frame3d.set_size(800, 600)
```

## Examples

### Basic Usage

```python
import cyber_ui_core as ui

# Create window
renderer = ui.MetalRenderer()
renderer.initialize(800, 600, "Size Configuration Demo")

# Create scene
scene = ui.SceneRoot()
camera = ui.Camera()
camera.set_position(0, 0, 5)
scene.set_camera(camera)

# Create Frame3D with matching window size
frame3d = ui.Frame3D(800, 600)
frame3d.set_position(0, 0, 0)

# Create Frame2D with clipping
frame2d = ui.Frame2D(400, 300)
frame2d.set_position(0, 0)
frame2d.set_clipping_enabled(True)

# Add to hierarchy
frame3d.add_child(frame2d)
scene.add_frame3d(frame3d)

# Render loop
while not renderer.should_close():
    renderer.poll_events()
    if renderer.begin_frame():
        renderer.render_scene(scene)
        renderer.end_frame()
```

### Dynamic Resizing

```python
# Handle window resize
def on_window_resize(new_width, new_height):
    # Update Frame3D render target size
    frame3d.set_size(new_width, new_height)
    
    # Update camera aspect ratio
    camera.set_aspect(new_width / new_height)
```

## See Also

- [Off-Screen Rendering](OFFSCREEN_RENDERING.md) - Details on Frame3D off-screen rendering
- [Clipping Implementation](CLIPPING_IMPLEMENTATION.md) - How clipping works with Frame2D
