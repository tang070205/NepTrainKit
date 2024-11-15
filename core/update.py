#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/11/14 17:17
# @Author  : 兵
# @email    : 1747193328@qq.com
import traceback

import requests
from PySide6.QtCore import QThread,Signal
from qfluentwidgets import MessageBox

import utils
from core import MessageManager
from version import RELEASES_URL
@utils.loghandle
class UpdateWoker(QThread):
    version=Signal(dict)
    def __init__(self,parent):
        self._parent=parent
        super(UpdateWoker, self).__init__()
        self.func=self._check_update
        self.version.connect(self._check_update_call_back)


    def run(self):
        self.func()


    def _update(self):
        pass

    def update(self):
        self.func=self._update
        self.start()
    def _check_update(self):
        MessageManager.send_info_message("检查更新中...")

        RELEASES_URL = "https://api.github.com/repos/brucefan1983/GPUMD/releases/latest"
        try:
            headers={
                "User-Agent": "Awesome-Octocat-App"
            }
            version_info = requests.get(RELEASES_URL,headers=headers).json()
            self.version.emit(version_info)

        except:
            self.logger.error(traceback.format_exc())
            MessageManager.send_error_message("网络异常！")



    def _check_update_call_back(self,version_info):


        if "message" in version_info:
            MessageManager.send_warning_message(version_info['message'])
            return
        box = MessageBox("检测到新版本：" + version_info["name"] + version_info["tag_name"],
                         version_info["body"],
                         self._parent
                         )
        box.yesButton.setText("更新")
        box.cancelButton.setText("取消")

        box.exec_()
        if box.result() == 0:
            return

        self.update()
    def check_update(self):
        self.func=self._check_update
        self.start()