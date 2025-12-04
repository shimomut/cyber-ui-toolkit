#!/usr/bin/env python3
"""
Simplest possible rendering test to isolate the issue.
Just render a single white rectangle on black background.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build'))

import cyber_ui_core as ui
import time


def main():
    print("Simple Render Debug Test")
    print("=" * 70)
    
    # Create renderer with BLACK background
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(800, 600, "Simple Render Test"):
        print("Failed to initialize renderer")
        return 1
    
    # Create scene
    scene = ui.SceneRoot()
    camera = ui.Camera()
    camera.set_position(0, 0, 5)
    scene.set_camera(camera)
    
    # Create a single white rectangle
    frame = ui.Frame3D()
    frame.set_position(0, 0, 0)
    
    rect = ui.Rectangle(400, 400)
    rect.set_color(1.0, 1.0, 1.0, 1.0)  # Pure white
    rect.set_position(0, 0)
    rect.set_name("WhiteRect")
    frame.add_child(rect)
    
    scene.add_frame3d(frame)
    
    print("Rendering white rectangle on black background...")
    
    # Render several frames
    for i in range(10):
        renderer.poll_events()
        if renderer.should_close():
            renderer.shutdown()
            return 0
        
        renderer.begin_frame()
        renderer.render_scene(scene)
        renderer.end_frame()
        time.sleep(0.05)
    
    # Capture
    print("Capturing frame...")
    renderer.poll_events()
    renderer.begin_frame()
    renderer.render_scene(scene)
    renderer.end_frame()
    
    data, width, height = renderer.capture_frame()
    if data is None:
        print("Failed to capture frame")
        renderer.shutdown()
        return 1
    
    # Save
    os.makedirs("tests/output", exist_ok=True)
    filename = "tests/output/simple_render_test.png"
    renderer.save_capture(filename)
    print(f"Saved: {filename}")
    
    # Analyze center pixels
    import struct
    pixels = struct.unpack(f'{len(data)}B', data)
    
    # Sample center 100x100 region
    center_x = width // 2
    center_y = height // 2
    sample_size = 100
    
    samples = []
    for dy in range(-sample_size//2, sample_size//2):
        for dx in range(-sample_size//2, sample_size//2):
            px = center_x + dx
            py = center_y + dy
            offset = (py * width + px) * 4
            b = pixels[offset]
            g = pixels[offset + 1]
            r = pixels[offset + 2]
            a = pixels[offset + 3]
            samples.append((r, g, b, a))
    
    # Statistics
    avg_r = sum(s[0] for s in samples) / len(samples)
    avg_g = sum(s[1] for s in samples) / len(samples)
    avg_b = sum(s[2] for s in samples) / len(samples)
    avg_a = sum(s[3] for s in samples) / len(samples)
    
    min_r = min(s[0] for s in samples)
    max_r = max(s[0] for s in samples)
    min_g = min(s[1] for s in samples)
    max_g = max(s[1] for s in samples)
    min_b = min(s[2] for s in samples)
    max_b = max(s[2] for s in samples)
    
    print("\nCenter Region Analysis (100x100 pixels):")
    print(f"  Average RGBA: ({avg_r:.2f}, {avg_g:.2f}, {avg_b:.2f}, {avg_a:.2f})")
    print(f"  R range: {min_r}-{max_r} (span: {max_r-min_r})")
    print(f"  G range: {min_g}-{max_g} (span: {max_g-min_g})")
    print(f"  B range: {min_b}-{max_b} (span: {max_b-min_b})")
    print()
    
    # Expected: white rectangle should be (255, 255, 255, 255)
    if avg_r > 250 and avg_g > 250 and avg_b > 250:
        print("✓ Rectangle is rendering as white")
    else:
        print("✗ Rectangle is NOT white!")
        print(f"  Expected: ~(255, 255, 255)")
        print(f"  Got:      ({avg_r:.0f}, {avg_g:.0f}, {avg_b:.0f})")
    
    if max_r - min_r < 5 and max_g - min_g < 5 and max_b - min_b < 5:
        print("✓ Pixels are consistent (low variance)")
    else:
        print("✗ High pixel variance detected!")
        print("  This indicates rendering corruption or blending issues")
    
    # Keep window open
    print("\nWindow will stay open for 5 seconds...")
    for i in range(50):
        renderer.poll_events()
        if renderer.should_close():
            break
        renderer.begin_frame()
        renderer.render_scene(scene)
        renderer.end_frame()
        time.sleep(0.1)
    
    renderer.shutdown()
    print("Test complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
