#!/usr/bin/env python3
"""
Frame2D Clipping Demo - Clear demonstration of hardware-accelerated clipping

This sample shows:
- Frame2D with bright green borders marking the clipping boundary
- Large, brightly colored rectangles that move in/out of the clipping region
- Animated text elements that get clipped at the boundaries
- Clear visual demonstration of content being clipped at Frame2D edges

Features:
- Bright colors (red, blue, yellow, magenta, cyan) for high visibility
- Large rectangles (200x150 to 250x250) that clearly extend beyond boundaries
- Smooth animations showing content entering and leaving the clipping region
- Dark background for maximum contrast

Usage:
    python clipping_demo.py              # Normal mode (no capture)
    python clipping_demo.py --capture    # Enable frame capture
"""

import sys
sys.path.insert(0, '../../build')

import cyber_ui_core as ui
from PIL import Image as PILImage
import os
import math
import argparse

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
            print(f"✓ Loaded: {os.path.basename(filepath)} ({width}x{height})")
            return ui_img
        else:
            print(f"✗ Failed to load: {filepath}")
            return None
            
    except Exception as e:
        print(f"✗ Error loading {filepath}: {e}")
        return None

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Frame2D Clipping Demo')
    parser.add_argument('--capture', action='store_true',
                        help='Enable frame capture to samples/output/')
    args = parser.parse_args()
    
    print("=== Cyber UI Toolkit - Frame2D Clipping Demo ===\n")
    
    if args.capture:
        print("📸 Frame capture ENABLED")
        print("   Frames will be saved to samples/output/\n")
    else:
        print("Frame capture disabled (use --capture to enable)\n")
    
    # Initialize renderer
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(800, 700, "Cyber UI - Clipping Demo"):
        print("Failed to initialize renderer")
        return
    
    print("Renderer initialized successfully!")
    print("Press ESC or close window to exit\n")
    
    # Create scene root and camera
    scene = ui.SceneRoot()
    camera = scene.get_camera()
    camera.set_position(0.0, 0.0, 800.0)
    camera.set_perspective(1.0472, 800.0/700.0, 0.1, 2000.0)  # 60 degrees FOV
    print("✓ Camera configured\n")
    
    # Load textures
    print("Loading textures...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "data")
    
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
    
    # ===== SINGLE PANEL: Clipping Enabled =====
    print("Creating clipping panel...")
    clip_panel = ui.Frame2D()
    clip_panel.set_name("ClippingPanel")
    clip_panel.set_position(150.0, 50.0)
    clip_panel.set_size(500.0, 600.0)
    clip_panel.set_clipping_enabled(True)
    
    # Dark background for contrast
    panel_bg = ui.Rectangle(500.0, 600.0)
    panel_bg.set_name("PanelBackground")
    panel_bg.set_position(0.0, 0.0)
    panel_bg.set_color(0.05, 0.05, 0.08, 1.0)  # Very dark background
    clip_panel.add_child(panel_bg)
    
    # Thick bright green borders to show clipping boundary
    border_width = 8.0
    
    border_top = ui.Rectangle(500.0, border_width)
    border_top.set_name("BorderTop")
    border_top.set_position(0.0, 0.0)
    border_top.set_color(0.0, 1.0, 0.0, 1.0)  # Bright green
    clip_panel.add_child(border_top)
    
    border_bottom = ui.Rectangle(500.0, border_width)
    border_bottom.set_name("BorderBottom")
    border_bottom.set_position(0.0, 600.0 - border_width)
    border_bottom.set_color(0.0, 1.0, 0.0, 1.0)
    clip_panel.add_child(border_bottom)
    
    border_left = ui.Rectangle(border_width, 600.0)
    border_left.set_name("BorderLeft")
    border_left.set_position(0.0, 0.0)
    border_left.set_color(0.0, 1.0, 0.0, 1.0)
    clip_panel.add_child(border_left)
    
    border_right = ui.Rectangle(border_width, 600.0)
    border_right.set_name("BorderRight")
    border_right.set_position(500.0 - border_width, 0.0)
    border_right.set_color(0.0, 1.0, 0.0, 1.0)
    clip_panel.add_child(border_right)
    
    # Title
    title = ui.Text("Frame2D Clipping Demo")
    title.set_name("Title")
    title.set_position(250.0, 30.0)
    title.set_color(1.0, 1.0, 0.0, 1.0)  # Yellow for visibility
    title.set_font(title_font)
    title.set_alignment(ui.TextAlignment.Center)
    clip_panel.add_child(title)
    
    subtitle = ui.Text("Green borders = clipping boundary")
    subtitle.set_name("Subtitle")
    subtitle.set_position(250.0, 65.0)
    subtitle.set_color(0.0, 1.0, 0.0, 1.0)  # Green to match borders
    subtitle.set_font(font)
    subtitle.set_alignment(ui.TextAlignment.Center)
    clip_panel.add_child(subtitle)
    
    # Large, bright colored rectangles that clearly extend beyond boundaries
    animated_rects = []
    
    # Red rectangle - moves vertically
    rect1 = ui.Rectangle(250.0, 250.0)
    rect1.set_name("RedRect")
    rect1.set_position(125.0, 150.0)
    rect1.set_color(1.0, 0.0, 0.0, 1.0)  # Pure red
    if gradient_img:
        rect1.set_image(gradient_img)
    clip_panel.add_child(rect1)
    animated_rects.append(rect1)
    
    # Blue rectangle - moves vertically (opposite phase)
    rect2 = ui.Rectangle(250.0, 250.0)
    rect2.set_name("BlueRect")
    rect2.set_position(125.0, 350.0)
    rect2.set_color(0.0, 0.5, 1.0, 1.0)  # Bright blue
    if checker_img:
        rect2.set_image(checker_img)
    clip_panel.add_child(rect2)
    animated_rects.append(rect2)
    
    # Yellow rectangle - moves horizontally
    rect3 = ui.Rectangle(200.0, 150.0)
    rect3.set_name("YellowRect")
    rect3.set_position(150.0, 250.0)
    rect3.set_color(1.0, 1.0, 0.0, 1.0)  # Bright yellow
    if icon_img:
        rect3.set_image(icon_img)
    clip_panel.add_child(rect3)
    animated_rects.append(rect3)
    
    # Animated text elements with bright colors
    animated_texts = []
    
    text1 = ui.Text("MOVING TEXT")
    text1.set_name("Text1")
    text1.set_position(250.0, 500.0)
    text1.set_color(1.0, 0.0, 1.0, 1.0)  # Magenta
    text1.set_font(title_font)
    text1.set_alignment(ui.TextAlignment.Center)
    clip_panel.add_child(text1)
    animated_texts.append(text1)
    
    text2 = ui.Text("WATCH ME CLIP!")
    text2.set_name("Text2")
    text2.set_position(250.0, 100.0)
    text2.set_color(0.0, 1.0, 1.0, 1.0)  # Cyan
    text2.set_font(title_font)
    text2.set_alignment(ui.TextAlignment.Center)
    clip_panel.add_child(text2)
    animated_texts.append(text2)
    
    frame3d.add_child(clip_panel)
    print("✓ Clipping panel created with 3 large rectangles and 2 text elements")
    
    print("\n" + "="*70)
    print("Scene Hierarchy:")
    print("="*70)
    print("Frame3D (MainFrame3D)")
    print("└── Frame2D (ClippingPanel) - CLIPPING ENABLED")
    print("    ├── Dark background")
    print("    ├── Bright green borders (clipping boundary)")
    print("    ├── Title and subtitle text")
    print("    ├── 3 large colored rectangles with textures")
    print("    └── 2 animated text elements")
    print("="*70)
    print()
    
    # Setup capture if enabled
    output_dir = None
    capture_count = 0
    
    if args.capture:
        output_dir = os.path.join(script_dir, "..", "output")
        os.makedirs(output_dir, exist_ok=True)
    
    # Render loop with animations
    print("Starting render loop with slow clipping animations...")
    print("Watch how content gets clipped at the green borders!")
    if args.capture:
        print("Capturing frames automatically...")
    print()
    
    frame_count = 0
    
    while not renderer.should_close():
        renderer.poll_events()
        
        time = frame_count * 0.016  # ~60fps
        
        # Animate rectangles with clear, visible movement
        # Red rectangle - vertical oscillation
        offset_y1 = math.sin(time * 0.5) * 250.0  # Large movement to show clipping
        animated_rects[0].set_position(125.0, 150.0 + offset_y1)
        
        # Blue rectangle - vertical oscillation (opposite phase)
        offset_y2 = math.sin(time * 0.5 + 3.14) * 250.0  # 180 degrees out of phase
        animated_rects[1].set_position(125.0, 350.0 + offset_y2)
        
        # Yellow rectangle - horizontal oscillation
        offset_x = math.sin(time * 0.6) * 200.0  # Horizontal movement
        animated_rects[2].set_position(150.0 + offset_x, 250.0)
        
        # Animate text with clear movement
        # Top text - moves vertically
        text_offset_y1 = math.sin(time * 0.7) * 300.0
        animated_texts[0].set_position(250.0, 500.0 + text_offset_y1)
        
        # Bottom text - moves vertically (opposite)
        text_offset_y2 = math.sin(time * 0.7 + 3.14) * 300.0
        animated_texts[1].set_position(250.0, 100.0 + text_offset_y2)
        
        # Very subtle 3D rotation for depth
        frame3d.set_rotation(math.sin(time * 0.1) * 0.02, math.cos(time * 0.08) * 0.01, 0.0)
        
        if renderer.begin_frame():
            renderer.render_scene(scene)
            renderer.end_frame()
            frame_count += 1
            
            # Capture frames if enabled
            if args.capture and output_dir:
                if frame_count == 5:
                    capture_filename = os.path.join(output_dir, "clipping_demo_initial.png")
                    if renderer.save_capture(capture_filename):
                        print(f"✓ Captured initial frame: {capture_filename}")
                        capture_count += 1
                
                if frame_count > 5 and frame_count % 120 == 0:
                    capture_filename = os.path.join(output_dir, f"clipping_demo_frame_{frame_count:05d}.png")
                    if renderer.save_capture(capture_filename):
                        print(f"✓ Captured frame {frame_count}: {capture_filename}")
                        capture_count += 1
    
    # Final capture if enabled
    if args.capture and output_dir:
        print("\nCapturing final frame...")
        final_filename = os.path.join(output_dir, "clipping_demo_final.png")
        if renderer.save_capture(final_filename):
            print(f"✓ Final frame saved: {final_filename}")
            capture_count += 1
        
        print(f"\nRendered {frame_count} frames")
        print(f"Captured {capture_count} images to {output_dir}")
    else:
        print(f"\nRendered {frame_count} frames")
    
    renderer.shutdown()
    print("Renderer shutdown complete")

if __name__ == "__main__":
    main()
