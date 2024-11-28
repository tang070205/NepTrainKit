#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/10/17 13:03
# @Author  : 兵
# @email    : 1747193328@qq.com
import os
import sys
import traceback

import pyqtgraph as pg
from PySide6.QtCore import Qt, QFile, QTextStream
from PySide6.QtGui import QIcon
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from PySide6.QtWidgets import QApplication, QMenuBar
from qfluentwidgets import (setTheme, Theme, FluentWindow, NavigationItemPosition, InfoBadgePosition, InfoBadge)
from qfluentwidgets import FluentIcon as FIF
from loguru import logger

from NepTrainKit.core import MessageManager, Config
from NepTrainKit.core.widget import *

from NepTrainKit import utils,src_rc

# pg.setConfigOptions(antialias=False )

pg.setConfigOption('background', 'w')  # 设置背景为白色
pg.setConfigOption('foreground', 'k')  # 设置前景元素为黑色（如坐标轴）
@utils.loghandle
class NepTrainKitMainWindow(FluentWindow):

    def __init__(self):
        super().__init__()
        self.setMicaEffectEnabled(False)
        self.init_ui()


    def init_ui(self):
        # create sub interface
        MessageManager._createInstance(self)
        Config()

        self.init_widget()
        self.init_navigation()
        self.initWindow()
        self.init_menu()




    def init_menu(self):
        self.menu = QMenuBar(self)

        file_menu = self.menu.addMenu("文件")

        open_dir_action = file_menu.addAction(QIcon(':/images/src/images/open.svg'),"打开")
        open_dir_action.triggered.connect(self.open_file_dialog)
        export_action=file_menu.addAction(QIcon(':/images/src/images/save.svg'),"导出")

        export_action.triggered.connect(self.export_file_dialog)


        self.titleBar.hBoxLayout.insertWidget(2, self.menu,0,Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignCenter)

    def init_navigation(self):
        self.navigationInterface.setReturnButtonVisible(False)
        self.navigationInterface.setExpandWidth(200)
        self.navigationInterface.addSeparator()
        self.addSubInterface(self.show_nep_interface, QIcon(':/images/src/images/show_nep.svg'), 'NEP数据集展示')

        self.addSubInterface(self.setting_interface, FIF.SETTING, '设置', NavigationItemPosition.BOTTOM)



        self.navigationInterface.activateWindow()

    def init_widget(self):
        self.show_nep_interface=ShowNepWidget(self)

        self.setting_interface=SettingsWidget(self)

    def initWindow(self):
        self.resize(1200, 700)
        self.setWindowIcon(QIcon(':/images/src/images/logo.svg'))
        self.setWindowTitle(f'NepTrainKit')
        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)


    def open_file_dialog(self):


        widget = self.stackedWidget.currentWidget()
        if hasattr(widget,"open_file"):
            widget.open_file( )
    def export_file_dialog(self):
        widget = self.stackedWidget.currentWidget()
        if hasattr(widget,"export_file"):
            widget.export_file( )

def global_exception_handler(exc_type, exc_value, exc_traceback):
    """
    全局异常处理函数
    """


    # 格式化异常信息
    error_message = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))

    # 写入日志
    logger.error(error_message)

def main():
    setTheme(Theme.LIGHT)
    # 设置全局异常捕获
    sys.excepthook = global_exception_handler
    if os.path.exists("update.zip") or os.path.exists("update.tar.gz"):
        utils.unzip()
    app = QApplication(sys.argv)

    theme_file = QFile(":/theme/src/qss/theme.qss")
    theme_file.open(QFile.ReadOnly )
    theme=theme_file.readAll().data().decode("utf-8")
    app.setStyleSheet(theme)
    w = NepTrainKitMainWindow()
    w.show()

    app.exec()


if __name__ == '__main__':
    main()

