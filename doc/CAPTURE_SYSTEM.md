# Rendering Capture System

The Cyber UI Toolkit includes a comprehensive rendering capture system for debugging, testing, and troubleshooting rendering issues. This system allows you to capture rendered frames as images or raw pixel data.

## Overview

The capture system provides two main capabilities:

1. **Frame Capture**: Save rendered frames as PNG images
2. **Raw Data Access**: Access pixel data directly for analysis

## API Reference

### C++ API

```cpp
// Capture current frame to raw pixel data
bool captureFrame(std::vector<uint8_t>& pixelData, int& width, int& height);

// Save current frame directly to PNG file
bool saveCapture(const char* filename);
```

### Python API

```python
# Save current frame to PNG file
renderer.save_capture("output.png")

# Get raw pixel data
data, width, height = renderer.capture_frame()
# data is bytes object in BGRA format (4 bytes per pixel)
```

## Usage Examples

### Basic Frame Capture

```python
import cyber_ui_core as ui

# Create and initialize renderer
renderer = ui.create_metal_renderer()
renderer.initialize(800, 600, "My App")

# Create scene
scene = ui.SceneRoot()
camera = ui.Camera()
camera.set_position(0, 0, 5)
scene.set_camera(camera)

# Add content to scene
frame = ui.Frame3D()
rect = ui.Rectangle(200, 200)
rect.set_color(1.0, 0.0, 0.0, 1.0)
frame.add_child(rect)
scene.add_frame3d(frame)

# Render a few frames to ensure everything is loaded
for _ in range(3):
    renderer.begin_frame()
    renderer.render_scene(scene)
    renderer.end_frame()

# Capture the frame
renderer.save_capture("my_render.png")

renderer.shutdown()
```

### Capturing Animation Frames

```python
# Capture multiple frames from an animation
for frame_num in range(60):
    # Update animation
    angle = frame_num * 6  # 6 degrees per frame
    my_object.set_rotation(0, 0, angle * 3.14159 / 180.0)
    
    # Render
    renderer.begin_frame()
    renderer.render_scene(scene)
    renderer.end_frame()
    
    # Capture every 10th frame
    if frame_num % 10 == 0:
        renderer.save_capture(f"frame_{frame_num:04d}.png")
```

### Analyzing Raw Pixel Data

```python
import struct

# Capture raw pixel data
data, width, height = renderer.capture_frame()

if data is not None:
    # Convert bytes to list of integers
    pixels = struct.unpack(f'{len(data)}B', data)
    
    # Access specific pixel (BGRA format)
    x, y = 100, 100
    offset = (y * width + x) * 4
    
    blue = pixels[offset]
    green = pixels[offset + 1]
    red = pixels[offset + 2]
    alpha = pixels[offset + 3]
    
    print(f"Pixel at ({x}, {y}): R={red}, G={green}, B={blue}, A={alpha}")
    
    # Calculate average color
    total_r = sum(pixels[i+2] for i in range(0, len(pixels), 4))
    total_g = sum(pixels[i+1] for i in range(0, len(pixels), 4))
    total_b = sum(pixels[i] for i in range(0, len(pixels), 4))
    
    num_pixels = width * height
    avg_r = total_r / num_pixels
    avg_g = total_g / num_pixels
    avg_b = total_b / num_pixels
    
    print(f"Average color: R={avg_r:.1f}, G={avg_g:.1f}, B={avg_b:.1f}")
```

### Using with NumPy

```python
import numpy as np

# Capture frame
data, width, height = renderer.capture_frame()

if data is not None:
    # Convert to numpy array
    pixels = np.frombuffer(data, dtype=np.uint8)
    pixels = pixels.reshape((height, width, 4))  # BGRA format
    
    # Convert BGRA to RGB
    rgb = pixels[:, :, [2, 1, 0]]  # Swap B and R channels
    
    # Now you can use numpy operations
    print(f"Shape: {rgb.shape}")
    print(f"Mean color: {rgb.mean(axis=(0, 1))}")
    print(f"Max values: {rgb.max(axis=(0, 1))}")
```

## Testing and Troubleshooting

### Running Capture Tests

The toolkit includes comprehensive tests for the capture system:

```bash
# Run all capture tests
python tests/test_capture.py

# Tests include:
# - Basic shape capture
# - Textured shape capture
# - Raw data capture and analysis
# - Animated frame capture
```

### Comparing Captures

Use the comparison utility to check for rendering differences:

```bash
# Compare two images
python tests/compare_captures.py image1.png image2.png

# Compare with tolerance (allow up to 5 units difference per pixel)
python tests/compare_captures.py image1.png image2.png 5

# Create visual diff image
python tests/compare_captures.py image1.png image2.png --diff diff.png
```

The comparison tool provides:
- Pixel-by-pixel comparison
- Difference statistics (max, average, percentage)
- Visual diff image generation
- Configurable tolerance threshold

### Common Troubleshooting Scenarios

#### 1. Verifying Texture Loading

```python
# Capture frame with texture
image = ui.Image()
if image.load_from_file("texture.png"):
    rect = ui.Rectangle(300, 300)
    rect.set_image(image)
    # ... render and capture
    renderer.save_capture("texture_test.png")
    # Visually inspect the captured image
```

#### 2. Debugging Color Issues

```python
# Set known color and verify
rect.set_color(1.0, 0.0, 0.0, 1.0)  # Pure red

# Render and capture
renderer.begin_frame()
renderer.render_scene(scene)
renderer.end_frame()

data, width, height = renderer.capture_frame()
# Check if pixels are actually red (high R, low G/B)
```

#### 3. Checking Transform Hierarchy

```python
# Capture at different hierarchy levels
parent = ui.Frame3D()
child = ui.Frame3D()
parent.add_child(child)

# Add visible content to child
rect = ui.Rectangle(100, 100)
rect.set_color(0.0, 1.0, 0.0, 1.0)
child.add_child(rect)

# Test different transforms
parent.set_position(100, 0, 0)
renderer.save_capture("parent_offset.png")

child.set_position(50, 50, 0)
renderer.save_capture("child_offset.png")
```

#### 4. Regression Testing

```python
# Capture reference image
renderer.save_capture("reference.png")

# Make changes to rendering code...

# Capture new image
renderer.save_capture("current.png")

# Compare
# python tests/compare_captures.py reference.png current.png
```

## Pixel Format

Captured pixel data uses **BGRA format** (Blue, Green, Red, Alpha):
- 4 bytes per pixel
- Byte order: [B, G, R, A]
- Values: 0-255 per channel
- Alpha: 255 = fully opaque, 0 = fully transparent

### Converting to Other Formats

```python
# BGRA to RGB
def bgra_to_rgb(data, width, height):
    rgb = bytearray(width * height * 3)
    for i in range(0, len(data), 4):
        rgb_idx = (i // 4) * 3
        rgb[rgb_idx] = data[i + 2]      # R
        rgb[rgb_idx + 1] = data[i + 1]  # G
        rgb[rgb_idx + 2] = data[i]      # B
    return bytes(rgb)

# BGRA to RGBA
def bgra_to_rgba(data):
    rgba = bytearray(len(data))
    for i in range(0, len(data), 4):
        rgba[i] = data[i + 2]      # R
        rgba[i + 1] = data[i + 1]  # G
        rgba[i + 2] = data[i]      # B
        rgba[i + 3] = data[i + 3]  # A
    return bytes(rgba)
```

## Performance Considerations

- **Frame capture is synchronous**: It waits for GPU operations to complete
- **Use sparingly in production**: Capture adds overhead to rendering
- **Batch captures**: If capturing multiple frames, render several frames between captures
- **File I/O**: Saving to disk is slower than capturing to memory

### Optimization Tips

```python
# Good: Capture after rendering is stable
for _ in range(5):  # Let rendering stabilize
    renderer.begin_frame()
    renderer.render_scene(scene)
    renderer.end_frame()

renderer.save_capture("output.png")  # Now capture

# Avoid: Capturing every frame in a loop
for i in range(1000):
    renderer.begin_frame()
    renderer.render_scene(scene)
    renderer.end_frame()
    renderer.save_capture(f"frame_{i}.png")  # Too slow!
```

## Integration with CI/CD

The capture system can be integrated into automated testing:

```python
def test_rendering_regression():
    """Automated regression test for rendering."""
    renderer = setup_renderer()
    scene = create_test_scene()
    
    # Render
    for _ in range(3):
        renderer.begin_frame()
        renderer.render_scene(scene)
        renderer.end_frame()
    
    # Capture
    renderer.save_capture("tests/output/current.png")
    
    # Compare with reference
    result = compare_images(
        "tests/reference/expected.png",
        "tests/output/current.png",
        threshold=5  # Allow minor differences
    )
    
    assert result['identical'] or result['diff_percentage'] < 1.0, \
        f"Rendering differs by {result['diff_percentage']:.2f}%"
```

## Limitations

- **Platform-specific**: Currently implemented for Metal (macOS)
- **Window must be visible**: Capture requires an active rendering context
- **No offscreen rendering**: Captures from the displayed window
- **Format**: Output is always PNG for file saves

## Future Enhancements

Potential improvements to the capture system:

- Offscreen rendering support
- Additional output formats (JPEG, BMP, etc.)
- Capture specific regions of the frame
- Capture depth buffer and stencil buffer
- Video capture (multiple frames to video file)
- GPU-accelerated comparison

## See Also

- [Troubleshooting Guide](TROUBLESHOOTING.md) - General rendering troubleshooting
- [Texture Implementation](TEXTURE_IMPLEMENTATION.md) - Texture-specific debugging
- [3D Rendering](3D_RENDERING.md) - 3D rendering concepts
