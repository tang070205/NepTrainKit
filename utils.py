#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/10/17 13:14
# @Author  : 兵
# @email    : 1747193328@qq.com
import os

import numpy as np
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFileDialog
from loguru import logger
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

