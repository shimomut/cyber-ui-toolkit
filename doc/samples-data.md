# Test Image Data

This directory contains test images used in the Cyber UI Toolkit samples.

## Available Images

### gradient.png (256x256)
- RGB gradient pattern
- Red channel varies horizontally (0-255)
- Green channel varies vertically (0-255)
- Blue channel constant at 128
- Useful for testing color rendering and interpolation

### checkerboard.png (128x128)
- Black and white checkerboard pattern
- 16x16 pixel squares
- Useful for testing texture mapping and alignment

### icon.png (64x64)
- RGBA format with transparency
- Orange circle with yellow center
- Useful for testing alpha blending and small texture rendering

## Usage

These images are loaded in the sample applications using Python Imaging Library (Pillow):

```python
from PIL import Image as PILImage
import numpy as np
import cyber_ui_core as ui

# Load image with Pillow
pil_img = PILImage.open("../data/gradient.png")
pil_img = pil_img.convert('RGBA')

# Convert to numpy array
img_array = np.array(pil_img, dtype=np.uint8)

# Create cyber_ui Image object
ui_img = ui.Image()
width, height = pil_img.size
ui_img.load_from_data(img_array, width, height, 4)

# Apply texture to a rectangle
rect = ui.Rectangle(256, 256)
rect.set_position(100, 100, 0)
rect.set_color(1.0, 1.0, 1.0, 1.0)  # White to show texture as-is
rect.set_image(ui_img)

# You can also tint textures by using colors other than white
rect.set_color(1.0, 0.5, 0.5, 1.0)  # Red tint
```

## Regenerating Images

To regenerate these test images, run:

```bash
python3 -c "from PIL import Image, ImageDraw
import os

os.makedirs('samples/data', exist_ok=True)

# Gradient
img1 = Image.new('RGB', (256, 256))
pixels = img1.load()
for y in range(256):
    for x in range(256):
        pixels[x, y] = (x, y, 128)
img1.save('samples/data/gradient.png')

# Checkerboard
img2 = Image.new('RGB', (128, 128))
pixels = img2.load()
for y in range(128):
    for x in range(128):
        if (x // 16 + y // 16) % 2 == 0:
            pixels[x, y] = (255, 255, 255)
        else:
            pixels[x, y] = (0, 0, 0)
img2.save('samples/data/checkerboard.png')

# Icon
img3 = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
draw = ImageDraw.Draw(img3)
draw.ellipse([8, 8, 56, 56], fill=(255, 100, 50, 255))
draw.ellipse([20, 20, 44, 44], fill=(255, 200, 100, 255))
img3.save('samples/data/icon.png')
"
```
