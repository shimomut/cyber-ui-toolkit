#!/usr/bin/env python3
"""
Test simple rectangle rendering without Frame2D to isolate the issue.
"""

import sys
sys.path.insert(0, '../build')

import cyber_ui_core as ui
from PIL import Image as PILImage
import os

def main():
    print("=== Simple Rectangle Test ===\n")
    
    # Initialize renderer
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(800, 700, "Simple Rect Test"):
        print("Failed to initialize renderer")
        return
    
    print("✓ Renderer initialized\n")
    
    # Create scene
    scene = ui.SceneRoot()
    camera = scene.get_camera()
    camera.set_position(0.0, 0.0, 800.0)
    camera.set_perspective(1.0472, 800.0/700.0, 0.1, 2000.0)
    
    # Create Frame3D
    frame3d = ui.Frame3D(800, 600)
    frame3d.set_position(0.0, 0.0, 0.0)
    scene.add_frame3d(frame3d)
    
    # Test 1: Rectangle directly in Frame3D (no Frame2D)
    print("Test 1: Rectangle directly in Frame3D")
    rect1 = ui.Rectangle(200.0, 200.0)
    rect1.set_position(0.0, 0.0)
    rect1.set_color(1.0, 0.0, 0.0, 1.0)
    frame3d.add_child(rect1)
    print("  Added RED rectangle at (0, 0) size 200x200")
    
    # Test 2: Rectangle offset
    rect2 = ui.Rectangle(150.0, 150.0)
    rect2.set_position(250.0, 100.0)
    rect2.set_color(0.0, 1.0, 0.0, 1.0)
    frame3d.add_child(rect2)
    print("  Added GREEN rectangle at (250, 100) size 150x150")
    
    # Test 3: Rectangle negative offset
    rect3 = ui.Rectangle(100.0, 100.0)
    rect3.set_position(-200.0, -150.0)
    rect3.set_color(0.0, 0.0, 1.0, 1.0)
    frame3d.add_child(rect3)
    print("  Added BLUE rectangle at (-200, -150) size 100x100")
    
    print()
    
    # Render
    if renderer.begin_frame():
        renderer.render_scene(scene)
        renderer.end_frame()
    
    # Capture
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "simple_rect_test.png")
    
    if renderer.save_capture(output_file):
        print(f"✓ Saved to: {output_file}\n")
        
        # Analyze
        img = PILImage.open(output_file)
        pixels = list(img.getdata())
        
        bg_color = (26, 26, 26, 255)
        non_bg_count = sum(1 for p in pixels if abs(p[0] - bg_color[0]) > 30 or 
                          abs(p[1] - bg_color[1]) > 30 or 
                          abs(p[2] - bg_color[2]) > 30)
        
        print(f"Non-background pixels: {non_bg_count} ({non_bg_count/len(pixels)*100:.2f}%)")
        
        if non_bg_count > 0:
            print("✓ Rectangles are visible!")
        else:
            print("✗ No rectangles visible")
    
    renderer.shutdown()

if __name__ == "__main__":
    main()
