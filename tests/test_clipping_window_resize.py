#!/usr/bin/env python3
"""
Test to verify clipping boundaries remain correct when window size changes.

This test checks that:
1. Borders are always visible at Frame2D boundaries
2. Clipping position doesn't change with window size
3. Scissor rect uses drawable size, not window size
"""

import sys
sys.path.insert(0, '../build')

import cyber_ui_core as ui
import os

def main():
    print("=== Clipping Window Resize Test ===\n")
    
    # Initialize renderer with initial size
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(800, 600, "Clipping Resize Test"):
        print("Failed to initialize renderer")
        return
    
    print("✓ Renderer initialized (800x600)")
    
    # Create scene
    scene = ui.SceneRoot()
    camera = scene.get_camera()
    camera.set_position(0.0, 0.0, 800.0)
    camera.set_perspective(1.0472, 800.0/600.0, 0.1, 2000.0)
    
    # Create Frame3D
    frame3d = ui.Frame3D(800, 600)
    frame3d.set_position(0.0, 0.0, 0.0)
    frame3d.set_size(800, 600)
    scene.add_frame3d(frame3d)
    
    # Create Frame2D with clipping
    clip_panel = ui.Frame2D(600.0, 500.0)
    clip_panel.set_position(100.0, 50.0)
    clip_panel
    clip_panel.set_clipping_enabled(True)
    
    # Background
    bg = ui.Rectangle(600.0, 500.0)
    bg.set_position(0.0, 0.0)
    bg.set_color(0.1, 0.1, 0.15, 1.0)
    clip_panel.add_child(bg)
    
    # Borders - these should ALWAYS be visible
    border_width = 10.0
    
    # Top border (yellow)
    border_top = ui.Rectangle(600.0, border_width)
    border_top.set_position(0.0, 0.0)
    border_top.set_color(1.0, 1.0, 0.0, 1.0)
    clip_panel.add_child(border_top)
    
    # Bottom border (green)
    border_bottom = ui.Rectangle(600.0, border_width)
    border_bottom.set_position(0.0, 500.0 - border_width)
    border_bottom.set_color(0.0, 1.0, 0.0, 1.0)
    clip_panel.add_child(border_bottom)
    
    # Left border (cyan)
    border_left = ui.Rectangle(border_width, 500.0)
    border_left.set_position(0.0, 0.0)
    border_left.set_color(0.0, 1.0, 1.0, 1.0)
    clip_panel.add_child(border_left)
    
    # Right border (magenta)
    border_right = ui.Rectangle(border_width, 500.0)
    border_right.set_position(600.0 - border_width, 0.0)
    border_right.set_color(1.0, 0.0, 1.0, 1.0)
    clip_panel.add_child(border_right)
    
    # Test rectangle that extends beyond boundaries
    test_rect = ui.Rectangle(400.0, 300.0)
    test_rect.set_position(100.0, 100.0)
    test_rect.set_color(1.0, 0.0, 0.0, 1.0)
    clip_panel.add_child(test_rect)
    
    frame3d.add_child(clip_panel)
    
    print("\nScene created:")
    print("- Frame2D at (100, 50) with size 600x500")
    print("- 4 colored borders marking clipping boundary")
    print("- Red rectangle inside that should be clipped")
    print("\nExpected behavior:")
    print("- ALL 4 borders should be visible")
    print("- Borders should stay at Frame2D edges regardless of window size")
    print("- Red rectangle should be clipped at border edges")
    print("\nResize the window and verify borders remain visible!")
    print("Press ESC to exit\n")
    
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
            
            # Capture initial frame
            if frame_count == 5:
                filename = os.path.join(output_dir, "clipping_resize_test.png")
                if renderer.save_capture(filename):
                    print(f"✓ Captured frame: {filename}")
    
    print(f"\nRendered {frame_count} frames")
    renderer.shutdown()

if __name__ == "__main__":
    main()
