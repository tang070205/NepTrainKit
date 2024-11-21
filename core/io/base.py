#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/10/18 15:31
# @Author  : 兵
# @email    : 1747193328@qq.com
from functools import cached_property

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush


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
        shape=list(self.now_data.shape)
        shape[0]=0
        self.remove_data = np.empty( tuple(shape), dtype=self.now_data.dtype)


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
            self.remove_data = np.append(self.remove_data, datas,axis=0)
            self.remove_num.append(len(i))

    def __getitem__(self, item):
        return self.now_data[item]

    def revoke(self):
        if self.remove_num:
            last_remove_num=self.remove_num.pop(-1)


            self.now_data = np.append(self.now_data, self.remove_data[-last_remove_num: ],axis=0)
            self.remove_data = np.delete(self.remove_data, np.s_[-last_remove_num:], axis=0)


class NepData:
    def __init__(self,data_list,group_list=1, **kwargs ):
        if isinstance(data_list,(list )):
            data_list=np.array(data_list)

        self.data = DataBase(data_list )
        if isinstance(group_list,int):

            group = np.arange(data_list.shape[0])

            self.group_array=DataBase(group)
        else:
            group = np.arange(len(group_list))

            self.group_array=DataBase(group.repeat(group_list))

        for key,value in kwargs.items():
            setattr(self,key,value)
    @property
    def num(self):
        return self.data.num
    @cached_property
    def cols(self):
        if self.now_data.shape[0]==0:
            #数据为0
            return 0
        index = self.now_data.shape[1] // 2
        return index
    @property
    def now_data(self):
        return self.data.now_data

    @property
    def remove_data(self):
        return self.data.remove_data

    def convert_index(self,index_list):
        if isinstance(index_list,int):
            index_list=[index_list]
        return np.where(np.isin(self.group_array.now_data,index_list))[0]



    def remove(self,remove_index):
        """
        这里根据权重添加一层 根据权重 计算下实际删除的索引坐标
        :param i:
        :return:
        """
        remove_indices=self.convert_index(remove_index)
        # print(self.title,remove_indices)
        self.data.remove(remove_indices)
        self.group_array.remove(remove_indices)

    def revoke(self):
        self.data.revoke()
        self.group_array.revoke()



class NepPlotData(NepData):

    def __init__(self,data_list,**kwargs ):
        super().__init__(data_list,**kwargs )

        self.__color1=QBrush(Qt.GlobalColor.blue)
        self.__selected_color=QBrush(Qt.GlobalColor.red)


    @property
    def colors(self):
        structure_index=self.structure_index
        colors = np.full(structure_index.shape[0], self.__color1)  # 初始颜色为蓝色
        # print(colors)
        return colors
    @property
    def selected_color(self):
        return self.__selected_color
    @property
    def normal_color(self):
        return self.__color1
    @property
    def x(self):
        if self.cols==0:
            return self.now_data

        return self.now_data[ : ,self.cols:].flatten()
    @property
    def y(self):
        if self.cols==0:
            return self.now_data
        return self.now_data[ : , :self.cols].flatten()
    @property
    def structure_index(self):
        return self.group_array[ : ].repeat(self.cols)






