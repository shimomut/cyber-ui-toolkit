#!/usr/bin/env python3
"""Debug script with corner markers to identify coordinate system issue"""

import sys
sys.path.insert(0, 'build')

import cyber_ui_core as ui
import os

def main():
    print("=== Debug Corner Markers ===\n")
    
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(800, 700, "Debug Corners"):
        return
    
    scene = ui.SceneRoot()
    camera = scene.get_camera()
    camera.set_position(0.0, 0.0, 800.0)
    camera.set_perspective(1.0472, 800.0/700.0, 0.1, 2000.0)
    
    frame3d = ui.Frame3D(800, 600)
    frame3d.set_position(0.0, 0.0, 0.0)
    frame3d.set_size(800, 700)
    scene.add_frame3d(frame3d)
    
    # Frame2D at center of window
    clip_panel = ui.Frame2D(500.0, 600.0)
    clip_panel.set_position(150.0, 50.0)
    clip_panel
    clip_panel.set_clipping_enabled(False)  # Disable clipping to see everything
    
    # Background - should fill entire Frame2D
    panel_bg = ui.Rectangle(500.0, 600.0)
    panel_bg.set_position(0.0, 0.0)
    panel_bg.set_color(0.2, 0.2, 0.2, 1.0)  # Dark gray
    clip_panel.add_child(panel_bg)
    
    # Corner markers - small colored squares at each corner
    marker_size = 40.0
    
    # TOP-LEFT corner (0, 0) - RED
    tl_marker = ui.Rectangle(marker_size, marker_size)
    tl_marker.set_position(0.0, 0.0)
    tl_marker.set_color(1.0, 0.0, 0.0, 1.0)  # Red
    clip_panel.add_child(tl_marker)
    
    # TOP-RIGHT corner (500-40, 0) - GREEN
    tr_marker = ui.Rectangle(marker_size, marker_size)
    tr_marker.set_position(500.0 - marker_size, 0.0)
    tr_marker.set_color(0.0, 1.0, 0.0, 1.0)  # Green
    clip_panel.add_child(tr_marker)
    
    # BOTTOM-LEFT corner (0, 600-40) - BLUE
    bl_marker = ui.Rectangle(marker_size, marker_size)
    bl_marker.set_position(0.0, 600.0 - marker_size)
    bl_marker.set_color(0.0, 0.0, 1.0, 1.0)  # Blue
    clip_panel.add_child(bl_marker)
    
    # BOTTOM-RIGHT corner (500-40, 600-40) - YELLOW
    br_marker = ui.Rectangle(marker_size, marker_size)
    br_marker.set_position(500.0 - marker_size, 600.0 - marker_size)
    br_marker.set_color(1.0, 1.0, 0.0, 1.0)  # Yellow
    clip_panel.add_child(br_marker)
    
    # CENTER marker (250-20, 300-20) - MAGENTA
    center_marker = ui.Rectangle(marker_size, marker_size)
    center_marker.set_position(250.0 - marker_size/2, 300.0 - marker_size/2)
    center_marker.set_color(1.0, 0.0, 1.0, 1.0)  # Magenta
    clip_panel.add_child(center_marker)
    
    frame3d.add_child(clip_panel)
    
    print("Frame2D: 500x600 at position (150, 50)")
    print("\nCorner markers (40x40 each):")
    print("  RED    = Top-left (0, 0)")
    print("  GREEN  = Top-right (460, 0)")
    print("  BLUE   = Bottom-left (0, 560)")
    print("  YELLOW = Bottom-right (460, 560)")
    print("  MAGENTA = Center (230, 280)")
    print()
    
    if renderer.begin_frame():
        renderer.render_scene(scene)
        renderer.end_frame()
        
        output_dir = "tests/output"
        os.makedirs(output_dir, exist_ok=True)
        capture_file = os.path.join(output_dir, "debug_corners.png")
        if renderer.save_capture(capture_file):
            print(f"✓ Saved: {capture_file}")
            print("\nExpected layout:")
            print("  RED (top-left) should be in upper-left of gray area")
            print("  GREEN (top-right) should be in upper-right of gray area")
            print("  BLUE (bottom-left) should be in lower-left of gray area")
            print("  YELLOW (bottom-right) should be in lower-right of gray area")
            print("  MAGENTA should be at center of gray area")
            print("\nIf colors are in wrong positions, coordinate system is broken!")
    
    renderer.shutdown()

if __name__ == "__main__":
    main()
