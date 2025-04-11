#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/10/24 14:22
# @Author  : 兵
# @email    : 1747193328@qq.com
"""Pymatgen package configuration."""

from __future__ import annotations
import tempfile
import platform
import sys
import os
import subprocess
import pybind11
from pybind11.setup_helpers import Pybind11Extension
from setuptools import Extension, find_packages, setup
from setuptools.command.build_ext import build_ext


# 获取 pybind11 的 include 路径
pybind11_include = pybind11.get_include()

# 设定编译选项
extra_link_args = []
extra_compile_args = []
data_files = []  # 默认初始化为空列表，避免未定义错误

# 检查平台并设置相应的 OpenMP 编译标志
if sys.platform == "win32":
    mingw_bin_dir = os.path.abspath("src/nep_cpu")
    os.environ['CC'] = os.path.join(mingw_bin_dir, 'gcc.exe')
    os.environ['CXX'] = os.path.join(mingw_bin_dir, 'g++.exe')
    data_files = [('bin', [  # 仅 Windows 平台需要 data_files
            os.path.join(mingw_bin_dir, 'gcc.exe'),
            os.path.join(mingw_bin_dir, 'g++.exe'),
            os.path.join(mingw_bin_dir, 'libgcc_s_seh-1.dll'),
            os.path.join(mingw_bin_dir, 'libstdc++-6.dll'),
            os.path.join(mingw_bin_dir, 'libwinpthread-1.dll'),
            os.path.join(mingw_bin_dir, 'libgomp-1.dll')
        ])]
    # 使用 MinGW 的 GCC 编译器
    extra_compile_args.append('-fopenmp')
    extra_compile_args.append('-O3')
    extra_compile_args.append('-std=c++11')

    extra_link_args.append('-fopenmp')
    extra_link_args.append('-O3')
    extra_link_args.append('-std=c++11')
elif sys.platform == "darwin":
    # macOS 使用 Clang（默认不支持 OpenMP）
    extra_compile_args.append('-O3')
    extra_compile_args.append('-std=c++11')

    extra_link_args.append('-O3')
    extra_link_args.append('-std=c++11')
else:
    # Linux 使用 GCC + OpenMP
    extra_compile_args.append('-fopenmp')
    extra_compile_args.append('-O3')
    extra_compile_args.append('-std=c++11')

    extra_link_args.append('-fopenmp')
    extra_link_args.append('-O3')
    extra_link_args.append('-std=c++11')

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
        # 设置编译器标准为 C++11
        ct = self.compiler.compiler_type
        opts = []
        for ext in self.extensions:
            ext.extra_compile_args = opts + ext.extra_compile_args
        try:
            # 尝试构建扩展模块
            build_ext.build_extensions(self)
        except Exception as e:
            # 捕获编译错误并打印警告
            print(f"WARNING: Failed to build extension module: {e}")
            print("WARNING: Skipping nep_cpu module build. The package will be installed without it.")
            # 清空 ext_modules，跳过扩展模块的构建
            self.ext_modules = []


setup(
    author="Chen Cheng bing",
    cmdclass={'build_ext': BuildExt},
    ext_modules=ext_modules,
    data_files=data_files,  # 现在 data_files 始终有定义
    zip_safe=False,
)
