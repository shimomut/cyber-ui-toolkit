.PHONY: all build build-metal build-opengl clean run-hierarchy run-clipping test-capture test-clipping install-deps help

# Configuration
CXX := clang++
PYTHON := python3
PYTHON_INCLUDE := $(shell $(PYTHON) -c "import sysconfig; print(sysconfig.get_path('include'))")
PYTHON_EXT_SUFFIX := $(shell $(PYTHON) -c "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))")
PYBIND11_INCLUDE := $(shell $(PYTHON) -m pybind11 --includes 2>/dev/null || echo "")

# Directories
BUILD_DIR := build
SRC_DIR := src
OBJ_DIR := $(BUILD_DIR)/obj

# Backend selection (default: metal)
BACKEND ?= metal

# Compiler flags
CXXFLAGS := -std=c++17 -O3 -Wall -fPIC
OBJCXXFLAGS := -std=c++17 -O3 -Wall -fPIC -fobjc-arc
INCLUDES := -I$(SRC_DIR) -I$(PYTHON_INCLUDE) $(PYBIND11_INCLUDE)

# Backend-specific flags
ifeq ($(BACKEND),opengl)
    GLFW_PREFIX := $(shell brew --prefix glfw 2>/dev/null || echo "/usr/local")
    CXXFLAGS += -DUSE_OPENGL_BACKEND -I$(GLFW_PREFIX)/include
    LDFLAGS := -shared -undefined dynamic_lookup -L$(GLFW_PREFIX)/lib -lglfw -framework OpenGL
    BACKEND_SOURCES := $(SRC_DIR)/rendering/OpenGLRenderer.cpp
    BACKEND_OBJECTS := $(OBJ_DIR)/rendering/OpenGLRenderer.o
else
    CXXFLAGS += -DUSE_METAL_BACKEND
    OBJCXXFLAGS += -DUSE_METAL_BACKEND
    LDFLAGS := -shared -undefined dynamic_lookup -framework Metal -framework MetalKit -framework Cocoa -framework QuartzCore
    BACKEND_SOURCES := $(SRC_DIR)/rendering/MetalRenderer.mm
    BACKEND_OBJECTS := $(OBJ_DIR)/rendering/MetalRenderer.o
endif

# Source files
CORE_SOURCES := $(SRC_DIR)/core/Object2D.cpp $(SRC_DIR)/core/Frame3D.cpp $(SRC_DIR)/core/Frame2D.cpp $(SRC_DIR)/core/Camera.cpp $(SRC_DIR)/core/SceneRoot.cpp
RENDERING_SOURCES := $(SRC_DIR)/rendering/Shape2D.cpp $(SRC_DIR)/rendering/Image.cpp $(SRC_DIR)/rendering/Font.cpp $(SRC_DIR)/rendering/Text.cpp $(SRC_DIR)/rendering/RendererFactory.cpp
BINDING_SOURCES := $(SRC_DIR)/bindings/python_bindings.cpp
COMMON_CPP_SOURCES := $(CORE_SOURCES) $(RENDERING_SOURCES) $(BINDING_SOURCES)

# Object files
COMMON_CPP_OBJECTS := $(patsubst $(SRC_DIR)/%.cpp,$(OBJ_DIR)/%.o,$(COMMON_CPP_SOURCES))
OBJECTS := $(COMMON_CPP_OBJECTS) $(BACKEND_OBJECTS)

# Output library
TARGET := $(BUILD_DIR)/cyber_ui_core$(PYTHON_EXT_SUFFIX)

# Default target
all: build

# Build with Metal backend
build-metal:
	@$(MAKE) build BACKEND=metal

# Build with OpenGL backend
build-opengl:
	@$(MAKE) build BACKEND=opengl

# Build the C++ library
build: $(TARGET)

$(TARGET): $(OBJECTS)
	@echo "Linking $@..."
	@mkdir -p $(dir $@)
	@$(CXX) $(LDFLAGS) -o $@ $^
	@echo "Build complete: $@"

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp
	@echo "Compiling $<..."
	@mkdir -p $(dir $@)
	@$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

$(OBJ_DIR)/rendering/MetalRenderer.o: $(SRC_DIR)/rendering/MetalRenderer.mm
	@echo "Compiling $<..."
	@mkdir -p $(dir $@)
	@$(CXX) $(OBJCXXFLAGS) $(INCLUDES) -c $< -o $@

$(OBJ_DIR)/rendering/OpenGLRenderer.o: $(SRC_DIR)/rendering/OpenGLRenderer.cpp
	@echo "Compiling $<..."
	@mkdir -p $(dir $@)
	@$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf $(BUILD_DIR)
	@echo "Clean complete!"

# Install Python dependencies
install-deps:
	@echo "Installing dependencies..."
	@pip3 install pybind11
	@echo "Dependencies installed!"

# Check if pybind11 is installed
check-deps:
	@$(PYTHON) -m pybind11 --includes >/dev/null 2>&1 || \
		(echo "Error: pybind11 not found. Run 'make install-deps' first." && exit 1)

# Run hierarchy demo sample (uses current build)
run-hierarchy:
	@echo "Running hierarchy demo sample..."
	@cd samples/basic && $(PYTHON) hierarchy_demo.py

# Run hierarchy demo with Metal backend
run-hierarchy-metal: build-metal
	@echo "Running hierarchy demo sample (Metal backend)..."
	@cd samples/basic && $(PYTHON) hierarchy_demo.py

# Run hierarchy demo with OpenGL backend
run-hierarchy-opengl: build-opengl
	@echo "Running hierarchy demo sample (OpenGL backend)..."
	@cd samples/basic && $(PYTHON) hierarchy_demo.py

# Run clipping demo sample (uses current build)
run-clipping:
	@echo "Running clipping demo sample..."
	@cd samples/basic && $(PYTHON) clipping_demo.py

# Run clipping demo with Metal backend
run-clipping-metal: build-metal
	@echo "Running clipping demo sample (Metal backend)..."
	@cd samples/basic && $(PYTHON) clipping_demo.py

# Run clipping demo with OpenGL backend
run-clipping-opengl: build-opengl
	@echo "Running clipping demo sample (OpenGL backend)..."
	@cd samples/basic && $(PYTHON) clipping_demo.py

# Run capture tests
test-capture: build
	@echo "Running capture system tests..."
	@$(PYTHON) tests/test_capture.py

# Run clipping tests
test-clipping: build
	@echo "Running Frame2D clipping tests..."
	@cd tests && $(PYTHON) test_clipping_comprehensive.py

# Rebuild from scratch
rebuild: clean build

# Help target
help:
	@echo "Cyber UI Toolkit - Makefile targets:"
	@echo ""
	@echo "Build targets:"
	@echo "  make build                  - Build the C++ library (default: Metal backend)"
	@echo "  make build-metal            - Build with Metal backend"
	@echo "  make build-opengl           - Build with OpenGL backend (requires GLFW)"
	@echo "  make clean                  - Remove build artifacts"
	@echo "  make rebuild                - Clean and build"
	@echo ""
	@echo "Run samples:"
	@echo "  make run-hierarchy          - Run hierarchy demo (uses current build)"
	@echo "  make run-hierarchy-metal    - Build with Metal and run hierarchy demo"
	@echo "  make run-hierarchy-opengl   - Build with OpenGL and run hierarchy demo"
	@echo "  make run-clipping           - Run clipping demo (uses current build)"
	@echo "  make run-clipping-metal     - Build with Metal and run clipping demo"
	@echo "  make run-clipping-opengl    - Build with OpenGL and run clipping demo"
	@echo ""
	@echo "Test targets:"
	@echo "  make test-capture           - Build and run capture system tests"
	@echo "  make test-clipping          - Build and run Frame2D clipping tests"
	@echo ""
	@echo "Other:"
	@echo "  make install-deps           - Install Python dependencies (pybind11)"
	@echo "  make check-deps             - Check if dependencies are installed"
	@echo "  make help                   - Show this help message"
	@echo ""
	@echo "Quick start with OpenGL:"
	@echo "  brew install glfw           # Install GLFW first"
	@echo "  make build-opengl           # Build with OpenGL backend"
	@echo "  make run-hierarchy-opengl   # Run demo with OpenGL"
	@echo ""
