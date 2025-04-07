#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2025/4/6 13:21
# @Author  : 兵
# @email    : 1747193328@qq.com
import time
from typing import List, Tuple

import numpy as np
from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QGridLayout, QFrame, QWidget
from qfluentwidgets import ComboBox, BodyLabel, RadioButton, SplitToolButton, RoundMenu, PrimaryDropDownToolButton, \
    PrimaryDropDownPushButton, CommandBar, Action

from NepTrainKit.core.custom_widget import MakeDataCard, SpinBoxUnitInputFrame
from NepTrainKit import utils

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
        self.menu.addAction(QAction(QIcon(r":/images/src/images/group.svg"), 'Card Group'))
        self.menu.addSeparator()
        self.menu.addAction(QAction(QIcon(r":/images/src/images/supercell.svg"), 'Super Cell'))
        self.menu.addAction(QAction(QIcon(r":/images/src/images/perturb.svg"), 'Atomic perturb'))
        self.menu.addAction(QAction(QIcon(r":/images/src/images/scaling.svg"), 'Lattice scaling'))
        self.menu.addAction(QAction(QIcon(r":/images/src/images/defect.svg"), 'Defect Generation'))
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
        self.super_cell_frame = QFrame(self.setting_widget)

        self.super_cell_frame_layout = QGridLayout(self.super_cell_frame)

        self.super_cell_type_combo=ComboBox(self.setting_widget)
        self.super_cell_type_combo.addItem("Maximum")
        self.super_cell_type_combo.addItem("Random")
        self.combo_label=BodyLabel("behavior:",self.setting_widget)

        self.super_scale_radio_button = RadioButton("super scale",self.setting_widget)
        self.super_scale_radio_button.setChecked(True)
        self.super_scale_condition_frame = SpinBoxUnitInputFrame(self)
        self.super_scale_condition_frame.set_input("",3)
        self.super_scale_condition_frame.setRange(1,100)

        self.super_cell_radio_button = RadioButton("super cell",self.setting_widget)
        self.super_cell_condition_frame = SpinBoxUnitInputFrame(self)
        self.super_cell_condition_frame.set_input("A",3)
        self.super_cell_condition_frame.setRange(1,100)


        self.max_atoms_condition_frame = SpinBoxUnitInputFrame(self)
        self.max_atoms_condition_frame.set_input("",1)
        self.max_atoms_condition_frame.setRange(1,10000)

        self.max_atoms_radio_button = RadioButton("Max atoms",self.setting_widget)


        self.super_cell_frame_layout.addWidget(self.combo_label,0, 0,1, 1)
        self.super_cell_frame_layout.addWidget(self.super_cell_type_combo,0, 1, 1, 2)
        self.super_cell_frame_layout.addWidget(self.super_scale_radio_button, 1, 0, 1, 1)
        self.super_cell_frame_layout.addWidget(self.super_scale_condition_frame, 1, 1, 1, 2)
        self.super_cell_frame_layout.addWidget(self.super_cell_radio_button, 2, 0, 1, 1)
        self.super_cell_frame_layout.addWidget(self.super_cell_condition_frame, 2, 1, 1, 2)
        self.super_cell_frame_layout.addWidget(self.max_atoms_radio_button, 3, 0, 1, 1)
        self.super_cell_frame_layout.addWidget(self.max_atoms_condition_frame, 3, 1, 1, 2)

        self.settingLayout.addWidget(self.super_cell_frame, 0, 0, 1, 1)
    def bind_signals(self):
        pass

    # @utils.timeit

    def _get_scale_factors(self) -> List[Tuple[int, int, int]]:
        """从 super_scale_condition_frame 获取扩包比例"""
        na, nb, nc = self.super_scale_condition_frame.get_input()
        return [(na, nb, nc)]
    # @utils.timeit
    def _get_max_cell_factors(self, structure) -> List[Tuple[int, int, int]]:
        """根据最大晶格常数计算扩包比例"""
        max_a, max_b, max_c = self.super_cell_condition_frame.get_input()
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
    # @utils.timeit

    def _get_max_atoms_factors(self, structure) -> List[Tuple[int, int, int]]:
        """根据最大原子数计算所有可能的扩包比例"""
        max_atoms = self.max_atoms_condition_frame.get_input()[0]
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
    # @utils.timeit

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


        super_cell_type = self.super_cell_type_combo.currentIndex()

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
