#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/12/20 17:18
# @Author  : 兵
# @email    : 1747193328@qq.com
import numpy as np
from PySide6.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QSizePolicy,QVBoxLayout
from ..plot.makedata import MakeDataGraphicsWidget
from .. import Structure
def pca(X, k):
    # 1. 标准化数据（去均值和方差标准化）

    mean = np.mean(X, axis=0)
    X_centered = X - mean


    # 2. 计算协方差矩阵
    cov_matrix = np.cov(X_centered.T)

    # 3. 特征值分解协方差矩阵
    eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)

    # 4. 对特征值进行排序，选择前k个特征值和对应的特征向量
    sorted_indices = np.argsort(eigenvalues)[::-1]  # 从大到小排序
    top_k_eigenvectors = eigenvectors[:, sorted_indices[:k]]

    # 5. 投影到前k个主成分
    X_pca = X_centered.dot(top_k_eigenvectors)

    return X_pca

class MakeDataWidget(QWidget):
    """
微扰训练集制作
    """
    def __init__(self,parent=None):
        super().__init__(parent)
        self._parent = parent
        self.setObjectName("MakeDataWidget")
        self.setAcceptDrops(True)
        self.nep_result_data=None
        self.init_ui()

    def dragEnterEvent(self, event):
        # 检查拖拽的内容是否包含文件
        if event.mimeData().hasUrls():
            event.acceptProposedAction()  # 接受拖拽事件
        else:
            event.ignore()  # 忽略其他类型的拖拽

    def dropEvent(self, event):
        # 获取拖拽的文件路径
        urls = event.mimeData().urls()
        if urls:
            # 获取第一个文件路径
            file_path = urls[0].toLocalFile()
            print(file_path)
            self.test(file_path)

    def init_ui(self):

        self.gridLayout = QGridLayout(self)
        self.gridLayout.setObjectName("make_data_gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.left_widget = QWidget(self)
        self.left_layout = QVBoxLayout(self.left_widget)
        self.plot_widget = MakeDataGraphicsWidget(self.left_widget)
        self.left_layout.addWidget(self.plot_widget)

        self.gridLayout.addWidget(self.left_widget , 0, 0, 1, 1)

        self.setLayout(self.gridLayout)

    def test(self,path):
        structures = Structure.read_multiple(path)
        desc_array=[structure.positions for structure in structures if structure.num_atoms==90]
        desc_array = pca(np.array(desc_array), 2)
