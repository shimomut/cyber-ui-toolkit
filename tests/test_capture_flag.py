#!/usr/bin/env python3
"""
Test script to verify the --capture flag works correctly.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build'))

import cyber_ui_core as ui
import argparse


def main():
    parser = argparse.ArgumentParser(description='Test capture flag')
    parser.add_argument('--capture', action='store_true',
                        help='Enable frame capture')
    args = parser.parse_args()
    
    print("Testing capture flag functionality...")
    print(f"Capture enabled: {args.capture}")
    
    # Create renderer
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(400, 300, "Capture Flag Test"):
        print("Failed to initialize renderer")
        return 1
    
    # Create simple scene
    scene = ui.SceneRoot()
    camera = ui.Camera()
    camera.set_position(0, 0, 5)
    scene.set_camera(camera)
    
    frame = ui.Frame3D()
    rect = ui.Rectangle(200, 200)
    rect.set_color(1.0, 0.0, 0.0, 1.0)
    frame.add_child(rect)
    scene.add_frame3d(frame)
    
    # Render a few frames
    for i in range(5):
        renderer.poll_events()
        if renderer.should_close():
            break
        
        renderer.begin_frame()
        renderer.render_scene(scene)
        renderer.end_frame()
    
    # Test capture based on flag
    if args.capture:
        output_dir = "tests/output"
        os.makedirs(output_dir, exist_ok=True)
        
        filename = os.path.join(output_dir, "capture_flag_test.png")
        if renderer.save_capture(filename):
            print(f"✓ Capture successful: {filename}")
            result = 0
        else:
            print("✗ Capture failed")
            result = 1
    else:
        print("✓ Capture skipped (as expected)")
        result = 0
    
    renderer.shutdown()
    return result


if __name__ == "__main__":
    sys.exit(main())
