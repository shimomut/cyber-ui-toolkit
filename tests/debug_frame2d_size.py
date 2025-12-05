#!/usr/bin/env python3
"""
Debug Frame2D size - check if the rendered size matches the specified size.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build'))

import cyber_ui_core as ui
from PIL import Image as PILImage
import numpy as np


def main():
    print("Frame2D Size Debug")
    print("=" * 70)
    
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(800, 700, "Frame2D Size Debug"):
        print("Failed to initialize renderer")
        return 1
    
    scene = ui.SceneRoot()
    camera = scene.get_camera()
    camera.set_position(0, 0, 800)
    camera.set_perspective(1.0472, 1600.0/1400.0, 0.1, 2000.0)
    
    # Create Frame3D
    frame3d = ui.Frame3D(800, 600)
    frame3d.set_position(0, 0, 0)
    scene.add_frame3d(frame3d)
    
    # Create Frame2D with specific size
    clip_panel = ui.Frame2D(500, 600)
    clip_panel.set_position(150, 50)  # Center at (150, 50)
    clip_panel     # Size 500x600
    clip_panel.set_clipping_enabled(True)
    
    # Fill entire Frame2D with bright red background
    bg = ui.Rectangle(500, 600)
    bg.set_position(0, 0)  # Top-left corner in Frame2D coordinates
    bg.set_color(1.0, 0.0, 0.0, 1.0)  # Bright red
    clip_panel.add_child(bg)
    
    # Add green borders at exact Frame2D boundaries
    border_width = 4
    
    # Top border
    border_top = ui.Rectangle(500, border_width)
    border_top.set_position(0, 0)
    border_top.set_color(0.0, 1.0, 0.0, 1.0)
    clip_panel.add_child(border_top)
    
    # Bottom border
    border_bottom = ui.Rectangle(500, border_width)
    border_bottom.set_position(0, 600 - border_width)
    border_bottom.set_color(0.0, 1.0, 0.0, 1.0)
    clip_panel.add_child(border_bottom)
    
    # Left border
    border_left = ui.Rectangle(border_width, 600)
    border_left.set_position(0, 0)
    border_left.set_color(0.0, 1.0, 0.0, 1.0)
    clip_panel.add_child(border_left)
    
    # Right border
    border_right = ui.Rectangle(border_width, 600)
    border_right.set_position(500 - border_width, 0)
    border_right.set_color(0.0, 1.0, 0.0, 1.0)
    clip_panel.add_child(border_right)
    
    frame3d.add_child(clip_panel)
    
    print("Setup:")
    print(f"  Window: 800x700 logical (1600x1400 physical)")
    print(f"  Frame2D position: (150, 50)")
    print(f"  Frame2D size: (500, 600)")
    print(f"  Expected screen bounds:")
    print(f"    Top-left: ({150-250}, {50-300}) = (-100, -250)")
    print(f"    Bottom-right: ({150+250}, {50+300}) = (400, 350)")
    print(f"  At 2x scale:")
    print(f"    Top-left: (-200, -500)")
    print(f"    Bottom-right: (800, 700)")
    print()
    
    # Render
    for i in range(10):
        renderer.poll_events()
        if renderer.should_close():
            break
        renderer.begin_frame()
        renderer.render_scene(scene)
        renderer.end_frame()
    
    # Capture
    os.makedirs("tests/output", exist_ok=True)
    filename = "tests/output/frame2d_size_debug.png"
    renderer.save_capture(filename)
    
    data, width, height = renderer.capture_frame()
    print(f"Captured: {width}x{height}")
    
    # Load and analyze
    img = PILImage.open(filename)
    pixels = np.array(img)
    
    # Find red pixels (background)
    red_mask = (pixels[:, :, 0] > 200) & (pixels[:, :, 1] < 50) & (pixels[:, :, 2] < 50)
    
    # Find bounding box of red pixels
    red_rows = np.any(red_mask, axis=1)
    red_cols = np.any(red_mask, axis=0)
    
    if np.any(red_rows) and np.any(red_cols):
        top = np.argmax(red_rows)
        bottom = len(red_rows) - np.argmax(red_rows[::-1]) - 1
        left = np.argmax(red_cols)
        right = len(red_cols) - np.argmax(red_cols[::-1]) - 1
        
        actual_width = right - left + 1
        actual_height = bottom - top + 1
        
        print()
        print("Actual rendered bounds (physical pixels):")
        print(f"  Top-left: ({left}, {top})")
        print(f"  Bottom-right: ({right}, {bottom})")
        print(f"  Width: {actual_width} pixels")
        print(f"  Height: {actual_height} pixels")
        print()
        
        # Convert to logical pixels
        logical_width = actual_width / 2
        logical_height = actual_height / 2
        
        print("Logical size:")
        print(f"  Width: {logical_width:.1f} (expected: 500)")
        print(f"  Height: {logical_height:.1f} (expected: 600)")
        print()
        
        # Check if size matches
        width_diff = abs(logical_width - 500)
        height_diff = abs(logical_height - 600)
        
        if width_diff < 5 and height_diff < 5:
            print("✓ Frame2D size matches specification!")
        else:
            print("✗ Frame2D size DOES NOT match!")
            print(f"  Width difference: {width_diff:.1f} pixels")
            print(f"  Height difference: {height_diff:.1f} pixels")
            
            if logical_height > 600:
                print(f"  Frame2D is {logical_height - 600:.1f} pixels TALLER than expected")
            elif logical_height < 600:
                print(f"  Frame2D is {600 - logical_height:.1f} pixels SHORTER than expected")
    else:
        print("✗ No red pixels found - Frame2D not rendering!")
    
    renderer.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
