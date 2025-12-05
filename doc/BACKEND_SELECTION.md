# Backend Selection Guide

This guide explains how to choose and build with different rendering backends in the Cyber UI Toolkit.

## Available Backends

### Metal (Default)
- **Platform**: macOS only
- **Performance**: Native, optimized for Apple hardware
- **Dependencies**: None (built into macOS)
- **Status**: ✅ Fully implemented

### OpenGL
- **Platform**: Cross-platform (macOS, Linux, Windows)
- **Performance**: Good, portable
- **Dependencies**: GLFW 3.x
- **Status**: ✅ Core features implemented

## Installation

### Metal Backend (macOS)
No additional dependencies required - Metal is built into macOS.

```bash
# Build with Metal
make build-metal
```

### OpenGL Backend (Cross-platform)

**macOS**:
```bash
# Install GLFW
brew install glfw

# Build with OpenGL
make build-opengl
```

**Linux**:
```bash
# Ubuntu/Debian
sudo apt-get install libglfw3-dev

# Fedora
sudo dnf install glfw-devel

# Build with OpenGL
make build-opengl
```

**Windows**:
- Download GLFW from https://www.glfw.org/download.html
- Update Makefile paths for Windows
- Build with OpenGL

## Building

### Quick Start

```bash
# Default (Metal on macOS)
make build

# Explicitly choose backend
make build-metal    # Metal backend
make build-opengl   # OpenGL backend

# Clean and rebuild
make clean && make build-metal
```

### Verify Installation

```bash
# Test which backends are available
python3 tests/test_backend_selection.py

# Test OpenGL specifically
python3 tests/test_opengl_backend.py
```

## Usage in Python

### Basic Usage

```python
import sys
sys.path.insert(0, 'build')
import cyber_ui_core as ui

# Metal backend (if built with BACKEND=metal)
renderer = ui.create_metal_renderer()

# OpenGL backend (if built with BACKEND=opengl)
renderer = ui.create_opengl_renderer()

# Initialize and use (API is identical)
renderer.initialize(800, 600, "My App")
# ... render loop ...
renderer.shutdown()
```

### Platform-Specific Selection

```python
import sys
import cyber_ui_core as ui

# Choose backend based on platform
if sys.platform == 'darwin':
    # macOS - prefer Metal if available
    try:
        renderer = ui.create_metal_renderer()
        print("Using Metal backend")
    except AttributeError:
        renderer = ui.create_opengl_renderer()
        print("Using OpenGL backend")
else:
    # Linux/Windows - use OpenGL
    renderer = ui.create_opengl_renderer()
    print("Using OpenGL backend")
```

### Runtime Detection

```python
import cyber_ui_core as ui

# Check which backends are available
has_metal = hasattr(ui, 'create_metal_renderer')
has_opengl = hasattr(ui, 'create_opengl_renderer')

print(f"Metal available: {has_metal}")
print(f"OpenGL available: {has_opengl}")

# Use available backend
if has_metal:
    renderer = ui.create_metal_renderer()
elif has_opengl:
    renderer = ui.create_opengl_renderer()
else:
    raise RuntimeError("No rendering backend available")
```

## Feature Comparison

| Feature | Metal | OpenGL |
|---------|-------|--------|
| 2D Rectangles | ✅ | ✅ |
| Textures | ✅ | ✅ |
| Text Rendering | ✅ | ⚠️ Placeholder |
| Clipping | ✅ | ✅ |
| Frame Capture | ✅ | ✅ |
| Off-screen Rendering | ✅ | ⚠️ TODO |
| 3D Transforms | ✅ | ✅ |
| Retina Display | ✅ | ✅ |

## Troubleshooting

### "GLFW/glfw3.h not found"

**Solution**: Install GLFW
```bash
# macOS
brew install glfw

# Linux
sudo apt-get install libglfw3-dev
```

### "create_opengl_renderer not found"

**Cause**: Library was built with Metal backend

**Solution**: Rebuild with OpenGL
```bash
make clean && make build-opengl
```

### "create_metal_renderer not found"

**Cause**: Library was built with OpenGL backend

**Solution**: Rebuild with Metal
```bash
make clean && make build-metal
```

### Linker errors with GLFW

**Cause**: GLFW not in standard path

**Solution**: Update Makefile with correct GLFW path
```makefile
GLFW_PREFIX := /path/to/glfw
CXXFLAGS += -I$(GLFW_PREFIX)/include
LDFLAGS += -L$(GLFW_PREFIX)/lib -lglfw
```

## Performance Considerations

### Metal Backend
- **Best for**: macOS production applications
- **Pros**: Native performance, GPU-optimized, no dependencies
- **Cons**: macOS only

### OpenGL Backend
- **Best for**: Cross-platform development, testing
- **Pros**: Portable, widely supported
- **Cons**: Slightly lower performance than native APIs

## Recommendations

**For Production**:
- macOS: Use Metal backend
- Linux: Use OpenGL backend
- Windows: Use OpenGL backend (or DirectX in future)

**For Development**:
- Use Metal on macOS for best performance
- Use OpenGL for cross-platform testing

**For Distribution**:
- Provide separate builds for each platform
- Or build with OpenGL for maximum compatibility

## Future Backends

Planned backend support:
- [ ] Vulkan (Linux, Windows, Android)
- [ ] DirectX 12 (Windows)
- [ ] WebGPU (Web browsers)

## See Also

- [OpenGL Backend Documentation](OPENGL_BACKEND.md)
- [Build System](../Makefile)
- [Backend Tests](../tests/test_backend_selection.py)
