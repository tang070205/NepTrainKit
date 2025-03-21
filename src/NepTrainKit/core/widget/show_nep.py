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
from venv import logger

import numpy as np
from PySide6.QtCore import QUrl, QThread, QTimer
from PySide6.QtGui import QIcon, QFont
from PySide6.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QSizePolicy

from qfluentwidgets import HyperlinkLabel, MessageBox, SubtitleLabel, PlainTextEdit, CaptionLabel, SpinBox, \
    TransparentToolButton, StrongBodyLabel, getFont, ToolTipFilter, ToolTipPosition

from NepTrainKit import utils
from NepTrainKit.core import MessageManager, Config
from NepTrainKit.core.custom_widget.search_widget import   ConfigTypeSearchLineEdit
from NepTrainKit.core.io import NepTrainResultData
from NepTrainKit.core.io.nep import NepPolarizabilityResultData, NepDipoleResultData
from NepTrainKit.core.io.utils import get_nep_type

from NepTrainKit.core.plot import NepResultPlotWidget,NepDisplayGraphicsToolBar,StructurePlotWidget
from NepTrainKit.core.types import Brushes
from NepTrainKit.core.structure import table_info, atomic_numbers


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
        self.first_show=False
    def showEvent(self, event):
        auto_load_config = Config.getboolean("widget","auto_load",False)
        if not auto_load_config:
            return

        if not self.first_show:
            self.first_show=True
            if os.path.exists("./train.xyz") and os.path.exists("./nep.txt"):
                self.set_work_path(os.getcwd())

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

        self.bond_label=StrongBodyLabel(self)
        self.bond_label.setFont(getFont(20, QFont.DemiBold))
        # self.bond_label.setFixedHeight(30)  # 设置状态栏的高度
        self.bond_label.setWordWrap(True)
        # 添加到布局的底部
        self.gridLayout.addWidget(self.bond_label, 1, 1, 1, 1)
        # self.bond_label.setStyleSheet("QLabel { background-color: #f3f3f3; color: black; padding: 5px; }")
        self.bond_label.setToolTip('The Tip is the minimum distance between atoms in the current structure, in Å.')

        self.bond_label.installEventFilter(ToolTipFilter(self.bond_label, 300, ToolTipPosition.TOP))

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

        model_type=get_nep_type(os.path.join(path,"nep.txt"))
        logger.info(f"NEP model type: {model_type}")
        if model_type==0:
            self.nep_result_data=NepTrainResultData.from_path(path)
        elif model_type==1:
            self.nep_result_data=NepDipoleResultData.from_path(path)
        elif model_type==2:
            self.nep_result_data=NepPolarizabilityResultData.from_path(path)
        else:
            self.nep_result_data=None

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

        self.show_struct_widget.show_structure(atoms)
        self.update_structure_bond_info(atoms)
        text_io=StringIO()
        atoms.write(text_io)

        text_io.seek(0)
        # comm=text.readlines()[1]
        comm=text_io.read()
        self.struct_info_edit.setPlainText(comm)
        text_io.close()
    def update_structure_bond_info(self,atoms):
        distance_info = atoms.get_mini_distance_info()
        bond_text = ""
        radius_coefficient_config = Config.getfloat("widget","radius_coefficient",0.7)
        unreasonable = False
        for elems,bond_length in distance_info.items():
            elem0_info = table_info[str(atomic_numbers[elems[0]])]
            elem1_info = table_info[str(atomic_numbers[elems[1]])]
            bond_text += f"{elems[0]}-{elems[1]}:"
            #相邻原子距离小于共价半径之和×系数就标红
            if (elem0_info["radii"] + elem1_info["radii"]) * radius_coefficient_config > bond_length*100:
                bond_text += f'<font color="red">{bond_length:.2f}</font> Å | '
                unreasonable = True
            else:
                bond_text+=f'<font color="green">{bond_length:.2f}</font> Å | '
        self.bond_label.setText(bond_text )
        if unreasonable:
            MessageManager.send_info_message("The distance between atoms is too small, and the structure may be unreasonable.")
    def search_config_type(self,config):

        indexs= self.nep_result_data.structure.search_config(config)

        self.graph_widget.canvas.update_scatter_color(indexs,Brushes.Show)


    def checked_config_type(self, config):

        indexs = self.nep_result_data.structure.search_config(config)

        self.graph_widget.canvas.select_index(indexs,  False)

    def uncheck_config_type(self, config):

        indexs = self.nep_result_data.structure.search_config(config)

        self.graph_widget.canvas.select_index(indexs,True )