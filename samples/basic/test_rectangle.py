#!/usr/bin/env python3
"""
Basic example demonstrating Rectangle rendering
"""

import sys
sys.path.insert(0, '../../build')

import cyber_ui_core as ui

def main():
    print("=== Cyber UI Toolkit - Rectangle Test ===\n")
    
    # Create a rectangle
    rect = ui.Rectangle(200, 100)
    rect.set_name("MyRectangle")
    rect.set_position(10, 20, 0)
    rect.set_color(1.0, 0.0, 0.0, 1.0)  # Red
    
    # Create a child rectangle
    child_rect = ui.Rectangle(50, 50)
    child_rect.set_name("ChildRectangle")
    child_rect.set_position(5, 5, 0)
    child_rect.set_color(0.0, 0.0, 1.0, 1.0)  # Blue
    
    # Build hierarchy
    rect.add_child(child_rect)
    
    # Test getters
    print(f"Rectangle name: {rect.get_name()}")
    print(f"Position: {rect.get_position()}")
    print(f"Size: {rect.get_size()}")
    print(f"Color: {rect.get_color()}")
    print(f"Visible: {rect.is_visible()}\n")
    
    # Render
    print("Rendering scene:")
    rect.render()

if __name__ == "__main__":
    main()
