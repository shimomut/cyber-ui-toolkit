# Troubleshooting Guide

## Textures Not Visible

### Symptom
Rectangles appear as solid colors instead of showing textures.

### Checklist

1. **Verify images are loaded**
   ```bash
   PYTHONPATH=../../build python3 test_image_loading.py
   ```
   All three images should load successfully.

2. **Check texture is set**
   ```python
   rect.set_image(image)
   print(f"Has texture: {rect.has_image()}")  # Should be True
   ```

3. **Verify color is white**
   ```python
   rect.set_color(1.0, 1.0, 1.0, 1.0)  # White shows texture as-is
   ```
   Non-white colors will tint the texture.

4. **Rebuild the library**
   ```bash
   make clean && make
   ```

5. **Check Metal shader compilation**
   Look for shader errors in console output when running samples.

### Common Issues

**Issue: Textures appear as solid white**
- Cause: Texture not bound to shader
- Solution: Verify `setFragmentTexture` is called in `renderRectangle()`

**Issue: Textures appear as solid color**
- Cause: Shader not sampling texture
- Solution: Check fragment shader has `tex.sample()` call

**Issue: Textures appear black**
- Cause: Image data not uploaded to GPU
- Solution: Verify `replaceRegion` is called with correct data

**Issue: Transparent areas show as black**
- Cause: Alpha blending not enabled
- Solution: Check pipeline descriptor has `blendingEnabled = YES`

## Build Errors

### Missing pybind11
```bash
pip3 install pybind11
```

### Missing Pillow or numpy
```bash
pip3 install Pillow numpy
```

### Linker errors
```bash
# Clean and rebuild
make clean && make
```

## Runtime Errors

### ModuleNotFoundError: No module named 'cyber_ui_core'
```bash
# Set PYTHONPATH
PYTHONPATH=../../build python3 script.py

# Or from project root
PYTHONPATH=build python3 samples/basic/script.py
```

### Image file not found
- Ensure you're running from `samples/basic/` directory
- Or use absolute paths
- Check that `samples/data/*.png` files exist

### Window doesn't open
- Check Metal is supported (macOS 10.13+)
- Verify renderer initialization succeeds
- Check console for error messages

## Verification Steps

1. **Test image loading**
   ```bash
   PYTHONPATH=../../build python3 test_image_loading.py
   ```
   Expected: All 3 images load successfully

2. **Test texture demo (console)**
   ```bash
   PYTHONPATH=../../build python3 test_texture_demo.py
   ```
   Expected: Shows texture info in console

3. **Test visual rendering**
   ```bash
   PYTHONPATH=../../build python3 verify_textures.py
   ```
   Expected: Window opens showing textures

4. **Test full demo**
   ```bash
   PYTHONPATH=../../build python3 test_rectangle.py
   ```
   Expected: Window with 5 rectangles (4 textured, 1 solid)

## Debug Output

Enable verbose output in your script:

```python
# After loading image
if image and image.is_loaded():
    print(f"Image loaded: {image.get_width()}x{image.get_height()}")
    print(f"Channels: {image.get_channels()}")
    print(f"Data size: {len(image.get_data()) if hasattr(image, 'get_data') else 'N/A'}")

# After setting texture
if rect.has_image():
    img = rect.get_image()
    print(f"Texture set: {img.get_width()}x{img.get_height()}")
else:
    print("No texture set!")
```

## Getting Help

If issues persist:

1. Check `TEXTURE_IMPLEMENTATION.md` for implementation details
2. Review Metal shader code in `src/rendering/MetalRenderer.mm`
3. Verify Image class implementation in `src/rendering/Image.cpp`
4. Check Python bindings in `src/bindings/python_bindings.cpp`

## Known Limitations

- Textures are recreated every frame (performance impact)
- No texture caching
- No mipmap support
- Limited to RGBA8 format
- No texture compression
