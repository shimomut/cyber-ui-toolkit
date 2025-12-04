#!/usr/bin/env python3
"""
Test Frame2D clipping functionality by capturing and analyzing rendered frames.

This test verifies:
1. Content inside clipping region is rendered
2. Content outside clipping region is NOT rendered (clipped)
3. Clipping boundaries are correct
"""

import sys
sys.path.insert(0, '../build')

import cyber_ui_core as ui
from PIL import Image as PILImage
import os
import numpy as np

def load_image_with_pillow(filepath):
    """Load an image using Pillow and return a cyber_ui Image object"""
    if not os.path.exists(filepath):
        print(f"Warning: Image file not found: {filepath}")
        return None
    
    try:
        pil_img = PILImage.open(filepath)
        if pil_img.mode != 'RGBA':
            pil_img = pil_img.convert('RGBA')
        
        img_bytes = pil_img.tobytes()
        ui_img = ui.Image()
        width, height = pil_img.size
        channels = 4
        
        if ui_img.load_from_data(img_bytes, width, height, channels):
            return ui_img
        else:
            return None
            
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def analyze_clipping_region(pixel_data, width, height, clip_x, clip_y, clip_width, clip_height):
    """
    Analyze pixel data to verify clipping is working correctly.
    
    Returns:
        dict with analysis results
    """
    # Convert bytes to numpy array (BGRA format)
    pixels = np.frombuffer(pixel_data, dtype=np.uint8).reshape(height, width, 4)
    
    # Define regions
    inside_region = pixels[clip_y:clip_y+clip_height, clip_x:clip_x+clip_width]
    
    # Sample outside regions (top, bottom, left, right)
    outside_regions = []
    
    # Top region (above clipping area)
    if clip_y > 10:
        outside_regions.append(('top', pixels[0:clip_y-5, :]))
    
    # Bottom region (below clipping area)
    if clip_y + clip_height < height - 10:
        outside_regions.append(('bottom', pixels[clip_y+clip_height+5:, :]))
    
    # Left region (left of clipping area)
    if clip_x > 10:
        outside_regions.append(('left', pixels[:, 0:clip_x-5]))
    
    # Right region (right of clipping area)
    if clip_x + clip_width < width - 10:
        outside_regions.append(('right', pixels[:, clip_x+clip_width+5:]))
    
    # Calculate statistics
    results = {
        'inside_non_background': 0,
        'outside_non_background': 0,
        'inside_pixels': inside_region.shape[0] * inside_region.shape[1],
        'outside_pixels': 0,
        'background_color': [26, 26, 31],  # Expected background (0.1, 0.1, 0.1) * 255
        'regions_analyzed': []
    }
    
    # Background color in BGRA (Metal uses BGRA format)
    bg_b, bg_g, bg_r = 26, 26, 26  # Approximately 0.1 * 255
    bg_threshold = 30  # Tolerance for background detection
    
    # Analyze inside region
    for y in range(inside_region.shape[0]):
        for x in range(inside_region.shape[1]):
            b, g, r, a = inside_region[y, x]
            # Check if pixel is NOT background
            if abs(b - bg_b) > bg_threshold or abs(g - bg_g) > bg_threshold or abs(r - bg_r) > bg_threshold:
                results['inside_non_background'] += 1
    
    # Analyze outside regions
    for region_name, region in outside_regions:
        region_non_bg = 0
        region_pixels = region.shape[0] * region.shape[1]
        results['outside_pixels'] += region_pixels
        
        for y in range(region.shape[0]):
            for x in range(region.shape[1]):
                b, g, r, a = region[y, x]
                # Check if pixel is NOT background
                if abs(b - bg_b) > bg_threshold or abs(g - bg_g) > bg_threshold or abs(r - bg_r) > bg_threshold:
                    region_non_bg += 1
                    results['outside_non_background'] += 1
        
        results['regions_analyzed'].append({
            'name': region_name,
            'pixels': region_pixels,
            'non_background': region_non_bg,
            'percentage': (region_non_bg / region_pixels * 100) if region_pixels > 0 else 0
        })
    
    return results

def main():
    print("=== Frame2D Clipping Test ===\n")
    
    # Initialize renderer
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(800, 700, "Clipping Test"):
        print("Failed to initialize renderer")
        return False
    
    print("✓ Renderer initialized\n")
    
    # Create scene
    scene = ui.SceneRoot()
    camera = scene.get_camera()
    camera.set_position(0.0, 0.0, 800.0)
    camera.set_perspective(1.0472, 800.0/700.0, 0.1, 2000.0)
    
    # Load test image
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "samples", "data")
    gradient_img = load_image_with_pillow(os.path.join(data_dir, "gradient.png"))
    
    # Create Frame3D
    frame3d = ui.Frame3D()
    frame3d.set_name("TestFrame3D")
    frame3d.set_position(0.0, 0.0, 0.0)
    scene.add_frame3d(frame3d)
    
    # Create Frame2D with clipping
    clip_panel = ui.Frame2D()
    clip_panel.set_name("ClipPanel")
    clip_panel.set_position(150.0, 50.0)  # Position in world space
    clip_panel.set_size(500.0, 600.0)     # Clipping region size
    clip_panel.set_clipping_enabled(True)
    
    # Background
    panel_bg = ui.Rectangle(500.0, 600.0)
    panel_bg.set_position(0.0, 0.0)
    panel_bg.set_color(0.08, 0.08, 0.12, 1.0)
    clip_panel.add_child(panel_bg)
    
    # Add rectangles that extend beyond clipping region
    # Rectangle 1: Fully inside
    rect1 = ui.Rectangle(100.0, 100.0)
    rect1.set_position(200.0, 250.0)
    rect1.set_color(1.0, 0.3, 0.3, 1.0)
    if gradient_img:
        rect1.set_image(gradient_img)
    clip_panel.add_child(rect1)
    
    # Rectangle 2: Partially outside top
    rect2 = ui.Rectangle(150.0, 150.0)
    rect2.set_position(175.0, -50.0)  # Extends above clipping region
    rect2.set_color(0.3, 1.0, 0.3, 1.0)
    if gradient_img:
        rect2.set_image(gradient_img)
    clip_panel.add_child(rect2)
    
    # Rectangle 3: Partially outside bottom
    rect3 = ui.Rectangle(150.0, 150.0)
    rect3.set_position(175.0, 500.0)  # Extends below clipping region
    rect3.set_color(0.3, 0.3, 1.0, 1.0)
    if gradient_img:
        rect3.set_image(gradient_img)
    clip_panel.add_child(rect3)
    
    # Rectangle 4: Partially outside left
    rect4 = ui.Rectangle(150.0, 100.0)
    rect4.set_position(-50.0, 250.0)  # Extends left of clipping region
    rect4.set_color(1.0, 1.0, 0.3, 1.0)
    if gradient_img:
        rect4.set_image(gradient_img)
    clip_panel.add_child(rect4)
    
    # Rectangle 5: Partially outside right
    rect5 = ui.Rectangle(150.0, 100.0)
    rect5.set_position(400.0, 250.0)  # Extends right of clipping region
    rect5.set_color(1.0, 0.3, 1.0, 1.0)
    if gradient_img:
        rect5.set_image(gradient_img)
    clip_panel.add_child(rect5)
    
    frame3d.add_child(clip_panel)
    
    print("✓ Scene created with clipping test objects\n")
    
    # Render a single frame
    if renderer.begin_frame():
        renderer.render_scene(scene)
        renderer.end_frame()
    
    # Capture frame
    print("Capturing frame...")
    pixel_data, width, height = renderer.capture_frame()
    
    if pixel_data is None:
        print("✗ Failed to capture frame")
        renderer.shutdown()
        return False
    
    print(f"✓ Captured {width}x{height} frame ({len(pixel_data)} bytes)\n")
    
    # Save capture for visual inspection
    output_dir = os.path.join(script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "clipping_test.png")
    
    if renderer.save_capture(output_file):
        print(f"✓ Saved capture to: {output_file}\n")
    
    # Analyze clipping
    print("Analyzing clipping regions...")
    
    # Account for retina display scaling
    scale_factor = width / 800  # Actual width / window width
    print(f"Display scale factor: {scale_factor}x")
    
    # Transform world coordinates to screen coordinates
    # Frame2D is at (150, 50) in world space with size (500, 600)
    # The camera uses perspective projection, so we need to account for that
    # For now, use the scaled coordinates directly
    
    clip_screen_x = int(150 * scale_factor)
    clip_screen_y = int(50 * scale_factor)
    clip_width = int(500 * scale_factor)
    clip_height = int(600 * scale_factor)
    
    print(f"Clipping region in screen space: ({clip_screen_x}, {clip_screen_y}) size ({clip_width}x{clip_height})")
    
    results = analyze_clipping_region(
        pixel_data, width, height,
        clip_screen_x, clip_screen_y, clip_width, clip_height
    )
    
    print(f"\nClipping Analysis Results:")
    print(f"{'='*60}")
    print(f"Inside clipping region:")
    print(f"  Total pixels: {results['inside_pixels']}")
    print(f"  Non-background pixels: {results['inside_non_background']}")
    print(f"  Percentage: {results['inside_non_background']/results['inside_pixels']*100:.2f}%")
    print()
    print(f"Outside clipping region:")
    print(f"  Total pixels: {results['outside_pixels']}")
    print(f"  Non-background pixels: {results['outside_non_background']}")
    print(f"  Percentage: {results['outside_non_background']/results['outside_pixels']*100:.2f}%")
    print()
    
    for region in results['regions_analyzed']:
        print(f"  {region['name'].upper()} region:")
        print(f"    Pixels: {region['pixels']}")
        print(f"    Non-background: {region['non_background']}")
        print(f"    Percentage: {region['percentage']:.2f}%")
    
    print(f"{'='*60}\n")
    
    # Verify clipping is working
    success = True
    
    # Test 1: Inside region should have content
    inside_percentage = results['inside_non_background'] / results['inside_pixels'] * 100
    if inside_percentage < 5:
        print("✗ FAIL: Inside region has too little content")
        success = False
    else:
        print(f"✓ PASS: Inside region has content ({inside_percentage:.1f}%)")
    
    # Test 2: Outside region should be mostly background
    if results['outside_pixels'] > 0:
        outside_percentage = results['outside_non_background'] / results['outside_pixels'] * 100
        if outside_percentage > 5:
            print(f"✗ FAIL: Outside region has too much content ({outside_percentage:.1f}%)")
            print("  This suggests clipping is not working correctly")
            success = False
        else:
            print(f"✓ PASS: Outside region is mostly background ({outside_percentage:.1f}%)")
    
    # Test 3: Check individual outside regions
    for region in results['regions_analyzed']:
        if region['percentage'] > 5:
            print(f"✗ FAIL: {region['name'].upper()} region has {region['percentage']:.1f}% non-background pixels")
            success = False
    
    print()
    if success:
        print("="*60)
        print("✓ ALL TESTS PASSED - Clipping is working correctly!")
        print("="*60)
    else:
        print("="*60)
        print("✗ SOME TESTS FAILED - Clipping may not be working correctly")
        print("="*60)
    
    renderer.shutdown()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
