#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/12/21 12:56
# @Author  : 兵
# @email    : 1747193328@qq.com


import numpy as np
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPainter
from pyqtgraph import mkPen, ScatterPlotItem, TextItem, ViewBox,PlotDataItem


from .canvas import CustomGraphicsWidget
from .. import MessageManager, Config
from ..custom_widget.dialog import GetIntMessageBox, SparseMessageBox
from ..io import NepTrainResultData
from ..io.select import farthest_point_sampling
from ..types import Brushes, Pens
from NepTrainKit import utils


class MakeDataGraphicsWidget(CustomGraphicsWidget):
    structureIndexChanged=Signal(int)
    def __init__(self,parent=None):
        super().__init__(parent)
        self._parent=parent

