#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/10/18 17:14
# @Author  : 兵
# @email    : 1747193328@qq.com
import os

import numpy as np
from loguru import logger

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
        print(data.shape)
        return data
    else:
        return np.array([])