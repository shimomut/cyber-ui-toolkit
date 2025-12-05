#!/usr/bin/env python3
"""
Test if text renders in Frame2D.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build'))

import cyber_ui_core as ui


def main():
    print("Text Rendering Test")
    print("=" * 70)
    
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(800, 600, "Text Test"):
        print("Failed to initialize renderer")
        return 1
    
    scene = ui.SceneRoot()
    camera = scene.get_camera()
    camera.set_position(0, 0, 800)
    camera.set_perspective(1.0472, 1600.0/1200.0, 0.1, 2000.0)
    
    # Load font
    font = ui.Font()
    if not font.load_from_file("/System/Library/Fonts/Helvetica.ttc", 48.0):
        print("Failed to load font")
        return 1
    
    # Create Frame3D
    frame3d = ui.Frame3D(800, 600)
    frame3d.set_position(0, 0, 0)
    scene.add_frame3d(frame3d)
    
    # Create Frame2D
    frame2d = ui.Frame2D(600, 400)
    frame2d.set_position(0, 0)
    frame2d
    
    # Add text
    text = ui.Text("HELLO WORLD")
    text.set_position(300, 200)  # Center
    text.set_color(1.0, 1.0, 0.0, 1.0)  # Yellow
    text.set_font(font)
    text.set_alignment(ui.TextAlignment.Center)
    frame2d.add_child(text)
    
    frame3d.add_child(frame2d)
    
    print("Scene:")
    print("  Frame3D at (0, 0, 0)")
    print("  └─ Frame2D at (0, 0) size (600x400)")
    print("     └─ Yellow Text 'HELLO WORLD' at (300, 200)")
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
    renderer.save_capture("tests/output/text_test.png")
    
    data, width, height = renderer.capture_frame()
    print(f"Captured: {width}x{height}")
    
    # Analyze
    import struct
    pixels = struct.unpack(f'{len(data)}B', data)
    
    yellow_count = 0
    for i in range(0, len(pixels), 4):
        r, g, b = pixels[i+2], pixels[i+1], pixels[i]
        if r > 200 and g > 200 and b < 50:
            yellow_count += 1
    
    total = width * height
    print(f"Yellow pixels: {yellow_count:,} ({yellow_count/total*100:.2f}%)")
    
    if yellow_count > 1000:
        print("✓ Text is rendering!")
    else:
        print("✗ Text is NOT rendering")
    
    renderer.shutdown()
    return 0 if yellow_count > 1000 else 1


if __name__ == "__main__":
    sys.exit(main())
