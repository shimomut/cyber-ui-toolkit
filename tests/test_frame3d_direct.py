#!/usr/bin/env python3
"""
Test if rectangles render directly in Frame3D (not in Frame2D).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build'))

import cyber_ui_core as ui


def main():
    print("Frame3D Direct Rendering Test")
    print("=" * 70)
    
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(800, 600, "Frame3D Test"):
        print("Failed to initialize renderer")
        return 1
    
    scene = ui.SceneRoot()
    camera = scene.get_camera()
    camera.set_position(0, 0, 800)
    camera.set_perspective(1.0472, 1600.0/1200.0, 0.1, 2000.0)
    
    # Create Frame3D
    frame3d = ui.Frame3D()
    frame3d.set_position(0, 0, 0)
    scene.add_frame3d(frame3d)
    
    # Add rectangle DIRECTLY to Frame3D (not through Frame2D)
    rect = ui.Rectangle(200, 200)
    rect.set_position(0, 0)  # Center
    rect.set_color(0.0, 1.0, 0.0, 1.0)  # Bright green
    frame3d.add_child(rect)
    
    print("Scene:")
    print("  Frame3D at (0, 0, 0)")
    print("  └─ Green Rectangle at (0, 0) size (200x200)")
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
    renderer.save_capture("tests/output/frame3d_direct_test.png")
    
    data, width, height = renderer.capture_frame()
    print(f"Captured: {width}x{height}")
    
    # Analyze
    import struct
    pixels = struct.unpack(f'{len(data)}B', data)
    
    green_count = 0
    for i in range(0, len(pixels), 4):
        r, g, b = pixels[i+2], pixels[i+1], pixels[i]
        if g > 200 and r < 50 and b < 50:
            green_count += 1
    
    total = width * height
    print(f"Green pixels: {green_count:,} ({green_count/total*100:.2f}%)")
    
    if green_count > 10000:
        print("✓ Frame3D direct rendering works!")
    else:
        print("✗ Frame3D direct rendering NOT working")
    
    renderer.shutdown()
    return 0 if green_count > 10000 else 1


if __name__ == "__main__":
    sys.exit(main())
