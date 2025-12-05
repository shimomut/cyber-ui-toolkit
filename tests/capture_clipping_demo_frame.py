#!/usr/bin/env python3
"""
Capture a single frame from the clipping demo and verify it's rendering correctly.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build'))

import cyber_ui_core as ui
from PIL import Image as PILImage
import os
import numpy as np

# Import the clipping demo setup (without the render loop)
def load_image_with_pillow(filepath):
    if not os.path.exists(filepath):
        return None
    try:
        pil_img = PILImage.open(filepath)
        if pil_img.mode != 'RGBA':
            pil_img = pil_img.convert('RGBA')
        img_bytes = pil_img.tobytes()
        ui_img = ui.Image()
        width, height = pil_img.size
        if ui_img.load_from_data(img_bytes, width, height, 4):
            return ui_img
    except:
        pass
    return None

def main():
    print("="*70)
    print("CLIPPING DEMO - SINGLE FRAME CAPTURE & VERIFICATION")
    print("="*70)
    print()
    
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(800, 700, "Clipping Demo Capture"):
        print("Failed to initialize renderer")
        return False
    
    print("✓ Renderer initialized (800x700)\n")
    
    scene = ui.SceneRoot()
    camera = scene.get_camera()
    camera.set_position(0.0, 0.0, 800.0)
    camera.set_perspective(1.0472, 800.0/700.0, 0.1, 2000.0)
    
    # Load resources
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "samples", "data")
    
    gradient_img = load_image_with_pillow(os.path.join(data_dir, "gradient.png"))
    checker_img = load_image_with_pillow(os.path.join(data_dir, "checkerboard.png"))
    icon_img = load_image_with_pillow(os.path.join(data_dir, "icon.png"))
    
    font = ui.Font()
    font.load_from_file("/System/Library/Fonts/Helvetica.ttc", 20.0)
    title_font = ui.Font()
    title_font.load_from_file("/System/Library/Fonts/Helvetica.ttc", 28.0)
    title_font.set_bold(True)
    
    # Build scene exactly like clipping demo
    frame3d = ui.Frame3D(800, 600)
    scene.add_frame3d(frame3d)
    
    clip_panel = ui.Frame2D(500.0, 600.0)
    clip_panel.set_position(150.0, 50.0)
    clip_panel
    clip_panel.set_clipping_enabled(True)
    
    # Background
    bg = ui.Rectangle(500.0, 600.0)
    bg.set_position(0.0, 0.0)
    bg.set_color(0.05, 0.05, 0.08, 1.0)
    clip_panel.add_child(bg)
    
    # Borders
    for w, h, x, y in [(500, 8, 0, 0), (500, 8, 0, 592), (8, 600, 0, 0), (8, 600, 492, 0)]:
        border = ui.Rectangle(w, h)
        border.set_position(x, y)
        border.set_color(0.0, 1.0, 0.0, 1.0)
        clip_panel.add_child(border)
    
    # Title
    title = ui.Text("Frame2D Clipping Demo")
    title.set_position(250.0, 30.0)
    title.set_color(1.0, 1.0, 0.0, 1.0)
    title.set_font(title_font)
    title.set_alignment(ui.TextAlignment.Center)
    clip_panel.add_child(title)
    
    # Rectangles
    rect1 = ui.Rectangle(250.0, 250.0)
    rect1.set_position(125.0, 150.0)
    rect1.set_color(1.0, 0.0, 0.0, 1.0)
    if gradient_img:
        rect1.set_image(gradient_img)
    clip_panel.add_child(rect1)
    
    rect2 = ui.Rectangle(250.0, 250.0)
    rect2.set_position(125.0, 350.0)
    rect2.set_color(0.0, 0.5, 1.0, 1.0)
    if checker_img:
        rect2.set_image(checker_img)
    clip_panel.add_child(rect2)
    
    rect3 = ui.Rectangle(200.0, 150.0)
    rect3.set_position(150.0, 250.0)
    rect3.set_color(1.0, 1.0, 0.0, 1.0)
    if icon_img:
        rect3.set_image(icon_img)
    clip_panel.add_child(rect3)
    
    frame3d.add_child(clip_panel)
    
    print("✓ Scene created with:")
    print("  - Frame2D at (150, 50) size (500x600)")
    print("  - Bright green borders (8px thick)")
    print("  - 3 large colored rectangles (red, blue, yellow)")
    print("  - Yellow title text")
    print()
    
    # Render
    if renderer.begin_frame():
        renderer.render_scene(scene)
        renderer.end_frame()
    
    # Capture
    output_dir = os.path.join(script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "clipping_demo_snapshot.png")
    
    if renderer.save_capture(output_file):
        print(f"✓ Saved snapshot to: {output_file}\n")
        
        # Analyze
        img = PILImage.open(output_file)
        pixels = np.array(img)
        
        print("="*70)
        print("IMAGE ANALYSIS")
        print("="*70)
        print(f"Size: {img.size}")
        print(f"Unique colors: {len(np.unique(pixels.reshape(-1, 4), axis=0))}")
        
        bg_color = np.array([26, 26, 26])
        diff = np.abs(pixels[:, :, :3].astype(int) - bg_color)
        non_bg_mask = np.any(diff > 30, axis=2)
        non_bg_count = np.sum(non_bg_mask)
        total = pixels.shape[0] * pixels.shape[1]
        
        print(f"Non-background pixels: {non_bg_count:,} ({non_bg_count/total*100:.2f}%)")
        print()
        
        if non_bg_count > 50000:
            print("✓ SUCCESS: Clipping demo is rendering with good visibility!")
            print(f"  {non_bg_count:,} pixels of colored content visible")
            success = True
        elif non_bg_count > 10000:
            print("⚠ PARTIAL: Content is rendering but visibility is low")
            print(f"  Only {non_bg_count:,} pixels visible")
            print("  Consider using brighter colors or larger shapes")
            success = True
        else:
            print("✗ FAIL: Very little content visible")
            print(f"  Only {non_bg_count:,} pixels visible")
            success = False
        
        print("="*70)
    
    renderer.shutdown()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
