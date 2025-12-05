#!/usr/bin/env python3
"""Test FPS limiting with V-Sync for both Metal and OpenGL backends."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build'))

import cyber_ui_core as ui
import time

def test_fps_limit(backend_name):
    """Test FPS limiting for a specific backend."""
    print(f"\n{'='*60}")
    print(f"Testing FPS limit with {backend_name} backend")
    print(f"{'='*60}\n")
    
    # Create renderer
    if backend_name == "metal":
        renderer = ui.create_metal_renderer()
    elif backend_name == "opengl":
        renderer = ui.create_opengl_renderer()
    else:
        print(f"Unknown backend: {backend_name}")
        return False
    
    if not renderer.initialize(800, 600, f"FPS Test - {backend_name}"):
        print(f"Failed to initialize {backend_name} renderer")
        return False
    
    # Create simple scene
    scene = ui.SceneRoot()
    camera = scene.get_camera()
    camera.set_position(0.0, 0.0, 800.0)
    camera.set_perspective(1.0472, 800.0/600.0, 0.1, 2000.0)
    
    # Create a simple frame with a rectangle
    frame = ui.Frame3D(800, 600)
    frame.set_position(0, 0, 0)
    
    rect = ui.Rectangle(200, 200)
    rect.set_position(300, 200)
    rect.set_color(0.2, 0.8, 0.3, 1.0)
    frame.add_child(rect)
    
    scene.add_frame3d(frame)
    
    # Run for 5 seconds and measure FPS
    start_time = time.time()
    frame_count = 0
    last_fps_time = start_time
    fps_samples = []
    
    print("Running for 5 seconds to measure FPS...")
    print("Expected: ~60 FPS with V-Sync enabled\n")
    
    while time.time() - start_time < 5.0 and not renderer.should_close():
        renderer.begin_frame()
        renderer.render_scene(scene)
        renderer.end_frame()
        renderer.poll_events()
        
        frame_count += 1
        
        # Calculate FPS every 0.5 seconds
        current_time = time.time()
        if current_time - last_fps_time >= 0.5:
            elapsed = current_time - last_fps_time
            fps = frame_count / elapsed
            fps_samples.append(fps)
            print(f"Current FPS: {fps:.2f}")
            frame_count = 0
            last_fps_time = current_time
    
    # Calculate statistics
    total_time = time.time() - start_time
    avg_fps = sum(fps_samples) / len(fps_samples) if fps_samples else 0
    min_fps = min(fps_samples) if fps_samples else 0
    max_fps = max(fps_samples) if fps_samples else 0
    
    print(f"\n{'='*60}")
    print(f"Results for {backend_name}:")
    print(f"  Average FPS: {avg_fps:.2f}")
    print(f"  Min FPS: {min_fps:.2f}")
    print(f"  Max FPS: {max_fps:.2f}")
    print(f"  Total time: {total_time:.2f}s")
    print(f"{'='*60}\n")
    
    # Check if FPS is within acceptable range (55-65 FPS)
    success = 55 <= avg_fps <= 65
    if success:
        print(f"✓ {backend_name}: FPS is properly limited to ~60 FPS")
    else:
        print(f"✗ {backend_name}: FPS is NOT properly limited (expected ~60, got {avg_fps:.2f})")
    
    renderer.shutdown()
    return success

if __name__ == "__main__":
    print("\n" + "="*60)
    print("FPS Limiting Test with V-Sync")
    print("="*60)
    
    # Check which backend is available
    has_metal = hasattr(ui, 'create_metal_renderer')
    has_opengl = hasattr(ui, 'create_opengl_renderer')
    
    print(f"\nAvailable backends:")
    print(f"  Metal:  {'✓' if has_metal else '✗'}")
    print(f"  OpenGL: {'✓' if has_opengl else '✗'}")
    
    results = {}
    
    # Test Metal backend if available
    if has_metal:
        results['metal'] = test_fps_limit("metal")
    else:
        print("\nMetal backend not available (rebuild with: make build-metal)")
    
    # Test OpenGL backend if available
    if has_opengl:
        results['opengl'] = test_fps_limit("opengl")
    else:
        print("\nOpenGL backend not available (rebuild with: make build-opengl)")
    
    # Summary
    if results:
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        for backend, success in results.items():
            print(f"{backend.capitalize():8} {'✓ PASS' if success else '✗ FAIL'}")
        print("="*60 + "\n")
        
        sys.exit(0 if all(results.values()) else 1)
    else:
        print("\nNo backends available to test!")
        sys.exit(1)
