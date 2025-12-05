# Quick Start - OpenGL Backend

This guide shows you how to build and run the Cyber UI Toolkit with the OpenGL backend.

## Prerequisites

Install GLFW:
```bash
brew install glfw
```

## Build with OpenGL

```bash
# Clean any previous builds
make clean

# Build with OpenGL backend
make build-opengl
```

## Verify Installation

```bash
# Test that OpenGL backend is available
python3 tests/test_backend_selection.py

# Should show:
# ✓ OpenGL backend available
```

## Run Samples

### Option 1: Use OpenGL-specific targets (Recommended)

```bash
# These will automatically build with OpenGL if needed
make run-hierarchy-opengl
make run-clipping-opengl
```

### Option 2: Build first, then run

```bash
# Build with OpenGL
make build-opengl

# Run samples (will use OpenGL build)
make run-hierarchy
make run-clipping
```

## Switching Between Backends

```bash
# Switch to Metal
make clean && make build-metal
make run-hierarchy  # Uses Metal

# Switch to OpenGL
make clean && make build-opengl
make run-hierarchy  # Uses OpenGL
```

## Common Issues

### "symbol not found" error

**Problem**: Library was built with different backend than expected

**Solution**: Clean and rebuild
```bash
make clean
make build-opengl
```

### "GLFW/glfw3.h not found"

**Problem**: GLFW not installed

**Solution**: Install GLFW
```bash
brew install glfw
```

## Testing

```bash
# Quick test
python3 tests/test_opengl_simple.py

# Full backend test
python3 tests/test_backend_selection.py
```

## Summary

**To use OpenGL backend:**
1. `brew install glfw`
2. `make clean && make build-opengl`
3. `make run-hierarchy-opengl`

That's it! The samples will automatically detect and use the OpenGL backend.
