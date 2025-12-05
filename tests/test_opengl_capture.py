#!/usr/bin/env python3
"""
Test OpenGL rendering by capturing a frame and checking pixel colors.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build'))

import cyber_ui_core as ui

print("Testing OpenGL rendering with frame capture...")

# Create renderer
renderer = ui.create_opengl_renderer()

# Initialize
if not renderer.initialize(600, 600, "OpenGL Capture Test"):
    print("ERROR: Failed to initialize renderer!")
    sys.exit(1)

# Create red rectangle at (100, 100) with size 400x400
rect = ui.Rectangle(400, 400)
rect.set_position(100, 100)
rect.set_color(1.0, 0.0, 0.0, 1.0)  # Bright red

# Render one frame
if not renderer.begin_frame():
    print("ERROR: Failed to begin frame")
    sys.exit(1)

renderer.render_object(rect)

# Capture BEFORE end_frame (before buffer swap)
print("Capturing frame before buffer swap...")
result = renderer.capture_frame()

renderer.end_frame()
if result[0] is None:
    print("ERROR: Failed to capture frame")
    sys.exit(1)

pixel_data, width, height = result
print(f"Captured frame: {width}x{height}, {len(pixel_data)} bytes")

# Convert bytes to list for easier access
pixels = list(pixel_data)

# Check a pixel in the center of the rectangle (300, 300)
# Accounting for Retina scaling
scale = width // 600
center_x = 300 * scale
center_y = 300 * scale
pixel_index = (center_y * width + center_x) * 4

r = pixels[pixel_index]
g = pixels[pixel_index + 1]
b = pixels[pixel_index + 2]
a = pixels[pixel_index + 3]

print(f"\nPixel at center of rectangle ({center_x}, {center_y}):")
print(f"  RGBA: ({r}, {g}, {b}, {a})")

# Check if it's red (R should be high, G and B should be low)
if r > 200 and g < 50 and b < 50:
    print("  ✓ RED pixel detected - rectangle is rendering correctly!")
    success = True
else:
    print("  ✗ Expected red pixel but got different color")
    success = False
    
    # Search for red pixels to see where the rectangle actually is
    print("\nSearching for red pixels (sampling every 10 pixels)...")
    red_pixels = []
    for y in range(0, height, scale * 10):
        for x in range(0, width, scale * 10):
            idx = (y * width + x) * 4
            if pixels[idx] > 200 and pixels[idx+1] < 50 and pixels[idx+2] < 50:
                red_pixels.append((x//scale, y//scale))
    
    if red_pixels:
        print(f"  Found {len(red_pixels)} red pixels")
        print(f"  First red pixel: {red_pixels[0]}")
        print(f"  Last red pixel: {red_pixels[-1]}")
        # Calculate bounding box
        min_x = min(p[0] for p in red_pixels)
        max_x = max(p[0] for p in red_pixels)
        min_y = min(p[1] for p in red_pixels)
        max_y = max(p[1] for p in red_pixels)
        print(f"  Bounding box: ({min_x},{min_y}) to ({max_x},{max_y})")
        print(f"  Expected: (100,100) to (500,500)")
        
        # Check exact corners
        corners_to_check = [(100, 100), (499, 100), (100, 499), (499, 499)]
        print("\n  Checking exact corners:")
        for cx, cy in corners_to_check:
            cidx = (cy * scale * width + cx * scale) * 4
            cr = pixels[cidx]
            is_red = cr > 200 and pixels[cidx+1] < 50 and pixels[cidx+2] < 50
            print(f"    ({cx},{cy}): {'RED' if is_red else 'NOT RED'}")
    else:
        print("  No red pixels found in frame!")

# Check a pixel outside the rectangle (50, 50) - should be background
bg_x = 50 * scale
bg_y = 50 * scale
bg_index = (bg_y * width + bg_x) * 4

bg_r = pixels[bg_index]
bg_g = pixels[bg_index + 1]
bg_b = pixels[bg_index + 2]

print(f"\nPixel outside rectangle ({bg_x}, {bg_y}):")
print(f"  RGB: ({bg_r}, {bg_g}, {bg_b})")

if bg_r < 100 and bg_g < 100 and bg_b < 150:
    print("  ✓ Background color detected")
else:
    print("  ✗ Unexpected background color")
    success = False

renderer.shutdown()

if success:
    print("\n✓ OpenGL rendering test PASSED!")
    sys.exit(0)
else:
    print("\n✗ OpenGL rendering test FAILED!")
    sys.exit(1)
