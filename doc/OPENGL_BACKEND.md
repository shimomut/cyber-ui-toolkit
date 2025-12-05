# OpenGL Backend

This document describes the OpenGL rendering backend for the Cyber UI Toolkit.

## Overview

The OpenGL backend provides cross-platform rendering support using OpenGL 3.3 Core Profile. It implements the same `Renderer` interface as the Metal backend, ensuring consistent behavior across platforms.

## Architecture

### Key Components

1. **OpenGLRenderer** - Main renderer class implementing the `Renderer` interface
2. **GLFW** - Window management and input handling
3. **OpenGL 3.3 Core** - Graphics API
4. **Shader Pipeline** - Vertex and fragment shaders for 2D rendering

### Features

- **2D Rendering**: Rectangles, text, and textured quads
- **Clipping Support**: Scissor test-based clipping for Frame2D
- **Texture Caching**: Efficient texture management with caching
- **Transparency**: Alpha blending support
- **Retina Display**: Automatic framebuffer scaling

## Building

### Prerequisites

- **GLFW**: Window management library
  ```bash
  # macOS
  brew install glfw
  
  # Linux
  sudo apt-get install libglfw3-dev
  ```

- **OpenGL**: Included with system (macOS) or Mesa (Linux)

### Build Commands

```bash
# Build with OpenGL backend
make build-opengl

# Or explicitly set backend
make build BACKEND=opengl

# Clean and rebuild
make clean
make build-opengl
```

## Usage

### Python API

```python
import cyber_ui_core as ui

# Create OpenGL renderer instead of Metal
renderer = ui.create_opengl_renderer()

# Initialize window
renderer.initialize(800, 600, "OpenGL Demo")

# Rest of the API is identical to Metal backend
scene = ui.SceneRoot()
camera = ui.Camera()
scene.set_camera(camera)

# Render loop
while not renderer.should_close():
    renderer.begin_frame()
    renderer.render_scene(scene)
    renderer.end_frame()
    renderer.poll_events()

renderer.shutdown()
```

### Backend Selection

The toolkit supports runtime backend selection:

```python
import sys
import cyber_ui_core as ui

# Choose backend based on platform or preference
if sys.platform == 'darwin':
    renderer = ui.create_metal_renderer()  # Preferred on macOS
else:
    renderer = ui.create_opengl_renderer()  # Cross-platform
```

## Implementation Details

### Coordinate System

The OpenGL backend maintains the same coordinate system as Metal:

- **Screen Space**: Origin at top-left, Y+ down
- **Object2D**: Position refers to top-left corner
- **Frame2D**: Top-left origin with Y+ down for children
- **NDC Conversion**: Automatic transformation to OpenGL's NDC space

### Shader Pipeline

**Vertex Shader**:
- Transforms 2D positions to 3D (z=0)
- Applies MVP matrix transformation
- Passes through color and texture coordinates

**Fragment Shader**:
- Samples texture
- Multiplies texture color by vertex color (for tinting)
- Outputs final RGBA color

### Texture Management

- **Caching**: Textures are cached by Image pointer
- **Format**: RGBA8 for images, text textures
- **Filtering**: Linear filtering for smooth scaling
- **Wrapping**: Clamp to edge to prevent artifacts

### Clipping

Clipping is implemented using OpenGL's scissor test:

1. Transform Frame2D bounds to screen space
2. Push scissor rect to stack
3. Apply scissor test
4. Render children
5. Pop scissor rect and restore previous state

## Platform Support

### macOS
- OpenGL 3.3 Core Profile
- Requires `GLFW_OPENGL_FORWARD_COMPAT`
- Native OpenGL framework

### Linux
- OpenGL 3.3 Core Profile
- Requires GLEW for extension loading
- Mesa or proprietary drivers

### Windows
- OpenGL 3.3 Core Profile
- Requires GLEW for extension loading
- DirectX alternative recommended for production

## Performance Considerations

### Texture Caching
- Textures are cached to avoid recreation
- Cache invalidation on Image object destruction
- GPU synchronization only when new textures created

### Batch Rendering
- Currently renders one quad at a time
- Future optimization: batch similar draw calls
- Minimize state changes

### Scissor Test
- Efficient hardware-accelerated clipping
- Stack-based management for nested clipping
- Automatic bounds clamping

## Limitations

### Current Implementation

1. **Text Rendering**: Placeholder implementation
   - Full implementation requires FreeType integration
   - Currently returns without rendering

2. **Off-screen Rendering**: Not yet implemented
   - Frame3D texture rendering incomplete
   - Requires framebuffer objects (FBOs)

3. **3D Rendering**: Basic support
   - Transform matrices implemented
   - Depth testing not fully configured

### Future Enhancements

- [ ] Complete text rendering with FreeType
- [ ] Implement off-screen rendering with FBOs
- [ ] Add depth testing for 3D scenes
- [ ] Optimize with instanced rendering
- [ ] Add MSAA support for anti-aliasing
- [ ] Implement shader hot-reloading

## Debugging

### Enable OpenGL Debug Output

```cpp
// Add to OpenGLRenderer::initialize()
#ifdef DEBUG
glEnable(GL_DEBUG_OUTPUT);
glDebugMessageCallback(debugCallback, nullptr);
#endif
```

### Common Issues

**Black Screen**:
- Check shader compilation errors
- Verify MVP matrix calculation
- Ensure viewport is set correctly

**Texture Not Showing**:
- Verify texture is bound before drawing
- Check texture coordinates (0-1 range)
- Ensure texture unit is active

**Clipping Not Working**:
- Verify scissor test is enabled
- Check scissor rect coordinates
- Ensure proper stack management

## Comparison with Metal Backend

| Feature | Metal | OpenGL |
|---------|-------|--------|
| Platform | macOS only | Cross-platform |
| Performance | Native, optimized | Good, portable |
| Text Rendering | Complete | Placeholder |
| Off-screen | Complete | TODO |
| Shader Language | MSL | GLSL |
| API Complexity | Modern | Legacy-compatible |

## References

- [OpenGL 3.3 Core Specification](https://www.khronos.org/registry/OpenGL/specs/gl/glspec33.core.pdf)
- [GLFW Documentation](https://www.glfw.org/documentation.html)
- [Learn OpenGL](https://learnopengl.com/)
