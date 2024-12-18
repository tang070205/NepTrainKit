#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/10/18 13:26
# @Author  : 兵
# @email    : 1747193328@qq.com
import multiprocessing
import traceback
from functools import partial

from pathlib import Path

import numpy as np
from PySide6.QtCore import QObject
from loguru import logger

from NepTrainKit.core import MessageManager, Structure, Config
from .base import NepPlotData, StructureData
from .utils import read_nep_out_file, read_atom_num_from_xyz, check_fullbatch, read_nep_in
from ..calculator import  process_calculate,process_get_descriptors,_calculate,_get_descriptors,Nep3Calculator
import pyqtgraph.multiprocess as mp


def pca(X, k):
    # 1. 标准化数据（去均值和方差标准化）
    mean = np.mean(X, axis=0)
    X_centered = X - mean

    # 2. 计算协方差矩阵
    cov_matrix = np.cov(X_centered.T)

    # 3. 特征值分解协方差矩阵
    eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)

    # 4. 对特征值进行排序，选择前k个特征值和对应的特征向量
    sorted_indices = np.argsort(eigenvalues)[::-1]  # 从大到小排序
    top_k_eigenvectors = eigenvectors[:, sorted_indices[:k]]

    # 5. 投影到前k个主成分
    X_pca = X_centered.dot(top_k_eigenvectors)

    return X_pca





class NepTrainResultData(QObject):
    def __init__(self,
                 nep_txt_path,
                 data_xyz_path,
                 energy_out_path,
                 force_out_path,
                 stress_out_path,
                 virial_out_path,

                 ):
        super().__init__()
        #这里不知道怎么展示结构  先保存下路径
        self.nep_txt_path=nep_txt_path
        self.data_xyz_path = data_xyz_path
        self.energy_out_path = energy_out_path
        self.force_out_path = force_out_path
        self.stress_out_path = stress_out_path
        self.virial_out_path = virial_out_path

        atoms_num_list = read_atom_num_from_xyz(self.data_xyz_path)
        structures = Structure.read_multiple(self.data_xyz_path)

        self._atoms_dataset=StructureData(structures)
        nep_in= read_nep_in(self.nep_txt_path.with_name("nep.in"))

        if (not check_fullbatch(nep_in,len(structures))
                or all([
                    not self.energy_out_path.exists(),
                    not self.force_out_path.exists(),
                    not self.stress_out_path.exists(),
                    not self.virial_out_path.exists()

        ])):



                nep_potentials_array,nep_forces_array,nep_virials_array = process_calculate(self.nep_txt_path.as_posix(), structures)
                energy_array=np.column_stack([nep_potentials_array/atoms_num_list,[structure.per_atom_energy for structure in structures]])
                try:

                    forces_array=np.column_stack([nep_forces_array,
                        np.vstack([structure.forces for structure in structures]),

                        ])
                except:
                    logger.error(traceback.format_exc())

                    forces_array=np.array([])
                try:
                    virials_array = np.column_stack([nep_virials_array,
                        np.vstack([structure.nep_virial  for structure in structures]),

                        ])

                    coefficient=(atoms_num_list/np.array([structure.volume for structure in structures]))[:, np.newaxis]

                    stress_array = virials_array*coefficient*160.21766208

                except:
                    logger.error(traceback.format_exc())
                    virials_array = np.array([])
                    stress_array=np.array([])



                # MessageManager.send_message_box("Detected that the current mode is not full batch. Please make predictions first, then load!")
                # raise ValueError("Detected that the current mode is not full batch. Please make predictions first, then load!")
        else:
            energy_array=read_nep_out_file(self.energy_out_path)
            forces_array=read_nep_out_file(self.force_out_path)
            virials_array=read_nep_out_file(self.virial_out_path)
            stress_array=read_nep_out_file(self.stress_out_path)
        default_forces = Config.get("widget","forces_data","Row")
        if forces_array.size!=0 and default_forces=="Norm":
            # 使用 np.cumsum() 计算每个分组的结束索引
            split_indices = np.cumsum(atoms_num_list)[:-1]

            # 使用 np.split() 按照分组拆分数组
            split_arrays = np.split(forces_array, split_indices)


            sum_along_axis_1 = partial(np.linalg.norm, axis=0)


            # 对每个分组求和，使用 np.vectorize 进行向量化
            forces_array = np.array(list(map(sum_along_axis_1, split_arrays)))
            self._force_dataset=NepPlotData(forces_array, title="force")
        else:
            self._force_dataset=NepPlotData(forces_array,group_list=atoms_num_list, title="force")


        self._energy_dataset=NepPlotData(energy_array,title="energy")



        if float(nep_in.get("lambda_v",1)) !=0:
            self._stress_dataset = NepPlotData(stress_array, title="stress")

            self._virial_dataset = NepPlotData(virials_array,title="virial")
        else:
            self._stress_dataset = NepPlotData([], title="stress")

            self._virial_dataset = NepPlotData([],title="virial")

        desc_array=process_get_descriptors(self.nep_txt_path.as_posix(), structures)
        desc_array = pca(desc_array,2)

        # desc_array=np.array([])
        self._descriptor_dataset=NepPlotData(desc_array,title="descriptor")

        self.select_index=set()




    @property
    def dataset(self):
        # return [self.energy, self.stress,self.virial, self.descriptor]
        return [self.energy,self.force,self.stress,self.virial, self.descriptor]

    @property
    def num(self):
        return self._atoms_dataset.num
    @property
    def structure(self):
        return self._atoms_dataset

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

    @property
    def descriptor(self):
        return self._descriptor_dataset


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
            # row_model=  ase_read(self.data_xyz_path,index=":",format="extxyz")


            # result=[row_model[i] for i in self._atoms_dataset.now_data ]
            # remove=[row_model[i] for i in self._atoms_dataset.remove_data ]
            with open(Path(save_path).joinpath("export_good_model.xyz"),"w",encoding="utf8") as f:
                for structure in self._atoms_dataset.now_data:
                    structure.write(f)

            with open(Path(save_path).joinpath("export_remove_model.xyz"),"w",encoding="utf8") as f:
                for structure in self._atoms_dataset.remove_data:
                    structure.write(f)

            # ase_write(Path(save_path).joinpath("export_good_model.xyz") ,result,append=True)
            # ase_write(Path(save_path).joinpath("export_remove_model.xyz") ,remove,append=True)
            MessageManager.send_info_message(f"File exported to: {save_path}")
        except:
            MessageManager.send_info_message(f"An unknown error occurred while saving. The error message has been output to the log!")
            logger.error(traceback.format_exc())


    def get_atoms(self,index ):

        index=self._atoms_dataset.convert_index(index)
        return self._atoms_dataset.now_data[index][0]



    def remove(self,i):


        self._atoms_dataset.remove(i)
        for dataset in self.dataset:
            dataset.remove(i)
    @property
    def is_revoke(self):
        return self._atoms_dataset.remove_data.size!=0
    def revoke(self):
        self._atoms_dataset.revoke()
        for dataset in self.dataset:
            dataset.revoke( )

    def delete_selected(self ):

        self.remove(list(self.select_index))
        self.select_index.clear()
    @classmethod
    def from_path(cls, path,model="train"):
        path = Path(path)
        dataset_path = path.joinpath(f"{model}.xyz")
        if not dataset_path.exists():
            MessageManager.send_message_box(f"{model}.xyz not found in the current working directory.")
            return None
        nep_txt_path = path.joinpath(f"nep.txt")
        if not nep_txt_path.exists():
            MessageManager.send_message_box(f"nep.txt not found in the current working directory.")
            return None

        energy_out_path = path.joinpath(f"energy_{model}.out")
        force_out_path = path.joinpath(f"force_{model}.out")
        stress_out_path = path.joinpath(f"stress_{model}.out")
        virial_out_path = path.joinpath(f"virial_{model}.out")

        return NepTrainResultData(nep_txt_path,dataset_path,energy_out_path,force_out_path,stress_out_path,virial_out_path)