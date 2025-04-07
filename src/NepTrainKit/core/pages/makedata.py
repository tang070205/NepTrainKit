#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/12/20 17:18
# @Author  : 兵
# @email    : 1747193328@qq.com
from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QGridLayout, QApplication
from qfluentwidgets import CommandBar

from NepTrainKit.core import MessageManager
from NepTrainKit.core.custom_widget import MakeWorkflowArea, CardGroup
from NepTrainKit.core.io.base import StructureData
from NepTrainKit.core.structure import Structure
from NepTrainKit.core.views.cards import *





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
        self.dataset=None

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
        structures_list = []

        if path.is_file():
            # 读取文件
            structures=Structure.read_multiple(path)
            structures_list.extend(structures)

        else:
            for file in path.iterdir():
                if file.is_file():
                    # 读取文件
                    if file.suffix==".xyz":
                        structures=Structure.read_multiple(file)
                        structures_list.extend(structures)

        self.dataset=structures_list

    def init_ui(self):

        self.gridLayout = QGridLayout(self)
        self.gridLayout.setObjectName("make_data_gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.workspace_card_widget = MakeWorkflowArea(self)
        self.setting_group=ConsoleWidget(self)
        self.setting_group.runSignal.connect(self.run_card)
        self.setting_group.stopSignal.connect(self.stop_run_card)
        self.setting_group.newCardSignal.connect(self.add_card)
        self.gridLayout.addWidget(self.setting_group, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.workspace_card_widget, 1, 0, 1, 1)
        self.setLayout(self.gridLayout)

    def open_file(self):
        path = utils.call_path_dialog(self,"Please choose the structure files",
                                      "select",file_filter="XYZ Files (*.xyz)")
        if path:
            self.load_base_structure(path)
    def _export_file(self,path):
        with open(path, "w") as file:
            for card in self.workspace_card_widget.cards:
                if card.check_state:

                    card.write_result_dataset(file)

    def export_file(self):


        path = utils.call_path_dialog(self, "Choose a file save location", "file",default_filename="make_dataset.xyz")
        if path:
            thread = utils.LoadingThread(self, show_tip=True, title="Exporting data")
            thread.start_work(self._export_file, path)
    def run_card(self):
        if not  self.dataset  :
            MessageManager.send_info_message("Please import the structure file first. You can drag it in directly or import it from the upper left corner!")
        first_card=self.workspace_card_widget.cards[0]
        first_card.dataset = self.dataset
        first_card.index=0
        first_card.runFinishedSignal.connect(self._run_next_card)
        first_card.run()


    def _run_next_card(self,current_card_index):

        cards=self.workspace_card_widget.cards
        current_card=cards[current_card_index]
        current_card.runFinishedSignal.disconnect(self._run_next_card)
        if current_card_index+1<len(cards):
            next_card=cards[current_card_index+1]
            if current_card.result_dataset:
                next_card.set_dataset(current_card.result_dataset)
                next_card.index=current_card_index+1
                next_card.runFinishedSignal.connect(self._run_next_card)
                next_card.run()
        else:
            MessageManager.send_success_message("Perturbation training set created successfully.")
    def stop_run_card(self):
        for card in self.workspace_card_widget.cards:
            card.stop()
    def add_card(self,card_name):
        if card_name =="Card Group":
            card=CardGroup()
        else:
            card=SuperCellCard()

        self.workspace_card_widget.add_card(card)
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    window = MakeDataWidget()
    window.resize( 800,600)
    window.show()
    sys.exit(app.exec_())