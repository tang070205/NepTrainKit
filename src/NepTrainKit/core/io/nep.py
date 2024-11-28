#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/10/18 13:26
# @Author  : 兵
# @email    : 1747193328@qq.com
import time
import traceback
from pathlib import Path

import numpy as np

from NepTrainKit.core import MessageManager,Structure
from .base import NepPlotData, NepData, DataBase
from .utils import read_nep_out_file, read_atom_num_from_xyz,check_fullbatch


from NepTrainKit import utils
from ..calculator import Nep3Calculator
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

@utils.loghandle
class NepTrainResultData:
    def __init__(self,
                 nep_txt_path,
                 data_xyz_path,
                 energy_out_path,
                 force_out_path,
                 stress_out_path,
                 virial_out_path,

                 ):

        #这里不知道怎么展示结构  先保存下路径
        self.nep_txt_path=nep_txt_path
        self.data_xyz_path = data_xyz_path
        self.energy_out_path = energy_out_path
        self.force_out_path = force_out_path
        self.stress_out_path = stress_out_path
        self.virial_out_path = virial_out_path
        atoms_num_list = read_atom_num_from_xyz(self.data_xyz_path)






        # self._atoms_dataset=DataBase(ase_read(self.data_xyz_path,index=":",format="extxyz"))
        # self._atoms_dataset=NepData(np.arange(len(atoms_num_list)))
        structures=Structure.read_multiple(self.data_xyz_path)
        if len(structures)>=1000:
            if not check_fullbatch(self.nep_txt_path.with_name("nep.in"),len(structures)):
                MessageManager.send_message_box("检测到目前是非full batch，请先预测后再加载！")
                raise ValueError("检测到目前是非full batch，请先预测后再加载！")

        self._atoms_dataset=NepData(structures)

        self._energy_dataset=NepPlotData(read_nep_out_file(self.energy_out_path),title="energy")

        self._force_dataset=NepPlotData(read_nep_out_file(self.force_out_path),group_list=atoms_num_list,title="force")

        self._stress_dataset=NepPlotData(read_nep_out_file(self.stress_out_path),title="stress")
        self._virial_dataset=NepPlotData(read_nep_out_file(self.virial_out_path),title="virial")

        nep3 = Nep3Calculator(nep_txt_path.as_posix())
        desc_list=[nep3.get_descriptors(structure).mean(0) for structure in structures]
        desc_array=np.vstack(desc_list)
        desc_array = pca(desc_array,2)


        self._descriptor_dataset=NepPlotData(desc_array,title="descriptor")

        self.select_index=set()




    @property
    def dataset(self):
        # return [self.energy, self.stress,self.virial]
        return [self.energy,self.force,self.stress,self.virial, self.descriptor]

    @property
    def num(self):
        return self._atoms_dataset.num
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
            MessageManager.send_info_message(f"文件导出到：{save_path}")
        except:
            MessageManager.send_info_message(f"保存出现未知错误，错误信息已经输出到日志!")
            self.logger.error(traceback.format_exc())


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
            MessageManager.send_error_message(f"当前工作路径不存在{model}.xyz")
            return None
        nep_txt_path = path.joinpath(f"nep.txt")

        energy_out_path = path.joinpath(f"energy_{model}.out")
        force_out_path = path.joinpath(f"force_{model}.out")
        stress_out_path = path.joinpath(f"stress_{model}.out")
        virial_out_path = path.joinpath(f"virial_{model}.out")

        return NepTrainResultData(nep_txt_path,dataset_path,energy_out_path,force_out_path,stress_out_path,virial_out_path)