#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/10/20 21:45
# @Author  : 兵
# @email    : 1747193328@qq.com
import json
import os.path
import sys
import numpy as np
from PySide6.QtGui import QColor


from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
import pyqtgraph as pg
import pyqtgraph.opengl as gl

from NepTrainKit.core import MessageManager
from NepTrainKit import module_path

class StructurePlotWidget(gl.GLViewWidget):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        # 创建 PyQtGraph 的 3D 窗口
        self.setBackgroundColor('w')
        self.setCameraPosition(distance=30, elevation=30, azimuth=30)
        with open(os.path.join(module_path,"Config/ptable.json"), "r",encoding="utf-8") as f:
            self.table_info=json.loads(f.read())
        # self.setAntialiasing(True)

    def show_lattice(self,lattice_matrix):


        # 定义晶格顶点
        origin = np.array([0.0, 0.0, 0.0])
        a1 = lattice_matrix[0]
        a2 = lattice_matrix[1]
        a3 = lattice_matrix[2]

        vertices = np.array([
            origin,  # (0, 0, 0)
            a1,  # a1
            a2,  # a2
            a3,  # a3
            a1 + a2,  # a1 + a2
            a1 + a3,  # a1 + a3
            a2 + a3,  # a2 + a3
            a1 + a2 + a3  # a1 + a2 + a3
        ])

        # 定义线条连接的顶点索引
        edges = [
            [0, 1], [0, 2], [0, 3],  # 从原点到三个基矢量的线
            [1, 4], [1, 5],  # a1 与 a1 + a2, a1 + a3
            [2, 4], [2, 6],  # a2 与 a1 + a2, a2 + a3
            [3, 5], [3, 6],  # a3 与 a1 + a3, a2 + a3
            [4, 7], [5, 7], [6, 7]  # 顶部的三个线
        ]

        # 将顶点坐标转换为线段的起点和终点
        lines = []
        for edge in edges:
            lines.append(vertices[edge])

        lines = np.array(lines).reshape(-1, 3)

        # 绘制晶格线条
        lattice_lines = gl.GLLinePlotItem(pos=lines, color=(0,0,0,1),
                                          width=1.5, mode='lines',glOptions="translucent",
                                          antialias=True

                                          )
        # lattice_lines.color=(0,1,0,1)
        center = lattice_matrix.sum(axis=0) / 2
        self.opts['center'] = pg.Vector(center[0], center[1], center[2])
        self.addItem(lattice_lines)


    def show_elem(self,numbers,postions):

        for n,p in zip(numbers,postions):
            color=QColor(self.table_info[str(n)]["color"]).getRgbF()
            size=self.table_info[str(n)]["radii"]/100

            sphere = gl.MeshData.sphere(rows=20, cols=20,radius=size)
            m = gl.GLMeshItem(meshdata=sphere, smooth=False, shader='shaded', color=color)
            self.addItem(m)

            m.translate(p[0], p[1], p[2])  # 设置球体的位置


    def show_atoms(self,atoms):

        self.clear()

        self.show_lattice(atoms.cell )
        self.show_elem(atoms.numbers,atoms.positions)
if __name__ == '__main__':
    app = QApplication([])
    view = AtomsPlotWidget()
    view.show()
    QApplication.instance().exec_()
