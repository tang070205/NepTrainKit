#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/11/21 14:45
# @Author  : 兵
# @email    : 1747193328@qq.com
import re

import numpy as np

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



class Structure:
    def __init__(self, lattice, structure_info, properties, additional_fields):
        self.properties = properties
        self.lattice = np.array(lattice).reshape((3,3))  # Optional: Lattice vectors
        self.structure_info = structure_info
        self.additional_fields = additional_fields


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
    def numbers(self):
        return [atomic_numbers[element] for element in self.elements]

    @property
    def elements(self):
        return self.structure_info['species']
    @property
    def positions(self):
        return self.structure_info['pos']


    @property
    def num_atoms(self):
        return len(self.elements)



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
        array = np.array([line.split() for line in lines[2:]])

        structure_info = {}
        index = 0
        for prop in properties:

            _info = array[:, index:index + prop["count"]]
            if prop["type"] == "S":
                _info = _info.astype(str)
            elif prop["type"] == "R":
                _info = _info.astype(float)
            else:
                pass
            if prop["count"] == 1:
                _info = _info.flatten()
            else:

                _info = _info.reshape((-1, prop["count"]))

            structure_info[prop["name"]] = _info
            index += prop["count"]

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
            value = match[1] or match[3]

            if key == "Lattice":
                lattice = list(map(float, value.split()))
            elif key == "Properties":
                # Parse Properties details
                properties = cls._parse_properties(value)
            else:
                if '"' in value:

                    additional_fields[key] = value.strip('"')  # 去掉引号
                else:
                    try:
                        additional_fields[key] = float(value)
                    except Exception as e:
                        additional_fields[key] = value
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
    def read_multiple(filename):
        """
        Read a multi-structure XYZ file and return a list of Structure objects.
        """
        structures = []
        with open(filename, 'r') as file:
            lines = file.readlines()

        i = 0
        while i < len(lines):
            num_atoms = int(lines[i].strip())
            end = i + 2 + num_atoms
            structure_lines = lines[i:end]
            structure = Structure.read(structure_lines)
            structures.append(structure)
            i = end
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
        prop_list = []

        for prop in self.properties:
            prop_list.append(self.structure_info[prop["name"]].reshape((-1, prop["count"])))
        prop_array = np.hstack(prop_list)
        np.savetxt(
            file,  # 输出到 StringIO 而不是文件
            prop_array,  # 数据
            fmt="% -5s" + "%14s" * (prop_array.shape[1] - 1),
            delimiter="       ",  # 无额外分隔符
        )
