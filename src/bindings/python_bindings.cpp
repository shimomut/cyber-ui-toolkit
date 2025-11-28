#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../core/Object3D.h"
#include "../rendering/Shape2D.h"
#include "../rendering/Renderer.h"

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
        .def("should_close", &Renderer::shouldClose)
        .def("poll_events", &Renderer::pollEvents);

    // Factory function
    m.def("create_metal_renderer", &createMetalRenderer,
          "Create a Metal-based renderer for macOS");

    // Object3D base class
    py::class_<Object3D, std::shared_ptr<Object3D>>(m, "Object3D")
        .def("add_child", &Object3D::addChild)
        .def("remove_child", &Object3D::removeChild)
        .def("get_parent", &Object3D::getParent, py::return_value_policy::reference)
        .def("set_position", &Object3D::setPosition)
        .def("get_position", [](const Object3D& obj) {
            float x, y, z;
            obj.getPosition(x, y, z);
            return py::make_tuple(x, y, z);
        })
        .def("set_visible", &Object3D::setVisible)
        .def("is_visible", &Object3D::isVisible)
        .def("set_name", &Object3D::setName)
        .def("get_name", &Object3D::getName)
        .def("render", &Object3D::render);

    // Shape2D class
    py::class_<Shape2D, Object3D, std::shared_ptr<Shape2D>>(m, "Shape2D")
        .def(py::init<>())
        .def("set_color", &Shape2D::setColor, 
             py::arg("r"), py::arg("g"), py::arg("b"), py::arg("a") = 1.0f)
        .def("get_color", [](const Shape2D& shape) {
            float r, g, b, a;
            shape.getColor(r, g, b, a);
            return py::make_tuple(r, g, b, a);
        });

    // Rectangle class
    py::class_<Rectangle, Shape2D, std::shared_ptr<Rectangle>>(m, "Rectangle")
        .def(py::init<float, float>(), 
             py::arg("width") = 100.0f, py::arg("height") = 100.0f)
        .def("set_size", &Rectangle::setSize)
        .def("get_size", [](const Rectangle& rect) {
            float w, h;
            rect.getSize(w, h);
            return py::make_tuple(w, h);
        });
}
