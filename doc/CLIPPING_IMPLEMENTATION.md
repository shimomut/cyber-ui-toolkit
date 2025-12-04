# Frame2D Clipping Implementation

## Current Status

✅ **IMPLEMENTED** - Frame2D clipping is fully functional with Metal scissor test support.

## Features

- **Scissor Test Clipping** - Uses Metal's hardware scissor test for efficient clipping
- **Transform-Aware** - Correctly handles Frame3D rotation, scale, and position
- **Nested Clipping** - Supports nested Frame2D with proper clipping intersection
- **Screen Space Transformation** - Transforms clipping bounds from world space to screen space

## API

- `Frame2D::setClippingEnabled(bool)` - Enable/disable clipping
- `Frame2D::setSize(width, height)` - Define clipping region size
- `Frame2D::isClippingEnabled()` - Query clipping state

## Implementation Details

The clipping system consists of:

### 1. MetalRenderer Scissor Methods

**In `src/rendering/MetalRenderer.h`:**
```cpp
void pushScissorRect(float x, float y, float width, float height, const float* mvpMatrix);
void popScissorRect();
void transformPointToScreen(float x, float y, const float* mvpMatrix, float& screenX, float& screenY);
```

**Scissor Stack:**
```cpp
struct ScissorRect {
    int x, y, width, height;
};
std::vector<ScissorRect> scissorStack_;
```

### 2. Transform-Aware Clipping

The `pushScissorRect` method:
1. Transforms all four corners of the clipping rectangle using the MVP matrix
2. Finds the bounding box in screen space
3. Intersects with parent scissor rect (if any) for nested clipping
4. Applies to Metal render encoder using `setScissorRect`

### 3. Automatic Frame2D Detection

In `MetalRenderer::renderObject2D()`:
```cpp
Frame2D* frame2d = dynamic_cast<Frame2D*>(object);
if (frame2d) {
    bool hasClipping = frame2d->isClippingEnabled();
    
    if (hasClipping) {
        float width, height;
        frame2d->getSize(width, height);
        pushScissorRect(0, 0, width, height, objectMVP);
    }
    
    // Render children...
    
    if (hasClipping) {
        popScissorRect();
    }
}
```

### 4. Coordinate Transformation

The `transformPointToScreen` method:
1. Applies MVP matrix transformation
2. Performs perspective divide
3. Converts from NDC [-1, 1] to screen space [0, width/height]
4. Flips Y coordinate for screen space

### 5. Nested Clipping Support

When pushing a new scissor rect, it's automatically intersected with the parent:
```cpp
if (!scissorStack_.empty()) {
    const ScissorRect& parent = scissorStack_.back();
    // Intersect new rect with parent rect
    scissorX = std::max(scissorX, parent.x);
    scissorY = std::max(scissorY, parent.y);
    // ... calculate intersection
}
```

## Testing

Run the clipping demo to see it in action:

```bash
python3 samples/basic/clipping_demo.py
```

The demo demonstrates:
- ✅ Content being clipped at Frame2D boundaries (green borders)
- ✅ Animated rectangles with textures moving in/out of clipping region
- ✅ Animated text elements being clipped
- ✅ Slow animations (10x slower) for clear visualization
- ✅ Proper clipping with Frame3D rotation and scale

## Key Implementation Notes

1. **Hardware Acceleration** - Uses Metal's native scissor test, no CPU-side clipping needed
2. **Transform Support** - Correctly handles all Frame3D transformations (position, rotation, scale)
3. **Nested Clipping** - Multiple Frame2D levels automatically intersect clipping regions
4. **Performance** - Minimal overhead, scissor test is a fast GPU operation
5. **Initialization** - Scissor rect is set to full viewport at frame start and cleared each frame

## Example Usage

```python
# Create a Frame2D with clipping
clip_frame = ui.Frame2D()
clip_frame.set_position(100.0, 100.0)
clip_frame.set_size(400.0, 300.0)
clip_frame.set_clipping_enabled(True)  # Enable clipping

# Add content that will be clipped
rect = ui.Rectangle(200.0, 200.0)
rect.set_position(0.0, 0.0)  # Relative to frame
clip_frame.add_child(rect)

# Content outside the 400x300 region will be clipped
```
