# Object2D Coordinate System

## Overview

All Object2D classes (Rectangle, Text, Frame2D) use a **top-left origin** coordinate system. This document clarifies how positioning works throughout the hierarchy.

## Coordinate System Rules

### 1. Position Refers to Top-Left Corner

When you set an object's position, you're specifying where its **top-left corner** should be:

```python
rect = ui.Rectangle(100, 50)
rect.set_position(20, 30)
# Rectangle's top-left corner is at (20, 30)
# Rectangle's bottom-right corner is at (120, 80)
```

### 2. Frame2D Children Use Top-Left Origin

Children are positioned relative to their parent's **top-left corner**:

```python
frame2d = ui.Frame2D()
frame2d.set_size(500, 600)

child = ui.Rectangle(100, 100)
child.set_position(0, 0)  # At Frame2D's top-left corner
frame2d.add_child(child)

child2 = ui.Rectangle(50, 50)
child2.set_position(100, 100)  # 100 pixels from Frame2D's top-left
frame2d.add_child(child2)
```

### 3. Frame3D Uses Centered Positioning

Frame3D itself is positioned by its **center** in 3D space (standard for 3D objects):

```python
frame3d = ui.Frame3D()
frame3d.set_position(0, 0, 0)  # Frame3D's center at origin
```

But Frame3D's children (Object2D) still use top-left origin relative to Frame3D.

## Axis Directions

### 2D Space (Object2D)
- **X-axis**: Right is positive, Left is negative
- **Y-axis**: Down is positive, Up is negative
- **Origin**: Top-left corner

### 3D Space (Frame3D)
- **X-axis**: Right is positive, Left is negative
- **Y-axis**: Up is positive, Down is negative
- **Z-axis**: Forward (toward camera) is negative, Backward is positive
- **Origin**: Center of object

## Complete Example

```python
# Create Frame3D (centered in 3D space)
frame3d = ui.Frame3D()
frame3d.set_position(0, 0, 0)  # Center at world origin

# Create Frame2D container
frame2d = ui.Frame2D()
frame2d.set_position(100, 50)  # Frame2D's center at (100, 50) relative to Frame3D
frame2d.set_size(400, 300)
frame3d.add_child(frame2d)

# Add rectangle to Frame2D
rect = ui.Rectangle(80, 60)
rect.set_position(10, 10)  # 10 pixels from Frame2D's top-left corner
frame2d.add_child(rect)

# Add text to Frame2D
text = ui.Text("Hello")
text.set_position(10, 80)  # Text's top-left at (10, 80) within Frame2D
frame2d.add_child(text)
```

**Resulting positions:**
- Frame2D's top-left corner: (100 - 200, 50 - 150) = (-100, -100)
- Rectangle's top-left: (-100, -100) + (10, 10) = (-90, -90)
- Rectangle's bottom-right: (-90, -90) + (80, 60) = (10, -30)
- Text's top-left: (-100, -100) + (10, 80) = (-90, -20)

## Migration from Centered Coordinates

If you were using the old centered coordinate system, you need to adjust positions:

**Old (centered):**
```python
rect = ui.Rectangle(100, 100)
rect.set_position(250, 300)  # Center at (250, 300)
```

**New (top-left):**
```python
rect = ui.Rectangle(100, 100)
rect.set_position(200, 250)  # Top-left at (200, 250), center at (250, 300)
```

**Conversion formula:**
```
new_x = old_x - (width / 2)
new_y = old_y - (height / 2)
```

## Text Alignment

Text alignment affects how text is rendered relative to its position:

```python
text = ui.Text("Hello")
text.set_position(100, 50)

# Left alignment (default)
text.set_alignment(ui.TextAlignment.Left)
# Text starts at (100, 50)

# Center alignment
text.set_alignment(ui.TextAlignment.Center)
# Text is centered horizontally around x=100

# Right alignment
text.set_alignment(ui.TextAlignment.Right)
# Text ends at x=100
```

Note: Vertical positioning is always from the top-left corner of the text bounding box.

## Clipping

Frame2D clipping uses the same top-left origin coordinate system:

```python
frame2d = ui.Frame2D()
frame2d.set_size(500, 600)
frame2d.set_clipping_enabled(True)

# Clipping region is from (0, 0) to (500, 600)
# Content outside this region will be clipped

rect = ui.Rectangle(100, 100)
rect.set_position(-50, -50)  # Partially clipped (top-left outside)
frame2d.add_child(rect)

rect2 = ui.Rectangle(100, 100)
rect2.set_position(450, 550)  # Partially clipped (bottom-right outside)
frame2d.add_child(rect2)
```

## Best Practices

1. **Think in terms of top-left corners** when positioning objects
2. **Use consistent spacing** by positioning from (0, 0) with offsets
3. **Account for object size** when centering manually:
   ```python
   # Center a 100x100 rectangle in a 500x600 Frame2D
   rect.set_position(200, 250)  # (500-100)/2, (600-100)/2
   ```
4. **Use Frame2D size for layout calculations**:
   ```python
   frame2d.get_size(width, height)
   # Position at bottom-right corner
   rect.set_position(width - rect_width, height - rect_height)
   ```

## See Also

- [3D_RENDERING.md](3D_RENDERING.md) - Complete rendering system documentation
- [COORDINATE_SYSTEM_FIX_2024.md](COORDINATE_SYSTEM_FIX_2024.md) - Implementation details
- [FRAME2D_KNOWN_ISSUES.md](FRAME2D_KNOWN_ISSUES.md) - Known issues and workarounds
