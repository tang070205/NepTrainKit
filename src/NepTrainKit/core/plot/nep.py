#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/10/20 22:22
# @Author  : 兵
# @email    : 1747193328@qq.com
import time

import numpy as np
from PySide6.QtCore import QTimer

from PySide6.QtWidgets import QHBoxLayout, QWidget, QProgressDialog
from pyqtgraph import ProgressDialog

from .toolbar import NepDisplayGraphicsToolBar

from .. import MessageManager, Config
from ..custom_widget.dialog import GetIntMessageBox, SparseMessageBox
from ..io import NepTrainResultData
from ..io.select import farthest_point_sampling
from ..structure import table_info, atomic_numbers
from ..types import Brushes, Pens
from NepTrainKit import utils


class NepResultPlotWidget(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self._parent=parent

        self.draw_mode=False
        # self.setRenderHint(QPainter.Antialiasing, False)
        self._layout = QHBoxLayout(self)
        self.setLayout(self._layout)
        canvas_type = Config.get("widget","canvas_type","pyqtgraph")
        self.last_figure_num=None
        self.swith_canvas(canvas_type)
    def swith_canvas(self,canvas_type="pyqtgraph"):
        if canvas_type == "pyqtgraph":
            from ..canvas.pyqtgraph.canvas import PyqtgraphCanvas

            self.canvas = PyqtgraphCanvas(self)
            self._layout.addWidget(self.canvas)
        elif canvas_type == "vispy":
            from ..canvas.vispy.canvas import VispyCanvas


            self.canvas = VispyCanvas(self, bgcolor='white')
            self._layout.addWidget(self.canvas.native)





    def set_tool_bar(self, tool):
        self.tool_bar: NepDisplayGraphicsToolBar = tool
        self.tool_bar.panSignal.connect(self.canvas.pan)
        self.tool_bar.resetSignal.connect(self.canvas.auto_range)
        self.tool_bar.deleteSignal.connect(self.canvas.delete)
        self.tool_bar.revokeSignal.connect(self.canvas.revoke)
        self.tool_bar.penSignal.connect(self.canvas.pen)
        self.tool_bar.exportSignal.connect(self.export_descriptor_data)
        self.tool_bar.findMaxSignal.connect(self.find_max_error_point)
        self.tool_bar.discoverySignal.connect(self.find_non_physical_structures)
        self.tool_bar.sparseSignal.connect(self.sparse_point)
        self.canvas.tool_bar=self.tool_bar
    def __find_non_physical_structures(self):
        structure_list = self.canvas.nep_result_data.structure.now_data
        group_array = self.canvas.nep_result_data.structure.group_array.now_data
        radius_coefficient_config = Config.getfloat("widget","radius_coefficient",0.7)
        unreasonable_index=[]
        for structure,index in zip(structure_list,group_array):

            distance_info=structure.get_mini_distance_info()
            for elems, bond_length in distance_info.items():
                elem0_info = table_info[str(atomic_numbers[elems[0]])]
                elem1_info = table_info[str(atomic_numbers[elems[1]])]

                # 相邻原子距离小于共价半径之和×系数就选中
                if (elem0_info["radii"] + elem1_info["radii"]) * radius_coefficient_config > bond_length * 100:
                    unreasonable_index.append(index)
                    break


            yield 1
        self.canvas.select_index(unreasonable_index,False)


    def find_non_physical_structures(self):

        if self.canvas.nep_result_data is None:
            return
        progress_diag = QProgressDialog(f"" ,"Cancel",0,self.canvas.nep_result_data.structure.num,self._parent)
        thread=utils.LoadingThread(self._parent,show_tip=False )
        progress_diag.setFixedSize(300, 100)
        progress_diag.setWindowTitle("Finding non-physical structures")
        thread.progressSignal.connect(progress_diag.setValue)
        thread.finished.connect(progress_diag.accept)
        progress_diag.canceled.connect(thread.stop_work)  # 用户取消时终止线程
        thread.start_work(self.__find_non_physical_structures)
        progress_diag.exec()

    def find_max_error_point(self):
        dataset = self.canvas.get_axes_dataset(self.canvas.current_axes)

        if dataset is None:
            return

        box= GetIntMessageBox(self._parent,"Please enter an integer N, it will find the top N structures with the largest errors")
        n = Config.getint("widget","max_error_value",10)
        box.intSpinBox.setValue(n)

        if not box.exec():
            return
        nmax= box.intSpinBox.value()
        Config.set("widget","max_error_value",nmax)
        index= (dataset.get_max_error_index(nmax))

        self.canvas.select_index(index,False)

    def sparse_point(self):
        if  self.canvas.nep_result_data is None:
            return
        box= SparseMessageBox(self._parent,"Please specify the maximum number of structures and minimum distance")
        n_samples = Config.getint("widget","sparse_num_value",10)
        distance = Config.getfloat("widget","sparse_distance_value",0.01)

        box.intSpinBox.setValue(n_samples)
        box.doubleSpinBox.setValue(distance)

        if not box.exec():
            return
        n_samples= box.intSpinBox.value()
        distance= box.doubleSpinBox.value()

        Config.set("widget","sparse_num_value",n_samples)
        Config.set("widget","sparse_distance_value",distance)

        dataset = self.canvas.nep_result_data.descriptor
        if dataset.now_data.size ==0:
            MessageManager.send_message_box("No descriptor data available","Error")
            return
        indices_to_remove = farthest_point_sampling(dataset.now_data,n_samples=n_samples,min_dist=distance)

        # 获取所有索引（从 0 到 len(arr)-1）
        all_indices = np.arange(dataset.now_data.shape[0])

        # 使用 setdiff1d 获取不在 indices_to_remove 中的索引
        remaining_indices = np.setdiff1d(all_indices, indices_to_remove)
        structures = dataset.group_array[remaining_indices]
        self.canvas.select_index(structures.tolist(),False)

    def export_descriptor_data(self):
        if self.canvas.nep_result_data is None:
            MessageManager.send_info_message("NEP data has not been loaded yet!")
            return
        path = utils.call_path_dialog(self, "Choose a file save ", "file",default_filename="export_descriptor_data.out")
        if path:
            thread = utils.LoadingThread(self, show_tip=True, title="Exporting descriptor data")
            thread.start_work(self._export_descriptor_data, path)
    def _export_descriptor_data(self,path):

        if len(self.canvas.nep_result_data.select_index) == 0:
            MessageManager.send_info_message("No data selected!")
            return
        select_index=self.canvas.nep_result_data.descriptor.convert_index(list(self.canvas.nep_result_data.select_index))
        descriptor_data = self.canvas.nep_result_data.descriptor.now_data[select_index,:]
        if hasattr(self.canvas.nep_result_data,"energy"):
            select_index = self.canvas.nep_result_data.energy.convert_index(
                list(self.canvas.nep_result_data.select_index))

            energy_data = self.canvas.nep_result_data.energy.now_data[select_index,1]
            descriptor_data = np.column_stack((descriptor_data,energy_data))

        with open(path, "w") as f:
            np.savetxt(f,descriptor_data,fmt='%.6g',delimiter='\t')

    def set_dataset(self,dataset):

        if self.last_figure_num !=len(dataset.dataset):
            self.canvas.init_axes(len(dataset.dataset))
            self.last_figure_num = len(dataset.dataset)
        self.canvas.set_nep_result_data(dataset)
        self.canvas.plot_nep_result()















