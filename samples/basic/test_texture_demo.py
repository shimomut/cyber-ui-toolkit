#!/usr/bin/env python3
"""
Demo script showing texture loading and application to rectangles
This is a non-interactive demo that just prints the rendering info
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
        print(f"Warning: Image file not found: {filepath}")
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
    print("=== Texture Demo ===\n")
    
    # Get paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "data")
    
    # Load images
    print("Loading test images...")
    gradient_img = load_image_with_pillow(os.path.join(data_dir, "gradient.png"))
    checkerboard_img = load_image_with_pillow(os.path.join(data_dir, "checkerboard.png"))
    icon_img = load_image_with_pillow(os.path.join(data_dir, "icon.png"))
    print()
    
    # Create textured rectangles
    print("Creating textured rectangles:\n")
    
    rectangles = []
    
    # Gradient texture
    if gradient_img:
        rect1 = ui.Rectangle(256, 256)
        rect1.set_name("GradientRectangle")
        rect1.set_position(50, 50, 0)
        rect1.set_color(1.0, 1.0, 1.0, 1.0)
        rect1.set_image(gradient_img)
        rectangles.append(rect1)
        print(f"✓ {rect1.get_name()}: {gradient_img.get_width()}x{gradient_img.get_height()} texture")
    
    # Checkerboard texture
    if checkerboard_img:
        rect2 = ui.Rectangle(128, 128)
        rect2.set_name("CheckerboardRectangle")
        rect2.set_position(350, 100, 0)
        rect2.set_color(1.0, 1.0, 1.0, 1.0)
        rect2.set_image(checkerboard_img)
        rectangles.append(rect2)
        print(f"✓ {rect2.get_name()}: {checkerboard_img.get_width()}x{checkerboard_img.get_height()} texture")
    
    # Icon texture
    if icon_img:
        rect3 = ui.Rectangle(64, 64)
        rect3.set_name("IconRectangle")
        rect3.set_position(520, 150, 0)
        rect3.set_color(1.0, 1.0, 1.0, 1.0)
        rect3.set_image(icon_img)
        rectangles.append(rect3)
        print(f"✓ {rect3.get_name()}: {icon_img.get_width()}x{icon_img.get_height()} texture")
    
    # Solid color (no texture)
    rect4 = ui.Rectangle(150, 100)
    rect4.set_name("SolidColorRectangle")
    rect4.set_position(350, 300, 0)
    rect4.set_color(0.2, 0.6, 1.0, 1.0)
    rectangles.append(rect4)
    print(f"✓ {rect4.get_name()}: solid color (no texture)")
    
    # Tinted texture
    if checkerboard_img:
        rect5 = ui.Rectangle(128, 128)
        rect5.set_name("TintedCheckerboard")
        rect5.set_position(100, 350, 0)
        rect5.set_color(1.0, 0.5, 0.5, 1.0)  # Red tint
        rect5.set_image(checkerboard_img)
        rectangles.append(rect5)
        print(f"✓ {rect5.get_name()}: {checkerboard_img.get_width()}x{checkerboard_img.get_height()} texture (tinted)")
    
    # Render all rectangles (console output)
    print("\n" + "="*60)
    print("Rendering rectangles (console output):")
    print("="*60 + "\n")
    
    for rect in rectangles:
        rect.render()
    
    print("\n✓ Demo complete!")
    print(f"  Total rectangles: {len(rectangles)}")
    print(f"  Textured: {sum(1 for r in rectangles if r.has_image())}")
    print(f"  Solid color: {sum(1 for r in rectangles if not r.has_image())}")

if __name__ == "__main__":
    main()
