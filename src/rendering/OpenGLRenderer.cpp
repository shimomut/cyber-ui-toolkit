#include "OpenGLRenderer.h"
#include "Shape2D.h"
#include "Image.h"
#include "Text.h"
#include "../core/SceneRoot.h"
#include "../core/Frame3D.h"
#include "../core/Frame2D.h"
#include "../core/Camera.h"

#ifdef __APPLE__
#define GL_SILENCE_DEPRECATION
#include <OpenGL/gl3.h>
#else
#include <GL/glew.h>
#endif

#include <GLFW/glfw3.h>
#include <cmath>
#include <cstring>
#include <iostream>

namespace CyberUI {

// Vertex structure for rectangles
struct Vertex {
    float position[2];
    float color[4];
    float texCoord[2];
};

// Shader sources
static const char* vertexShaderSource = R"(
#version 330 core
layout (location = 0) in vec2 aPosition;
layout (location = 1) in vec4 aColor;
layout (location = 2) in vec2 aTexCoord;

uniform mat4 uMVPMatrix;

out vec4 vColor;
out vec2 vTexCoord;

void main() {
    vec4 pos3D = vec4(aPosition.x, aPosition.y, 0.0, 1.0);
    gl_Position = uMVPMatrix * pos3D;
    vColor = aColor;
    vTexCoord = aTexCoord;
}
)";

static const char* fragmentShaderSource = R"(
#version 330 core
in vec4 vColor;
in vec2 vTexCoord;

uniform sampler2D uTexture;

out vec4 FragColor;

void main() {
    vec4 texColor = texture(uTexture, vTexCoord);
    FragColor = texColor * vColor;
}
)";

OpenGLRenderer::OpenGLRenderer() 
    : window_(nullptr), shaderProgram_(0), vao_(0), vbo_(0),
      initialized_(false), shouldClose_(false), windowWidth_(800), windowHeight_(600),
      newTexturesCreatedThisFrame_(false),
      currentRenderTargetWidth_(0), currentRenderTargetHeight_(0),
      whiteTexture_(0) {
}

OpenGLRenderer::~OpenGLRenderer() {
    shutdown();
}

bool OpenGLRenderer::initialize(int width, int height, const char* title) {
    windowWidth_ = width;
    windowHeight_ = height;
    
    // Initialize GLFW
    if (!glfwInit()) {
        std::cerr << "Failed to initialize GLFW" << std::endl;
        return false;
    }
    
    // Set OpenGL version (3.3 Core)
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    glfwWindowHint(GLFW_VISIBLE, GLFW_TRUE);
    glfwWindowHint(GLFW_FOCUSED, GLFW_TRUE);
    
#ifdef __APPLE__
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);
#endif
    
    // Create window
    GLFWwindow* window = glfwCreateWindow(width, height, title, nullptr, nullptr);
    if (!window) {
        std::cerr << "Failed to create GLFW window" << std::endl;
        glfwTerminate();
        return false;
    }
    window_ = window;
    
    glfwMakeContextCurrent(window);
    
#ifndef __APPLE__
    // Initialize GLEW (not needed on macOS)
    glewExperimental = GL_TRUE;
    if (glewInit() != GLEW_OK) {
        std::cerr << "Failed to initialize GLEW" << std::endl;
        return false;
    }
#endif
    
    // Enable blending for transparency
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    
    // Enable scissor test for clipping
    glEnable(GL_SCISSOR_TEST);
    
    // Setup shaders
    setupShaders();
    
    // Create VAO and VBO
    glGenVertexArrays(1, &vao_);
    glGenBuffers(1, &vbo_);
    
    glBindVertexArray(vao_);
    glBindBuffer(GL_ARRAY_BUFFER, vbo_);
    
    // Position attribute
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, sizeof(Vertex), (void*)0);
    glEnableVertexAttribArray(0);
    
    // Color attribute
    glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, sizeof(Vertex), (void*)(2 * sizeof(float)));
    glEnableVertexAttribArray(1);
    
    // TexCoord attribute
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, sizeof(Vertex), (void*)(6 * sizeof(float)));
    glEnableVertexAttribArray(2);
    
    glBindVertexArray(0);
    
    // Create white texture for non-textured rectangles
    glGenTextures(1, &whiteTexture_);
    glBindTexture(GL_TEXTURE_2D, whiteTexture_);
    uint8_t whitePixel[4] = {255, 255, 255, 255};
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 1, 1, 0, GL_RGBA, GL_UNSIGNED_BYTE, whitePixel);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glBindTexture(GL_TEXTURE_2D, 0);
    
    initialized_ = true;
    return true;
}

void OpenGLRenderer::setupShaders() {
    // Compile vertex shader
    unsigned int vertexShader = glCreateShader(GL_VERTEX_SHADER);
    glShaderSource(vertexShader, 1, &vertexShaderSource, nullptr);
    glCompileShader(vertexShader);
    
    int success;
    char infoLog[512];
    glGetShaderiv(vertexShader, GL_COMPILE_STATUS, &success);
    if (!success) {
        glGetShaderInfoLog(vertexShader, 512, nullptr, infoLog);
        std::cerr << "Vertex shader compilation failed: " << infoLog << std::endl;
    }
    
    // Compile fragment shader
    unsigned int fragmentShader = glCreateShader(GL_FRAGMENT_SHADER);
    glShaderSource(fragmentShader, 1, &fragmentShaderSource, nullptr);
    glCompileShader(fragmentShader);
    
    glGetShaderiv(fragmentShader, GL_COMPILE_STATUS, &success);
    if (!success) {
        glGetShaderInfoLog(fragmentShader, 512, nullptr, infoLog);
        std::cerr << "Fragment shader compilation failed: " << infoLog << std::endl;
    }
    
    // Link shaders
    shaderProgram_ = glCreateProgram();
    glAttachShader(shaderProgram_, vertexShader);
    glAttachShader(shaderProgram_, fragmentShader);
    glLinkProgram(shaderProgram_);
    
    glGetProgramiv(shaderProgram_, GL_LINK_STATUS, &success);
    if (!success) {
        glGetProgramInfoLog(shaderProgram_, 512, nullptr, infoLog);
        std::cerr << "Shader program linking failed: " << infoLog << std::endl;
    }
    
    glDeleteShader(vertexShader);
    glDeleteShader(fragmentShader);
}

void OpenGLRenderer::shutdown() {
    if (initialized_) {
        // Clean up texture cache
        for (auto& pair : textureCache_) {
            glDeleteTextures(1, &pair.second);
        }
        textureCache_.clear();
        
        for (auto& pair : textTextureCache_) {
            glDeleteTextures(1, &pair.second);
        }
        textTextureCache_.clear();
        
        for (auto& pair : renderTargetCache_) {
            glDeleteTextures(1, &pair.second);
        }
        renderTargetCache_.clear();
        
        if (whiteTexture_) {
            glDeleteTextures(1, &whiteTexture_);
            whiteTexture_ = 0;
        }
        
        if (vbo_) {
            glDeleteBuffers(1, &vbo_);
            vbo_ = 0;
        }
        
        if (vao_) {
            glDeleteVertexArrays(1, &vao_);
            vao_ = 0;
        }
        
        if (shaderProgram_) {
            glDeleteProgram(shaderProgram_);
            shaderProgram_ = 0;
        }
        
        if (window_) {
            glfwDestroyWindow(static_cast<GLFWwindow*>(window_));
            window_ = nullptr;
        }
        
        glfwTerminate();
        initialized_ = false;
    }
}

bool OpenGLRenderer::beginFrame() {
    if (!initialized_) return false;
    
    // Reset texture creation flag for this frame
    newTexturesCreatedThisFrame_ = false;
    
    // Clear scissor stack for new frame
    scissorStack_.clear();
    
    GLFWwindow* window = static_cast<GLFWwindow*>(window_);
    
    // Get framebuffer size (accounts for Retina scaling)
    int fbWidth, fbHeight;
    glfwGetFramebufferSize(window, &fbWidth, &fbHeight);
    
    // Set viewport
    glViewport(0, 0, fbWidth, fbHeight);
    
    // Set initial scissor rect to full viewport
    glScissor(0, 0, fbWidth, fbHeight);
    
    // Store current render target dimensions
    currentRenderTargetWidth_ = fbWidth;
    currentRenderTargetHeight_ = fbHeight;
    
    // Clear screen to a visible color for debugging
    glClearColor(0.2f, 0.2f, 0.3f, 1.0f);  // Dark blue-gray
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    
    // Check for errors
    GLenum err = glGetError();
    if (err != GL_NO_ERROR) {
        std::cerr << "OpenGL error after clear: " << err << std::endl;
    }
    
    // Use shader program
    glUseProgram(shaderProgram_);
    
    err = glGetError();
    if (err != GL_NO_ERROR) {
        std::cerr << "OpenGL error after useProgram: " << err << std::endl;
    }
    
    return true;
}

void OpenGLRenderer::endFrame() {
    GLFWwindow* window = static_cast<GLFWwindow*>(window_);
    glfwSwapBuffers(window);
    
    // Only wait for GPU if new textures were created this frame
    if (newTexturesCreatedThisFrame_) {
        glFinish();
    }
}

void OpenGLRenderer::renderObject(Object2D* object) {
    if (!object || !object->isVisible()) return;
    
    // Get framebuffer size (accounts for Retina scaling)
    GLFWwindow* window = static_cast<GLFWwindow*>(window_);
    int fbWidth, fbHeight;
    glfwGetFramebufferSize(window, &fbWidth, &fbHeight);
    
    float viewWidth = static_cast<float>(fbWidth);
    float viewHeight = static_cast<float>(fbHeight);
    
    float scaleX = 2.0f / viewWidth;
    float scaleY = -2.0f / viewHeight;
    
    float orthoMatrix[16] = {
        scaleX, 0, 0, 0,
        0, scaleY, 0, 0,
        0, 0, 1, 0,
        -1, 1, 0, 1
    };
    
    renderObject2D(object, orthoMatrix);
}

bool OpenGLRenderer::shouldClose() {
    if (!window_) return true;
    return shouldClose_ || glfwWindowShouldClose(static_cast<GLFWwindow*>(window_));
}

void OpenGLRenderer::pollEvents() {
    glfwPollEvents();
    
    GLFWwindow* window = static_cast<GLFWwindow*>(window_);
    if (glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS) {
        shouldClose_ = true;
    }
}

void OpenGLRenderer::renderScene(SceneRoot* scene) {
    if (!scene) return;
    
    auto camera = scene->getCamera();
    if (!camera) return;
    
    // Get view and projection matrices
    float viewMatrix[16];
    float projMatrix[16];
    camera->getViewMatrix(viewMatrix);
    camera->getProjectionMatrix(projMatrix);
    
    // Combine view and projection
    float viewProjMatrix[16];
    multiplyMatrices(projMatrix, viewMatrix, viewProjMatrix);
    
    // Render all Frame3D objects
    for (const auto& frame : scene->getFrames()) {
        renderFrame3D(frame.get(), viewProjMatrix);
    }
}

void OpenGLRenderer::renderFrame3D(Frame3D* frame, const float* viewProjMatrix) {
    if (!frame || !frame->isVisible()) return;
    
    // Check if off-screen rendering is enabled
    if (frame->isOffscreenRenderingEnabled()) {
        // First, render Frame3D content to texture
        renderFrame3DToTexture(frame);
        
        // Then render the texture as a quad with 3D transforms
        unsigned int texture = frame->getRenderTargetTexture() ? 
            *static_cast<unsigned int*>(frame->getRenderTargetTexture()) : 0;
        
        if (texture) {
            // Get Frame3D transform
            float pos[3], rot[3], scale[3];
            frame->getPosition(pos[0], pos[1], pos[2]);
            frame->getRotation(rot[0], rot[1], rot[2]);
            frame->getScale(scale[0], scale[1], scale[2]);
            
            // Create model matrix
            float modelMatrix[16];
            createTransformMatrix(pos[0], pos[1], pos[2], 
                                 rot[0], rot[1], rot[2],
                                 scale[0], scale[1], scale[2],
                                 modelMatrix);
            
            // Combine with view-projection
            float mvpMatrix[16];
            multiplyMatrices(viewProjMatrix, modelMatrix, mvpMatrix);
            
            // Get render target size
            int rtWidth, rtHeight;
            frame->getRenderTargetSize(rtWidth, rtHeight);
            
            // Render the texture as a quad
            renderTexturedQuad(texture, static_cast<float>(rtWidth), 
                             static_cast<float>(rtHeight), mvpMatrix);
        }
    } else {
        // Direct rendering
        float pos[3], rot[3], scale[3];
        frame->getPosition(pos[0], pos[1], pos[2]);
        frame->getRotation(rot[0], rot[1], rot[2]);
        frame->getScale(scale[0], scale[1], scale[2]);
        
        // Create model matrix
        float modelMatrix[16];
        createTransformMatrix(pos[0], pos[1], pos[2], 
                             rot[0], rot[1], rot[2],
                             scale[0], scale[1], scale[2],
                             modelMatrix);
        
        // Combine with view-projection
        float mvpMatrix[16];
        multiplyMatrices(viewProjMatrix, modelMatrix, mvpMatrix);
        
        // Render all 2D children
        for (const auto& child : frame->getChildren()) {
            renderObject2D(child.get(), mvpMatrix);
        }
    }
}

void OpenGLRenderer::renderObject2D(Object2D* object, const float* mvpMatrix) {
    if (!object || !object->isVisible()) return;
    
    // Get 2D position and create translation matrix
    float x, y;
    object->getPosition(x, y);
    
    float translationMatrix[16] = {
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        x, y, 0, 1
    };
    
    // Combine with parent MVP
    float objectMVP[16];
    multiplyMatrices(mvpMatrix, translationMatrix, objectMVP);
    
    // Check if it's a Frame2D
    Frame2D* frame2d = dynamic_cast<Frame2D*>(object);
    if (frame2d) {
        float width, height;
        frame2d->getSize(width, height);
        
        // Frame2D coordinate system: Y-axis flip, origin at top-left
        float offsetMatrix[16] = {
            1, 0, 0, 0,
            0, -1, 0, 0,
            0, 0, 1, 0,
            0, height, 0, 1
        };
        
        // Combine with Frame2D's MVP
        float frame2dMVP[16];
        multiplyMatrices(objectMVP, offsetMatrix, frame2dMVP);
        
        // Handle clipping
        bool hasClipping = frame2d->isClippingEnabled();
        
        if (hasClipping) {
            pushScissorRect(0, 0, width, height, frame2dMVP);
        }
        
        // Render children
        for (const auto& child : frame2d->getChildren()) {
            renderObject2D(child.get(), frame2dMVP);
        }
        
        if (hasClipping) {
            popScissorRect();
        }
        
        return;
    }
    
    // Check if it's a Rectangle
    Rectangle* rect = dynamic_cast<Rectangle*>(object);
    if (rect) {
        renderRectangle(rect, objectMVP);
    }
    
    // Check if it's a Text
    Text* text = dynamic_cast<Text*>(object);
    if (text) {
        renderText(text, objectMVP);
    }
    
    // Render children
    for (const auto& child : object->getChildren()) {
        renderObject2D(child.get(), objectMVP);
    }
}

void OpenGLRenderer::renderRectangle(Rectangle* rect, const float* mvpMatrix) {
    float width, height;
    rect->getSize(width, height);
    
    float r, g, b, a;
    rect->getColor(r, g, b, a);
    
    // Debug output
    static int callCount = 0;
    if (callCount < 5) {
        std::cout << "renderRectangle called: size=" << width << "x" << height 
                  << " color=(" << r << "," << g << "," << b << "," << a << ")" << std::endl;
        callCount++;
    }
    
    // Create vertices with top-left origin
    Vertex vertices[] = {
        {{0.0f, 0.0f}, {r, g, b, a}, {0.0f, 1.0f}},
        {{width, 0.0f}, {r, g, b, a}, {1.0f, 1.0f}},
        {{0.0f, height}, {r, g, b, a}, {0.0f, 0.0f}},
        {{width, 0.0f}, {r, g, b, a}, {1.0f, 1.0f}},
        {{width, height}, {r, g, b, a}, {1.0f, 0.0f}},
        {{0.0f, height}, {r, g, b, a}, {0.0f, 0.0f}},
    };
    
    // Upload vertices
    glBindVertexArray(vao_);
    glBindBuffer(GL_ARRAY_BUFFER, vbo_);
    glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_DYNAMIC_DRAW);
    
    // Set MVP matrix uniform
    int mvpLoc = glGetUniformLocation(shaderProgram_, "uMVPMatrix");
    if (mvpLoc == -1) {
        static bool warned = false;
        if (!warned) {
            std::cerr << "WARNING: uMVPMatrix uniform not found in shader!" << std::endl;
            warned = true;
        }
    }
    // Pass as row-major (GL_TRUE) since our matrices are row-major
    glUniformMatrix4fv(mvpLoc, 1, GL_TRUE, mvpMatrix);
    
    // Debug: print first MVP matrix
    static bool printedMVP = false;
    if (!printedMVP) {
        std::cout << "MVP Matrix:" << std::endl;
        for (int i = 0; i < 4; i++) {
            std::cout << "  [" << mvpMatrix[i*4] << ", " << mvpMatrix[i*4+1] << ", " 
                      << mvpMatrix[i*4+2] << ", " << mvpMatrix[i*4+3] << "]" << std::endl;
        }
        printedMVP = true;
    }
    
    // Handle texture
    unsigned int texture = whiteTexture_;
    if (rect->hasImage()) {
        auto image = rect->getImage();
        if (image && image->isLoaded()) {
            texture = getOrCreateTexture(image.get());
        }
    }
    
    glActiveTexture(GL_TEXTURE0);
    glBindTexture(GL_TEXTURE_2D, texture);
    glUniform1i(glGetUniformLocation(shaderProgram_, "uTexture"), 0);
    
    // Draw
    glDrawArrays(GL_TRIANGLES, 0, 6);
    
    // Check for OpenGL errors (debug)
    GLenum err = glGetError();
    if (err != GL_NO_ERROR) {
        std::cerr << "OpenGL error in renderRectangle: " << err << std::endl;
    }
    
    glBindVertexArray(0);
}

void OpenGLRenderer::renderText(Text* text, const float* mvpMatrix) {
    // Text rendering implementation would go here
    // For now, this is a placeholder
    // Full implementation would require FreeType or similar library
}

unsigned int OpenGLRenderer::getOrCreateTexture(Image* image) {
    // Check cache
    auto it = textureCache_.find(image);
    if (it != textureCache_.end()) {
        return it->second;
    }
    
    // Create new texture
    unsigned int texture;
    glGenTextures(1, &texture);
    glBindTexture(GL_TEXTURE_2D, texture);
    
    int width = image->getWidth();
    int height = image->getHeight();
    int channels = image->getChannels();
    const uint8_t* data = image->getData();
    
    GLenum format = (channels == 4) ? GL_RGBA : GL_RGB;
    glTexImage2D(GL_TEXTURE_2D, 0, format, width, height, 0, format, GL_UNSIGNED_BYTE, data);
    
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
    
    glBindTexture(GL_TEXTURE_2D, 0);
    
    // Cache the texture
    textureCache_[image] = texture;
    newTexturesCreatedThisFrame_ = true;
    
    return texture;
}

unsigned int OpenGLRenderer::getOrCreateRenderTarget(Frame3D* frame) {
    // Render target implementation
    return 0;
}

void OpenGLRenderer::renderFrame3DToTexture(Frame3D* frame) {
    // Off-screen rendering implementation
}

void OpenGLRenderer::renderTexturedQuad(unsigned int texture, float width, float height, const float* mvpMatrix) {
    // Textured quad rendering implementation
}

void OpenGLRenderer::pushScissorRect(float x, float y, float width, float height, const float* mvpMatrix) {
    // Transform corners to screen space
    float screenX, screenY;
    transformPointToScreen(x, y, mvpMatrix, screenX, screenY);
    
    float screenX2, screenY2;
    transformPointToScreen(x + width, y + height, mvpMatrix, screenX2, screenY2);
    
    // Calculate scissor rect in screen coordinates
    int scissorX = static_cast<int>(std::min(screenX, screenX2));
    int scissorY = static_cast<int>(std::min(screenY, screenY2));
    int scissorWidth = static_cast<int>(std::abs(screenX2 - screenX));
    int scissorHeight = static_cast<int>(std::abs(screenY2 - screenY));
    
    // Clamp to render target bounds
    scissorX = std::max(0, std::min(scissorX, currentRenderTargetWidth_));
    scissorY = std::max(0, std::min(scissorY, currentRenderTargetHeight_));
    scissorWidth = std::min(scissorWidth, currentRenderTargetWidth_ - scissorX);
    scissorHeight = std::min(scissorHeight, currentRenderTargetHeight_ - scissorY);
    
    // Push to stack
    scissorStack_.push_back({scissorX, scissorY, scissorWidth, scissorHeight});
    
    // Apply scissor rect
    glScissor(scissorX, scissorY, scissorWidth, scissorHeight);
}

void OpenGLRenderer::popScissorRect() {
    if (!scissorStack_.empty()) {
        scissorStack_.pop_back();
    }
    
    if (!scissorStack_.empty()) {
        auto& rect = scissorStack_.back();
        glScissor(rect.x, rect.y, rect.width, rect.height);
    } else {
        // Restore full viewport
        glScissor(0, 0, currentRenderTargetWidth_, currentRenderTargetHeight_);
    }
}

void OpenGLRenderer::transformPointToScreen(float x, float y, const float* mvpMatrix, float& screenX, float& screenY) {
    // Transform point through MVP matrix
    float clipX = mvpMatrix[0] * x + mvpMatrix[4] * y + mvpMatrix[12];
    float clipY = mvpMatrix[1] * x + mvpMatrix[5] * y + mvpMatrix[13];
    float clipW = mvpMatrix[3] * x + mvpMatrix[7] * y + mvpMatrix[15];
    
    // Convert to NDC
    float ndcX = clipX / clipW;
    float ndcY = clipY / clipW;
    
    // Convert to screen coordinates
    screenX = (ndcX + 1.0f) * 0.5f * currentRenderTargetWidth_;
    screenY = (1.0f - ndcY) * 0.5f * currentRenderTargetHeight_;
}

bool OpenGLRenderer::captureFrame(std::vector<uint8_t>& pixelData, int& width, int& height) {
    if (!initialized_) return false;
    
    GLFWwindow* window = static_cast<GLFWwindow*>(window_);
    glfwGetFramebufferSize(window, &width, &height);
    
    pixelData.resize(width * height * 4);
    glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE, pixelData.data());
    
    // Flip image vertically (OpenGL reads bottom-to-top)
    std::vector<uint8_t> flipped(pixelData.size());
    for (int y = 0; y < height; y++) {
        memcpy(&flipped[y * width * 4], 
               &pixelData[(height - 1 - y) * width * 4], 
               width * 4);
    }
    pixelData = std::move(flipped);
    
    return true;
}

bool OpenGLRenderer::saveCapture(const char* filename) {
    std::vector<uint8_t> pixelData;
    int width, height;
    
    if (!captureFrame(pixelData, width, height)) {
        return false;
    }
    
    // Save to file (would need image library like stb_image_write)
    // Placeholder implementation
    return false;
}

void OpenGLRenderer::multiplyMatrices(const float* a, const float* b, float* result) {
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            result[i * 4 + j] = 0;
            for (int k = 0; k < 4; k++) {
                result[i * 4 + j] += a[i * 4 + k] * b[k * 4 + j];
            }
        }
    }
}

void OpenGLRenderer::createTransformMatrix(float x, float y, float z, 
                                          float pitch, float yaw, float roll,
                                          float sx, float sy, float sz,
                                          float* matrix) {
    // Create transformation matrix (simplified)
    float cosPitch = std::cos(pitch);
    float sinPitch = std::sin(pitch);
    float cosYaw = std::cos(yaw);
    float sinYaw = std::sin(yaw);
    float cosRoll = std::cos(roll);
    float sinRoll = std::sin(roll);
    
    matrix[0] = sx * (cosYaw * cosRoll);
    matrix[1] = sx * (cosYaw * sinRoll);
    matrix[2] = sx * (-sinYaw);
    matrix[3] = 0;
    
    matrix[4] = sy * (sinPitch * sinYaw * cosRoll - cosPitch * sinRoll);
    matrix[5] = sy * (sinPitch * sinYaw * sinRoll + cosPitch * cosRoll);
    matrix[6] = sy * (sinPitch * cosYaw);
    matrix[7] = 0;
    
    matrix[8] = sz * (cosPitch * sinYaw * cosRoll + sinPitch * sinRoll);
    matrix[9] = sz * (cosPitch * sinYaw * sinRoll - sinPitch * cosRoll);
    matrix[10] = sz * (cosPitch * cosYaw);
    matrix[11] = 0;
    
    matrix[12] = x;
    matrix[13] = y;
    matrix[14] = z;
    matrix[15] = 1;
}

} // namespace CyberUI
