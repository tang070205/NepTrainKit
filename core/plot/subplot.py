#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/10/17 19:37
# @Author  : 兵
# @email    : 1747193328@qq.com
from matplotlib.backend_bases import MouseEvent, MouseButton
from matplotlib.gridspec import GridSpec

from .canvas import MplCanvas

class SubplotSwitcher:

    def __init__(self,Canvas:MplCanvas):
        self.Canvas=Canvas
        self.axes_list = []
        self.width = 3
        self.height = 3
        self.last_enlarge_index =None
        self.grid_spec:GridSpec = None
        self.cid=None
    def subplot(self,row,col,**kwargs):

        self.axes_list.clear()
        self.Canvas.figure.clf()

        self.grid_spec = GridSpec(row, col , figure=self.Canvas.figure )

        for r in range(row):
            for c in range(col):

                self.axes_list.append(self.Canvas.figure.add_subplot(self.grid_spec[r, c]))

        self.Canvas.figure.tight_layout()
        self.cid=self.Canvas.mpl_connect('button_press_event', self.on_click)
        MouseEvent(
            name="button_press_event",
            canvas=self.Canvas,
            x=182,y=540,
            button=MouseButton.LEFT,
            dblclick=True

        )._process()


    def __del__(self):
        if self.cid is not None:
            self.Canvas.mpl_disconnect(self.cid)


    def on_click(self,event):
        """
        子图点击  负责下逻辑
        :param event:
        :return:
        """
        if not event.dblclick or event.inaxes is None:
            #只处理双击的
            return


        axes=event.inaxes
        axes_index = self.axes_list.index(axes)
        if self.last_enlarge_index == axes_index:

            return
        self.last_enlarge_index = axes_index
        width_ratios = [1 for i in range(self.grid_spec._ncols)]
        height_ratios = [1 for i in range(self.grid_spec._nrows)]

        print(axes_index,self.grid_spec._ncols)
        height_ratios[axes_index // self.grid_spec._ncols] = self.height
        width_ratios[axes_index % self.grid_spec._ncols] = self.width
        self.grid_spec.set_height_ratios(height_ratios)
        self.grid_spec.set_width_ratios(width_ratios)

        i=0
        for r in range(self.grid_spec._nrows):
            for c in range(self.grid_spec._ncols):
                self.axes_list[i]._set_position(self.grid_spec[r,c].get_position(self.Canvas.figure))
                i+=1
        self.Canvas.axes=axes
        self.Canvas.draw()

