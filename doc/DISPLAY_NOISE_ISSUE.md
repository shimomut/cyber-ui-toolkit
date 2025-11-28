# Display Noise Issue

## Problem Description

Visual noise or dithering may appear in the rendered window display, but this noise is **not present** in captured images. This indicates the noise is being introduced during the display presentation stage, not during the actual rendering.

## Symptoms

- Visible noise/grain/dithering in the application window
- Captured PNG images are perfectly clean
- Noise is most visible in solid color areas or gradients
- Noise may appear as a subtle pattern or grain

## Root Cause

The noise is added **after** the rendering pipeline, during one of these stages:

1. **MTKView Drawable Presentation** - Metal's presentation layer
2. **Display Scaling** - macOS scaling for Retina displays
3. **Window Compositing** - macOS window manager effects
4. **Color Management** - Display color profile conversion
5. **Dithering** - Intentional dithering for smooth gradients

## Why Captures Are Clean

The capture system reads directly from the Metal texture **before** it goes through the display pipeline:

```
Rendering → Metal Texture → [CAPTURE HERE] → Drawable → Display
                ↑                                ↓
            Clean image                    Noise added here
```

This is actually **good news** - it means:
- Your rendering is correct
- The capture system works perfectly for debugging
- The noise is a display artifact, not a rendering bug

## Diagnostic Tool

Run the diagnostic tool to analyze the issue:

```bash
python tests/diagnose_display_noise.py
```

This will:
1. Display a test pattern with solid gray bars
2. Capture multiple frames
3. Analyze pixel consistency
4. Compare window display vs captured images

## Common Causes and Solutions

### 1. Display Scaling (Most Likely)

**Cause:** macOS Retina display scaling interpolates pixels

**Check:**
```bash
# Check your display scaling
system_profiler SPDisplaysDataType | grep Resolution
```

**Solution:** The MTKView may need to account for the backing scale factor.

Add to MetalRenderer initialization:
```objective-c
// In MetalRenderer::initialize()
MTKView* metalView = [[MTKView alloc] initWithFrame:frame device:device];

// Add this line to handle Retina displays properly
[metalView setContentScaleFactor:[[NSScreen mainScreen] backingScaleFactor]];
```

### 2. Color Pixel Format

**Cause:** 8-bit color format may show banding

**Current:** `MTLPixelFormatBGRA8Unorm` (8 bits per channel)

**Alternative:** Use higher precision format
```objective-c
[metalView setColorPixelFormat:MTLPixelFormatBGRA8Unorm_sRGB];
// or
[metalView setColorPixelFormat:MTLPixelFormatRGBA16Float];
```

### 3. Drawable Properties

**Cause:** Default drawable settings may enable dithering

**Solution:** Configure drawable properties explicitly
```objective-c
// Disable automatic drawable management
[metalView setFramebufferOnly:NO];

// Or enable framebuffer-only for better performance
[metalView setFramebufferOnly:YES];
```

### 4. Clear Color Precision

**Cause:** Clear color may not match exactly

**Solution:** Use precise clear color values
```objective-c
// Instead of 0.1, use exact values
[metalView setClearColor:MTLClearColorMake(26.0/255.0, 26.0/255.0, 26.0/255.0, 1.0)];
```

### 5. macOS Display Settings

**Cause:** System-wide display settings

**Check:**
- System Preferences → Displays → Color Profile
- "True Tone" setting (if available)
- "Night Shift" setting

**Solution:** Try different color profiles or disable True Tone

## Implementation Fix

Here's a recommended fix to add to MetalRenderer:

```objective-c
// In MetalRenderer::initialize(), after creating metalView:

MTKView* metalView = [[MTKView alloc] initWithFrame:frame device:device];

// Handle Retina displays properly
NSScreen* screen = [NSScreen mainScreen];
if (screen) {
    CGFloat scaleFactor = [screen backingScaleFactor];
    [metalView setContentScaleFactor:scaleFactor];
    NSLog(@"Display scale factor: %.1f", scaleFactor);
}

// Use sRGB color space for better color accuracy
[metalView setColorPixelFormat:MTLPixelFormatBGRA8Unorm_sRGB];

// Configure drawable properties
[metalView setFramebufferOnly:NO];  // Allow reading back for captures

// Rest of initialization...
```

## Testing the Fix

After applying fixes:

1. Run the diagnostic tool again:
```bash
python tests/diagnose_display_noise.py
```

2. Compare window display with captured images

3. Check if noise is reduced or eliminated

## Verification

To verify the rendering is correct:

1. **Capture images** - Should always be clean
2. **Pixel analysis** - Should show consistent values
3. **Cross-frame comparison** - Should show minimal variance

```bash
# Capture and analyze
python samples/basic/hierarchy_demo.py

# Compare captures
python tests/compare_captures.py \
  samples/output/hierarchy_demo_frame_00120.png \
  samples/output/hierarchy_demo_frame_00240.png
```

## Expected Results

**Good rendering (what you have):**
- Captured images are clean ✓
- Pixel values are consistent ✓
- No rendering artifacts ✓

**Display noise (cosmetic issue):**
- Window shows noise (may be unavoidable)
- Captures are clean (this is what matters)

## Conclusion

The display noise is a **cosmetic issue** that doesn't affect:
- Rendering correctness
- Capture quality
- Testing and debugging
- Production use (if rendering to images/video)

The capture system successfully bypasses this issue, making it perfect for:
- Debugging rendering problems
- Regression testing
- Quality assurance
- Documentation screenshots

## Further Reading

- [Metal Best Practices Guide](https://developer.apple.com/metal/Metal-Best-Practices-Guide.pdf)
- [MTKView Documentation](https://developer.apple.com/documentation/metalkit/mtkview)
- [High Resolution Guidelines for macOS](https://developer.apple.com/design/human-interface-guidelines/macos/icons-and-images/image-size-and-resolution/)

## Related Files

- `src/rendering/MetalRenderer.mm` - Renderer implementation
- `tests/diagnose_display_noise.py` - Diagnostic tool
- `doc/CAPTURE_SYSTEM.md` - Capture system documentation
