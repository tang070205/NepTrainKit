#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2025/1/7 23:23
# @Author  : 兵
# @email    : 1747193328@qq.com
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox
from qfluentwidgets import HeaderCardWidget,CheckBox


class CheckableHeaderCardWidget(HeaderCardWidget):
    def __init__(self, parent=None):
        super(CheckableHeaderCardWidget, self).__init__(parent)
        self.state_checkbox=CheckBox()
        self.state_checkbox.stateChanged.connect(self.state_changed)
        self.headerLayout.insertWidget(0, self.state_checkbox, 0,Qt.AlignmentFlag.AlignLeft)
        self.headerLayout.setStretch(1, 3)
        self.headerLayout.setContentsMargins(10, 0, 3, 0)
        self.headerLayout.setSpacing(3)

        self.headerLayout.setAlignment(self.headerLabel, Qt.AlignmentFlag.AlignLeft)
        self.check_state=False

    def state_changed(self, state):
        if state == 2:
            self.check_state = True
        else:
            self.check_state = False
