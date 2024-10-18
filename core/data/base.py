#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/10/18 15:31
# @Author  : 兵
# @email    : 1747193328@qq.com
from collections.abc import Iterable

import numpy as np


class DataBase:
    """
    对列表进行封装 比如结构训练集 能量 力
    以下功能要实现：
        1.根据索引删除指定结构
        2.支持回退（记录删除的data）

    """
    def __init__(self,data_list ):
        self.raw_data = np.array(data_list)
        self.now_data=np.array(data_list)
        self.remove_data=np.array([])

        #记录每次删除了几个  比如[3,6,4]
        self.remove_num=[]

    @property
    def num(self):
        return self.now_data.shape[0]
    def remove(self,i):
        if self.now_data.size==0:
            return
        if isinstance(i,int):
            data=self.now_data[i]
            self.now_data = np.delete(self.now_data,i,0)
            self.remove_data=np.append(self.remove_data,data)
            self.remove_num.append(1)
        elif isinstance(i,(list,np.ndarray)):
            datas = self.now_data[i]
            self.now_data = np.delete(self.now_data, i, 0)
            self.remove_data = np.append(self.remove_data, datas)
            self.remove_num.append(len(i))
        else:
            print(i,type(i),isinstance(i,(list,np.ndarray)))
        print(self.now_data.shape)


    def __getitem__(self, item):
        return self.now_data[item]

class NepData:
    def __init__(self,data_list,weight,**kwargs ):
        self.data = DataBase(data_list )
        if isinstance(weight,int):

            weight=np.ones(data_list.shape[0], dtype=int)
        self.weight = DataBase(weight)
        for key,value in kwargs.items():
            setattr(self,key,value)
    @property
    def num(self):
        return self.data.num

    @property
    def now_data(self):
        return self.data.now_data

    def convert_index(self,index_list):

        # 用于存储实际要删除的索引
        remove_indices = list()

        # 根据权重计算实际要删除的索引
        for index in index_list:
            weight_value = self.weight[index]
            actual_indices_to_remove = list(range(index, index + weight_value))
            remove_indices.extend(actual_indices_to_remove)
        # print("convert_index",index_list)

        # print("remove_indices",remove_indices)
        return  remove_indices
    def remove(self,remove_index):
        """
        这里根据权重添加一层 根据权重 计算下实际删除的索引坐标
        :param i:
        :return:
        """
        remove_indices=self.convert_index(remove_index)
        self.data.remove(remove_indices)
        self.weight.remove(remove_index)

class NepPlotData(NepData):

    def __init__(self,data_list,weight,**kwargs ):
        super().__init__(data_list,weight,**kwargs )
        self.__color1="blue"
        self.__selected_color="red"
        self._colors=np.full(data_list.shape[0], self.__color1)  # 初始颜色为蓝色
    @property
    def colors(self):
        return self._colors

    def set_colors(self,index_list,colors,reverse):

        if colors is None:
            colors=self.__selected_color
        index_list=self.convert_index(index_list)

        if reverse:
            # 通过索引列表创建一个布尔数组，用于索引原数组
            change_mask = np.zeros(len(self.colors), dtype=bool)
            change_mask[index_list] = True
            self.colors[change_mask] = np.where(self.colors[change_mask] == self.__color1, colors, self.__color1)
        else:
            self.colors[index_list] = self.__selected_color

    def remove(self,remove_index):

        super().remove(remove_index)
        self._colors=np.full(self.num, self.__color1)  # 初始颜色为蓝色


    def remove_selected(self):
        selected_i = np.where(self.colors == 'red')[0]

        self.remove(selected_i)