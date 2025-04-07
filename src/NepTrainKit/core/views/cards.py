#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2025/4/6 13:21
# @Author  : 兵
# @email    : 1747193328@qq.com
from PySide6.QtWidgets import QGridLayout, QFrame
from qfluentwidgets import ComboBox, BodyLabel, RadioButton

from NepTrainKit.core.custom_widget import MakeDataCard, SpinBoxUnitInputFrame


class SuperCellCard(MakeDataCard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("超胞制作")

        self.init_ui()
    def init_ui(self):
        self.setObjectName("super_cell_card_widget")




        self.super_cell_frame = QFrame(self.setting_widget)

        self.super_cell_frame_layout = QGridLayout(self.super_cell_frame)

        self.super_cell_type_combo=ComboBox(self.setting_widget)
        self.super_cell_type_combo.addItem("最大扩包")
        self.super_cell_type_combo.addItem("随机组合")
        self.combo_label=BodyLabel("扩包行为：",self.setting_widget)

        self.radio_button_1 = RadioButton("super scale",self.setting_widget)
        self.super_cell_condition_frame_1 = SpinBoxUnitInputFrame(self)
        self.super_cell_condition_frame_1.set_input("",3)

        self.super_cell_condition_frame_2 = SpinBoxUnitInputFrame(self)
        self.super_cell_condition_frame_2.set_input("A",3)
        self.radio_button_2 = RadioButton("super cell",self.setting_widget)

        self.super_cell_frame_layout.addWidget(self.combo_label,0, 0,1, 1)
        self.super_cell_frame_layout.addWidget(self.super_cell_type_combo,0, 1, 1, 2)
        self.super_cell_frame_layout.addWidget(self.radio_button_1, 1, 0, 1, 1)
        self.super_cell_frame_layout.addWidget(self.super_cell_condition_frame_1, 1, 1, 1, 2)
        self.super_cell_frame_layout.addWidget(self.radio_button_2, 2, 0, 1, 1)
        self.super_cell_frame_layout.addWidget(self.super_cell_condition_frame_2, 2, 1, 1, 2)



        self.settingLayout.addWidget(self.super_cell_frame, 0, 0, 1, 1)
    def bind_signals(self):
        pass
    def super_cell_entry(self):
        super_cell_type=self.super_cell_type_combo.currentIndex()
        if super_cell_type==0:
            # 最大扩包
            pass
        elif super_cell_type==1:
            # 随机组合
            pass
        else:
            #还没写 暂时不处理 就两种扩包方式
            pass
