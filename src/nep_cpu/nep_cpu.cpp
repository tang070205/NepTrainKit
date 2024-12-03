#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "nep.h"
#include "nep.cpp"
#include <omp.h>
namespace py = pybind11;

std::vector<double> calculate_column_averages(const std::vector<std::vector<double>>& arr) {
    std::vector<double> averages;

    if (arr.empty()) return averages;

    size_t num_columns = arr[0].size();

    // 使用一行一行的平均计算，而不是计算整个数组
    for (size_t col = 0; col < num_columns; ++col) {
        double sum = 0;
        size_t row_count = arr.size();
        for (size_t row = 0; row < row_count; ++row) {
            sum += arr[row][col];
        }
        averages.push_back(sum / row_count);
    }

    return averages;
}
std::vector<double> calculate_row_averages(const std::vector<std::vector<double>>& arr) {
    std::vector<double> averages;

    if (arr.empty()) return averages;  // 如果输入数组为空，返回空的平均值列表

    // 遍历每一行
    for (const auto& row : arr) {
        double sum = 0;
        size_t num_elements = row.size();

        // 遍历当前行的每一个元素，累加
        for (size_t i = 0; i < num_elements; ++i) {
            sum += row[i];
        }

        // 计算该行的平均值并保存
        averages.push_back(sum / num_elements);
    }

    return averages;
}

std::vector<std::vector<double>> reshape(const std::vector<double>& input, int rows, int cols) {
    if (input.size() != rows * cols) {
        throw std::invalid_argument("The number of elements does not match the new shape.");
    }

    std::vector<std::vector<double>> result(rows, std::vector<double>(cols));
    for (int i = 0; i < rows; ++i) {
        for (int j = 0; j < cols; ++j) {
            result[i][j] = input[i * cols + j];
        }
    }

    return result;
}

class CpuNep : public NEP3 {
public:
    CpuNep(const std::string& potential_filename) : NEP3(potential_filename) {}

    std::vector<double> get_descriptor(const std::vector<int>& type,
                                       const std::vector<double>& box,
                                       const std::vector<double>& position) {
        std::vector<double> descriptor(type.size() * annmb.dim);
        find_descriptor(type, box, position, descriptor);
        return descriptor;
    }

    std::vector<std::string> get_element_list() {
        return element_list;
    }



    std::vector<std::vector<double>> get_descriptors(const std::vector<std::vector<int>>& type,
                                                     const std::vector<std::vector<double>>& box,
                                                     const std::vector<std::vector<double>>& position) {

        size_t type_size = type.size();
        std::vector<std::vector<double>> all_descriptors(type_size, std::vector<double>(annmb.dim));
        for (size_t i = 0; i < type_size; ++i) {
            std::vector<double> struct_des(type[i].size() * annmb.dim);
            find_descriptor(type[i], box[i], position[i], struct_des);
            std::vector<std::vector<double>> struct_des_reshaped = reshape(struct_des,   annmb.dim,type[i].size());
            all_descriptors[i] = calculate_row_averages(struct_des_reshaped);
        }


        return all_descriptors;
    }
};

PYBIND11_MODULE(nep_cpu, m) {
    m.doc() = "A pybind11 module for NEP";

    py::class_<CpuNep>(m, "CpuNep")
        .def(py::init<const std::string &>(), py::arg("potential_filename"))
        .def("get_descriptor", &CpuNep::get_descriptor)
        .def("get_element_list", &CpuNep::get_element_list)
        .def("get_descriptors", &CpuNep::get_descriptors);
}
