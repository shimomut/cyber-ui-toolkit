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
    
    // Enable depth testing for 3D rendering
    glEnable(GL_DEPTH_TEST);
    glDepthFunc(GL_LEQUAL);
    
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
    
    // Use window size (logical coordinates) for the ortho matrix
    // Object positions and sizes are in logical coordinates, not framebuffer coordinates
    float viewWidth = static_cast<float>(windowWidth_);
    float viewHeight = static_cast<float>(windowHeight_);
    
    // Create orthographic projection matrix that maps pixel coordinates to clip space
    // Using COLUMN-MAJOR format (OpenGL standard)
    // Maps from top-left origin [0, width] x [0, height] to OpenGL clip space [-1, 1] x [1, -1]
    // Note: Y is flipped because our coordinate system has Y increasing downward (top-left origin)
    // but OpenGL clip space has Y increasing upward
    float scaleX = 2.0f / viewWidth;
    float scaleY = -2.0f / viewHeight;  // Negative to flip Y-axis
    
    float orthoMatrix[16] = {
        scaleX, 0, 0, 0,      // Column 0
        0, scaleY, 0, 0,      // Column 1  
        0, 0, 1, 0,           // Column 2
        -1, 1, 0, 1           // Column 3 (translation: map (0,0) to (-1,1) in clip space)
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
        void* texturePtr = frame->getRenderTargetTexture();
        unsigned int texture = texturePtr ? static_cast<unsigned int>(reinterpret_cast<uintptr_t>(texturePtr)) : 0;
        
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
    
    // Translation matrix in pixel space (applied before projection)
    // Using COLUMN-MAJOR format (OpenGL standard)
    float translationMatrix[16] = {
        1, 0, 0, 0,    // Column 0
        0, 1, 0, 0,    // Column 1
        0, 0, 1, 0,    // Column 2
        x, y, 0, 1     // Column 3 (translation)
    };
    
    // Combine: MVP * Translation (right-to-left: first translate, then project)
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
    // Pass as column-major (GL_FALSE) since our matrices are now column-major
    glUniformMatrix4fv(mvpLoc, 1, GL_FALSE, mvpMatrix);
    
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
    if (!frame) return 0;
    
    // Check cache first
    auto it = renderTargetCache_.find(frame);
    if (it != renderTargetCache_.end()) {
        return it->second;
    }
    
    // Create new render target texture
    int width, height;
    frame->getRenderTargetSize(width, height);
    
    unsigned int texture;
    glGenTextures(1, &texture);
    glBindTexture(GL_TEXTURE_2D, texture);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, nullptr);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
    glBindTexture(GL_TEXTURE_2D, 0);
    
    // Cache the texture
    renderTargetCache_[frame] = texture;
    frame->setRenderTargetTexture(reinterpret_cast<void*>(static_cast<uintptr_t>(texture)));
    
    return texture;
}

void OpenGLRenderer::renderFrame3DToTexture(Frame3D* frame) {
    if (!frame) return;
    
    // Get or create render target
    unsigned int renderTarget = getOrCreateRenderTarget(frame);
    if (!renderTarget) return;
    
    // Get render target size
    int rtWidth, rtHeight;
    frame->getRenderTargetSize(rtWidth, rtHeight);
    
    // Create framebuffer object
    unsigned int fbo;
    glGenFramebuffers(1, &fbo);
    glBindFramebuffer(GL_FRAMEBUFFER, fbo);
    
    // Attach texture to framebuffer
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, renderTarget, 0);
    
    // Check framebuffer status
    if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE) {
        std::cerr << "Framebuffer is not complete!" << std::endl;
        glBindFramebuffer(GL_FRAMEBUFFER, 0);
        glDeleteFramebuffers(1, &fbo);
        return;
    }
    
    // Save current state
    int savedRenderTargetWidth = currentRenderTargetWidth_;
    int savedRenderTargetHeight = currentRenderTargetHeight_;
    
    // Set viewport for off-screen rendering
    glViewport(0, 0, rtWidth, rtHeight);
    glScissor(0, 0, rtWidth, rtHeight);
    
    // Update current render target dimensions
    currentRenderTargetWidth_ = rtWidth;
    currentRenderTargetHeight_ = rtHeight;
    
    // Clear to transparent
    glClearColor(0.0f, 0.0f, 0.0f, 0.0f);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    
    // Create orthographic projection for 2D rendering
    float scaleX = 2.0f / rtWidth;
    float scaleY = -2.0f / rtHeight;
    
    float orthoMatrix[16] = {
        scaleX, 0, 0, 0,
        0, scaleY, 0, 0,
        0, 0, 1, 0,
        -1, 1, 0, 1
    };
    
    // Render all children to texture
    for (const auto& child : frame->getChildren()) {
        renderObject2D(child.get(), orthoMatrix);
    }
    
    // Restore framebuffer and state
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
    glDeleteFramebuffers(1, &fbo);
    
    // Restore viewport and scissor
    GLFWwindow* window = static_cast<GLFWwindow*>(window_);
    int fbWidth, fbHeight;
    glfwGetFramebufferSize(window, &fbWidth, &fbHeight);
    glViewport(0, 0, fbWidth, fbHeight);
    glScissor(0, 0, fbWidth, fbHeight);
    
    // Restore render target dimensions
    currentRenderTargetWidth_ = savedRenderTargetWidth;
    currentRenderTargetHeight_ = savedRenderTargetHeight;
}

void OpenGLRenderer::renderTexturedQuad(unsigned int texture, float width, float height, const float* mvpMatrix) {
    if (!texture) return;
    
    // Create quad vertices (centered)
    float halfW = width * 0.5f;
    float halfH = height * 0.5f;
    
    Vertex vertices[] = {
        // Triangle 1
        {{-halfW, -halfH}, {1, 1, 1, 1}, {0, 1}},  // Bottom-left
        {{ halfW, -halfH}, {1, 1, 1, 1}, {1, 1}},  // Bottom-right
        {{-halfW,  halfH}, {1, 1, 1, 1}, {0, 0}},  // Top-left
        
        // Triangle 2
        {{ halfW, -halfH}, {1, 1, 1, 1}, {1, 1}},  // Bottom-right
        {{ halfW,  halfH}, {1, 1, 1, 1}, {1, 0}},  // Top-right
        {{-halfW,  halfH}, {1, 1, 1, 1}, {0, 0}}   // Top-left
    };
    
    // Upload vertices
    glBindVertexArray(vao_);
    glBindBuffer(GL_ARRAY_BUFFER, vbo_);
    glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_DYNAMIC_DRAW);
    
    // Set MVP matrix uniform
    int mvpLoc = glGetUniformLocation(shaderProgram_, "uMVPMatrix");
    glUniformMatrix4fv(mvpLoc, 1, GL_FALSE, mvpMatrix);
    
    // Bind texture
    glActiveTexture(GL_TEXTURE0);
    glBindTexture(GL_TEXTURE_2D, texture);
    glUniform1i(glGetUniformLocation(shaderProgram_, "uTexture"), 0);
    
    // Draw
    glDrawArrays(GL_TRIANGLES, 0, 6);
    
    glBindVertexArray(0);
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
    // Column-major matrix multiplication: C = A * B
    // result[col][row] = sum(a[k][row] * b[col][k])
    for (int col = 0; col < 4; col++) {
        for (int row = 0; row < 4; row++) {
            result[col * 4 + row] = 0;
            for (int k = 0; k < 4; k++) {
                result[col * 4 + row] += a[k * 4 + row] * b[col * 4 + k];
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
