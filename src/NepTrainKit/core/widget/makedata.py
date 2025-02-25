#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/12/20 17:18
# @Author  : 兵
# @email    : 1747193328@qq.com
import numpy as np
from PySide6.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QSizePolicy,QVBoxLayout,QGroupBox

from .. import Structure
from qfluentwidgets import HeaderCardWidget

from ..custom_widget.card_widget import CheckableHeaderCardWidget


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



    def init_ui(self):

        self.gridLayout = QGridLayout(self)
        self.gridLayout.setObjectName("make_data_gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.left_widget = QWidget(self)
        self.left_layout = QVBoxLayout(self.left_widget)



        self.gridLayout.addWidget(self.left_widget , 0, 0, 1, 1)
        self.card_widget = CheckableHeaderCardWidget(self)
        self.card_widget.setObjectName("card_widget")
        self.card_widget.setFixedSize(400, 200)
        self.card_widget.setTitle("不同晶胞结构")
        self.left_layout.addWidget(self.card_widget)
        self.setLayout(self.gridLayout)


