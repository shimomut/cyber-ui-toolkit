#!/usr/bin/env python3
"""
Capture a single frame from hierarchy demo to verify Frame2D works there.
"""

import sys
import os

# Run hierarchy demo for 1 frame and capture
sys.path.insert(0, '../build')
os.chdir('../samples/basic')

# Import after changing directory
import cyber_ui_core as ui
from PIL import Image as PILImage

# Just run the first part of hierarchy demo
renderer = ui.create_metal_renderer()
if not renderer.initialize(1024, 768, "Test"):
    print("Failed")
    sys.exit(1)

scene = ui.SceneRoot()
camera = scene.get_camera()
camera.set_position(0.0, 0.0, 800.0)
camera.set_perspective(1.0472, 1024.0/768.0, 0.1, 2000.0)

frame3d = ui.Frame3D(800, 600)
frame3d.set_position(0.0, 0.0, 0.0)
scene.add_frame3d(frame3d)

# Create a simple Frame2D like in hierarchy demo
left_panel = ui.Frame2D(250.0, 650.0)
left_panel.set_position(50.0, 50.0)
left_panel
left_panel.set_clipping_enabled(True)

# Background
left_bg = ui.Rectangle(250.0, 650.0)
left_bg.set_position(0.0, 0.0)
left_bg.set_color(0.15, 0.15, 0.2, 1.0)
left_panel.add_child(left_bg)

# A rectangle
rect = ui.Rectangle(210.0, 80.0)
rect.set_position(20.0, 80.0)
rect.set_color(0.2, 0.4, 0.6, 1.0)
left_panel.add_child(rect)

frame3d.add_child(left_panel)

# Render
if renderer.begin_frame():
    renderer.render_scene(scene)
    renderer.end_frame()

# Capture
os.chdir('../../tests')
output_file = "output/hierarchy_test_capture.png"
os.makedirs("output", exist_ok=True)

if renderer.save_capture(output_file):
    print(f"Saved to: {output_file}")
    
    img = PILImage.open(output_file)
    pixels = list(img.getdata())
    
    bg_color = (26, 26, 26, 255)
    non_bg = sum(1 for p in pixels if abs(p[0] - bg_color[0]) > 30 or 
                  abs(p[1] - bg_color[1]) > 30 or 
                  abs(p[2] - bg_color[2]) > 30)
    
    print(f"Non-background: {non_bg} ({non_bg/len(pixels)*100:.2f}%)")
    
    if non_bg > 0:
        print("✓ Frame2D content is visible!")
    else:
        print("✗ Frame2D content NOT visible")

renderer.shutdown()
