#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/12/20 17:18
# @Author  : 兵
# @email    : 1747193328@qq.com
from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QGridLayout, QApplication

from NepTrainKit.core.custom_widget import MakeWorkflowArea
from NepTrainKit.core.io.base import StructureData
from NepTrainKit.core.structure import Structure


class ConsoleWidget(QWidget):
    """
控制台"""
    newCardSignal = Signal(str)  # 定义一个信号，用于通知上层组件新增卡片
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setObjectName("ConsoleWidget")
        self.setMinimumHeight(50)
        self.init_ui()
    def init_ui(self):
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setObjectName("console_gridLayout")




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
        # print("dropEvent",event)
        urls = event.mimeData().urls()

        if urls:
            # 获取第一个文件路径
            file_path = urls[0].toLocalFile()
            self.load_base_structure(file_path)
            print(urls)
        # event.accept()
    def load_base_structure(self,path):
        path=Path(path)
        if path.is_file():
            # 读取文件
            structures=Structure.read_multiple(path)
            dataset=StructureData(structures)
            # self.super_cell_card_widget.dataset=dataset
        else:
            structures_list=[]
            for file in path.iterdir():
                if file.is_file():
                    # 读取文件
                    if file.suffix==".xyz":
                        structures=Structure.read_multiple(file)
                        structures_list.extend(structures)
            dataset=StructureData(structures_list)
            # self.super_cell_card_widget.dataset=dataset


    def init_ui(self):

        self.gridLayout = QGridLayout(self)
        self.gridLayout.setObjectName("make_data_gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.workspace_card_widget = MakeWorkflowArea(self)

        self.setting_group=ConsoleWidget(self)


        self.gridLayout.addWidget(self.setting_group, 0, 0, 1, 1)

        self.gridLayout.addWidget(self.workspace_card_widget, 1, 0, 1, 1)


        self.setLayout(self.gridLayout)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    window = MakeDataWidget()
    window.resize( 800,600)
    window.show()
    sys.exit(app.exec_())