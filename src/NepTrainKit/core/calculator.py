#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/11/21 14:22
# @Author  : 兵
# @email    : 1747193328@qq.com
import contextlib
import os

import numpy as np
from PySide6.QtCore import QObject
from NepTrainKit import utils
from NepTrainKit.core import Structure
from nep_cpu import CpuNep

class Nep3Calculator(QObject):

    def __init__(self, model_file="nep.txt"):
        super().__init__()
        if not isinstance(model_file, str):
            model_file=str(model_file,encoding="utf-8")
        with open(os.devnull, 'w') as devnull:
            with contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull):
                self.nep3 = CpuNep(model_file)
        self.element_list=self.nep3.get_element_list()
        self.type_dict = {e: i for i, e in enumerate(self.element_list)}




    def get_descriptor(self,structure:Structure):
        symbols = structure.elements
        _type = [self.type_dict[k] for k in symbols]
        _box = structure.cell.transpose(1, 0).reshape(-1).tolist()

        _position = structure.positions.transpose(1, 0).reshape(-1).tolist()

        descriptor = self.nep3.get_descriptor(_type, _box, _position)

        descriptors_per_atom = np.array(descriptor).reshape(-1, len(structure)).T

        return descriptors_per_atom
    @utils.timeit
    def get_descriptors(self,structures:list[Structure]):
        _types=[]
        _boxs=[]
        _positions=[]
        for structure in structures:
            symbols = structure.elements
            _type = [self.type_dict[k] for k in symbols]
            _box = structure.cell.transpose(1, 0).reshape(-1).tolist()

            _position = structure.positions.transpose(1, 0).reshape(-1).tolist()
            _types.append(_type)
            _boxs.append(_box)
            _positions.append(_position)

        descriptor = self.nep3.get_descriptors(_types, _boxs, _positions)

        return np.array(descriptor)


if __name__ == '__main__':
    Nep3Calculator("../nep.txt")