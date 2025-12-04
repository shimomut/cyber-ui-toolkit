# Frame2D Known Issues

## Issue: Frame2D Size Doesn't Match Screen Pixels

### Problem

When you specify a Frame2D size of 500x600, the rendered size on screen is much smaller (approximately 76x265 logical pixels). This is a **fundamental coordinate system mismatch** between Frame2D's pixel-based sizing and the 3D perspective projection system.

### Root Cause

Frame2D is rendered as part of a 3D scene with perspective projection. The size values (500x600) are interpreted as **world-space units**, not screen pixels. These world-space coordinates then go through:

1. **3D transformation** (Frame3D's position/rotation/scale)
2. **View transformation** (camera position/orientation)
3. **Perspective projection** (FOV, aspect ratio, near/far planes)
4. **Viewport transformation** (world → screen pixels)

The perspective projection causes objects to appear smaller based on their distance from the camera and the field of view. A 500-unit wide object in world space does NOT translate to 500 pixels on screen.

### Why This Happens

The current implementation treats Frame2D as a 3D object that happens to contain 2D children. This means:

- Frame2D position is in 3D world space
- Frame2D size is in world-space units
- Children are rendered with 3D perspective projection
- Final screen size depends on camera FOV, distance, and aspect ratio

### Current Behavior

With typical camera settings:
- Camera at Z=800
- FOV = 60 degrees (1.0472 radians)
- Frame3D at Z=0

A Frame2D with size 500x600 renders at approximately:
- Width: ~76 logical pixels (15% of specified size)
- Height: ~265 logical pixels (44% of specified size)

The ratios are different because of aspect ratio and perspective effects.

### Workarounds

#### Option 1: Scale Up Frame2D Size

Multiply your desired pixel size by approximately 6-7x:

```python
# Want 500x600 pixels on screen?
frame2d.set_size(3000, 2400)  # Approximately 6x larger
```

The exact multiplier depends on:
- Camera FOV
- Camera distance (Z position)
- Frame3D Z position
- Window aspect ratio

#### Option 2: Use Orthographic Projection

For pure 2D UI, use an orthographic camera instead of perspective:

```python
camera = scene.get_camera()
camera.set_position(0, 0, 5)
# Don't call set_perspective() - use default orthographic
```

With orthographic projection, world units map more directly to screen pixels (though still affected by camera distance and viewport size).

#### Option 3: Calculate Correct Size

To calculate the required Frame2D size for a desired screen size:

```python
import math

def calculate_frame2d_size(desired_pixels, camera_z, frame_z, fov, viewport_size):
    """
    Calculate Frame2D size needed to achieve desired screen size.
    
    Args:
        desired_pixels: (width, height) in pixels
        camera_z: Camera Z position
        frame_z: Frame3D Z position  
        fov: Field of view in radians
        viewport_size: (width, height) of viewport in pixels
    """
    distance = camera_z - frame_z
    
    # Calculate world-space size at this distance
    height_at_distance = 2 * distance * math.tan(fov / 2)
    pixels_per_unit = viewport_size[1] / height_at_distance
    
    world_width = desired_pixels[0] / pixels_per_unit
    world_height = desired_pixels[1] / pixels_per_unit
    
    return (world_width, world_height)

# Example:
size = calculate_frame2d_size(
    desired_pixels=(500, 600),
    camera_z=800,
    frame_z=0,
    fov=1.0472,  # 60 degrees
    viewport_size=(1600, 1400)  # Retina 2x of 800x700
)
frame2d.set_size(size[0], size[1])
```

### Coordinate System

**Current behavior** (after removing offset):
- Frame2D children use **centered coordinates**
- Child at (0, 0) is at Frame2D's center
- Child at (-250, -300) is at top-left of a 500x600 Frame2D
- Child at (250, 300) is at bottom-right

**Original intention** (not working):
- Frame2D children should use **top-left origin**
- Child at (0, 0) should be at Frame2D's top-left corner
- Child at (500, 600) should be at bottom-right

The top-left origin system doesn't work correctly with perspective projection because the offset transformation gets applied in clip space instead of world space.

### Recommended Solutions

For the long term, Frame2D needs to be redesigned with one of these approaches:

#### Solution 1: Separate 2D Rendering Path

Frame2D should use a completely separate rendering path with:
- Orthographic projection (no perspective)
- Screen-space coordinates (pixels, not world units)
- Rendered after 3D content (overlay)

This is how most game engines handle UI.

#### Solution 2: Explicit World-Space Sizing

Document that Frame2D size is in world-space units, not pixels. Provide helper functions to convert between screen pixels and world units based on camera settings.

#### Solution 3: Auto-Scaling

Frame2D could automatically calculate the correct world-space size based on:
- Desired screen-pixel size
- Current camera settings
- Frame3D position

This would require Frame2D to have access to camera and viewport information.

### Related Issues

- Text rendering size also affected (text size is in points, gets perspective-projected)
- Clipping rect calculation needs to account for perspective
- Nested Frame2D would compound the scaling issues

### Testing

To verify Frame2D rendering size:

```bash
python3 tests/debug_frame2d_size.py
```

This will show the actual rendered size vs expected size.

### References

- `doc/FRAME2D_COORDINATE_FIX.md` - Previous attempt to fix coordinate system
- `doc/RETINA_DISPLAY_FIX.md` - Retina scaling fix that exposed these issues
- `tests/debug_frame2d_size.py` - Size verification test
- `tests/debug_coordinate_transform.py` - Coordinate transformation test

### Status

**Current state**: Frame2D renders at incorrect size due to perspective projection.

**Workaround**: Scale up Frame2D size by 6-7x, or use orthographic projection.

**Long-term fix**: Requires architectural changes to separate 2D UI rendering from 3D scene rendering.
