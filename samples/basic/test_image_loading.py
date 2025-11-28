#!/usr/bin/env python3
"""
Test script to verify image loading with Pillow
"""

import sys
sys.path.insert(0, '../../build')

import cyber_ui_core as ui
from PIL import Image as PILImage
import numpy as np
import os

def load_image_with_pillow(filepath):
    """Load an image using Pillow and return a cyber_ui Image object"""
    if not os.path.exists(filepath):
        print(f"Error: Image file not found: {filepath}")
        return None
    
    try:
        # Load image with Pillow
        pil_img = PILImage.open(filepath)
        
        # Convert to RGBA if needed
        if pil_img.mode != 'RGBA':
            pil_img = pil_img.convert('RGBA')
        
        # Get image data as numpy array
        img_array = np.array(pil_img, dtype=np.uint8)
        
        # Create cyber_ui Image object
        ui_img = ui.Image()
        width, height = pil_img.size
        channels = 4  # RGBA
        
        # Load data into Image object
        if ui_img.load_from_data(img_array, width, height, channels):
            return ui_img
        else:
            print(f"Failed to load image data: {filepath}")
            return None
            
    except Exception as e:
        print(f"Error loading image {filepath}: {e}")
        return None

def main():
    print("=== Image Loading Test ===\n")
    
    # Get script directory for relative paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "data")
    
    # Test images
    test_images = [
        (os.path.join(data_dir, "gradient.png"), "Gradient"),
        (os.path.join(data_dir, "checkerboard.png"), "Checkerboard"),
        (os.path.join(data_dir, "icon.png"), "Icon")
    ]
    
    loaded_count = 0
    for filepath, name in test_images:
        print(f"Loading {name}...")
        img = load_image_with_pillow(filepath)
        if img and img.is_loaded():
            print(f"  ✓ {name}: {img.get_width()}x{img.get_height()}, {img.get_channels()} channels")
            loaded_count += 1
        else:
            print(f"  ✗ {name}: Failed to load")
        print()
    
    print(f"Successfully loaded {loaded_count}/{len(test_images)} images")
    
    if loaded_count == len(test_images):
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
