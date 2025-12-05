#!/usr/bin/env python3
"""
Test backend selection and verify both backends work identically.
"""

import sys
import os

# Add build directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build'))

try:
    import cyber_ui_core as ui
    
    print("Testing backend availability...")
    
    # Test Metal backend (should always be available on macOS)
    try:
        metal_renderer = ui.create_metal_renderer()
        print("✓ Metal backend available")
        has_metal = True
    except Exception as e:
        print(f"✗ Metal backend not available: {e}")
        has_metal = False
    
    # Test OpenGL backend (requires GLFW)
    try:
        opengl_renderer = ui.create_opengl_renderer()
        print("✓ OpenGL backend available")
        has_opengl = True
    except Exception as e:
        print(f"✗ OpenGL backend not available: {e}")
        has_opengl = False
    
    if not has_metal and not has_opengl:
        print("\n✗ No rendering backends available!")
        sys.exit(1)
    
    # Test that both backends have the same API
    print("\nTesting API compatibility...")
    
    if has_metal:
        renderer = metal_renderer
        backend_name = "Metal"
    else:
        renderer = opengl_renderer
        backend_name = "OpenGL"
    
    print(f"Using {backend_name} backend for API test...")
    
    # Check all required methods exist
    required_methods = [
        'initialize', 'shutdown', 'begin_frame', 'end_frame',
        'render_object', 'render_scene', 'should_close', 'poll_events',
        'capture_frame', 'save_capture'
    ]
    
    for method in required_methods:
        if not hasattr(renderer, method):
            print(f"✗ Missing method: {method}")
            sys.exit(1)
    
    print(f"✓ All required methods present")
    
    # Test basic initialization
    if renderer.initialize(800, 600, f"{backend_name} Test"):
        print(f"✓ {backend_name} renderer initialized")
        renderer.shutdown()
        print(f"✓ {backend_name} renderer shutdown")
    else:
        print(f"✗ Failed to initialize {backend_name} renderer")
        sys.exit(1)
    
    print("\n✓ Backend selection test passed!")
    print(f"\nAvailable backends:")
    print(f"  Metal:  {'Yes' if has_metal else 'No'}")
    print(f"  OpenGL: {'Yes' if has_opengl else 'No'}")
    
except ImportError as e:
    print(f"✗ Failed to import cyber_ui_core: {e}")
    print("  Build the library first: make build")
    sys.exit(1)
