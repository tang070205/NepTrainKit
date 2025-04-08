#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2025/4/6 13:21
# @Author  : 兵
# @email    : 1747193328@qq.com
import time
from typing import List, Tuple
import sobol

import numpy as np
from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QGridLayout, QFrame, QWidget

from qfluentwidgets import ComboBox, BodyLabel, RadioButton, SplitToolButton, RoundMenu, PrimaryDropDownToolButton, \
    PrimaryDropDownPushButton, CommandBar, Action,CheckBox

from NepTrainKit.core.custom_widget import MakeDataCard, SpinBoxUnitInputFrame
from NepTrainKit import utils
from NepTrainKit.core.types import CardName

class ConsoleWidget(QWidget):
    """
控制台"""
    newCardSignal = Signal(str)  # 定义一个信号，用于通知上层组件新增卡片
    stopSignal = Signal()
    runSignal = Signal( )
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setObjectName("ConsoleWidget")
        self.setMinimumHeight(50)
        self.init_ui()
    def init_ui(self):
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setObjectName("console_gridLayout")
        self.setting_command =CommandBar(self)


        self.new_card_button = PrimaryDropDownPushButton(QIcon(":/images/src/images/copy_figure.svg"),
                                                         "Add new card",self)
        self.new_card_button.setMaximumWidth(200 )
        self.new_card_button.setObjectName("new_card_button")
        self.menu = RoundMenu(parent=self)
        self.menu.addAction(QAction(QIcon(r":/images/src/images/group.svg"), CardName.group))
        self.menu.addSeparator()
        self.menu.addAction(QAction(QIcon(r":/images/src/images/supercell.svg"),CardName.superCell))
        self.menu.addAction(QAction(QIcon(r":/images/src/images/perturb.svg"), CardName.perturb))
        self.menu.addAction(QAction(QIcon(r":/images/src/images/scaling.svg"), CardName.scaling))
        self.menu.addAction(QAction(QIcon(r":/images/src/images/defect.svg"), CardName.vacancy_defect))
        self.menu.triggered.connect(self.menu_clicked)
        self.new_card_button.setMenu(self.menu)
        self.setting_command.addWidget(self.new_card_button)

        self.setting_command.addSeparator()
        self.setting_command.addAction(Action(QIcon(r":/images/src/images/run.svg"), 'Run', triggered=self.run ))
        self.setting_command.addAction(Action(QIcon(r":/images/src/images/stop.svg"), 'Stop', triggered=self.stop ))



        self.gridLayout.addWidget(self.setting_command, 0, 0, 1, 1)

    def menu_clicked(self,action):


        self.newCardSignal.emit(action.text())

    def run(self,*args,**kwargs):
        self.runSignal.emit()
    def stop(self,*args,**kwargs):
        self.stopSignal.emit()
class SuperCellCard(MakeDataCard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Make Supercell")

        self.init_ui()

    def init_ui(self):
        self.setObjectName("super_cell_card_widget")


        self.behavior_type_combo=ComboBox(self.setting_widget)
        self.behavior_type_combo.addItem("Maximum")
        self.behavior_type_combo.addItem("Iteration")
        self.combo_label=BodyLabel("behavior:",self.setting_widget)

        self.super_scale_radio_button = RadioButton("super scale",self.setting_widget)
        self.super_scale_radio_button.setChecked(True)
        self.super_scale_condition_frame = SpinBoxUnitInputFrame(self)
        self.super_scale_condition_frame.set_input("",3)
        self.super_scale_condition_frame.setRange(1,100)

        self.super_cell_radio_button = RadioButton("super cell",self.setting_widget)
        self.super_cell_condition_frame = SpinBoxUnitInputFrame(self)
        self.super_cell_condition_frame.set_input("Å",3)
        self.super_cell_condition_frame.setRange(1,100)


        self.max_atoms_condition_frame = SpinBoxUnitInputFrame(self)
        self.max_atoms_condition_frame.set_input("unit",1)
        self.max_atoms_condition_frame.setRange(1,10000)

        self.max_atoms_radio_button = RadioButton("Max atoms",self.setting_widget)


        self.settingLayout.addWidget(self.combo_label,0, 0,1, 1)
        self.settingLayout.addWidget(self.behavior_type_combo,0, 1, 1, 2)
        self.settingLayout.addWidget(self.super_scale_radio_button, 1, 0, 1, 1)
        self.settingLayout.addWidget(self.super_scale_condition_frame, 1, 1, 1, 2)
        self.settingLayout.addWidget(self.super_cell_radio_button, 2, 0, 1, 1)
        self.settingLayout.addWidget(self.super_cell_condition_frame, 2, 1, 1, 2)
        self.settingLayout.addWidget(self.max_atoms_radio_button, 3, 0, 1, 1)
        self.settingLayout.addWidget(self.max_atoms_condition_frame, 3, 1, 1, 2)






    def _get_scale_factors(self) -> List[Tuple[int, int, int]]:
        """从 super_scale_condition_frame 获取扩包比例"""
        na, nb, nc = self.super_scale_condition_frame.get_input_value()
        return [(na, nb, nc)]

    def _get_max_cell_factors(self, structure) -> List[Tuple[int, int, int]]:
        """根据最大晶格常数计算扩包比例"""
        max_a, max_b, max_c = self.super_cell_condition_frame.get_input_value()
        lattice = structure.lattice

        # 计算晶格向量长度
        a_len = np.linalg.norm(lattice[0])
        b_len = np.linalg.norm(lattice[1])
        c_len = np.linalg.norm(lattice[2])

        # 计算最大倍数并确保至少为 1
        na = max(int(max_a / a_len) if a_len > 0 else 0, 1)
        nb = max(int(max_b / b_len) if b_len > 0 else 0, 1)
        nc = max(int(max_c / c_len) if c_len > 0 else 0, 1)

        # 调整倍数以不超过最大值
        na = na - 1 if na * a_len > max_a else na
        nb = nb - 1 if nb * b_len > max_b else nb
        nc = nc - 1 if nc * c_len > max_c else nc

        # 确保最小值为 1
        return [(max(na, 1), max(nb, 1), max(nc, 1))]


    def _get_max_atoms_factors(self, structure) -> List[Tuple[int, int, int]]:
        """根据最大原子数计算所有可能的扩包比例"""
        max_atoms = self.max_atoms_condition_frame.get_input_value()[0]
        num_atoms_orig = structure.num_atoms



        # 估算最大可能倍数
        max_n = int(max_atoms / num_atoms_orig)
        max_n_a = max_n_b = max_n_c = max(max_n, 1)

        # 枚举所有可能的扩包比例
        expansion_factors = []
        for na in range(1, max_n_a + 1):
            for nb in range(1, max_n_b + 1):
                for nc in range(1, max_n_c + 1):
                    total_atoms = num_atoms_orig * na * nb * nc
                    if total_atoms <= max_atoms:
                        expansion_factors.append((na, nb, nc))
                    else:
                        break

        # 按总原子数排序
        expansion_factors.sort(key=lambda x: num_atoms_orig * x[0] * x[1] * x[2])
        if len(expansion_factors)==0:
            return [(1, 1, 1)]

        return expansion_factors

    def _generate_structures(self, structure, expansion_factors, super_cell_type) :
        """根据超胞类型和扩包比例生成结构列表"""
        structure_list = []

        if super_cell_type == 0:  # 最大扩包
            na, nb, nc = expansion_factors[-1]  # 取最大的扩包比例

            if na == 1 and nb == 1 and nc == 1:  # 只有一个扩包


                return [structure]  # 直接返回原始结构
            supercell = structure.supercell([na, nb, nc])
            structure_list.append(supercell)

        elif super_cell_type == 1:  # 随机组合或所有组合
            if self.max_atoms_radio_button.isChecked():
                # 对于 max_atoms，返回所有可能的扩包
                for na, nb, nc in expansion_factors:


                    if na==1 and nb==1 and nc==1:  # 只有一个扩包
                        supercell=structure


                    else:

                        supercell = structure.supercell([na, nb, nc])
                    structure_list.append(supercell)
            else:
                # 对于 scale 或 max_cell，枚举所有子组合
                na, nb, nc = expansion_factors[0]
                for i in range(1, na + 1):
                    for j in range(1, nb + 1):
                        for k in range(1, nc + 1):

                            if na == 1 and nb == 1 and nc == 1:  # 只有一个扩包
                                supercell = structure


                            else:
                                supercell = structure.supercell((i, j, k))

                            structure_list.append(supercell)

        # super_cell_type == 2 的情况未实现，保持为空
        return structure_list
    def process_structure(self,structure):
        # time.sleep(0.2)


        super_cell_type = self.behavior_type_combo.currentIndex()

        # 根据选择的扩包方式获取扩包参数
        if self.super_scale_radio_button.isChecked():
            expansion_factors = self._get_scale_factors()
        elif self.super_cell_radio_button.isChecked():
            expansion_factors = self._get_max_cell_factors(structure)
        elif self.max_atoms_radio_button.isChecked():
            expansion_factors = self._get_max_atoms_factors(structure)
        else:
            expansion_factors = [(1, 1, 1)]  # 默认情况

        # 根据超胞类型生成结构
        structure_list = self._generate_structures(structure, expansion_factors, super_cell_type)
        return structure_list

    def to_dict(self):
        data_dict = {}
        data_dict['class']="SuperCellCard"
        data_dict['name'] =  CardName.superCell
        data_dict["check_state"]=self.check_state

        data_dict['super_cell_type'] = self.behavior_type_combo.currentIndex()
        data_dict['super_scale_radio_button'] = self.super_scale_radio_button.isChecked()
        data_dict['super_scale_condition'] = self.super_scale_condition_frame.get_input_value()
        data_dict['super_cell_radio_button'] = self.super_cell_radio_button.isChecked()
        data_dict['super_cell_condition'] = self.super_cell_condition_frame.get_input_value()
        data_dict['max_atoms_radio_button'] = self.max_atoms_radio_button.isChecked()
        data_dict['max_atoms_condition'] = self.max_atoms_condition_frame.get_input_value()
        return data_dict
    def from_dict(self, data_dict):
        self.state_checkbox.setChecked(data_dict['check_state'])

        self.behavior_type_combo.setCurrentIndex(data_dict['super_cell_type'])
        self.super_scale_radio_button.setChecked(data_dict['super_scale_radio_button'])
        self.super_scale_condition_frame.set_input_value(data_dict['super_scale_condition'])
        self.super_cell_radio_button.setChecked(data_dict['super_cell_radio_button'])
        self.super_cell_condition_frame.set_input_value(data_dict['super_cell_condition'])
        self.max_atoms_radio_button.setChecked(data_dict['max_atoms_radio_button'])
        self.max_atoms_condition_frame.set_input_value(data_dict['max_atoms_condition'])



class VacancyDefectCard(MakeDataCard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Make Vacancy Defect")
        self.init_ui()

    def init_ui(self):
        self.setObjectName("vacancy_defect_card_widget")

        self.engine_label=BodyLabel("Random engine:",self.setting_widget)
        self.engine_type_combo=ComboBox(self.setting_widget)
        self.engine_type_combo.addItem("Sobol")
        self.engine_type_combo.addItem("Uniform")

        self.num_radio_button = RadioButton("num",self.setting_widget)
        self.num_radio_button.setChecked(True)
        self.num_condition_frame = SpinBoxUnitInputFrame(self)
        self.num_condition_frame.set_input("unit",1)
        self.num_condition_frame.setRange(1,10000)

        self.concentration_radio_button = RadioButton("concentration",self.setting_widget)
        self.concentration_condition_frame = SpinBoxUnitInputFrame(self)
        self.concentration_condition_frame.set_input("",1,"float")
        self.concentration_condition_frame.setRange(0,1)


        self.max_atoms_condition_frame = SpinBoxUnitInputFrame(self)
        self.max_atoms_condition_frame.set_input("unit",1)
        self.max_atoms_condition_frame.setRange(1,10000)

        self.max_atoms_label= BodyLabel("Max atoms",self.setting_widget)


        self.settingLayout.addWidget(self.engine_label,0, 0,1, 1)
        self.settingLayout.addWidget(self.engine_type_combo,0, 1, 1, 2)
        self.settingLayout.addWidget(self.num_radio_button, 1, 0, 1, 1)
        self.settingLayout.addWidget(self.num_condition_frame, 1, 1, 1, 2)
        self.settingLayout.addWidget(self.concentration_radio_button, 2, 0, 1, 1)
        self.settingLayout.addWidget(self.concentration_condition_frame, 2, 1, 1, 2)
        self.settingLayout.addWidget(self.max_atoms_label, 3, 0, 1, 1)
        self.settingLayout.addWidget(self.max_atoms_condition_frame, 3, 1, 1, 2)
    def process_structure(self,structure):
        structure_list = []
        engine_type = self.engine_type_combo.currentIndex()
        concentration = self.concentration_condition_frame.get_input_value()[0]

        defect_num = self.num_condition_frame.get_input_value()[0]

        max_num = self.max_atoms_condition_frame.get_input_value()[0]

        n_atoms = len(structure)
        if self.concentration_radio_button.isChecked():
            max_defects = int(concentration * n_atoms)
        else:
            max_defects =  defect_num  # 固定数量
        if max_defects ==n_atoms:
            max_defects=max_defects-1


        orig_positions = structure.positions
        orig_elements = structure.elements

        if engine_type == 0:
            # 为数量和位置分配维度：1 维用于数量，n_atoms 维用于位置
            sobol_seq = sobol.sample(dimension=n_atoms + 1, n_points=max_num)

        else:
            # Uniform 模式下分开处理
            defect_counts = np.random.randint(1, max_defects + 1, max_num)


        for i in range(max_num):
            new_struct =structure.copy()

            # 确定当前结构的缺陷数量
            if engine_type == 0:

                target_defects = 1 + int(sobol_seq[i, 0] * max_defects)  # [0, 1] -> [1, max_defects]
                target_defects = min(target_defects, max_defects)  # 确保不超过 max_defects
                # 使用 Sobol 第 0 维控制数量
                # target_defects = int(sobol_seq[i, 0] * (max_defects + 1))  # [0, 1] 映射到 [0, max_defects]
                # 使用剩余维度控制位置
                position_scores = sobol_seq[i, 1:]
            else:
                target_defects = defect_counts[i]

            if target_defects == 0:
                structure_list.append(structure)
                continue
            if engine_type == 0:
                sorted_indices = np.argsort(position_scores)
                defect_indices = sorted_indices[:target_defects]
            else:

                defect_indices = np.random.choice(n_atoms, target_defects, replace=False)



            # 创建空位
            mask = np.ones(n_atoms, dtype=bool)
            mask[defect_indices] = False
            n_vacancies = np.sum(~mask)
            new_positions = orig_positions[mask]
            new_elements = orig_elements[mask]

            # 更新结构
            new_struct.structure_info['pos'] = new_positions
            new_struct.structure_info['species'] = new_elements
            new_struct.additional_fields["Config_type"] = structure.additional_fields["Config_type"] +f"Vacancy Defect {i} (num={n_vacancies}) "
            if structure.force_label in new_struct.structure_info:
                new_struct.structure_info[structure.force_label] = new_struct.structure_info[structure.force_label][mask]
            structure_list.append(new_struct)

        return structure_list

    def to_dict(self):
        data_dict = {}
        data_dict['class']="VacancyDefectCard"
        data_dict['name'] =  CardName.vacancy_defect
        data_dict["check_state"]=self.check_state
        data_dict['engine_type'] = self.engine_type_combo.currentIndex()
        data_dict['num_condition'] = self.num_condition_frame.get_input_value()
        data_dict['concentration_condition'] = self.concentration_condition_frame.get_input_value()
        data_dict['max_atoms_condition'] = self.max_atoms_condition_frame.get_input_value()

        return data_dict
    def from_dict(self, data_dict):
        self.state_checkbox.setChecked(data_dict['check_state'])
        self.engine_type_combo.setCurrentIndex(data_dict['engine_type'])
        self.num_condition_frame.set_input_value(data_dict['num_condition'])
        self.concentration_condition_frame.set_input_value(data_dict['concentration_condition'])
        self.max_atoms_condition_frame.set_input_value(data_dict['max_atoms_condition'])
        pass

class PerturbCard(MakeDataCard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Make Perturb")
        self.init_ui()

    def init_ui(self):
        self.setObjectName("perturb_card_widget")
        self.engine_label=BodyLabel("Random engine:",self.setting_widget)
        self.engine_type_combo=ComboBox(self.setting_widget)
        self.engine_type_combo.addItem("Sobol")
        self.engine_type_combo.addItem("Uniform")

        self.scaling_condition_frame = SpinBoxUnitInputFrame(self)
        self.scaling_condition_frame.set_input("Å",1,"float")
        self.scaling_condition_frame.setRange(0,1)
        self.scaling_radio_label=BodyLabel("Max distance:",self.setting_widget)


        self.num_condition_frame = SpinBoxUnitInputFrame(self)
        self.num_condition_frame.set_input("unit",1,"int")
        self.num_condition_frame.setRange(1,10000)
        self.num_label=BodyLabel("Max num:",self.setting_widget)


        self.settingLayout.addWidget(self.engine_label,0, 0,1, 1)
        self.settingLayout.addWidget(self.engine_type_combo,0, 1, 1, 2)

        self.settingLayout.addWidget(self.scaling_radio_label, 1, 0, 1, 1)

        self.settingLayout.addWidget(self.scaling_condition_frame, 1, 1, 1,2)
        self.settingLayout.addWidget(self.num_label, 2, 0, 1, 1)

        self.settingLayout.addWidget(self.num_condition_frame, 2, 1, 1,2)
    def process_structure(self, structure):
        structure_list=[]
        engine_type=self.engine_type_combo.currentIndex()
        max_scaling=self.scaling_condition_frame.get_input_value()[0]
        max_num=self.num_condition_frame.get_input_value()[0]

        n_atoms = len(structure)
        dim = n_atoms * 3  # 每个原子有 x, y, z 三个维度

        if engine_type == 0:
            sobol_seq = sobol.sample(dimension=dim, n_points=max_num)
            perturbation_factors = (sobol_seq - 0.5) * 2  # 转换为 [-1, 1]


        else:
            # 生成均匀分布的扰动因子，范围 [-1, 1]
            perturbation_factors = np.random.uniform(-1, 1, (max_num, dim))

        orig_positions = structure.positions
        for i in range(max_num):
            new_struct = structure.copy()
            # 提取当前结构的扰动因子并重塑为 (n_atoms, 3)
            delta = perturbation_factors[i].reshape(n_atoms, 3) * max_scaling
            new_positions = orig_positions + delta

            # 更新坐标
            new_struct.structure_info['pos'] = new_positions
            new_struct.additional_fields["Config_type"] = structure.additional_fields["Config_type"] + f"Perturb {i} (distance={max_scaling},{'uniform' if engine_type==1 else 'Sobol'  }) "

            structure_list.append(new_struct)

        return structure_list
    def to_dict(self):
        data_dict = {}
        data_dict['class']="PerturbCard"
        data_dict['name'] =  CardName.perturb
        data_dict["check_state"]=self.check_state

        data_dict['engine_type'] = self.engine_type_combo.currentIndex()

        data_dict['scaling_condition'] = self.scaling_condition_frame.get_input_value()

        data_dict['num_condition'] = self.num_condition_frame.get_input_value()
        return data_dict
    def from_dict(self, data_dict):
        self.state_checkbox.setChecked(data_dict['check_state'])

        self.engine_type_combo.setCurrentIndex(data_dict['engine_type'])

        self.scaling_condition_frame.set_input_value(data_dict['scaling_condition'])

        self.num_condition_frame.set_input_value(data_dict['num_condition'])

class CellScalingCard(MakeDataCard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Make Cell Scaling")

        self.init_ui()

    def init_ui(self):
        self.setObjectName("cell_scaling_card_widget")


        self.engine_label=BodyLabel("Random engine:",self.setting_widget)
        self.engine_type_combo=ComboBox(self.setting_widget)
        self.engine_type_combo.addItem("Sobol")
        self.engine_type_combo.addItem("Uniform")


        self.scaling_condition_frame = SpinBoxUnitInputFrame(self)
        self.scaling_condition_frame.set_input("",1,"float")
        self.scaling_condition_frame.setRange(0,1)
        self.scaling_radio_label=BodyLabel("Max Scaling:",self.setting_widget)
        self.perturb_angle_checkbox=CheckBox( self.setting_widget)
        self.perturb_angle_checkbox.setText("Perturb angle")
        self.perturb_angle_checkbox.setChecked(True)
        self.perturb_angle_label=BodyLabel("Optional",self.setting_widget)


        self.num_condition_frame = SpinBoxUnitInputFrame(self)
        self.num_condition_frame.set_input("unit",1,"int")
        self.num_condition_frame.setRange(1,10000)
        self.num_label=BodyLabel("Max num:",self.setting_widget)

        self.settingLayout.addWidget(self.engine_label,0, 0,1, 1)
        self.settingLayout.addWidget(self.engine_type_combo,0, 1, 1, 2)

        self.settingLayout.addWidget(self.perturb_angle_label, 1, 0, 1, 1)
        self.settingLayout.addWidget(self.perturb_angle_checkbox, 1, 1, 1,1)

        self.settingLayout.addWidget(self.scaling_radio_label, 2, 0, 1, 1)

        self.settingLayout.addWidget(self.scaling_condition_frame, 2, 1, 1,2)
        self.settingLayout.addWidget(self.num_label, 3, 0, 1, 1)

        self.settingLayout.addWidget(self.num_condition_frame, 3, 1, 1,2)
    def process_structure(self, structure):
        structure_list=[]
        engine_type=self.engine_type_combo.currentIndex()
        max_scaling=self.scaling_condition_frame.get_input_value()[0]
        max_num=self.num_condition_frame.get_input_value()[0]

        if self.perturb_angle_checkbox.isChecked():
            perturb_angles=True
            dim=6 #abc + angles
        else:
            dim=3 #abc
            perturb_angles=False
        if engine_type == 0:
            sobol_seq = sobol.sample(dimension=dim, n_points=max_num)

            perturbation_factors = 1 + (sobol_seq - 0.5) * 2 * max_scaling
        else:
            perturbation_factors = 1 + np.random.uniform(-max_scaling, max_scaling, (max_num, dim))

        orig_lattice = structure.lattice
        orig_lengths = np.linalg.norm(orig_lattice, axis=1)
        unit_vectors = orig_lattice / orig_lengths[:, np.newaxis]  # 原始晶格的单位向量
        for i in range(max_num):
            # 提取微扰因子
            length_factors = perturbation_factors[i, :3]
            new_lengths = orig_lengths * length_factors

            # 构造新晶格：仅缩放长度，保持方向
            new_lattice = unit_vectors * new_lengths[:, np.newaxis]

            # 可选：扰动角度
            if perturb_angles:
                angle_factors = perturbation_factors[i, 3:]
                angles = np.arccos([
                    np.dot(orig_lattice[1], orig_lattice[2]) / (orig_lengths[1] * orig_lengths[2]),
                    np.dot(orig_lattice[0], orig_lattice[2]) / (orig_lengths[0] * orig_lengths[2]),
                    np.dot(orig_lattice[0], orig_lattice[1]) / (orig_lengths[0] * orig_lengths[1])
                ])
                new_angles = angles * angle_factors
                # 重新构造晶格（保持角度扰动）
                new_lattice = np.zeros((3, 3), dtype=np.float32)
                new_lattice[0] = [new_lengths[0], 0, 0]
                new_lattice[1] = [new_lengths[1] * np.cos(new_angles[2]),
                                  new_lengths[1] * np.sin(new_angles[2]), 0]
                cx = new_lengths[2] * np.cos(new_angles[1])
                cy = new_lengths[2] * (np.cos(new_angles[0]) - np.cos(new_angles[1]) * np.cos(new_angles[2])) / np.sin(
                    new_angles[2])
                cz = np.sqrt(max(new_lengths[2] ** 2 - cx ** 2 - cy ** 2, 0))  # 防止负值
                new_lattice[2] = [cx, cy, cz]

            # 缩放原子位置
            new_struct = structure.set_lattice(new_lattice,in_place=False)
            new_struct.additional_fields["Config_type"] = structure.additional_fields["Config_type"] +f"Cell Scaling {i} (scaling={max_scaling},{'uniform' if engine_type==1 else 'Sobol'  }) "

            structure_list.append(new_struct)
        return structure_list
    def to_dict(self):
        data_dict = {}
        data_dict['class']="CellScalingCard"
        data_dict['name'] =  CardName.scaling
        data_dict["check_state"]=self.check_state
        data_dict['engine_type'] = self.engine_type_combo.currentIndex()
        data_dict['perturb_angle'] = self.perturb_angle_checkbox.isChecked()
        data_dict['scaling_condition'] = self.scaling_condition_frame.get_input_value()
        data_dict['num_condition'] = self.num_condition_frame.get_input_value()
        return data_dict
    def from_dict(self, data_dict):
        self.state_checkbox.setChecked(data_dict['check_state'])

        self.engine_type_combo.setCurrentIndex(data_dict['engine_type'])
        self.perturb_angle_checkbox.setChecked(data_dict['perturb_angle'])
        self.scaling_condition_frame.set_input_value(data_dict['scaling_condition'])
        self.num_condition_frame.set_input_value(data_dict['num_condition'])