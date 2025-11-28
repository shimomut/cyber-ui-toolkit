# Basic Samples

This directory contains basic examples demonstrating the core features of the Cyber UI Toolkit.

## Prerequisites

Install required Python packages:

```bash
pip3 install Pillow numpy pybind11
```

Build the library:

```bash
make clean && make
```

## Available Samples

### test_rectangle.py

Interactive demo showing textured rectangles with the Metal renderer.

**Features demonstrated:**
- Loading images with Pillow
- Converting image data to RGBA format
- Creating Image objects from bitmap data
- Applying textures to rectangles
- Color tinting of textures
- Mixing textured and solid-color rectangles

**Run:**
```bash
PYTHONPATH=../../build python3 test_rectangle.py
```

**What you'll see:**
- Gradient texture (256x256)
- Checkerboard texture (128x128)
- Icon texture with transparency (64x64)
- Solid color rectangle (no texture)
- Tinted checkerboard texture

Press ESC or close the window to exit.

### test_image_loading.py

Non-interactive test that verifies image loading functionality.

**Features demonstrated:**
- Loading PNG images with Pillow
- Converting to RGBA format
- Creating cyber_ui Image objects
- Validating image properties

**Run:**
```bash
PYTHONPATH=../../build python3 test_image_loading.py
```

**Output:**
- Success/failure status for each image
- Image dimensions and channel count
- Overall test results

### test_texture_demo.py

Non-interactive demo showing texture application without opening a window.

**Features demonstrated:**
- Complete texture loading workflow
- Applying textures to rectangles
- Color tinting
- Console-based rendering output

**Run:**
```bash
PYTHONPATH=../../build python3 test_texture_demo.py
```

**Output:**
- Texture loading status
- Rectangle creation with textures
- Rendering information for each rectangle
- Summary statistics

## Code Structure

### Loading Images

```python
from PIL import Image as PILImage
import numpy as np
import cyber_ui_core as ui

def load_image_with_pillow(filepath):
    # Load with Pillow
    pil_img = PILImage.open(filepath)
    pil_img = pil_img.convert('RGBA')
    
    # Convert to numpy array
    img_array = np.array(pil_img, dtype=np.uint8)
    
    # Create cyber_ui Image
    ui_img = ui.Image()
    width, height = pil_img.size
    ui_img.load_from_data(img_array, width, height, 4)
    
    return ui_img
```

### Applying Textures

```python
# Create rectangle
rect = ui.Rectangle(256, 256)
rect.set_position(100, 100, 0)

# White color shows texture as-is
rect.set_color(1.0, 1.0, 1.0, 1.0)

# Apply texture
rect.set_image(gradient_img)

# Optional: Tint the texture
rect.set_color(1.0, 0.5, 0.5, 1.0)  # Red tint
```

### Rendering

```python
# Create renderer
renderer = ui.create_metal_renderer()
renderer.initialize(800, 600, "Window Title")

# Render loop
while not renderer.should_close():
    renderer.poll_events()
    
    if renderer.begin_frame():
        renderer.render_object(rect)
        renderer.end_frame()

renderer.shutdown()
```

## Test Images

Test images are located in `../data/`:
- `gradient.png` - RGB gradient (256x256)
- `checkerboard.png` - Black/white pattern (128x128)
- `icon.png` - RGBA icon with transparency (64x64)

See `../data/README.md` for more details.

## Troubleshooting

**Module not found error:**
```bash
# Make sure to set PYTHONPATH or run from correct directory
PYTHONPATH=../../build python3 test_rectangle.py
```

**Build errors:**
```bash
# Rebuild from scratch
make clean && make
```

**Missing dependencies:**
```bash
pip3 install Pillow numpy pybind11
```
