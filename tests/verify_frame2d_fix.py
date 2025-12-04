#!/usr/bin/env python3
"""Verify Frame2D coordinate fix by checking if panel_bg renders correctly"""

import sys
sys.path.insert(0, 'build')

import cyber_ui_core as ui
import os
from PIL import Image
import numpy as np

def main():
    print("=== Verify Frame2D Fix ===\n")
    
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(800, 700, "Verify Fix"):
        return
    
    scene = ui.SceneRoot()
    camera = scene.get_camera()
    camera.set_position(0.0, 0.0, 800.0)
    camera.set_perspective(1.0472, 800.0/700.0, 0.1, 2000.0)
    
    frame3d = ui.Frame3D()
    frame3d.set_position(0.0, 0.0, 0.0)
    frame3d.set_size(800, 700)
    scene.add_frame3d(frame3d)
    
    # Simple test: Frame2D at (0, 0) with a single rectangle
    clip_panel = ui.Frame2D()
    clip_panel.set_position(0.0, 0.0)  # Center of window
    clip_panel.set_size(200.0, 200.0)  # Small size
    clip_panel.set_clipping_enabled(False)
    
    # Red rectangle filling the Frame2D
    panel_bg = ui.Rectangle(200.0, 200.0)
    panel_bg.set_position(0.0, 0.0)  # Top-left of Frame2D
    panel_bg.set_color(1.0, 0.0, 0.0, 1.0)  # Red
    clip_panel.add_child(panel_bg)
    
    frame3d.add_child(clip_panel)
    
    print("Frame2D: 200x200 at position (0, 0) - window center")
    print("Rectangle: 200x200 at position (0, 0) - Frame2D top-left")
    print("\nExpected: Red square centered in window")
    print("If top-left corner of red is at center, coordinate system is WRONG")
    print("If red square is centered, coordinate system is CORRECT\n")
    
    if renderer.begin_frame():
        renderer.render_scene(scene)
        renderer.end_frame()
        
        output_dir = "tests/output"
        os.makedirs(output_dir, exist_ok=True)
        capture_file = os.path.join(output_dir, "verify_fix.png")
        if renderer.save_capture(capture_file):
            print(f"✓ Saved: {capture_file}\n")
            
            # Analyze the image
            img = Image.open(capture_file)
            pixels = np.array(img)
            
            # Find red pixels
            red_mask = (pixels[:,:,0] > 200) & (pixels[:,:,1] < 50) & (pixels[:,:,2] < 50)
            red_coords = np.where(red_mask)
            
            if len(red_coords[0]) > 0:
                red_top = red_coords[0].min()
                red_bottom = red_coords[0].max()
                red_left = red_coords[1].min()
                red_right = red_coords[1].max()
                red_center_x = (red_left + red_right) / 2
                red_center_y = (red_top + red_bottom) / 2
                
                window_center_x = img.size[0] / 2
                window_center_y = img.size[1] / 2
                
                print(f"Red rectangle:")
                print(f"  Bounds: ({red_left}, {red_top}) to ({red_right}, {red_bottom})")
                print(f"  Center: ({red_center_x:.0f}, {red_center_y:.0f})")
                print(f"  Size: {red_right - red_left + 1} x {red_bottom - red_top + 1}")
                print(f"\nWindow center: ({window_center_x}, {window_center_y})")
                
                # Check if red is centered
                dx = abs(red_center_x - window_center_x)
                dy = abs(red_center_y - window_center_y)
                
                if dx < 50 and dy < 50:
                    print("\n✅ SUCCESS: Red square is centered!")
                    print("   Frame2D coordinate system is working correctly")
                else:
                    print(f"\n❌ FAIL: Red square is off-center by ({dx:.0f}, {dy:.0f}) pixels")
                    print("   Frame2D coordinate system still has issues")
                    
                    # Check if top-left is at center
                    dx_tl = abs(red_left - window_center_x)
                    dy_tl = abs(red_top - window_center_y)
                    if dx_tl < 50 and dy_tl < 50:
                        print("   Top-left corner is at window center - Y-axis might be flipped")
            else:
                print("❌ No red pixels found - rectangle not rendering")
    
    renderer.shutdown()

if __name__ == "__main__":
    main()
