#!/usr/bin/env python3
"""
Analyze a clipping demo capture to understand the actual layout.
"""

from PIL import Image
import numpy as np

def analyze_image(image_path):
    img = Image.open(image_path)
    pixels = np.array(img)
    height, width = pixels.shape[:2]
    
    print(f"Image size: {width}x{height}")
    print(f"Expected Retina scale: 2x")
    print(f"Expected drawable size: {width}x{height}")
    print()
    
    # Find non-background pixels
    # Background is dark (0.1, 0.1, 0.1) = (25, 25, 25)
    background_threshold = 50
    non_bg_mask = (pixels[:,:,0] > background_threshold) | \
                  (pixels[:,:,1] > background_threshold) | \
                  (pixels[:,:,2] > background_threshold)
    
    # Find bounding box of non-background content
    rows = np.any(non_bg_mask, axis=1)
    cols = np.any(non_bg_mask, axis=0)
    
    if np.any(rows) and np.any(cols):
        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]
        
        print(f"Content bounding box:")
        print(f"  X: {cmin} to {cmax} (width: {cmax-cmin+1})")
        print(f"  Y: {rmin} to {rmax} (height: {rmax-rmin+1})")
        print()
        
        # Expected Frame2D position and size (with Retina scaling)
        expected_x = 150 * 2
        expected_y = 50 * 2
        expected_w = 500 * 2
        expected_h = 600 * 2
        
        print(f"Expected Frame2D (with 2x Retina):")
        print(f"  Position: ({expected_x}, {expected_y})")
        print(f"  Size: {expected_w}x{expected_h}")
        print(f"  Bounds: X={expected_x} to {expected_x+expected_w}, Y={expected_y} to {expected_y+expected_h}")
        print()
        
        # Check for specific colors
        # Yellow: (255, 255, 0)
        # Green: (0, 255, 0)
        # Cyan: (0, 255, 255)
        
        yellow_mask = (pixels[:,:,0] > 200) & (pixels[:,:,1] > 200) & (pixels[:,:,2] < 100)
        green_mask = (pixels[:,:,0] < 100) & (pixels[:,:,1] > 200) & (pixels[:,:,2] < 100)
        cyan_mask = (pixels[:,:,0] < 100) & (pixels[:,:,1] > 200) & (pixels[:,:,2] > 200)
        
        yellow_count = np.sum(yellow_mask)
        green_count = np.sum(green_mask)
        cyan_count = np.sum(cyan_mask)
        
        print(f"Border color pixel counts:")
        print(f"  Yellow pixels: {yellow_count}")
        print(f"  Green pixels: {green_count}")
        print(f"  Cyan pixels: {cyan_count}")
        print()
        
        if yellow_count > 0:
            yellow_rows, yellow_cols = np.where(yellow_mask)
            print(f"  Yellow found at: Y={yellow_rows.min()}-{yellow_rows.max()}, X={yellow_cols.min()}-{yellow_cols.max()}")
        
        if green_count > 0:
            green_rows, green_cols = np.where(green_mask)
            print(f"  Green found at: Y={green_rows.min()}-{green_rows.max()}, X={green_cols.min()}-{green_cols.max()}")
        
        if cyan_count > 0:
            cyan_rows, cyan_cols = np.where(cyan_mask)
            print(f"  Cyan found at: Y={cyan_rows.min()}-{cyan_rows.max()}, X={cyan_cols.min()}-{cyan_cols.max()}")
        
        # Sample some pixels at expected border locations
        print(f"\nSampling pixels at expected border locations:")
        
        # Top border center
        sample_x = expected_x + expected_w // 2
        sample_y = expected_y + 8
        if 0 <= sample_x < width and 0 <= sample_y < height:
            r, g, b = pixels[sample_y, sample_x, :3]
            print(f"  Top border center ({sample_x}, {sample_y}): RGB({r}, {g}, {b})")
        
        # Bottom border center
        sample_y = expected_y + expected_h - 8
        if 0 <= sample_x < width and 0 <= sample_y < height:
            r, g, b = pixels[sample_y, sample_x, :3]
            print(f"  Bottom border center ({sample_x}, {sample_y}): RGB({r}, {g}, {b})")
        
        # Left border center
        sample_x = expected_x + 8
        sample_y = expected_y + expected_h // 2
        if 0 <= sample_x < width and 0 <= sample_y < height:
            r, g, b = pixels[sample_y, sample_x, :3]
            print(f"  Left border center ({sample_x}, {sample_y}): RGB({r}, {g}, {b})")
        
        # Right border center
        sample_x = expected_x + expected_w - 8
        if 0 <= sample_x < width and 0 <= sample_y < height:
            r, g, b = pixels[sample_y, sample_x, :3]
            print(f"  Right border center ({sample_x}, {sample_y}): RGB({r}, {g}, {b})")

if __name__ == "__main__":
    analyze_image("samples/output/clipping_demo_initial.png")
