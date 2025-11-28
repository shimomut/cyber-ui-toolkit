#!/usr/bin/env python3
"""
Visual verification script for texture rendering
Opens a window showing all test textures
"""

import sys
sys.path.insert(0, '../../build')

import cyber_ui_core as ui
from PIL import Image as PILImage
import numpy as np
import os

def load_image_with_pillow(filepath):
    """Load an image using Pillow and return a cyber_ui Image object"""
    if not os.path.exists(filepath):
        print(f"Error: Image file not found: {filepath}")
        return None
    
    try:
        pil_img = PILImage.open(filepath)
        if pil_img.mode != 'RGBA':
            pil_img = pil_img.convert('RGBA')
        
        img_array = np.array(pil_img, dtype=np.uint8)
        ui_img = ui.Image()
        width, height = pil_img.size
        
        if ui_img.load_from_data(img_array, width, height, 4):
            return ui_img
        return None
            
    except Exception as e:
        print(f"Error loading image {filepath}: {e}")
        return None

def main():
    print("=== Texture Rendering Verification ===\n")
    
    # Create renderer
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(800, 600, "Texture Verification"):
        print("Failed to initialize renderer")
        return 1
    
    print("✓ Renderer initialized")
    print("Press ESC or close window to exit\n")
    
    # Get paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "data")
    
    # Load images
    print("Loading textures...")
    gradient_img = load_image_with_pillow(os.path.join(data_dir, "gradient.png"))
    checkerboard_img = load_image_with_pillow(os.path.join(data_dir, "checkerboard.png"))
    icon_img = load_image_with_pillow(os.path.join(data_dir, "icon.png"))
    print()
    
    # Create rectangles with textures
    rectangles = []
    
    # Row 1: Original textures
    if gradient_img:
        rect1 = ui.Rectangle(256, 256)
        rect1.set_name("Gradient")
        rect1.set_position(20, 20, 0)
        rect1.set_color(1.0, 1.0, 1.0, 1.0)
        rect1.set_image(gradient_img)
        rectangles.append(rect1)
        print("✓ Gradient texture (256x256) at (20, 20)")
    
    if checkerboard_img:
        rect2 = ui.Rectangle(128, 128)
        rect2.set_name("Checkerboard")
        rect2.set_position(300, 20, 0)
        rect2.set_color(1.0, 1.0, 1.0, 1.0)
        rect2.set_image(checkerboard_img)
        rectangles.append(rect2)
        print("✓ Checkerboard texture (128x128) at (300, 20)")
    
    if icon_img:
        rect3 = ui.Rectangle(64, 64)
        rect3.set_name("Icon")
        rect3.set_position(450, 20, 0)
        rect3.set_color(1.0, 1.0, 1.0, 1.0)
        rect3.set_image(icon_img)
        rectangles.append(rect3)
        print("✓ Icon texture (64x64) at (450, 20)")
    
    # Row 2: Tinted textures
    if checkerboard_img:
        rect4 = ui.Rectangle(128, 128)
        rect4.set_name("Red Tint")
        rect4.set_position(20, 300, 0)
        rect4.set_color(1.0, 0.3, 0.3, 1.0)
        rect4.set_image(checkerboard_img)
        rectangles.append(rect4)
        print("✓ Red tinted checkerboard at (20, 300)")
    
    if checkerboard_img:
        rect5 = ui.Rectangle(128, 128)
        rect5.set_name("Green Tint")
        rect5.set_position(170, 300, 0)
        rect5.set_color(0.3, 1.0, 0.3, 1.0)
        rect5.set_image(checkerboard_img)
        rectangles.append(rect5)
        print("✓ Green tinted checkerboard at (170, 300)")
    
    if checkerboard_img:
        rect6 = ui.Rectangle(128, 128)
        rect6.set_name("Blue Tint")
        rect6.set_position(320, 300, 0)
        rect6.set_color(0.3, 0.3, 1.0, 1.0)
        rect6.set_image(checkerboard_img)
        rectangles.append(rect6)
        print("✓ Blue tinted checkerboard at (320, 300)")
    
    # Solid color rectangle for comparison
    rect7 = ui.Rectangle(100, 80)
    rect7.set_name("Solid Color")
    rect7.set_position(470, 320, 0)
    rect7.set_color(1.0, 0.5, 0.0, 1.0)
    rectangles.append(rect7)
    print("✓ Solid color rectangle at (470, 320)")
    
    print(f"\nRendering {len(rectangles)} rectangles...")
    print("\nWhat you should see:")
    print("  Top row: Gradient, Checkerboard, Icon (original colors)")
    print("  Bottom row: Red, Green, Blue tinted checkerboards + Orange solid")
    print()
    
    # Render loop
    frame_count = 0
    while not renderer.should_close():
        renderer.poll_events()
        
        if renderer.begin_frame():
            for rect in rectangles:
                renderer.render_object(rect)
            renderer.end_frame()
            frame_count += 1
    
    print(f"\n✓ Rendered {frame_count} frames")
    renderer.shutdown()
    print("✓ Renderer shutdown complete")
    return 0

if __name__ == "__main__":
    sys.exit(main())
