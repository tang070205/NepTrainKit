#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/10/17 13:03
# @Author  : 兵
# @email    : 1747193328@qq.com
import time
from abc import abstractmethod

import numpy as np
from PySide6.QtCore import Signal
from pyqtgraph import GraphicsLayoutWidget, mkPen, ScatterPlotItem, PlotItem

from NepTrainKit.core.types import Brushes, Pens


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






class PlotBase:



    def __init__(self):
        self.current_plot=self

    @abstractmethod
    def select(self,*args,**kwargs):
        raise NotImplementedError
    @abstractmethod
    def delete(self,*args,**kwargs):
        raise NotImplementedError

    def select_point_from_polygon(self,polygon_x,polygon_y):
        pass
    @staticmethod
    def is_point_in_polygon(points, polygon):
        """
        判断多个点是否在多边形内
        :param points: (N, 2) 的数组，表示 N 个点的坐标
        :param polygon: (M, 2) 的数组，表示多边形的顶点坐标
        :return: (N,) 的布尔数组，表示每个点是否在多边形内
        """
        n = len(polygon)
        inside = np.zeros(len(points), dtype=bool)

        px, py = points[:, 0], points[:, 1]
        p1x, p1y = polygon[0]

        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            mask = ((py > np.minimum(p1y, p2y)) &
                    (py <= np.maximum(p1y, p2y)) &
                    (px <= np.maximum(p1x, p2x)) &
                    (p1y != p2y))
            xinters = (py[mask] - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
            inside[mask] ^= (px[mask] <= xinters)
            p1x, p1y = p2x, p2y

        return inside



class LayoutPlotBase(PlotBase):
    def __init__(self,row=None,col=None,**kwargs):
        super().__init__()
        self.current_plot=None
        self.current_view_box=None
        self.tool_bar=None
        self.axes_list=[]
        self.width = 3
        self.height = 3
        if row is not None and col is not None:
            self.subplot(row,col)

    def subplot(self,row,col):

        self.axes_list.clear()
        self.rows=row
        self.cols=col
        self.clear()

        for r in range(5):
            plot = MyPlotItem()

            if r==0:
                self.addItem(plot,row=r, col=0,colspan=3 )
            else:

                self.addItem(plot,row=1, col=r-1  )
            plot.getViewBox().mouseDoubleClickEvent = self.on_click(plot)
            plot.getViewBox().setMouseEnabled(False, False)
            self.axes_list.append(plot)

        self.on_click(self.axes_list[0])(None)


    def set_current_plot(self,plot):

        if self.current_plot != plot:
            self.current_view_box = plot.getViewBox()
            self.current_plot=plot
            if self.tool_bar is not None:
                self.tool_bar.reset()
            return True
        return False
    def on_click(self,plot):
        """
        子图点击  放大
        :param event:
        :return:
        """


        def handler(event):
            # 清除现有布局
            self.ci.clear()

            # 将被双击的子图放在第一行
            self.addItem(plot, row=0, col=0, colspan=4 )

            self.set_current_plot(plot)

            # 将其他子图放在第二行
            other_plots = [p for p in self.axes_list if p != plot]
            for i, other_plot in enumerate(other_plots):
                self.addItem(other_plot, row=1, col=i)

            for col, factor in enumerate([3, 1]):
                self.ci.layout.setRowStretchFactor(col, factor)

        return handler

class CustomGraphicsLayoutWidget(LayoutPlotBase,GraphicsLayoutWidget):

    def __init__(self,*args,**kwargs):
        super().__init__(self )

        GraphicsLayoutWidget.__init__(self,*args,**kwargs)


