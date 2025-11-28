# Text Rendering Samples

This document describes the text rendering sample in `samples/basic/text_demo.py`.

## Text Demo (`samples/basic/text_demo.py`)

Demonstrates the Text and Font classes with a live rendering loop, including:
- Font creation and loading with different sizes
- Text object creation with various properties
- Color and alignment settings (left, center, right)
- Font association with text objects
- Scene hierarchy with Frame3D and Frame2D
- Animated text with position and color effects
- Dynamic text updates (frame counter)
- 3D rotation effects on text containers

### Running the Sample

```bash
make run-text
```

Or directly:

```bash
PYTHONPATH=build python3 samples/basic/text_demo.py
```

### What It Demonstrates

1. **Renderer Setup**: Initializes Metal renderer with window and camera
2. **Font Loading**: Creates Font objects with different sizes (16pt, 24pt, 32pt)
3. **Text Creation**: Creates multiple Text objects with different content and styles
4. **Styling**: Sets colors (white, red, green, blue, yellow, gray) and alignments (left, center, right)
5. **Font Styles**: Demonstrates bold font usage for title and animated text
6. **Scene Hierarchy**: Builds Frame3D → Frame2D → Text hierarchy
7. **Animation**: Animates text position (floating, sliding) and color (pulsing)
8. **3D Effects**: Rotates the Frame3D container for subtle 3D movement
9. **Dynamic Updates**: Updates frame counter text in real-time
10. **Rendering Loop**: Continuous rendering with event polling

### Expected Output

The sample displays:
- A window with animated text rendered using actual glyphs
- Text strings are rendered with proper anti-aliasing and font rendering
- Different font sizes (16pt, 24pt, 32pt) are visible
- Bold text is rendered with heavier weight
- Text colors (white, red, green, blue, yellow, gray) are applied
- Smooth animations: floating, sliding, color pulsing, and 3D rotation
- Frame counter updates in real-time showing dynamic text updates
- Console logs showing font loading and scene hierarchy

**Implementation**: Text is rendered using Core Text/Core Graphics to generate textures, which are then displayed as textured quads in Metal.

### Code Structure

```python
# Create and load fonts
font = ui.Font()
font.load_from_file("/System/Library/Fonts/Helvetica.ttc", 24.0)

# Create text with properties
text = ui.Text("Hello, Cyber UI!")
text.set_position(100, 50)
text.set_color(1.0, 0.0, 0.0, 1.0)
text.set_font(font)
text.set_alignment(ui.TextAlignment.Left)

# Build hierarchy
parent.add_child(child)

# Render
parent.render()
```

## Related Documentation

- [TEXT_RENDERING.md](TEXT_RENDERING.md) - Complete API reference for Text and Font classes
- [HIERARCHY.md](HIERARCHY.md) - Scene graph hierarchy system
- [samples-basic.md](samples-basic.md) - Other basic samples
