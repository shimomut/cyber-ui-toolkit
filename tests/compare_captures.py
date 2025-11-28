#!/usr/bin/env python3
"""
Utility for comparing captured rendering frames.
Useful for regression testing and debugging rendering issues.
"""

import sys
import os
from pathlib import Path


def load_image(filepath):
    """Load an image file and return pixel data."""
    try:
        from PIL import Image
        img = Image.open(filepath)
        return img, img.tobytes(), img.size
    except ImportError:
        print("Error: PIL/Pillow not installed. Install with: pip install Pillow")
        return None, None, None
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None, None, None


def compare_images(img1_path, img2_path, threshold=0):
    """
    Compare two images pixel by pixel.
    
    Args:
        img1_path: Path to first image
        img2_path: Path to second image
        threshold: Maximum allowed difference per pixel (0-255)
    
    Returns:
        dict with comparison results
    """
    img1, data1, size1 = load_image(img1_path)
    img2, data2, size2 = load_image(img2_path)
    
    if data1 is None or data2 is None:
        return None
    
    # Check dimensions
    if size1 != size2:
        return {
            'identical': False,
            'size_match': False,
            'size1': size1,
            'size2': size2,
            'error': 'Image dimensions do not match'
        }
    
    width, height = size1
    
    # Convert to lists for comparison
    pixels1 = list(data1)
    pixels2 = list(data2)
    
    if len(pixels1) != len(pixels2):
        return {
            'identical': False,
            'size_match': True,
            'error': 'Pixel data length mismatch'
        }
    
    # Compare pixels
    total_pixels = width * height
    channels = len(pixels1) // total_pixels
    different_pixels = 0
    max_diff = 0
    total_diff = 0
    
    for i in range(0, len(pixels1), channels):
        pixel_diff = 0
        for c in range(min(channels, 3)):  # Compare RGB only
            diff = abs(pixels1[i + c] - pixels2[i + c])
            pixel_diff = max(pixel_diff, diff)
            total_diff += diff
        
        if pixel_diff > threshold:
            different_pixels += 1
        
        max_diff = max(max_diff, pixel_diff)
    
    avg_diff = total_diff / (total_pixels * min(channels, 3))
    diff_percentage = (different_pixels / total_pixels) * 100
    
    return {
        'identical': different_pixels == 0,
        'size_match': True,
        'dimensions': size1,
        'total_pixels': total_pixels,
        'different_pixels': different_pixels,
        'diff_percentage': diff_percentage,
        'max_difference': max_diff,
        'avg_difference': avg_diff,
        'threshold': threshold
    }


def create_diff_image(img1_path, img2_path, output_path, amplify=10):
    """
    Create a visual diff image highlighting differences.
    
    Args:
        img1_path: Path to first image
        img2_path: Path to second image
        output_path: Path to save diff image
        amplify: Factor to amplify differences for visibility
    """
    try:
        from PIL import Image
        
        img1 = Image.open(img1_path).convert('RGB')
        img2 = Image.open(img2_path).convert('RGB')
        
        if img1.size != img2.size:
            print("Cannot create diff: images have different sizes")
            return False
        
        width, height = img1.size
        diff_img = Image.new('RGB', (width, height))
        
        pixels1 = img1.load()
        pixels2 = img2.load()
        diff_pixels = diff_img.load()
        
        for y in range(height):
            for x in range(width):
                r1, g1, b1 = pixels1[x, y]
                r2, g2, b2 = pixels2[x, y]
                
                # Calculate absolute difference
                r_diff = min(255, abs(r1 - r2) * amplify)
                g_diff = min(255, abs(g1 - g2) * amplify)
                b_diff = min(255, abs(b1 - b2) * amplify)
                
                diff_pixels[x, y] = (r_diff, g_diff, b_diff)
        
        diff_img.save(output_path)
        print(f"Diff image saved to: {output_path}")
        return True
        
    except ImportError:
        print("Error: PIL/Pillow not installed")
        return False
    except Exception as e:
        print(f"Error creating diff image: {e}")
        return False


def print_comparison_report(result):
    """Print a formatted comparison report."""
    if result is None:
        print("Comparison failed")
        return
    
    if 'error' in result:
        print(f"Error: {result['error']}")
        if 'size1' in result:
            print(f"  Image 1: {result['size1']}")
            print(f"  Image 2: {result['size2']}")
        return
    
    print(f"Dimensions: {result['dimensions'][0]}x{result['dimensions'][1]}")
    print(f"Total pixels: {result['total_pixels']:,}")
    
    if result['identical']:
        print("✓ Images are IDENTICAL")
    else:
        print(f"✗ Images are DIFFERENT")
        print(f"  Different pixels: {result['different_pixels']:,} ({result['diff_percentage']:.2f}%)")
        print(f"  Max difference: {result['max_difference']}/255")
        print(f"  Avg difference: {result['avg_difference']:.2f}/255")
        print(f"  Threshold: {result['threshold']}")


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print("Usage: python compare_captures.py <image1> <image2> [threshold] [--diff output.png]")
        print()
        print("Arguments:")
        print("  image1, image2  : Images to compare")
        print("  threshold       : Optional pixel difference threshold (default: 0)")
        print("  --diff output   : Create visual diff image")
        print()
        print("Examples:")
        print("  python compare_captures.py capture1.png capture2.png")
        print("  python compare_captures.py capture1.png capture2.png 5")
        print("  python compare_captures.py capture1.png capture2.png 0 --diff diff.png")
        return 1
    
    img1_path = sys.argv[1]
    img2_path = sys.argv[2]
    
    # Parse threshold
    threshold = 0
    diff_output = None
    
    i = 3
    while i < len(sys.argv):
        if sys.argv[i] == '--diff' and i + 1 < len(sys.argv):
            diff_output = sys.argv[i + 1]
            i += 2
        else:
            try:
                threshold = int(sys.argv[i])
                i += 1
            except ValueError:
                print(f"Warning: Invalid threshold '{sys.argv[i]}', using 0")
                i += 1
    
    # Check files exist
    if not os.path.exists(img1_path):
        print(f"Error: File not found: {img1_path}")
        return 1
    
    if not os.path.exists(img2_path):
        print(f"Error: File not found: {img2_path}")
        return 1
    
    print("=" * 60)
    print("Image Comparison")
    print("=" * 60)
    print(f"Image 1: {img1_path}")
    print(f"Image 2: {img2_path}")
    print()
    
    # Compare
    result = compare_images(img1_path, img2_path, threshold)
    print_comparison_report(result)
    
    # Create diff image if requested
    if diff_output and result and not result['identical']:
        print()
        print("Creating diff image...")
        create_diff_image(img1_path, img2_path, diff_output)
    
    print()
    
    # Return exit code
    if result and result['identical']:
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
