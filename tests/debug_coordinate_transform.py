#!/usr/bin/env python3
"""
Debug coordinate transformation - test if coordinates are being transformed correctly.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build'))

import cyber_ui_core as ui
from PIL import Image as PILImage
import numpy as np


def main():
    print("Coordinate Transform Debug")
    print("=" * 70)
    
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(800, 700, "Coordinate Debug"):
        print("Failed to initialize renderer")
        return 1
    
    scene = ui.SceneRoot()
    camera = scene.get_camera()
    camera.set_position(0, 0, 800)
    camera.set_perspective(1.0472, 1600.0/1400.0, 0.1, 2000.0)
    
    # Create Frame3D at origin
    frame3d = ui.Frame3D()
    frame3d.set_position(0, 0, 0)
    scene.add_frame3d(frame3d)
    
    # Test 1: Rectangle directly in Frame3D (no Frame2D)
    print("Test 1: Rectangle directly in Frame3D")
    print("  Position: (0, 0)")
    print("  Size: 100x100")
    
    rect_direct = ui.Rectangle(100, 100)
    rect_direct.set_position(0, 0)
    rect_direct.set_color(1.0, 0.0, 0.0, 1.0)  # Red
    frame3d.add_child(rect_direct)
    
    # Render
    for i in range(5):
        renderer.poll_events()
        if renderer.should_close():
            break
        renderer.begin_frame()
        renderer.render_scene(scene)
        renderer.end_frame()
    
    # Capture
    os.makedirs("tests/output", exist_ok=True)
    renderer.save_capture("tests/output/coord_test1.png")
    
    # Analyze
    img = PILImage.open("tests/output/coord_test1.png")
    pixels = np.array(img)
    red_mask = (pixels[:, :, 0] > 200) & (pixels[:, :, 1] < 50) & (pixels[:, :, 2] < 50)
    
    if np.any(red_mask):
        red_rows = np.any(red_mask, axis=1)
        red_cols = np.any(red_mask, axis=0)
        top = np.argmax(red_rows)
        bottom = len(red_rows) - np.argmax(red_rows[::-1]) - 1
        left = np.argmax(red_cols)
        right = len(red_cols) - np.argmax(red_cols[::-1]) - 1
        
        center_x = (left + right) / 2 / 2  # Physical to logical
        center_y = (top + bottom) / 2 / 2
        
        print(f"  Rendered center: ({center_x:.1f}, {center_y:.1f}) logical")
        print(f"  Expected center: (400, 350) logical (center of 800x700 window)")
        print()
    
    # Clear scene
    scene.clear()
    frame3d = ui.Frame3D()
    frame3d.set_position(0, 0, 0)
    scene.add_frame3d(frame3d)
    
    # Test 2: Rectangle in Frame2D at (0, 0)
    print("Test 2: Rectangle in Frame2D")
    print("  Frame2D position: (0, 0)")
    print("  Frame2D size: 400x400")
    print("  Rectangle position in Frame2D: (0, 0)")
    print("  Rectangle size: 100x100")
    
    frame2d = ui.Frame2D()
    frame2d.set_position(0, 0)
    frame2d.set_size(400, 400)
    
    rect_in_frame = ui.Rectangle(100, 100)
    rect_in_frame.set_position(0, 0)  # Top-left of Frame2D
    rect_in_frame.set_color(0.0, 1.0, 0.0, 1.0)  # Green
    frame2d.add_child(rect_in_frame)
    
    frame3d.add_child(frame2d)
    
    # Render
    for i in range(5):
        renderer.poll_events()
        if renderer.should_close():
            break
        renderer.begin_frame()
        renderer.render_scene(scene)
        renderer.end_frame()
    
    # Capture
    renderer.save_capture("tests/output/coord_test2.png")
    
    # Analyze
    img = PILImage.open("tests/output/coord_test2.png")
    pixels = np.array(img)
    green_mask = (pixels[:, :, 0] < 50) & (pixels[:, :, 1] > 200) & (pixels[:, :, 2] < 50)
    
    if np.any(green_mask):
        green_rows = np.any(green_mask, axis=1)
        green_cols = np.any(green_mask, axis=0)
        top = np.argmax(green_rows)
        bottom = len(green_rows) - np.argmax(green_rows[::-1]) - 1
        left = np.argmax(green_cols)
        right = len(green_cols) - np.argmax(green_cols[::-1]) - 1
        
        center_x = (left + right) / 2 / 2  # Physical to logical
        center_y = (top + bottom) / 2 / 2
        width = (right - left + 1) / 2
        height = (bottom - top + 1) / 2
        
        print(f"  Rendered center: ({center_x:.1f}, {center_y:.1f}) logical")
        print(f"  Rendered size: {width:.1f}x{height:.1f} logical")
        print(f"  Expected: Rectangle at Frame2D's top-left corner")
        print(f"  Frame2D center is at (400, 350)")
        print(f"  Frame2D top-left is at (400-200, 350-200) = (200, 150)")
        print(f"  Rectangle center should be at (200+50, 150+50) = (250, 200)")
        print()
    
    renderer.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
