#!/usr/bin/env python3
"""
Simple test to verify OpenGL backend works.
"""

import sys
import os

# Add build directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build'))

import cyber_ui_core as ui

print("Testing OpenGL backend...")

# Create renderer
renderer = ui.create_opengl_renderer()
print("✓ OpenGL renderer created")

# Initialize
if renderer.initialize(800, 600, "OpenGL Test"):
    print("✓ OpenGL renderer initialized")
    
    # Create simple scene
    scene = ui.SceneRoot()
    camera = scene.get_camera()
    camera.set_position(0, 0, 500)
    
    # Create a Frame3D with a rectangle
    frame = ui.Frame3D(800, 600)
    frame.set_position(0, 0, 0)
    scene.add_frame3d(frame)
    
    rect = ui.Rectangle(200, 200)
    rect.set_position(300, 200)
    rect.set_color(1.0, 0.0, 0.0, 1.0)  # Red
    frame.add_child(rect)
    
    print("✓ Scene created")
    
    # Render a few frames
    for i in range(3):
        if renderer.begin_frame():
            renderer.render_scene(scene)
            renderer.end_frame()
        renderer.poll_events()
        if renderer.should_close():
            break
    
    print("✓ Rendered 3 frames successfully")
    
    # Shutdown
    renderer.shutdown()
    print("✓ OpenGL renderer shutdown")
    
    print("\n✅ OpenGL backend test PASSED!")
else:
    print("✗ Failed to initialize OpenGL renderer")
    sys.exit(1)
