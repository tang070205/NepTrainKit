#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/11/21 14:45
# @Author  : 兵
# @email    : 1747193328@qq.com
import json
import os
import re

import numpy as np

from NepTrainKit import utils, module_path

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
with open(os.path.join(module_path, "Config/ptable.json"), "r", encoding="utf-8") as f:
    table_info = json.loads(f.read())


class Structure():
    def __init__(self, lattice, structure_info, properties, additional_fields):
        super().__init__()
        self.properties = properties
        self.lattice = np.array(lattice,dtype=np.float32).reshape((3,3))  # Optional: Lattice vectors
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
            return cls.parse_xyz(f.read())
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

        vir=np.array(self.virial.split(" "),dtype=np.float32)

        return vir[[0,4,8,1,5,6]]/self.num_atoms
    @property
    def nep_dipole(self):

        dipole=np.array(self.dipole.split(" "),dtype=np.float32)

        return dipole/self.num_atoms
    @property
    def nep_polarizability(self):
        vir = np.array(self.pol.split(" "), dtype=np.float32)

        return vir[[0,4,8,1,5,6]] / self.num_atoms


    @property
    def elements(self):
        return self.structure_info['species']
    @property
    def positions(self):
        return self.structure_info['pos']


    @property
    def num_atoms(self):
        return len(self.elements)

    def adjust_reasonable(self,coeff=0.7):
        """
        根据传入系数 对比共价半径和实际键长，
        如果实际键长小于coeff*共价半径之和，判定为不合理结构 返回False
        否则返回 True
        :param coeff: 系数
        :return:

        """
        distance_info = self.get_mini_distance_info()
        for elems, bond_length in distance_info.items():
            elem0_info = table_info[str(atomic_numbers[elems[0]])]
            elem1_info = table_info[str(atomic_numbers[elems[1]])]

            # 相邻原子距离小于共价半径之和×系数就选中
            if (elem0_info["radii"] + elem1_info["radii"]) * coeff > bond_length * 100:
                return False
        return True





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
    def parse_xyz(cls, lines):
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
                # pass
                _info=_info.astype(np.str_)
                # _info = np.array(_info,dtype=str)
            elif prop["type"] == "R":
                _info=_info.astype( np.float32)
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
        pattern = r'(\w+)=\s*"([^"]+)"|(\w+)=\s*([\S]+)'
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
    @utils.timeit
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
            structure = Structure.parse_xyz(structure_lines)
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

    def get_all_distances(self):
        return  calculate_pairwise_distances(self.cell, self.positions,False)

    def get_mini_distance_info(self):
        """
        返回原子对之间的最小距离
        """
        dist_matrix = calculate_pairwise_distances(self.cell, self.positions,False)
        symbols=self.elements
        # 提取上三角矩阵（排除对角线）
        i, j = np.triu_indices(len(self), k=1)
        # 用字典来存储每种元素对的最小键长
        bond_lengths = {}
        # 遍历所有原子对，计算每一对元素的最小键长
        for idx in range(len(i)):
            atom_i, atom_j = symbols[i[idx]], symbols[j[idx]]
            # if atom_i==atom_j:
            #     continue
            # 获取当前键长
            bond_length = dist_matrix[i[idx], j[idx]]
            # if bond_length>5:
            #     continue
            # 确保元素对按字母顺序排列，避免 Cs-Ag 和 Ag-Cs 视为不同
            element_pair = tuple(sorted([atom_i, atom_j]))
            # 如果该元素对尚未存在于字典中，初始化其最小键长
            if element_pair not in bond_lengths:
                bond_lengths[element_pair] = bond_length
            else:
                # 更新最小键长
                bond_lengths[element_pair] = min(bond_lengths[element_pair], bond_length)

        return bond_lengths
    def get_bond_pairs(self):
        """
        返回在范围内的所有键长
        """
        i, j = np.triu_indices(len(self), k=1)
        pos = np.array(self.positions)
        diff = pos[i] - pos[j]
        upper_distances = np.linalg.norm(diff, axis=1)
        covalent_radii = np.array([table_info[str(n)]["radii"] / 100 for n in self.numbers])
        radius_sum = covalent_radii[i] + covalent_radii[j]
        bond_mask = (upper_distances < radius_sum * 1.15)
        bond_pairs = [(i[k], j[k]) for k in np.where(bond_mask)[0]]
        return bond_pairs

    def get_bad_bond_pairs(self, cutoff=0.8):
        """
        根据键长阈值判断
        返回所有的非物理键长
        """
        i, j = np.triu_indices(len(self), k=1)
        distances = self.get_all_distances()
        upper_distances = distances[i, j]
        covalent_radii = np.array([table_info[str(n)]["radii"] / 100 for n in self.numbers])
        radius_sum = covalent_radii[i] + covalent_radii[j]
        bond_mask = (upper_distances < radius_sum * cutoff)

        bad_bond_pairs = [(i[k], j[k]) for k in np.where(bond_mask)[0]]
        return bad_bond_pairs
def calculate_pairwise_distances(lattice_params, atom_coords, fractional=True):
    """
    计算晶体中所有原子对之间的距离，考虑周期性边界条件

    参数:
    lattice_params: 晶格参数，3x3 numpy array 表示晶格向量 (a, b, c)
    atom_coords: 原子坐标，Nx3 numpy array
    fractional: 是否为分数坐标 (True) 或笛卡尔坐标 (False)

    返回:
    distances: NxN numpy array，所有原子对之间的距离
    """


    if fractional:
        atom_coords = np.dot(atom_coords, lattice_params)

    diff = atom_coords[np.newaxis, :, :] - atom_coords[:, np.newaxis, :]
    shifts = np.array(np.meshgrid([-1, 0, 1], [-1, 0, 1], [-1, 0, 1])).T.reshape(-1, 3)
    lattice_shifts = np.dot(shifts, lattice_params)
    all_diffs = diff[:, :, np.newaxis, :] + lattice_shifts[np.newaxis, np.newaxis, :, :]
    all_distances = np.sqrt(np.sum(all_diffs ** 2, axis=-1))
    distances = np.min(all_distances, axis=-1)
    np.fill_diagonal(distances, 0)
    return distances