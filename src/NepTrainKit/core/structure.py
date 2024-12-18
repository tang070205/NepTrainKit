#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/11/21 14:45
# @Author  : 兵
# @email    : 1747193328@qq.com
import multiprocessing
import re
import threading
import time
from concurrent.futures import ProcessPoolExecutor,ThreadPoolExecutor

import numpy as np
from PySide6.QtCore import QThread, QObject
from PySide6.QtWidgets import QApplication

from NepTrainKit import utils
from NepTrainKit.utils import timeit

atomic_numbers={ 'H': 1, 'He': 2, 'Li': 3, 'Be': 4,
                 'B': 5, 'C': 6, 'N': 7, 'O': 8,
                 'F': 9, 'Ne': 10, 'Na': 11, 'Mg': 12,
                 'Al': 13, 'Si': 14, 'P': 15, 'S': 16,
                 'Cl': 17, 'Ar': 18, 'K': 19, 'Ca': 20,
                 'Sc': 21, 'Ti': 22, 'V': 23, 'Cr': 24,
                 'Mn': 25, 'Fe': 26, 'Co': 27, 'Ni': 28,
                 'Cu': 29, 'Zn': 30, 'Ga': 31, 'Ge': 32,
                 'As': 33, 'Se': 34, 'Br': 35, 'Kr': 36,
                 'Rb': 37, 'Sr': 38, 'Y': 39, 'Zr': 40,
                 'Nb': 41, 'Mo': 42, 'Tc': 43, 'Ru': 44,
                 'Rh': 45, 'Pd': 46, 'Ag': 47, 'Cd': 48,
                 'In': 49, 'Sn': 50, 'Sb': 51, 'Te': 52, 'I': 53,
                 'Xe': 54, 'Cs': 55, 'Ba': 56, 'La': 57, 'Ce': 58,
                 'Pr': 59, 'Nd': 60, 'Pm': 61, 'Sm': 62, 'Eu': 63,
                 'Gd': 64, 'Tb': 65, 'Dy': 66, 'Ho': 67, 'Er': 68,
                 'Tm': 69, 'Yb': 70, 'Lu': 71, 'Hf': 72, 'Ta': 73,
                 'W': 74, 'Re': 75, 'Os': 76, 'Ir': 77, 'Pt': 78,
                 'Au': 79, 'Hg': 80, 'Tl': 81, 'Pb': 82, 'Bi': 83,
                 'Po': 84, 'At': 85, 'Rn': 86, 'Fr': 87, 'Ra': 88,
                 'Ac': 89, 'Th': 90, 'Pa': 91, 'U': 92, 'Np': 93,
                 'Pu': 94, 'Am': 95, 'Cm': 96, 'Bk': 97, 'Cf': 98,
                 'Es': 99, 'Fm': 100, 'Md': 101, 'No': 102, 'Lr': 103,
                 'Rf': 104, 'Db': 105, 'Sg': 106, 'Bh': 107, 'Hs': 108,
                 'Mt': 109, 'Ds': 110, 'Rg': 111, 'Cn': 112, 'Nh': 113,
                 'Fl': 114, 'Mc': 115, 'Lv': 116, 'Ts': 117, 'Og': 118}



class Structure():
    def __init__(self, lattice, structure_info, properties, additional_fields):
        super().__init__()
        self.properties = properties
        self.lattice = np.array(lattice).reshape((3,3))  # Optional: Lattice vectors
        self.structure_info = structure_info
        self.additional_fields = additional_fields
        if "Config_type" not in self.additional_fields.keys():
            self.additional_fields["Config_type"] = ""
        if "forces" in self.structure_info.keys():
            self.force_label="forces"
        else:
            self.force_label = "force"

    def __len__(self):
        return len(self.elements)

    @classmethod
    def read_xyz(cls, filename):
        with open(filename, 'r') as f:
            return cls.read(f.read())
    @property
    def cell(self):
        return self.lattice
    @property
    def volume(self):
        return np.abs(np.linalg.det(self.lattice))

    @property
    def numbers(self):
        return [atomic_numbers[element] for element in self.elements]

    @property
    def per_atom_energy(self):


        return self.additional_fields[ "energy"]/self.num_atoms
    @property
    def forces(self):
        return self.structure_info[self.force_label]


    @property
    def nep_virial(self):

        vir=np.array(self.virial.split(" "),dtype=float)

        return vir[[0,4,8,1,5,6]]/self.num_atoms





    @property
    def elements(self):
        return self.structure_info['species']
    @property
    def positions(self):
        return self.structure_info['pos']


    @property
    def num_atoms(self):
        return len(self.elements)
    # 在序列化时使用 __getstate__ 进行处理
    def __getstate__(self):
        # 返回对象的状态字典，这里可以控制哪些属性需要序列化

        state = self.__dict__.copy()

        return state

    # 反序列化时使用 __setstate__
    def __setstate__(self, state):
        self.__dict__.update(state)

    def __getattr__(self, item):

        if item in self.additional_fields.keys():
            return self.additional_fields[item]
        elif item in self.structure_info.keys():
            return self.structure_info[item]
        else:
            raise AttributeError

    @classmethod
    def read(cls, lines):
        """
        Parse a single structure from a list of lines.
        """
        if isinstance(lines, str):
            lines = lines.strip().split('\n')
        # Read the number of atoms (1st line)
        num_atoms = int(lines[0].strip())

        # Parse the second line (global properties)
        global_properties = lines[1].strip()
        lattice, properties, additional_fields = cls._parse_global_properties(global_properties)
        # array = np.array([line.split() for line in lines[2:]],dtype=str)
        # array =  [line.split() for line in lines[2:]]

        array = np.array([line.split() for line in lines[2:]],dtype=object )
        # print(array.shape)
        # array = np.array([line.split() for line in lines[2:]])

        # print(array.shape)
        structure_info = {}
        index = 0

        for prop in properties:

            _info = array[:, index:index + prop["count"]]
            #
            # _info =[row[index:index + prop["count"]] for row in array]

            if prop["type"] == "S":
                pass
                # _info=_info.astype(np.str_)
                # _info = np.array(_info,dtype=str)
            elif prop["type"] == "R":
                _info=_info.astype(float)
                 # _info = np.array(_info,dtype=float)
            else:
                pass
            if prop["count"] == 1:
                _info = _info.flatten()
            else:

                _info = _info.reshape((-1, prop["count"]))

            structure_info[prop["name"]] = _info
            index += prop["count"]

        # return
        return cls(lattice, structure_info, properties, additional_fields)

    @classmethod
    def _parse_global_properties(cls, line):
        """
        Parse global properties from the second line of an XYZ block.
        """
        pattern = r'(\w+)="([^"]+)"|(\w+)=([\S]+)'
        matches = re.findall(pattern, line)
        properties = []
        lattice = None
        additional_fields = {}

        for match in matches:
            key = match[0] or match[2]
            # key=key.capitalize()
            value = match[1] or match[3]

            if key.capitalize()  == "Lattice":
                lattice = list(map(float, value.split()))
            elif key.capitalize()  == "Properties":
                # Parse Properties details
                properties = cls._parse_properties(value)
            else:

                if '"' in value:

                    value = value.strip('"')  # 去掉引号
                else:
                    try:
                        value = float(value)
                    except Exception as e:
                        value = value
                if key == "config_type" or key == "Config_type":
                    # 这里是为了后面的Config搜索做统一
                    key = "Config_type"
                    value=str(value)
                if key.lower() in ("energy", "pbc","virial"):
                    key=key.lower()
                additional_fields[key] = value
                # print(additional_fields)
        return lattice, properties, additional_fields

    @staticmethod
    def _parse_properties(properties_str):
        """
        Parse `Properties` attribute string to extract atom-specific fields.
        """
        tokens = properties_str.split(":")
        parsed_properties = []
        i = 0
        while i < len(tokens):
            name = tokens[i]
            dtype = tokens[i + 1]
            count = int(tokens[i + 2]) if i + 2 < len(tokens) else 1
            parsed_properties.append({"name": name, "type": dtype, "count": count})
            i += 3
        return parsed_properties

    @staticmethod
    # @utils.timeit
    def read_multiple(filename ):
        """
        Read a multi-structure XYZ file and return a list of Structure objects.
        """

        # data_to_process = []
        structures = []

        with open(filename, 'r') as file:
            lines = file.read().splitlines()

        i = 0
        while i < len(lines):
            num_atoms = lines[i].strip()

            if not num_atoms:
                i += 1
                continue
            num_atoms = int(num_atoms)
            end = i + 2 + num_atoms
            structure_lines = lines[i:end]
            # data_to_process.append(structure_lines)
            structure = Structure.read(structure_lines)
            structures.append(structure)
            i = end
        # with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
            # map 函数并行处理每个结构的读取
            # structures = pool.map(Structure.read, data_to_process)

        return structures

    def write(self, file):
        """
        Write the current structure to an XYZ file.
        """

        # Write number of atoms
        file.write(f"{self.num_atoms}\n")

        # Write global properties
        global_line = []
        if self.lattice.size!=0:
            global_line.append(f'Lattice="' + ' '.join(f"{x}" for x in self.cell.flatten()) + '"')

        props = ":".join(f"{p['name']}:{p['type']}:{p['count']}" for p in self.properties)
        global_line.append(f"Properties={props}")
        for key, value in self.additional_fields.items():

            if isinstance(value, (float, int)):
                global_line.append(f"{key}={value}")

            else:
                global_line.append(f'{key}="{value}"')
        file.write(" ".join(global_line) + "\n")





        for row in range(self.num_atoms):
            line = ""
            for prop  in self.properties :
                if prop["count"] == 1:
                    values=[self.structure_info[prop["name"]][row]]
                else:
                    values=self.structure_info[prop["name"]][row,:]



                if prop["type"] == 'S':  # 字符串类型
                    line += " ".join([f"{x }" for x in values]) + " "

                elif prop["type"] == 'R':  # 浮点数类型
                    line += " ".join([f"{x:.10g}" for x in values]) + " "
            file.write(line.strip() + "\n")