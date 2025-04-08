#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2025/1/7 23:23
# @Author  : 兵
# @email    : 1747193328@qq.com
from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtGui import QIcon, QDrag, QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout
from qfluentwidgets import HeaderCardWidget, CheckBox, TransparentToolButton

from NepTrainKit.core import MessageManager

from qfluentwidgets import FluentIcon as FIF
from NepTrainKit.core.custom_widget import ProcessLabel
from NepTrainKit import utils
from NepTrainKit.core.types import CardName


class CheckableHeaderCardWidget(HeaderCardWidget):
    def __init__(self, parent=None):
        super(CheckableHeaderCardWidget, self).__init__(parent)
        self.state_checkbox=CheckBox()
        self.state_checkbox.setChecked(True)
        self.state_checkbox.stateChanged.connect(self.state_changed)
        self.headerLayout.insertWidget(0, self.state_checkbox, 0,Qt.AlignmentFlag.AlignLeft)
        self.headerLayout.setStretch(1, 3)
        self.headerLayout.setContentsMargins(10, 0, 3, 0)
        self.headerLayout.setSpacing(3)
        self.viewLayout.setContentsMargins(6, 0, 6, 0)
        self.headerLayout.setAlignment(self.headerLabel, Qt.AlignmentFlag.AlignLeft)
        self.check_state=True
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

        self.close_button=TransparentToolButton(FIF.CLOSE,self)
        self.close_button.clicked.connect(self.close)


        self.headerLayout.addWidget(self.export_button, 0, Qt.AlignmentFlag.AlignRight)
        self.headerLayout.addWidget(self.close_button, 0, Qt.AlignmentFlag.AlignRight)

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
    #通知下一个card执行
    runFinishedSignal=Signal(int)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.exportSignal.connect(self.export_data)
        self.dataset:list=None
        self.result_dataset=[]
        self.index=0
        # self.setFixedSize(400, 200)
        self.setting_widget = QWidget(self)
        self.viewLayout.setContentsMargins(3, 6, 3, 6)
        self.viewLayout.addWidget(self.setting_widget)
        self.settingLayout = QGridLayout(self.setting_widget)
        self.settingLayout.setContentsMargins(5, 0, 5,0)
        self.settingLayout.setSpacing(3)
        self.status_label = ProcessLabel(self)
        self.vBoxLayout.addWidget(self.status_label)


    def set_dataset(self,dataset):
        self.dataset =dataset
        self.result_dataset=[]

        self.update_dataset_info()
    def write_result_dataset(self, file):
        if isinstance(file, str):
            file=open(file, "w", encoding="utf8")
            io_action=False
        else:
            io_action=True

        for structure in self.result_dataset:
            structure.write(file)
        if not io_action:
            file.close()
    def export_data(self):

        if self.dataset is not None:

            path = utils.call_path_dialog(self, "Choose a file save location", "file",f"export_{self.getTitle().replace(' ', '_')}_structure.xyz")
            if not path:
                return
            thread=utils.LoadingThread(self,show_tip=True,title="Exporting data")
            thread.start_work(self.write_result_dataset, path)

    def process_structure(self, structure) :
        """
        自定义对每个结构的处理 最后返回一个处理后的结构列表
        """
        raise NotImplementedError
    def closeEvent(self, event):

        if hasattr(self, "worker_thread"):

            if self.worker_thread.isRunning():

                self.worker_thread.terminate()
                self.runFinishedSignal.emit(self.index)

        self.deleteLater()
        super().closeEvent(event)
    def stop(self):
        if hasattr(self, "worker_thread"):
            if self.worker_thread.isRunning():
                self.worker_thread.terminate()
                self.result_dataset = self.worker_thread.result_dataset
                self.update_dataset_info()
                del self.worker_thread
    def run(self):
        # 创建并启动线程

        if self.check_state:
            self.worker_thread = utils.DataProcessingThread(
                self.dataset,
                self.process_structure
            )
            self.status_label.set_colors(["#59745A" ])

            # 连接信号
            self.worker_thread.progressSignal.connect(self.update_progress)
            self.worker_thread.finishSignal.connect(self.on_processing_finished)
            self.worker_thread.errorSignal.connect(self.on_processing_error)

            self.worker_thread.start()
        else:
            self.result_dataset = self.dataset
            self.update_dataset_info()
            self.runFinishedSignal.emit(self.index)
        # self.worker_thread.wait()
    def update_progress(self, progress):
        self.status_label.setText(f"Processing {progress}%")
        self.status_label.set_progress(progress)
    def on_processing_finished(self):
        # self.status_label.setText("Processing finished")

        self.result_dataset = self.worker_thread.result_dataset
        self.update_dataset_info()
        self.status_label.set_colors(["#a5d6a7" ])
        self.runFinishedSignal.emit(self.index)
        del self.worker_thread
    def on_processing_error(self, error):
        self.close_button.setEnabled(True)

        self.status_label.set_colors(["red" ])
        self.result_dataset = self.worker_thread.result_dataset
        del self.worker_thread
        self.update_dataset_info()
        self.runFinishedSignal.emit(self.index)

        MessageManager.send_error_message(f"Error occurred: {error}")
    def update_dataset_info(self ):
        text = f"Input structures: {len(self.dataset)} → Output: {len(self.result_dataset)}"
        self.status_label.setText(text)


class CardGroup(MakeDataCardWidget):
    #通知下一个card执行
    runFinishedSignal=Signal(int)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Card Group")
        self.setAcceptDrops(True)
        self.index=0
        self.group_widget = QWidget(self)
        self.viewLayout.addWidget(self.group_widget)
        self.group_layout = QVBoxLayout(self.group_widget)
        self.exportSignal.connect(self.export_data)
        self.card_list = []
        self.resize(400, 200)
    def set_dataset(self,dataset):
        self.dataset =dataset
        self.result_dataset=[]

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
    def check_card_state(self):
        """
        将卡片拖出后 不会将list更新  这里使用之前手动更新list
        """

        self.card_list.clear()
        for i in range(self.group_layout.count()):
            self.card_list.append(self.group_layout.itemAt(i).widget())
    def get_card_list(self):
        return self.card_list
    def closeEvent(self, event):
        self.check_card_state()
        for card in self.card_list:
            card.close()
        self.deleteLater()
        super().closeEvent(event)




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
    def on_card_finished(self, index):
        self.run_card_num-=1
        self.card_list[index].runFinishedSignal.disconnect(self.on_card_finished)
        self.result_dataset.extend(self.card_list[index].result_dataset)

        if self.run_card_num==0:

            self.runFinishedSignal.emit(self.index)

    def stop(self):
        for card in self.card_list:
            card.stop()
    def run(self):
        # 创建并启动线程
        self.check_card_state()
        self.result_dataset =[]
        self.run_card_num=len(self.card_list)
        for index,card in enumerate(self.card_list):
            card.set_dataset(self.dataset)
            card.index=index
            card.runFinishedSignal.connect(self.on_card_finished)
            card.run()


    def write_result_dataset(self, file):
        self.check_card_state()
        if isinstance(file,str):
            file=open(file, "w", encoding="utf8")
        for card in self.card_list:
            if card.check_state:
                card.write_result_dataset(file)
        file.close()
    def export_data(self):

        if self.dataset is not None:

            path = utils.call_path_dialog(self, "Choose a file save location", "file",f"export_{self.getTitle()}_structure.xyz")
            if not path:
                return
            thread=utils.LoadingThread(self,show_tip=True,title="Exporting data")
            thread.start_work(self.write_result_dataset, path)
    def to_dict(self):
        data_dict={}
        data_dict['class']="CardGroup"
        data_dict['name']=CardName.group

        data_dict["check_state"]=self.check_state

        data_dict["card_list"]=[]
        self.check_card_state()
        for card in self.card_list:
            data_dict["card_list"].append(card.to_dict())
        return data_dict
    def from_dict(self,data_dict):

        self.state_checkbox.setChecked(data_dict['check_state'])

