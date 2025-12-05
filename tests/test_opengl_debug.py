#!/usr/bin/env python3
"""
Debug OpenGL rendering - minimal test with verbose output.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build'))

import cyber_ui_core as ui

print("=== OpenGL Debug Test ===\n")

# Create renderer
print("1. Creating OpenGL renderer...")
renderer = ui.create_opengl_renderer()
print("   ✓ Renderer created\n")

# Initialize
print("2. Initializing renderer (800x600)...")
if not renderer.initialize(800, 600, "OpenGL Debug"):
    print("   ✗ Failed to initialize!")
    sys.exit(1)
print("   ✓ Renderer initialized\n")

# Create scene
print("3. Creating scene...")
scene = ui.SceneRoot()
camera = scene.get_camera()
camera.set_position(0, 0, 500)
print(f"   Camera position: {camera.get_position()}")
print(f"   Camera FOV: {camera.get_fov()}")
print("   ✓ Scene created\n")

# Create Frame3D
print("4. Creating Frame3D...")
frame = ui.Frame3D(800, 600)
frame.set_position(0, 0, 0)
scene.add_frame3d(frame)
print(f"   Frame3D size: {frame.get_size()}")
print(f"   Frame3D position: {frame.get_position()}")
print("   ✓ Frame3D created\n")

# Create a large red rectangle in center
print("5. Creating red rectangle (400x400 at center)...")
rect = ui.Rectangle(400, 400)
rect.set_position(200, 100)  # Center-ish
rect.set_color(1.0, 0.0, 0.0, 1.0)  # Bright red
frame.add_child(rect)
print(f"   Rectangle size: {rect.get_size()}")
print(f"   Rectangle position: {rect.get_position()}")
print(f"   Rectangle color: {rect.get_color()}")
print("   ✓ Rectangle created\n")

# Render loop
print("6. Starting render loop...")
print("   Press ESC or close window to exit\n")

frame_count = 0
max_frames = 300  # Run for ~5 seconds at 60fps

while not renderer.should_close() and frame_count < max_frames:
    if renderer.begin_frame():
        renderer.render_scene(scene)
        renderer.end_frame()
    
    renderer.poll_events()
    frame_count += 1
    
    if frame_count % 60 == 0:
        print(f"   Rendered {frame_count} frames...")

print(f"\n7. Rendered {frame_count} frames total")
print("   Shutting down...\n")

renderer.shutdown()
print("✅ Test complete!")
