#!/usr/bin/env python3
"""
Visual test for OpenGL - should show a bright red square.
If you see a gray window with a red square, OpenGL is working!
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build'))

import cyber_ui_core as ui

print("=" * 60)
print("OpenGL Visual Test")
print("=" * 60)
print()
print("You should see:")
print("  - A window titled 'OpenGL Visual Test'")
print("  - Gray background")
print("  - Large RED square in the center")
print()
print("If you see this, OpenGL is working correctly!")
print("Press ESC or close window to exit")
print("=" * 60)
print()

# Create renderer
renderer = ui.create_opengl_renderer()

# Initialize with smaller window for easier visibility
if not renderer.initialize(600, 600, "OpenGL Visual Test"):
    print("ERROR: Failed to initialize renderer!")
    sys.exit(1)

# Create simple 2D scene (no 3D transforms)
rect = ui.Rectangle(400, 400)
rect.set_position(100, 100)  # Centered in 600x600 window
rect.set_color(1.0, 0.0, 0.0, 1.0)  # Bright red, full opacity

print("Rendering... (window should be visible now)")

# Render loop
frame_count = 0
while not renderer.should_close():
    if renderer.begin_frame():
        renderer.render_object(rect)
        renderer.end_frame()
    
    renderer.poll_events()
    frame_count += 1
    
    # Print status every 2 seconds
    if frame_count % 120 == 0:
        print(f"Still rendering... ({frame_count} frames)")

print(f"\nRendered {frame_count} frames total")
renderer.shutdown()
print("Test complete!")
