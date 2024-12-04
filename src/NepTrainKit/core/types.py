#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/12/2 20:02
# @Author  : 兵
# @email    : 1747193328@qq.com
from PySide6.QtGui import QBrush, QColor


class Brushes:
    # 基本颜色刷子
    RedBrush = QBrush(QColor(255, 0, 0))  # 红色
    GreenBrush = QBrush(QColor(0, 255, 0))  # 绿色
    BlueBrush = QBrush(QColor(0, 0, 255))  # 蓝色
    YellowBrush = QBrush(QColor(255, 255, 0))  # 黄色
    TransparentBrush = QBrush(QColor(0, 0, 0,0))  # 黄色
