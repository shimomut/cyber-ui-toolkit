#!/usr/bin/env python3
"""
Test Frame2D exactly like hierarchy demo does.
"""

import sys
sys.path.insert(0, '../build')

import cyber_ui_core as ui
from PIL import Image as PILImage
import os

def main():
    print("=== Hierarchy-style Frame2D Test ===\n")
    
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(1024, 768, "Hierarchy Test"):
        print("Failed to initialize renderer")
        return
    
    print("✓ Renderer initialized\n")
    
    scene = ui.SceneRoot()
    camera = scene.get_camera()
    camera.set_position(0.0, 0.0, 800.0)
    camera.set_perspective(1.0472, 1024.0/768.0, 0.1, 2000.0)
    
    frame3d = ui.Frame3D(800, 600)
    frame3d.set_position(0.0, 0.0, 0.0)
    scene.add_frame3d(frame3d)
    
    # Create Frame2D exactly like hierarchy demo
    print("Creating Frame2D like hierarchy demo...")
    left_panel = ui.Frame2D(250.0, 650.0)
    left_panel.set_name("LeftPanel")
    left_panel.set_position(50.0, 50.0)
    left_panel
    left_panel.set_clipping_enabled(True)
    print(f"  Position: (50, 50)")
    print(f"  Size: (250, 650)")
    
    # Background
    left_bg = ui.Rectangle(250.0, 650.0)
    left_bg.set_name("LeftBackground")
    left_bg.set_position(0.0, 0.0)
    left_bg.set_color(0.15, 0.15, 0.2, 1.0)
    left_panel.add_child(left_bg)
    print(f"  Added background at (0, 0)")
    
    # Content rectangle
    content_rect = ui.Rectangle(210.0, 80.0)
    content_rect.set_name("ContentRect1")
    content_rect.set_position(20.0, 80.0)
    content_rect.set_color(0.2, 0.4, 0.6, 1.0)
    left_panel.add_child(content_rect)
    print(f"  Added content rect at (20, 80)")
    
    frame3d.add_child(left_panel)
    
    print()
    
    # Render
    if renderer.begin_frame():
        renderer.render_scene(scene)
        renderer.end_frame()
    
    # Capture
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "hierarchy_style_test.png")
    
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
            print("✓ Frame2D content is visible!")
        else:
            print("✗ Frame2D content NOT visible")
    
    renderer.shutdown()

if __name__ == "__main__":
    main()
