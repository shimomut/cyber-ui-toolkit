# Tests Directory

This directory contains test scripts and verification utilities for the Cyber UI Toolkit.

## Test Scripts

### Capture System Tests

**test_capture.py** - Comprehensive tests for the rendering capture system
```bash
python tests/test_capture.py
```

Tests include:
- Basic shape capture
- Textured shape capture  
- Raw pixel data capture and analysis
- Animated frame capture

**compare_captures.py** - Utility for comparing captured frames
```bash
# Compare two images
python tests/compare_captures.py image1.png image2.png

# With tolerance threshold
python tests/compare_captures.py image1.png image2.png 5

# Generate visual diff
python tests/compare_captures.py image1.png image2.png --diff diff.png
```

### Image and Texture Tests

**test_image_loading.py** - Test image loading functionality

**verify_textures.py** - Verify texture rendering

**verify_texture_sync.py** - Verify texture synchronization

## Output Directory

Test outputs are saved to `tests/output/` (created automatically):
- Captured frames (PNG images)
- Test results
- Debug visualizations

## Running All Tests

```bash
# Run capture tests
python tests/test_capture.py

# Run image loading tests
python tests/test_image_loading.py

# Run texture verification
python tests/verify_textures.py
python tests/verify_texture_sync.py
```

## See Also

- [Capture System Documentation](/doc/CAPTURE_SYSTEM.md)
- [Troubleshooting Guide](/doc/TROUBLESHOOTING.md)
