# Clipping Window Size Fix - December 2024

## Issue

Clipping boundaries (borders) were not consistently visible in `clipping_demo.py`, and the clipping position changed depending on window size. This made it impossible to see where the Frame2D clipping boundaries were.

## Root Cause

The scissor rect calculation had three coordinate space issues:

1. **popScissorRect() using cached window dimensions**: When restoring the full viewport after clipping, it used `windowWidth_` and `windowHeight_` which were set at initialization and never updated. This caused incorrect scissor rect restoration on Retina displays and after window resizing.

2. **No tracking of render target context**: The renderer didn't distinguish between rendering to the main screen vs off-screen textures, causing scissor rects to be calculated in the wrong coordinate space.

3. **transformPointToScreen() using wrong dimensions**: This function always queried the main view's drawable size, even when rendering to off-screen textures, causing incorrect coordinate transformations.

## Solution

### Fix 1: Dynamic Drawable Size in popScissorRect()

Changed from using cached window dimensions to querying actual render target dimensions:

```cpp
// Before (WRONG):
metalScissor.width = windowWidth_;
metalScissor.height = windowHeight_;

// After (CORRECT):
metalScissor.width = static_cast<NSUInteger>(currentRenderTargetWidth_);
metalScissor.height = static_cast<NSUInteger>(currentRenderTargetHeight_);
```

### Fix 2: Track Render Target Dimensions

Added member variables to track current render target dimensions:

```cpp
// In MetalRenderer.h:
int currentRenderTargetWidth_;
int currentRenderTargetHeight_;
```

These are updated:
- In `beginFrame()` - set to drawable size for main screen rendering
- In `renderFrame3DToTexture()` - set to texture size for off-screen rendering

### Fix 3: Use Tracked Dimensions in transformPointToScreen()

Changed coordinate transformation to use tracked dimensions instead of always querying the main view:

```cpp
// Before (WRONG):
MTKView* view = (__bridge MTKView*)metalView_;
CGSize drawableSize = [view drawableSize];
screenX = (clipX + 1.0f) * 0.5f * drawableSize.width;
screenY = (1.0f - clipY) * 0.5f * drawableSize.height;

// After (CORRECT):
float targetWidth = static_cast<float>(currentRenderTargetWidth_);
float targetHeight = static_cast<float>(currentRenderTargetHeight_);
screenX = (clipX + 1.0f) * 0.5f * targetWidth;
screenY = (1.0f - clipY) * 0.5f * targetHeight;
```

## Results

After these fixes:
- ✅ All 4 borders are visible in clipping demo
- ✅ Clipping boundaries remain consistent regardless of window size
- ✅ Scissor rect correctly calculated: (0, 0, 400, 400) for 400x400 Frame2D
- ✅ Works correctly on Retina displays with 2x scaling
- ✅ Handles both off-screen texture rendering and direct screen rendering

## Testing

Run the clipping demo to verify all borders are visible:
```bash
PYTHONPATH=build python3 samples/basic/clipping_demo.py
```

Expected behavior:
- All 4 colored borders visible at Frame2D edges
- Content clipped at border boundaries
- Borders remain in correct position when resizing window

## Files Modified

- `src/rendering/MetalRenderer.h` - Added currentRenderTargetWidth/Height members
- `src/rendering/MetalRenderer.mm` - Implemented all three fixes
- `doc/CLIPPING_SCISSOR_FIX.md` - Detailed analysis and fix documentation

## Related Issues

This fix resolves the coordinate space mismatch between off-screen rendering and main screen rendering, ensuring scissor rects are always calculated in the correct coordinate system.
