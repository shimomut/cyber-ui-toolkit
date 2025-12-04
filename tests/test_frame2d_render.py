#!/usr/bin/env python3
"""
Test if Frame2D renders at all with the Retina fix.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build'))

import cyber_ui_core as ui


def main():
    print("Testing Frame2D rendering...")
    
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(800, 600, "Frame2D Test"):
        print("Failed to initialize renderer")
        return 1
    
    scene = ui.SceneRoot()
    camera = scene.get_camera()
    camera.set_position(0, 0, 5)
    
    # Create Frame3D
    frame3d = ui.Frame3D()
    frame3d.set_position(0, 0, 0)
    
    # Create Frame2D with a simple white rectangle
    frame2d = ui.Frame2D()
    frame2d.set_position(0, 0)  # Center
    frame2d.set_size(400, 400)
    
    rect = ui.Rectangle(200, 200)
    rect.set_position(200, 200)  # Center in Frame2D
    rect.set_color(1.0, 1.0, 1.0, 1.0)  # White
    frame2d.add_child(rect)
    
    frame3d.add_child(frame2d)
    scene.add_frame3d(frame3d)
    
    print("Scene created:")
    print("  Frame3D at (0, 0, 0)")
    print("  Frame2D at (0, 0) size (400x400)")
    print("  White rectangle at (200, 200) size (200x200)")
    print()
    
    # Render
    for i in range(5):
        renderer.poll_events()
        if renderer.should_close():
            break
        renderer.begin_frame()
        renderer.render_scene(scene)
        renderer.end_frame()
    
    # Capture
    data, width, height = renderer.capture_frame()
    if data is None:
        print("Failed to capture frame")
        renderer.shutdown()
        return 1
    
    os.makedirs("tests/output", exist_ok=True)
    renderer.save_capture("tests/output/frame2d_test.png")
    print(f"Saved: tests/output/frame2d_test.png ({width}x{height})")
    
    # Analyze
    import struct
    pixels = struct.unpack(f'{len(data)}B', data)
    
    # Count white pixels
    white_count = 0
    bg_count = 0
    other_count = 0
    
    for i in range(0, len(pixels), 4):
        r, g, b, a = pixels[i+2], pixels[i+1], pixels[i], pixels[i+3]
        if r > 250 and g > 250 and b > 250:
            white_count += 1
        elif r < 30 and g < 30 and b < 30:
            bg_count += 1
        else:
            other_count += 1
    
    total = width * height
    print()
    print(f"Pixel analysis:")
    print(f"  White pixels: {white_count:,} ({white_count/total*100:.2f}%)")
    print(f"  Background:   {bg_count:,} ({bg_count/total*100:.2f}%)")
    print(f"  Other:        {other_count:,} ({other_count/total*100:.2f}%)")
    print()
    
    # Expected: 200x200 rectangle at 2x scale = 400x400 pixels = 160,000 pixels
    # In 1600x1200 image = 13.3%
    expected_pct = 160000 / total * 100
    
    if white_count > 100000:
        print(f"✓ Frame2D is rendering! ({white_count:,} white pixels)")
        print(f"  Expected ~{expected_pct:.1f}%, got {white_count/total*100:.1f}%")
        success = True
    else:
        print(f"✗ Frame2D is NOT rendering properly")
        print(f"  Expected ~{expected_pct:.1f}%, got only {white_count/total*100:.1f}%")
        success = False
    
    renderer.shutdown()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
