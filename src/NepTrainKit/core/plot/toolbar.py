#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/10/18 22:12
# @Author  : 兵
# @email    : 1747193328@qq.com
from enum import Enum

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon, QPen
from PySide6.QtWidgets import QToolBar
from pyqtgraph import ViewBox, PlotCurveItem

from NepTrainKit import utils


class _Mode(str, Enum):
    NONE = ""
    PAN = "pan"
    ZOOM = "zoom rect"
    PEN="pen"
    def __str__(self):
        return self.value

    @property
    def _navigate_mode(self):
        return self.name if self is not _Mode.NONE else None





class GraphicsToolBar(QToolBar):


    def __init__(self,graph_widget, parent=None):
        super().__init__(parent)
        self.graph_widget=graph_widget
        self.graph_widget.tool_bar=self
        self.graph_widget.currentPlotChanged.connect(self.reset_connect)
        self._actions={}
        self.init_actions()
        self.mode=_Mode.NONE
        if self.graph_widget.current_plot:
            self.current_plot=self.graph_widget.current_plot
            self.view_box = self.graph_widget.current_plot.getViewBox()
        else:
            self.current_plot=None
            self.view_box=None
    def init_actions(self):
        self.add_action("重置视图",QIcon(":/images/src/images/init.svg"),self.reset_view)
        pan_action=self.add_action("平移",QIcon(":/images/src/images/pan.svg"),self.pan)
        pan_action.setCheckable(True)

        pen_action=self.add_action("鼠标框选",QIcon(":/images/src/images/pen.svg"),self.pen)
        pen_action.setCheckable(True)

        revoke_action=self.add_action("撤销",QIcon(":/images/src/images/revoke.svg"),self.revoke)

        delete_action=self.add_action("删除选中",QIcon(":/images/src/images/delete.svg"),self.delete)

    def add_action(self, name,icon,callback):
        action=QAction(QIcon(icon),name,self)
        action.triggered.connect(callback)
        self._actions[name]=action
        self.addAction(action)
        action.setToolTip(name)
        return action
    def reset_connect(self):
        """
        在选中工具栏的情况下  双击进行切换 会出现问题
        这里直接判断下
        :return:
        """



        if self.view_box is not None:

            del self.view_box.mousePressEvent
            del self.view_box.mouseMoveEvent
            del self.view_box.mouseReleaseEvent
            if self.mode==_Mode.PAN:
                self.pan(False)

            elif self.mode==_Mode.PEN:
                self.pen(False)
            self.mode = _Mode.NONE
            self._update_buttons_checked()
        self.current_plot=self.graph_widget.current_plot

        self.view_box=self.current_plot.getViewBox()

        self.view_box.mousePressEvent = self._mousePressEvent
        self.view_box.mouseMoveEvent = self._mouseMoveEvent
        self.view_box.mouseReleaseEvent = self._mouseReleaseEvent

    def reset_view(self):
        """重置视图"""
        if self.view_box is None:
            return False

        self.view_box.autoRange()

    def delete(self):
        self.graph_widget.delete()

    def revoke(self):
        self.graph_widget.revoke()



    def pan(self, checked):
        """切换平移模式"""
        if self.view_box is None:
            self._update_buttons_checked()
            return False

        if checked:
            self.mode = _Mode.PAN

            self.view_box.setMouseEnabled(True, True)

            self.view_box.setMouseMode(ViewBox.PanMode)  # 启用平移模式
        else:
            self.mode = _Mode.NONE

            self.view_box.setMouseEnabled(False, False)
        self._update_buttons_checked()



    def pen(self, checked):
        if self.view_box is None:
            self._update_buttons_checked()

            return False

        if checked:
            self.mode = _Mode.PEN
            # 初始化鼠标状态和轨迹数据
            self.is_drawing = False
            self.x_data = []
            self.y_data = []

        else:
            self.mode = _Mode.NONE
        self._update_buttons_checked()
    def _update_buttons_checked(self,):

        # sync button checkstates to match active mode
        if '平移' in self._actions:
            self._actions['平移'].setChecked(self.mode.name == 'PAN')

        if '鼠标框选' in self._actions:
            self._actions['鼠标框选'].setChecked(self.mode.name == 'PEN')

    def _mousePressEvent(self, event):
        """鼠标按下时开始绘制"""
        if self.mode !=_Mode.PEN:
            return ViewBox.mousePressEvent(self.view_box,event)
        if event.button() == Qt.MouseButton.LeftButton or event.button() == Qt.MouseButton.RightButton:
            self.is_drawing = True
            self.x_data.clear()  # 清空之前的轨迹数据
            self.y_data.clear()  # 清空之前的轨迹数据
            self.curve = self.current_plot.plot([], [], pen='r')

            self.curve.setData([], [])  # 清空绘制线条，避免对角线
            # 创建一个单独的 QGraphicsItem 用于绘制鼠标轨迹
            # self.curve = PlotCurveItem(pen=QPen(Qt.red,0.05))
            # self.current_plot.addItem(self.curve)



    def on_mouse_move(self,pos):
        if self.is_drawing:

            # 将场景坐标转换为视图坐标
            mouse_point =self.view_box.mapSceneToView(pos)
            x, y = mouse_point.x(), mouse_point.y()
            # 记录轨迹数据
            self.x_data.append(x)
            self.y_data.append(y)

            # 更新绘图
            self.curve.setData(self.x_data, self.y_data)


    def _mouseMoveEvent(self, event):
        """当鼠标移动时，如果按住左键，则绘制鼠标的轨迹"""
        if self.is_drawing:
            pos = event.scenePos()
            # 将场景坐标转换为视图坐标
            mouse_point =self.view_box.mapSceneToView(pos)
            x, y = mouse_point.x(), mouse_point.y()
            # 记录轨迹数据
            self.x_data.append(x)
            self.y_data.append(y)

            # 更新绘图
            self.curve.setData(self.x_data, self.y_data)
        else:
            return ViewBox.mousePressEvent(self.view_box,event)

    def _mouseReleaseEvent(self, event):
        """鼠标松开时停止绘制，并标记轨迹内的散点"""
        if self.mode !=_Mode.PEN:
            return ViewBox.mousePressEvent(self.view_box,event)



        if event.button() == Qt.MouseButton.LeftButton  or event.button() == Qt.MouseButton.RightButton:
            self.is_drawing = False
            reverse=event.button() == Qt.MouseButton.RightButton
            self.current_plot.removeItem(self.curve)
            # 创建鼠标轨迹的多边形
            if len(self.x_data)>2:

                self.graph_widget.select_point_from_polygon(np.column_stack((self.x_data, self.y_data)),reverse)
            else:


                # 右键的话  选中单个点
                pass
                pos = event.scenePos()
                mouse_point = self.view_box.mapSceneToView(pos)

                x = mouse_point.x()
                self.graph_widget.select_point(mouse_point,reverse)
            return

