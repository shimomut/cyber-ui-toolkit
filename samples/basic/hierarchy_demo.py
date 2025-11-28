#!/usr/bin/env python3
"""
Hierarchy Demo - Demonstrates Frame3D, Frame2D, and Rectangle hierarchy

This sample shows:
- Frame3D for 3D positioning
- Frame2D containers with clipping
- Nested Frame2D structures
- Rectangle shapes with colors and textures
- Parent-child relationships and relative positioning
"""

import sys
sys.path.insert(0, '../../build')

import cyber_ui_core as ui
from PIL import Image as PILImage
import os
import math

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
    print("=== Cyber UI Toolkit - 3D Hierarchy Demo ===\n")
    
    # Initialize renderer
    renderer = ui.create_metal_renderer()
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
    frame3d_left = ui.Frame3D()
    frame3d_left.set_name("Frame3D_Left")
    frame3d_left.set_position(-350.0, 0.0, -100.0)
    frame3d_left.set_rotation(0.0, 0.2, 0.0)  # Rotated to face camera
    frame3d_left.set_scale(1.0, 1.0, 1.0)
    print("✓ Created Frame3D: Frame3D_Left (pos: -350, 0, -100, rot: 0, 0.2, 0)")
    
    # Frame3D #2 - Center section (positioned at center, closer to camera)
    frame3d_center = ui.Frame3D()
    frame3d_center.set_name("Frame3D_Center")
    frame3d_center.set_position(0.0, 0.0, 50.0)
    frame3d_center.set_rotation(0.0, 0.0, 0.0)  # Facing camera directly
    frame3d_center.set_scale(1.0, 1.0, 1.0)
    print("✓ Created Frame3D: Frame3D_Center (pos: 0, 0, 50, rot: 0, 0, 0)")
    
    # Frame3D #3 - Right section (positioned right and rotated opposite)
    frame3d_right = ui.Frame3D()
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
    left_panel = ui.Frame2D()
    left_panel.set_name("LeftPanel")
    left_panel.set_position(50.0, 50.0)
    left_panel.set_size(250.0, 650.0)
    left_panel.set_clipping_enabled(True)
    print("✓ Created Frame2D: LeftPanel (with clipping)")
    
    # Background for left panel
    left_bg = ui.Rectangle(250.0, 650.0)
    left_bg.set_name("LeftPanelBackground")
    left_bg.set_position(0.0, 0.0)
    left_bg.set_color(0.15, 0.15, 0.2, 1.0)
    left_panel.add_child(left_bg)
    
    # Title rectangle in left panel
    title_rect = ui.Rectangle(230.0, 50.0)
    title_rect.set_name("TitleRect")
    title_rect.set_position(10.0, 10.0)
    title_rect.set_color(0.3, 0.5, 0.8, 1.0)
    if gradient_img:
        title_rect.set_image(gradient_img)
    left_panel.add_child(title_rect)
    
    # Content rectangles in left panel
    for i in range(6):
        content_rect = ui.Rectangle(210.0, 80.0)
        content_rect.set_name(f"ContentRect{i+1}")
        content_rect.set_position(20.0, 80.0 + i * 95.0)
        
        # Alternate colors
        if i % 2 == 0:
            content_rect.set_color(0.2, 0.4, 0.6, 1.0)
        else:
            content_rect.set_color(0.3, 0.3, 0.5, 1.0)
        
        if checker_img and i == 2:
            content_rect.set_image(checker_img)
        
        left_panel.add_child(content_rect)
    
    frame3d_left.add_child(left_panel)
    print("  └─ Added 7 rectangles to LeftPanel")
    
    # ===== Frame3D Center - Nested Grid Panel =====
    center_panel = ui.Frame2D()
    center_panel.set_name("CenterPanel")
    center_panel.set_position(350.0, 100.0)
    center_panel.set_size(300.0, 550.0)
    center_panel.set_clipping_enabled(False)
    print("✓ Created Frame2D: CenterPanel (no clipping)")
    
    # Background
    center_bg = ui.Rectangle(300.0, 550.0)
    center_bg.set_name("CenterBackground")
    center_bg.set_position(0.0, 0.0)
    center_bg.set_color(0.1, 0.15, 0.15, 1.0)
    center_panel.add_child(center_bg)
    
    # Header
    center_header = ui.Rectangle(280.0, 60.0)
    center_header.set_name("CenterHeader")
    center_header.set_position(10.0, 10.0)
    center_header.set_color(0.4, 0.3, 0.6, 1.0)
    if gradient_img:
        center_header.set_image(gradient_img)
    center_panel.add_child(center_header)
    
    # Nested Frame2D inside center panel
    nested_frame = ui.Frame2D()
    nested_frame.set_name("NestedFrame")
    nested_frame.set_position(10.0, 90.0)
    nested_frame.set_size(280.0, 440.0)
    nested_frame.set_clipping_enabled(True)
    print("  ✓ Created nested Frame2D: NestedFrame (with clipping)")
    
    # Nested frame background
    nested_bg = ui.Rectangle(280.0, 440.0)
    nested_bg.set_name("NestedBackground")
    nested_bg.set_position(0.0, 0.0)
    nested_bg.set_color(0.2, 0.25, 0.25, 1.0)
    nested_frame.add_child(nested_bg)
    
    # Grid of rectangles in nested frame (4x4)
    for row in range(4):
        for col in range(4):
            grid_rect = ui.Rectangle(60.0, 60.0)
            grid_rect.set_name(f"GridRect_{row}_{col}")
            grid_rect.set_position(10.0 + col * 67.0, 10.0 + row * 67.0)
            
            # Color based on position
            r = 0.3 + (col / 4.0) * 0.5
            g = 0.3 + (row / 4.0) * 0.5
            b = 0.5
            grid_rect.set_color(r, g, b, 1.0)
            
            # Add textures to some rectangles
            if (row + col) % 3 == 0 and icon_img:
                grid_rect.set_image(icon_img)
            elif (row + col) % 3 == 1 and checker_img:
                grid_rect.set_image(checker_img)
            
            nested_frame.add_child(grid_rect)
    
    center_panel.add_child(nested_frame)
    frame3d_center.add_child(center_panel)
    print("    └─ Added 4x4 grid (16 rectangles) to NestedFrame")
    
    # ===== Frame3D Right - Carousel Panel =====
    right_panel = ui.Frame2D()
    right_panel.set_name("RightPanel")
    right_panel.set_position(700.0, 150.0)
    right_panel.set_size(280.0, 450.0)
    right_panel.set_clipping_enabled(True)
    print("✓ Created Frame2D: RightPanel (with clipping)")
    
    # Background
    right_bg = ui.Rectangle(280.0, 450.0)
    right_bg.set_name("RightBackground")
    right_bg.set_position(0.0, 0.0)
    right_bg.set_color(0.15, 0.2, 0.15, 1.0)
    right_panel.add_child(right_bg)
    
    # Create a carousel-like layout with overlapping rectangles
    carousel_items = []
    for i in range(5):
        item = ui.Rectangle(240.0, 140.0)
        item.set_name(f"CarouselItem{i+1}")
        item.set_position(20.0, 30.0 + i * 80.0)
        
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
    print("Starting render loop with 3D animation...")
    print("Watch the panels rotate and move in 3D space!")
    print("Press SPACE to capture a frame, or ESC/close window to exit\n")
    
    # Create output directory for captures
    output_dir = os.path.join(script_dir, "..", "output")
    os.makedirs(output_dir, exist_ok=True)
    
    frame_count = 0
    capture_count = 0
    
    # Capture initial frame after a few frames to ensure everything is loaded
    initial_capture_frame = 5
    
    while not renderer.should_close():
        renderer.poll_events()
        
        time = frame_count * 0.001
        
        # Animate Frame3D rotations
        frame3d_left.set_rotation(0.0, 0.2 + math.sin(time) * 0.15, 0.0)
        frame3d_center.set_rotation(math.sin(time * 0.5) * 0.1, 0.0, 0.0)
        frame3d_right.set_rotation(0.0, -0.2 + math.sin(time) * 0.15, 0.0)
        
        # Animate Frame3D positions (gentle floating)
        frame3d_left.set_position(-350.0, math.sin(time * 0.8) * 30.0, -100.0 + math.cos(time * 0.6) * 20.0)
        frame3d_center.set_position(0.0, math.sin(time * 0.6 + 1.0) * 25.0, 50.0 + math.sin(time * 0.4) * 30.0)
        frame3d_right.set_position(350.0, math.sin(time * 0.7 + 2.0) * 30.0, -100.0 + math.cos(time * 0.5) * 20.0)
        
        # Animate nested frame position (vertical oscillation)
        offset_y = math.sin(time * 2.0) * 30.0
        nested_frame.set_position(10.0, 90.0 + offset_y)
        
        # Animate carousel items (staggered vertical movement)
        for i, item in enumerate(carousel_items):
            item_offset = math.sin(time * 1.5 + i * 0.5) * 15.0
            item.set_position(20.0, 30.0 + i * 80.0 + item_offset)
        
        if renderer.begin_frame():
            # Render entire scene with automatic tree traversal
            renderer.render_scene(scene)
            
            renderer.end_frame()
            frame_count += 1
            
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
    
    # Capture final frame
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
    renderer.shutdown()
    print("Renderer shutdown complete")

if __name__ == "__main__":
    main()
