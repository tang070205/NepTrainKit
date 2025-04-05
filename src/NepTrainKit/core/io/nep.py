#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/10/18 13:26
# @Author  : 兵
# @email    : 1747193328@qq.com

import os
import traceback


from pathlib import Path

import numpy as np
from PySide6.QtCore import QObject
from loguru import logger

from NepTrainKit.core import MessageManager, Structure, Config
from .base import NepPlotData, StructureData
from .utils import read_nep_out_file,  check_fullbatch, read_nep_in, parse_array_by_atomnum
from ..calculator import run_nep3_calculator_process


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


class ResultData(QObject):

    def __init__(self,nep_txt_path,data_xyz_path,descriptor_path):
        super().__init__()

        structures = Structure.read_multiple(data_xyz_path)

        self.descriptor_path=descriptor_path
        self.data_xyz_path=data_xyz_path
        self.nep_txt_path=nep_txt_path

        self._atoms_dataset=StructureData(structures)
        self.select_index=set()

    @property
    def dataset(self):
        return []

    @property
    def descriptor(self):
        return self._descriptor_dataset

    @property
    def num(self):
        return self._atoms_dataset.num
    @property
    def structure(self):
        return self._atoms_dataset

    def is_select(self,i):
        return i in self.select_index

    def select(self,_list):
        """
        传入一个索引列表，将索引对应的结构标记为选中状态
        这个下标是结构在train.xyz中的索引
        """
        if isinstance(_list,(int,np.int_,np.int64, np.int32,np.uint32,np.uint64)):
            _list=[_list]

        for i in _list:
            self.select_index.add(i)

    def uncheck(self,_list):
        """
        check_list 传入一个索引列表，将索引对应的结构标记为未选中状态
        这个下标是结构在train.xyz中的索引
        """
        if isinstance(_list,int):
            _list=[_list]
        for i in _list:
            if i in self.select_index:
                self.select_index.remove(i)



    def export_model_xyz(self,save_path):
        """
        导出当前结构
        :param save_path: 保存路径
        被删除的导出到export_remove_model.xyz
        被保留的导出到export_good_model.xyz
        """
        try:

            with open(Path(save_path).joinpath("export_good_model.xyz"),"w",encoding="utf8") as f:
                for structure in self._atoms_dataset.now_data:
                    structure.write(f)

            with open(Path(save_path).joinpath("export_remove_model.xyz"),"w",encoding="utf8") as f:
                for structure in self._atoms_dataset.remove_data:
                    structure.write(f)


            MessageManager.send_info_message(f"File exported to: {save_path}")
        except:
            MessageManager.send_info_message(f"An unknown error occurred while saving. The error message has been output to the log!")
            logger.error(traceback.format_exc())


    def get_atoms(self,index ):
        """根据原始索引获取原子结构对象"""
        index=self._atoms_dataset.convert_index(index)
        return self._atoms_dataset.now_data[index][0]



    def remove(self,i):

        """
        在所有的dataset中删除某个索引对应的结构
        """
        self._atoms_dataset.remove(i)
        for dataset in self.dataset:
            dataset.remove(i)
    @property
    def is_revoke(self):
        """
        判断是否有被删除的结构
        """
        return self._atoms_dataset.remove_data.size!=0
    def revoke(self):
        """
        撤销到上一次的删除
        """
        self._atoms_dataset.revoke()
        for dataset in self.dataset:
            dataset.revoke( )

    def delete_selected(self ):
        """
        删除所有selected的结构
        """
        self.remove(list(self.select_index))
        self.select_index.clear()


    def _load_descriptors(self):
        atoms_num_list=[len(structure) for structure in self.structure.now_data]

        if os.path.exists(self.descriptor_path):
            desc_array = read_nep_out_file(self.descriptor_path,dtype=np.float32)

        else:
            desc_array = np.array([])

        if desc_array.size == 0:

            desc_array = run_nep3_calculator_process(self.nep_txt_path.as_posix(), self.structure.now_data,"descriptor")
            if desc_array.size != 0:
                np.savetxt(self.descriptor_path, desc_array, fmt='%.6g')
        else:
            if desc_array.shape[0] != len(atoms_num_list):
                # 原子描述符 需要计算结构描述符
                desc_array = parse_array_by_atomnum(desc_array, atoms_num_list, map_func=np.mean, axis=0)

                pass
            else:
                # 结构描述符
                pass
        if desc_array.size != 0:
            if desc_array.shape[1] > 2:
                desc_array = pca(desc_array, 2)

        self._descriptor_dataset = NepPlotData(desc_array, title="descriptor")


class NepTrainResultData(ResultData):
    def __init__(self,
                 nep_txt_path,
                 data_xyz_path,
                 energy_out_path,
                 force_out_path,
                 stress_out_path,
                 virial_out_path,
                 descriptor_path

                 ):
        super().__init__(nep_txt_path,data_xyz_path,descriptor_path)
        self.energy_out_path = energy_out_path
        self.force_out_path = force_out_path
        self.stress_out_path = stress_out_path
        self.virial_out_path = virial_out_path




        self._load_dataset()
        self._load_descriptors()






    @property
    def dataset(self):
        # return [self.energy, self.stress,self.virial, self.descriptor]
        return [self.energy,self.force,self.stress,self.virial, self.descriptor]



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

    @classmethod

    def from_path(cls, path,model="train"):
        path = Path(path)
        dataset_path = path.joinpath(f"{model}.xyz")
        if not dataset_path.exists():
            MessageManager.send_message_box(f"{model}.xyz not found in the current working directory.")
            return None
        nep_txt_path = path.joinpath(f"nep.txt")
        if not nep_txt_path.exists():
            MessageManager.send_warning_message(f"nep.txt not found in the current working directory.")


        energy_out_path = path.joinpath(f"energy_{model}.out")
        force_out_path = path.joinpath(f"force_{model}.out")
        stress_out_path = path.joinpath(f"stress_{model}.out")
        virial_out_path = path.joinpath(f"virial_{model}.out")
        descriptor_path = path.joinpath(f"descriptor.out")

        return cls(nep_txt_path,dataset_path,energy_out_path,force_out_path,stress_out_path,virial_out_path,descriptor_path)



    def _load_dataset(self ):
        nep_in = read_nep_in(self.nep_txt_path.with_name("nep.in"))
        atoms_num_list=[len(structure) for structure in self.structure.now_data]

        if (not check_fullbatch(nep_in, len(atoms_num_list))
                or all([
                    not self.energy_out_path.exists(),
                    not self.force_out_path.exists(),
                    not self.stress_out_path.exists(),
                    not self.virial_out_path.exists()

                ])):
            nep_potentials_array, nep_forces_array, nep_virials_array = run_nep3_calculator_process(self.nep_txt_path.as_posix(),
                                                                                          self.structure.now_data,"calculate")


            try:
                energy_array = np.column_stack(
                    [nep_potentials_array / atoms_num_list, np.array([structure.per_atom_energy for structure in self.structure.now_data],dtype=np.float32)] )

                energy_array = energy_array.astype(np.float32)
                np.savetxt(self.energy_out_path, energy_array, fmt='%10.8f')

            except:
                pass

                energy_array = np.column_stack(
                    [nep_potentials_array / atoms_num_list, nep_potentials_array / atoms_num_list])

            try:

                forces_array = np.column_stack([nep_forces_array,
                                                np.vstack([structure.forces for structure in self.structure.now_data],dtype=np.float32),

                                                ])
                np.savetxt(self.force_out_path, forces_array, fmt='%10.8f')

            except:
                logger.debug(traceback.format_exc())

                forces_array = np.column_stack([nep_forces_array,
                                                nep_forces_array

                                                ])
            coefficient = (atoms_num_list / np.array([structure.volume for structure in self.structure.now_data]))[:, np.newaxis]

            try:
                virials_array = np.column_stack([nep_virials_array,
                                                 np.vstack([structure.nep_virial for structure in self.structure.now_data],dtype=np.float32),

                                                 ])

                stress_array = virials_array * coefficient * 160.21766208
                stress_array=stress_array.astype(np.float32)

                np.savetxt(self.virial_out_path, virials_array, fmt='%10.8f')
                np.savetxt(self.stress_out_path, stress_array, fmt='%10.8f')

            except:
                logger.debug(traceback.format_exc())

                virials_array = np.column_stack([nep_virials_array,
                                                 nep_virials_array

                                                 ])

                stress_array = virials_array * coefficient * 160.21766208
                stress_array=stress_array.astype(np.float32)
            # MessageManager.send_message_box("Detected that the current mode is not full batch. Please make predictions first, then load!")
            # raise ValueError("Detected that the current mode is not full batch. Please make predictions first, then load!")
        else:
            energy_array = read_nep_out_file(self.energy_out_path,dtype=np.float32)
            forces_array = read_nep_out_file(self.force_out_path,dtype=np.float32)
            virials_array = read_nep_out_file(self.virial_out_path,dtype=np.float32)
            stress_array = read_nep_out_file(self.stress_out_path,dtype=np.float32)
        # print(energy_array.dtype,forces_array.dtype,virials_array.dtype,stress_array.dtype)
        default_forces = Config.get("widget", "forces_data", "Row")
        if forces_array.size != 0 and default_forces == "Norm":

            forces_array = parse_array_by_atomnum(forces_array, atoms_num_list, map_func=np.linalg.norm, axis=0)

            self._force_dataset = NepPlotData(forces_array, title="force")
        else:
            self._force_dataset = NepPlotData(forces_array, group_list=atoms_num_list, title="force")

        self._energy_dataset = NepPlotData(energy_array, title="energy")

        if float(nep_in.get("lambda_v", 1)) != 0:
            self._stress_dataset = NepPlotData(stress_array, title="stress")

            self._virial_dataset = NepPlotData(virials_array, title="virial")
        else:
            self._stress_dataset = NepPlotData([], title="stress")

            self._virial_dataset = NepPlotData([], title="virial")



class NepPolarizabilityResultData(ResultData):
    def __init__(self,
                 nep_txt_path,
                 data_xyz_path,
                 polarizability_out_path,

        descriptor_path
                 ):
        super().__init__(nep_txt_path,data_xyz_path,descriptor_path)


        self.polarizability_out_path = polarizability_out_path


        self._load_dataset()

        self._load_descriptors()


    @property
    def dataset(self):

        return [self.polarizability_diagonal,self.polarizability_no_diagonal, self.descriptor]

    @property
    def num(self):
        return self._atoms_dataset.num
    @property
    def structure(self):
        return self._atoms_dataset

    @property
    def polarizability_diagonal(self):
        return self._polarizability_diagonal_dataset
    @property
    def polarizability_no_diagonal(self):
        return self._polarizability_no_diagonal_dataset



    @property
    def descriptor(self):
        return self._descriptor_dataset



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

        polarizability_out_path = path.joinpath(f"polarizability_{model}.out")

        descriptor_path = path.joinpath(f"descriptor.out")

        return cls(nep_txt_path, dataset_path, polarizability_out_path, descriptor_path)
    def _load_dataset(self ):
        nep_in = read_nep_in(self.nep_txt_path.with_name("nep.in"))
        atoms_num_list=np.array([len(structure) for structure in self.structure.now_data])
        if (not check_fullbatch(nep_in, len(atoms_num_list))
                or all([
                    not self.polarizability_out_path.exists(),


                ])):

            try:
                nep_polarizability_array = run_nep3_calculator_process(self.nep_txt_path.as_posix(),self.structure.now_data,"polarizability")

                nep_polarizability_array=nep_polarizability_array/(atoms_num_list[:, np.newaxis])
                polarizability_array = np.column_stack([nep_polarizability_array,
                                                np.vstack([structure.nep_polarizability for structure in self.structure.now_data]),

                                                ])


                np.savetxt(self.polarizability_out_path, polarizability_array, fmt='%10.8f')

            except:
                logger.debug(traceback.format_exc())

                polarizability_array = np.column_stack([nep_polarizability_array,
                                                nep_polarizability_array

                                                ])
        else:
            polarizability_array = read_nep_out_file(self.polarizability_out_path)

        self._polarizability_diagonal_dataset = NepPlotData(polarizability_array[:, [0,1,2,6,7,8]], title="Polar Diag")

        self._polarizability_no_diagonal_dataset = NepPlotData(polarizability_array[:, [3,4,5,9,10,11]], title="Polar NoDiag")


class NepDipoleResultData(ResultData):
    def __init__(self,
                 nep_txt_path,
                 data_xyz_path,
                 dipole_out_path,

                 descriptor_path
                 ):
        super().__init__(nep_txt_path, data_xyz_path, descriptor_path)

        self.dipole_out_path = dipole_out_path

        self._load_dataset()

        self._load_descriptors()

    @property
    def dataset(self):

        return [self.dipole , self.descriptor]

    @property
    def num(self):
        return self._atoms_dataset.num

    @property
    def structure(self):
        return self._atoms_dataset

    @property
    def dipole(self):
        return self._dipole_dataset



    @property
    def descriptor(self):
        return self._descriptor_dataset

    @classmethod
    def from_path(cls, path, model="train"):
        path = Path(path)
        dataset_path = path.joinpath(f"{model}.xyz")
        if not dataset_path.exists():
            MessageManager.send_message_box(f"{model}.xyz not found in the current working directory.")
            return None
        nep_txt_path = path.joinpath(f"nep.txt")
        if not nep_txt_path.exists():
            MessageManager.send_message_box(f"nep.txt not found in the current working directory.")
            return None

        polarizability_out_path = path.joinpath(f"dipole_{model}.out")

        descriptor_path = path.joinpath(f"descriptor.out")

        return cls(nep_txt_path, dataset_path, polarizability_out_path, descriptor_path)

    def _load_dataset(self):
        nep_in = read_nep_in(self.nep_txt_path.with_name("nep.in"))
        atoms_num_list = np.array([len(structure) for structure in self.structure.now_data])
        if (not check_fullbatch(nep_in, len(atoms_num_list))
                or all([
                    not self.dipole_out_path.exists(),

                ])):

            try:
                nep_dipole_array = run_nep3_calculator_process(self.nep_txt_path.as_posix(),
                                                                       self.structure.now_data, "dipole")

                nep_dipole_array = nep_dipole_array / (atoms_num_list[:, np.newaxis])
                dipole_array = np.column_stack([nep_dipole_array,
                                                        np.vstack([structure.nep_dipole for structure in
                                                                   self.structure.now_data]),

                                                        ])

                np.savetxt(self.dipole_out_path, dipole_array, fmt='%10.8f')

            except:
                logger.debug(traceback.format_exc())

                dipole_array = np.column_stack([nep_dipole_array,
                                                        nep_dipole_array

                                                        ])
        else:
            dipole_array = read_nep_out_file(self.dipole_out_path)

        self._dipole_dataset = NepPlotData(dipole_array,
                                                            title="dipole")

