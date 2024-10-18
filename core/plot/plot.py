#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/10/17 21:44
# @Author  : 兵
# @email    : 1747193328@qq.com
from typing import List

import numpy as np
from matplotlib.collections import PathCollection

from core.data import NepTrainResultData



class NepPlotBase:
    pass
    """
    实现什么效果
        1.绑定框选函数
        2.支持选中变色
        3.delete键删除
         
    """

    def __init__(self,figure,axes_list,dataset):
        self.figure = figure
        self.axes_list = axes_list
        self.pick_cid = self.figure.canvas.mpl_connect('pick_event', self.on_pick)

        self.scatter_list:List[PathCollection]=[None for i in range(len(self.axes_list))]
        self.dataset:NepTrainResultData=dataset
        # 绑定鼠标点击事件
        self.figure.canvas.mpl_connect('pick_event', self.on_pick)
        self.figure.canvas.mpl_connect('key_press_event', self.on_key_press)







    def on_pick(self, event):

        """处理点击事件，通过 pick_event 获取点击的散点"""

        if event.mouseevent.name=="button_press_event":
            #直接点击的

            self.set_color(event.ind,True)
        else:
            self.set_color(event.ind,False)
        self.update_scatter()
    def set_color(self,ind,reverse):
        self.dataset.energy.set_colors(ind,"red",reverse)

        self.dataset.force.set_colors(ind,"red",reverse)
        self.dataset.stress.set_colors(ind,"red",reverse)
        self.dataset.virial.set_colors(ind,"red",reverse)



    def on_key_press(self, event):

        if event.key=="delete":
            #删除选中的点
            pass
            for dataset in self.dataset.dataset:

                dataset.remove_selected()
            self.plot()


        # 重新绘制图表
        self.update_scatter()
    def update_scatter(self):

        for i,dataset in enumerate(self.dataset.dataset):
            if self.scatter_list[i] is not None:
                self.scatter_list[i].set_color(dataset.colors)
        self.figure.canvas.axes.draw_artist(self.scatter_list[0])  # 再绘制线条

                # 只更新该子图区域
        self.figure.canvas.blit(self.figure.canvas.axes.bbox)
        # self.figure.canvas.draw_idle()

    def __del__(self):
        self.figure.canvas.mpl_disconnect(self.pick_cid)

    def plot(self):
        for i in self.scatter_list:
            if i is not None:
                i.remove()


        # 绘制函数
        for i,axes in enumerate(self.axes_list):

            self.scatter_list[i] = self.plot_axes_by_dataset(self.axes_list[i],self.dataset.dataset[i])

        self.figure.canvas.draw_idle()
    def plot_axes_by_dataset(self,axes,dataset):

        index = dataset.now_data.shape[1] // 2
        axes.set_title(dataset.title)
        color=np.tile(dataset.colors, index)
        sc = axes.scatter(dataset.now_data[:, index:], dataset.now_data[:, :index],marker='o',c=color)
        return sc