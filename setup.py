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


from setuptools import Extension, setup
import pybind11
import setuptools
from pybind11.setup_helpers import Pybind11Extension
from setuptools import find_packages, setup
from setuptools.command.build_ext import build_ext

# 获取 pybind11 的 include 路径
pybind11_include = pybind11.get_include()

# 检测当前编译器
compiler = get_default_compiler()

# 设定编译选项
extra_compile_args = []
extra_link_args = []

if platform.system() == 'Windows' and compiler == 'msvc':  # 对于 MSVC 编译器（Windows）
    extra_compile_args = ['/O2', '/std:c++17', '/openmp']
elif platform.system() != 'Windows' and compiler != 'msvc':  # 对于 GCC 或 Clang 编译器（Linux/macOS）
    extra_compile_args = ['-O3', '-std=c++17', '-fopenmp']
# 定义扩展模块
ext_modules = [
    Extension(
        "nep_cpu",  # 模块名
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

is_win_64 = sys.platform.startswith("win") and platform.machine().endswith("64")
extra_link_args = ["-Wl,--allow-multiple-definition"] if is_win_64 else []

setup(
    author="Chen Cheng bing",
cmdclass={'build_ext': BuildExt},
    # include_dirs=[np.get_include()],
ext_modules=ext_modules,
zip_safe=False,
)