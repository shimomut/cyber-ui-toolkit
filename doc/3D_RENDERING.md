# 3D Rendering System

## Overview

The Cyber UI Toolkit now supports full 3D rendering with camera control and automatic scene tree traversal. This document describes the 3D rendering architecture and how to use it.

## Architecture

### Camera Class

The `Camera` class defines the viewpoint for 3D rendering:

**Properties:**
- **Position**: (x, y, z) coordinates in 3D space
- **Rotation**: Euler angles (pitch, yaw, roll) for camera orientation
- **Perspective**: Field of view, aspect ratio, near/far clipping planes

**Methods:**
```cpp
void setPosition(float x, float y, float z);
void setRotation(float pitch, float yaw, float roll);
void setPerspective(float fov, float aspect, float near, float far);
```

**Default Configuration:**
- Position: (0, 0, 5)
- Rotation: (0, 0, 0)
- FOV: 60 degrees (1.0472 radians)
- Aspect: 16:9
- Near/Far: 0.1 / 100.0

### SceneRoot Class

The `SceneRoot` class manages the entire scene hierarchy:

**Features:**
- Contains multiple Frame3D objects
- Manages the camera
- Provides scene-level operations

**Methods:**
```cpp
void addFrame3D(std::shared_ptr<Frame3D> frame);
void removeFrame3D(std::shared_ptr<Frame3D> frame);
void setCamera(std::shared_ptr<Camera> camera);
std::shared_ptr<Camera> getCamera() const;
void clear();
```

### Automatic Scene Traversal

The renderer now automatically traverses the entire scene tree:

1. **SceneRoot** → Contains Frame3D objects and Camera
2. **Frame3D** → 3D containers with position, rotation, scale
3. **Object2D** → 2D objects (Frame2D, Shape2D, Rectangle, etc.)
4. **Children** → Recursively rendered with inherited transforms

## Transform Hierarchy

Transforms are applied hierarchically:

```
Camera (View + Projection)
  ↓
Frame3D (Model Transform: position, rotation, scale)
  ↓
Object2D (2D Translation)
  ↓
Children (Relative to parent)
```

### Matrix Math

The rendering system uses 4x4 matrices (column-major):

- **View Matrix**: Camera position and orientation
- **Projection Matrix**: Perspective projection
- **Model Matrix**: Frame3D transform (TRS: Translation, Rotation, Scale)
- **MVP Matrix**: Combined Model-View-Projection for each object

## Usage

### Python Example

```python
import cyber_ui_core as ui

# Create renderer
renderer = ui.create_metal_renderer()
renderer.initialize(1024, 768, "3D Demo")

# Create scene and configure camera
scene = ui.SceneRoot()
camera = scene.get_camera()
camera.set_position(0.0, 0.0, 800.0)
camera.set_rotation(0.0, 0.0, 0.0)
camera.set_perspective(1.0472, 1024.0/768.0, 0.1, 2000.0)

# Create Frame3D with 3D transform
frame3d = ui.Frame3D()
frame3d.set_position(-200.0, 0.0, -100.0)
frame3d.set_rotation(0.0, 0.3, 0.0)  # Rotate 0.3 radians around Y
frame3d.set_scale(1.0, 1.0, 1.0)

# Create 2D content
panel = ui.Frame2D()
panel.set_position(0.0, 0.0)
panel.set_size(300.0, 400.0)

rect = ui.Rectangle(200.0, 150.0)
rect.set_position(50.0, 50.0)
rect.set_color(1.0, 0.5, 0.2, 1.0)

# Build hierarchy
panel.add_child(rect)
frame3d.add_child(panel)
scene.add_frame3d(frame3d)

# Render loop
while not renderer.should_close():
    renderer.poll_events()
    
    # Animate Frame3D
    time += 0.01
    frame3d.set_rotation(0.0, math.sin(time) * 0.5, 0.0)
    
    if renderer.begin_frame():
        # Automatic scene traversal
        renderer.render_scene(scene)
        renderer.end_frame()

renderer.shutdown()
```

### C++ Example

```cpp
#include "core/SceneRoot.h"
#include "core/Camera.h"
#include "core/Frame3D.h"
#include "core/Frame2D.h"
#include "rendering/Shape2D.h"
#include "rendering/Renderer.h"

using namespace CyberUI;

// Create renderer
auto renderer = createMetalRenderer();
renderer->initialize(1024, 768, "3D Demo");

// Create scene
auto scene = std::make_shared<SceneRoot>();
auto camera = scene->getCamera();
camera->setPosition(0.0f, 0.0f, 800.0f);
camera->setPerspective(1.0472f, 1024.0f/768.0f, 0.1f, 2000.0f);

// Create Frame3D
auto frame3d = std::make_shared<Frame3D>();
frame3d->setPosition(-200.0f, 0.0f, -100.0f);
frame3d->setRotation(0.0f, 0.3f, 0.0f);

// Create 2D content
auto panel = std::make_shared<Frame2D>();
panel->setPosition(0.0f, 0.0f);
panel->setSize(300.0f, 400.0f);

auto rect = std::make_shared<Rectangle>(200.0f, 150.0f);
rect->setPosition(50.0f, 50.0f);
rect->setColor(1.0f, 0.5f, 0.2f, 1.0f);

// Build hierarchy
panel->addChild(rect);
frame3d->addChild(panel);
scene->addFrame3D(frame3d);

// Render loop
while (!renderer->shouldClose()) {
    renderer->pollEvents();
    
    if (renderer->beginFrame()) {
        renderer->renderScene(scene.get());
        renderer->endFrame();
    }
}

renderer->shutdown();
```

## Coordinate Systems

### 3D Space (Frame3D)
- **X**: Right (positive) / Left (negative)
- **Y**: Up (positive) / Down (negative)
- **Z**: Forward (negative) / Backward (positive)
- Camera looks down negative Z axis by default

### 2D Space (Object2D)
- **X**: Right (positive) / Left (negative)
- **Y**: Down (positive) / Up (negative)
- Origin at top-left of parent

## Performance Considerations

### Optimization Tips

1. **Minimize Frame3D count**: Group related content in single Frame3D
2. **Use visibility flags**: Hide entire subtrees with `setVisible(false)`
3. **Batch similar objects**: Group objects with same textures
4. **Limit hierarchy depth**: Deep nesting increases transform calculations
5. **Reuse matrices**: Cache MVP matrices when possible

### Rendering Pipeline

1. Begin frame
2. For each Frame3D in scene:
   - Calculate Model matrix (TRS)
   - Combine with View-Projection matrix
   - For each Object2D child:
     - Apply 2D translation
     - Render shape with combined MVP
     - Recursively render children
3. End frame

## Migration from Legacy API

### Old Way (Manual Rendering)

```python
# Old: Manual rendering of each object
if renderer.begin_frame():
    renderer.render_object(panel1)
    renderer.render_object(panel2)
    renderer.render_object(panel3)
    renderer.end_frame()
```

### New Way (Automatic Scene Traversal)

```python
# New: Automatic scene traversal
scene.add_frame3d(frame3d1)
scene.add_frame3d(frame3d2)
scene.add_frame3d(frame3d3)

if renderer.begin_frame():
    renderer.render_scene(scene)
    renderer.end_frame()
```

**Benefits:**
- Automatic transform hierarchy
- Cleaner code
- Better performance (matrix caching)
- Easier to manage complex scenes

## Limitations

- No depth testing between Frame3D objects (render order matters)
- No frustum culling (all objects rendered)
- No occlusion culling
- Limited to orthographic 2D shapes in 3D space

## Future Enhancements

- Depth buffer support for proper 3D ordering
- Frustum culling for performance
- 3D shapes (cubes, spheres, meshes)
- Lighting system
- Shadow rendering
- Post-processing effects

## See Also

- [HIERARCHY.md](HIERARCHY.md) - Scene hierarchy documentation
- [samples-hierarchy.md](samples-hierarchy.md) - 3D hierarchy demo sample
- [TEXTURE_IMPLEMENTATION.md](TEXTURE_IMPLEMENTATION.md) - Texture system
