#!/usr/bin/env python3
"""
Quick OpenGL test - renders one frame and checks if rectangle is visible.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build'))

import cyber_ui_core as ui

print("=" * 60)
print("Quick OpenGL Test")
print("=" * 60)

# Create renderer
renderer = ui.create_opengl_renderer()

# Initialize
if not renderer.initialize(600, 600, "OpenGL Quick Test"):
    print("ERROR: Failed to initialize renderer!")
    sys.exit(1)

# Create red rectangle
rect = ui.Rectangle(400, 400)
rect.set_position(100, 100)
rect.set_color(1.0, 0.0, 0.0, 1.0)  # Bright red

print("Rendering single frame...")

# Render one frame
if renderer.begin_frame():
    renderer.render_object(rect)
    renderer.end_frame()
    print("Frame rendered successfully")
else:
    print("ERROR: Failed to begin frame")
    sys.exit(1)

# Keep window open for 5 seconds so you can see the red rectangle
import time
print("\nWindow will stay open for 5 seconds...")
print("You should see a RED 400x400 rectangle at position (100, 100)")
print("Press ESC to close early\n")

for i in range(50):
    renderer.poll_events()
    if renderer.should_close():
        print("Window closed by user")
        break
    time.sleep(0.1)

renderer.shutdown()
print("Test complete!")
