#!/usr/bin/env python3
"""
Test Frame2D with clipping DISABLED to see if rectangles render.
"""

import sys
sys.path.insert(0, '../build')

import cyber_ui_core as ui
from PIL import Image as PILImage
import os

def main():
    print("=== Frame2D WITHOUT Clipping Test ===\n")
    
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(800, 700, "No Clipping Test"):
        print("Failed to initialize renderer")
        return
    
    print("✓ Renderer initialized\n")
    
    scene = ui.SceneRoot()
    camera = scene.get_camera()
    camera.set_position(0.0, 0.0, 800.0)
    camera.set_perspective(1.0472, 800.0/700.0, 0.1, 2000.0)
    
    frame3d = ui.Frame3D()
    frame3d.set_position(0.0, 0.0, 0.0)
    scene.add_frame3d(frame3d)
    
    # Create Frame2D with clipping DISABLED
    print("Creating Frame2D with clipping DISABLED...")
    frame2d = ui.Frame2D()
    frame2d.set_position(0.0, 0.0)
    frame2d.set_size(400.0, 400.0)
    frame2d.set_clipping_enabled(False)  # DISABLED
    print(f"  Clipping: DISABLED")
    
    # Add rectangle
    rect = ui.Rectangle(200.0, 200.0)
    rect.set_position(0.0, 0.0)
    rect.set_color(1.0, 0.0, 0.0, 1.0)
    frame2d.add_child(rect)
    print(f"  Added RED rectangle at (0, 0)")
    
    frame3d.add_child(frame2d)
    
    print()
    
    # Render
    if renderer.begin_frame():
        renderer.render_scene(scene)
        renderer.end_frame()
    
    # Capture
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "frame2d_no_clipping_test.png")
    
    if renderer.save_capture(output_file):
        print(f"✓ Saved to: {output_file}\n")
        
        img = PILImage.open(output_file)
        pixels = list(img.getdata())
        
        bg_color = (26, 26, 26, 255)
        non_bg_count = sum(1 for p in pixels if abs(p[0] - bg_color[0]) > 30 or 
                          abs(p[1] - bg_color[1]) > 30 or 
                          abs(p[2] - bg_color[2]) > 30)
        
        print(f"Non-background pixels: {non_bg_count} ({non_bg_count/len(pixels)*100:.2f}%)")
        
        if non_bg_count > 0:
            print("✓ Rectangle is visible without clipping!")
            print("  This means the issue is with the scissor rect, not rendering")
        else:
            print("✗ Rectangle NOT visible even without clipping")
            print("  This means Frame2D rendering is fundamentally broken")
    
    renderer.shutdown()

if __name__ == "__main__":
    main()
