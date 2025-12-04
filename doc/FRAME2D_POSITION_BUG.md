# Frame2D Position Bug - December 2024

## Problem

Frame2D's `set_position()` is being interpreted as CENTER positioning, but according to the coordinate system specification, Frame2D is an Object2D and should use TOP-LEFT origin positioning.

## Current Behavior

In `clipping_demo.py`:
```python
clip_panel = ui.Frame2D()
clip_panel.set_position(150.0, 50.0)  # Intended: top-left at (150, 50)
clip_panel.set_size(500.0, 600.0)
```

**Expected:** Frame2D's top-left corner at (150, 50), center at (400, 350)
**Actual:** Frame2D's center at (150, 50), top-left at (-100, -250)

## Root Cause

In `src/rendering/MetalRenderer.mm` (lines 473-485):

```cpp
// Create offset matrix to move origin from center to top-left
float halfWidth = width * 0.5f;
float halfHeight = height * 0.5f;

float offsetMatrix[16] = {
    1, 0, 0, 0,
    0, -1, 0, 0,  // Flip Y-axis: Y+ down for 2D UI
    0, 0, 1, 0,
    -halfWidth, halfHeight, 0, 1  // Move to top-left (with flipped Y)
};
```

This offset matrix assumes Frame2D's position is at its CENTER and offsets to top-left for children. However, Frame2D's position should already BE the top-left corner.

## Coordinate System Rules

From the specification:
- **Frame2D and Object2D's origin is top-left**
- Frame2D inherits from Object2D
- `set_position(x, y)` should place the top-left corner at (x, y)

## The Confusion

The offset matrix is correct for **Frame2D's children** (they need top-left origin), but Frame2D's own position is being treated incorrectly.

The issue is:
1. Frame2D position (150, 50) is applied as a translation
2. Then offset matrix moves -250, +300 to convert "center to top-left"
3. This double-transforms the position

## Solution Options

### Option 1: Remove the offset for Frame2D position (CORRECT)

Frame2D's position should already be top-left. The offset should only apply to establish the coordinate system for children, not to reposition Frame2D itself.

**Change needed in MetalRenderer.mm:**

```cpp
// Frame2D position is already top-left origin
// We only need to:
// 1. Apply Frame2D's position (already done via objectMVP)
// 2. Set up coordinate system for children (top-left origin, Y-down)

// For children, origin should be at Frame2D's top-left corner
// Since Frame2D's position is already top-left, we just need Y-flip
float offsetMatrix[16] = {
    1, 0, 0, 0,
    0, -1, 0, 0,  // Flip Y-axis: Y+ down for 2D UI
    0, 0, 1, 0,
    0, height, 0, 1  // Move origin to top-left with Y-flip
};
```

### Option 2: Change Frame2D to use center positioning (WRONG)

This would violate the coordinate system specification that Frame2D uses top-left origin.

## Recommended Fix

**Option 1** is correct. Frame2D should use top-left origin positioning like all Object2D classes.

The offset matrix should:
1. Flip Y-axis (Y-down for 2D UI)
2. Position origin at top-left (0, 0) in Frame2D's local space
3. NOT offset Frame2D's own position

## Test Case

After fix, this should work correctly:

```python
# Window: 800x700
# Frame2D: 500x600 at position (150, 50)

clip_panel.set_position(150.0, 50.0)  # Top-left at (150, 50)
clip_panel.set_size(500.0, 600.0)

# Expected positions:
# - Frame2D top-left: (150, 50)
# - Frame2D center: (150 + 250, 50 + 300) = (400, 350)
# - Frame2D bottom-right: (150 + 500, 50 + 600) = (650, 650)

# Window center: (400, 350)
# Frame2D center should align with window center ✓
```

## Related Files

- `src/rendering/MetalRenderer.mm` - Needs fix
- `doc/OBJECT2D_COORDINATE_SYSTEM.md` - Specifies top-left origin
- `doc/COORDINATE_SYSTEM_FIX_2024.md` - Previous fix (may have introduced this bug)
- `samples/basic/clipping_demo.py` - Demonstrates the bug
