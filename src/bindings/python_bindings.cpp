#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include "../core/Object2D.h"
#include "../core/Frame3D.h"
#include "../core/Frame2D.h"
#include "../core/Camera.h"
#include "../core/SceneRoot.h"
#include "../rendering/Shape2D.h"
#include "../rendering/Renderer.h"
#include "../rendering/Image.h"
#include "../rendering/Font.h"
#include "../rendering/Text.h"

namespace py = pybind11;
using namespace CyberUI;

PYBIND11_MODULE(cyber_ui_core, m) {
    m.doc() = "Cyber UI Toolkit - Graphics Primitive Rendering Layer";

    // Renderer class
    py::class_<Renderer>(m, "Renderer")
        .def("initialize", &Renderer::initialize)
        .def("shutdown", &Renderer::shutdown)
        .def("begin_frame", &Renderer::beginFrame)
        .def("end_frame", &Renderer::endFrame)
        .def("render_object", &Renderer::renderObject)
        .def("render_scene", &Renderer::renderScene)
        .def("should_close", &Renderer::shouldClose)
        .def("poll_events", &Renderer::pollEvents)
        .def("capture_frame", [](Renderer& renderer) {
            std::vector<uint8_t> pixelData;
            int width, height;
            bool success = renderer.captureFrame(pixelData, width, height);
            if (!success) {
                return py::make_tuple(py::none(), 0, 0);
            }
            // Return as numpy-compatible bytes
            py::bytes data(reinterpret_cast<const char*>(pixelData.data()), pixelData.size());
            return py::make_tuple(data, width, height);
        })
        .def("save_capture", &Renderer::saveCapture)
        .def("get_fps", &Renderer::getFPS)
        .def("get_frame_count", &Renderer::getFrameCount);

    // Factory functions
#ifdef USE_METAL_BACKEND
    m.def("create_metal_renderer", &createMetalRenderer,
          "Create a Metal-based renderer for macOS");
#endif
    
#ifdef USE_OPENGL_BACKEND
    m.def("create_opengl_renderer", &createOpenGLRenderer,
          "Create an OpenGL-based renderer (cross-platform)");
#endif

    // Camera class
    py::class_<Camera, std::shared_ptr<Camera>>(m, "Camera")
        .def(py::init<>())
        .def("set_position", &Camera::setPosition)
        .def("get_position", [](const Camera& cam) {
            float x, y, z;
            cam.getPosition(x, y, z);
            return py::make_tuple(x, y, z);
        })
        .def("set_rotation", &Camera::setRotation)
        .def("get_rotation", [](const Camera& cam) {
            float pitch, yaw, roll;
            cam.getRotation(pitch, yaw, roll);
            return py::make_tuple(pitch, yaw, roll);
        })
        .def("set_perspective", &Camera::setPerspective)
        .def("get_fov", [](const Camera& cam) {
            float fov;
            cam.getFOV(fov);
            return fov;
        })
        .def("get_aspect", [](const Camera& cam) {
            float aspect;
            cam.getAspect(aspect);
            return aspect;
        })
        .def("get_near_far", [](const Camera& cam) {
            float near, far;
            cam.getNearFar(near, far);
            return py::make_tuple(near, far);
        });

    // SceneRoot class
    py::class_<SceneRoot, std::shared_ptr<SceneRoot>>(m, "SceneRoot")
        .def(py::init<>())
        .def("add_frame3d", &SceneRoot::addFrame3D)
        .def("remove_frame3d", &SceneRoot::removeFrame3D)
        .def("set_camera", &SceneRoot::setCamera)
        .def("get_camera", &SceneRoot::getCamera)
        .def("clear", &SceneRoot::clear);

    // Frame3D - top-level 3D container
    py::class_<Frame3D, std::shared_ptr<Frame3D>>(m, "Frame3D")
        .def(py::init<int, int>())
        .def("add_child", &Frame3D::addChild)
        .def("remove_child", &Frame3D::removeChild)
        .def("set_position", &Frame3D::setPosition)
        .def("get_position", [](const Frame3D& obj) {
            float x, y, z;
            obj.getPosition(x, y, z);
            return py::make_tuple(x, y, z);
        })
        .def("set_rotation", &Frame3D::setRotation)
        .def("get_rotation", [](const Frame3D& obj) {
            float pitch, yaw, roll;
            obj.getRotation(pitch, yaw, roll);
            return py::make_tuple(pitch, yaw, roll);
        })
        .def("set_scale", &Frame3D::setScale)
        .def("get_scale", [](const Frame3D& obj) {
            float x, y, z;
            obj.getScale(x, y, z);
            return py::make_tuple(x, y, z);
        })
        .def("set_visible", &Frame3D::setVisible)
        .def("is_visible", &Frame3D::isVisible)
        .def("set_name", &Frame3D::setName)
        .def("get_name", &Frame3D::getName)
        .def("is_offscreen_rendering_enabled", &Frame3D::isOffscreenRenderingEnabled)
        .def("set_size", &Frame3D::setSize)
        .def("get_size", [](const Frame3D& obj) {
            int width, height;
            obj.getSize(width, height);
            return py::make_tuple(width, height);
        })
        .def("get_render_target_size", [](const Frame3D& obj) {
            int width, height;
            obj.getRenderTargetSize(width, height);
            return py::make_tuple(width, height);
        })
        .def("render", &Frame3D::render);

    // Object2D base class for all 2D objects
    py::class_<Object2D, std::shared_ptr<Object2D>>(m, "Object2D")
        .def("add_child", &Object2D::addChild)
        .def("remove_child", &Object2D::removeChild)
        .def("get_parent", &Object2D::getParent, py::return_value_policy::reference)
        .def("set_position", &Object2D::setPosition)
        .def("get_position", [](const Object2D& obj) {
            float x, y;
            obj.getPosition(x, y);
            return py::make_tuple(x, y);
        })
        .def("set_visible", &Object2D::setVisible)
        .def("is_visible", &Object2D::isVisible)
        .def("set_name", &Object2D::setName)
        .def("get_name", &Object2D::getName)
        .def("render", &Object2D::render);

    // Frame2D - 2D container with clipping
    py::class_<Frame2D, Object2D, std::shared_ptr<Frame2D>>(m, "Frame2D")
        .def(py::init<float, float>())
        .def("set_size", &Frame2D::setSize)
        .def("get_size", [](const Frame2D& frame) {
            float w, h;
            frame.getSize(w, h);
            return py::make_tuple(w, h);
        })
        .def("set_clipping_enabled", &Frame2D::setClippingEnabled)
        .def("is_clipping_enabled", &Frame2D::isClippingEnabled);

    // Image class (defined before Shape2D since Shape2D uses it)
    py::class_<Image, std::shared_ptr<Image>>(m, "Image")
        .def(py::init<>())
        .def("load_from_file", &Image::loadFromFile)
        .def("load_from_data", [](Image& img, py::buffer data, int width, int height, int channels) {
            // Accept any buffer-like object (bytes, bytearray, numpy array, etc.)
            py::buffer_info buf = data.request();
            return img.loadFromData(static_cast<unsigned char*>(buf.ptr), width, height, channels);
        })
        .def("get_width", &Image::getWidth)
        .def("get_height", &Image::getHeight)
        .def("get_channels", &Image::getChannels)
        .def("is_loaded", &Image::isLoaded)
        .def("get_file_path", &Image::getFilePath);

    // Shape2D class
    py::class_<Shape2D, Object2D, std::shared_ptr<Shape2D>>(m, "Shape2D")
        .def(py::init<>())
        .def("set_color", &Shape2D::setColor, 
             py::arg("r"), py::arg("g"), py::arg("b"), py::arg("a") = 1.0f)
        .def("get_color", [](const Shape2D& shape) {
            float r, g, b, a;
            shape.getColor(r, g, b, a);
            return py::make_tuple(r, g, b, a);
        })
        .def("set_image", &Shape2D::setImage)
        .def("get_image", &Shape2D::getImage)
        .def("has_image", &Shape2D::hasImage);

    // Rectangle class
    py::class_<Rectangle, Shape2D, std::shared_ptr<Rectangle>>(m, "Rectangle")
        .def(py::init<float, float>())
        .def("set_size", &Rectangle::setSize)
        .def("get_size", [](const Rectangle& rect) {
            float w, h;
            rect.getSize(w, h);
            return py::make_tuple(w, h);
        });

    // Font class
    py::class_<Font, std::shared_ptr<Font>>(m, "Font")
        .def(py::init<>())
        .def("load_from_file", &Font::loadFromFile,
             py::arg("file_path"), py::arg("size") = 16.0f)
        .def("set_size", &Font::setSize)
        .def("get_size", &Font::getSize)
        .def("get_file_path", &Font::getFilePath)
        .def("is_loaded", &Font::isLoaded)
        .def("set_bold", &Font::setBold)
        .def("is_bold", &Font::isBold)
        .def("set_italic", &Font::setItalic)
        .def("is_italic", &Font::isItalic);

    // Text class
    py::class_<Text, Object2D, std::shared_ptr<Text>>(m, "Text")
        .def(py::init<const std::string&>(), py::arg("text") = "")
        .def("set_text", &Text::setText)
        .def("get_text", &Text::getText)
        .def("set_font", &Text::setFont)
        .def("get_font", &Text::getFont)
        .def("has_font", &Text::hasFont)
        .def("set_color", &Text::setColor,
             py::arg("r"), py::arg("g"), py::arg("b"), py::arg("a") = 1.0f)
        .def("get_color", [](const Text& text) {
            float r, g, b, a;
            text.getColor(r, g, b, a);
            return py::make_tuple(r, g, b, a);
        })
        .def("set_alignment", &Text::setAlignment)
        .def("get_alignment", &Text::getAlignment);

    // Text alignment enum
    py::enum_<Text::Alignment>(m, "TextAlignment")
        .value("Left", Text::Alignment::Left)
        .value("Center", Text::Alignment::Center)
        .value("Right", Text::Alignment::Right)
        .export_values();
}
