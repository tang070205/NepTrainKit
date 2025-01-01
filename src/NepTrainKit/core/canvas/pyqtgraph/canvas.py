#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/10/17 13:03
# @Author  : 兵
# @email    : 1747193328@qq.com
import time
from abc import abstractmethod

import numpy as np
from PySide6.QtCore import Signal
from pyqtgraph import GraphicsLayoutWidget, mkPen, ScatterPlotItem, PlotItem,GraphicsView
from ..base.canvas import CanvasBase,CanvasLayoutBase
from NepTrainKit.core.types import Brushes, Pens

from functools import partial
class MyPlotItem(PlotItem):
    pass
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._scatter=None
        self.current_point=ScatterPlotItem()
        self.current_point.setZValue(100)
    def add_scatter(self, scatter:ScatterPlotItem, **kwargs):
        self._scatter=scatter
        self.addItem(scatter,**kwargs)

    def set_current_point(self, x,y):

        self.current_point.setData( x, y,brush=Brushes.Current ,pen=Pens.Current,
                                      symbol='star',size=15 )
        if self.current_point not in self.items:

            self.addItem(self.current_point)



class PyqtgraphCanvas(CanvasLayoutBase,GraphicsLayoutWidget):
    def __init__(self,*args, **kwargs):
        super().__init__()
        GraphicsLayoutWidget.__init__(self,*args,**kwargs)



    def init_axes(self ):
        self.clear()
        for r in range(5):
            plot = MyPlotItem()
            self.addItem(plot  )
            plot.getViewBox().mouseDoubleClickEvent = partial(self.set_current_plot,plot=plot)
            plot.getViewBox().setMouseEnabled(False, False)
            self.axes_list.append(plot)
    def set_view_layout(self):
        if len(self.axes_list)==0:
            return
        if self.current_plot not in self.axes_list:
            self.set_current_plot(self.axes_list[0])
            return

        self.ci.clear()
        self.addItem(self.current_plot, row=0, col=0, colspan=4)

        # 将其他子图放在第二行
        other_plots = [p for p in self.axes_list if p != self.current_plot]
        for i, other_plot in enumerate(other_plots):
            self.addItem(other_plot, row=1, col=i)

        for col, factor in enumerate([3, 1]):
            self.ci.layout.setRowStretchFactor(col, factor)






    def auto_range(self,plot=None):
        if plot is None:
            plot=self.current_plot
        if plot:

            view = plot.getViewBox()

            x_range=[10000,-10000]
            y_range=[10000,-10000]
            for item in view.addedItems:
                if isinstance(item, ScatterPlotItem):

                    x=item.data["x"]
                    y=item.data["y"]

                    x=x[x>-10000]
                    y=y[y>-10000]
                    if x.size==0:
                        x_range=[0,1]
                        y_range=[0,1]
                        continue
                    x_min = np.min(x )
                    x_max = np.max(x )
                    y_min = np.min(y )
                    y_max = np.max(y )
                    if x_min < x_range[0]:
                        x_range[0]=x_min
                    if x_max > x_range[1]:
                        x_range[1]=x_max
                    if y_min <y_range[0]:
                        y_range[0]=y_min
                    if y_max > y_range[1]:
                        y_range[1]=y_max

            view.setRange(xRange=x_range,yRange=y_range)

    def pan(self, checked):

        if self.current_plot:

            self.current_plot.setMouseEnabled(checked, checked)
            self.current_plot.getViewBox().setMouseMode(ViewBox.PanMode)
    def pen(self, checked):
        if self.current_plot is None:

            return False

        if checked:
            self.draw_mode=True
            # 初始化鼠标状态和轨迹数据
            self.is_drawing = False
            self.x_data = []
            self.y_data = []

        else:
            self.draw_mode=False
            pass