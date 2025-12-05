#!/usr/bin/env python3
"""
Test the simplified clipping demo setup.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build'))

import cyber_ui_core as ui


def main():
    print("Testing Simplified Clipping Demo Setup")
    print("=" * 70)
    
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(800, 700, "Clipping Demo Test"):
        print("Failed to initialize renderer")
        return 1
    
    scene = ui.SceneRoot()
    camera = scene.get_camera()
    camera.set_position(0, 0, 800)
    camera.set_perspective(1.0472, 1600.0/1400.0, 0.1, 2000.0)
    
    # Load fonts
    font = ui.Font()
    font.load_from_file("/System/Library/Fonts/Helvetica.ttc", 32.0)
    
    title_font = ui.Font()
    title_font.load_from_file("/System/Library/Fonts/Helvetica.ttc", 48.0)
    title_font.set_bold(True)
    
    # Create Frame3D
    frame3d = ui.Frame3D(800, 600)
    frame3d.set_position(0, 0, 0)
    scene.add_frame3d(frame3d)
    
    # Create Frame2D with clipping
    clip_panel = ui.Frame2D(500, 600)
    clip_panel.set_position(150, 50)
    clip_panel
    clip_panel.set_clipping_enabled(True)
    
    # Background
    bg = ui.Rectangle(500, 600)
    bg.set_position(0, 0)
    bg.set_color(0.05, 0.05, 0.08, 1.0)
    clip_panel.add_child(bg)
    
    # Borders
    border_width = 8
    borders = [
        (500, border_width, 0, 0),           # Top
        (500, border_width, 0, 600 - border_width),  # Bottom
        (border_width, 600, 0, 0),           # Left
        (border_width, 600, 500 - border_width, 0),  # Right
    ]
    
    for w, h, x, y in borders:
        border = ui.Rectangle(w, h)
        border.set_position(x, y)
        border.set_color(0.0, 1.0, 0.0, 1.0)  # Green
        clip_panel.add_child(border)
    
    # Title - REMOVED for now to debug
    
    # Red rectangle
    rect1 = ui.Rectangle(300, 300)
    rect1.set_position(100, 200)
    rect1.set_color(1.0, 0.2, 0.2, 1.0)
    clip_panel.add_child(rect1)
    
    # Blue rectangle
    rect2 = ui.Rectangle(300, 300)
    rect2.set_position(200, 400)
    rect2.set_color(0.2, 0.5, 1.0, 1.0)
    clip_panel.add_child(rect2)
    
    # Moving text
    text1 = ui.Text("MOVING TEXT")
    text1.set_position(250, 300)
    text1.set_color(1.0, 0.0, 1.0, 1.0)  # Magenta
    text1.set_font(title_font)
    text1.set_alignment(ui.TextAlignment.Center)
    clip_panel.add_child(text1)
    
    frame3d.add_child(clip_panel)
    
    print("Scene created:")
    print("  - Frame2D at (150, 50) size (500x600)")
    print("  - Background + 4 green borders")
    print("  - Title: 'CLIPPING DEMO' (48pt yellow)")
    print("  - 2 rectangles (300x300 red and blue)")
    print("  - Text: 'MOVING TEXT' (48pt magenta)")
    print()
    
    # Render
    for i in range(10):
        renderer.poll_events()
        if renderer.should_close():
            break
        renderer.begin_frame()
        renderer.render_scene(scene)
        renderer.end_frame()
    
    # Capture
    os.makedirs("tests/output", exist_ok=True)
    renderer.save_capture("tests/output/clipping_demo_simple.png")
    
    data, width, height = renderer.capture_frame()
    print(f"Captured: {width}x{height}")
    
    # Analyze
    import struct
    pixels = struct.unpack(f'{len(data)}B', data)
    
    # Count colored pixels
    yellow_count = 0  # Title
    magenta_count = 0  # Moving text
    red_count = 0
    blue_count = 0
    green_count = 0  # Borders
    
    for i in range(0, len(pixels), 4):
        r, g, b = pixels[i+2], pixels[i+1], pixels[i]
        
        if r > 150 and g > 150 and b < 100:
            yellow_count += 1
        elif r > 200 and g < 50 and b > 200:
            magenta_count += 1
        elif r > 200 and g < 100 and b < 100:
            red_count += 1
        elif r < 100 and g > 100 and b > 200:
            blue_count += 1
        elif r < 50 and g > 200 and b < 50:
            green_count += 1
    
    total = width * height
    print()
    print("Pixel counts:")
    print(f"  Yellow (title):      {yellow_count:6,} ({yellow_count/total*100:.2f}%)")
    print(f"  Magenta (text):      {magenta_count:6,} ({magenta_count/total*100:.2f}%)")
    print(f"  Red (rect):          {red_count:6,} ({red_count/total*100:.2f}%)")
    print(f"  Blue (rect):         {blue_count:6,} ({blue_count/total*100:.2f}%)")
    print(f"  Green (borders):     {green_count:6,} ({green_count/total*100:.2f}%)")
    print()
    
    success = True
    
    if yellow_count > 500:
        print("✓ Title text is rendering")
    else:
        print("✗ Title text NOT rendering")
        success = False
    
    if magenta_count > 500:
        print("✓ Moving text is rendering")
    else:
        print("✗ Moving text NOT rendering")
        success = False
    
    if red_count > 10000:
        print("✓ Red rectangle is rendering")
    else:
        print("✗ Red rectangle NOT rendering")
        success = False
    
    if blue_count > 10000:
        print("✓ Blue rectangle is rendering")
    else:
        print("✗ Blue rectangle NOT rendering")
        success = False
    
    if green_count > 1000:
        print("✓ Green borders are rendering")
    else:
        print("✗ Green borders NOT rendering")
        success = False
    
    renderer.shutdown()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
