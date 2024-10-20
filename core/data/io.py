#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/10/18 17:14
# @Author  : 兵
# @email    : 1747193328@qq.com
import os
import threading

import numpy as np
from PySide6.QtCore import QThread
from loguru import logger
from qfluentwidgets import StateToolTip


def read_atom_num_from_xyz(path):
    with open(path, 'rb') as file:
        atom_counts = []
        while True:
            line = file.readline().decode().strip()  # 读取一行并去除空白字符
            if not line:  # 如果读到文件末尾，退出循环
                break
            if line.isdigit():  # 检查行是否为数字
                atom_counts.append(int(line))  # 将数字添加到列表中
                skip_lines = int(line)  # 要跳过的行数

                file.seek(skip_lines, 1)  # 移动文件指针，跳过接下来的N行

    return atom_counts




def read_nep_out_file(file_path):
    logger.info("读取文件{}".format(file_path))
    if os.path.exists(file_path):

        data = np.loadtxt(file_path)

        return data
    else:
        return np.array([])


class LoadingThread(QThread):

    def __init__(self,parent=None,show_tip=True,title='运行中'):
        super(LoadingThread,self).__init__(parent)
        if show_tip:
            self.tip = StateToolTip(title, '请耐心等待哦~~', parent)
            self.tip.show()
            self.finished.connect(self.__finished_work)
            self.tip.closedSignal.connect(self.quit)
        else:
            self.tip=None

    def run(self ):

        self.func()
    def start_work(self,func,*args,**kwargs):
        self.func=lambda : func(*args,**kwargs)
        self.start()
    def __finished_work(self ):
        if self.tip:

            self.tip.setContent('任务完成啦 😆')
            self.tip.setState(True)

