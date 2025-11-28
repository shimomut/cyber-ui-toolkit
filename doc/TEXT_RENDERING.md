# Text Rendering

This document describes the Text and Font classes in the Cyber UI Toolkit.

## Overview

The Text class is a child of Object2D, allowing text to be positioned, hierarchically organized, and rendered within the 2D scene graph. Font objects can be associated with Text objects to control typography.

## Font Class

The Font class manages font resources and properties.

### Creating a Font

```python
import cyber_ui_core as ui

# Create a font object
font = ui.Font()

# Load from file with size
font.load_from_file("/System/Library/Fonts/Helvetica.ttc", 24.0)
```

### Font Properties

```python
# Set font size
font.set_size(32.0)
size = font.get_size()

# Font style
font.set_bold(True)
font.set_italic(True)

# Check if loaded
if font.is_loaded():
    print(f"Font: {font.get_file_path()}")
```

## Text Class

The Text class renders text content with associated font and styling.

### Creating Text

```python
# Create text with initial content
text = ui.Text("Hello, World!")

# Or create empty and set later
text = ui.Text()
text.set_text("Hello, World!")
```

### Text Properties

```python
# Position (inherited from Object2D)
text.set_position(100, 50)
x, y = text.get_position()

# Color (RGBA)
text.set_color(1.0, 0.0, 0.0, 1.0)  # Red
r, g, b, a = text.get_color()

# Visibility (inherited from Object2D)
text.set_visible(True)
visible = text.is_visible()

# Name for debugging (inherited from Object2D)
text.set_name("title_text")
name = text.get_name()
```

### Font Association

```python
# Associate a font with text
font = ui.Font()
font.load_from_file("/path/to/font.ttf", 18.0)
text.set_font(font)

# Check if text has a font
if text.has_font():
    current_font = text.get_font()
```

### Text Alignment

```python
# Set alignment
text.set_alignment(ui.TextAlignment.Left)
text.set_alignment(ui.TextAlignment.Center)
text.set_alignment(ui.TextAlignment.Right)

# Get current alignment
alignment = text.get_alignment()
```

## Hierarchy Support

Since Text inherits from Object2D, it supports the full scene graph hierarchy:

```python
# Create parent-child relationships
parent_text = ui.Text("Parent")
child_text = ui.Text("Child")
parent_text.add_child(child_text)

# Remove from hierarchy
parent_text.remove_child(child_text)

# Get parent
parent = child_text.get_parent()

# Render hierarchy
parent_text.render()  # Renders parent and all children
```

## Complete Example

```python
import cyber_ui_core as ui

# Create fonts
title_font = ui.Font()
title_font.load_from_file("/System/Library/Fonts/Helvetica.ttc", 32.0)
title_font.set_bold(True)

body_font = ui.Font()
body_font.load_from_file("/System/Library/Fonts/Helvetica.ttc", 16.0)

# Create title text
title = ui.Text("Welcome to Cyber UI")
title.set_name("title")
title.set_position(100, 50)
title.set_color(1.0, 1.0, 1.0, 1.0)  # White
title.set_font(title_font)
title.set_alignment(ui.TextAlignment.Center)

# Create body text as child
body = ui.Text("This is a text rendering demo")
body.set_name("body")
body.set_position(0, 50)  # Relative to parent
body.set_color(0.8, 0.8, 0.8, 1.0)  # Light gray
body.set_font(body_font)
body.set_alignment(ui.TextAlignment.Left)

# Build hierarchy
title.add_child(body)

# Render
title.render()
```

## Implementation Notes

- **Current Rendering**: Text objects are rendered using Core Text/Core Graphics
  - Each text string is rendered to a bitmap texture using macOS system fonts
  - The texture is then rendered as a textured quad in Metal
  - Text color is applied through vertex colors
  - Font size and bold style are supported
  - Text is rendered with proper anti-aliasing
- **Font Loading**: Currently accepts file paths but uses system fonts for rendering
- **Performance**: Each text object generates a new texture per frame (not cached)
- **Future Enhancements**:
  - Font atlas generation for better performance
  - Texture caching to avoid regenerating unchanged text
  - Support for custom font files (TTF/OTF)
  - Advanced text features (kerning, ligatures, multi-line)
  - Text metrics and bounding box queries

## Future Enhancements

- Font atlas generation and caching
- Text metrics and bounding box calculation
- Multi-line text support
- Text wrapping and overflow handling
- Rich text formatting (bold, italic, underline)
- Unicode and emoji support
- Kerning and ligature support
