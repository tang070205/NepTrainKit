#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/10/17 13:38
# @Author  : 兵
# @email    : 1747193328@qq.com
import os.path

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QWidget,QGridLayout
from qfluentwidgets import HyperlinkLabel
import utils
from core.plot.plot import init_canvas


class ShowNepWidget(QWidget):
    """
    针对NEP训练过程中 对预测结果的展示
    实现以下功能
        1.支持交互筛选训练集
        2.拖拽实现目录导入
        3.对于选定的结构 进行展示
    """
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setObjectName("ShowNepWidget")
        self.setAcceptDrops(True)
        self.init_ui()

    def init_ui(self):
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setObjectName("show_nep_gridLayout")
        self.gridLayout.setContentsMargins(0,0,0,0)
        self.plot_widget = QWidget(self)
        # self.plot_widget.setObjectName("plot_widget")
        self.show_struct_widget = QWidget(self)
        self.Canvas = init_canvas(self.plot_widget)
        self.Canvas.add_axes(2,2)
        self.gridLayout.addWidget(self.plot_widget, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.show_struct_widget, 0, 1, 1, 1)


        # 创建状态栏
        self.path_label = HyperlinkLabel(  self)
        self.path_label.setFixedHeight(30)  # 设置状态栏的高度

        # 将状态栏添加到布局的底部
        self.gridLayout.addWidget(self.path_label, 1, 0, 1, 2)
        self.gridLayout.setColumnStretch(0, 2)
        self.gridLayout.setColumnStretch(1, 1)

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

            self.set_work_path(file_path)


    def open_file(self):
        path = utils.call_path_dialog(self,"请选择工作路径","directory")
        if path:
            self.set_work_path(path)
    def set_work_path(self,path):

        if os.path.isfile(path):
            path = os.path.dirname(path)
        self.path_label.setText(f"当前工作路径：{path}")
        self.path_label.setUrl(QUrl.fromLocalFile(path))