#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/10/17 13:14
# @Author  : 兵
# @email    : 1747193328@qq.com
import os
import subprocess
import sys

import numpy as np
from PySide6.QtCore import QThread
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFileDialog, QApplication
from loguru import logger
from qfluentwidgets import StateToolTip

from core import Config
#设置log日志文件
logger.add("./Log/{time:%Y-%m-%d}.log", rotation='00:00' ,
           level="INFO",   encoding="utf8",
           compression="zip", retention="4 days")


def loghandle(cls):
    #装饰器 给类传入一个变量可以直接调用self.logger
    if not hasattr(cls, "logger"):
        setattr(cls, "logger", logger)
    return cls

def image_abs_path(file_name):
    """
    将图转换成绝对路径的格式
    :param file_name: 文件名 比如save.svg
    :return: 全路径
    """

    root=os.path.abspath(os.path.dirname(__file__))

    return os.path.join(root,f"src/images/{file_name}")
def image_to_qicon(file_name):
    path=image_abs_path(file_name)
    if not os.path.exists(path):
        logger.warning(f"尝试使用不存在的文件路径：{path}")
    return QIcon(path)





def call_path_dialog(self, title, dialog_type="file", default_filename="", file_filter="", selected_filter=""):
    dialog_map = {
        "file": lambda: QFileDialog.getSaveFileName(self, title, os.path.join(Config.get_path(), default_filename), file_filter, selected_filter),
        "select": lambda: QFileDialog.getOpenFileName(self, title, Config.get_path(), file_filter),
        "selects": lambda: QFileDialog.getOpenFileNames(self, title, Config.get_path(), file_filter),
        "directory": lambda: QFileDialog.getExistingDirectory(self, title, Config.get_path())
    }

    dialog_func = dialog_map.get(dialog_type)
    if not dialog_func:
        return None

    path = dialog_func()

    if isinstance(path, tuple):
        path = path[0]  # 处理 `getSaveFileName` 和 `getOpenFileName` 返回的 tuple
    elif isinstance(path, list):
        if not path:
            return None
        path = path[0]  # `getOpenFileNames` 返回 list

    if not path:
        return None

    # 提取目录并保存到配置
    if os.path.isfile(path):
        last_dir = os.path.dirname(path)
    else:
        last_dir = path
    Config.set("setting", "last_path", last_dir)
    return path

def unzip( ):
    if sys.platform=="win32":

        cmd = f"ping -n 3 127.0.0.1&update.exe update.zip&ping -n 2 127.0.0.1&start NepTrainKit.exe"
    else:
        cmd = f"ping -n 3 127.0.0.1&update.bin update.zip&ping -n 2 127.0.0.1&start NepTrainKit.bin"

    subprocess.Popen(cmd, shell=True)
    if QApplication.instance():
        QApplication.instance().exit()
    else:
        quit()


class LoadingThread(QThread):

    def __init__(self,parent=None,show_tip=True,title='运行中'):
        super(LoadingThread,self).__init__(parent)
        self.show_tip=show_tip
        self.title=title
        self._parent=parent
    def run(self ):

        self.func()
    def start_work(self,func,*args,**kwargs):
        if self.show_tip:
            self.tip = StateToolTip(self.title, '请耐心等待哦~~', self._parent)
            self.tip.show()
            self.finished.connect(self.__finished_work)
            self.tip.closedSignal.connect(self.quit)
        else:
            self.tip=None
        self.func=lambda : func(*args,**kwargs)
        self.start()
    def __finished_work(self ):
        if self.tip:
            self.tip.setContent('任务完成啦 😆')
            self.tip.setState(True)