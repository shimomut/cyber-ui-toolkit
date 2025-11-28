#!/usr/bin/env python3
"""
Basic example demonstrating Rectangle rendering with Metal backend
"""

import sys
sys.path.insert(0, '../../build')

import cyber_ui_core as ui
from PIL import Image as PILImage
import os

def load_image_with_pillow(filepath):
    """Load an image using Pillow and return a cyber_ui Image object"""
    if not os.path.exists(filepath):
        print(f"Warning: Image file not found: {filepath}")
        return None
    
    try:
        # Load image with Pillow
        pil_img = PILImage.open(filepath)
        
        # Convert to RGBA if needed
        if pil_img.mode != 'RGBA':
            pil_img = pil_img.convert('RGBA')
        
        # Get image data as bytes
        img_bytes = pil_img.tobytes()
        
        # Create cyber_ui Image object
        ui_img = ui.Image()
        width, height = pil_img.size
        channels = 4  # RGBA
        
        # Load data into Image object
        if ui_img.load_from_data(img_bytes, width, height, channels):
            print(f"Loaded image: {filepath} ({width}x{height}, {channels} channels)")
            return ui_img
        else:
            print(f"Failed to load image data: {filepath}")
            return None
            
    except Exception as e:
        print(f"Error loading image {filepath}: {e}")
        return None

def main():
    print("=== Cyber UI Toolkit - Rectangle Test ===\n")
    
    # Create Metal renderer
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(800, 600, "Cyber UI - Rectangle Demo"):
        print("Failed to initialize renderer")
        return
    
    print("Renderer initialized successfully!")
    print("Press ESC or close window to exit\n")
    
    # Load test images
    print("Loading test images...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "data")
    
    gradient_img = load_image_with_pillow(os.path.join(data_dir, "gradient.png"))
    checkerboard_img = load_image_with_pillow(os.path.join(data_dir, "checkerboard.png"))
    icon_img = load_image_with_pillow(os.path.join(data_dir, "icon.png"))
    print()
    
    # Create textured rectangles
    print("Creating rectangles with textures...\n")
    
    # Rectangle 1: Gradient texture
    rect1 = ui.Rectangle(256, 256)
    rect1.set_name("GradientRectangle")
    rect1.set_position(50, 50, 0)
    rect1.set_color(1.0, 1.0, 1.0, 1.0)  # White (to show texture as-is)
    if gradient_img:
        rect1.set_image(gradient_img)
        print("✓ Applied gradient texture to rect1")
    
    # Rectangle 2: Checkerboard texture
    rect2 = ui.Rectangle(128, 128)
    rect2.set_name("CheckerboardRectangle")
    rect2.set_position(350, 100, 0)
    rect2.set_color(1.0, 1.0, 1.0, 1.0)  # White
    if checkerboard_img:
        rect2.set_image(checkerboard_img)
        print("✓ Applied checkerboard texture to rect2")
    
    # Rectangle 3: Icon texture
    rect3 = ui.Rectangle(64, 64)
    rect3.set_name("IconRectangle")
    rect3.set_position(520, 150, 0)
    rect3.set_color(1.0, 1.0, 1.0, 1.0)  # White
    if icon_img:
        rect3.set_image(icon_img)
        print("✓ Applied icon texture to rect3")
    
    # Rectangle 4: Colored rectangle without texture (for comparison)
    rect4 = ui.Rectangle(150, 100)
    rect4.set_name("SolidColorRectangle")
    rect4.set_position(350, 300, 0)
    rect4.set_color(0.2, 0.6, 1.0, 1.0)  # Light blue
    print("✓ Created solid color rectangle (no texture)")
    
    # Rectangle 5: Tinted texture (color + texture)
    rect5 = ui.Rectangle(128, 128)
    rect5.set_name("TintedCheckerboard")
    rect5.set_position(100, 350, 0)
    rect5.set_color(1.0, 0.5, 0.5, 1.0)  # Red tint
    if checkerboard_img:
        rect5.set_image(checkerboard_img)
        print("✓ Applied tinted checkerboard texture to rect5")
    
    print()
    
    # Render loop
    print("Starting render loop...")
    frame_count = 0
    while not renderer.should_close():
        renderer.poll_events()
        
        if renderer.begin_frame():
            # Render all rectangles
            renderer.render_object(rect1)
            renderer.render_object(rect2)
            renderer.render_object(rect3)
            renderer.render_object(rect4)
            renderer.render_object(rect5)
            
            renderer.end_frame()
            frame_count += 1
    
    print(f"\nRendered {frame_count} frames")
    renderer.shutdown()
    print("Renderer shutdown complete")

if __name__ == "__main__":
    main()
