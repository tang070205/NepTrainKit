#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/10/17 13:03
# @Author  : 兵
# @email    : 1747193328@qq.com
import time
from abc import abstractmethod

import numpy as np
from PySide6.QtCore import Signal
from pyqtgraph import GraphicsLayoutWidget, mkPen, ScatterPlotItem

from core.data.nep import NepTrainResultData


class PlotBase:

    currentPlotChanged=Signal()

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

        for r in range(row):
            for c in range(col):
                plot = self.addPlot(row=r, col=c )
                plot.getViewBox().mouseDoubleClickEvent = self.on_click(plot)
                plot.getViewBox().setMouseEnabled(False, False)
                self.axes_list.append(plot)

        self.on_click(self.axes_list[0])(None)


    def set_current_plot(self,plot):

        if self.current_plot != plot:


            self.current_plot=plot
            self.currentPlotChanged.emit()
    def on_click(self,plot):
        """
        子图点击  放大
        :param event:
        :return:
        """

        def handler(event):
            width_ratios = [1 for i in range(self.cols)]
            height_ratios = [1 for i in range(self.rows)]
            axes_index = self.axes_list.index(plot)

            height_ratios[axes_index // self.cols] = self.height
            width_ratios[axes_index % self.cols] = self.width
            self.set_current_plot(plot)

            for row,factor in enumerate(width_ratios):
                self.ci.layout.setColumnStretchFactor(row, factor)

            for col, factor in enumerate(height_ratios):
                self.ci.layout.setRowStretchFactor(col, factor)

        return handler

class CustomGraphicsLayoutWidget(LayoutPlotBase,GraphicsLayoutWidget):

    def __init__(self,*args,**kwargs):
        super().__init__(self,*args,**kwargs)

        GraphicsLayoutWidget.__init__(self,*args,**kwargs)


class NepResultGraphicsLayoutWidget(CustomGraphicsLayoutWidget):

    def __init__(self):
        super().__init__()
        self.dataset=None


    def set_dataset(self,dataset):
        self.dataset:NepTrainResultData=dataset
        self.subplot(2,2)
        self.plot_all()
    def plot_all(self):

        for index,_dataset in enumerate(self.dataset.dataset):
            plot=self.axes_list[index]
            plot.clear()
            plot.setTitle(_dataset.title)
            plot.addLine(angle=45, pos=(0.5, 0.5), pen=mkPen('r', width=2))

            colors=_dataset.colors
            scatter = ScatterPlotItem(_dataset.x,_dataset.y,data=_dataset.structure_index,brush=colors, pen=None, symbol='o', size=5)

            plot.scatter=scatter
            plot.addItem(scatter)
            # sc = axes.scatter(, , marker='o', c=color)


    def delete(self):
        if self.dataset is not None:
            self.dataset.delete_selected()
            self.plot_all()

    def select(self,index):
        self.dataset.select(index)
    def select_point_from_polygon(self,polygon_xy ):
        index=self.is_point_in_polygon(np.column_stack([self.current_plot.scatter.data["x"],self.current_plot.scatter.data["y"]]),polygon_xy)
        index = np.where(index)[0]
        select_index=self.current_plot.scatter.data[index]["data"].tolist()
        self.dataset.select(select_index)
        self.update_axes_color( )

    def select_point(self,pos):
        items=self.current_plot.scatter.pointsAt(pos)
        if len(items):

            item=items[0]
            index=item.index()
            structure_index =item.data()
            if   self.dataset.is_select(structure_index):

                self.dataset.uncheck(structure_index)
            else:

                self.dataset.select(structure_index)
            self.update_axes_color( )


    def update_axes_color(self ):
        for i,plot in enumerate(self.axes_list):

            if not hasattr(plot,"scatter"):
                continue

            structure_index_set= self.dataset.select_index
            index_list = [i for i, val in enumerate(plot.scatter.data["data"]) if val in structure_index_set]

            color=self.dataset.dataset[i].colors
            color[index_list]=self.dataset.dataset[i].selected_color
            plot.scatter.setBrush(color)


