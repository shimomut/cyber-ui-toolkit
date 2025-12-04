#!/usr/bin/env python3
"""
Debug color values to see what's actually being rendered.
Test different alpha values to understand the blending.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build'))

import cyber_ui_core as ui
import time


def test_color(renderer, scene, color_name, r, g, b, a, position):
    """Test a specific color and return the captured result."""
    # Create new frame for this test
    frame = ui.Frame3D()
    frame.set_position(0, 0, 0)
    
    # Create rectangle with test color
    rect = ui.Rectangle(200, 200)
    rect.set_color(r, g, b, a)
    rect.set_position(position, 0)
    rect.set_name(color_name)
    frame.add_child(rect)
    
    # Update scene
    scene.clear()
    scene.add_frame3d(frame)
    
    # Render a few frames
    for i in range(5):
        renderer.poll_events()
        if renderer.should_close():
            return None
        renderer.begin_frame()
        renderer.render_scene(scene)
        renderer.end_frame()
        time.sleep(0.02)
    
    # Capture
    data, width, height = renderer.capture_frame()
    if data is None:
        return None
    
    # Analyze center pixels
    import struct
    pixels = struct.unpack(f'{len(data)}B', data)
    
    # Calculate screen position
    center_x = width // 2 + int(position)
    center_y = height // 2
    sample_size = 50
    
    samples = []
    for dy in range(-sample_size//2, sample_size//2):
        for dx in range(-sample_size//2, sample_size//2):
            px = center_x + dx
            py = center_y + dy
            if 0 <= px < width and 0 <= py < height:
                offset = (py * width + px) * 4
                b_val = pixels[offset]
                g_val = pixels[offset + 1]
                r_val = pixels[offset + 2]
                a_val = pixels[offset + 3]
                samples.append((r_val, g_val, b_val, a_val))
    
    if not samples:
        return None
    
    avg_r = sum(s[0] for s in samples) / len(samples)
    avg_g = sum(s[1] for s in samples) / len(samples)
    avg_b = sum(s[2] for s in samples) / len(samples)
    avg_a = sum(s[3] for s in samples) / len(samples)
    
    min_r = min(s[0] for s in samples)
    max_r = max(s[0] for s in samples)
    
    return {
        'input': (r, g, b, a),
        'output': (avg_r, avg_g, avg_b, avg_a),
        'variance': max_r - min_r
    }


def main():
    print("Color Value Debug Test")
    print("=" * 70)
    
    # Create renderer
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(800, 600, "Color Debug Test"):
        print("Failed to initialize renderer")
        return 1
    
    # Create scene
    scene = ui.SceneRoot()
    camera = ui.Camera()
    camera.set_position(0, 0, 5)
    scene.set_camera(camera)
    
    # Test cases: (name, r, g, b, a, x_position)
    tests = [
        ("White_A1.0", 1.0, 1.0, 1.0, 1.0, 0),
        ("White_A0.5", 1.0, 1.0, 1.0, 0.5, 0),
        ("Gray_A1.0", 0.5, 0.5, 0.5, 1.0, 0),
    ]
    
    print("\nTesting different colors and alpha values...")
    print()
    
    results = []
    for name, r, g, b, a, pos in tests:
        result = test_color(renderer, scene, name, r, g, b, a, pos)
        if result:
            results.append((name, result))
            
            inp = result['input']
            out = result['output']
            var = result['variance']
            
            print(f"{name}:")
            print(f"  Input:    ({inp[0]:.2f}, {inp[1]:.2f}, {inp[2]:.2f}, {inp[3]:.2f})")
            print(f"  Expected: ({inp[0]*255:.0f}, {inp[1]*255:.0f}, {inp[2]*255:.0f}, {inp[3]*255:.0f})")
            print(f"  Output:   ({out[0]:.0f}, {out[1]:.0f}, {out[2]:.0f}, {out[3]:.0f})")
            print(f"  Variance: {var}")
            
            # Check if output matches expected
            expected_r = inp[0] * 255
            if abs(out[0] - expected_r) < 5:
                print(f"  ✓ Color matches expected")
            else:
                print(f"  ✗ Color mismatch!")
                # Calculate what the blend formula would produce
                # If using premultiplied alpha: result = src + dst * (1 - src.a)
                # Background is (26, 26, 26)
                bg = 26
                src_premult = inp[0] * inp[3] * 255
                blended = src_premult + bg * (1 - inp[3])
                print(f"  Premult blend would give: {blended:.0f}")
                
                # If using straight alpha: result = src * src.a + dst * (1 - src.a)
                straight = inp[0] * 255 * inp[3] + bg * (1 - inp[3])
                print(f"  Straight blend would give: {straight:.0f}")
            print()
    
    # Save a capture
    os.makedirs("tests/output", exist_ok=True)
    renderer.save_capture("tests/output/color_debug_test.png")
    print("Saved: tests/output/color_debug_test.png")
    
    # Keep window open
    print("\nWindow will stay open for 3 seconds...")
    for i in range(30):
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
