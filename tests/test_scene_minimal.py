#!/usr/bin/env python3
"""
Minimal scene test - just a rectangle through render_scene
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build'))

import cyber_ui_core as ui

print("Testing render_scene with minimal setup...")

renderer = ui.create_opengl_renderer()
if not renderer.initialize(600, 600, "Minimal Scene Test"):
    print("Failed to initialize!")
    sys.exit(1)

# Create scene
scene = ui.SceneRoot()
camera = scene.get_camera()

# Simple orthographic-like setup
camera.set_position(0.0, 0.0, 500.0)
camera.set_perspective(1.0472, 1.0, 0.1, 1000.0)

# Create Frame3D at origin
frame3d = ui.Frame3D(600, 600)
frame3d.set_position(0.0, 0.0, 0.0)

# Create Frame2D
frame2d = ui.Frame2D(600.0, 600.0)
frame2d.set_position(0.0, 0.0)

# Create rectangle
rect = ui.Rectangle(400.0, 400.0)
rect.set_position(300.0, 300.0)  # Center
rect.set_color(1.0, 0.0, 0.0, 1.0)

# Build hierarchy
frame2d.add_child(rect)
frame3d.add_child(frame2d)
scene.add_frame3d(frame3d)

print("Hierarchy built. Rendering...")

frame_count = 0
while not renderer.should_close() and frame_count < 300:
    if renderer.begin_frame():
        renderer.render_scene(scene)
        renderer.end_frame()
    renderer.poll_events()
    frame_count += 1
    if frame_count == 1:
        print("First frame done")

print(f"Rendered {frame_count} frames")
renderer.shutdown()
