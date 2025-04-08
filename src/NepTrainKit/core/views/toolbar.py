#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/10/18 22:12
# @Author  : 兵
# @email    : 1747193328@qq.com

from PySide6.QtCore import Signal
from PySide6.QtGui import QAction, QIcon, QActionGroup
from PySide6.QtWidgets import QToolBar




class NepDisplayGraphicsToolBar(QToolBar):
    panSignal=Signal(bool)
    resetSignal=Signal()
    findMaxSignal=Signal()
    sparseSignal=Signal()
    penSignal=Signal(bool)
    undoSignal=Signal()
    discoverySignal=Signal()
    deleteSignal=Signal()
    revokeSignal=Signal()
    exportSignal=Signal()
    def __init__(self,  parent=None):
        super().__init__(parent)
        self._parent = parent
        self._actions={}
        self.init_actions()


    def init_actions(self):
        self.add_action("Reset View",QIcon(":/images/src/images/init.svg"),self.resetSignal)
        pan_action=self.add_action("Pan View",
                                   QIcon(":/images/src/images/pan.svg"),
                                   self.pan,
                                   True
                                   )


        find_max_action=self.add_action( "Find Max Error Point",
                                          QIcon(":/images/src/images/find_max.svg"),
                                          self.findMaxSignal)
        sparse_action=self.add_action( "Sparse samples",
                                          QIcon(":/images/src/images/sparse.svg"),
                                          self.sparseSignal)


        pen_action=self.add_action("Mouse Selection",
                                   QIcon(":/images/src/images/pen.svg"),
                                   self.pen,
                                   True

                                   )

        self.action_group = QActionGroup(self)
        self.action_group.setExclusive(True)  # 设置为互斥组
        self.action_group.addAction(pan_action)
        self.action_group.addAction(pen_action)
        self.action_group.setExclusionPolicy(QActionGroup.ExclusionPolicy.ExclusiveOptional)

        discovery_action=self.add_action("Finding non-physical structures",QIcon(":/images/src/images/discovery.svg"),self.discoverySignal)


        revoke_action=self.add_action("Undo",QIcon(":/images/src/images/revoke.svg"),self.revokeSignal)

        delete_action=self.add_action("Delete Selected Items",QIcon(":/images/src/images/delete.svg"),self.deleteSignal)
        self.addSeparator()
        export_action=self.add_action("Export structure descriptor",QIcon(":/images/src/images/export.svg"),self.exportSignal)

    def reset(self):
        if self.action_group.checkedAction():
            self.action_group.checkedAction().setChecked(False)

    def add_action(self, name,icon,callback,checkable=False):
        action=QAction(QIcon(icon),name,self)
        if checkable:
            action.setCheckable(True)
            action.toggled.connect(callback)
        else:
            action.triggered.connect(callback)
        self._actions[name]=action
        self.addAction(action)
        action.setToolTip(name)
        return action


    def pan(self, checked):
        """切换平移模式"""

        if checked:
            self.panSignal.emit(True)
        else:
            self.panSignal.emit(False)


    def pen(self, checked):

        if checked:
            self.penSignal.emit(True)
        else:
            self.penSignal.emit(False)
