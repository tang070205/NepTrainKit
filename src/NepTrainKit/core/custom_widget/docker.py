#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2025/4/6 13:27
# @Author  : 兵
# @email    : 1747193328@qq.com
# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/12/20 17:18
# @Author  : 兵
# @email    : 1747193328@qq.com

from PySide6.QtWidgets import QWidget, QApplication, QScrollArea

from NepTrainKit.core.custom_widget import CardGroup, FlowLayout
from NepTrainKit.core.views.cards import SuperCellCard, MakeDataCard


class MakeWorkflowArea(QScrollArea):
    """
微扰训练集制作
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent = parent
        self.setObjectName("MakeWorkflowArea")
        self.setWidgetResizable(True)

        self.setAcceptDrops(True)

        self.init_ui()

    def dragEnterEvent(self, event):


        if isinstance(event.source(), (MakeDataCard,CardGroup)):
            event.acceptProposedAction()
        else:
            event.ignore()  # 忽略其他类型的拖拽

    def dropEvent(self, event):

        if isinstance(event.source(), (MakeDataCard,CardGroup)):


            dragged_widget = event.source()
            drag_start_index = self.flow_layout.findWidgetAt(dragged_widget)[0]
            drop_pos = event.position().toPoint()
            drop_index, _ = self.flow_layout.findItemAt(drop_pos)

            if drop_index == -1:
                drop_index = self.flow_layout.count() - 1

            drop_index = min(max(0, drop_index), self.flow_layout.count())

            if drag_start_index==-1:
                self.flow_layout.insertWidget(drop_index,dragged_widget)
            else:
                if drag_start_index != drop_index:
                    self.flow_layout.moveItem(drag_start_index, drop_index)

            self.flow_layout.update()


            event.acceptProposedAction()




    def init_ui(self):


        self.container = QWidget(self)
        self.flow_layout = FlowLayout(self.container)
        self.container.setLayout(self.flow_layout)
        self.setWidget(self.container)

        self.super_cell_card_widget = SuperCellCard(self)

        self.super_cell_card_widget.setTitle("超胞制作1")
        self.flow_layout.addWidget(self.super_cell_card_widget)

        self.super_cell_card_widget2 = SuperCellCard(self)

        self.super_cell_card_widget2.setTitle("超胞制作2")

        self.flow_layout.addWidget(self.super_cell_card_widget2)

        card_group = CardGroup(self)
        card_group.setTitle("卡片组")
        self.flow_layout.addWidget(card_group)






        self.super_cell_card_widget3 = SuperCellCard(self)
        self.super_cell_card_widget3.setTitle("超胞制作3")

        self.flow_layout.addWidget(self.super_cell_card_widget3)

        self.super_cell_card_widget4 = SuperCellCard(self)
        self.super_cell_card_widget4.setTitle("超胞制作4")

        self.flow_layout.addWidget(self.super_cell_card_widget4)

        # self.setLayout(self.gridLayout)







if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    window = MakeWorkflowArea()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())