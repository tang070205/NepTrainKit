#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/10/20 22:22
# @Author  : 兵
# @email    : 1747193328@qq.com

import numpy as np
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPainter
from pyqtgraph import mkPen, ScatterPlotItem, TextItem, ViewBox,PlotDataItem

from .toolbar import NepDisplayGraphicsToolBar
from .canvas import CustomGraphicsLayoutWidget
from .. import MessageManager, Config
from ..custom_widget.dialog import GetIntMessageBox, SparseMessageBox
from ..io import NepTrainResultData
from ..io.select import farthest_point_sampling
from ..types import Brushes, Pens
from NepTrainKit import utils


class NepResultGraphicsLayoutWidget(CustomGraphicsLayoutWidget):
    structureIndexChanged=Signal(int)
    def __init__(self,parent=None):
        super().__init__(parent)
        self._parent=parent
        self.nep_result_data=None
        self.draw_mode=False
        self.setRenderHint(QPainter.Antialiasing, False)
        # self.setViewportUpdateMode(self.ViewportUpdateMode.BoundingRectViewportUpdate)

    def set_tool_bar(self, tool):
        self.tool_bar: NepDisplayGraphicsToolBar = tool
        self.tool_bar.panSignal.connect(self.pan)
        self.tool_bar.resetSignal.connect(self.auto_range)
        self.tool_bar.deleteSignal.connect(self.delete)
        self.tool_bar.revokeSignal.connect(self.revoke)
        self.tool_bar.findMaxSignal.connect(self.find_max_error_point)
        self.tool_bar.sparseSignal.connect(self.sparse_point)
        self.tool_bar.penSignal.connect(self.pen)

    def auto_range(self):
        if self.current_plot:
            self.current_plot.getViewBox().autoRange()

    def pan(self, checked):

        if self.current_plot:

            self.current_plot.setMouseEnabled(checked, checked)
            self.current_plot.getViewBox().setMouseMode(ViewBox.PanMode)
    def pen(self, checked):
        if self.current_plot is None:

            return False

        if checked:
            self.draw_mode=True
            # 初始化鼠标状态和轨迹数据
            self.is_drawing = False
            self.x_data = []
            self.y_data = []

        else:
            self.draw_mode=False
            pass
    def mousePressEvent(self, event):
        if not self.draw_mode:
            return super().mousePressEvent(event)

        if event.button() == Qt.MouseButton.LeftButton or event.button() == Qt.MouseButton.RightButton:
            self.is_drawing = True
            self.x_data.clear()  # 清空之前的轨迹数据
            self.y_data.clear()  # 清空之前的轨迹数据
            self.curve = self.current_plot.plot([], [], pen='r')

            self.curve.setData([], [])  # 清空绘制线条，避免对角线


    def mouseReleaseEvent(self, event):

        if not self.draw_mode:
            return super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.LeftButton  or event.button() == Qt.MouseButton.RightButton:
            self.is_drawing = False
            reverse=event.button() == Qt.MouseButton.RightButton
            self.current_plot.removeItem(self.curve)
            # 创建鼠标轨迹的多边形
            if len(self.x_data)>2:

                self.select_point_from_polygon(np.column_stack((self.x_data, self.y_data)),reverse)
            else:
                # 右键的话  选中单个点
                pass
                pos = event.pos()
                mouse_point = self.current_view_box.mapSceneToView(pos)

                x = mouse_point.x()
                self.select_point(mouse_point,reverse)
            return


    def mouseMoveEvent(self, event):
        if not self.draw_mode:
            return super().mouseMoveEvent(event)

        if self.is_drawing:
            pos = event.pos()
            if self.current_plot.sceneBoundingRect().contains(pos):
                # 将场景坐标转换为视图坐标
                mouse_point =self.current_view_box.mapSceneToView(pos)
                x, y = mouse_point.x(), mouse_point.y()
                # 记录轨迹数据
                self.x_data.append(x)
                self.y_data.append(y)

                # 更新绘图
                self.curve.setData(self.x_data, self.y_data)

    def find_max_error_point(self):
        dataset = self.get_current_dataset()
        if dataset is None:
            return
        box= GetIntMessageBox(self._parent,"Please enter an integer N, it will find the top N structures with the largest errors")
        n = Config.getint("widget","max_error_value",10)
        box.intSpinBox.setValue(n)

        if not box.exec():
            return
        nmax= box.intSpinBox.value()
        Config.set("widget","max_error_value",nmax)
        index= (dataset.get_max_error_index(nmax))

        self.select_index(index,False)

    def sparse_point(self):
        if  self.nep_result_data is None:
            return
        box= SparseMessageBox(self._parent,"Please specify the maximum number of structures and minimum distance")
        n_samples = Config.getint("widget","sparse_num_value",10)
        distance = Config.getfloat("widget","sparse_distance_value",0.01)

        box.intSpinBox.setValue(n_samples)
        box.doubleSpinBox.setValue(distance)

        if not box.exec():
            return
        n_samples= box.intSpinBox.value()
        distance= box.doubleSpinBox.value()

        Config.set("widget","sparse_num_value",n_samples)
        Config.set("widget","sparse_distance_value",distance)

        dataset = self.nep_result_data.descriptor
        indices_to_remove = farthest_point_sampling(dataset.now_data,n_samples=n_samples,min_dist=distance)

        # 获取所有索引（从 0 到 len(arr)-1）
        all_indices = np.arange(dataset.now_data.shape[0])

        # 使用 setdiff1d 获取不在 indices_to_remove 中的索引
        remaining_indices = np.setdiff1d(all_indices, indices_to_remove)
        structures = dataset.group_array[remaining_indices]
        self.select_index(structures.tolist(),False)
    def set_dataset(self,dataset):
        self.nep_result_data:NepTrainResultData=dataset
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

    def get_plot_dataset(self,plot):
        plot_index = self.axes_list.index(plot)
        return self.nep_result_data.dataset[plot_index]




    def get_current_dataset(self):
        if self.current_plot is None:
            return None
        return self.get_plot_dataset(self.current_plot)
    @utils.timeit
    def plot_all(self):
        self.nep_result_data.select_index.clear()

        for index,_dataset in enumerate(self.nep_result_data.dataset):
            plot=self.axes_list[index]
            plot.disableAutoRange()
            plot.clear()
            if _dataset.title not in ["descriptor"]:
                plot.addLine(angle=45, pos=(0.5, 0.5), pen=mkPen('r', width=2))

            # else:
            plot.setTitle(_dataset.title)

            scatter = ScatterPlotItem(_dataset.x,_dataset.y,data=_dataset.structure_index,
                                      brush=Brushes.get(_dataset.title.upper()) ,pen=Pens.get(_dataset.title.upper()),
                                      symbol='o',size=7,

                                      )


            scatter.sigClicked.connect(self.item_clicked)
            plot.add_scatter(scatter)





            # 设置视图框更新模式
            plot.autoRange()
            if _dataset.title not in ["descriptor"]:

                pos=self.convert_pos(plot,(0 ,1))
                text=f"rmse: {_dataset.get_formart_rmse()}"
                text_item = TextItem(text=text ,color=(231, 63, 50))
                text_item.setPos(*pos)
                plot.addItem(text_item)

        # print(time.time()-start)
        #5.67748498916626
    def item_clicked(self,scatter_item,items,event):

        if items.any():
            item=items[0]

            self.structureIndexChanged.emit(item.data())

    def plot_current_point(self,structure_index):

        for plot in  self.axes_list :
            dataset=self.get_plot_dataset(plot)
            array_index=dataset.convert_index(structure_index)

            data=dataset.now_data[array_index,: ]
            plot.set_current_point(data[:,dataset.cols:].flatten(),
                                   data[:, :dataset.cols].flatten(),
                                   )



    def delete(self):
        if self.nep_result_data is not None and self.nep_result_data.select_index:

            self.nep_result_data.delete_selected()
            self.plot_all()


    def select_point_from_polygon(self,polygon_xy,reverse ):
        index=self.is_point_in_polygon(np.column_stack([self.current_plot._scatter.data["x"],self.current_plot._scatter.data["y"]]),polygon_xy)
        index = np.where(index)[0]
        select_index=self.current_plot._scatter.data[index]["data"].tolist()
        self.select_index(select_index,reverse)


    def select_point(self,pos,reverse):
        items=self.current_plot._scatter.pointsAt(pos)
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
            self.nep_result_data.uncheck(structure_index)
            self.update_axes_color(structure_index, Brushes.Default)

        else:

            self.nep_result_data.select(structure_index)

            self.update_axes_color(structure_index, Brushes.Selected)


    def update_axes_color(self,structure_index,color=Brushes.Selected):


        for i,plot in enumerate(self.axes_list):

            if not plot._scatter:
                continue
            structure_index_set= set(structure_index)
            index_list = [i for i, val in enumerate(plot._scatter.data["data"]) if val in structure_index_set]

            plot._scatter.data["brush"][index_list]=   color
            plot._scatter.data['sourceRect'][index_list] = (0, 0, 0, 0)


            plot._scatter.updateSpots( )





    def revoke(self):
        """
        如果有删除的结构  撤销上一次删除的
        :return:
        """

        if self.nep_result_data and  self.nep_result_data.is_revoke:
            self.nep_result_data.revoke()
            self.plot_all()

        else:
            MessageManager.send_info_message("No undoable deletion!")
