#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/10/17 13:38
# @Author  : 兵
# @email    : 1747193328@qq.com
import os.path
import sys
import threading
import time
from io import StringIO

import numpy as np
from PySide6.QtCore import QUrl, QThread, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QSizePolicy

from qfluentwidgets import HyperlinkLabel, MessageBox, SubtitleLabel, PlainTextEdit, CaptionLabel, SpinBox, \
    TransparentToolButton

from NepTrainKit import utils
from NepTrainKit.core import MessageManager
from NepTrainKit.core.custom_widget.search_widget import   ConfigTypeSearchLineEdit
from NepTrainKit.core.io import NepTrainResultData


from NepTrainKit.core.plot import NepResultPlotWidget,NepDisplayGraphicsToolBar,StructurePlotWidget
from NepTrainKit.core.types import Brushes


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
        self._parent = parent
        self.setObjectName("ShowNepWidget")
        self.setAcceptDrops(True)
        self.nep_result_data=None
        self.init_ui()

    def init_ui(self):
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setObjectName("show_nep_gridLayout")
        self.gridLayout.setContentsMargins(0,0,0,0)

        self.struct_widget = QWidget(self)
        self.struct_widget_layout = QGridLayout(self.struct_widget)

        self.show_struct_widget = StructurePlotWidget(self.struct_widget)

        self.struct_info_edit = PlainTextEdit(self.struct_widget)
        self.struct_info_edit.setReadOnly(True)

        self.struct_index_widget = QWidget(self)
        self.struct_index_widget_layout = QHBoxLayout(self.struct_index_widget)
        self.struct_index_label = CaptionLabel(self.struct_index_widget)
        self.struct_index_label.setText("Current structure (original file index):")

        self.struct_index_spinbox = SpinBox(self.struct_index_widget)

        self.struct_index_spinbox.upButton.clicked.disconnect(self.struct_index_spinbox.stepUp)
        self.struct_index_spinbox.downButton.clicked.disconnect(self.struct_index_spinbox.stepDown)
        self.struct_index_spinbox.downButton.clicked.connect(self.to_last_structure)
        self.struct_index_spinbox.upButton.clicked.connect(self.to_next_structure)
        self.struct_index_spinbox.setMinimum(0)
        self.struct_index_spinbox.setMaximum(0)

        self.play_timer=QTimer(self)
        self.play_timer.timeout.connect(self.play_show_structures)

        self.auto_switch_button = TransparentToolButton(QIcon(':/images/src/images/play.svg') ,self.struct_index_widget)
        self.auto_switch_button.clicked.connect(self.start_play)
        self.auto_switch_button.setCheckable(True)


        self.struct_index_widget_layout.addWidget(self.struct_index_label)
        self.struct_index_widget_layout.addWidget(self.struct_index_spinbox)

        self.struct_index_widget_layout.addWidget(self.auto_switch_button)
        self.struct_index_spinbox.valueChanged.connect(self.show_current_structure)

        self.struct_widget_layout.addWidget(self.show_struct_widget, 0, 0, 1, 1)
        self.struct_widget_layout.addWidget(self.struct_info_edit, 1, 0, 1, 1)
        self.struct_widget_layout.addWidget(self.struct_index_widget, 2, 0, 1, 1)

        self.struct_widget_layout.setRowStretch(0, 3)
        self.struct_widget_layout.setRowStretch(1, 1)
        self.struct_widget_layout.setRowStretch(2, 0)

        self.struct_widget_layout.setContentsMargins(0, 0, 0, 0)

        self.plot_widget = QWidget(self)

        self.plot_widget_layout = QGridLayout(self.plot_widget)

        self.graph_widget = NepResultPlotWidget(self  )

        self.graph_widget.canvas.structureIndexChanged.connect(self.struct_index_spinbox.setValue)

        self.graph_toolbar = NepDisplayGraphicsToolBar(  self.plot_widget)
        self.graph_widget.set_tool_bar(self.graph_toolbar)

        self.search_lineEdit=ConfigTypeSearchLineEdit(self.plot_widget)
        self.search_lineEdit.searchSignal.connect(self.search_config_type)
        self.search_lineEdit.checkSignal.connect(self.checked_config_type)
        self.search_lineEdit.uncheckSignal.connect(self.uncheck_config_type)



        self.plot_widget_layout.addWidget(self.graph_toolbar)

        self.plot_widget_layout.addWidget(self.search_lineEdit)
        self.plot_widget_layout.addWidget(self.graph_widget)
        self.plot_widget_layout.setContentsMargins(0,0,0,0)





        self.gridLayout.addWidget(self.plot_widget, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.struct_widget, 0, 1, 1, 1)

        # 创建状态栏
        self.path_label = HyperlinkLabel(  self)
        self.path_label.setFixedHeight(30)  # 设置状态栏的高度

        # 将状态栏添加到布局的底部
        self.gridLayout.addWidget(self.path_label, 1, 0, 1, 1)
        # self.gridLayout.setHorizontalSpacing( 0)

        self.gridLayout.setColumnStretch(0, 3)
        self.gridLayout.setColumnStretch(1, 3)

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
        path = utils.call_path_dialog(self,"Please choose the working directory","directory")
        if path:
            self.set_work_path(path)

    def export_file(self):
        if self.nep_result_data is None:
            MessageManager.send_info_message("NEP data has not been loaded yet!")
            return
        path=utils.call_path_dialog(self,"Choose a file save location","directory")
        if path:
            thread=utils.LoadingThread(self,show_tip=True,title="Exporting data")
            thread.start_work(self.nep_result_data.export_model_xyz, path)



    def set_work_path(self,path):

        if os.path.isfile(path):
            path = os.path.dirname(path)
        url=self.path_label.getUrl().toString()

        old_path=url.replace("file://","")
        if sys.platform == "win32":
            old_path=old_path[1:]
        else:
            pass
        if os.path.exists(old_path):
            box=MessageBox("Ask","A working directory already exists. Loading a new directory will erase the previous results.\nDo you want to load the new working path?",self)
            box.exec_()
            if box.result()==0:
                return




        #设置工作路径后 开始画图了


        self.load_thread=utils.LoadingThread(self,show_tip=True,title="Loading NEP data")
        self.load_thread.finished.connect(self.set_dataset)

        self.load_thread.start_work(self.check_nep_result,path)

        # self.check_nep_result(path)
    def set_dataset(self):
        if self.nep_result_data is None:
            return
        self.struct_index_spinbox.setMaximum(self.nep_result_data.num)

        self.graph_widget.set_dataset(self.nep_result_data)
        self.search_lineEdit.setCompleterKeyWord(self.nep_result_data.structure.get_all_config())
        self.struct_index_spinbox.valueChanged.emit(0)

    def check_nep_result(self,path):
        """
        检查输出文件都有什么
        然后设置窗口布局
        :return:
        """
        self.nep_result_data = NepTrainResultData.from_path(path)
        if self.nep_result_data is None:
            return

        self.path_label.setText(f"Current working directory: {path}")
        self.path_label.setUrl(QUrl.fromLocalFile(path))
        # self.graph_widget.set_dataset(self.dataset)

    def to_last_structure(self):
        if self.nep_result_data is None:
            return None
        current_index = self.struct_index_spinbox.value()
        sort_index = np.sort(self.nep_result_data.structure.group_array.now_data, axis=0)
        index = np.searchsorted(sort_index, current_index, side='left')

        self.struct_index_spinbox.setValue(int(sort_index[index-1 if index>0 else index]))
    # @utils.timeit
    def to_next_structure(self):
        if self.nep_result_data is None:
            return None
        current_index=self.struct_index_spinbox.value()
        sort_index= np.sort(self.nep_result_data.structure.group_array.now_data,axis=0)
        index = np.searchsorted(sort_index, current_index, side='right')
        if index>=sort_index.shape[0]:
            return False
        self.struct_index_spinbox.setValue(int(sort_index[index]))

        if index==sort_index.shape[0]-1:

            return True
        else:

            return False
    def start_play(self):
        if self.auto_switch_button.isChecked():
            self.auto_switch_button.setIcon(QIcon(':/images/src/images/pause.svg'))
            self.play_timer.start(50)
        else:
            self.auto_switch_button.setIcon(QIcon(':/images/src/images/play.svg'))
            self.play_timer.stop()
    def play_show_structures(self):
        if   self.to_next_structure():

            self.auto_switch_button.click()
    # @utils.timeit
    def show_current_structure(self,current_index):

        try:
            atoms=self.nep_result_data.get_atoms(current_index)
        except:
            MessageManager.send_message_box("The index is invalid, perhaps the structure has been deleted")
            return

        self.graph_widget.canvas.plot_current_point(current_index)

        self.show_struct_widget.show_atoms(atoms)

        text_io=StringIO()
        atoms.write(text_io)

        text_io.seek(0)
        # comm=text.readlines()[1]
        comm=text_io.read()
        self.struct_info_edit.setPlainText(comm)
        text_io.close()


    def search_config_type(self,config):

        indexs= self.nep_result_data.structure.search_config(config)

        self.graph_widget.canvas.update_scatter_color(indexs,Brushes.Show)


    def checked_config_type(self, config):

        indexs = self.nep_result_data.structure.search_config(config)

        self.graph_widget.canvas.select_index(indexs,  False)

    def uncheck_config_type(self, config):

        indexs = self.nep_result_data.structure.search_config(config)

        self.graph_widget.canvas.select_index(indexs,True )