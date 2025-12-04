#!/usr/bin/env python3
"""
Simplified test to verify clipping borders are visible.
No animations, just static borders and content.
"""

import sys
sys.path.insert(0, '../build')

import cyber_ui_core as ui
import os

def main():
    print("=== Simple Clipping Border Test ===\n")
    
    # Initialize renderer
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(800, 600, "Simple Clipping Test"):
        print("Failed to initialize renderer")
        return
    
    print("✓ Renderer initialized (800x600)")
    
    # Create scene
    scene = ui.SceneRoot()
    camera = scene.get_camera()
    camera.set_position(0.0, 0.0, 800.0)
    camera.set_perspective(1.0472, 800.0/600.0, 0.1, 2000.0)
    
    # Create Frame3D - NO POSITION, NO ROTATION
    frame3d = ui.Frame3D()
    frame3d.set_position(0.0, 0.0, 0.0)
    frame3d.set_size(800, 600)
    scene.add_frame3d(frame3d)
    
    # Create Frame2D - CENTERED, NO OFFSET
    clip_panel = ui.Frame2D()
    clip_panel.set_position(0.0, 0.0)  # At origin
    clip_panel.set_size(400.0, 400.0)  # Smaller, centered
    clip_panel.set_clipping_enabled(True)
    
    # Background - should fill entire Frame2D
    bg = ui.Rectangle(400.0, 400.0)
    bg.set_position(0.0, 0.0)
    bg.set_color(0.2, 0.2, 0.3, 1.0)
    clip_panel.add_child(bg)
    
    # Borders - THICK and BRIGHT
    border_w = 20.0
    
    # Top border (RED)
    top = ui.Rectangle(400.0, border_w)
    top.set_position(0.0, 0.0)
    top.set_color(1.0, 0.0, 0.0, 1.0)
    clip_panel.add_child(top)
    
    # Bottom border (GREEN)
    bottom = ui.Rectangle(400.0, border_w)
    bottom.set_position(0.0, 400.0 - border_w)
    bottom.set_color(0.0, 1.0, 0.0, 1.0)
    clip_panel.add_child(bottom)
    
    # Left border (BLUE)
    left = ui.Rectangle(border_w, 400.0)
    left.set_position(0.0, 0.0)
    left.set_color(0.0, 0.0, 1.0, 1.0)
    clip_panel.add_child(left)
    
    # Right border (YELLOW)
    right = ui.Rectangle(border_w, 400.0)
    right.set_position(400.0 - border_w, 0.0)
    right.set_color(1.0, 1.0, 0.0, 1.0)
    clip_panel.add_child(right)
    
    # Large rectangle that extends beyond borders
    test_rect = ui.Rectangle(500.0, 500.0)
    test_rect.set_position(-50.0, -50.0)  # Extends beyond all edges
    test_rect.set_color(1.0, 0.5, 0.0, 0.5)  # Semi-transparent orange
    clip_panel.add_child(test_rect)
    
    frame3d.add_child(clip_panel)
    
    print("\nScene created:")
    print("- Frame3D at (0, 0, 0) with size 800x600")
    print("- Frame2D at (0, 0) with size 400x400")
    print("- 4 thick colored borders (20px each)")
    print("- Orange rectangle extending beyond all edges")
    print("\nExpected:")
    print("- ALL 4 borders should be visible")
    print("- Orange rectangle should be clipped at border edges")
    print("- Borders mark the exact clipping boundary")
    print("\nPress ESC to exit\n")
    
    # Render a few frames and capture
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    frame_count = 0
    while not renderer.should_close() and frame_count < 10:
        renderer.poll_events()
        
        if renderer.begin_frame():
            renderer.render_scene(scene)
            renderer.end_frame()
            frame_count += 1
            
            if frame_count == 5:
                filename = os.path.join(output_dir, "simple_clipping_test.png")
                if renderer.save_capture(filename):
                    print(f"✓ Captured: {filename}")
                    break
    
    renderer.shutdown()

if __name__ == "__main__":
    main()
