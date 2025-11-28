#!/usr/bin/env python3
"""
Simple demonstration of the rendering capture system.
Shows how to capture frames for debugging and analysis.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'build'))

import cyber_ui_core as ui
import time


def main():
    """Demonstrate frame capture functionality."""
    print("Cyber UI Toolkit - Capture Demo")
    print("=" * 50)
    
    # Create renderer
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(800, 600, "Capture Demo"):
        print("Failed to initialize renderer")
        return 1
    
    # Create scene
    scene = ui.SceneRoot()
    camera = ui.Camera()
    camera.set_position(0, 0, 5)
    scene.set_camera(camera)
    
    # Create 3D frame
    frame = ui.Frame3D()
    frame.set_position(0, 0, 0)
    
    # Add some colorful shapes
    colors = [
        (1.0, 0.0, 0.0, 1.0),  # Red
        (0.0, 1.0, 0.0, 1.0),  # Green
        (0.0, 0.0, 1.0, 1.0),  # Blue
        (1.0, 1.0, 0.0, 1.0),  # Yellow
    ]
    
    positions = [
        (-200, 150),
        (200, 150),
        (-200, -150),
        (200, -150),
    ]
    
    for color, pos in zip(colors, positions):
        rect = ui.Rectangle(150, 150)
        rect.set_color(*color)
        rect.set_position(*pos)
        frame.add_child(rect)
    
    scene.add_frame3d(frame)
    
    print("\nRendering scene...")
    print("Press Ctrl+C to capture and exit")
    
    # Create output directory
    os.makedirs("samples/output", exist_ok=True)
    
    frame_count = 0
    rotation = 0
    
    try:
        while not renderer.should_close():
            renderer.poll_events()
            
            # Animate rotation
            rotation += 0.5
            frame.set_rotation(0, 0, rotation * 3.14159 / 180.0)
            
            # Render
            renderer.begin_frame()
            renderer.render_scene(scene)
            renderer.end_frame()
            
            frame_count += 1
            
            # Auto-capture every 60 frames
            if frame_count % 60 == 0:
                filename = f"samples/output/capture_{frame_count:04d}.png"
                if renderer.save_capture(filename):
                    print(f"Captured frame {frame_count} -> {filename}")
            
            time.sleep(0.016)  # ~60 FPS
            
    except KeyboardInterrupt:
        print("\n\nCapturing final frame...")
        
        # Capture final frame
        final_file = "samples/output/capture_final.png"
        if renderer.save_capture(final_file):
            print(f"✓ Saved to: {final_file}")
        
        # Also demonstrate raw data capture
        print("\nCapturing raw pixel data...")
        data, width, height = renderer.capture_frame()
        
        if data is not None:
            print(f"✓ Captured {width}x{height} frame")
            print(f"  Data size: {len(data)} bytes")
            print(f"  Format: BGRA (4 bytes per pixel)")
            
            # Analyze the data
            import struct
            pixels = struct.unpack(f'{len(data)}B', data)
            
            # Calculate average color
            total_r = sum(pixels[i+2] for i in range(0, len(pixels), 4))
            total_g = sum(pixels[i+1] for i in range(0, len(pixels), 4))
            total_b = sum(pixels[i] for i in range(0, len(pixels), 4))
            
            num_pixels = width * height
            avg_r = total_r / num_pixels
            avg_g = total_g / num_pixels
            avg_b = total_b / num_pixels
            
            print(f"  Average color: R={avg_r:.1f}, G={avg_g:.1f}, B={avg_b:.1f}")
        else:
            print("✗ Failed to capture raw data")
    
    renderer.shutdown()
    
    print("\nDemo complete!")
    print(f"Total frames rendered: {frame_count}")
    print("Check samples/output/ for captured images")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
