#!/usr/bin/env python3
"""
Debug the clipping demo by capturing a single frame and analyzing it.
"""

import sys
sys.path.insert(0, '../build')

import cyber_ui_core as ui
from PIL import Image as PILImage
import os
import math

def load_image_with_pillow(filepath):
    """Load an image using Pillow and return a cyber_ui Image object"""
    if not os.path.exists(filepath):
        print(f"Warning: Image file not found: {filepath}")
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
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def main():
    print("=== Debugging Clipping Demo ===\n")
    
    # Initialize renderer
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(800, 700, "Debug Clipping Demo"):
        print("Failed to initialize renderer")
        return
    
    print("✓ Renderer initialized\n")
    
    # Create scene root and camera
    scene = ui.SceneRoot()
    camera = scene.get_camera()
    camera.set_position(0.0, 0.0, 800.0)
    camera.set_perspective(1.0472, 800.0/700.0, 0.1, 2000.0)
    print("✓ Camera configured\n")
    
    # Load textures
    print("Loading textures...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "samples", "data")
    
    gradient_img = load_image_with_pillow(os.path.join(data_dir, "gradient.png"))
    checker_img = load_image_with_pillow(os.path.join(data_dir, "checkerboard.png"))
    icon_img = load_image_with_pillow(os.path.join(data_dir, "icon.png"))
    print()
    
    # Create Frame3D container
    frame3d = ui.Frame3D()
    frame3d.set_name("MainFrame3D")
    frame3d.set_position(0.0, 0.0, 0.0)
    scene.add_frame3d(frame3d)
    
    # Load fonts
    print("Loading fonts...")
    font = ui.Font()
    font.load_from_file("/System/Library/Fonts/Helvetica.ttc", 20.0)
    
    title_font = ui.Font()
    title_font.load_from_file("/System/Library/Fonts/Helvetica.ttc", 28.0)
    title_font.set_bold(True)
    print("✓ Fonts loaded\n")
    
    # Create Frame2D with clipping
    print("Creating clipping panel...")
    clip_panel = ui.Frame2D()
    clip_panel.set_name("ClippingPanel")
    clip_panel.set_position(150.0, 50.0)
    clip_panel.set_size(500.0, 600.0)
    clip_panel.set_clipping_enabled(True)
    
    print(f"  Position: (150, 50)")
    print(f"  Size: (500, 600)")
    print(f"  Clipping: ENABLED")
    
    # Background
    panel_bg = ui.Rectangle(500.0, 600.0)
    panel_bg.set_name("PanelBackground")
    panel_bg.set_position(0.0, 0.0)
    panel_bg.set_color(0.08, 0.08, 0.12, 1.0)
    clip_panel.add_child(panel_bg)
    print(f"  Added background: 500x600 at (0, 0)")
    
    # Border rectangles
    border_top = ui.Rectangle(500.0, 3.0)
    border_top.set_position(0.0, 0.0)
    border_top.set_color(0.3, 1.0, 0.3, 1.0)
    clip_panel.add_child(border_top)
    
    border_bottom = ui.Rectangle(500.0, 3.0)
    border_bottom.set_position(0.0, 597.0)
    border_bottom.set_color(0.3, 1.0, 0.3, 1.0)
    clip_panel.add_child(border_bottom)
    
    border_left = ui.Rectangle(3.0, 600.0)
    border_left.set_position(0.0, 0.0)
    border_left.set_color(0.3, 1.0, 0.3, 1.0)
    clip_panel.add_child(border_left)
    
    border_right = ui.Rectangle(3.0, 600.0)
    border_right.set_position(497.0, 0.0)
    border_right.set_color(0.3, 1.0, 0.3, 1.0)
    clip_panel.add_child(border_right)
    print(f"  Added green borders")
    
    # Title
    title = ui.Text("Frame2D Clipping Demo")
    title.set_position(250.0, 25.0)
    title.set_color(1.0, 1.0, 1.0, 1.0)
    title.set_font(title_font)
    title.set_alignment(ui.TextAlignment.Center)
    clip_panel.add_child(title)
    print(f"  Added title text at (250, 25)")
    
    # Animated rectangles
    print("\n  Adding animated rectangles:")
    for i in range(5):
        rect = ui.Rectangle(140.0, 140.0)
        rect.set_name(f"AnimatedRect{i}")
        base_y = 120.0 + i * 100.0
        rect.set_position(180.0, base_y)
        
        if i % 3 == 0:
            rect.set_color(1.0, 0.3, 0.3, 1.0)
            print(f"    Rect {i}: RED at (180, {base_y})")
            if gradient_img:
                rect.set_image(gradient_img)
        elif i % 3 == 1:
            rect.set_color(0.3, 0.5, 1.0, 1.0)
            print(f"    Rect {i}: BLUE at (180, {base_y})")
            if checker_img:
                rect.set_image(checker_img)
        else:
            rect.set_color(1.0, 0.8, 0.2, 1.0)
            print(f"    Rect {i}: YELLOW at (180, {base_y})")
            if icon_img:
                rect.set_image(icon_img)
        
        clip_panel.add_child(rect)
    
    # Animated text
    print("\n  Adding animated text:")
    for i in range(4):
        text = ui.Text(f"Moving Text {i+1}")
        text.set_name(f"AnimatedText{i}")
        text.set_position(250.0, 150.0 + i * 130.0)
        text.set_color(1.0, 1.0, 1.0, 0.95)
        text.set_font(font)
        text.set_alignment(ui.TextAlignment.Center)
        clip_panel.add_child(text)
        print(f"    Text {i}: at (250, {150.0 + i * 130.0})")
    
    frame3d.add_child(clip_panel)
    
    print("\n✓ Scene created\n")
    
    # Render a single frame
    print("Rendering frame...")
    if renderer.begin_frame():
        renderer.render_scene(scene)
        renderer.end_frame()
    
    # Capture
    output_dir = os.path.join(script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "clipping_demo_debug.png")
    
    if renderer.save_capture(output_file):
        print(f"✓ Saved capture to: {output_file}\n")
        
        # Analyze the image
        img = PILImage.open(output_file)
        pixels = list(img.getdata())
        
        # Count unique colors
        unique_colors = set(pixels)
        print(f"Image analysis:")
        print(f"  Size: {img.size}")
        print(f"  Unique colors: {len(unique_colors)}")
        
        # Sample some pixels
        width, height = img.size
        center_x, center_y = width // 2, height // 2
        
        print(f"\n  Sample pixels:")
        print(f"    Center ({center_x}, {center_y}): {img.getpixel((center_x, center_y))}")
        print(f"    Top-left (10, 10): {img.getpixel((10, 10))}")
        print(f"    Top-right ({width-10}, 10): {img.getpixel((width-10, 10))}")
        
        # Check if there's any non-background content
        bg_color = (26, 26, 26, 255)  # Expected background
        non_bg_count = sum(1 for p in pixels if abs(p[0] - bg_color[0]) > 30 or 
                          abs(p[1] - bg_color[1]) > 30 or 
                          abs(p[2] - bg_color[2]) > 30)
        
        print(f"\n  Non-background pixels: {non_bg_count} ({non_bg_count/len(pixels)*100:.2f}%)")
        
        if non_bg_count < len(pixels) * 0.01:
            print("\n⚠ WARNING: Very little content rendered!")
            print("  This suggests the objects may not be visible.")
    
    renderer.shutdown()
    print("\n✓ Debug complete")

if __name__ == "__main__":
    main()
