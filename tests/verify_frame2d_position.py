#!/usr/bin/env python3
"""
Verify Frame2D Position Fix

This test verifies that Frame2D uses top-left origin positioning correctly.

Expected behavior:
- Window: 800x700 (center at 400, 350)
- Frame2D: 500x600 at position (150, 50)
- Frame2D top-left: (150, 50)
- Frame2D center: (400, 350) - should align with window center
- Frame2D bottom-right: (650, 650)

Visual verification:
- Green border should be centered in the window
- Red rectangle at (0, 0) should be at Frame2D's top-left corner
- Blue rectangle at (250, 300) should be at Frame2D's center
"""

import sys
sys.path.insert(0, '../../build')

import cyber_ui_core as ui
import os

def main():
    print("=== Frame2D Position Verification ===\n")
    
    # Initialize renderer
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(800, 700, "Frame2D Position Test"):
        print("Failed to initialize renderer")
        return
    
    print("Window: 800x700")
    print("Window center: (400, 350)\n")
    
    # Create scene
    scene = ui.SceneRoot()
    camera = scene.get_camera()
    camera.set_position(0.0, 0.0, 800.0)
    camera.set_perspective(1.0472, 800.0/700.0, 0.1, 2000.0)
    
    # Create Frame3D
    frame3d = ui.Frame3D()
    frame3d.set_position(0.0, 0.0, 0.0)
    frame3d.set_size(800, 700)
    scene.add_frame3d(frame3d)
    
    # Create Frame2D with specific positioning
    frame2d = ui.Frame2D()
    frame2d.set_position(150.0, 50.0)  # Top-left at (150, 50)
    frame2d.set_size(500.0, 600.0)
    frame2d.set_clipping_enabled(True)
    
    print("Frame2D:")
    print("  Position: (150, 50) - top-left corner")
    print("  Size: 500x600")
    print("  Expected center: (150 + 250, 50 + 300) = (400, 350)")
    print("  Expected bottom-right: (150 + 500, 50 + 600) = (650, 650)\n")
    
    # Dark background
    bg = ui.Rectangle(500.0, 600.0)
    bg.set_position(0.0, 0.0)
    bg.set_color(0.1, 0.1, 0.15, 1.0)
    frame2d.add_child(bg)
    
    # Green border to show Frame2D bounds
    border_width = 4.0
    
    border_top = ui.Rectangle(500.0, border_width)
    border_top.set_position(0.0, 0.0)
    border_top.set_color(0.0, 1.0, 0.0, 1.0)
    frame2d.add_child(border_top)
    
    border_bottom = ui.Rectangle(500.0, border_width)
    border_bottom.set_position(0.0, 600.0 - border_width)
    border_bottom.set_color(0.0, 1.0, 0.0, 1.0)
    frame2d.add_child(border_bottom)
    
    border_left = ui.Rectangle(border_width, 600.0)
    border_left.set_position(0.0, 0.0)
    border_left.set_color(0.0, 1.0, 0.0, 1.0)
    frame2d.add_child(border_left)
    
    border_right = ui.Rectangle(border_width, 600.0)
    border_right.set_position(500.0 - border_width, 0.0)
    border_right.set_color(0.0, 1.0, 0.0, 1.0)
    frame2d.add_child(border_right)
    
    # Red marker at Frame2D's top-left (0, 0)
    marker_tl = ui.Rectangle(20.0, 20.0)
    marker_tl.set_position(0.0, 0.0)
    marker_tl.set_color(1.0, 0.0, 0.0, 1.0)
    frame2d.add_child(marker_tl)
    
    # Blue marker at Frame2D's center (250, 300)
    marker_center = ui.Rectangle(20.0, 20.0)
    marker_center.set_position(240.0, 290.0)  # Centered around (250, 300)
    marker_center.set_color(0.0, 0.5, 1.0, 1.0)
    frame2d.add_child(marker_center)
    
    # Yellow marker at Frame2D's bottom-right (500, 600)
    marker_br = ui.Rectangle(20.0, 20.0)
    marker_br.set_position(480.0, 580.0)
    marker_br.set_color(1.0, 1.0, 0.0, 1.0)
    frame2d.add_child(marker_br)
    
    frame3d.add_child(frame2d)
    
    print("Visual markers:")
    print("  Red square (20x20) at (0, 0) - Frame2D top-left")
    print("  Blue square (20x20) at (240, 290) - Frame2D center area")
    print("  Yellow square (20x20) at (480, 580) - Frame2D bottom-right area")
    print("\nExpected result:")
    print("  ✓ Green border should be centered in window")
    print("  ✓ Red marker should be at top-left of green border")
    print("  ✓ Blue marker should be at center of green border (and window)")
    print("  ✓ Yellow marker should be at bottom-right of green border")
    print("\nPress ESC or close window to exit\n")
    
    # Render loop
    frame_count = 0
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    while not renderer.should_close():
        renderer.poll_events()
        
        if renderer.begin_frame():
            renderer.render_scene(scene)
            renderer.end_frame()
            frame_count += 1
            
            # Capture first frame
            if frame_count == 5:
                output_file = os.path.join(output_dir, "frame2d_position_test.png")
                if renderer.save_capture(output_file):
                    print(f"✓ Captured: {output_file}")
                    print("  Check if green border is centered in the image!")
    
    renderer.shutdown()
    print("\nTest complete")

if __name__ == "__main__":
    main()
