#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2025/1/7 23:23
# @Author  : 兵
# @email    : 1747193328@qq.com
from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtGui import QIcon, QDrag, QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout
from qfluentwidgets import HeaderCardWidget, CheckBox, TransparentToolButton

from NepTrainKit import utils


class CheckableHeaderCardWidget(HeaderCardWidget):
    def __init__(self, parent=None):
        super(CheckableHeaderCardWidget, self).__init__(parent)
        self.state_checkbox=CheckBox()
        self.state_checkbox.stateChanged.connect(self.state_changed)
        self.headerLayout.insertWidget(0, self.state_checkbox, 0,Qt.AlignmentFlag.AlignLeft)
        self.headerLayout.setStretch(1, 3)
        self.headerLayout.setContentsMargins(10, 0, 3, 0)
        self.headerLayout.setSpacing(3)
        self.viewLayout.setContentsMargins(6, 0, 6, 0)
        self.headerLayout.setAlignment(self.headerLabel, Qt.AlignmentFlag.AlignLeft)
        self.check_state=False
    def state_changed(self, state):
        if state == 2:
            self.check_state = True
        else:
            self.check_state = False


class ShareCheckableHeaderCardWidget(CheckableHeaderCardWidget):
    exportSignal=Signal()
    def __init__(self, parent=None):
        super(ShareCheckableHeaderCardWidget, self).__init__(parent)
        self.export_button=TransparentToolButton(QIcon(":/images/src/images/export1.svg"),self)
        self.export_button.clicked.connect(self.exportSignal)
        self.headerLayout.addWidget(self.export_button, 0, Qt.AlignmentFlag.AlignRight)
class MakeDataCardWidget(ShareCheckableHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)

    def mouseMoveEvent(self, e):
        if e.buttons() != Qt.LeftButton:
            return
        drag = QDrag(self)
        mime = QMimeData()
        drag.setMimeData(mime)

        # 显示拖拽时的控件预览
        pixmap = QPixmap(self.size())
        self.render(pixmap)
        drag.setPixmap(pixmap)
        drag.setHotSpot(e.pos())

        drag.exec(Qt.MoveAction)

class MakeDataCard(MakeDataCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.exportSignal.connect(self.export_data)
        self.dataset=None
        self.setFixedSize(400, 200)
        self.setting_widget = QWidget(self)
        self.viewLayout.addWidget(self.setting_widget)
        self.settingLayout = QGridLayout(self.setting_widget)

    def export_data(self):

        if self.dataset is not None:

            path = utils.call_path_dialog(self, "Choose a file save location", "file",f"export_{self.getTitle()}_structure.xyz")
            if not path:
                return

            with open(path,"w",encoding="utf8") as f:
                for structure in self.dataset.now_data:
                    structure.write(f)



class CardGroup(MakeDataCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Card Group")
        self.setAcceptDrops(True)
        self.group_widget = QWidget(self)
        self.viewLayout.addWidget(self.group_widget)
        self.group_layout = QVBoxLayout(self.group_widget)
        self.card_list = []
        self.resize(400, 200)
    def add_card(self, card):
        self.card_list.append(card)
        self.group_layout.addWidget(card)
    def remove_card(self, card):
        self.card_list.remove(card)
        self.group_layout.removeWidget(card)
    def clear_cards(self):
        for card in self.card_list:
            self.group_layout.removeWidget(card)
        self.card_list.clear()

    def get_card_list(self):
        return self.card_list
    def dragEnterEvent(self, event):
        if isinstance(event.source(), MakeDataCard):
            event.acceptProposedAction()
        else:
            event.ignore()  # 忽略其他类型的拖拽
    def dropEvent(self, event):
        widget = event.source()
        if isinstance(widget, MakeDataCard):
            self.add_card(widget)


        event.acceptProposedAction()