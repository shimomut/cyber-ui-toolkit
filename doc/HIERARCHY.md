# Graphics Primitive Hierarchy

This document describes the parent-child hierarchy system for graphics primitives in the Cyber UI Toolkit.

## Overview

The toolkit now supports a hierarchical scene graph with two main container types:
- **Frame3D**: Top-level 3D container with position, rotation, and scale
- **Frame2D**: 2D container with clipping capabilities

All 2D objects (Frame2D, Shape2D, and their subclasses) inherit from **Object2D**, which provides the base hierarchy functionality.

## Class Hierarchy

```
Frame3D (standalone, not inheriting from Object2D)
├── Can contain: Object2D and all its subclasses
│
Object2D (abstract base class for all 2D objects)
├── Frame2D (2D container with clipping)
│   └── Can contain: Object2D and all its subclasses
│       ├── Frame2D (nested frames)
│       ├── Shape2D
│       └── Rectangle, Circle, etc.
│
└── Shape2D (base class for 2D shapes)
    ├── Rectangle
    ├── Circle (future)
    └── Other shapes...
```

## Frame3D

Top-level 3D frame that positions 2D content in 3D space.

### Properties
- **3D Position**: (x, y, z) coordinates in 3D space
- **3D Rotation**: (pitch, yaw, roll) orientation
- **3D Scale**: (x, y, z) scaling factors
- **Visibility**: Show/hide the frame and all its children
- **Name**: Debug identifier

### Methods
```cpp
void setPosition(float x, float y, float z);
void getPosition(float& x, float& y, float& z) const;

void setRotation(float pitch, float yaw, float roll);
void getRotation(float& pitch, float& yaw, float& roll) const;

void setScale(float x, float y, float z);
void getScale(float& x, float& y, float& z) const;

void addChild(std::shared_ptr<Object2D> child);
void removeChild(std::shared_ptr<Object2D> child);
```

### Use Cases
- Positioning UI panels in 3D space
- Creating HUD elements with depth
- Building 3D UI layouts for VR/AR applications

## Object2D

Abstract base class for all 2D objects in the scene hierarchy.

### Properties
- **2D Position**: (x, y) coordinates in 2D space
- **Parent**: Reference to parent Object2D (if any)
- **Children**: List of child Object2D objects
- **Visibility**: Show/hide the object and all its children
- **Name**: Debug identifier

### Methods
```cpp
void setPosition(float x, float y);
void getPosition(float& x, float& y) const;

void addChild(std::shared_ptr<Object2D> child);
void removeChild(std::shared_ptr<Object2D> child);
Object2D* getParent() const;

void setVisible(bool visible);
bool isVisible() const;

virtual void render() = 0;  // Must be implemented by subclasses
```

## Frame2D

2D container that can hold other 2D objects with optional clipping.

### Properties
- All Object2D properties
- **Size**: (width, height) for clipping region
- **Clipping Enabled**: Whether to clip children to the frame bounds

### Methods
```cpp
void setSize(float width, float height);
void getSize(float& width, float& height) const;

void setClippingEnabled(bool enabled);
bool isClippingEnabled() const;
```

### Use Cases
- Creating scrollable containers
- Implementing viewport clipping
- Building nested UI layouts
- Organizing complex UI hierarchies

## Shape2D

Base class for all 2D shapes (Rectangle, Circle, etc.).

### Properties
- All Object2D properties
- **Color**: RGBA color values
- **Image/Texture**: Optional texture for the shape

### Subclasses
- **Rectangle**: Rectangular shape with width and height

## Hierarchy Rules

1. **Frame3D** can only contain **Object2D** and its subclasses
2. **Frame2D** can contain any **Object2D** subclass, including other Frame2D objects
3. **Shape2D** objects can contain other **Object2D** objects as children
4. When a parent is hidden (visible=false), all children are also hidden
5. Transforms are relative to the parent (positions are in parent's coordinate space)

## Example Usage (C++)

```cpp
// Create a 3D frame
auto frame3d = std::make_shared<Frame3D>();
frame3d->setPosition(0.0f, 0.0f, -5.0f);
frame3d->setRotation(0.0f, 0.0f, 0.0f);

// Create a 2D container with clipping
auto container = std::make_shared<Frame2D>();
container->setPosition(100.0f, 100.0f);
container->setSize(400.0f, 300.0f);
container->setClippingEnabled(true);

// Create rectangles
auto rect1 = std::make_shared<Rectangle>(200.0f, 150.0f);
rect1->setPosition(50.0f, 50.0f);
rect1->setColor(1.0f, 0.0f, 0.0f, 1.0f);

auto rect2 = std::make_shared<Rectangle>(100.0f, 100.0f);
rect2->setPosition(150.0f, 100.0f);
rect2->setColor(0.0f, 1.0f, 0.0f, 1.0f);

// Build hierarchy
container->addChild(rect1);
container->addChild(rect2);
frame3d->addChild(container);

// Render the entire hierarchy
frame3d->render();
```

## Example Usage (Python)

```python
import cyber_ui_core as ui

# Create a 3D frame
frame3d = ui.Frame3D()
frame3d.set_position(0.0, 0.0, -5.0)
frame3d.set_rotation(0.0, 0.0, 0.0)

# Create a 2D container with clipping
container = ui.Frame2D()
container.set_position(100.0, 100.0)
container.set_size(400.0, 300.0)
container.set_clipping_enabled(True)

# Create rectangles
rect1 = ui.Rectangle(200.0, 150.0)
rect1.set_position(50.0, 50.0)
rect1.set_color(1.0, 0.0, 0.0, 1.0)

rect2 = ui.Rectangle(100.0, 100.0)
rect2.set_position(150.0, 100.0)
rect2.set_color(0.0, 1.0, 0.0, 1.0)

# Build hierarchy
container.add_child(rect1)
container.add_child(rect2)
frame3d.add_child(container)

# Render the entire hierarchy
frame3d.render()
```

## Benefits of Hierarchical Structure

1. **Organized Scene Management**: Group related objects together
2. **Relative Positioning**: Child positions are relative to parent
3. **Batch Visibility Control**: Hide/show entire subtrees
4. **Clipping Support**: Frame2D provides viewport clipping
5. **3D Positioning**: Frame3D allows positioning 2D UI in 3D space
6. **Scalability**: Easy to build complex UI layouts
