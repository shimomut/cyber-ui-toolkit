#!/usr/bin/env python3
"""
Test OpenGL backend availability and basic functionality.
Note: Requires GLFW to be installed (brew install glfw on macOS).
"""

import sys
import os

# Add build directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build'))

try:
    import cyber_ui_core as ui
    
    # Check if OpenGL backend is available
    try:
        renderer = ui.create_opengl_renderer()
        print("✓ OpenGL backend is available")
        
        # Test initialization
        if renderer.initialize(800, 600, "OpenGL Test"):
            print("✓ OpenGL renderer initialized successfully")
            renderer.shutdown()
        else:
            print("✗ Failed to initialize OpenGL renderer")
            sys.exit(1)
            
    except AttributeError:
        print("✗ OpenGL backend not compiled (GLFW not installed)")
        print("  Install GLFW: brew install glfw")
        print("  Then rebuild: make clean && make build-opengl")
        sys.exit(1)
        
except ImportError as e:
    print(f"✗ Failed to import cyber_ui_core: {e}")
    print("  Build the library first: make build")
    sys.exit(1)

print("\nOpenGL backend test passed!")
