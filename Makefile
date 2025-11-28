.PHONY: all build clean run-basic run-hierarchy install-deps help

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

# Compiler flags
CXXFLAGS := -std=c++17 -O3 -Wall -fPIC
OBJCXXFLAGS := -std=c++17 -O3 -Wall -fPIC -fobjc-arc
INCLUDES := -I$(SRC_DIR) -I$(PYTHON_INCLUDE) $(PYBIND11_INCLUDE)
LDFLAGS := -shared -undefined dynamic_lookup -framework Metal -framework MetalKit -framework Cocoa -framework QuartzCore

# Source files
CORE_SOURCES := $(SRC_DIR)/core/Object2D.cpp $(SRC_DIR)/core/Frame3D.cpp $(SRC_DIR)/core/Frame2D.cpp $(SRC_DIR)/core/Camera.cpp $(SRC_DIR)/core/SceneRoot.cpp
RENDERING_SOURCES := $(SRC_DIR)/rendering/Shape2D.cpp $(SRC_DIR)/rendering/Image.cpp $(SRC_DIR)/rendering/Font.cpp $(SRC_DIR)/rendering/Text.cpp
METAL_SOURCES := $(SRC_DIR)/rendering/MetalRenderer.mm
BINDING_SOURCES := $(SRC_DIR)/bindings/python_bindings.cpp
ALL_CPP_SOURCES := $(CORE_SOURCES) $(RENDERING_SOURCES) $(BINDING_SOURCES)
ALL_MM_SOURCES := $(METAL_SOURCES)

# Object files
CPP_OBJECTS := $(patsubst $(SRC_DIR)/%.cpp,$(OBJ_DIR)/%.o,$(ALL_CPP_SOURCES))
MM_OBJECTS := $(patsubst $(SRC_DIR)/%.mm,$(OBJ_DIR)/%.o,$(ALL_MM_SOURCES))
OBJECTS := $(CPP_OBJECTS) $(MM_OBJECTS)

# Output library
TARGET := $(BUILD_DIR)/cyber_ui_core$(PYTHON_EXT_SUFFIX)

# Default target
all: build

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

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.mm
	@echo "Compiling $<..."
	@mkdir -p $(dir $@)
	@$(CXX) $(OBJCXXFLAGS) $(INCLUDES) -c $< -o $@

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

# Run basic shape2d sample
run-basic: build
	@echo "Running basic shape2d sample..."
	@cd samples/basic && $(PYTHON) shape2d.py

# Run hierarchy demo sample
run-hierarchy: build
	@echo "Running hierarchy demo sample..."
	@cd samples/basic && $(PYTHON) hierarchy_demo.py

# Run text demo sample
run-text: build
	@echo "Running text demo sample..."
	@cd samples/basic && $(PYTHON) text_demo.py

# Rebuild from scratch
rebuild: clean build

# Help target
help:
	@echo "Cyber UI Toolkit - Makefile targets:"
	@echo ""
	@echo "  make build         - Build the C++ library"
	@echo "  make clean         - Remove build artifacts"
	@echo "  make rebuild       - Clean and build"
	@echo "  make install-deps  - Install Python dependencies (pybind11)"
	@echo "  make check-deps    - Check if dependencies are installed"
	@echo "  make run-basic     - Build and run basic shape2d sample"
	@echo "  make run-hierarchy - Build and run hierarchy demo sample"
	@echo "  make run-text      - Build and run text rendering demo sample"
	@echo "  make help          - Show this help message"
	@echo ""
