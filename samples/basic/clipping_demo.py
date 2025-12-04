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
    
    # Get script directory for output
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create Frame3D container with off-screen rendering enabled
    frame3d = ui.Frame3D()
    frame3d.set_name("MainFrame3D")
    frame3d.set_position(0.0, 0.0, 0.0)
    frame3d.set_offscreen_rendering_enabled(True)
    frame3d.set_render_target_size(800, 700)  # Match window size
    scene.add_frame3d(frame3d)
    
    # Load fonts with larger sizes for visibility
    print("Loading fonts...")
    font = ui.Font()
    font.load_from_file("/System/Library/Fonts/Helvetica.ttc", 32.0)  # Larger
    
    title_font = ui.Font()
    title_font.load_from_file("/System/Library/Fonts/Helvetica.ttc", 48.0)  # Much larger
    title_font.set_bold(True)
    print("✓ Fonts loaded\n")
    
    # ===== SINGLE PANEL: Clipping Enabled =====
    print("Creating clipping panel...")
    clip_panel = ui.Frame2D()
    clip_panel.set_name("ClippingPanel")
    clip_panel.set_position(150.0, 50.0)
    clip_panel.set_size(500.0, 600.0)
    clip_panel.set_clipping_enabled(True)
    
    # Dark background for contrast - fills entire Frame2D from top-left
    panel_bg = ui.Rectangle(500.0, 600.0)
    panel_bg.set_name("PanelBackground")
    panel_bg.set_position(0.0, 0.0)  # Top-left corner (Rectangle uses top-left origin)
    panel_bg.set_color(0.05, 0.05, 0.08, 1.0)  # Very dark background
    clip_panel.add_child(panel_bg)
    
    # Thick bright green borders to show clipping boundary
    border_width = 8.0
    
    border_top = ui.Rectangle(500.0, border_width)
    border_top.set_name("BorderTop")
    border_top.set_position(0.0, 0.0)  # Top edge
    border_top.set_color(0.0, 1.0, 0.0, 1.0)  # Bright green
    clip_panel.add_child(border_top)
    
    border_bottom = ui.Rectangle(500.0, border_width)
    border_bottom.set_name("BorderBottom")
    border_bottom.set_position(0.0, 600.0 - border_width)  # Bottom edge
    border_bottom.set_color(0.0, 1.0, 0.0, 1.0)
    clip_panel.add_child(border_bottom)
    
    border_left = ui.Rectangle(border_width, 600.0)
    border_left.set_name("BorderLeft")
    border_left.set_position(0.0, 0.0)  # Left edge
    border_left.set_color(0.0, 1.0, 0.0, 1.0)
    clip_panel.add_child(border_left)
    
    border_right = ui.Rectangle(border_width, 600.0)
    border_right.set_name("BorderRight")
    border_right.set_position(500.0 - border_width, 0.0)  # Right edge
    border_right.set_color(0.0, 1.0, 0.0, 1.0)
    clip_panel.add_child(border_right)
    
    # Title - larger and more visible, positioned from top-left origin
    title = ui.Text("CLIPPING DEMO")
    title.set_name("Title")
    title.set_position(100.0, 20.0)  # Near top-left
    title.set_color(1.0, 1.0, 0.0, 1.0)  # Yellow for visibility
    title.set_font(title_font)
    title.set_alignment(ui.TextAlignment.Left)
    clip_panel.add_child(title)
    
    # Simplified: Just 2 large rectangles (no textures)
    animated_rects = []
    
    # Red rectangle - moves vertically
    rect1 = ui.Rectangle(300.0, 300.0)
    rect1.set_name("RedRect")
    rect1.set_position(100.0, 100.0)  # Position from top-left
    rect1.set_color(1.0, 0.2, 0.2, 1.0)  # Bright red
    clip_panel.add_child(rect1)
    animated_rects.append(rect1)
    
    # Blue rectangle - moves vertically (opposite phase)
    rect2 = ui.Rectangle(300.0, 300.0)
    rect2.set_name("BlueRect")
    rect2.set_position(100.0, 250.0)  # Position from top-left
    rect2.set_color(0.2, 0.5, 1.0, 1.0)  # Bright blue
    clip_panel.add_child(rect2)
    animated_rects.append(rect2)
    
    # Simplified: Just 1 animated text element
    animated_texts = []
    
    text1 = ui.Text("MOVING TEXT")
    text1.set_name("MovingText")
    text1.set_position(150.0, 200.0)  # Position from top-left
    text1.set_color(1.0, 0.0, 1.0, 1.0)  # Magenta
    text1.set_font(title_font)
    text1.set_alignment(ui.TextAlignment.Left)
    clip_panel.add_child(text1)
    animated_texts.append(text1)
    
    frame3d.add_child(clip_panel)
    print("✓ Clipping panel created with 2 rectangles and 1 text element")
    
    print("\n" + "="*70)
    print("Scene Hierarchy:")
    print("="*70)
    print("Frame3D (MainFrame3D)")
    print("└── Frame2D (ClippingPanel) - CLIPPING ENABLED")
    print("    ├── Dark background")
    print("    ├── Bright green borders (clipping boundary)")
    print("    ├── Title text (yellow)")
    print("    ├── 2 large colored rectangles (red, blue)")
    print("    └── 1 animated text element (magenta)")
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
        
        # Animate rectangles with clear, visible movement (10x slower)
        # Red rectangle - vertical oscillation
        offset_y1 = math.sin(time * 0.05) * 250.0  # Large movement to show clipping
        animated_rects[0].set_position(100.0, 100.0 + offset_y1)
        
        # Blue rectangle - vertical oscillation (opposite phase)
        offset_y2 = math.sin(time * 0.05 + 3.14) * 250.0  # 180 degrees out of phase
        animated_rects[1].set_position(100.0, 250.0 + offset_y2)
        
        # Animate text with clear movement (10x slower)
        text_offset_y = math.sin(time * 0.07) * 300.0
        animated_texts[0].set_position(150.0, 200.0 + text_offset_y)
        
        # 3D rotation now works with off-screen rendering!
        # Content is rendered to texture with proper clipping, then the texture is rotated
        frame3d.set_rotation(math.sin(time * 0.01) * 0.3, math.cos(time * 0.008) * 0.2, 0.0)
        
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
