# Text Rendering in OpenGL Backend

## Current Status

The OpenGL backend has **basic placeholder text rendering** implemented. It renders text as semi-transparent colored rectangles to indicate where text would appear.

### What Works
- Text positioning and sizing (estimated)
- Text color support
- Font size consideration (for size estimation)
- Integration with the rendering pipeline

### What's Missing
- Actual glyph rendering (characters are not visible)
- Font loading and management
- Proper text metrics (width, height, baseline)
- Text quality (anti-aliasing, hinting)

## Comparison with Metal Backend

The **Metal backend has full text rendering support** using macOS-specific APIs:
- Uses `NSFont` for font management
- Uses `NSGraphicsContext` and `CGContext` for text rasterization
- Renders text to bitmap textures
- Supports Retina displays with proper scaling
- Caches rendered text textures for performance

## Implementation Approach for Full OpenGL Text Rendering

To implement proper text rendering in OpenGL, you need to integrate the **FreeType** library, which is the industry-standard solution for font rendering.

### Step 1: Add FreeType Dependency

**On macOS (using Homebrew):**
```bash
brew install freetype
```

**On Linux (Ubuntu/Debian):**
```bash
sudo apt-get install libfreetype6-dev
```

**Update Makefile:**
```makefile
# Add FreeType flags
FREETYPE_CFLAGS = $(shell pkg-config --cflags freetype2)
FREETYPE_LIBS = $(shell pkg-config --libs freetype2)

CXXFLAGS += $(FREETYPE_CFLAGS)
LDFLAGS += $(FREETYPE_LIBS)
```

### Step 2: Implement Font Atlas Generation

Create a font atlas (texture containing all glyphs) for each font:

```cpp
struct Character {
    unsigned int textureID;  // Glyph texture ID
    glm::ivec2 size;        // Size of glyph
    glm::ivec2 bearing;     // Offset from baseline
    unsigned int advance;    // Horizontal advance
};

std::map<char, Character> characters_;

void OpenGLRenderer::loadFont(const char* fontPath, int fontSize) {
    FT_Library ft;
    FT_Init_FreeType(&ft);
    
    FT_Face face;
    FT_New_Face(ft, fontPath, 0, &face);
    FT_Set_Pixel_Sizes(face, 0, fontSize);
    
    // Load first 128 ASCII characters
    for (unsigned char c = 0; c < 128; c++) {
        if (FT_Load_Char(face, c, FT_LOAD_RENDER)) {
            continue;
        }
        
        // Generate texture for this glyph
        unsigned int texture;
        glGenTextures(1, &texture);
        glBindTexture(GL_TEXTURE_2D, texture);
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RED,
            face->glyph->bitmap.width,
            face->glyph->bitmap.rows,
            0,
            GL_RED,
            GL_UNSIGNED_BYTE,
            face->glyph->bitmap.buffer
        );
        
        // Set texture options
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
        
        // Store character info
        Character character = {
            texture,
            glm::ivec2(face->glyph->bitmap.width, face->glyph->bitmap.rows),
            glm::ivec2(face->glyph->bitmap_left, face->glyph->bitmap_top),
            face->glyph->advance.x
        };
        characters_.insert(std::pair<char, Character>(c, character));
    }
    
    FT_Done_Face(face);
    FT_Done_FreeType(ft);
}
```

### Step 3: Update Shader for Text Rendering

The fragment shader needs to handle single-channel (RED) textures for glyphs:

```glsl
#version 330 core
in vec4 vColor;
in vec2 vTexCoord;

uniform sampler2D uTexture;
uniform bool uIsText;  // Flag to indicate text rendering

out vec4 FragColor;

void main() {
    if (uIsText) {
        // For text, texture is single-channel (RED)
        float alpha = texture(uTexture, vTexCoord).r;
        FragColor = vec4(vColor.rgb, vColor.a * alpha);
    } else {
        // For regular textures
        vec4 texColor = texture(uTexture, vTexCoord);
        FragColor = texColor * vColor;
    }
}
```

### Step 4: Implement renderText Method

```cpp
void OpenGLRenderer::renderText(Text* text, const float* mvpMatrix) {
    std::string textStr = text->getText();
    if (textStr.empty()) return;
    
    float r, g, b, a;
    text->getColor(r, g, b, a);
    
    // Enable text rendering mode
    glUniform1i(glGetUniformLocation(shaderProgram_, "uIsText"), 1);
    
    float x = 0.0f;
    float y = 0.0f;
    
    // Render each character
    for (char c : textStr) {
        Character ch = characters_[c];
        
        float xpos = x + ch.bearing.x;
        float ypos = y - (ch.size.y - ch.bearing.y);
        float w = ch.size.x;
        float h = ch.size.y;
        
        // Create vertices for this character
        Vertex vertices[] = {
            {{xpos, ypos}, {r, g, b, a}, {0.0f, 1.0f}},
            {{xpos + w, ypos}, {r, g, b, a}, {1.0f, 1.0f}},
            {{xpos, ypos + h}, {r, g, b, a}, {0.0f, 0.0f}},
            {{xpos + w, ypos}, {r, g, b, a}, {1.0f, 1.0f}},
            {{xpos + w, ypos + h}, {r, g, b, a}, {1.0f, 0.0f}},
            {{xpos, ypos + h}, {r, g, b, a}, {0.0f, 0.0f}},
        };
        
        // Upload vertices
        glBindVertexArray(vao_);
        glBindBuffer(GL_ARRAY_BUFFER, vbo_);
        glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_DYNAMIC_DRAW);
        
        // Set MVP matrix
        int mvpLoc = glGetUniformLocation(shaderProgram_, "uMVPMatrix");
        glUniformMatrix4fv(mvpLoc, 1, GL_FALSE, mvpMatrix);
        
        // Bind glyph texture
        glActiveTexture(GL_TEXTURE0);
        glBindTexture(GL_TEXTURE_2D, ch.textureID);
        glUniform1i(glGetUniformLocation(shaderProgram_, "uTexture"), 0);
        
        // Draw
        glDrawArrays(GL_TRIANGLES, 0, 6);
        
        // Advance cursor
        x += (ch.advance >> 6);  // Bitshift by 6 to convert from 1/64th pixels
    }
    
    glBindVertexArray(0);
    
    // Disable text rendering mode
    glUniform1i(glGetUniformLocation(shaderProgram_, "uIsText"), 0);
}
```

## Alternative: Signed Distance Field (SDF) Text

For better quality at different scales, consider using **SDF text rendering**:
- Pre-generate SDF textures for glyphs
- Use specialized shader for SDF rendering
- Provides crisp text at any scale
- Better for 3D text rendering

Libraries like **msdfgen** can help generate multi-channel SDF textures.

## Testing Text Rendering

Create a test sample to verify text rendering:

```python
# samples/basic/text_demo.py
from cyber_ui import *

renderer = OpenGLRenderer()
renderer.initialize(800, 600, "Text Rendering Demo")

root = Object2D()

# Create text objects
text1 = Text("Hello, OpenGL!")
text1.setPosition(50, 50)
text1.setColor(1.0, 1.0, 1.0, 1.0)

text2 = Text("Text Rendering Test")
text2.setPosition(50, 100)
text2.setColor(1.0, 0.5, 0.0, 1.0)

root.addChild(text1)
root.addChild(text2)

while not renderer.shouldClose():
    renderer.beginFrame()
    renderer.renderObject(root)
    renderer.endFrame()
    renderer.pollEvents()

renderer.shutdown()
```

## Resources

- **FreeType Documentation**: https://freetype.org/freetype2/docs/tutorial/step1.html
- **LearnOpenGL Text Rendering**: https://learnopengl.com/In-Practice/Text-Rendering
- **SDF Text Rendering**: https://github.com/Chlumsky/msdfgen

## Summary

- ✅ OpenGL backend has **placeholder text rendering** (shows colored rectangles)
- ✅ Metal backend has **full text rendering** (using macOS APIs)
- ⚠️ For production use, implement FreeType-based text rendering in OpenGL
- 📝 The placeholder implementation allows development to continue while proper text rendering is being implemented
