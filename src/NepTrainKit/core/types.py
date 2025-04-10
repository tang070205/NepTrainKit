#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/12/2 20:02
# @Author  : 兵
# @email    : 1747193328@qq.com
from enum import Enum

from PySide6.QtGui import QBrush, QColor
from pyqtgraph import mkPen


class ForcesMode(Enum):
    Raw="Raw"
    Norm="Norm"

class CanvasMode(Enum):
    vispy="vispy"
    pyqtgraph="pyqtgraph"



class Base:

    @classmethod
    def get(cls,name):
        if hasattr(cls, name):
            return getattr(cls, name)
        else:
            return getattr(cls,"Default")





class Pens(Base):
    Default=mkPen(color="blue", width=0.5)
    Energy = Default
    Force = Default
    Virial = Default
    Stress = Default
    Descriptor = Default
    Current=mkPen(color="red", width=1)
    def __getattr__(self, item):
        return getattr(self.Default, item)

class Brushes(Base):
    # 基本颜色刷子



    BlueBrush = QBrush(QColor(0, 0, 255))   # 蓝色
    YellowBrush = QBrush(QColor(255, 255, 0))  # 黄色
    Default = QBrush(QColor(255, 255, 255,0))  # 黄色
    Energy = Default
    Force =Default
    Virial =Default
    Stress = Default
    Descriptor = Default
    Show=QBrush(QColor(0, 255, 0))  # 绿色
    Selected=QBrush(QColor(255, 0, 0))
    Current=QBrush(QColor(255, 0,0 ))
    def __getattr__(self, item):
        return getattr(self.Default, item)