# Texture Implementation Details

This document explains how texture rendering was implemented in the Cyber UI Toolkit.

## Problem

Initially, images were loaded successfully using Pillow and passed to Rectangle objects via `set_image()`, but the textures were not visible when rendering. The rectangles only showed solid colors.

## Root Cause

The Metal renderer (`MetalRenderer.mm`) was not implementing texture support:

1. **Shader limitation**: The vertex/fragment shaders only handled solid colors, with no texture sampling
2. **Vertex structure**: Vertices didn't include texture coordinates
3. **Rendering logic**: `renderRectangle()` didn't create or bind Metal textures

## Solution

### 1. Updated Vertex Structure

Added texture coordinates to the vertex structure:

```cpp
struct Vertex {
    float position[2];
    float color[4];
    float texCoord[2];  // Added
};
```

### 2. Enhanced Shaders

Updated Metal shaders to support texture sampling:

```metal
struct Vertex {
    float2 position [[attribute(0)]];
    float4 color [[attribute(1)]];
    float2 texCoord [[attribute(2)]];  // Added
};

struct VertexOut {
    float4 position [[position]];
    float4 color;
    float2 texCoord;  // Added
};

vertex VertexOut vertex_main(Vertex in [[stage_in]]) {
    VertexOut out;
    out.position = float4(in.position, 0.0, 1.0);
    out.color = in.color;
    out.texCoord = in.texCoord;  // Pass through
    return out;
}

fragment float4 fragment_main(VertexOut in [[stage_in]],
                             texture2d<float> tex [[texture(0)]],
                             sampler texSampler [[sampler(0)]]) {
    // Sample texture and multiply by vertex color (enables tinting)
    float4 texColor = tex.sample(texSampler, in.texCoord);
    return texColor * in.color;
}
```

### 3. Updated Vertex Descriptor

Added texture coordinate attribute to the pipeline:

```objc
// TexCoord attribute
vertexDesc.attributes[2].format = MTLVertexFormatFloat2;
vertexDesc.attributes[2].offset = sizeof(float) * 6;
vertexDesc.attributes[2].bufferIndex = 0;
```

### 4. Enabled Alpha Blending

Added blending support for transparent textures:

```objc
pipelineDesc.colorAttachments[0].blendingEnabled = YES;
pipelineDesc.colorAttachments[0].rgbBlendOperation = MTLBlendOperationAdd;
pipelineDesc.colorAttachments[0].sourceRGBBlendFactor = MTLBlendFactorSourceAlpha;
pipelineDesc.colorAttachments[0].destinationRGBBlendFactor = MTLBlendFactorOneMinusSourceAlpha;
```

### 5. Implemented Texture Creation in renderRectangle()

The rendering method now:

1. **Checks for texture**: Uses `rect->hasImage()` to determine if texture is available
2. **Creates Metal texture**: Converts Image data to `MTLTexture`
3. **Uploads pixel data**: Copies RGBA bitmap to GPU
4. **Creates sampler**: Configures texture filtering (linear) and addressing (clamp to edge)
5. **Binds to shader**: Sets texture and sampler for fragment shader
6. **Fallback**: Creates 1x1 white texture for non-textured rectangles

```objc
if (rect->hasImage()) {
    auto image = rect->getImage();
    if (image && image->isLoaded()) {
        // Create Metal texture
        MTLTextureDescriptor* texDesc = [MTLTextureDescriptor 
            texture2DDescriptorWithPixelFormat:MTLPixelFormatRGBA8Unorm
            width:image->getWidth()
            height:image->getHeight()
            mipmapped:NO];
        
        id<MTLTexture> texture = [device newTextureWithDescriptor:texDesc];
        
        // Upload image data
        MTLRegion region = MTLRegionMake2D(0, 0, image->getWidth(), image->getHeight());
        [texture replaceRegion:region
                   mipmapLevel:0
                     withBytes:image->getData()
                   bytesPerRow:4 * image->getWidth()];
        
        // Create and bind sampler
        MTLSamplerDescriptor* samplerDesc = [[MTLSamplerDescriptor alloc] init];
        samplerDesc.minFilter = MTLSamplerMinMagFilterLinear;
        samplerDesc.magFilter = MTLSamplerMinMagFilterLinear;
        id<MTLSamplerState> sampler = [device newSamplerStateWithDescriptor:samplerDesc];
        
        [renderEncoder setFragmentTexture:texture atIndex:0];
        [renderEncoder setFragmentSamplerState:sampler atIndex:0];
    }
}
```

## Features Enabled

### Texture Mapping
- Images loaded via Pillow are now visible on rectangles
- Proper UV mapping (0,0 to 1,1)
- Linear filtering for smooth scaling

### Color Tinting
- Vertex color multiplies with texture color
- White (1,1,1,1) shows texture as-is
- Other colors tint the texture
- Example: Red (1,0.5,0.5,1) creates red-tinted texture

### Alpha Blending
- Transparent textures (RGBA with alpha < 1) blend correctly
- Icon texture with transparency works properly
- Proper alpha compositing with background

### Mixed Rendering
- Textured and non-textured rectangles can coexist
- Non-textured rectangles use 1x1 white texture internally
- Consistent shader pipeline for all rectangles

## Testing

Run these scripts to verify texture rendering:

```bash
# Visual verification (opens window)
PYTHONPATH=build python3 samples/basic/verify_textures.py

# Interactive demo with multiple textures
PYTHONPATH=build python3 samples/basic/test_rectangle.py

# Console output test
PYTHONPATH=build python3 samples/basic/test_texture_demo.py
```

## Performance Considerations

**Current Implementation:**
- Textures are created every frame (not cached)
- Suitable for prototyping and testing
- Simple and straightforward

**Future Optimizations:**
- Cache Metal textures per Image object
- Reuse textures across frames
- Implement texture atlas for small images
- Add mipmap support for better quality at distance

## Files Modified

- `src/rendering/MetalRenderer.mm` - Added texture support
- `samples/basic/test_rectangle.py` - Updated to use textures
- `samples/basic/verify_textures.py` - Created visual test

## Verification

To confirm textures are working:

1. **Gradient texture**: Should show smooth color gradient from corner to corner
2. **Checkerboard**: Should show black and white squares
3. **Icon**: Should show orange circle with yellow center and transparent background
4. **Tinted textures**: Should show checkerboard with color overlay
5. **Solid color**: Should show plain colored rectangle

If textures appear as solid colors, the issue is likely in shader binding or texture creation.
