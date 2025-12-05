#!/usr/bin/env python3
"""
Debug aspect ratio - check if rectangles are being squashed.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build'))

import cyber_ui_core as ui
from PIL import Image as PILImage
import numpy as np


def test_square(name, use_frame2d=False):
    """Test if a square renders as a square."""
    print(f"\n{name}")
    print("=" * 70)
    
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(800, 700, f"Aspect Test - {name}"):
        return None
    
    scene = ui.SceneRoot()
    camera = scene.get_camera()
    camera.set_position(0, 0, 800)
    camera.set_perspective(1.0472, 1600.0/1400.0, 0.1, 2000.0)
    
    frame3d = ui.Frame3D(800, 600)
    frame3d.set_position(0, 0, 0)
    scene.add_frame3d(frame3d)
    
    if use_frame2d:
        # Test with Frame2D - use EXACT same parameters as debug_frame2d_size.py
        frame2d = ui.Frame2D(500, 600)
        frame2d.set_position(150, 50)  # Same as original test
        frame2d      # Same as original test
        
        # Fill entire Frame2D with rectangle
        rect = ui.Rectangle(500, 600)
        rect.set_position(0, 0)
        rect.set_color(1.0, 0.0, 0.0, 1.0)
        frame2d.add_child(rect)
        
        frame3d.add_child(frame2d)
        print("  500x600 rectangle in Frame2D at (150, 50)")
    else:
        # Test directly in Frame3D
        rect = ui.Rectangle(500, 500)
        rect.set_position(0, 0)
        rect.set_color(1.0, 0.0, 0.0, 1.0)
        frame3d.add_child(rect)
        print("  500x500 square directly in Frame3D")
    
    # Render
    for i in range(5):
        renderer.poll_events()
        if renderer.should_close():
            break
        renderer.begin_frame()
        renderer.render_scene(scene)
        renderer.end_frame()
    
    # Capture
    os.makedirs("tests/output", exist_ok=True)
    filename = f"tests/output/aspect_{name.replace(' ', '_')}.png"
    renderer.save_capture(filename)
    
    # Analyze
    img = PILImage.open(filename)
    pixels = np.array(img)
    red_mask = (pixels[:, :, 0] > 200) & (pixels[:, :, 1] < 50) & (pixels[:, :, 2] < 50)
    
    if np.any(red_mask):
        red_rows = np.any(red_mask, axis=1)
        red_cols = np.any(red_mask, axis=0)
        top = np.argmax(red_rows)
        bottom = len(red_rows) - np.argmax(red_rows[::-1]) - 1
        left = np.argmax(red_cols)
        right = len(red_cols) - np.argmax(red_cols[::-1]) - 1
        
        width_px = right - left + 1
        height_px = bottom - top + 1
        
        width_logical = width_px / 2
        height_logical = height_px / 2
        
        aspect_ratio = width_logical / height_logical
        
        print(f"  Rendered size: {width_logical:.1f} x {height_logical:.1f} logical pixels")
        print(f"  Aspect ratio: {aspect_ratio:.3f} (expected: 1.000 for square)")
        
        if abs(aspect_ratio - 1.0) < 0.05:
            print(f"  ✓ Square is rendering correctly")
        else:
            if aspect_ratio < 1.0:
                print(f"  ✗ Square is SQUASHED horizontally ({1/aspect_ratio:.2f}x)")
            else:
                print(f"  ✗ Square is STRETCHED horizontally ({aspect_ratio:.2f}x)")
        
        renderer.shutdown()
        return aspect_ratio
    else:
        print("  ✗ No pixels rendered")
        renderer.shutdown()
        return None


def main():
    print("Aspect Ratio Debug")
    print("Testing if squares render as squares...")
    
    # Test 1: Direct in Frame3D (baseline)
    ratio1 = test_square("Direct_Frame3D", use_frame2d=False)
    
    # Test 2: Inside Frame2D
    ratio2 = test_square("Inside_Frame2D", use_frame2d=True)
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if ratio1 and ratio2:
        print(f"Direct Frame3D aspect ratio: {ratio1:.3f}")
        print(f"Inside Frame2D aspect ratio: {ratio2:.3f}")
        print()
        
        if abs(ratio1 - 1.0) < 0.05 and abs(ratio2 - 1.0) > 0.05:
            print("✗ Frame2D is causing aspect ratio distortion!")
            print(f"  Frame2D squashes width by {1/ratio2:.2f}x")
        elif abs(ratio1 - 1.0) > 0.05:
            print("✗ Base rendering has aspect ratio issues")
        else:
            print("✓ Both render correctly")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
