#!/usr/bin/env python3
"""
Analyze the clipping test result image to verify clipping is working correctly.
"""

from PIL import Image
import numpy as np
import sys
import os

def analyze_image(image_path):
    """Analyze the clipping test image"""
    
    print(f"Analyzing: {image_path}\n")
    
    # Load image
    img = Image.open(image_path)
    pixels = np.array(img)
    height, width = pixels.shape[:2]
    
    print(f"Image size: {width}x{height}")
    
    # Calculate clipping region (accounting for retina display)
    scale = width / 800
    clip_x = int(150 * scale)
    clip_y = int(50 * scale)
    clip_w = int(500 * scale)
    clip_h = int(600 * scale)
    
    print(f"Clipping region: ({clip_x}, {clip_y}) size ({clip_w}x{clip_h})")
    print(f"Scale factor: {scale}x\n")
    
    # Define regions
    inside = pixels[clip_y:clip_y+clip_h, clip_x:clip_x+clip_w]
    
    # Outside regions with margins to avoid edge artifacts
    margin = 10
    top = pixels[0:clip_y-margin, :] if clip_y > margin else None
    bottom = pixels[clip_y+clip_h+margin:, :] if clip_y+clip_h+margin < height else None
    left = pixels[:, 0:clip_x-margin] if clip_x > margin else None
    right = pixels[:, clip_x+clip_w+margin:] if clip_x+clip_w+margin < width else None
    
    # Background color (dark gray from renderer clear color)
    bg_color = np.array([26, 26, 26])  # RGB for 0.1, 0.1, 0.1
    bg_threshold = 30
    
    def count_non_background(region):
        """Count pixels that are significantly different from background"""
        if region is None or region.size == 0:
            return 0, 0
        
        # Calculate color distance from background
        diff = np.abs(region[:, :, :3].astype(int) - bg_color)
        non_bg_mask = np.any(diff > bg_threshold, axis=2)
        non_bg_count = np.sum(non_bg_mask)
        total_count = region.shape[0] * region.shape[1]
        
        return non_bg_count, total_count
    
    # Analyze each region
    results = {}
    
    inside_non_bg, inside_total = count_non_background(inside)
    results['inside'] = {
        'non_bg': inside_non_bg,
        'total': inside_total,
        'percentage': (inside_non_bg / inside_total * 100) if inside_total > 0 else 0
    }
    
    regions = [
        ('top', top),
        ('bottom', bottom),
        ('left', left),
        ('right', right)
    ]
    
    total_outside_non_bg = 0
    total_outside_pixels = 0
    
    for name, region in regions:
        non_bg, total = count_non_background(region)
        if total > 0:
            results[name] = {
                'non_bg': non_bg,
                'total': total,
                'percentage': (non_bg / total * 100)
            }
            total_outside_non_bg += non_bg
            total_outside_pixels += total
    
    results['outside_total'] = {
        'non_bg': total_outside_non_bg,
        'total': total_outside_pixels,
        'percentage': (total_outside_non_bg / total_outside_pixels * 100) if total_outside_pixels > 0 else 0
    }
    
    # Print results
    print("="*70)
    print("ANALYSIS RESULTS")
    print("="*70)
    
    print(f"\nINSIDE clipping region:")
    print(f"  Total pixels: {results['inside']['total']:,}")
    print(f"  Non-background: {results['inside']['non_bg']:,}")
    print(f"  Percentage: {results['inside']['percentage']:.2f}%")
    
    print(f"\nOUTSIDE clipping region (combined):")
    print(f"  Total pixels: {results['outside_total']['total']:,}")
    print(f"  Non-background: {results['outside_total']['non_bg']:,}")
    print(f"  Percentage: {results['outside_total']['percentage']:.2f}%")
    
    print(f"\nOUTSIDE regions breakdown:")
    for name in ['top', 'bottom', 'left', 'right']:
        if name in results:
            r = results[name]
            print(f"  {name.upper():8s}: {r['non_bg']:6,} / {r['total']:8,} pixels ({r['percentage']:5.2f}%)")
    
    print("\n" + "="*70)
    print("VERIFICATION")
    print("="*70)
    
    # Verify results
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Inside region should have content (at least 5%)
    tests_total += 1
    if results['inside']['percentage'] >= 5:
        print(f"✓ PASS: Inside region has content ({results['inside']['percentage']:.1f}%)")
        tests_passed += 1
    else:
        print(f"✗ FAIL: Inside region has too little content ({results['inside']['percentage']:.1f}%)")
    
    # Test 2: Outside region should be mostly background (less than 2%)
    tests_total += 1
    if results['outside_total']['percentage'] < 2:
        print(f"✓ PASS: Outside region is mostly background ({results['outside_total']['percentage']:.2f}%)")
        tests_passed += 1
    else:
        print(f"✗ FAIL: Outside region has too much content ({results['outside_total']['percentage']:.2f}%)")
        print("       This indicates clipping is NOT working correctly!")
    
    # Test 3: Each outside region should be mostly background
    for name in ['top', 'bottom', 'left', 'right']:
        if name in results:
            tests_total += 1
            if results[name]['percentage'] < 2:
                print(f"✓ PASS: {name.upper()} region is clean ({results[name]['percentage']:.2f}%)")
                tests_passed += 1
            else:
                print(f"✗ FAIL: {name.upper()} region has content ({results[name]['percentage']:.2f}%)")
    
    print("\n" + "="*70)
    if tests_passed == tests_total:
        print(f"✓ ALL {tests_total} TESTS PASSED - Clipping is working correctly!")
        print("="*70)
        return True
    else:
        print(f"✗ {tests_total - tests_passed}/{tests_total} TESTS FAILED")
        print("="*70)
        return False

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, "output", "clipping_visual_test.png")
    
    if not os.path.exists(image_path):
        print(f"Error: Image not found: {image_path}")
        print("Run verify_clipping_visual.py first to generate the test image")
        return False
    
    return analyze_image(image_path)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
