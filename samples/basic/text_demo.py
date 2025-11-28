#!/usr/bin/env python3
"""
Text and Font Demo
Demonstrates the Text class (child of Object2D) and Font class usage with rendering loop.
"""

import sys
sys.path.insert(0, '../../build')

import cyber_ui_core as ui
import math

def main():
    print("=== Text and Font Demo ===\n")
    
    # Initialize renderer
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(800, 600, "Cyber UI - Text Demo"):
        print("Failed to initialize renderer")
        return
    
    print("Renderer initialized successfully!")
    print("Press ESC or close window to exit\n")
    
    # Create scene root and camera
    scene = ui.SceneRoot()
    camera = scene.get_camera()
    camera.set_position(0.0, 0.0, 800.0)
    camera.set_perspective(1.0472, 800.0/600.0, 0.1, 2000.0)  # 60 degrees FOV
    print("✓ Camera configured\n")
    
    # Create Frame3D container
    frame3d = ui.Frame3D()
    frame3d.set_name("TextFrame3D")
    frame3d.set_position(0.0, 0.0, 0.0)
    scene.add_frame3d(frame3d)
    
    # Create Frame2D for 2D layout
    frame2d = ui.Frame2D()
    frame2d.set_name("TextFrame2D")
    frame2d.set_position(50.0, 50.0)
    frame2d.set_size(700.0, 500.0)
    frame2d.set_clipping_enabled(False)
    frame3d.add_child(frame2d)
    
    # Create fonts
    print("Loading fonts...")
    font = ui.Font()
    font.load_from_file("/System/Library/Fonts/Helvetica.ttc", 24.0)
    print(f"✓ Font loaded: {font.get_file_path()} (size: {font.get_size()})")
    
    bold_font = ui.Font()
    bold_font.load_from_file("/System/Library/Fonts/Helvetica.ttc", 32.0)
    bold_font.set_bold(True)
    print(f"✓ Bold font loaded (size: {bold_font.get_size()})")
    
    small_font = ui.Font()
    small_font.load_from_file("/System/Library/Fonts/Helvetica.ttc", 16.0)
    print(f"✓ Small font loaded (size: {small_font.get_size()})\n")
    
    # Create text objects
    print("Creating text objects...")
    
    # Title text
    title = ui.Text("Cyber UI Text Rendering")
    title.set_name("title")
    title.set_position(50.0, 20.0)
    title.set_color(1.0, 1.0, 1.0, 1.0)  # White
    title.set_font(bold_font)
    title.set_alignment(ui.TextAlignment.Left)
    frame2d.add_child(title)
    print("✓ Created title text")
    
    # Left-aligned text
    text_left = ui.Text("Left Aligned Text")
    text_left.set_name("text_left")
    text_left.set_position(50.0, 100.0)
    text_left.set_color(1.0, 0.3, 0.3, 1.0)  # Red
    text_left.set_font(font)
    text_left.set_alignment(ui.TextAlignment.Left)
    frame2d.add_child(text_left)
    print("✓ Created left-aligned text")
    
    # Center-aligned text
    text_center = ui.Text("Center Aligned Text")
    text_center.set_name("text_center")
    text_center.set_position(350.0, 180.0)
    text_center.set_color(0.3, 1.0, 0.3, 1.0)  # Green
    text_center.set_font(font)
    text_center.set_alignment(ui.TextAlignment.Center)
    frame2d.add_child(text_center)
    print("✓ Created center-aligned text")
    
    # Right-aligned text
    text_right = ui.Text("Right Aligned Text")
    text_right.set_name("text_right")
    text_right.set_position(650.0, 260.0)
    text_right.set_color(0.3, 0.3, 1.0, 1.0)  # Blue
    text_right.set_font(font)
    text_right.set_alignment(ui.TextAlignment.Right)
    frame2d.add_child(text_right)
    print("✓ Created right-aligned text")
    
    # Animated text
    animated_text = ui.Text("Animated Text")
    animated_text.set_name("animated_text")
    animated_text.set_position(350.0, 340.0)
    animated_text.set_color(1.0, 0.8, 0.2, 1.0)  # Yellow
    animated_text.set_font(bold_font)
    animated_text.set_alignment(ui.TextAlignment.Center)
    frame2d.add_child(animated_text)
    print("✓ Created animated text")
    
    # Info text
    info_text = ui.Text("Frame counter will appear here")
    info_text.set_name("info_text")
    info_text.set_position(50.0, 450.0)
    info_text.set_color(0.7, 0.7, 0.7, 1.0)  # Gray
    info_text.set_font(small_font)
    info_text.set_alignment(ui.TextAlignment.Left)
    frame2d.add_child(info_text)
    print("✓ Created info text")
    
    print("\n" + "="*60)
    print("Scene Hierarchy:")
    print("="*60)
    print("Frame3D (TextFrame3D)")
    print("└── Frame2D (TextFrame2D)")
    print("    ├── Text (title) - Bold, White")
    print("    ├── Text (text_left) - Red, Left-aligned")
    print("    ├── Text (text_center) - Green, Center-aligned")
    print("    ├── Text (text_right) - Blue, Right-aligned")
    print("    ├── Text (animated_text) - Yellow, Animated")
    print("    └── Text (info_text) - Gray, Small font")
    print("="*60)
    print()
    
    # Render loop
    print("Starting render loop with text animation...")
    print("Watch the text animate!\n")
    frame_count = 0
    
    while not renderer.should_close():
        renderer.poll_events()
        
        time = frame_count * 0.02
        
        # Animate text position (floating effect)
        offset_y = math.sin(time * 2.0) * 20.0
        animated_text.set_position(350.0, 340.0 + offset_y)
        
        # Animate text color (pulsing effect)
        pulse = (math.sin(time * 3.0) + 1.0) * 0.5  # 0 to 1
        animated_text.set_color(1.0, 0.5 + pulse * 0.5, 0.2, 1.0)
        
        # Animate left text position (horizontal slide)
        slide_x = 50.0 + math.sin(time) * 30.0
        text_left.set_position(slide_x, 100.0)
        
        # Rotate Frame3D slightly for 3D effect
        frame3d.set_rotation(math.sin(time * 0.5) * 0.05, math.cos(time * 0.3) * 0.05, 0.0)
        
        # Update info text with frame count
        info_text.set_text(f"Frame: {frame_count} | Time: {time:.2f}s")
        
        if renderer.begin_frame():
            # Render entire scene
            renderer.render_scene(scene)
            
            renderer.end_frame()
            frame_count += 1
    
    print(f"\nRendered {frame_count} frames")
    renderer.shutdown()
    print("Renderer shutdown complete")

if __name__ == "__main__":
    main()
