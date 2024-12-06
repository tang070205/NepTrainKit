#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/10/24 14:22
# @Author  : 兵
# @email    : 1747193328@qq.com
"""Pymatgen package configuration."""

from __future__ import annotations

import platform
import sys
from distutils.ccompiler import get_default_compiler
import os
import subprocess
import pybind11
from pybind11.setup_helpers import Pybind11Extension
from setuptools import  Extension, find_packages, setup
from setuptools.command.build_ext import build_ext

# 获取 pybind11 的 include 路径
pybind11_include = pybind11.get_include()

# 检测当前编译器
compiler = get_default_compiler()

# 设定编译选项
extra_compile_args = []
extra_link_args = []



def check_openmp_support():
    code = """
    #include <omp.h>
    #include <stdio.h>
    int main() {
        #ifdef _OPENMP
        return 0;
        #else
        return 1;
        #endif
    }
    """
    with open("test_openmp.c", "w") as f:
        f.write(code)

    compiler = os.environ.get("CC", "gcc")  # 默认使用 gcc，用户可通过 CC 环境变量指定编译器
    try:
        subprocess.run([compiler, "-fopenmp", "test_openmp.c", "-o", "test_openmp"],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = subprocess.run(["./test_openmp"], check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError:
        return False
    finally:
        os.remove("test_openmp.c")
        for o in ["test_openmp.exe","test_openmp.bin","test_openmp.o","test_openmp"]:
            if os.path.exists(o):
                os.remove(o)

# 检测结果
openmp_supported = check_openmp_support()




if platform.system() == 'Windows' and compiler == 'msvc':  # 对于 MSVC 编译器（Windows）
    extra_compile_args = ['/O2', '/std:c++17' ]
    if openmp_supported:
        extra_compile_args.append('/openmp')
        extra_link_args.append('/openmp')

elif platform.system() != 'Windows' and compiler != 'msvc':  # 对于 GCC 或 Clang 编译器（Linux/macOS）
    extra_compile_args = ['-O3', '-std=c++17' ]
    if openmp_supported:
        extra_compile_args.append('-fopenmp')
        extra_link_args.append('-fopenmp')

# 定义扩展模块
ext_modules = [
    Extension(
        "NepTrainKit.nep_cpu",  # 模块名
        ["src/nep_cpu/nep_cpu.cpp"],  # 源文件
        include_dirs=[
            pybind11_include,
            # "src/nep_cpu"
        ],
        extra_compile_args=extra_compile_args,  # 编译选项
        extra_link_args=extra_link_args,
        language="c++",  # 指定语言为 C++
    ),
]

# 自定义 build_ext 命令，确保兼容性
class BuildExt(build_ext):
    def build_extensions(self):
        # 设置编译器标准为 C++17
        ct = self.compiler.compiler_type
        opts = [ ]
        for ext in self.extensions:
            ext.extra_compile_args = opts + ext.extra_compile_args
        build_ext.build_extensions(self)



setup(
    author="Chen Cheng bing",
cmdclass={'build_ext': BuildExt},
    # include_dirs=[np.get_include()],
ext_modules=ext_modules,
zip_safe=False,
)