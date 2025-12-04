# Frame2D Y-Axis Coordinate System Issue

## Problem

When running `clipping_demo.py`, the Frame2D content appears incorrectly positioned. The user reports seeing "top-right corner of panel_bg at the center of the window" instead of the expected layout.

## Investigation Results

Diagnostic testing with corner markers revealed:
- YELLOW marker (positioned at bottom-right: 460, 560) renders near window center
- MAGENTA marker (positioned at center: 230, 280) renders below window center  
- RED, GREEN, BLUE markers (top-left, top-right, bottom-left) are not visible

This indicates the Frame2D coordinate system is inverted on the Y-axis.

## Root Cause

The coordinate system mismatch between 3D space and 2D UI:

- **3D Space (OpenGL/Metal convention)**: Y+ is UP
- **2D UI convention**: Y+ is DOWN (top-left origin)

Frame2D tries to provide a top-left origin coordinate system for its children, but the vertices are being generated in 3D space where Y+ is up.

## Diagnostic Results

Test with corner markers at:
- RED: (0, 0) - should be top-left
- GREEN: (460, 0) - should be top-right  
- BLUE: (0, 560) - should be bottom-left
- YELLOW: (460, 560) - should be bottom-right
- MAGENTA: (230, 280) - should be center

**Actual result:**
- YELLOW appears at window center (769, 790)
- MAGENTA appears below center (420, 1207)
- RED, GREEN, BLUE not visible (off-screen)

This confirms the Y-axis is inverted.

## Solution

Negate Y coordinates when generating vertices for all Object2D types within Frame2D:

1. **Rectangle vertices**: Use `-height` instead of `+height`
2. **Text quads**: Use `-height` instead of `+height`
3. **Any other 2D primitives**: Apply same Y-negation

This makes Y+ go down in Frame2D space while keeping the 3D coordinate system unchanged.

## Implementation

### Rectangle (MetalRenderer.mm)

```cpp
// OLD (wrong):
Vertex vertices[] = {
    {{0.0f, 0.0f}, ...},      // Top-left
    {{width, 0.0f}, ...},     // Top-right
    {{0.0f, height}, ...},    // Bottom-left
    {{width, height}, ...},   // Bottom-right
};

// NEW (correct):
Vertex vertices[] = {
    {{0.0f, 0.0f}, ...},       // Top-left
    {{width, 0.0f}, ...},      // Top-right
    {{0.0f, -height}, ...},    // Bottom-left (Y negative)
    {{width, -height}, ...},   // Bottom-right (Y negative)
};
```

### Text (similar fix needed)

Text rendering also needs Y-negation for the quad vertices.

## Testing

Run diagnostic test:
```bash
python3 tests/debug_corner_markers.py
python3 tests/analyze_corners.py
```

Expected result after fix:
- RED at top-left of gray area
- GREEN at top-right of gray area
- BLUE at bottom-left of gray area
- YELLOW at bottom-right of gray area
- MAGENTA at center of gray area

## Related Files

- `src/rendering/MetalRenderer.mm` - Rendering implementation
- `doc/OBJECT2D_COORDINATE_SYSTEM.md` - Coordinate system documentation
- `doc/FRAME2D_KNOWN_ISSUES.md` - Known Frame2D issues
- `tests/debug_corner_markers.py` - Diagnostic test

## Current Status

✅ Rectangle Y-negation applied
✅ Text Y-negation applied  
✅ Offset matrix updated to (+halfHeight instead of -halfHeight)

### Test Results

After fixes:
- GREEN (top-right) appears near window center
- MAGENTA (center) appears left of center
- RED, BLUE, YELLOW still not visible

This indicates partial progress but coordinate system still needs adjustment.

## Next Steps

The issue is more complex than just Y-negation. The Frame2D positioning in 3D space combined with perspective projection is causing unexpected results. Need to investigate:

1. How Frame3D children are positioned (centered vs top-left)
2. Whether Frame2D should use a different positioning system
3. If the offset matrix calculation is correct for the 3D→2D transformation

## Attempted Fixes

### Approach 1: Y-axis flip in offset matrix
```cpp
float offsetMatrix[16] = {
    1, 0, 0, 0,
    0, -1, 0, 0,  // Flip Y
    0, 0, 1, 0,
    -halfWidth, halfHeight, 0, 1
};
```
Result: GREEN (top-right) appears at window center instead of YELLOW (bottom-right). Partial improvement but still incorrect.

### Approach 2: Negate Y in vertices
Negating Y coordinates in Rectangle and Text vertex generation.
Result: Content disappears or renders in wrong location.

### Approach 3: Combination
Combining Y-flip in offset matrix with Y-negation in vertices.
Result: Still incorrect positioning.

## Root Cause Analysis

The issue is more fundamental than a simple coordinate flip. The problem involves:

1. **Frame3D positioning**: Uses centered coordinates (standard 3D)
2. **Frame2D positioning**: Inherits from Object2D but positioned as 3D object
3. **Frame2D children**: Should use top-left origin (2D UI convention)
4. **Perspective projection**: Transforms world space to screen space
5. **Y-axis convention mismatch**: 3D uses Y+ up, 2D UI uses Y+ down

The offset matrix attempts to bridge these systems but the transformation is incomplete.

## Recommended Solution

The Frame2D system needs architectural changes:

1. **Option A**: Make Frame2D use screen-space coordinates instead of world-space
   - Render Frame2D content in a separate 2D pass after 3D content
   - Use orthographic projection for Frame2D
   - Direct pixel-to-screen mapping

2. **Option B**: Fix the coordinate transformation pipeline
   - Properly account for Y-axis flip at each transformation stage
   - Ensure offset matrix correctly transforms from 3D centered to 2D top-left
   - Test with various Frame2D positions and sizes

3. **Option C**: Document current behavior as "working as designed"
   - Frame2D uses 3D positioning (centered)
   - Children use relative coordinates from Frame2D center
   - Provide helper functions to calculate positions

## Status

⚠️ BLOCKED - Requires architectural decision on Frame2D coordinate system design

The current implementation has fundamental issues that cannot be fixed with simple coordinate transformations. A design decision is needed on how Frame2D should integrate with the 3D rendering system.
