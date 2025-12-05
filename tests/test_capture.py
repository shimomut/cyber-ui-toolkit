#!/usr/bin/env python3
"""
Test script for rendering capture functionality.
Demonstrates how to capture rendered frames for debugging and testing.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build'))

import cyber_ui_core as ui
import time


def test_basic_capture():
    """Test basic frame capture with simple shapes."""
    print("Testing basic frame capture...")
    
    # Create renderer
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(800, 600, "Capture Test - Basic"):
        print("Failed to initialize renderer")
        return False
    
    # Create scene
    scene = ui.SceneRoot()
    camera = ui.Camera()
    camera.set_position(0, 0, 5)
    scene.set_camera(camera)
    
    # Create a 3D frame with some shapes
    frame = ui.Frame3D(800, 600)
    frame.set_position(0, 0, 0)
    
    # Add colored rectangles
    rect1 = ui.Rectangle(200, 200)
    rect1.set_color(1.0, 0.0, 0.0, 1.0)  # Red
    rect1.set_position(-150, 0)
    frame.add_child(rect1)
    
    rect2 = ui.Rectangle(200, 200)
    rect2.set_color(0.0, 1.0, 0.0, 1.0)  # Green
    rect2.set_position(150, 0)
    frame.add_child(rect2)
    
    scene.add_frame3d(frame)
    
    # Render a few frames
    for i in range(5):
        renderer.poll_events()
        if renderer.should_close():
            break
        
        renderer.begin_frame()
        renderer.render_scene(scene)
        renderer.end_frame()
        time.sleep(0.1)
    
    # Capture the frame
    print("Capturing frame...")
    success = renderer.save_capture("tests/output/capture_basic.png")
    
    if success:
        print("✓ Frame captured successfully to tests/output/capture_basic.png")
    else:
        print("✗ Failed to capture frame")
    
    renderer.shutdown()
    return success


def test_capture_with_texture():
    """Test frame capture with textured shapes."""
    print("\nTesting capture with textures...")
    
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(800, 600, "Capture Test - Texture"):
        print("Failed to initialize renderer")
        return False
    
    scene = ui.SceneRoot()
    camera = ui.Camera()
    camera.set_position(0, 0, 5)
    scene.set_camera(camera)
    
    frame = ui.Frame3D(800, 600)
    
    # Load and display an image
    image = ui.Image()
    if image.load_from_file("samples/data/checkerboard.png"):
        rect = ui.Rectangle(300, 300)
        rect.set_image(image)
        frame.add_child(rect)
    else:
        print("Warning: Could not load texture, using colored rectangle")
        rect = ui.Rectangle(300, 300)
        rect.set_color(0.0, 0.0, 1.0, 1.0)  # Blue
        frame.add_child(rect)
    
    scene.add_frame3d(frame)
    
    # Render frames
    for i in range(5):
        renderer.poll_events()
        if renderer.should_close():
            break
        
        renderer.begin_frame()
        renderer.render_scene(scene)
        renderer.end_frame()
        time.sleep(0.1)
    
    # Capture
    print("Capturing textured frame...")
    success = renderer.save_capture("tests/output/capture_texture.png")
    
    if success:
        print("✓ Textured frame captured to tests/output/capture_texture.png")
    else:
        print("✗ Failed to capture textured frame")
    
    renderer.shutdown()
    return success


def test_capture_raw_data():
    """Test capturing raw pixel data for analysis."""
    print("\nTesting raw pixel data capture...")
    
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(400, 300, "Capture Test - Raw Data"):
        print("Failed to initialize renderer")
        return False
    
    scene = ui.SceneRoot()
    camera = ui.Camera()
    camera.set_position(0, 0, 5)
    scene.set_camera(camera)
    
    frame = ui.Frame3D(800, 600)
    
    # Create a simple red square
    rect = ui.Rectangle(200, 200)
    rect.set_color(1.0, 0.0, 0.0, 1.0)
    frame.add_child(rect)
    
    scene.add_frame3d(frame)
    
    # Render
    for i in range(3):
        renderer.poll_events()
        if renderer.should_close():
            break
        
        renderer.begin_frame()
        renderer.render_scene(scene)
        renderer.end_frame()
        time.sleep(0.1)
    
    # Capture raw data
    print("Capturing raw pixel data...")
    data, width, height = renderer.capture_frame()
    
    if data is not None:
        print(f"✓ Captured {width}x{height} frame ({len(data)} bytes)")
        print(f"  Format: BGRA (4 bytes per pixel)")
        print(f"  Expected size: {width * height * 4} bytes")
        
        # Analyze some pixels
        import struct
        pixels = struct.unpack(f'{len(data)}B', data)
        
        # Sample center pixel
        center_x = width // 2
        center_y = height // 2
        center_offset = (center_y * width + center_x) * 4
        
        b = pixels[center_offset]
        g = pixels[center_offset + 1]
        r = pixels[center_offset + 2]
        a = pixels[center_offset + 3]
        
        print(f"  Center pixel (BGRA): ({b}, {g}, {r}, {a})")
        
        success = True
    else:
        print("✗ Failed to capture raw data")
        success = False
    
    renderer.shutdown()
    return success


def test_animated_capture():
    """Test capturing multiple frames from an animation."""
    print("\nTesting animated capture...")
    
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(600, 600, "Capture Test - Animation"):
        print("Failed to initialize renderer")
        return False
    
    scene = ui.SceneRoot()
    camera = ui.Camera()
    camera.set_position(0, 0, 5)
    scene.set_camera(camera)
    
    frame = ui.Frame3D(800, 600)
    
    # Create rotating rectangle
    rect = ui.Rectangle(200, 200)
    rect.set_color(1.0, 0.5, 0.0, 1.0)  # Orange
    frame.add_child(rect)
    
    scene.add_frame3d(frame)
    
    # Capture frames at different rotation angles
    angles = [0, 45, 90, 135]
    success_count = 0
    
    for i, angle in enumerate(angles):
        # Set rotation
        frame.set_rotation(0, 0, angle * 3.14159 / 180.0)
        
        # Render
        for _ in range(3):
            renderer.poll_events()
            if renderer.should_close():
                break
            
            renderer.begin_frame()
            renderer.render_scene(scene)
            renderer.end_frame()
            time.sleep(0.05)
        
        # Capture
        filename = f"tests/output/capture_anim_{i:02d}_{angle:03d}deg.png"
        if renderer.save_capture(filename):
            print(f"✓ Captured frame {i+1}/4 at {angle}° -> {filename}")
            success_count += 1
        else:
            print(f"✗ Failed to capture frame {i+1}/4")
    
    renderer.shutdown()
    return success_count == len(angles)


def main():
    """Run all capture tests."""
    print("=" * 60)
    print("Rendering Capture System Tests")
    print("=" * 60)
    
    # Create output directory
    os.makedirs("tests/output", exist_ok=True)
    
    results = []
    
    # Run tests
    results.append(("Basic Capture", test_basic_capture()))
    results.append(("Texture Capture", test_capture_with_texture()))
    results.append(("Raw Data Capture", test_capture_raw_data()))
    results.append(("Animated Capture", test_animated_capture()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
