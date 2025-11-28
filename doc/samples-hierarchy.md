# Hierarchy Demo Sample

## Overview

The `hierarchy_demo.py` sample demonstrates the hierarchical scene graph capabilities of the Cyber UI Toolkit, showcasing how Frame3D, Frame2D, and Rectangle objects work together to create complex UI layouts.

## What This Sample Demonstrates

### 1. Multiple Frame3D Containers
- Creates three separate Frame3D containers with different 3D positions and rotations
- Demonstrates how Frame3D can organize different sections of UI
- Shows 3D transform properties (position, rotation, scale) being set
- Note: 3D transforms are stored but not yet applied during rendering

### 2. Frame2D - 2D Containers with Clipping
- **Left Panel**: Frame2D with clipping enabled, containing a vertical list of content items
- **Center Panel**: Frame2D without clipping, containing a nested Frame2D with a 4x4 grid
- **Right Panel**: Frame2D with clipping, containing animated carousel items

### 3. Nested Hierarchy
- Shows Frame2D nested inside another Frame2D
- Demonstrates how clipping works at different hierarchy levels
- Illustrates relative positioning (child positions are relative to parent)

### 4. Rectangle Shapes
- Solid color rectangles for backgrounds and UI elements
- Textured rectangles using gradient, checkerboard, and icon images
- Grid layout of rectangles (4x4 grid in nested frame)
- Carousel-style overlapping rectangles with animated movement

## Scene Structure

```
Frame3D_Left (position: 0, 0, 0)
└── Frame2D (LeftPanel) [clipping: ON]
    ├── Rectangle (Background)
    ├── Rectangle (Title with gradient texture)
    └── 6x Rectangle (Content items, one with checkerboard texture)

Frame3D_Center (position: 0, 0, -2, rotation: 0, 0.1, 0)
└── Frame2D (CenterPanel) [clipping: OFF]
    ├── Rectangle (Background)
    ├── Rectangle (Header with gradient texture)
    └── Frame2D (NestedFrame) [clipping: ON]
        ├── Rectangle (Background)
        └── 16x Rectangle (4x4 grid with mixed textures)

Frame3D_Right (position: 0, 0, 2, rotation: 0, -0.1, 0)
└── Frame2D (RightPanel) [clipping: ON]
    ├── Rectangle (Background)
    └── 5x Rectangle (Carousel items with alternating textures)
```

## Key Concepts Illustrated

### Hierarchical Positioning
All child objects use positions relative to their parent:
```python
# Parent at (400, 50)
center_panel.set_position(400.0, 50.0)

# Child at (25, 100) relative to parent
# Actual screen position: (425, 150)
nested_frame.set_position(25.0, 100.0)
```

### Clipping Behavior
Frame2D can clip children to its bounds:
```python
left_panel.set_clipping_enabled(True)  # Children clipped to 300x400
center_panel.set_clipping_enabled(False)  # Children can extend beyond bounds
```

### Animation
The sample includes two types of animation:
- **Nested frame movement**: Vertical oscillation demonstrating dynamic positioning within the hierarchy
- **Carousel items**: Staggered vertical movement creating a wave effect

### Multiple Frame3D Containers
The sample demonstrates three Frame3D containers with different 3D properties:
- **Frame3D_Left**: Positioned at origin (0, 0, 0) with no rotation
- **Frame3D_Center**: Positioned forward in Z (-2) with slight Y rotation (0.1)
- **Frame3D_Right**: Positioned back in Z (2) with opposite Y rotation (-0.1)

Note: Frame3D transformations (position, rotation, scale) are stored but not currently applied during rendering as the renderer only accepts Object2D types. Frame3D serves as a logical container for organizing the scene hierarchy and will support full 3D transforms in future updates.

### Texture Application
Demonstrates three ways to use textures:
1. **Background textures**: Full-size textured rectangles
2. **Tinted textures**: Colored rectangles with textures
3. **Mixed content**: Some rectangles with textures, others with solid colors

## Running the Sample

```bash
# From the project root
cd samples/basic
python3 hierarchy_demo.py
```

### Requirements
- Built `cyber_ui_core` module in `build/` directory
- Python 3.x with PIL/Pillow installed
- Test images in `samples/data/` directory:
  - `gradient.png`
  - `checkerboard.png`
  - `icon.png`

## Expected Output

The sample creates a window showing three distinct panels organized by separate Frame3D containers:

1. **Left Panel** (dark blue-gray): Vertical list with title and 6 content items
2. **Center Panel** (dark teal): Contains a nested frame with a 4x4 grid of colored and textured rectangles
3. **Right Panel** (dark green): Carousel-style layout with 5 overlapping items

The nested frame in the center panel oscillates vertically, and the carousel items in the right panel move in a staggered wave pattern.

## Learning Points

### For Beginners
- How to create and organize UI elements hierarchically
- Understanding parent-child relationships
- Basic positioning and sizing of rectangles
- Applying colors and textures to shapes

### For Advanced Users
- Implementing complex nested layouts
- Using clipping for viewport management
- Combining 3D and 2D transformations
- Creating animated UI elements
- Building reusable container components

## Extending This Sample

Try these modifications to learn more:

1. **Add more nesting levels**: Create Frame2D inside the nested frame
2. **Implement scrolling**: Animate child positions to simulate scrolling
3. **Add interaction**: Detect mouse clicks on rectangles (requires event system)
4. **Create custom layouts**: Build grid, stack, or flow layouts
5. **Experiment with clipping**: Toggle clipping on/off to see the difference
6. **3D effects**: Adjust Frame3D position and rotation for different perspectives

## Related Documentation

- [HIERARCHY.md](HIERARCHY.md) - Complete hierarchy system documentation
- [samples-basic.md](samples-basic.md) - Basic shape rendering samples
- [TEXTURE_IMPLEMENTATION.md](TEXTURE_IMPLEMENTATION.md) - Texture system details

## Troubleshooting

### Rectangles not visible
- Check that Frame3D and Frame2D visibility is set to true (default)
- Verify positions are within the window bounds
- Ensure colors have alpha > 0

### Textures not loading
- Verify image files exist in `samples/data/`
- Check console output for loading errors
- Ensure PIL/Pillow is installed: `pip install Pillow`

### Clipping not working
- Verify `set_clipping_enabled(True)` is called
- Check that Frame2D size is set correctly
- Ensure child positions are relative to parent

### Animation stuttering
- This is expected on some systems
- Frame rate depends on display refresh rate
- Animation is for demonstration only
