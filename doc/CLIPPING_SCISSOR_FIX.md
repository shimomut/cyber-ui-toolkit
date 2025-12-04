# Clipping Scissor Rect Fix - Window Size Independence

## Problem

The clipping boundaries (borders) are not consistently visible and their position changes depending on window size. This is caused by incorrect scissor rect calculation when using off-screen rendering.

## Root Cause

The rendering architecture uses two-stage rendering:

1. **Off-screen rendering**: Frame2D and children are rendered to a texture
2. **Screen rendering**: The texture is rendered as a quad to the main screen

The scissor rect is applied during off-screen rendering, but the calculation was using screen-space coordinates instead of texture-space coordinates.

### Specific Issues

1. **`popScissorRect()` using window dimensions**: When restoring the full viewport, it used `windowWidth_` and `windowHeight_` which are set at initialization and never updated. On Retina displays and when resizing, this causes incorrect scissor rect restoration.

2. **Coordinate space mismatch**: The scissor rect is calculated by transforming Frame2D-local coordinates through the MVP matrix to screen space. However, during off-screen rendering, the "screen" is actually the texture, not the window.

## Analysis Results

From captured frames:
- Window size: 800x600
- Drawable size (Retina 2x): 1600x1400
- Expected Frame2D position: (150, 50) → (300, 100) in pixels
- Expected Frame2D size: (500, 600) → (1000, 1200) in pixels
- Actual content bounds: X=648-1149, Y=234-1087

The content is offset and incorrectly clipped.

## Solution

### Fix 1: Use Drawable Size in popScissorRect() ✓

Changed `popScissorRect()` to query the actual drawable size instead of using cached window dimensions:

```cpp
// Before (WRONG):
metalScissor.width = windowWidth_;
metalScissor.height = windowHeight_;

// After (CORRECT):
MTKView* view = (__bridge MTKView*)metalView_;
CGSize drawableSize = [view drawableSize];
metalScissor.width = static_cast<NSUInteger>(drawableSize.width);
metalScissor.height = static_cast<NSUInteger>(drawableSize.height);
```

This ensures the scissor rect always matches the actual render target size, accounting for:
- Retina display scaling
- Window resizing
- Different display configurations

### Fix 2: Coordinate Space Context (TODO)

The scissor rect calculation needs to be aware of whether it's rendering to:
- Off-screen texture (use texture dimensions)
- Main screen (use drawable dimensions)

Currently, `pushScissorRect()` always uses drawable size from `metalView_`, which is correct for direct rendering but may need adjustment for off-screen rendering contexts.

## Testing

### Manual Test
Run the clipping demo and resize the window:
```bash
PYTHONPATH=build python3 samples/basic/clipping_demo.py
```

Expected behavior:
- All 4 colored borders should be visible at Frame2D edges
- Borders should remain at the same relative position when resizing
- Content should be clipped at border edges

### Automated Test
```bash
python3 tests/verify_clipping_borders.py
```

This analyzes captured frames to verify all borders are visible.

## Related Files

- `src/rendering/MetalRenderer.mm` - Scissor rect implementation
- `samples/basic/clipping_demo.py` - Visual demonstration
- `tests/verify_clipping_borders.py` - Automated verification
- `tests/analyze_clipping_borders.py` - Debug analysis tool

## Status

- ✓ Fix 1 implemented: Use drawable size in popScissorRect()
- ✓ Fix 2 implemented: Track render target dimensions separately for off-screen vs main screen  
- ✓ Fix 3 implemented: Use currentRenderTargetWidth/Height in transformPointToScreen()
- ✅ Scissor rect now correctly calculated: (0, 0, 400, 400) for 400x400 Frame2D
- ⚠️ Issue persists: Borders still not visible - likely a different rendering issue

## Root Cause Analysis

The actual problem is in the rendering architecture:

1. Frame3D uses off-screen rendering: children are rendered to a texture
2. Frame2D is a child of Frame3D, positioned at (150, 50)
3. When rendering to the off-screen texture, Frame2D's position (150, 50) is applied
4. This causes Frame2D children to be rendered at (150, 50) within the 800x700 texture
5. The scissor rect is correctly calculated for this position
6. But the Frame2D should render its children at (0, 0) within the texture
7. The Frame2D's position should only affect where the textured quad appears in 3D space

**Expected behavior:**
- Frame2D children render at (0, 0) within the 800x700 texture
- The texture quad is positioned at Frame3D's position in 3D space
- Frame2D's position is ignored during off-screen rendering

**Actual behavior:**
- Frame2D children render at (150, 50) within the texture
- This leaves empty space in the texture and clips content incorrectly

## Next Steps

The fix requires changing how Frame2D position is handled during off-screen rendering:
1. When rendering to off-screen texture, Frame2D should not apply its position to children
2. Frame2D position should only be used for direct rendering (non-off-screen path)
3. Or, Frame3D should account for Frame2D positions when creating the orthographic projection
