#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/10/17 13:38
# @Author  : 兵
# @email    : 1747193328@qq.com
import os.path
from io import StringIO

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QWidget, QGridLayout



from qfluentwidgets import HyperlinkLabel, MessageBox,SubtitleLabel,PlainTextEdit,CaptionLabel

from NepTrainKit import utils
from NepTrainKit.core import MessageManager
from NepTrainKit.core.io import NepTrainResultData


from NepTrainKit.core.plot import NepResultGraphicsLayoutWidget,GraphicsToolBar,StructurePlotWidget



class ShowNepWidget(QWidget):
    """
    针对NEP训练过程中 对预测结果的展示
    实现以下功能
        1.支持交互筛选训练集
        2.拖拽实现目录导入
        3.对于选定的结构 进行展示
    """
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setObjectName("ShowNepWidget")
        self.setAcceptDrops(True)
        self.dataset=None
        self.init_ui()

    def init_ui(self):
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setObjectName("show_nep_gridLayout")
        self.gridLayout.setContentsMargins(0,0,0,0)
        self.plot_widget = QWidget(self)

        self.plot_widget_layout = QGridLayout(self.plot_widget)

        self.graph_widget = NepResultGraphicsLayoutWidget(  )

        self.graph_widget.structureIndexChanged.connect(self.show_current_structure)

        self.graph_toolbar = GraphicsToolBar(self.graph_widget,self.plot_widget)

        self.plot_widget_layout.addWidget(self.graph_toolbar)

        self.plot_widget_layout.addWidget(self.graph_widget)
        self.plot_widget_layout.setContentsMargins(0,0,0,0)


        self.struct_widget = QWidget(self)
        self.struct_widget_layout = QGridLayout(self.struct_widget)

        self.show_struct_widget = StructurePlotWidget(self.struct_widget )

        self.struct_info_edit = PlainTextEdit(self.struct_widget)
        self.struct_info_edit.setReadOnly(True)

        self.struct_index_label=CaptionLabel(self.struct_widget)


        self.struct_widget_layout.addWidget(self.show_struct_widget,0,0,1,1)
        self.struct_widget_layout.addWidget(self.struct_info_edit,1,0,1,1)
        self.struct_widget_layout.addWidget(self.struct_index_label,2,0,1,1)




        self.struct_widget_layout.setRowStretch(0, 3)
        self.struct_widget_layout.setRowStretch(1, 1)
        self.struct_widget_layout.setRowStretch(2, 0)

        self.struct_widget_layout.setContentsMargins(0,0,0,0)







        self.gridLayout.addWidget(self.plot_widget, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.struct_widget, 0, 1, 1, 1)




        # 创建状态栏
        self.path_label = HyperlinkLabel(  self)
        self.path_label.setFixedHeight(30)  # 设置状态栏的高度

        # 将状态栏添加到布局的底部
        self.gridLayout.addWidget(self.path_label, 1, 0, 1, 1)
        # self.gridLayout.setHorizontalSpacing( 0)



        self.gridLayout.setColumnStretch(0, 3)
        self.gridLayout.setColumnStretch(1, 3)

    def dragEnterEvent(self, event):
        # 检查拖拽的内容是否包含文件
        if event.mimeData().hasUrls():
            event.acceptProposedAction()  # 接受拖拽事件
        else:
            event.ignore()  # 忽略其他类型的拖拽

    def dropEvent(self, event):
        # 获取拖拽的文件路径
        urls = event.mimeData().urls()
        if urls:
            # 获取第一个文件路径
            file_path = urls[0].toLocalFile()

            self.set_work_path(file_path)


    def open_file(self):
        path = utils.call_path_dialog(self,"请选择工作路径","directory")
        if path:
            self.set_work_path(path)

    def export_file(self):
        if self.dataset is None:
            MessageManager.send_info_message("您还没有加载NEP数据！")
            return
        path=utils.call_path_dialog(self,"选择文件保存路径","directory")
        if path:
            thread=utils.LoadingThread(self,show_tip=True,title="正在导出数据")
            thread.start_work(self.dataset.export_model_xyz,path)



    def set_work_path(self,path):

        if os.path.isfile(path):
            path = os.path.dirname(path)
        url=self.path_label.getUrl().toString()

        if os.path.exists(url.replace("file:///","")):
            box=MessageBox("询问","检测到已有工作目录，加载新的目录将清空之前的结果\n请问是否要载入新的工作路径？",self)
            box.exec_()
            if box.result()==0:
                return


        #设置工作路径后 开始画图了
        self.check_nep_result(path)
    def check_nep_result(self,path):
        """
        检查输出文件都有什么
        然后设置窗口布局
        :return:
        """
        self.dataset = NepTrainResultData.from_path(path)
        if self.dataset is None:
            # MessageManager.send_error_message(f"当前目录下并没有训练集xyz文件：")
            return
        self.path_label.setText(f"当前工作路径：{path}")
        self.path_label.setUrl(QUrl.fromLocalFile(path))
        self.graph_widget.set_dataset(self.dataset)

    def show_current_structure(self,current_index):
        atoms=self.dataset.get_atoms(current_index)

        self.show_struct_widget.show_atoms(atoms)
        self.struct_index_label.setText(f"当前结构(原始文件下标)：{current_index}")
        text_io=StringIO()
        atoms.write(text_io)

        text_io.seek(0)
        # comm=text.readlines()[1]
        comm=text_io.read()

        self.struct_info_edit.setPlainText(comm)
        text_io.close()