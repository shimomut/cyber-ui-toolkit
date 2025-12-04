#!/usr/bin/env python3
"""Analyze corner marker positions"""

from PIL import Image
import numpy as np

img = Image.open('tests/output/debug_corners.png')
pixels = np.array(img)

print(f"Image size: {img.size}\n")

colors = {
    'RED (top-left)': ((200, 255), (0, 50), (0, 50)),
    'GREEN (top-right)': ((0, 50), (200, 255), (0, 50)),
    'BLUE (bottom-left)': ((0, 50), (0, 50), (200, 255)),
    'YELLOW (bottom-right)': ((200, 255), (200, 255), (0, 50)),
    'MAGENTA (center)': ((200, 255), (0, 50), (200, 255)),
}

for name, (r_range, g_range, b_range) in colors.items():
    mask = ((pixels[:,:,0] >= r_range[0]) & (pixels[:,:,0] <= r_range[1]) &
            (pixels[:,:,1] >= g_range[0]) & (pixels[:,:,1] <= g_range[1]) &
            (pixels[:,:,2] >= b_range[0]) & (pixels[:,:,2] <= b_range[1]))
    
    coords = np.where(mask)
    
    if len(coords[0]) > 0:
        top = coords[0].min()
        bottom = coords[0].max()
        left = coords[1].min()
        right = coords[1].max()
        center_x = (left + right) / 2
        center_y = (top + bottom) / 2
        
        print(f"{name}:")
        print(f"  Position: ({left}, {top}) to ({right}, {bottom})")
        print(f"  Center: ({center_x:.0f}, {center_y:.0f})")
        print()
    else:
        print(f"{name}: NOT FOUND")
        print()

# Window center
window_center_x = img.size[0] / 2
window_center_y = img.size[1] / 2
print(f"Window center: ({window_center_x}, {window_center_y})")
