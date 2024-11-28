#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "nep.h"
#include "nep.cpp"
namespace py = pybind11;

PYBIND11_MODULE(nep_cpu, m) {
         m.doc() = "A pybind11 module for NEP";

    py::class_<NEP3>(m, "NEP3")
        .def(py::init<const std::string &>(), py::arg("potential_filename"))
        .def("find_descriptors", [](NEP3& self, 
                                   const std::vector<int>& type, 
                                   const std::vector<double>& box, 
                                   const std::vector<double>& position) {
            std::vector<double> descriptor(type.size() * self.annmb.dim);
            self.find_descriptor(type, box, position, descriptor);
            return descriptor;
        })
        .def(
            "get_element_list", 
            [](NEP3& self ) {
             
            return self.element_list;
        }
        );
}
