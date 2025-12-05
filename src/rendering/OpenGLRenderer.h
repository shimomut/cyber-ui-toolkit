#pragma once

#include "Renderer.h"
#include <map>
#include <string>
#include <vector>

namespace CyberUI {

class Frame3D;
class Image;

class OpenGLRenderer : public Renderer {
public:
    OpenGLRenderer();
    ~OpenGLRenderer() override;
    
    bool initialize(int width, int height, const char* title) override;
    void shutdown() override;
    bool beginFrame() override;
    void endFrame() override;
    void renderObject(Object2D* object) override;
    void renderScene(SceneRoot* scene) override;
    bool shouldClose() override;
    void pollEvents() override;
    
    // Capture functionality
    bool captureFrame(std::vector<uint8_t>& pixelData, int& width, int& height) override;
    bool saveCapture(const char* filename) override;

private:
    void setupShaders();
    void renderRectangle(class Rectangle* rect, const float* mvpMatrix);
    void renderText(class Text* text, const float* mvpMatrix);
    void renderFrame3D(Frame3D* frame, const float* viewProjMatrix);
    void renderObject2D(Object2D* object, const float* mvpMatrix);
    
    unsigned int getOrCreateTexture(Image* image);
    unsigned int getOrCreateRenderTarget(Frame3D* frame);
    void renderFrame3DToTexture(Frame3D* frame);
    void renderTexturedQuad(unsigned int texture, float width, float height, const float* mvpMatrix);
    
    // Scissor rect management for clipping
    void pushScissorRect(float x, float y, float width, float height, const float* mvpMatrix);
    void popScissorRect();
    void transformPointToScreen(float x, float y, const float* mvpMatrix, float& screenX, float& screenY);
    
    void multiplyMatrices(const float* a, const float* b, float* result);
    void createTransformMatrix(float x, float y, float z, 
                              float pitch, float yaw, float roll,
                              float sx, float sy, float sz,
                              float* matrix);
    
    void* window_;
    unsigned int shaderProgram_;
    unsigned int vao_;
    unsigned int vbo_;
    
    bool initialized_;
    bool shouldClose_;
    int windowWidth_;
    int windowHeight_;
    
    // Texture cache to avoid recreating textures every frame
    std::map<Image*, unsigned int> textureCache_;
    std::map<std::string, unsigned int> textTextureCache_;
    std::map<Frame3D*, unsigned int> renderTargetCache_;
    
    // Track if new textures were created this frame
    bool newTexturesCreatedThisFrame_;
    
    // Scissor rect stack for clipping
    struct ScissorRect {
        int x, y, width, height;
    };
    std::vector<ScissorRect> scissorStack_;
    
    // Current render target dimensions
    int currentRenderTargetWidth_;
    int currentRenderTargetHeight_;
    
    // White texture for non-textured rectangles
    unsigned int whiteTexture_;
};

} // namespace CyberUI
