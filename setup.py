#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import sys
import platform
import subprocess
import pybind11
from pybind11.setup_helpers import Pybind11Extension
from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext

# 获取系统架构信息
SYSTEM = sys.platform
ARCH = platform.machine()
IS_64BIT = sys.maxsize > 2 ** 32

# 静态编译配置参数
STATIC_FLAGS = {
    'win32': {
        'compile': ['/MT', '/openmp', '/O2', '/std:c++17', '/Zc:__cplusplus', '/permissive-'],
        'link': ['/NODEFAULTLIB:libcmt', '/DEBUG:NONE', 'vcomp140.lib']
    },
    'linux': {
        'compile': ['-fopenmp', '-O3', '-std=c++17', '-static-libstdc++'],
        'link': ['-fopenmp', '-static-libgcc', '-Wl,-Bstatic', '-lomp', '-Wl,-Bdynamic']
    },
    'darwin': {
        'compile': ['-Xpreprocessor', '-fopenmp', '-O3', '-std=c++17'],
        'link': ['-lomp', '-Wl,-rpath,@loader_path/']
    }
}


class UniversalBuild(build_ext):
    """跨平台静态编译构建器"""

    def _get_omp_path(self):
        """获取OpenMP库路径"""
        if SYSTEM == 'darwin':
            # 自动检测Homebrew安装的libomp路径
            brew_path = subprocess.check_output(
                ['brew', '--prefix'], text=True).strip()
            return f"{brew_path}/opt/libomp"
        return None

    def build_extensions(self):
        # 设置平台特定参数
        omp_path = self._get_omp_path()
        config = STATIC_FLAGS.get(SYSTEM, {})

        for ext in self.extensions:
            # 添加通用编译参数
            ext.extra_compile_args = [
                *config.get('compile', []),
                '-DNDEBUG',
                '-D_FORTIFY_SOURCE=2',
                '-march=native' if SYSTEM != 'win32' else ''
            ]

            # 添加链接参数
            ext.extra_link_args = [
                *config.get('link', []),
                '-fuse-ld=lld' if SYSTEM != 'darwin' else ''
            ]

            # macOS特殊处理
            if SYSTEM == 'darwin' and omp_path:
                ext.include_dirs.append(f"{omp_path}/include")
                ext.library_dirs.append(f"{omp_path}/lib")
                ext.extra_link_args.append(f"-L{omp_path}/lib")

            # Windows特殊处理
            if SYSTEM == 'win32':
                ext.define_macros.append(('NOMINMAX', None))
                ext.extra_compile_args.extend([
                    '--target=x86_64-pc-windows-msvc',
                    '-fms-extensions',
                    '-fms-compatibility'
                ])
                ext.extra_link_args.extend([
                    '-fuse-ld=lld',
                    '--target=x86_64-pc-windows-msvc'
                ])

        # 调用父类构建方法
        try:
            super().build_extensions()
        except Exception as e:
            print(f"⚠️ Extension build failed: {e}")
            print("⚠️ Falling back to pure Python implementation")
            self.extensions = []


# 扩展模块配置
ext_modules = [
    Pybind11Extension(
        "NepTrainKit.nep_cpu",
        ["src/nep_cpu/nep_cpu.cpp"],
        include_dirs=[
            pybind11.get_include(),
            "src/nep_cpu",
            *([STATIC_FLAGS['darwin']['include']] if SYSTEM == 'darwin' else [])
        ],
        cxx_std=17,
        define_macros=[('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION')],
        language='c++'
    )
]

# 设置入口
setup(
    name="NepTrainKit",
    # version="0.1",
    author="Chen Cheng bing",
    ext_modules=ext_modules,
    cmdclass={'build_ext': UniversalBuild},
    zip_safe=False,
    python_requires='>=3.7',
    setup_requires=['pybind11>=2.6', 'numpy>=1.18'],
    install_requires=['numpy>=1.18', 'pybind11>=2.6']
)