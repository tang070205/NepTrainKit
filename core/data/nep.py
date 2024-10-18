#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/10/18 13:26
# @Author  : 兵
# @email    : 1747193328@qq.com
from pathlib import Path

import numpy as np


import utils
from core import MessageManager
from ase.io import read as ase_read
from ase.io import write as ase_write

from .base import DataBase, NepData, NepPlotData

from .io import read_nep_out_file, read_atom_num_from_xyz


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

        # self._atoms_dataset=DataBase(ase_read(self.data_xyz_path,index=":",format="extxyz"))
        # self._atoms_dataset=DataBase(ase_read(self.data_xyz_path,index=":",format="extxyz"))
        atoms_num_list = read_atom_num_from_xyz(self.data_xyz_path)

        self._energy_dataset=NepPlotData(read_nep_out_file(self.energy_out_path),1,title="energy")

        self._force_dataset=NepPlotData(read_nep_out_file(self.force_out_path),atoms_num_list,title="force")
        self._stress_dataset=NepPlotData(read_nep_out_file(self.stress_out_path),1,title="stress")
        self._virial_dataset=NepPlotData(read_nep_out_file(self.virial_out_path),1,title="virial")

    @property
    def dataset(self):
        return [self.energy, self.stress,self.virial]
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



    def remove(self,i):
        # self._atoms_num_dataset.remove(i)
        self._energy_dataset.remove(i)
        self._force_dataset.remove(i)
        self._stress_dataset.remove(i)
        self._virial_dataset.remove(i)




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