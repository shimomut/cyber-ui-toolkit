#!/usr/bin/env python3
"""
Analyze the pixel distribution in the simple render test.
Count how many pixels are white vs background.
"""

from PIL import Image
import sys

def main():
    img = Image.open("tests/output/simple_render_test.png")
    pixels = img.load()
    width, height = img.size
    
    print(f"Image size: {width}x{height}")
    print()
    
    # Count pixels by color
    color_counts = {}
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            color = (r, g, b)
            color_counts[color] = color_counts.get(color, 0) + 1
    
    # Sort by count
    sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
    
    print("Top 10 colors:")
    total_pixels = width * height
    for i, (color, count) in enumerate(sorted_colors[:10]):
        pct = count / total_pixels * 100
        print(f"  {i+1}. RGB{color}: {count:6d} pixels ({pct:5.2f}%)")
    
    # Check for white and background
    white_count = color_counts.get((255, 255, 255), 0)
    bg_count = color_counts.get((26, 26, 26), 0)
    
    print()
    print(f"White (255,255,255): {white_count} pixels ({white_count/total_pixels*100:.2f}%)")
    print(f"Background (26,26,26): {bg_count} pixels ({bg_count/total_pixels*100:.2f}%)")
    print()
    
    # Expected: 400x400 rectangle in 800x600 window
    # Rectangle should be 400*400 = 160,000 pixels
    # Background should be 800*600 - 160,000 = 320,000 pixels
    expected_rect = 400 * 400
    expected_bg = total_pixels - expected_rect
    
    print(f"Expected rectangle: {expected_rect} pixels ({expected_rect/total_pixels*100:.2f}%)")
    print(f"Expected background: {expected_bg} pixels ({expected_bg/total_pixels*100:.2f}%)")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
