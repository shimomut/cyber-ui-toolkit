# Coordinate System Fix - December 2024

## Summary

Fixed the Frame2D coordinate system implementation to match documentation. Frame2D and its children now correctly use **top-left origin** coordinates.

**Update (December 2024):** Fixed Frame2D positioning bug where Frame2D's own position was incorrectly treated as center-based instead of top-left origin.

## Changes Made

### Implementation Fix (src/rendering/MetalRenderer.mm)

**Original Fix:** Added offset matrix transformation for Frame2D children coordinate system.

**Updated Fix (December 2024):** Corrected to treat Frame2D's position as top-left origin (not center):

```objective-c
// Frame2D position is already top-left origin (Object2D coordinate system)
// We only need to set up the coordinate system for children:
// - Y-axis flip (Y+ down for 2D UI)
// - Origin at (0, 0) = Frame2D's top-left corner
float offsetMatrix[16] = {
    1, 0, 0, 0,
    0, -1, 0, 0,  // Flip Y-axis: Y+ down for 2D UI
    0, 0, 1, 0,
    0, height, 0, 1  // Move origin to top-left with Y-flip
};

// Combine with Frame2D's MVP
float frame2dMVP[16];
multiplyMatrices(objectMVP, offsetMatrix, frame2dMVP);
```

The key change: Removed the `-halfWidth, halfHeight` offset because Frame2D's position already represents its top-left corner, not its center.

### Coordinate System Behavior

**All Object2D (Rectangle, Text, Frame2D):**
- Use **top-left origin coordinates**
- Position refers to the **top-left corner** of the object
- Child at (0, 0) is at parent's top-left corner
- Rectangle/Text at position (x, y) has its top-left corner at (x, y)

**Frame2D Specific:**
- Frame2D children are positioned relative to Frame2D's top-left corner
- Clipping rect uses (0, 0) to (width, height) coordinates
- Child at (width, height) would be at Frame2D's bottom-right corner

**Frame3D Positioning:**
- Frame3D itself uses centered positioning in 3D space
- `frame3d.set_position(x, y, z)` places Frame3D's center at that position
- But Frame3D's children (Object2D) use top-left origin relative to Frame3D

### Example

```python
frame2d = ui.Frame2D()
frame2d.set_position(150, 50)  # Frame2D center at (150, 50)
frame2d.set_size(500, 600)

rect = ui.Rectangle(100, 100)
rect.set_position(0, 0)  # Rectangle's top-left at Frame2D's top-left corner
frame2d.add_child(rect)
```

**Result:**
- Frame2D center: (150, 50)
- Frame2D top-left: (150 - 250, 50 - 300) = (-100, -250)
- Rectangle top-left: (-100, -250) + (0, 0) = (-100, -250)
- Rectangle bottom-right: (-100, -250) + (100, 100) = (0, -150)

**Another Example:**
```python
# Place rectangle at specific position within Frame2D
rect2 = ui.Rectangle(50, 50)
rect2.set_position(100, 100)  # 100 pixels from Frame2D's top-left
frame2d.add_child(rect2)
```

**Result:**
- Rectangle top-left: Frame2D's top-left + (100, 100)
- Rectangle covers area from (100, 100) to (150, 150) within Frame2D

## Verification

Tests confirm the coordinate system is working correctly:

```bash
python3 tests/debug_coordinate_transform.py
python3 tests/test_clipping_demo_simple.py
```

## Known Issues

The Frame2D size issue (perspective projection causing incorrect screen size) remains a separate problem documented in `FRAME2D_KNOWN_ISSUES.md`. This fix addresses only the coordinate system origin, not the size scaling.

## References

- `doc/3D_RENDERING.md` - Coordinate system documentation
- `doc/FRAME2D_COORDINATE_FIX.md` - Previous coordinate fix attempt
- `doc/FRAME2D_KNOWN_ISSUES.md` - Known issues including size mismatch
- `tests/debug_coordinate_transform.py` - Coordinate system verification test
