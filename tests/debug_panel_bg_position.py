#!/usr/bin/env python3
"""Debug script to check panel_bg rendering position"""

import sys
sys.path.insert(0, 'build')

import cyber_ui_core as ui
import os

def main():
    print("=== Debug Panel Background Position ===\n")
    
    # Initialize renderer
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(800, 700, "Debug Panel BG"):
        print("Failed to initialize renderer")
        return
    
    # Create scene
    scene = ui.SceneRoot()
    camera = scene.get_camera()
    camera.set_position(0.0, 0.0, 800.0)
    camera.set_perspective(1.0472, 800.0/700.0, 0.1, 2000.0)
    
    # Create Frame3D
    frame3d = ui.Frame3D(800, 600)
    frame3d.set_name("MainFrame3D")
    frame3d.set_position(0.0, 0.0, 0.0)
    frame3d.set_size(800, 700)
    scene.add_frame3d(frame3d)
    
    # Create Frame2D at specific position
    clip_panel = ui.Frame2D(500.0, 600.0)
    clip_panel.set_name("ClippingPanel")
    clip_panel.set_position(150.0, 50.0)  # This uses center-origin in Frame3D space
    clip_panel
    clip_panel.set_clipping_enabled(True)
    
    # Background at (0, 0) - should be at Frame2D's top-left
    panel_bg = ui.Rectangle(500.0, 600.0)
    panel_bg.set_name("PanelBackground")
    panel_bg.set_position(0.0, 0.0)
    panel_bg.set_color(1.0, 0.0, 0.0, 1.0)  # Bright red for visibility
    clip_panel.add_child(panel_bg)
    
    # Add a small marker at Frame2D's expected center
    center_marker = ui.Rectangle(20.0, 20.0)
    center_marker.set_name("CenterMarker")
    center_marker.set_position(250.0, 300.0)  # Center of 500x600 Frame2D
    center_marker.set_color(0.0, 1.0, 0.0, 1.0)  # Green
    clip_panel.add_child(center_marker)
    
    frame3d.add_child(clip_panel)
    
    print("Frame2D position in Frame3D: (150, 50)")
    print("Frame2D size: 500x600")
    print("Expected Frame2D center in Frame3D: (150, 50)")
    print("Expected Frame2D top-left in Frame3D: (150-250, 50-300) = (-100, -250)")
    print("Expected Frame2D bottom-right in Frame3D: (150+250, 50+300) = (400, 350)")
    print()
    print("panel_bg: position (0, 0) in Frame2D, size 500x600")
    print("  Should fill entire Frame2D from top-left")
    print()
    print("center_marker: position (250, 300) in Frame2D, size 20x20")
    print("  Should be at Frame2D's center")
    print()
    
    # Render one frame
    if renderer.begin_frame():
        renderer.render_scene(scene)
        renderer.end_frame()
        
        # Save capture
        output_dir = "tests/output"
        os.makedirs(output_dir, exist_ok=True)
        capture_file = os.path.join(output_dir, "debug_panel_bg.png")
        if renderer.save_capture(capture_file):
            print(f"✓ Saved: {capture_file}")
            print("\nCheck the image:")
            print("- Red rectangle should fill the Frame2D area")
            print("- Green marker should be at the center of the red area")
            print("- If you see red at window center, Frame2D positioning is wrong")
    
    renderer.shutdown()

if __name__ == "__main__":
    main()
