# OpenGL Backend Setup - Quick Start

This is a quick reference for setting up the OpenGL backend.

## Installation

### Step 1: Install GLFW

```bash
# macOS
brew install glfw

# Linux (Ubuntu/Debian)
sudo apt-get install libglfw3-dev

# Linux (Fedora)
sudo dnf install glfw-devel
```

### Step 2: Verify GLFW Installation

```bash
# Check where GLFW is installed
brew --prefix glfw  # macOS
pkg-config --cflags glfw3  # Linux
```

### Step 3: Build with OpenGL Backend

```bash
# Clean previous builds
make clean

# Build with OpenGL
make build-opengl
```

### Step 4: Test

```bash
# Test backend availability
python3 tests/test_backend_selection.py

# Should show:
# ✓ OpenGL backend available
```

## Usage

```python
import sys
sys.path.insert(0, 'build')
import cyber_ui_core as ui

# Create OpenGL renderer
renderer = ui.create_opengl_renderer()
renderer.initialize(800, 600, "OpenGL Demo")

# ... your rendering code ...

renderer.shutdown()
```

## Switching Between Backends

```bash
# Build with Metal (default)
make clean && make build-metal

# Build with OpenGL
make clean && make build-opengl
```

## Troubleshooting

**Error: "GLFW/glfw3.h not found"**
- Install GLFW: `brew install glfw`

**Error: "create_opengl_renderer not found"**
- Rebuild: `make clean && make build-opengl`

**Error: Linker cannot find -lglfw**
- Check GLFW path: `brew --prefix glfw`
- Update Makefile if needed

## Complete Example

```bash
# Full setup from scratch
brew install glfw
cd ~/projects/cyber-ui-toolkit
make clean
make build-opengl
python3 tests/test_backend_selection.py
```

## See Also

- [Backend Selection Guide](BACKEND_SELECTION.md) - Detailed guide
- [OpenGL Backend](OPENGL_BACKEND.md) - Implementation details
