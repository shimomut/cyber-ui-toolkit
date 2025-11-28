# Capture System Samples

Quick reference for using the rendering capture system.

## Basic Capture

```python
import cyber_ui_core as ui

renderer = ui.create_metal_renderer()
renderer.initialize(800, 600, "My App")

# ... setup scene and render ...

# Save frame to PNG
renderer.save_capture("output.png")
```

## Raw Data Capture

```python
# Get pixel data as bytes
data, width, height = renderer.capture_frame()

if data is not None:
    print(f"Captured {width}x{height} frame")
    print(f"Data size: {len(data)} bytes (BGRA format)")
```

## Capture Animation Frames

```python
for frame_num in range(60):
    # Update scene
    my_object.set_rotation(0, 0, frame_num * 6 * 3.14159 / 180.0)
    
    # Render
    renderer.begin_frame()
    renderer.render_scene(scene)
    renderer.end_frame()
    
    # Capture every 10th frame
    if frame_num % 10 == 0:
        renderer.save_capture(f"frame_{frame_num:04d}.png")
```

## Analyze Pixels

```python
import struct

data, width, height = renderer.capture_frame()
pixels = struct.unpack(f'{len(data)}B', data)

# Get pixel at (x, y) - BGRA format
x, y = 100, 100
offset = (y * width + x) * 4
blue = pixels[offset]
green = pixels[offset + 1]
red = pixels[offset + 2]
alpha = pixels[offset + 3]
```

## Compare Images

```bash
# Compare two captures
python tests/compare_captures.py image1.png image2.png

# With tolerance
python tests/compare_captures.py image1.png image2.png 5

# Create diff image
python tests/compare_captures.py image1.png image2.png --diff diff.png
```

## Running Tests

```bash
# Run all capture tests
python tests/test_capture.py

# Run capture demo
python samples/basic/capture_demo.py
```

## Common Use Cases

### Debug Texture Loading
```python
image = ui.Image()
image.load_from_file("texture.png")
rect = ui.Rectangle(300, 300)
rect.set_image(image)

# Render and capture to verify texture loaded correctly
renderer.begin_frame()
renderer.render_scene(scene)
renderer.end_frame()
renderer.save_capture("texture_debug.png")
```

### Verify Colors
```python
rect.set_color(1.0, 0.0, 0.0, 1.0)  # Red

# Capture and check pixels are red
data, w, h = renderer.capture_frame()
# Verify red channel is high, others low
```

### Regression Testing
```python
# Capture reference
renderer.save_capture("reference.png")

# Make changes...

# Capture new version
renderer.save_capture("current.png")

# Compare programmatically
from tests.compare_captures import compare_images
result = compare_images("reference.png", "current.png", threshold=5)
assert result['identical'] or result['diff_percentage'] < 1.0
```

## See Also

- [Full Documentation](/doc/CAPTURE_SYSTEM.md)
- [Troubleshooting Guide](/doc/TROUBLESHOOTING.md)
