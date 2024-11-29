#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/10/20 22:22
# @Author  : 兵
# @email    : 1747193328@qq.com
import time

import numpy as np
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGraphicsItem
from pyqtgraph import mkPen, ScatterPlotItem, PlotDataItem


from .canvas import CustomGraphicsLayoutWidget
from .. import MessageManager
from ..io import NepTrainResultData


class NepResultGraphicsLayoutWidget(CustomGraphicsLayoutWidget):
    structureIndexChanged=Signal(int)
    def __init__(self,parent=None):
        super().__init__(parent)
        self._parent=parent
        self.dataset=None


    def set_dataset(self,dataset):
        self.dataset:NepTrainResultData=dataset
        self.subplot(2,3)
        self.plot_all()

    def get_current_dataset(self):
        if self.current_plot is None:
            return None
        plot_index = self.axes_list.index(self.current_plot)
        return self.dataset.dataset[plot_index]

    def plot_all(self):
        self.dataset.select_index.clear()
        _pen = mkPen(None)

        for index,_dataset in enumerate(self.dataset.dataset):
            plot=self.axes_list[index]
            plot.clear()
            plot.setTitle(_dataset.title)
            if _dataset.title not in ["descriptor"]:

                plot.addLine(angle=45, pos=(0.5, 0.5), pen=mkPen('r', width=2))
            scatter = ScatterPlotItem(_dataset.x,_dataset.y,data=_dataset.structure_index,
                                      brush=_dataset.normal_color, pen=None, symbol='o',
                                     )


            scatter.sigClicked.connect(self.item_clicked)
            plot.scatter=scatter
            plot.addItem(scatter)
            # plot.autoRange()

    def item_clicked(self,scatter_item,items,event):

        if items.any():
            item=items[0]

            self.structureIndexChanged.emit(item.data())

    def delete(self):
        if self.dataset is not None and self.dataset.select_index:

            self.dataset.delete_selected()
            self.plot_all()


    def select_point_from_polygon(self,polygon_xy,reverse ):
        index=self.is_point_in_polygon(np.column_stack([self.current_plot.scatter.data["x"],self.current_plot.scatter.data["y"]]),polygon_xy)
        index = np.where(index)[0]
        select_index=self.current_plot.scatter.data[index]["data"].tolist()
        self.select_index(select_index,reverse)


    def select_point(self,pos,reverse):
        items=self.current_plot.scatter.pointsAt(pos)
        if len(items):

            item=items[0]

            index=item.index()
            structure_index =item.data()
            self.select_index(structure_index,reverse)

    def select_index(self,structure_index,reverse):
        if isinstance(structure_index,int):
            structure_index=[structure_index]
        if reverse:
            self.dataset.uncheck(structure_index)
        else:

            self.dataset.select(structure_index)
        if structure_index:
            self.update_axes_color(structure_index, reverse)


    def update_axes_color(self,structure_index,reverse ):


        for i,plot in enumerate(self.axes_list):

            if not hasattr(plot,"scatter"):
                continue



            structure_index_set= set(structure_index)
            index_list = [i for i, val in enumerate(plot.scatter.data["data"]) if val in structure_index_set]
            plot.scatter.data["brush"][index_list]=self.dataset.dataset[i].normal_color if  reverse else self.dataset.dataset[i].selected_color
            plot.scatter.data['sourceRect'][index_list] = (0, 0, 0, 0)



            plot.scatter.updateSpots(  )


            #这种全部重新设置 比较慢  放弃
            # color=self.dataset.dataset[i].colors
            # color[index_list]=self.dataset.dataset[i].selected_color
            # plot.scatter.setBrush(color)


    def revoke(self):
        """
        如果有删除的结构  撤销上一次删除的
        :return:
        """
        if self.dataset.is_revoke:
            self.dataset.revoke()
            self.plot_all()

        else:
            MessageManager.send_info_message("No undoable deletion!")