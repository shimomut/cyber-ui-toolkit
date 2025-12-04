#!/usr/bin/env python3
"""Analyze panel_bg position in captured image"""

from PIL import Image
import numpy as np

img = Image.open('tests/output/debug_panel_bg.png')
pixels = np.array(img)

print(f"Image size: {img.size}")
print()

# Find red pixels (panel_bg)
red_mask = (pixels[:,:,0] > 200) & (pixels[:,:,1] < 50) & (pixels[:,:,2] < 50)
red_coords = np.where(red_mask)

if len(red_coords[0]) > 0:
    red_top = red_coords[0].min()
    red_bottom = red_coords[0].max()
    red_left = red_coords[1].min()
    red_right = red_coords[1].max()
    
    print(f"Red rectangle (panel_bg):")
    print(f"  Top: {red_top}, Bottom: {red_bottom}")
    print(f"  Left: {red_left}, Right: {red_right}")
    print(f"  Size: {red_right - red_left + 1} x {red_bottom - red_top + 1}")
    print(f"  Center: ({(red_left + red_right) / 2:.1f}, {(red_top + red_bottom) / 2:.1f})")
    print()

# Find green pixels (center_marker)
green_mask = (pixels[:,:,0] < 50) & (pixels[:,:,1] > 200) & (pixels[:,:,2] < 50)
green_coords = np.where(green_mask)

if len(green_coords[0]) > 0:
    green_top = green_coords[0].min()
    green_bottom = green_coords[0].max()
    green_left = green_coords[1].min()
    green_right = green_coords[1].max()
    
    print(f"Green marker (center_marker):")
    print(f"  Top: {green_top}, Bottom: {green_bottom}")
    print(f"  Left: {green_left}, Right: {green_right}")
    print(f"  Size: {green_right - green_left + 1} x {green_bottom - green_top + 1}")
    print(f"  Center: ({(green_left + green_right) / 2:.1f}, {(green_top + green_bottom) / 2:.1f})")
    print()

# Window center
window_center_x = img.size[0] / 2
window_center_y = img.size[1] / 2
print(f"Window center: ({window_center_x}, {window_center_y})")
print()

# Check if red is at window center
if len(red_coords[0]) > 0:
    red_center_x = (red_left + red_right) / 2
    red_center_y = (red_top + red_bottom) / 2
    
    if abs(red_center_x - window_center_x) < 50 and abs(red_center_y - window_center_y) < 50:
        print("⚠️  RED RECTANGLE IS AT WINDOW CENTER - This is the bug!")
        print("    Expected: Red should be offset from center")
    else:
        print("✓ Red rectangle is NOT at window center")
