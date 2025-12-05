# FPS Measurement

This document describes the FPS (Frames Per Second) measurement functionality in the Cyber UI Toolkit renderers.

## Overview

Both Metal and OpenGL renderers now include built-in FPS measurement capabilities. The FPS counter tracks rendering performance and provides statistics both during runtime and when the application closes.

## Features

- **Real-time FPS tracking**: Updated every 0.5 seconds
- **Total frame count**: Tracks all frames rendered since initialization
- **Automatic statistics on shutdown**: Prints comprehensive performance summary
- **Low overhead**: Minimal performance impact on rendering

## C++ API

### Getting FPS Information

```cpp
#include "rendering/Renderer.h"

// Get current FPS (updated every 0.5 seconds)
double fps = renderer->getFPS();

// Get total frame count
int totalFrames = renderer->getFrameCount();
```

### Automatic Statistics

When `shutdown()` is called, the renderer automatically prints performance statistics:

```
=== Metal Renderer Statistics ===
Total frames: 3600
Total time: 60.0 seconds
Average FPS: 60.0
==================================
```

## Python API

### Getting FPS Information

```python
import cyber_ui_core as ui

renderer = ui.create_metal_renderer()
renderer.initialize(800, 600, "FPS Demo")

# ... rendering loop ...

# Get current FPS
fps = renderer.get_fps()
print(f"Current FPS: {fps:.2f}")

# Get total frame count
frame_count = renderer.get_frame_count()
print(f"Total frames: {frame_count}")

# Shutdown prints final statistics automatically
renderer.shutdown()
```

## Implementation Details

### FPS Calculation

The FPS counter uses a rolling window approach:

1. **Frame counting**: Each call to `endFrame()` increments the frame counter
2. **Time tracking**: Uses high-resolution timers:
   - OpenGL: `glfwGetTime()` (GLFW's built-in timer)
   - Metal: `CACurrentMediaTime()` (Core Animation's media time)
3. **Update interval**: FPS is recalculated every 0.5 seconds
4. **Formula**: `FPS = frames_rendered / elapsed_time`

### Performance Impact

The FPS measurement has minimal overhead:
- Single timestamp query per frame
- Simple arithmetic operations
- No GPU synchronization (except when textures are created)
- Negligible memory footprint (4 variables)

### Statistics on Shutdown

When the renderer shuts down, it automatically calculates and prints:
- **Total frames**: All frames rendered during the session
- **Total time**: Time from initialization to shutdown
- **Average FPS**: Overall average across the entire session

## Example: FPS Display in Application

```python
import cyber_ui_core as ui
import time

renderer = ui.create_metal_renderer()
renderer.initialize(800, 600, "FPS Monitor")

rect = ui.Rectangle(100, 100)
rect.set_position(350, 250)
rect.set_color(0.0, 0.5, 1.0, 1.0)

frame_count = 0
last_print_time = time.time()

while not renderer.should_close():
    renderer.begin_frame()
    renderer.render_object(rect)
    renderer.end_frame()
    renderer.poll_events()
    
    frame_count += 1
    
    # Print FPS every second
    current_time = time.time()
    if current_time - last_print_time >= 1.0:
        fps = renderer.get_fps()
        print(f"FPS: {fps:.2f}")
        last_print_time = current_time

# Final statistics printed automatically
renderer.shutdown()
```

## Typical FPS Values

### Expected Performance

- **Metal Renderer (macOS)**:
  - Simple scenes: 1000-3000+ FPS
  - Complex scenes with textures: 60-120 FPS (often vsync-limited)
  - With off-screen rendering: 60-120 FPS

- **OpenGL Renderer**:
  - Simple scenes: 500-2000+ FPS
  - Complex scenes with textures: 60-120 FPS (often vsync-limited)
  - With off-screen rendering: 60-120 FPS

### VSync Limiting

Most systems enable VSync by default, which caps FPS at the display refresh rate (typically 60 Hz). This is normal and prevents screen tearing.

To see uncapped FPS:
- Disable VSync in the renderer (if supported)
- Use off-screen rendering
- Render to texture without presenting

## Troubleshooting

### Low FPS

If you're experiencing low FPS:

1. **Check GPU usage**: Use system monitoring tools
2. **Profile rendering**: Identify bottlenecks
3. **Reduce draw calls**: Batch similar objects
4. **Optimize textures**: Use appropriate sizes and formats
5. **Check for synchronization**: Avoid unnecessary `glFinish()` or `waitUntilCompleted()`

### FPS Shows 0.00

This can happen if:
- Less than 0.5 seconds have elapsed since the last update
- The application just started
- The renderer is paused or not rendering

Wait for at least 0.5 seconds of rendering for accurate FPS readings.

## Testing

Run the FPS measurement test:

```bash
PYTHONPATH=build python3 tests/test_fps_measurement.py
```

This test:
- Creates a simple scene
- Renders 120 frames
- Measures FPS
- Prints statistics on shutdown

## Future Enhancements

Potential improvements:
- Frame time histogram
- Min/max FPS tracking
- GPU time measurement
- Per-object rendering time
- Frame time graph visualization
- Export statistics to file

## Related Documentation

- [OpenGL Backend](OPENGL_BACKEND.md) - OpenGL renderer implementation
- [3D Rendering](3D_RENDERING.md) - 3D scene rendering
- [Capture System](CAPTURE_SYSTEM.md) - Frame capture for debugging
