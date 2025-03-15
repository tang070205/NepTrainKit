#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2025/3/15 13:44
# @Author  : 兵
# @email    : 1747193328@qq.com
import json
import os.path

import numpy as np
from PySide6 import QtOpenGL
from PySide6.QtGui import QColor

from OpenGL.GL import *  # noqa

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
import pyqtgraph as pg
import pyqtgraph.opengl as gl


from NepTrainKit.core import MessageManager, Config
from NepTrainKit.core.structure import table_info,Structure

class StructurePlotWidget(gl.GLViewWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setBackgroundColor('w')
        self.setCameraPosition(distance=30, elevation=30, azimuth=30)

    def show_lattice(self, structure):
        origin = np.array([0.0, 0.0, 0.0])
        a1 = structure.cell[0]
        a2 = structure.cell[1]
        a3 = structure.cell[2]

        vertices = np.array([
            origin, a1, a2, a3,
            a1 + a2, a1 + a3, a2 + a3,
            a1 + a2 + a3
        ])

        edges = [
            [0, 1], [0, 2], [0, 3],
            [1, 4], [1, 5],
            [2, 4], [2, 6],
            [3, 5], [3, 6],
            [4, 7], [5, 7], [6, 7]
        ]

        lines = []
        for edge in edges:
            lines.append(vertices[edge])

        lines = np.array(lines).reshape(-1, 3)
        lattice_lines = gl.GLLinePlotItem(
            pos=lines,
            color=(0, 0, 0, 1),
            width=1.5,
            mode='lines',
            glOptions="translucent",
            antialias=True
        )
        center = structure.cell.sum(axis=0) / 2
        self.opts['center'] = pg.Vector(center[0], center[1], center[2])
        self.addItem(lattice_lines)

    def get_bond_pairs(self, structure):
        # distances = structure.get_all_distances()
        i, j = np.triu_indices(len(structure), k=1)  # k=1 排除对角线

        # 计算上三角部分的距离矩阵
        pos = np.array(structure.positions)
        # 使用np.triu_indices生成上三角索引（不包括对角线）

        diff = pos[i] - pos[j]
        upper_distances = np.linalg.norm(diff, axis=1)



        #获取每个原子的共价半径(单位通常是Å)
        covalent_radii = np.array([table_info[str(n)]["radii"] / 100 for n in structure.numbers])  # 转换为Å
        # 计算共价半径之和的矩阵
        radius_sum = covalent_radii[i] + covalent_radii[j]
        bond_mask = (upper_distances < radius_sum*1.15)
        # 获取成键的原子对索引
        bond_pairs = [(i[k], j[k]) for k in np.where(bond_mask)[0]]

        return bond_pairs
    def show_bond(self, pos1, pos2, color1, color2, radius1, radius2,bond_radius=0.12):
        """使用圆柱体绘制两个原子之间的化学键，从球体表面开始"""
        # 计算键的方向和长度
        bond_vector = pos2 - pos1
        full_length = np.linalg.norm(bond_vector)
        bond_dir = bond_vector / full_length

        start_point=pos1
        end_point=pos2
        mid_point = (start_point + end_point) / 2
        # 计算键的旋转角度和轴
        bond=full_length-radius1-radius2
        bond1_length = radius1 + bond/2
        bond2_length = radius2 + bond/2
        # 调整起点和终点到球体表面
        # bond2_length = np.linalg.norm(end_point-mid_point)
        # 调整起点和终点到球体表面


        mid_point =start_point +bond_dir* bond1_length
        # start_point=


        # 创建圆柱体


        # 第一半部分（从start_point到中间）
        cylinder1 = gl.MeshData.cylinder(
            rows=10,
            cols=20,
            radius=[bond_radius, bond_radius],
            length=bond1_length
        )
        bond1 = gl.GLMeshItem(
            meshdata=cylinder1,
            smooth=True,
            shader='shaded',
            color=color1
        )

        # 计算旋转角度和轴
        z_axis = np.array([0, 0, 1])

        axis = np.cross(z_axis, bond_dir)
        if np.linalg.norm(axis) > 0:
            axis = axis / np.linalg.norm(axis)
            angle = np.arccos(np.dot(z_axis, bond_dir)) * 180 / np.pi
            bond1.rotate(angle, axis[0], axis[1], axis[2])

        bond1.translate(start_point[0], start_point[1], start_point[2])
        # bond1.translate(0, 0, bond1_length/2)  # 调整到正确位置
        self.addItem(bond1)

        # 第二半部分（从中间到end_point）
        cylinder2 = gl.MeshData.cylinder(
            rows=10,
            cols=20,
            radius=[bond_radius, bond_radius],
            length=bond2_length
        )
        bond2 = gl.GLMeshItem(
            meshdata=cylinder2,
            smooth=True,
            shader='shaded',
            color=color2
        )

        if np.linalg.norm(axis) > 0:
            bond2.rotate(angle, axis[0], axis[1], axis[2])

        bond2.translate(mid_point[0], mid_point[1], mid_point[2])
        # bond2.translate(0, 0,bond2_length/2)  # 调整到正确位置
        self.addItem(bond2)

    def show_elem(self, structure):
        # 原子显示为较小的球

        for n, p in zip(structure.numbers, structure.positions):
            color = QColor(table_info[str(n)]["color"]).getRgbF()
            size = table_info[str(n)]["radii"] / 150
            # size=0.8
            sphere = gl.MeshData.sphere(rows=10, cols=10, radius=size)
            m = gl.GLMeshItem(
                meshdata=sphere,
                smooth=True,
                shader='shaded',
                color=color
            )
            m.translate(p[0], p[1], p[2])
            self.addItem(m)


        # 添加化学键
        radius_coefficient_config = Config.getfloat("widget","radius_coefficient",0.9)

        bond_pairs = self.get_bond_pairs(structure)
        for pair in bond_pairs:
            elem0_info = table_info[str(structure.numbers[pair[0]])]
            elem1_info = table_info[str(structure.numbers[pair[1]])]

            pos1 = structure.positions[pair[0]]
            pos2 = structure.positions[pair[1]]
            bond_length = np.linalg.norm(pos1 - pos2)
            if (elem0_info["radii"] + elem1_info["radii"]) * radius_coefficient_config > bond_length*100:
                color1=(1.0, 0.0, 0.0, 0.7)
                color2=(1.0, 0.0, 0.0, 0.7)
                bond_radius=0.3
            else:
                color1 = QColor(elem0_info["color"]).getRgbF()
                color2 = QColor(elem1_info["color"]).getRgbF()
                bond_radius = 0.15
            radius1 = table_info[str(structure.numbers[pair[0]])]["radii"] / 150
            radius2 = table_info[str(structure.numbers[pair[1]])]["radii"] / 150
            # radius1=0.8
            # radius2=0.8
            self.show_bond(pos1, pos2, color1, color2, radius1, radius2,bond_radius=bond_radius)


    def show_structure(self, structure):
        self.clear()
        self.show_lattice(structure)
        self.show_elem(structure)


if __name__ == '__main__':
    app = QApplication([])
    view = StructurePlotWidget()
    view.show()
    import time
    start = time.time()
    atoms = Structure.read_xyz("good.xyz")
    view.show_atoms(atoms)
    print(time.time() - start)
    QApplication.instance().exec_()