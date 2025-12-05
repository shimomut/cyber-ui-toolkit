# Hierarchy Demo - Debug Features

## Overview

The `hierarchy_demo.py` sample now includes interactive debugging features to help diagnose rendering issues like noise, texture problems, clipping artifacts, and animation glitches.

## Debug Controls

While the demo is running, you can toggle various rendering features using terminal input:

### Available Commands

| Key | Feature | Description |
|-----|---------|-------------|
| `t` | Texture Mapping | Toggle all texture rendering on/off |
| `c` | Clipping | Toggle Frame2D clipping on/off |
| `a` | Animation | Toggle 3D animations on/off |
| `q` | Quit | Exit the demo |

### Usage

1. Run the demo:
   ```bash
   python samples/basic/hierarchy_demo.py
   ```

2. While the window is running, type commands in the terminal:
   ```
   t [ENTER]  # Toggle textures
   c [ENTER]  # Toggle clipping
   a [ENTER]  # Toggle animation
   q [ENTER]  # Quit
   ```

3. The terminal will display the current state after each toggle:
   ```
   [T] Texture Mapping: OFF
   [C] Clipping: OFF
   [A] Animation: OFF
   ```

## Debugging Workflow

### Investigating Rendering Noise

1. **Start with everything enabled** - Run the demo normally
2. **Disable animation** (`a`) - Check if noise is animation-related
3. **Disable textures** (`t`) - Check if noise comes from texture sampling
4. **Disable clipping** (`c`) - Check if noise is from clipping artifacts

### Common Issues to Diagnose

- **Texture flickering**: Toggle textures off to see if noise disappears
- **Clipping artifacts**: Toggle clipping off to check border rendering
- **Animation jitter**: Toggle animation off to see static rendering
- **Coordinate issues**: With animation off, verify object positions

## Technical Details

### What Gets Toggled

**Texture Mapping (`t`)**:
- All gradient textures (title_rect, center_header)
- Checkerboard textures (ContentRect3, grid items)
- Icon textures (carousel items, grid items)

**Clipping (`c`)**:
- LeftPanel clipping
- NestedFrame clipping
- RightPanel clipping

**Animation (`a`)**:
- Frame3D rotations
- Frame3D positions (floating effect)
- Nested frame vertical oscillation
- Carousel item staggered movement

### Implementation Notes

- Uses non-blocking terminal input via `select.select()`
- Toggles are applied immediately without frame delay
- When animation is disabled, objects freeze at their current position/rotation
- Texture state is managed through `set_image()` calls (pass `None` to clear)

## Capture Mode

You can combine debug toggles with capture mode:

```bash
python samples/basic/hierarchy_demo.py --capture
```

This allows you to:
1. Toggle features during runtime
2. Capture frames with different feature combinations
3. Compare captured images to identify the source of issues

## Example Debug Session

```bash
# Start the demo
python samples/basic/hierarchy_demo.py

# In terminal:
t [ENTER]    # Turn off textures - does noise persist?
c [ENTER]    # Turn off clipping - does noise disappear?
a [ENTER]    # Turn off animation - is rendering stable?

# Re-enable features one by one to isolate the issue
a [ENTER]    # Animation back on
c [ENTER]    # Clipping back on
t [ENTER]    # Textures back on

q [ENTER]    # Exit when done
```
