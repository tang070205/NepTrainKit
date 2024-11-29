#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/11/28 22:45
# @Author  : 兵
# @email    : 1747193328@qq.com
from PySide6.QtWidgets import QVBoxLayout,QHBoxLayout,QFrame,QGridLayout
from qfluentwidgets import MessageBoxBase, SubtitleLabel, LineEdit,SpinBox,CaptionLabel,DoubleSpinBox



class GetIntMessageBox(MessageBoxBase):
    """ Custom message box """

    def __init__(self, parent=None,tip=""):
        super().__init__(parent)
        self.titleLabel = CaptionLabel(tip, self)
        self.titleLabel.setWordWrap(True)
        self.intSpinBox = SpinBox(self)

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.intSpinBox)

        self.widget.setMinimumWidth(100)
class SparseMessageBox(MessageBoxBase):
    """用于最远点取样的弹窗 """

    def __init__(self, parent=None,tip=""):
        super().__init__(parent)
        self.titleLabel = CaptionLabel(tip, self)
        self.titleLabel.setWordWrap(True)
        self._frame = QFrame(self)
        self.frame_layout=QGridLayout(self._frame)
        self.frame_layout.setContentsMargins(0,0,0,0)
        self.frame_layout.setSpacing(0)
        self.intSpinBox = SpinBox(self)

        self.intSpinBox.setMaximum(9999999)
        self.intSpinBox.setMinimum(0)
        self.doubleSpinBox = DoubleSpinBox(self)
        self.doubleSpinBox.setDecimals(3)
        self.doubleSpinBox.setMinimum(0)
        self.doubleSpinBox.setMaximum(10)

        self.frame_layout.addWidget(CaptionLabel("Max num", self),0,0,1,1)

        self.frame_layout.addWidget(self.intSpinBox,0,1,1,2)
        self.frame_layout.addWidget(CaptionLabel("Min distance", self),1,0,1,1)

        self.frame_layout.addWidget(self.doubleSpinBox,1,1,1,2)

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self._frame )

        self.yesButton.setText('Ok')
        self.cancelButton.setText('Cancel')

        self.widget.setMinimumWidth(200)

