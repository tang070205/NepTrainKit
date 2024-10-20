#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/10/18 13:26
# @Author  : 兵
# @email    : 1747193328@qq.com
import traceback
from pathlib import Path

import numpy as np

from core import MessageManager
from .base import NepPlotData, NepData, DataBase
from .io import read_nep_out_file, read_atom_num_from_xyz
from ase.io import read as ase_read
from ase.io import write as ase_write
import utils



@utils.loghandle
class NepTrainResultData:
    def __init__(self,
                 data_xyz_path,
                 energy_out_path,
                 force_out_path,
                 stress_out_path,
                 virial_out_path,

                 ):

        #这里不知道怎么展示结构  先保存下路径
        self.data_xyz_path = data_xyz_path
        self.energy_out_path = energy_out_path
        self.force_out_path = force_out_path
        self.stress_out_path = stress_out_path
        self.virial_out_path = virial_out_path
        atoms_num_list = read_atom_num_from_xyz(self.data_xyz_path)

        # self._atoms_dataset=DataBase(ase_read(self.data_xyz_path,index=":",format="extxyz"))
        self._atoms_dataset=DataBase(np.arange(len(atoms_num_list)))

        self._energy_dataset=NepPlotData(read_nep_out_file(self.energy_out_path),title="energy")

        self._force_dataset=NepPlotData(read_nep_out_file(self.force_out_path),group_list=atoms_num_list,title="force")
        self._stress_dataset=NepPlotData(read_nep_out_file(self.stress_out_path),title="stress")
        self._virial_dataset=NepPlotData(read_nep_out_file(self.virial_out_path),title="virial")

        self.select_index=set()


    @property
    def dataset(self):
        # return [self.energy, self.stress,self.virial]
        return [self.energy,self.force,self.stress,self.virial]

    @property
    def num(self):
        return self._energy_dataset.num
    @property
    def energy(self):
        return self._energy_dataset

    @property
    def force(self):
        return self._force_dataset

    @property
    def stress(self):
        return self._stress_dataset

    @property
    def virial(self):
        return self._virial_dataset


    def is_select(self,i):
        return i in self.select_index

    def select(self,_list):
        if isinstance(_list,int):
            _list=[_list]

        for i in _list:
            self.select_index.add(i)

    def uncheck(self,_list):
        if isinstance(_list,int):
            _list=[_list]
        for i in _list:
            if i in self.select_index:
                self.select_index.remove(i)



    def export_model_xyz(self,save_path):
        try:
            row_model=  ase_read(self.data_xyz_path,index=":",format="extxyz")


            result=[row_model[i] for i in self._atoms_dataset.now_data ]
            remove=[row_model[i] for i in self._atoms_dataset.remove_data ]



            ase_write(Path(save_path).joinpath("export_good_model.xyz") ,result,append=True)
            ase_write(Path(save_path).joinpath("export_remove_model.xyz") ,remove,append=True)
            MessageManager.send_info_message(f"文件导出到：{save_path}")
        except:
            MessageManager.send_info_message(f"保存出现未知错误，错误信息已经输出到日志!")
            self.logger.error(traceback.format_exc())

    def remove(self,i):
        # self._atoms_num_dataset.remove(i)

        self._atoms_dataset.remove(i)
        for dataset in self.dataset:
            dataset.remove(i)

    def delete_selected(self ):
        # for i in self.select_index:
        self.remove(list(self.select_index))

    @classmethod
    def from_path(cls, path,model="train"):
        path = Path(path)
        dataset_path = path.joinpath(f"{model}.xyz")
        if not dataset_path.exists():
            MessageManager.send_error_message(f"当前工作路径不存在{model}.xyz")
            return None
        energy_out_path = path.joinpath(f"energy_{model}.out")
        force_out_path = path.joinpath(f"force_{model}.out")
        stress_out_path = path.joinpath(f"stress_{model}.out")
        virial_out_path = path.joinpath(f"virial_{model}.out")

        return NepTrainResultData(dataset_path,energy_out_path,force_out_path,stress_out_path,virial_out_path)