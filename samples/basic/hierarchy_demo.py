#!/usr/bin/env python3
"""
Hierarchy Demo - Demonstrates Frame3D, Frame2D, and Rectangle hierarchy

This sample shows:
- Frame3D for 3D positioning
- Frame2D containers with clipping
- Nested Frame2D structures
- Rectangle shapes with colors and textures
- Parent-child relationships and relative positioning

Usage:
    python hierarchy_demo.py              # Normal mode (no capture)
    python hierarchy_demo.py --capture    # Enable frame capture
"""

import sys
sys.path.insert(0, '../../build')

import cyber_ui_core as ui
from PIL import Image as PILImage
import os
import math
import argparse
import time

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
            print(f"✓ Loaded: {os.path.basename(filepath)} ({width}x{height})")
            return ui_img
        else:
            print(f"✗ Failed to load: {filepath}")
            return None
            
    except Exception as e:
        print(f"✗ Error loading {filepath}: {e}")
        return None

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='3D Hierarchy Demo')
    parser.add_argument('--capture', action='store_true',
                        help='Enable frame capture to samples/output/')
    args = parser.parse_args()
    
    print("=== Cyber UI Toolkit - 3D Hierarchy Demo ===\n")
    
    if args.capture:
        print("📸 Frame capture ENABLED")
        print("   Frames will be saved to samples/output/\n")
    else:
        print("Frame capture disabled (use --capture to enable)\n")
    
    # Initialize renderer (auto-detect available backend)
    if hasattr(ui, 'create_metal_renderer'):
        renderer = ui.create_metal_renderer()
        backend = "Metal"
    elif hasattr(ui, 'create_opengl_renderer'):
        renderer = ui.create_opengl_renderer()
        backend = "OpenGL"
    else:
        print("❌ No rendering backend available!")
        print("   Build with: make build-metal or make build-opengl")
        return
    
    print(f"Using {backend} backend")
    
    if not renderer.initialize(1024, 768, "Cyber UI - 3D Hierarchy Demo"):
        print("Failed to initialize renderer")
        return
    
    print("Renderer initialized successfully!")
    print("Press ESC or close window to exit\n")
    
    # Create scene root and camera
    scene = ui.SceneRoot()
    camera = scene.get_camera()
    
    # Configure camera for 3D view
    camera.set_position(0.0, 0.0, 800.0)  # Camera looking at scene from distance
    camera.set_rotation(0.0, 0.0, 0.0)
    camera.set_perspective(1.0472, 1024.0/768.0, 0.1, 2000.0)  # 60 degrees FOV
    print("✓ Camera configured: position (0, 0, 800), FOV 60°\n")
    
    # Load textures
    print("Loading textures...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "data")
    
    gradient_img = load_image_with_pillow(os.path.join(data_dir, "gradient.png"))
    checker_img = load_image_with_pillow(os.path.join(data_dir, "checkerboard.png"))
    icon_img = load_image_with_pillow(os.path.join(data_dir, "icon.png"))
    print()
    
    # ===== Create Multiple Frame3D Containers =====
    print("Building scene hierarchy with multiple Frame3D containers...")
    
    # Frame3D #1 - Left section (positioned left and slightly rotated)
    frame3d_left = ui.Frame3D(800, 600)
    frame3d_left.set_name("Frame3D_Left")
    frame3d_left.set_position(-350.0, 0.0, -100.0)
    frame3d_left.set_rotation(0.0, 0.2, 0.0)  # Rotated to face camera
    frame3d_left.set_scale(1.0, 1.0, 1.0)
    print("✓ Created Frame3D: Frame3D_Left (pos: -350, 0, -100, rot: 0, 0.2, 0)")
    
    # Frame3D #2 - Center section (positioned at center, closer to camera)
    frame3d_center = ui.Frame3D(800, 600)
    frame3d_center.set_name("Frame3D_Center")
    frame3d_center.set_position(0.0, 0.0, 50.0)
    frame3d_center.set_rotation(0.0, 0.0, 0.0)  # Facing camera directly
    frame3d_center.set_scale(1.0, 1.0, 1.0)
    print("✓ Created Frame3D: Frame3D_Center (pos: 0, 0, 50, rot: 0, 0, 0)")
    
    # Frame3D #3 - Right section (positioned right and rotated opposite)
    frame3d_right = ui.Frame3D(800, 600)
    frame3d_right.set_name("Frame3D_Right")
    frame3d_right.set_position(350.0, 0.0, -100.0)
    frame3d_right.set_rotation(0.0, -0.2, 0.0)  # Rotated to face camera
    frame3d_right.set_scale(1.0, 1.0, 1.0)
    print("✓ Created Frame3D: Frame3D_Right (pos: 350, 0, -100, rot: 0, -0.2, 0)")
    
    # Add Frame3D objects to scene
    scene.add_frame3d(frame3d_left)
    scene.add_frame3d(frame3d_center)
    scene.add_frame3d(frame3d_right)
    
    # ===== Frame3D Left - Vertical Panel =====
    left_panel = ui.Frame2D(250.0, 650.0)
    left_panel.set_name("LeftPanel")
    left_panel.set_position(50.0, 50.0)
    left_panel.set_clipping_enabled(True)
    print("✓ Created Frame2D: LeftPanel (with clipping)")
    
    # Background for left panel (centered in 250x650 area)
    left_bg = ui.Rectangle(250.0, 650.0)
    left_bg.set_name("LeftPanelBackground")
    left_bg.set_position(125.0, 325.0)  # Center of Frame2D (top-left origin)
    left_bg.set_color(0.15, 0.15, 0.2, 1.0)
    left_panel.add_child(left_bg)
    
    # Title rectangle in left panel
    title_rect = ui.Rectangle(230.0, 50.0)
    title_rect.set_name("TitleRect")
    title_rect.set_position(125.0, 35.0)  # Centered horizontally, near top
    title_rect.set_color(0.3, 0.5, 0.8, 1.0)
    if gradient_img:
        title_rect.set_image(gradient_img)
    left_panel.add_child(title_rect)
    
    # Content rectangles in left panel
    content_rect_with_checker = None
    for i in range(6):
        content_rect = ui.Rectangle(210.0, 80.0)
        content_rect.set_name(f"ContentRect{i+1}")
        content_rect.set_position(125.0, 120.0 + i * 95.0)  # Centered horizontally
        
        # Alternate colors
        if i % 2 == 0:
            content_rect.set_color(0.2, 0.4, 0.6, 1.0)
        else:
            content_rect.set_color(0.3, 0.3, 0.5, 1.0)
        
        if checker_img and i == 2:
            content_rect.set_image(checker_img)
            content_rect_with_checker = content_rect
        
        left_panel.add_child(content_rect)
    
    frame3d_left.add_child(left_panel)
    print("  └─ Added 7 rectangles to LeftPanel")
    
    # ===== Frame3D Center - Nested Grid Panel =====
    center_panel = ui.Frame2D(300.0, 550.0)
    center_panel.set_name("CenterPanel")
    center_panel.set_position(350.0, 100.0)
    center_panel.set_clipping_enabled(False)
    print("✓ Created Frame2D: CenterPanel (no clipping)")
    
    # Background (centered in 300x550 area)
    center_bg = ui.Rectangle(300.0, 550.0)
    center_bg.set_name("CenterBackground")
    center_bg.set_position(150.0, 275.0)  # Center of Frame2D
    center_bg.set_color(0.1, 0.15, 0.15, 1.0)
    center_panel.add_child(center_bg)
    
    # Header
    center_header = ui.Rectangle(280.0, 60.0)
    center_header.set_name("CenterHeader")
    center_header.set_position(150.0, 40.0)  # Centered horizontally, near top
    center_header.set_color(0.4, 0.3, 0.6, 1.0)
    if gradient_img:
        center_header.set_image(gradient_img)
    center_panel.add_child(center_header)
    
    # Nested Frame2D inside center panel (top-left origin positioning)
    nested_frame = ui.Frame2D(280.0, 440.0)
    nested_frame.set_name("NestedFrame")
    nested_frame.set_position(150.0, 310.0)  # Centered horizontally, below header
    nested_frame.set_clipping_enabled(True)
    print("  ✓ Created nested Frame2D: NestedFrame (with clipping)")
    
    # Nested frame background (centered in 280x440 area)
    nested_bg = ui.Rectangle(280.0, 440.0)
    nested_bg.set_name("NestedBackground")
    nested_bg.set_position(140.0, 220.0)  # Center of nested Frame2D
    nested_bg.set_color(0.2, 0.25, 0.25, 1.0)
    nested_frame.add_child(nested_bg)
    
    # Grid of rectangles in nested frame (4x4) - using top-left origin
    grid_rects = []
    for row in range(4):
        for col in range(4):
            grid_rect = ui.Rectangle(60.0, 60.0)
            grid_rect.set_name(f"GridRect_{row}_{col}")
            grid_rect.set_position(40.0 + col * 67.0, 40.0 + row * 67.0)  # Offset from top-left
            
            # Color based on position
            r = 0.3 + (col / 4.0) * 0.5
            g = 0.3 + (row / 4.0) * 0.5
            b = 0.5
            grid_rect.set_color(r, g, b, 1.0)
            
            # Add textures to some rectangles
            texture_type = None
            if (row + col) % 3 == 0 and icon_img:
                grid_rect.set_image(icon_img)
                texture_type = 'icon'
            elif (row + col) % 3 == 1 and checker_img:
                grid_rect.set_image(checker_img)
                texture_type = 'checker'
            
            grid_rects.append((grid_rect, texture_type, row, col))
            nested_frame.add_child(grid_rect)
    
    center_panel.add_child(nested_frame)
    frame3d_center.add_child(center_panel)
    print("    └─ Added 4x4 grid (16 rectangles) to NestedFrame")
    
    # ===== Frame3D Right - Carousel Panel =====
    right_panel = ui.Frame2D(280.0, 450.0)
    right_panel.set_name("RightPanel")
    right_panel.set_position(700.0, 150.0)
    right_panel.set_clipping_enabled(True)
    print("✓ Created Frame2D: RightPanel (with clipping)")
    
    # Background (centered in 280x450 area)
    right_bg = ui.Rectangle(280.0, 450.0)
    right_bg.set_name("RightBackground")
    right_bg.set_position(140.0, 225.0)  # Center of Frame2D
    right_bg.set_color(0.15, 0.2, 0.15, 1.0)
    right_panel.add_child(right_bg)
    
    # Create a carousel-like layout with overlapping rectangles
    carousel_items = []
    for i in range(5):
        item = ui.Rectangle(240.0, 140.0)
        item.set_name(f"CarouselItem{i+1}")
        item.set_position(140.0, 100.0 + i * 80.0)  # Centered horizontally
        
        # Different colors for each item
        hue = i / 5.0
        if i % 3 == 0:
            item.set_color(0.8, 0.3 + hue * 0.4, 0.3, 1.0)
            if gradient_img:
                item.set_image(gradient_img)
        elif i % 3 == 1:
            item.set_color(0.3, 0.8, 0.3 + hue * 0.4, 1.0)
            if checker_img:
                item.set_image(checker_img)
        else:
            item.set_color(0.3 + hue * 0.4, 0.3, 0.8, 1.0)
            if icon_img:
                item.set_image(icon_img)
        
        right_panel.add_child(item)
        carousel_items.append(item)
    
    frame3d_right.add_child(right_panel)
    print("  └─ Added 5 carousel items to RightPanel")
    
    print("\n" + "="*60)
    print("Scene Hierarchy Summary:")
    print("="*60)
    print("Frame3D_Left (pos: 0,0,0)")
    print("└── Frame2D (LeftPanel) - 7 rectangles")
    print()
    print("Frame3D_Center (pos: 0,0,-2, rot: 0,0.1,0)")
    print("└── Frame2D (CenterPanel)")
    print("    └── Frame2D (NestedFrame) - 16 rectangles in 4x4 grid")
    print()
    print("Frame3D_Right (pos: 0,0,2, rot: 0,-0.1,0)")
    print("└── Frame2D (RightPanel) - 5 carousel items")
    print("="*60)
    print()
    
    # Render loop with 3D animation
    # Debug toggle states
    texture_enabled = True
    clipping_enabled = True
    animation_enabled = True
    
    # Toggle intervals (in frames) - press keys during these windows
    toggle_check_interval = 60  # Check every 60 frames (1 second at 60fps)
    last_toggle_frame = 0
    
    print("Starting render loop with 3D animation...")
    print("Watch the panels rotate and move in 3D space!")
    if args.capture:
        print("Capturing frames automatically every 2 seconds...")
    print("\n" + "="*60)
    print("DEBUG CONTROLS (Terminal Input):")
    print("="*60)
    print("  Type 't' + ENTER to toggle Texture Mapping (currently: ON)")
    print("  Type 'c' + ENTER to toggle Clipping (currently: ON)")
    print("  Type 'a' + ENTER to toggle Animation (currently: ON)")
    print("  Type 'q' + ENTER or close window to exit")
    print("="*60)
    print("\nNote: Type commands in this terminal while the window is running\n")
    
    # Setup capture if enabled
    output_dir = None
    capture_count = 0
    initial_capture_frame = 5
    
    if args.capture:
        output_dir = os.path.join(script_dir, "..", "output")
        os.makedirs(output_dir, exist_ok=True)
    
    frame_count = 0
    start_time = time.time()
    
    # Function to apply texture state
    def apply_texture_state(enabled):
        # Toggle textures on title and header
        if gradient_img:
            if enabled:
                title_rect.set_image(gradient_img)
                center_header.set_image(gradient_img)
            else:
                title_rect.set_image(None)
                center_header.set_image(None)
        
        # Toggle checker texture on ContentRect3
        if content_rect_with_checker and checker_img:
            if enabled:
                content_rect_with_checker.set_image(checker_img)
            else:
                content_rect_with_checker.set_image(None)
        
        # Toggle grid textures
        for grid_rect, texture_type, row, col in grid_rects:
            if texture_type == 'icon' and icon_img:
                if enabled:
                    grid_rect.set_image(icon_img)
                else:
                    grid_rect.set_image(None)
            elif texture_type == 'checker' and checker_img:
                if enabled:
                    grid_rect.set_image(checker_img)
                else:
                    grid_rect.set_image(None)
        
        # Toggle carousel textures
        for i, item in enumerate(carousel_items):
            if i % 3 == 0 and gradient_img:
                if enabled:
                    item.set_image(gradient_img)
                else:
                    item.set_image(None)
            elif i % 3 == 1 and checker_img:
                if enabled:
                    item.set_image(checker_img)
                else:
                    item.set_image(None)
            elif i % 3 == 2 and icon_img:
                if enabled:
                    item.set_image(icon_img)
                else:
                    item.set_image(None)
    
    # Non-blocking input check
    import select
    import sys
    
    def check_input():
        """Check for terminal input without blocking"""
        if select.select([sys.stdin], [], [], 0.0)[0]:
            return sys.stdin.readline().strip().lower()
        return None
    
    while not renderer.should_close():
        renderer.poll_events()
        
        # Check for terminal input
        user_input = check_input()
        if user_input:
            if user_input == 't':
                texture_enabled = not texture_enabled
                status = "ON" if texture_enabled else "OFF"
                print(f"\n[T] Texture Mapping: {status}")
                apply_texture_state(texture_enabled)
            
            elif user_input == 'c':
                clipping_enabled = not clipping_enabled
                status = "ON" if clipping_enabled else "OFF"
                print(f"\n[C] Clipping: {status}")
                left_panel.set_clipping_enabled(clipping_enabled)
                nested_frame.set_clipping_enabled(clipping_enabled)
                right_panel.set_clipping_enabled(clipping_enabled)
            
            elif user_input == 'a':
                animation_enabled = not animation_enabled
                status = "ON" if animation_enabled else "OFF"
                print(f"\n[A] Animation: {status}")
            
            elif user_input == 'q':
                print("\nExiting...")
                break
        
        elapsed_time = time.time() - start_time
        
        # Apply animations only if enabled
        if animation_enabled:
            # Animate Frame3D rotations
            frame3d_left.set_rotation(0.0, 0.2 + math.sin(elapsed_time) * 0.15, 0.0)
            frame3d_center.set_rotation(math.sin(elapsed_time * 0.5) * 0.1, 0.0, 0.0)
            frame3d_right.set_rotation(0.0, -0.2 + math.sin(elapsed_time) * 0.15, 0.0)
            
            # Animate Frame3D positions (gentle floating)
            frame3d_left.set_position(-350.0, math.sin(elapsed_time * 0.8) * 30.0, -100.0 + math.cos(elapsed_time * 0.6) * 20.0)
            frame3d_center.set_position(0.0, math.sin(elapsed_time * 0.6 + 1.0) * 25.0, 50.0 + math.sin(elapsed_time * 0.4) * 30.0)
            frame3d_right.set_position(350.0, math.sin(elapsed_time * 0.7 + 2.0) * 30.0, -100.0 + math.cos(elapsed_time * 0.5) * 20.0)
            
            # Animate nested frame position (vertical oscillation)
            offset_y = math.sin(elapsed_time * 2.0) * 30.0
            nested_frame.set_position(150.0, 310.0 + offset_y)
            
            # Animate carousel items (staggered vertical movement)
            for i, item in enumerate(carousel_items):
                item_offset = math.sin(elapsed_time * 1.5 + i * 0.5) * 15.0
                item.set_position(140.0, 100.0 + i * 80.0 + item_offset)
        # When animation is disabled, positions remain frozen at their current state
        
        if renderer.begin_frame():
            # Render entire scene with automatic tree traversal
            renderer.render_scene(scene)
            
            renderer.end_frame()
            frame_count += 1
            
            # Capture frames only if enabled
            if args.capture and output_dir:
                # Auto-capture initial frame to verify rendering
                if frame_count == initial_capture_frame:
                    capture_filename = os.path.join(output_dir, "hierarchy_demo_initial.png")
                    if renderer.save_capture(capture_filename):
                        print(f"✓ Auto-captured initial frame: {capture_filename}")
                        capture_count += 1
                    else:
                        print("✗ Failed to capture initial frame")
                
                # Auto-capture every 120 frames (about every 2 seconds at 60fps)
                if frame_count > initial_capture_frame and frame_count % 120 == 0:
                    capture_filename = os.path.join(output_dir, f"hierarchy_demo_frame_{frame_count:05d}.png")
                    if renderer.save_capture(capture_filename):
                        print(f"✓ Captured frame {frame_count}: {capture_filename}")
                        capture_count += 1
    
    # Capture final frame and analysis only if capture mode enabled
    if args.capture and output_dir:
        print("\nCapturing final frame...")
        final_filename = os.path.join(output_dir, "hierarchy_demo_final.png")
        if renderer.save_capture(final_filename):
            print(f"✓ Final frame saved: {final_filename}")
            capture_count += 1
        
        # Demonstrate raw pixel data capture
        print("\nCapturing raw pixel data for analysis...")
        data, width, height = renderer.capture_frame()
        
        if data is not None:
            print(f"✓ Captured {width}x{height} frame ({len(data)} bytes)")
            print(f"  Format: BGRA (4 bytes per pixel)")
            
            # Analyze some pixels
            import struct
            pixels = struct.unpack(f'{len(data)}B', data)
            
            # Sample center pixel
            center_x = width // 2
            center_y = height // 2
            center_offset = (center_y * width + center_x) * 4
            
            b = pixels[center_offset]
            g = pixels[center_offset + 1]
            r = pixels[center_offset + 2]
            a = pixels[center_offset + 3]
            
            print(f"  Center pixel (BGRA): ({b}, {g}, {r}, {a})")
            
            # Calculate average color
            total_r = sum(pixels[i+2] for i in range(0, len(pixels), 4))
            total_g = sum(pixels[i+1] for i in range(0, len(pixels), 4))
            total_b = sum(pixels[i] for i in range(0, len(pixels), 4))
            
            num_pixels = width * height
            avg_r = total_r / num_pixels
            avg_g = total_g / num_pixels
            avg_b = total_b / num_pixels
            
            print(f"  Average color: R={avg_r:.1f}, G={avg_g:.1f}, B={avg_b:.1f}")
        else:
            print("✗ Failed to capture raw pixel data")
        
        print(f"\nRendered {frame_count} frames")
        print(f"Captured {capture_count} images to {output_dir}")
    else:
        print(f"\nRendered {frame_count} frames")
    
    renderer.shutdown()
    print("Renderer shutdown complete")

if __name__ == "__main__":
    main()
