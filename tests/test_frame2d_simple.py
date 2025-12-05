#!/usr/bin/env python3
"""
Simplest possible Frame2D test - just a rectangle directly in Frame2D.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build'))

import cyber_ui_core as ui


def main():
    print("Simplest Frame2D Test")
    print("=" * 70)
    
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(800, 600, "Frame2D Simple Test"):
        print("Failed to initialize renderer")
        return 1
    
    scene = ui.SceneRoot()
    camera = scene.get_camera()
    
    # Use drawable size for aspect ratio
    # On Retina: 1600x1200, aspect = 1.333
    camera.set_position(0, 0, 800)
    camera.set_perspective(1.0472, 1600.0/1200.0, 0.1, 2000.0)
    
    print("Camera: position (0, 0, 800), perspective FOV=60°, aspect=1.333")
    
    # Create Frame3D at origin
    frame3d = ui.Frame3D(800, 600)
    frame3d.set_position(0, 0, 0)
    scene.add_frame3d(frame3d)
    
    # Create Frame2D
    frame2d = ui.Frame2D(400, 400)
    frame2d.set_position(0, 0)  # Center of screen
    frame2d
    
    # Add a bright red rectangle
    rect = ui.Rectangle(200, 200)
    rect.set_position(200, 200)  # Center in Frame2D (Frame2D uses top-left origin for children)
    rect.set_color(1.0, 0.0, 0.0, 1.0)  # Bright red
    frame2d.add_child(rect)
    
    frame3d.add_child(frame2d)
    
    print("Scene:")
    print("  Frame3D at (0, 0, 0)")
    print("  └─ Frame2D at (0, 0) size (400x400)")
    print("     └─ Red Rectangle at (200, 200) size (200x200)")
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
    renderer.save_capture("tests/output/frame2d_simple_test.png")
    
    data, width, height = renderer.capture_frame()
    print(f"Captured: {width}x{height}")
    
    # Analyze
    import struct
    pixels = struct.unpack(f'{len(data)}B', data)
    
    red_count = 0
    for i in range(0, len(pixels), 4):
        r, g, b = pixels[i+2], pixels[i+1], pixels[i]
        if r > 200 and g < 50 and b < 50:
            red_count += 1
    
    total = width * height
    print(f"Red pixels: {red_count:,} ({red_count/total*100:.2f}%)")
    
    if red_count > 10000:
        print("✓ Frame2D is rendering!")
    else:
        print("✗ Frame2D is NOT rendering")
    
    renderer.shutdown()
    return 0 if red_count > 10000 else 1


if __name__ == "__main__":
    sys.exit(main())
