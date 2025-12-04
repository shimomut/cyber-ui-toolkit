#!/usr/bin/env python3
"""
Visual verification of Frame2D clipping.
Creates a simple test case and saves an annotated image.
"""

import sys
sys.path.insert(0, '../build')

import cyber_ui_core as ui
from PIL import Image as PILImage, ImageDraw, ImageFont
import os

def load_image_with_pillow(filepath):
    """Load an image using Pillow and return a cyber_ui Image object"""
    if not os.path.exists(filepath):
        return None
    
    try:
        pil_img = PILImage.open(filepath)
        if pil_img.mode != 'RGBA':
            pil_img = pil_img.convert('RGBA')
        
        img_bytes = pil_img.tobytes()
        ui_img = ui.Image()
        width, height = pil_img.size
        channels = 4
        
        if ui_img.load_from_data(img_bytes, width, height, channels):
            return ui_img
        return None
    except:
        return None

def main():
    print("=== Visual Clipping Verification ===\n")
    
    # Initialize renderer
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(800, 700, "Clipping Visual Test"):
        print("Failed to initialize renderer")
        return
    
    # Create scene
    scene = ui.SceneRoot()
    camera = scene.get_camera()
    camera.set_position(0.0, 0.0, 800.0)
    camera.set_perspective(1.0472, 800.0/700.0, 0.1, 2000.0)
    
    # Load test image
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "samples", "data")
    gradient_img = load_image_with_pillow(os.path.join(data_dir, "gradient.png"))
    
    # Create Frame3D
    frame3d = ui.Frame3D()
    frame3d.set_position(0.0, 0.0, 0.0)
    scene.add_frame3d(frame3d)
    
    # Create Frame2D with clipping at center of screen
    clip_panel = ui.Frame2D()
    clip_panel.set_position(150.0, 50.0)
    clip_panel.set_size(500.0, 600.0)
    clip_panel.set_clipping_enabled(True)
    
    # Dark background
    panel_bg = ui.Rectangle(500.0, 600.0)
    panel_bg.set_position(0.0, 0.0)
    panel_bg.set_color(0.15, 0.15, 0.2, 1.0)
    clip_panel.add_child(panel_bg)
    
    # Green border to show clipping boundary
    border_width = 4.0
    
    # Top border
    border_top = ui.Rectangle(500.0, border_width)
    border_top.set_position(0.0, 0.0)
    border_top.set_color(0.0, 1.0, 0.0, 1.0)
    clip_panel.add_child(border_top)
    
    # Bottom border
    border_bottom = ui.Rectangle(500.0, border_width)
    border_bottom.set_position(0.0, 600.0 - border_width)
    border_bottom.set_color(0.0, 1.0, 0.0, 1.0)
    clip_panel.add_child(border_bottom)
    
    # Left border
    border_left = ui.Rectangle(border_width, 600.0)
    border_left.set_position(0.0, 0.0)
    border_left.set_color(0.0, 1.0, 0.0, 1.0)
    clip_panel.add_child(border_left)
    
    # Right border
    border_right = ui.Rectangle(border_width, 600.0)
    border_right.set_position(500.0 - border_width, 0.0)
    border_right.set_color(0.0, 1.0, 0.0, 1.0)
    clip_panel.add_child(border_right)
    
    # Add large rectangles that extend beyond clipping region
    # Red rectangle extending top
    rect_top = ui.Rectangle(200.0, 200.0)
    rect_top.set_position(150.0, -80.0)  # Extends above clipping region
    rect_top.set_color(1.0, 0.2, 0.2, 1.0)
    if gradient_img:
        rect_top.set_image(gradient_img)
    clip_panel.add_child(rect_top)
    
    # Blue rectangle extending bottom
    rect_bottom = ui.Rectangle(200.0, 200.0)
    rect_bottom.set_position(150.0, 480.0)  # Extends below clipping region
    rect_bottom.set_color(0.2, 0.2, 1.0, 1.0)
    if gradient_img:
        rect_bottom.set_image(gradient_img)
    clip_panel.add_child(rect_bottom)
    
    # Yellow rectangle extending left
    rect_left = ui.Rectangle(200.0, 150.0)
    rect_left.set_position(-80.0, 225.0)  # Extends left of clipping region
    rect_left.set_color(1.0, 1.0, 0.2, 1.0)
    if gradient_img:
        rect_left.set_image(gradient_img)
    clip_panel.add_child(rect_left)
    
    # Magenta rectangle extending right
    rect_right = ui.Rectangle(200.0, 150.0)
    rect_right.set_position(380.0, 225.0)  # Extends right of clipping region
    rect_right.set_color(1.0, 0.2, 1.0, 1.0)
    if gradient_img:
        rect_right.set_image(gradient_img)
    clip_panel.add_child(rect_right)
    
    # Center rectangle (fully inside)
    rect_center = ui.Rectangle(150.0, 150.0)
    rect_center.set_position(175.0, 225.0)
    rect_center.set_color(0.2, 1.0, 0.2, 1.0)
    if gradient_img:
        rect_center.set_image(gradient_img)
    clip_panel.add_child(rect_center)
    
    frame3d.add_child(clip_panel)
    
    print("✓ Scene created")
    print("  - Frame2D at (150, 50) with size (500x600)")
    print("  - Green borders mark clipping boundary")
    print("  - 5 colored rectangles extend beyond boundaries")
    print("  - 1 green rectangle fully inside\n")
    
    # Render frame
    if renderer.begin_frame():
        renderer.render_scene(scene)
        renderer.end_frame()
    
    # Capture and save
    output_dir = os.path.join(script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "clipping_visual_test.png")
    
    if renderer.save_capture(output_file):
        print(f"✓ Saved capture to: {output_file}")
        
        # Load and annotate the image
        img = PILImage.open(output_file)
        draw = ImageDraw.Draw(img)
        
        # Calculate clipping region in screen space (accounting for retina)
        scale = img.width / 800
        clip_x = int(150 * scale)
        clip_y = int(50 * scale)
        clip_w = int(500 * scale)
        clip_h = int(600 * scale)
        
        # Draw annotation box (yellow dashed line)
        for i in range(0, clip_w, 20):
            draw.line([(clip_x + i, clip_y), (clip_x + i + 10, clip_y)], fill=(255, 255, 0), width=3)
            draw.line([(clip_x + i, clip_y + clip_h), (clip_x + i + 10, clip_y + clip_h)], fill=(255, 255, 0), width=3)
        
        for i in range(0, clip_h, 20):
            draw.line([(clip_x, clip_y + i), (clip_x, clip_y + i + 10)], fill=(255, 255, 0), width=3)
            draw.line([(clip_x + clip_w, clip_y + i), (clip_x + clip_w, clip_y + i + 10)], fill=(255, 255, 0), width=3)
        
        # Save annotated version
        annotated_file = os.path.join(output_dir, "clipping_visual_test_annotated.png")
        img.save(annotated_file)
        print(f"✓ Saved annotated version to: {annotated_file}")
        
        print("\nExpected result:")
        print("  - Green borders should be visible inside the yellow dashed box")
        print("  - Colored rectangles should be clipped at the green borders")
        print("  - NO colored content should appear outside the green borders")
        print("  - Background outside clipping region should be dark gray")
    
    renderer.shutdown()
    print("\n✓ Test complete")

if __name__ == "__main__":
    main()
