#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/10/20 22:22
# @Author  : 兵
# @email    : 1747193328@qq.com

import numpy as np
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QHBoxLayout,QWidget
from pyqtgraph import mkPen, ScatterPlotItem, TextItem, ViewBox,PlotDataItem


from .toolbar import NepDisplayGraphicsToolBar
from ..canvas.pyqtgraph.canvas  import PyqtgraphCanvas
from ..canvas.vispy.canvas import VispyCanvas
from .. import MessageManager, Config
from ..custom_widget.dialog import GetIntMessageBox, SparseMessageBox
from ..io import NepTrainResultData
from ..io.select import farthest_point_sampling
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

        self.swith_canvas(canvas_type)
    def swith_canvas(self,canvas_type="pyqtgraph"):

        if canvas_type == "pyqtgraph":
            self.canvas = PyqtgraphCanvas(self)
            self._layout.addWidget(self.canvas)
        elif canvas_type == "vispy":
            self.canvas = VispyCanvas(self, bgcolor='white')
            self._layout.addWidget(self.canvas.native)

        title=["energy","force","stress","virial", "descriptor"]
        self.canvas.init_axes(5,title)

    def set_tool_bar(self, tool):
        self.tool_bar: NepDisplayGraphicsToolBar = tool
        self.tool_bar.panSignal.connect(self.canvas.pan)
        self.tool_bar.resetSignal.connect(self.canvas.auto_range)
        self.tool_bar.deleteSignal.connect(self.canvas.delete)
        self.tool_bar.revokeSignal.connect(self.canvas.revoke)
        self.tool_bar.penSignal.connect(self.canvas.pen)

        self.tool_bar.findMaxSignal.connect(self.find_max_error_point)
        self.tool_bar.sparseSignal.connect(self.sparse_point)
        self.canvas.tool_bar=self.tool_bar


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
        indices_to_remove = farthest_point_sampling(dataset.now_data,n_samples=n_samples,min_dist=distance)

        # 获取所有索引（从 0 到 len(arr)-1）
        all_indices = np.arange(dataset.now_data.shape[0])

        # 使用 setdiff1d 获取不在 indices_to_remove 中的索引
        remaining_indices = np.setdiff1d(all_indices, indices_to_remove)
        structures = dataset.group_array[remaining_indices]
        self.canvas.select_index(structures.tolist(),False)
    def set_dataset(self,dataset):

        self.canvas.set_nep_result_data(dataset)
        self.canvas.plot_nep_result()















