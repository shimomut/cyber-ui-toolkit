#!/usr/bin/env python3
"""
Verify that all 4 borders are visible in clipping demo captures.
This checks that the scissor rect fix is working correctly.
"""

from PIL import Image
import sys
import os

def check_border_visibility(image_path):
    """Check if all 4 colored borders are visible in the image"""
    img = Image.open(image_path)
    pixels = img.load()
    width, height = img.size
    
    # Expected border colors (approximate, allowing for some variation)
    # Top: Yellow (1.0, 1.0, 0.0)
    # Bottom: Green (0.0, 1.0, 0.0)
    # Left: Cyan (0.0, 1.0, 1.0)
    # Right: Magenta (1.0, 0.0, 1.0) - but demo shows green
    
    def is_yellow(r, g, b):
        return r > 200 and g > 200 and b < 100
    
    def is_green(r, g, b):
        return r < 100 and g > 200 and b < 100
    
    def is_cyan(r, g, b):
        return r < 100 and g > 200 and b > 200
    
    # Sample pixels from each border region
    # Borders are at Frame2D position (150, 50) with size (500, 600)
    # On Retina display, multiply by 2
    scale = 2  # Retina scaling
    
    frame_x = 150 * scale
    frame_y = 50 * scale
    frame_w = 500 * scale
    frame_h = 600 * scale
    
    border_thickness = 8 * scale
    
    # Check top border (yellow)
    top_yellow_count = 0
    for x in range(frame_x + 50, frame_x + frame_w - 50, 20):
        y = frame_y + border_thickness // 2
        if 0 <= x < width and 0 <= y < height:
            r, g, b = pixels[x, y][:3]
            if is_yellow(r, g, b):
                top_yellow_count += 1
    
    # Check bottom border (green)
    bottom_green_count = 0
    for x in range(frame_x + 50, frame_x + frame_w - 50, 20):
        y = frame_y + frame_h - border_thickness // 2
        if 0 <= x < width and 0 <= y < height:
            r, g, b = pixels[x, y][:3]
            if is_green(r, g, b):
                bottom_green_count += 1
    
    # Check left border (cyan)
    left_cyan_count = 0
    for y in range(frame_y + 50, frame_y + frame_h - 50, 20):
        x = frame_x + border_thickness // 2
        if 0 <= x < width and 0 <= y < height:
            r, g, b = pixels[x, y][:3]
            if is_cyan(r, g, b):
                left_cyan_count += 1
    
    # Check right border (green)
    right_green_count = 0
    for y in range(frame_y + 50, frame_y + frame_h - 50, 20):
        x = frame_x + frame_w - border_thickness // 2
        if 0 <= x < width and 0 <= y < height:
            r, g, b = pixels[x, y][:3]
            if is_green(r, g, b):
                right_green_count += 1
    
    print(f"\nBorder visibility check for: {os.path.basename(image_path)}")
    print(f"  Top border (yellow):    {top_yellow_count} pixels")
    print(f"  Bottom border (green):  {bottom_green_count} pixels")
    print(f"  Left border (cyan):     {left_cyan_count} pixels")
    print(f"  Right border (green):   {right_green_count} pixels")
    
    # All borders should have at least some visible pixels
    all_visible = (top_yellow_count > 5 and 
                   bottom_green_count > 5 and 
                   left_cyan_count > 5 and 
                   right_green_count > 5)
    
    if all_visible:
        print("  ✓ All borders are visible!")
        return True
    else:
        print("  ✗ Some borders are missing!")
        if top_yellow_count <= 5:
            print("    - Top border (yellow) is missing or clipped")
        if bottom_green_count <= 5:
            print("    - Bottom border (green) is missing or clipped")
        if left_cyan_count <= 5:
            print("    - Left border (cyan) is missing or clipped")
        if right_green_count <= 5:
            print("    - Right border (green) is missing or clipped")
        return False

def main():
    output_dir = "samples/output"
    
    if not os.path.exists(output_dir):
        print(f"Output directory not found: {output_dir}")
        print("Run: PYTHONPATH=build python3 samples/basic/clipping_demo.py --capture")
        return 1
    
    # Check the initial capture
    initial_file = os.path.join(output_dir, "clipping_demo_initial.png")
    if not os.path.exists(initial_file):
        print(f"Initial capture not found: {initial_file}")
        return 1
    
    print("="*70)
    print("Clipping Border Visibility Test")
    print("="*70)
    
    success = check_border_visibility(initial_file)
    
    # Also check a few random frames
    frame_files = [
        "clipping_demo_frame_00120.png",
        "clipping_demo_frame_01200.png",
        "clipping_demo_final.png"
    ]
    
    for frame_file in frame_files:
        frame_path = os.path.join(output_dir, frame_file)
        if os.path.exists(frame_path):
            if not check_border_visibility(frame_path):
                success = False
    
    print("\n" + "="*70)
    if success:
        print("✓ SUCCESS: All borders are visible in all checked frames")
        print("  The scissor rect fix is working correctly!")
    else:
        print("✗ FAILURE: Some borders are missing")
        print("  The clipping boundaries are not being set correctly")
    print("="*70)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
