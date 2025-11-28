#!/usr/bin/env python3
"""
Basic example demonstrating Rectangle rendering with Metal backend
"""

import sys
sys.path.insert(0, '../../build')

import cyber_ui_core as ui

def main():
    print("=== Cyber UI Toolkit - Rectangle Test ===\n")
    
    # Create Metal renderer
    renderer = ui.create_metal_renderer()
    if not renderer.initialize(800, 600, "Cyber UI - Rectangle Demo"):
        print("Failed to initialize renderer")
        return
    
    print("Renderer initialized successfully!")
    print("Press ESC or close window to exit\n")
    
    # Create rectangles
    rect1 = ui.Rectangle(200, 150)
    rect1.set_name("RedRectangle")
    rect1.set_position(100, 100, 0)
    rect1.set_color(1.0, 0.0, 0.0, 1.0)  # Red
    
    rect2 = ui.Rectangle(150, 100)
    rect2.set_name("GreenRectangle")
    rect2.set_position(400, 200, 0)
    rect2.set_color(0.0, 1.0, 0.0, 1.0)  # Green
    
    rect3 = ui.Rectangle(100, 200)
    rect3.set_name("BlueRectangle")
    rect3.set_position(300, 350, 0)
    rect3.set_color(0.0, 0.0, 1.0, 1.0)  # Blue
    
    # Create a parent with children
    parent = ui.Rectangle(120, 80)
    parent.set_name("ParentRectangle")
    parent.set_position(550, 50, 0)
    parent.set_color(1.0, 1.0, 0.0, 1.0)  # Yellow
    
    child = ui.Rectangle(60, 40)
    child.set_name("ChildRectangle")
    child.set_position(580, 150, 0)
    child.set_color(1.0, 0.0, 1.0, 1.0)  # Magenta
    
    parent.add_child(child)
    
    # Render loop
    frame_count = 0
    while not renderer.should_close():
        renderer.poll_events()
        
        if renderer.begin_frame():
            # Render all rectangles
            renderer.render_object(rect1)
            renderer.render_object(rect2)
            renderer.render_object(rect3)
            renderer.render_object(parent)
            
            renderer.end_frame()
            frame_count += 1
    
    print(f"\nRendered {frame_count} frames")
    renderer.shutdown()
    print("Renderer shutdown complete")

if __name__ == "__main__":
    main()
