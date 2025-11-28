# Cyber UI Toolkit

A high-performance GUI toolkit library using 3D graphics API backend (Metal/Vulkan/OpenGL).

## Architecture

The library consists of two layers:

**Layer 1: Graphics Primitive Rendering (C++)**
- Low-level 3D graphics API integration (Metal on macOS)
- High-performance rendering primitives
- Image and texture management
- Python bindings via pybind11

**Layer 2: UI Toolkit (Python)** *(Coming soon)*
- Widget system and components
- Layout management
- Event handling and input
- Theme and styling system

## Features

- ✅ Metal renderer backend for macOS
- ✅ 2D shape rendering (rectangles)
- ✅ Image loading with Pillow integration
- ✅ Texture mapping and color tinting
- ✅ Scene graph with parent-child relationships
- ✅ Frame capture system for debugging and testing
- ✅ Python bindings for easy application development

## Quick Start

### Prerequisites

```bash
# Install Python dependencies
pip3 install pybind11 Pillow numpy

# macOS: Xcode Command Line Tools required
xcode-select --install
```

### Build

```bash
# Build the library
make

# Or rebuild from scratch
make clean && make
```

### Run Samples

```bash
# Interactive texture demo (opens window)
PYTHONPATH=build python3 samples/basic/test_rectangle.py

# Non-interactive demos
PYTHONPATH=build python3 samples/basic/test_image_loading.py
PYTHONPATH=build python3 samples/basic/test_texture_demo.py
```

## Usage Example

```python
import sys
sys.path.insert(0, 'build')

import cyber_ui_core as ui
from PIL import Image as PILImage
import numpy as np

# Load image with Pillow
pil_img = PILImage.open('samples/data/gradient.png')
pil_img = pil_img.convert('RGBA')
img_array = np.array(pil_img, dtype=np.uint8)

# Create cyber_ui Image
ui_img = ui.Image()
width, height = pil_img.size
ui_img.load_from_data(img_array, width, height, 4)

# Create textured rectangle
rect = ui.Rectangle(256, 256)
rect.set_position(100, 100, 0)
rect.set_color(1.0, 1.0, 1.0, 1.0)  # White
rect.set_image(ui_img)

# Create renderer and render
renderer = ui.create_metal_renderer()
renderer.initialize(800, 600, "Cyber UI Demo")

while not renderer.should_close():
    renderer.poll_events()
    if renderer.begin_frame():
        renderer.render_object(rect)
        renderer.end_frame()

renderer.shutdown()
```

## Project Structure

```
cyber-ui-toolkit/
├── src/                    # C++ source code
│   ├── core/              # Core components (Object2D, Frame3D, Frame2D)
│   ├── rendering/         # Rendering backend (Metal, shapes, images)
│   └── bindings/          # Python bindings (pybind11)
├── samples/               # Example applications
│   ├── basic/            # Basic usage examples
│   └── data/             # Test images and assets
├── build/                 # Build output
├── Makefile              # Build configuration
└── README.md             # This file
```

## Documentation

- [Project Structure](/.kiro/steering/project-structure.md) - Directory organization and conventions
- [Capture System](/doc/CAPTURE_SYSTEM.md) - Frame capture for debugging and testing
- [Basic Samples](/samples/basic/README.md) - Sample code documentation
- [Test Images](/samples/data/README.md) - Test image documentation

## Development

### Build Targets

```bash
make build         # Build the library
make clean         # Remove build artifacts
make rebuild       # Clean and build
make install-deps  # Install Python dependencies
make run-basic     # Build and run basic sample
make help          # Show all targets
```

### Adding New Features

1. Add C++ implementation in `src/`
2. Expose to Python in `src/bindings/python_bindings.cpp`
3. Update `Makefile` if adding new source files
4. Create samples in `samples/`
5. Update documentation

## Requirements

- **macOS**: 10.13+ (for Metal support)
- **Python**: 3.8+
- **Compiler**: Clang with C++17 support
- **Dependencies**: pybind11, Pillow, numpy

## License

*(Add your license here)*

## Contributing

*(Add contribution guidelines here)*
