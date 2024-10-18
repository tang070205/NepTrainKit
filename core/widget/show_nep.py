#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/10/17 13:38
# @Author  : 兵
# @email    : 1747193328@qq.com
import os.path

import numpy as np
from PySide6.QtCore import QUrl, Qt
from PySide6.QtWidgets import QWidget,QGridLayout
from qfluentwidgets import HyperlinkLabel, MessageBox
import utils
from core import MessageManager
from core.plot.canvas import init_canvas
from core.plot.plot import NepPlotBase
from core.plot.subplot import SubplotSwitcher

from core.data import NepTrainResultData



class ClickableScatterPlot:
    def __init__(self,fig,axes):
        # 创建随机散点
        self.ax=axes
        self.fig=fig
        self.x = np.random.rand(1000)
        self.y = np.random.rand(1000)
        self.colors = np.full(1000, 'blue')  # 初始颜色为蓝色

        # 绘制初始散点图，并设置 pickradius
        self.scatter = self.ax.scatter(self.x, self.y, c=self.colors, picker=True, pickradius=1)

        # 绑定鼠标点击事件
        self.fig.canvas.mpl_connect('pick_event', self.on_pick)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
    def on_pick(self, event):

        """处理点击事件，通过 pick_event 获取点击的散点"""

        if event.mouseevent.name=="button_press_event":
            #直接点击的
            self.set_color(event.ind,True)
        else:
            self.set_color(event.ind,False)

    def on_key_press(self, event):
        print(event.name)

        print(event.x,event.y,event.key)

    def set_color(self,index_list,reverse=True):
        if reverse:
            # 通过索引列表创建一个布尔数组，用于索引原数组
            change_mask = np.zeros(len(self.colors), dtype=bool)
            change_mask[index_list] = True
            self.colors[change_mask] = np.where(self.colors[change_mask] == 'blue', 'red', 'blue')
        else:
            self.colors[index_list] = 'red'
        # 更新散点颜色
        self.scatter.set_color(self.colors)
        # 重新绘制图表
        self.fig.canvas.draw_idle()

class ShowNepWidget(QWidget):
    """
    针对NEP训练过程中 对预测结果的展示
    实现以下功能
        1.支持交互筛选训练集
        2.拖拽实现目录导入
        3.对于选定的结构 进行展示
    """
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setObjectName("ShowNepWidget")
        self.setAcceptDrops(True)
        self.init_ui()

    def init_ui(self):
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setObjectName("show_nep_gridLayout")
        self.gridLayout.setContentsMargins(0,0,0,0)
        self.plot_widget = QWidget(self)
        self.show_struct_widget = QWidget(self)
        self.Canvas = init_canvas(self.plot_widget)
        self.plot_switcher = SubplotSwitcher(self.Canvas)

        self.gridLayout.addWidget(self.plot_widget, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.show_struct_widget, 0, 1, 1, 1)


        # 创建状态栏
        self.path_label = HyperlinkLabel(  self)
        self.path_label.setFixedHeight(30)  # 设置状态栏的高度

        # 将状态栏添加到布局的底部
        self.gridLayout.addWidget(self.path_label, 1, 0, 1, 2)
        self.gridLayout.setColumnStretch(0, 2)
        self.gridLayout.setColumnStretch(1, 1)

    def dragEnterEvent(self, event):
        # 检查拖拽的内容是否包含文件
        if event.mimeData().hasUrls():
            event.acceptProposedAction()  # 接受拖拽事件
        else:
            event.ignore()  # 忽略其他类型的拖拽

    def dropEvent(self, event):
        # 获取拖拽的文件路径
        urls = event.mimeData().urls()
        if urls:
            # 获取第一个文件路径
            file_path = urls[0].toLocalFile()

            self.set_work_path(file_path)


    def open_file(self):
        path = utils.call_path_dialog(self,"请选择工作路径","directory")
        if path:
            self.set_work_path(path)
    def set_work_path(self,path):

        if os.path.isfile(path):
            path = os.path.dirname(path)
        url=self.path_label.getUrl().toString()

        if os.path.exists(url.replace("file:///","")):
            box=MessageBox("询问","检测到已有工作目录，加载新的目录将清空之前的结果\n请问是否要载入新的工作路径？",self)
            box.exec_()
            if box.result()==0:
                return

        self.path_label.setText(f"当前工作路径：{path}")
        self.path_label.setUrl(QUrl.fromLocalFile(path))
        #设置工作路径后 开始画图了
        self.check_nep_result(path)
    def check_nep_result(self,path):
        """
        检查输出文件都有什么
        然后设置窗口布局
        :return:
        """

        self.plot_switcher.subplot(1,1)

        train_data=NepTrainResultData.from_path(path)
        if train_data is None:
            # MessageManager.send_error_message(f"当前目录下并没有训练集xyz文件：")
            return
        self.nep_plot = NepPlotBase(self.Canvas.figure,self.plot_switcher.axes_list,train_data)
        self.nep_plot.plot()
        # self.Canvas.mpl_disconnect()