---
inclusion: always
---

# Cyber UI Toolkit - Project Structure

This steering document defines the standard directory structure for the Cyber UI Toolkit project, a GUI toolkit library using 3D API backend.

## Architecture Overview

The library consists of two layers:

**Layer 1: Graphics Primitive Rendering (C++)**
- Low-level 3D graphics API integration (Metal/Vulkan/OpenGL)
- High-performance rendering primitives
- Buffer and resource management
- Shader compilation and management
- Python bindings via pybind11

**Layer 2: UI Toolkit (Python)**
- Widget system and components
- Layout management
- Event handling and input
- Theme and styling system
- Application-level API

**Applications (Python)**
- Built on top of Layer 2
- Pure Python for ease of development

## Directory Structure

```
cyber-ui-toolkit/
├── src/                    # Source code
│   ├── core/              # Core UI components and systems
│   ├── rendering/         # 3D rendering backend (Vulkan/Metal/DirectX)
│   ├── widgets/           # UI widget implementations
│   ├── layout/            # Layout management system
│   ├── events/            # Event handling system
│   ├── themes/            # Theming and styling
│   └── utils/             # Utility functions and helpers
├── test/                   # Test files
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── fixtures/          # Test fixtures and mock data
├── doc/                    # Documentation
│   ├── api/               # API reference documentation
│   ├── guides/            # User guides and tutorials
│   └── architecture/      # Architecture documentation
├── dev/                    # Development tools and scripts
│   ├── scripts/           # Build and utility scripts
│   └── configs/           # Development configurations
├── tools/                  # Development tooling
│   ├── profiler/          # Performance profiling tools
│   └── debugger/          # Debugging utilities
├── samples/                # Example applications
│   ├── basic/             # Basic usage examples
│   ├── advanced/          # Advanced feature demonstrations
│   └── showcase/          # Full application showcases
└── README.md              # Project overview and quick start
```

## File Organization Guidelines

### Source Code (src/)
- Keep core functionality separate from rendering backend
- Each widget should have its own file in `src/widgets/`
- Rendering backend implementations go in `src/rendering/`
- Use clear, descriptive names for all modules

### Tests (test/)
- Mirror the src/ structure in test directories
- Name test files with `.test` or `.spec` suffix
- Keep unit tests focused and isolated
- Integration tests should cover cross-component interactions

### Documentation (doc/)
- API docs should be auto-generated from source comments
- Guides should be practical and example-driven
- Architecture docs explain design decisions and patterns

### Samples (samples/)
- Each sample should be self-contained and runnable
- Include README in each sample directory
- Demonstrate specific features or use cases

## Naming Conventions

- Use lowercase with hyphens for directories: `event-system/`
- Use PascalCase for class/component files: `Button.cpp`, `Window.h`
- Use camelCase for utility files: `mathHelpers.cpp`
- Prefix test files with component name: `Button.test.cpp`

## When Creating New Files

Always place files in the appropriate directory based on their purpose:
- UI components → `src/widgets/`
- Rendering code → `src/rendering/`
- Tests → `test/unit/` or `test/integration/`
- Examples → `samples/`
- Documentation → `doc/`
