#!/usr/bin/env python3
"""
Diagnostic tool to investigate display noise vs captured image differences.

This script helps identify if noise is coming from:
1. The rendering pipeline
2. The Metal drawable presentation
3. Display scaling/compositing
4. Window manager effects
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build'))

import cyber_ui_core as ui
import time


def create_test_pattern(renderer, scene):
    """Create a simple test pattern to make noise more visible."""
    camera = ui.Camera()
    camera.set_position(0, 0, 5)
    scene.set_camera(camera)
    
    frame = ui.Frame3D(800, 600)
    frame.set_position(0, 0, 0)
    
    # Create a gradient pattern with solid colors
    # This makes any noise or dithering very obvious
    colors = [
        (0.0, 0.0, 0.0, 1.0),  # Black
        (0.25, 0.25, 0.25, 1.0),  # Dark gray
        (0.5, 0.5, 0.5, 1.0),  # Medium gray
        (0.75, 0.75, 0.75, 1.0),  # Light gray
        (1.0, 1.0, 1.0, 1.0),  # White
    ]
    
    rect_width = 160
    total_width = rect_width * len(colors)
    start_x = -total_width / 2 + rect_width / 2
    
    for i, color in enumerate(colors):
        rect = ui.Rectangle(rect_width, 400)
        rect.set_color(*color)
        rect.set_position(start_x + i * rect_width, 0)
        rect.set_name(f"GrayBar_{i}")
        frame.add_child(rect)
    
    scene.add_frame3d(frame)
    return frame


def analyze_captured_pixels(data, width, height, sample_regions):
    """Analyze pixel data in specific regions to detect noise."""
    import struct
    pixels = struct.unpack(f'{len(data)}B', data)
    
    results = {}
    
    for region_name, (x, y, w, h) in sample_regions.items():
        # Sample pixels in this region
        samples = []
        for dy in range(h):
            for dx in range(w):
                px = x + dx
                py = y + dy
                if 0 <= px < width and 0 <= py < height:
                    offset = (py * width + px) * 4
                    b = pixels[offset]
                    g = pixels[offset + 1]
                    r = pixels[offset + 2]
                    a = pixels[offset + 3]
                    samples.append((r, g, b, a))
        
        if samples:
            # Calculate statistics
            avg_r = sum(s[0] for s in samples) / len(samples)
            avg_g = sum(s[1] for s in samples) / len(samples)
            avg_b = sum(s[2] for s in samples) / len(samples)
            
            # Calculate variance (measure of noise)
            var_r = sum((s[0] - avg_r) ** 2 for s in samples) / len(samples)
            var_g = sum((s[1] - avg_g) ** 2 for s in samples) / len(samples)
            var_b = sum((s[2] - avg_b) ** 2 for s in samples) / len(samples)
            
            # Find min/max values
            min_r = min(s[0] for s in samples)
            max_r = max(s[0] for s in samples)
            min_g = min(s[1] for s in samples)
            max_g = max(s[1] for s in samples)
            min_b = min(s[2] for s in samples)
            max_b = max(s[2] for s in samples)
            
            results[region_name] = {
                'avg': (avg_r, avg_g, avg_b),
                'variance': (var_r, var_g, var_b),
                'range': ((min_r, max_r), (min_g, max_g), (min_b, max_b)),
                'samples': len(samples)
            }
    
    return results


def main():
    """Run display noise diagnostic."""
    print("=" * 70)
    print("Display Noise Diagnostic Tool")
    print("=" * 70)
    print()
    print("This tool will:")
    print("1. Display a test pattern with solid gray bars")
    print("2. Capture multiple frames")
    print("3. Analyze pixel consistency")
    print("4. Help identify the source of display noise")
    print()
    print("Look at the window - do you see noise/dithering?")
    print("The captured images should be perfectly clean.")
    print()
    
    # Create renderer
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(800, 600, "Display Noise Diagnostic"):
        print("Failed to initialize renderer")
        return 1
    
    # Create test pattern
    scene = ui.SceneRoot()
    frame = create_test_pattern(renderer, scene)
    
    print("Rendering test pattern...")
    print("Let it stabilize for a moment...")
    
    # Render several frames to ensure everything is loaded
    for i in range(10):
        renderer.poll_events()
        if renderer.should_close():
            renderer.shutdown()
            return 0
        
        renderer.begin_frame()
        renderer.render_scene(scene)
        renderer.end_frame()
        time.sleep(0.05)
    
    # Create output directory
    output_dir = "tests/output"
    os.makedirs(output_dir, exist_ok=True)
    
    print("\nCapturing frames for analysis...")
    
    # Capture multiple frames
    captures = []
    for i in range(5):
        # Render a frame
        renderer.poll_events()
        if renderer.should_close():
            break
        
        renderer.begin_frame()
        renderer.render_scene(scene)
        renderer.end_frame()
        
        # Capture it
        data, width, height = renderer.capture_frame()
        if data is not None:
            captures.append((data, width, height))
            
            # Save to file
            filename = os.path.join(output_dir, f"noise_test_{i+1}.png")
            renderer.save_capture(filename)
            print(f"  Captured frame {i+1}: {filename}")
        
        time.sleep(0.1)
    
    if not captures:
        print("Failed to capture any frames")
        renderer.shutdown()
        return 1
    
    print(f"\nAnalyzing {len(captures)} captured frames...")
    
    # Define sample regions (center of each gray bar)
    width = captures[0][1]
    height = captures[0][2]
    
    bar_width = 160
    bar_height = 400
    sample_size = 50  # Sample a 50x50 region in center of each bar
    
    center_y = height // 2
    
    sample_regions = {}
    for i in range(5):
        bar_x = (width // 2) - (bar_width * 5 // 2) + (bar_width * i) + (bar_width // 2)
        sample_x = bar_x - sample_size // 2
        sample_y = center_y - sample_size // 2
        sample_regions[f"Bar_{i}"] = (sample_x, sample_y, sample_size, sample_size)
    
    # Analyze each capture
    all_results = []
    for i, (data, w, h) in enumerate(captures):
        results = analyze_captured_pixels(data, w, h, sample_regions)
        all_results.append(results)
    
    # Print analysis
    print("\n" + "=" * 70)
    print("Pixel Analysis Results")
    print("=" * 70)
    
    for region_name in sorted(sample_regions.keys()):
        print(f"\n{region_name}:")
        print("-" * 70)
        
        for i, results in enumerate(all_results):
            if region_name in results:
                r = results[region_name]
                avg = r['avg']
                var = r['variance']
                rng = r['range']
                
                print(f"  Frame {i+1}:")
                print(f"    Average RGB: ({avg[0]:.2f}, {avg[1]:.2f}, {avg[2]:.2f})")
                print(f"    Variance:    ({var[0]:.4f}, {var[1]:.4f}, {var[2]:.4f})")
                print(f"    Range R:     {rng[0][0]}-{rng[0][1]} (span: {rng[0][1]-rng[0][0]})")
                print(f"    Range G:     {rng[1][0]}-{rng[1][1]} (span: {rng[1][1]-rng[1][0]})")
                print(f"    Range B:     {rng[2][0]}-{rng[2][1]} (span: {rng[2][1]-rng[2][0]})")
    
    # Check consistency across frames
    print("\n" + "=" * 70)
    print("Cross-Frame Consistency Check")
    print("=" * 70)
    
    for region_name in sorted(sample_regions.keys()):
        print(f"\n{region_name}:")
        
        # Collect averages across all frames
        avgs = [all_results[i][region_name]['avg'] for i in range(len(all_results))]
        
        # Calculate variance across frames
        avg_r_mean = sum(a[0] for a in avgs) / len(avgs)
        avg_g_mean = sum(a[1] for a in avgs) / len(avgs)
        avg_b_mean = sum(a[2] for a in avgs) / len(avgs)
        
        var_r = sum((a[0] - avg_r_mean) ** 2 for a in avgs) / len(avgs)
        var_g = sum((a[1] - avg_g_mean) ** 2 for a in avgs) / len(avgs)
        var_b = sum((a[2] - avg_b_mean) ** 2 for a in avgs) / len(avgs)
        
        print(f"  Mean across frames: ({avg_r_mean:.2f}, {avg_g_mean:.2f}, {avg_b_mean:.2f})")
        print(f"  Frame-to-frame variance: ({var_r:.6f}, {var_g:.6f}, {var_b:.6f})")
        
        if var_r < 0.01 and var_g < 0.01 and var_b < 0.01:
            print(f"  ✓ Highly consistent across frames")
        elif var_r < 0.1 and var_g < 0.1 and var_b < 0.1:
            print(f"  ✓ Reasonably consistent across frames")
        else:
            print(f"  ⚠ Significant variation across frames")
    
    print("\n" + "=" * 70)
    print("Interpretation")
    print("=" * 70)
    print()
    print("If captured images show:")
    print("  • Low variance within each region: ✓ Clean rendering")
    print("  • Low frame-to-frame variance: ✓ Consistent rendering")
    print("  • Pixel range span of 0-2: ✓ No noise in captures")
    print()
    print("If you see noise in the WINDOW but NOT in captures:")
    print("  → Noise is added during display presentation")
    print("  → Possible causes:")
    print("    - Display scaling/interpolation")
    print("    - Window compositing effects")
    print("    - MTKView drawable presentation")
    print("    - macOS display color management")
    print()
    print("Captured images are saved to: tests/output/noise_test_*.png")
    print("Examine these images closely - they should be perfectly clean.")
    print()
    
    # Keep window open for visual inspection
    print("Window will stay open for 10 seconds for visual inspection...")
    print("Compare what you see in the window vs the captured images.")
    
    for i in range(100):
        renderer.poll_events()
        if renderer.should_close():
            break
        
        renderer.begin_frame()
        renderer.render_scene(scene)
        renderer.end_frame()
        time.sleep(0.1)
    
    renderer.shutdown()
    print("\nDiagnostic complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
