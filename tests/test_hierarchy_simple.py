#!/usr/bin/env python3
"""
Simplified hierarchy test to debug OpenGL rendering
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build'))

import cyber_ui_core as ui

print("=" * 60)
print("Simple Hierarchy Test - OpenGL")
print("=" * 60)

# Create renderer
renderer = ui.create_opengl_renderer()

if not renderer.initialize(800, 600, "Simple Hierarchy Test"):
    print("ERROR: Failed to initialize renderer!")
    sys.exit(1)

print("✓ Renderer initialized")

# Create scene and camera
scene = ui.SceneRoot()
camera = scene.get_camera()

# Configure camera
camera.set_position(0.0, 0.0, 800.0)
camera.set_rotation(0.0, 0.0, 0.0)
camera.set_perspective(1.0472, 800.0/600.0, 0.1, 2000.0)
print("✓ Camera configured")

# Create a single Frame3D
frame3d = ui.Frame3D(400, 300)
frame3d.set_name("TestFrame3D")
frame3d.set_position(0.0, 0.0, 0.0)  # At origin
frame3d.set_rotation(0.0, 0.0, 0.0)
frame3d.set_scale(1.0, 1.0, 1.0)
print("✓ Created Frame3D at origin")

# Create a Frame2D inside it
frame2d = ui.Frame2D(400.0, 300.0)
frame2d.set_name("TestFrame2D")
frame2d.set_position(0.0, 0.0)
frame2d.set_clipping_enabled(False)
print("✓ Created Frame2D")

# Create a simple red rectangle
rect = ui.Rectangle(200.0, 200.0)
rect.set_name("TestRect")
rect.set_position(200.0, 150.0)  # Center of Frame2D
rect.set_color(1.0, 0.0, 0.0, 1.0)  # Red
print("✓ Created red rectangle")

# Build hierarchy
frame2d.add_child(rect)
frame3d.add_child(frame2d)
scene.add_frame3d(frame3d)
print("✓ Built hierarchy: Scene -> Frame3D -> Frame2D -> Rectangle")

print("\nStarting render loop...")
print("You should see a RED square in the center")
print("Press ESC to exit\n")

frame_count = 0
while not renderer.should_close():
    if renderer.begin_frame():
        renderer.render_scene(scene)
        renderer.end_frame()
    
    renderer.poll_events()
    frame_count += 1
    
    if frame_count == 1:
        print(f"First frame rendered")
    elif frame_count % 120 == 0:
        print(f"Still rendering... ({frame_count} frames)")

print(f"\nRendered {frame_count} frames")
renderer.shutdown()
print("Done!")
