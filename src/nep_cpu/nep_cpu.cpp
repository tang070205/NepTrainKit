#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "nep.h"
#include "nep.cpp"

#include <tuple>

namespace py = pybind11;

// 计算列的平均值
std::vector<double> calculate_column_averages(const std::vector<std::vector<double>>& arr) {
    std::vector<double> averages;

    if (arr.empty()) return averages;

    size_t num_columns = arr[0].size();

    // 计算每列的平均值
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

// 计算行的平均值
std::vector<double> calculate_row_averages(const std::vector<std::vector<double>>& arr) {
    std::vector<double> averages;

    if (arr.empty()) return averages;

    // 遍历每一行
    for (const auto& row : arr) {
        double sum = 0;
        size_t num_elements = row.size();

        // 遍历当前行的每个元素，累加
        for (size_t i = 0; i < num_elements; ++i) {
            sum += row[i];
        }

        // 计算该行的平均值并保存
        averages.push_back(sum / num_elements);
    }

    return averages;
}

// 重塑数组（将一维数组重塑为二维）
void reshape(const std::vector<double>& input, int rows, int cols, std::vector<std::vector<double>>& result) {
    if (input.size() != rows * cols) {
        throw std::invalid_argument("The number of elements does not match the new shape.");
    }

    result.resize(rows, std::vector<double>(cols));
    for (int i = 0; i < rows; ++i) {
        for (int j = 0; j < cols; ++j) {
            result[i][j] = input[i * cols + j];
        }
    }
}

// 矩阵转置
void transpose(const std::vector<std::vector<double>>& input, std::vector<std::vector<double>>& output) {
    int rows = input.size();
    int cols = input[0].size();

    // 初始化转置矩阵
    output.resize(cols, std::vector<double>(rows));

    // 执行转置操作
    for (int r = 0; r < rows; ++r) {
        for (int c = 0; c < cols; ++c) {
            output[c][r] = input[r][c];
        }
    }
}

class CpuNep : public NEP3 {
public:
    CpuNep(const std::string& potential_filename) : NEP3(potential_filename) {}

    // 计算所有结构的 potential, force, virial


std::tuple<std::vector<std::vector<double>>,
           std::vector<std::vector<double>>,
           std::vector<std::vector<double>>>
calculate(const std::vector<std::vector<int>>& type,
          const std::vector<std::vector<double>>& box,
          const std::vector<std::vector<double>>& position) {

    size_t type_size = type.size();
    std::vector<std::vector<double>> potentials(type_size);  // 预分配空间
    std::vector<std::vector<double>> forces(type_size);      // 预分配空间
    std::vector<std::vector<double>> virials(type_size);     // 预分配空间


    // OpenMP 并行化报错
    #if defined(_OPENMP)
    #pragma omp parallel for
    #endif
    for (size_t i = 0; i < type_size; ++i) {
        std::vector<double> potential_for_structure(type[i].size());
        std::vector<double> force_for_structure(type[i].size() * 3);  // 假设 force 是 3D 向量
        std::vector<double> virial_for_structure(type[i].size() * 9);  // 假设 virial 是 3x3 矩阵
        compute(type[i], box[i], position[i], potential_for_structure, force_for_structure, virial_for_structure );

        potentials[i] = potential_for_structure;
        forces[i] = force_for_structure;
        virials[i] = virial_for_structure;


    }

    return std::make_tuple(potentials, forces, virials);
}


    // 获取 descriptor
    std::vector<double> get_descriptor(const std::vector<int>& type,
                                       const std::vector<double>& box,
                                       const std::vector<double>& position) {
        std::vector<double> descriptor(type.size() * annmb.dim);
        find_descriptor(type, box, position, descriptor);
        return descriptor;
    }

    // 获取元素列表
    std::vector<std::string> get_element_list() {
        return element_list;
    }

    // 获取所有结构的 descriptor
    std::vector<std::vector<double>> get_descriptors(const std::vector<std::vector<int>>& type,
                                                     const std::vector<std::vector<double>>& box,
                                                     const std::vector<std::vector<double>>& position) {

        size_t type_size = type.size();
        std::vector<std::vector<double>> all_descriptors(type_size, std::vector<double>(annmb.dim));

        for (size_t i = 0; i < type_size; ++i) {
            std::vector<double> struct_des(type[i].size() * annmb.dim);
            find_descriptor(type[i], box[i], position[i], struct_des);
//
            // 重塑 descriptor 以适应矩阵
            std::vector<std::vector<double>> struct_des_reshaped;
            reshape(struct_des, annmb.dim, type[i].size(), struct_des_reshaped);

            // 计算行平均
            all_descriptors[i] = calculate_row_averages(struct_des_reshaped);
        }

        return all_descriptors;
    }
};

// pybind11 模块绑定
PYBIND11_MODULE(nep_cpu, m) {
    m.doc() = "A pybind11 module for NEP";

    py::class_<CpuNep>(m, "CpuNep")
        .def(py::init<const std::string &>(), py::arg("potential_filename"))
        .def("calculate", &CpuNep::calculate)
        .def("get_descriptor", &CpuNep::get_descriptor)
        .def("get_element_list", &CpuNep::get_element_list)
        .def("get_descriptors", &CpuNep::get_descriptors);
}
