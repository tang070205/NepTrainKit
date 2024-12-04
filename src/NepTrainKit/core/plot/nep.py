#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/10/20 22:22
# @Author  : 兵
# @email    : 1747193328@qq.com

import numpy as np
from PySide6.QtCore import Signal
from pyqtgraph import mkPen, ScatterPlotItem, TextItem

from .canvas import CustomGraphicsLayoutWidget
from .. import MessageManager
from ..io import NepTrainResultData
from ..types import Brushes
from NepTrainKit import utils


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

    def convert_pos(self,plot,pos):
        view_range = plot.viewRange()
        x_range = view_range[0]  # x轴范围 [xmin, xmax]
        y_range = view_range[1]  # y轴范围 [ymin, ymax]

        # 将百分比位置转换为坐标
        x_percent = pos[0] # 50% 对应 x 轴中间
        y_percent =  pos[1]  # 20% 对应 y 轴上的某个位置

        x_pos = x_range[0] + x_percent * (x_range[1] - x_range[0])  # 根据百分比计算实际位置
        y_pos = y_range[0] + y_percent * (y_range[1] - y_range[0])  # 根据百分比计算实际位置
        return x_pos,y_pos

    def get_current_dataset(self):
        if self.current_plot is None:
            return None
        plot_index = self.axes_list.index(self.current_plot)
        return self.dataset.dataset[plot_index]
    @utils.timeit
    def plot_all(self):
        self.dataset.select_index.clear()
        _pen = mkPen(None)
        # import time
        # start = time.time()
        for index,_dataset in enumerate(self.dataset.dataset):
            plot=self.axes_list[index]
            plot.clear()
            if _dataset.title not in ["descriptor"]:
                plot.addLine(angle=45, pos=(0.5, 0.5), pen=mkPen('r', width=2))

            # else:
            plot.setTitle(_dataset.title)

            scatter = ScatterPlotItem(_dataset.x,_dataset.y,data=_dataset.structure_index,
                                      brush=Brushes.TransparentBrush ,pen=mkPen(color="blue", width=0.5), symbol='o',size=7
                                     )


            scatter.sigClicked.connect(self.item_clicked)
            plot.scatter=scatter
            # plot.setDownsampling(auto=False )
            plot.addItem(scatter)
            if _dataset.title not in ["descriptor"]:

                pos=self.convert_pos(plot,(0 ,1))
                text=f"rmse: {_dataset.get_formart_rmse()}"
                text_item = TextItem(text=text ,color=(231, 63, 50))
                text_item.setPos(*pos)
                plot.addItem(text_item)

            # plot.autoRange()
        # print(time.time()-start)
        #5.67748498916626
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
        elif isinstance(structure_index,np.ndarray):
            structure_index=structure_index.tolist()

        if not structure_index:
            return
        if reverse:
            self.dataset.uncheck(structure_index)
            self.update_axes_color(structure_index, Brushes.TransparentBrush)

        else:

            self.dataset.select(structure_index)

            self.update_axes_color(structure_index, Brushes.RedBrush)


    def update_axes_color(self,structure_index,color=Brushes.RedBrush):


        for i,plot in enumerate(self.axes_list):

            if not hasattr(plot,"scatter"):
                continue
            structure_index_set= set(structure_index)
            index_list = [i for i, val in enumerate(plot.scatter.data["data"]) if val in structure_index_set]

            plot.scatter.data["brush"][index_list]=   color
            plot.scatter.data['sourceRect'][index_list] = (0, 0, 0, 0)


            plot.scatter.updateSpots(  )





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