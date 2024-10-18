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
from matplotlib.backend_bases import _Mode, PickEvent, MouseEvent, KeyEvent, MouseButton
import matplotlib.path as mplPath
from matplotlib.widgets import SpanSelector

import utils
from core import MessageManager

matplotlib.use('Qt5Agg')

from PySide6.QtCore import QBuffer, QIODevice
from PySide6.QtWidgets import QApplication, QVBoxLayout

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar

from matplotlib.figure import Figure

from PySide6.QtGui import Qt, QPixmap, QIcon, QAction, QPainter, QResizeEvent, QImage





def catch_plot_except(func):
    """
    画图函数的装饰器 用于捕捉异常 并在函数结束后进行更新画布
    :param func:
    :return:
    """
    def wrapper(self,*args,**kwargs):
        try:
            func(self,*args,**kwargs)
        except Exception as e:
            logger.error(traceback.format_exc())
            MessageManager.send_error_message("未处理的异常！")

        finally:
            if hasattr(self,"Canvas"):
                self.Canvas.figure.tight_layout()
                self.Canvas.draw_idle()
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

    Canvas = MplCanvas(plot_widget )
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
    fname = utils.call_path_dialog(canvas.parent(),"选择保存文件",default_filename=file_name,file_filter=filters,selected_filter=selectedFilter)

    if fname:
        try:
            canvas.figure.savefig(fname )
            MessageManager.send_success_message(f"图片成功保存到：{fname}" )

        except Exception as e:
            MessageManager.send_error_message("未知错误" )










class MplCanvas(FigureCanvasQTAgg):

    def __init__(self,*args,**kwargs):

        super(MplCanvas, self).__init__(Figure())
        self.axes = self.figure.add_subplot(111)
        self._update_pixel_ratio()

        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)


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

    def add_axes(self, row_num,col_num=1,**kwargs):

        self.figure.clf()

        result = []
        for i in range(1, row_num*col_num + 1):
            result.append(self.figure.add_subplot(row_num, col_num, i,**kwargs))
        return result





    def delaxes(self, ax):
        self.figure.delaxes(ax)


class MyToolBar(NavigationToolbar):
    def __init__(self, canvas, parent=None, coordinates=True):
        super().__init__(canvas, parent, coordinates)
        self.add_action("copy_fig",
                           utils.image_abs_path("copy_figure.svg"),
                           "复制图片到剪贴板", "copy_fig_to_clipboard")

        self.add_action(None,None,None,None)
        self.add_action("open_pen",
                           utils.image_abs_path("pen.svg"),
                           "开始框选", "toggle_drawing_mode").setCheckable(True)
        self.add_action("delete_path",
                           utils.image_abs_path("delete.svg"),
                           "删除选中点", "delete_point")


        # 添加工具按钮
        # self.Canvas.axes_button = plt.axes([0.8, 0.01, 0.1, 0.05])
        # self.button = Button(self.Canvas.axes_button, '自由绘制')
        # self.button.on_clicked(self.toggle_drawing_mode)

        # 初始化状态
        self.drawing = False  # 是否处于绘制模式
        self.line = None      # 保存当前绘制的线条
        self.xs = []          # x 坐标
        self.ys = []          # y 坐标

        # 绑定鼠标事件
        self.cid_press = self.canvas.mpl_connect('button_press_event', self.on_click)
        self.cid_motion = self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.cid_release = self.canvas.mpl_connect('button_release_event', self.on_release)


    def delete_point(self):
        KeyEvent(name="key_press_event",
                 key="delete",
                 x=0,y=0,
                 canvas=self.canvas,



        )._process()

    def toggle_drawing_mode(self):
        """ 切换是否处于自由绘制模式 """

        self.drawing = not self.drawing
        if self.drawing:
            MessageManager.send_info_message("自由绘制模式已激活，请按住并拖动以绘制轨迹")

            self.canvas.widgetlock(self)
            self._actions['toggle_drawing_mode'].setChecked(True)
            self.mode=_Mode.NONE
            super()._update_buttons_checked()

        else:
            MessageManager.send_info_message("自由绘制模式已关闭")
            self.canvas.widgetlock.release(self)

            self._actions['toggle_drawing_mode'].setChecked(False)




    def _update_buttons_checked(self):
        self._actions['toggle_drawing_mode'].setChecked(False)
        self.drawing=False
        super()._update_buttons_checked()



    def on_click(self, event):
        """ 鼠标按下时开始绘制 """
        if self.drawing and event.inaxes == self.canvas.axes:
            self.xs = [event.xdata]
            self.ys = [event.ydata]
            # 开始新的线条绘制
            self.line, = self.canvas.axes.plot(self.xs, self.ys, color='red')

    def on_motion(self, event):
        """ 鼠标拖动时更新轨迹 """
        if self.drawing and self.line and event.inaxes == self.canvas.axes:
            # 添加新坐标到列表
            self.xs.append(event.xdata)
            self.ys.append(event.ydata)
            # 更新线条数据
            self.line.set_data(self.xs, self.ys)
            # self.canvas.draw_idle()  # 实时刷新画布
            # self.canvas.axes.draw_artist(self.line)
            # self.canvas.axes.draw_artist(self.canvas.axes.patch)  # 先绘制背景
            self.canvas.axes.draw_artist(self.line)  # 再绘制线条

            # 只更新该子图区域
            self.canvas.blit(self.canvas.axes.bbox)
    def on_release(self, event):
        """ 鼠标释放时停止绘制 """
        if self.drawing:
            if self.line:
                self.line.remove()
                # self.canvas.axes.draw_artist(self.canvas.axes.patch)
                # self.canvas.blit(self.canvas.axes.bbox)
            else:
                return
            poly_path = mplPath.Path(np.column_stack((self.xs, self.ys)))
            scatter = self.canvas.axes.collections[0]  # Axes.collections 中的第一个对象是散点图

            # 获取所有散点的坐标
            coordinates = scatter.get_offsets()

            # for i in range(len(self.dataset_now)):
            #     if poly_path.contains_points(self.dataset_now[i]):

            contains_list=poly_path.contains_points(coordinates)

            true_indices = np.where(contains_list)[0]
            event = PickEvent(
                name='pick_event',
                canvas=self.canvas,
                mouseevent=event,  # 没有具体的鼠标事件
                artist=scatter,  # 拾取的对象
                ind=true_indices  # 被选中的数据索引
            )
            event._process()
            # event.
            # self.canvas.callbacks.process('pick_event', event)
            self.xs = []
            self.ys = []
            self.line = None
            # self.canvas.axes.draw_artist(self.line)

            # self.canvas.draw_idle()

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

        return QIcon(pm)
    def add_action(self, action_name, icon_path, tooltip_text, callback):

        if action_name is None:
            action=QAction(self)
            action.setSeparator(True)
            self.insertAction(self.actions()[-1],action)


        else:

            svg=QSvgRenderer(icon_path)

            icon = QPixmap(100,100)

            icon_color=Qt.transparent
            icon.fill(icon_color)


            painter = QPainter(icon)

            svg.render(painter)
            painter.end()
            icon.setDevicePixelRatio(
                self.devicePixelRatioF() or 1)
            action = QAction(icon,
                        action_name, self)

            action.triggered.connect(getattr(self, callback) if isinstance(callback, str) else callback)
            self.insertAction(self.actions()[-1], action)
            self._actions[callback] = action

            if tooltip_text is not None:
                action.setToolTip(tooltip_text)
        return action
