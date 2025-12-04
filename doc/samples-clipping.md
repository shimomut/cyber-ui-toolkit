# Frame2D Clipping Demo

## Overview

The clipping demo (`samples/basic/clipping_demo.py`) demonstrates Frame2D's hardware-accelerated clipping capability using Metal's scissor test.

## Running the Demo

```bash
# Normal mode
python3 samples/basic/clipping_demo.py

# With frame capture
python3 samples/basic/clipping_demo.py --capture
```

## What You'll See

A single Frame2D panel with:
- **Green borders** marking the clipping boundary (500x600 pixels)
- **5 animated rectangles** with textures (gradient, checkerboard, icon) moving vertically
- **4 animated text elements** moving horizontally
- **Slow animations** (10x slower than normal) for clear visualization

Content that moves outside the green borders is automatically clipped and not rendered.

## Key Features Demonstrated

### 1. Hardware Clipping
- Uses Metal's native scissor test
- No CPU-side pixel manipulation
- Efficient GPU-based clipping

### 2. Transform-Aware Clipping
- Works correctly with Frame3D rotation
- Handles Frame3D scaling
- Properly transforms clipping bounds to screen space

### 3. Animated Content
- Rectangles oscillate vertically with 200-pixel range
- Text elements wave horizontally with 150-pixel range
- Smooth 60fps animation at 10x slower speed

### 4. Visual Feedback
- Green borders clearly show clipping boundary
- Dark background inside the frame
- Title and subtitle text

## Code Structure

```python
# Create Frame2D with clipping
clip_panel = ui.Frame2D()
clip_panel.set_position(150.0, 50.0)
clip_panel.set_size(500.0, 600.0)
clip_panel.set_clipping_enabled(True)  # Enable clipping

# Add border rectangles to visualize clipping boundary
border_top = ui.Rectangle(500.0, 3.0)
border_top.set_color(0.3, 1.0, 0.3, 1.0)  # Green
clip_panel.add_child(border_top)

# Add animated content
for i in range(5):
    rect = ui.Rectangle(140.0, 140.0)
    rect.set_position(180.0, 120.0 + i * 100.0)
    if gradient_img:
        rect.set_image(gradient_img)
    clip_panel.add_child(rect)

# Animation loop
while not renderer.should_close():
    time = frame_count * 0.016
    
    # Slow vertical oscillation (10x slower)
    for i, rect in enumerate(animated_rects):
        base_y = 120.0 + i * 100.0
        offset_y = math.sin(time * 0.2 + i * 0.8) * 200.0
        rect.set_position(180.0, base_y + offset_y)
```

## Technical Details

### Clipping Implementation
- **Method**: Metal scissor test (`MTLScissorRect`)
- **Coordinate Transform**: World space → Screen space via MVP matrix
- **Nested Support**: Automatic intersection of parent/child clipping regions
- **Stack-Based**: Push/pop scissor rects for proper nesting

### Animation Parameters
- **Rectangle Movement**: `sin(time * 0.2) * 200px` vertical
- **Text Movement**: `sin(time * 0.15) * 150px` horizontal
- **Frame Rate**: ~60 FPS
- **Speed**: 10x slower than normal (0.2 and 0.15 vs 2.0 and 1.5)

### Performance
- Hardware-accelerated clipping (GPU scissor test)
- No CPU overhead for clipping calculations
- Efficient for large numbers of clipped objects

## Comparison with Non-Clipped Rendering

Without clipping (`setClippingEnabled(False)`):
- Content would render beyond the green borders
- Rectangles and text would be visible outside the frame
- No performance benefit from culling off-screen content

With clipping enabled:
- Content is cut off at the frame boundaries
- Only visible portions are rendered
- GPU automatically discards fragments outside scissor rect

## Related Documentation

- [Clipping Implementation Details](CLIPPING_IMPLEMENTATION.md)
- [Hierarchy Demo](samples-hierarchy.md) - Shows nested Frame2D structures
- [3D Rendering](3D_RENDERING.md) - Frame3D transform system
