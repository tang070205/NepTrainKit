#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/10/17 13:03
# @Author  : 兵
# @email    : 1747193328@qq.com
import traceback
from collections.abc import Iterable

import matplotlib
import matplotlib.backends.backend_pdf
import matplotlib.backends.backend_pgf
import matplotlib.backends.backend_ps
import matplotlib.backends.backend_svg
import numpy as np
from PySide6.QtSvg import QSvgRenderer
from loguru import logger
from matplotlib import cbook
from matplotlib.collections import PathCollection
from matplotlib.transforms import IdentityTransform
from matplotlib.widgets import SpanSelector

import utils
from core import MessageManager

matplotlib.use('Qt5Agg')

from PySide6.QtCore import QBuffer, QIODevice
from PySide6.QtWidgets import QApplication, QVBoxLayout

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from PySide6.QtGui import Qt, QPixmap, QIcon, QAction, QPainter, QResizeEvent, QImage





def catch_plot_except(func):
    """

    :param func:
    :return:
    """
    def wrapper(self,*args,**kwargs):
        try:

            func(self,*args,**kwargs)

        except NoDataError as e:
            #如果后面不想显示没有数据的消息 可以用pass代替
            MessageManager.send_message(str(e))
        except CalculateError as e:
            MessageManager.send_message(str(e))

        except Exception as e:
            logger.error(traceback.format_exc())
            MessageManager.send_message("未处理的异常！")

        finally:
            # print("draw",func)
            if hasattr(self,"Canvas"):


                self.Canvas.figure.tight_layout()

                self.Canvas.draw_idle()

            if hasattr(self,"Canvas1"):
                self.Canvas1.figure.tight_layout()
                self.Canvas1.draw_idle()

            if hasattr(self,"MapCanvas"):

                self.MapCanvas.figure.tight_layout()

                # self.MapCanvas.fig.subplots_adjust(bottom=0.2, top=0.8)  # 调整底部和顶部边距
                self.MapCanvas.draw()

            MessageManager.wake()

    return wrapper

def init_canvas(plot_widget,tool_bar=True ):
    layout=plot_widget.layout()
    layout:QVBoxLayout
    size=None
    if layout is not None:
        while not layout.isEmpty( ):
            w=layout.takeAt(0)
            wig=w.widget()
            if wig:
                if isinstance(wig,MplCanvas):
                    size=wig.size()
                w.widget().deleteLater()

    else:
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        plot_widget.setLayout(layout)

    Canvas = MplCanvas(plot_widget, width=5, height=4, dpi=100)
    if tool_bar:
        toolbar = MyToolBar(Canvas, plot_widget, )
        layout.addWidget(toolbar)
    layout.addWidget(Canvas)
    if size:
        Canvas.reshape(size)
    layout.update()
    return Canvas


def export_image(canvas,file_name):

    filetypes = canvas.get_supported_filetypes_grouped()
    sorted_filetypes = sorted(filetypes.items())
    default_filetype = canvas.get_default_filetype()

    filters = []
    selectedFilter = None
    for name, exts in sorted_filetypes:
        exts_list = " ".join(['*.%s' % ext for ext in exts])
        filter = f'{name} ({exts_list})'
        if default_filetype in exts:
            selectedFilter = filter
        filters.append(filter)
    filters = ';;'.join(filters)
    fname = utils.call_path_dialog(canvas.parent(),"选择保存文件",default_filename=file_name,file_filter=filters,selectedFilter=selectedFilter)

    if fname:

        try:


            canvas.figure.savefig(fname )
            MessageManager.send_save_message(fname,success=True)

        except Exception as e:
            MessageManager.send_save_message("未知错误",success=False)

class MyToolBar(NavigationToolbar):
    def __init__(self, canvas, parent=None, coordinates=True):
        super().__init__(canvas, parent, coordinates)

        self.add_action("copy_fig",
                           utils.image_abs_path("copy_figure.svg"),
                           "复制图片到剪贴板", "copy_fig_to_clipboard")




    def copy_fig_to_clipboard(self):

        image =self.canvas.get_image()


        QApplication.clipboard().setImage(image)

        MessageManager.send_success_message("复制成功！")


    def save_figure(self,*args):
        return export_image(self.canvas,"image.png")


    def _icon(self, name):
        """
        Construct a `.QIcon` from an image file *name*, including the extension
        and relative to Matplotlib's "images" data directory.
        """
        # use a high-resolution icon with suffix '_large' if available
        # note: user-provided icons may not have '_large' versions
        path_regular = cbook._get_data_path('images', name)
        path_large = path_regular.with_name(
            path_regular.name.replace('.png', '_large.png'))
        filename = str(path_large if path_large.exists() else path_regular)

        pm = QPixmap(filename)
        pm.setDevicePixelRatio(
            self.devicePixelRatioF() or 1)  # rarely, devicePixelRatioF=0
        # if self.palette().color(self.backgroundRole()).value() < 128:
        #     icon_color = self.palette().color(self.foregroundRole())
        #     mask = pm.createMaskFromColor(
        #         QColor('black'),
        #         Qt.MaskMode.MaskOutColor)
        #     pm.fill(icon_color)
        #     pm.setMask(mask)
        return QIcon(pm)
    def add_action(self, action_name, icon_path, tooltip_text, callback):

        if action_name is None:
            self.addSeparator()
        else:

            # pm = QPixmap(icon_path)
            # pm.setDevicePixelRatio(
            #     self.devicePixelRatioF() or 1)  # rarely, devicePixelRatioF=0
            svg=QSvgRenderer(icon_path)

            icon = QPixmap(100,100)

            icon_color=Qt.transparent
            icon.fill(icon_color)


            painter = QPainter(icon)

            # painter.begin(icon)
            svg.render(painter)
            painter.end()
            icon.setDevicePixelRatio(
                self.devicePixelRatioF() or 1)  # rarely, devicePixelRatioF=0


            a = QAction(icon,
                        action_name, self)

            a.triggered.connect(getattr(self, callback) if isinstance(callback, str) else callback)
            self.insertAction(list(self._actions.values())[-1], a)
            self._actions[callback] = a

            if tooltip_text is not None:
                a.setToolTip(tooltip_text)


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.vmax = None
        self.vmin = None

        self.create_fig()

        super(MplCanvas, self).__init__(self.fig)
        # self.setStyleSheet("QWidget{border-radius:5px}")

        self.axes = self.fig.add_subplot(111)
        self.connect_events = {}
        self._update_pixel_ratio()

        # self.fig.tight_layout()
    def create_fig(self):
        if hasattr(self,"fig"):

            self.fig=Figure()
            self.fig.set_canvas(self)
            self.figure = self.fig
        else:
            self.fig = Figure(  )

        # self.fig.set_canvas(self)
        # self.figure = self.fig
    def reshape(self,size):
        self._update_pixel_ratio()

        event = QResizeEvent(size, size)
        self.resizeEvent(event)
        self.update()

    def refresh(self):

        self.reshape(self.size())
    def get_image(self,*args, **kwargs):



        buff = QBuffer( )
        buff.open(QIODevice.OpenModeFlag.ReadWrite)
        self.print_figure(buff ,*args, **kwargs)

        buff.seek(0)
        image = QImage(self.size() ,QImage.Format.Format_ARGB32)

        image.loadFromData(buff.readAll())

        return image


    def bind_span(self):
        span = SpanSelector(self.axes, self.onselect, 'horizontal', useblit=True, minspan=0.01,
                            interactive=True, )
        self.connect_events["span"] = self.mpl_connect('key_press_event', span)

    def onselect(self, vmin, vmax):

        if vmin != vmax:

            self.vmin = vmin
            self.vmax = vmax
        else:
            self.vmin = None
            self.vmax = None

    def add_axes(self, row_num,col_num=1,**kwargs):
        # print_call_stack()
        for value in self.connect_events.values():
            # 每次都清理下事件
            self.mpl_disconnect(value)
        self.fig.clf()
        self.vmin=None
        self.vmax=None
        result = []
        for i in range(1, row_num*col_num + 1):
            result.append(self.fig.add_subplot(row_num, col_num, i,**kwargs))
        return result

    def create_collection(self,x, y, marker ,size=500,ax=None,**kwargs):
        if ax is None:
            ax=self.axes

        # transformed_paths = [marker(i) for i in angles]
        transformed_paths=marker
        offsets = np.array([x, y]).T

        # 将所有路径集合到一个   PathCollection
        # transformed_paths = [path.transformed(path.ge)  for path in transformed_paths]
        # collection = CustomPathCollection(transformed_paths,   offsets=offsets,
        #                             offset_transform= ax.projection or ax.transData,
        #                             **kwargs )

        if isinstance(size,Iterable):
            sizes=size
        else:
            sizes = [size] * len(transformed_paths)
        collection = CustomPathCollection(transformed_paths,sizes=sizes , offsets=offsets,
                                    offset_transform= ax.projection or ax.transData,
                                    **kwargs )
        collection.set_transform(IdentityTransform())
        ax.add_collection(collection)
        ax.autoscale_view()

        return collection

    def create_PatchCollection(self,x, y, marker ,size=500,ax=None,**kwargs):
        if ax is None:
            ax=self.axes

        # transformed_paths = [marker(i) for i in angles]
        transformed_paths=marker
        offsets = np.array([x, y]).T

        # 将所有路径集合到一个   PathCollection
        # transformed_paths = [path.transformed(path.ge)  for path in transformed_paths]
        # collection = CustomPathCollection(transformed_paths,   offsets=offsets,
        #                             offset_transform= ax.projection or ax.transData,
        #                             **kwargs )
        collection = CustomPatchCollection(transformed_paths,   offsets=offsets,
                                    offset_transform= ax.projection or ax.transData,
                                    **kwargs )
        collection.set_transform(IdentityTransform())
        ax.add_collection(collection)
        ax.autoscale_view()

        return collection

    def delaxes(self, ax):
        self.fig.delaxes(ax)

