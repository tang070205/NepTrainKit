#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/12/31 20:24
# @Author  : 兵
# @email    : 1747193328@qq.com

from abc import ABC, abstractmethod

import numpy as np
from PySide6.QtCore import Signal


class CanvasBase(ABC):
    def __init__(self):
        self.current_plot = None

        self.tool_bar=None
    @abstractmethod
    def pan(self ):
        """
        平移画布
        """
        pass


    def pen(self,*args,**kwargs):
        pass

    @abstractmethod
    def auto_range(self):
        """
        实现对坐标轴的区间自动适应
        """
        pass
    @abstractmethod
    def select(self,*args,**kwargs):
        pass
    @abstractmethod
    def delete(self,*args,**kwargs):
        pass



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

class CanvasLayoutBase(CanvasBase):
    CurrentAxesChanged=Signal()
    def __init__(self):
        super().__init__()
        self.axes_list=[]
        self.CurrentAxesChanged.connect(self.set_view_layout)
    @abstractmethod
    def set_view_layout(self):

        """
        设置子图的排布
        """
        pass

    @abstractmethod

    def init_axes(self):
        """
        初始化子图对象
        """
        pass
    def set_current_plot(self,plot):

        if self.current_plot != plot:

            self.current_plot=plot
            if self.tool_bar is not None:
                self.tool_bar.reset()
            self.CurrentAxesChanged.emit()
            return True
        return False

    def clear(self):
        """
        清空逻辑
        """
        self.axes_list.clear()