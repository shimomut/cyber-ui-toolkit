# Frame2D Position Fix - December 2024

## Problem

Frame2D's `set_position()` was incorrectly treating the position as the **center** of the Frame2D, when it should be the **top-left corner** (following Object2D coordinate system rules).

## Symptoms

In `clipping_demo.py`:
```python
clip_panel.set_position(150.0, 50.0)  # Intended: center at window center (400, 350)
clip_panel.set_size(500.0, 600.0)     # Size: 500x600
```

**Expected:** Frame2D centered in 800x700 window
- Top-left at (150, 50)
- Center at (400, 350) ✓ matches window center

**Actual (before fix):** Frame2D corner at window center
- Center at (150, 50) ✗ wrong
- Top-left at (-100, -250) ✗ off-screen

## Root Cause

In `src/rendering/MetalRenderer.mm`, the offset matrix was incorrectly offsetting Frame2D's position:

```cpp
// WRONG: This treated Frame2D position as center
float offsetMatrix[16] = {
    1, 0, 0, 0,
    0, -1, 0, 0,
    0, 0, 1, 0,
    -halfWidth, halfHeight, 0, 1  // ✗ Moved from center to top-left
};
```

This caused a double transformation:
1. Frame2D position (150, 50) applied as translation
2. Offset (-250, +300) to "convert center to top-left"
3. Result: top-left at (-100, -250) instead of (150, 50)

## Solution

Frame2D inherits from Object2D and follows the **top-left origin** coordinate system. The position is already the top-left corner, so we only need to set up the coordinate system for children (Y-flip):

```cpp
// CORRECT: Frame2D position is already top-left
float offsetMatrix[16] = {
    1, 0, 0, 0,
    0, -1, 0, 0,  // Flip Y-axis: Y+ down for 2D UI
    0, 0, 1, 0,
    0, height, 0, 1  // ✓ Only Y-flip, no position offset
};
```

## Changes Made

### File: `src/rendering/MetalRenderer.mm`

**Before:**
```cpp
float halfWidth = width * 0.5f;
float halfHeight = height * 0.5f;

float offsetMatrix[16] = {
    1, 0, 0, 0,
    0, -1, 0, 0,
    0, 0, 1, 0,
    -halfWidth, halfHeight, 0, 1
};
```

**After:**
```cpp
float offsetMatrix[16] = {
    1, 0, 0, 0,
    0, -1, 0, 0,
    0, 0, 1, 0,
    0, height, 0, 1
};
```

### Documentation Updates

- `doc/COORDINATE_SYSTEM_FIX_2024.md` - Updated with correct implementation
- `doc/FRAME2D_POSITION_BUG.md` - Detailed bug analysis
- `doc/FRAME2D_POSITION_FIX_2024.md` - This document

## Verification

### Test: `tests/verify_frame2d_position.py`

Creates a Frame2D at position (150, 50) with size 500x600 in an 800x700 window:

```python
frame2d.set_position(150.0, 50.0)
frame2d.set_size(500.0, 600.0)
```

**Expected results:**
- Green border centered in window ✓
- Red marker at top-left of border ✓
- Blue marker at center of border (and window) ✓
- Yellow marker at bottom-right of border ✓

### Visual Verification

Run the test:
```bash
python3 tests/verify_frame2d_position.py
```

The green border should be perfectly centered in the window, with:
- Red square at top-left corner
- Blue square at center
- Yellow square at bottom-right corner

## Impact

This fix affects all Frame2D positioning throughout the codebase. Any code that was compensating for the incorrect center-based positioning will need to be updated.

### Migration Guide

If you were compensating for the bug:

**Old (compensating for bug):**
```python
# To center a 500x600 Frame2D in 800x700 window
frame2d.set_position(400, 350)  # Set to window center
```

**New (correct):**
```python
# To center a 500x600 Frame2D in 800x700 window
frame2d.set_position(150, 50)  # Set top-left, Frame2D centers itself
# Calculation: (800-500)/2 = 150, (700-600)/2 = 50
```

## Coordinate System Rules (Confirmed)

1. **Frame2D** inherits from **Object2D**
2. **Object2D** uses **top-left origin** coordinate system
3. `set_position(x, y)` places the **top-left corner** at (x, y)
4. Frame2D's children also use top-left origin relative to Frame2D
5. Only **Frame3D** uses center-based positioning (in 3D space)

## Related Issues

- Original coordinate system fix: `doc/COORDINATE_SYSTEM_FIX_2024.md`
- Coordinate system specification: `doc/OBJECT2D_COORDINATE_SYSTEM.md`
- Hierarchy documentation: `doc/HIERARCHY.md`

## Status

✅ **FIXED** - Frame2D now correctly uses top-left origin positioning
