#!/usr/bin/env python3
"""Analyze the simple clipping test output"""

from PIL import Image
import numpy as np

img = Image.open("tests/output/simple_clipping_test.png")
pixels = np.array(img)
height, width = pixels.shape[:2]

print(f"Image size: {width}x{height}")
print()

# Find colored borders
red_mask = (pixels[:,:,0] > 200) & (pixels[:,:,1] < 100) & (pixels[:,:,2] < 100)
green_mask = (pixels[:,:,0] < 100) & (pixels[:,:,1] > 200) & (pixels[:,:,2] < 100)
blue_mask = (pixels[:,:,0] < 100) & (pixels[:,:,1] < 100) & (pixels[:,:,2] > 200)
yellow_mask = (pixels[:,:,0] > 200) & (pixels[:,:,1] > 200) & (pixels[:,:,2] < 100)

print("Border colors found:")
print(f"  Red (top):    {np.sum(red_mask)} pixels")
print(f"  Green (bottom): {np.sum(green_mask)} pixels")
print(f"  Blue (left):  {np.sum(blue_mask)} pixels")
print(f"  Yellow (right): {np.sum(yellow_mask)} pixels")
print()

if np.sum(red_mask) > 0:
    rows, cols = np.where(red_mask)
    print(f"  Red at: Y={rows.min()}-{rows.max()}, X={cols.min()}-{cols.max()}")

if np.sum(green_mask) > 0:
    rows, cols = np.where(green_mask)
    print(f"  Green at: Y={rows.min()}-{rows.max()}, X={cols.min()}-{cols.max()}")

if np.sum(blue_mask) > 0:
    rows, cols = np.where(blue_mask)
    print(f"  Blue at: Y={rows.min()}-{rows.max()}, X={cols.min()}-{cols.max()}")

if np.sum(yellow_mask) > 0:
    rows, cols = np.where(yellow_mask)
    print(f"  Yellow at: Y={rows.min()}-{rows.max()}, X={cols.min()}-{cols.max()}")

print()
print("Expected (with 2x Retina, Frame2D at origin, size 400x400):")
print("  Frame2D bounds: X=0-800, Y=0-800 (in pixels)")
print("  Top border (red): Y=0-40")
print("  Bottom border (green): Y=760-800")
print("  Left border (blue): X=0-40")
print("  Right border (yellow): X=760-800")
