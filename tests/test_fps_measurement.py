#!/usr/bin/env python3
"""Test FPS measurement functionality."""

import sys
sys.path.insert(0, 'build')

import cyber_ui_core as ui
import time

def test_fps_opengl():
    """Test FPS measurement with OpenGL renderer."""
    print("Testing FPS measurement with OpenGL renderer...")
    
    renderer = ui.create_opengl_renderer()
    renderer.initialize(800, 600, "FPS Test - OpenGL")
    
    # Create simple scene
    rect = ui.Rectangle(100, 100)
    rect.set_position(350, 250)
    rect.set_color(1.0, 0.5, 0.0, 1.0)
    
    # Run for a short time
    frame_count = 0
    max_frames = 120  # Run for ~2 seconds at 60 FPS
    
    while not renderer.should_close() and frame_count < max_frames:
        renderer.begin_frame()
        renderer.render_object(root)
        renderer.end_frame()
        renderer.poll_events()
        frame_count += 1
    
    # Get FPS before shutdown
    fps = renderer.get_fps()
    total_frames = renderer.get_frame_count()
    
    print(f"Current FPS: {fps:.2f}")
    print(f"Total frames rendered: {total_frames}")
    
    # Shutdown will print final statistics
    renderer.shutdown()
    
    print("✓ OpenGL FPS test completed\n")

def test_fps_metal():
    """Test FPS measurement with Metal renderer."""
    print("Testing FPS measurement with Metal renderer...")
    
    renderer = ui.create_metal_renderer()
    renderer.initialize(800, 600, "FPS Test - Metal")
    
    # Create simple scene
    rect = ui.Rectangle(100, 100)
    rect.set_position(350, 250)
    rect.set_color(0.0, 0.5, 1.0, 1.0)
    
    # Run for a short time
    frame_count = 0
    max_frames = 120  # Run for ~2 seconds at 60 FPS
    
    while not renderer.should_close() and frame_count < max_frames:
        renderer.begin_frame()
        renderer.render_object(rect)
        renderer.end_frame()
        renderer.poll_events()
        frame_count += 1
    
    # Get FPS before shutdown
    fps = renderer.get_fps()
    total_frames = renderer.get_frame_count()
    
    print(f"Current FPS: {fps:.2f}")
    print(f"Total frames rendered: {total_frames}")
    
    # Shutdown will print final statistics
    renderer.shutdown()
    
    print("✓ Metal FPS test completed\n")

if __name__ == "__main__":
    print("=== FPS Measurement Test ===\n")
    
    # Test Metal renderer (OpenGL not available on this build)
    test_fps_metal()
    
    print("=== All FPS tests completed ===")
