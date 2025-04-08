#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/11/14 17:17
# @Author  : 兵
# @email    : 1747193328@qq.com
import sys
import traceback

import requests
from PySide6.QtCore import Signal, QObject
from loguru import logger
from qfluentwidgets import MessageBox

from NepTrainKit import utils
from NepTrainKit.core import MessageManager
from NepTrainKit.version import RELEASES_API_URL, __version__, UPDATE_FILE


class UpdateWoker( QObject):
    version=Signal(dict)
    download_success=Signal( )
    def __init__(self,parent):
        self._parent=parent
        super().__init__(parent)

        self.func=self._check_update
        self.version.connect(self._check_update_call_back)
        self.download_success.connect(self._call_restart)
        self.update_thread=utils.LoadingThread(self._parent,show_tip=False)
        self.down_thread=utils.LoadingThread(self._parent,show_tip=True,title="Downloading")

    def download(self,url):
        # url="https://github.moeyy.xyz/"+url
        resp = requests.get(url, stream=True)
        # content_size = int(resp.headers['content-length'])

        count = 0

        with open(UPDATE_FILE, "wb") as f:
            for i in resp.iter_content(1024):
                if i:
                    f.write(i)
                    count += len(i)

        self.download_success.emit()

    def _call_restart(self):

        box = MessageBox("Do you want to restart？"  ,
                         "Update package downloaded successfully! Would you like to restart now?\nIf you cancel, the update will be applied automatically the next time you open the software.",
                         self._parent
                         )
        box.yesButton.setText("Update")
        box.cancelButton.setText("Cancel")

        box.exec_()
        if box.result() == 0:
            return
        utils.unzip()





    def _check_update(self):
        MessageManager.send_info_message("Checking for updates, please wait...")


        try:
            headers={
                "User-Agent": "Awesome-Octocat-App"
            }
            version_info = requests.get(RELEASES_API_URL,headers=headers).json()
            # print(version_info)


            self.version.emit(version_info)

        except:
            logger.error(traceback.format_exc())
            MessageManager.send_error_message("Network error!")



    def _check_update_call_back(self,version_info):


        if "message" in version_info:
            MessageManager.send_warning_message(version_info['message'])
            return
        if version_info['tag_name'][1:] == __version__:
            MessageManager.send_success_message("You are already using the latest version!")

            return
        box = MessageBox("检测到新版本：" + version_info["name"] + version_info["tag_name"],
                         version_info["body"],
                         self._parent
                         )
        box.yesButton.setText("Update")
        box.cancelButton.setText("Cancel")

        box.exec_()
        if box.result() == 0:
            return

        for assets in version_info["assets"]:

            if sys.platform in assets["name"] and "NepTrainKit" in assets["name"]:

                self.down_thread.start_work(self.download,assets["browser_download_url"])
                return
        MessageManager.send_warning_message("No update package available for your system. Please download it manually!")



    def check_update(self):
        self.update_thread.start_work(self._check_update)

