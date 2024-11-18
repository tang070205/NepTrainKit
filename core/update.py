#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/11/14 17:17
# @Author  : 兵
# @email    : 1747193328@qq.com
import os
import subprocess
import traceback

import requests
from PySide6.QtCore import QThread, Signal, QObject
from PySide6.QtWidgets import QApplication
from qfluentwidgets import MessageBox

import utils
from core import MessageManager
from version import RELEASES_URL, RELEASES_API_URL, __version__


@utils.loghandle
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
        self.down_thread=utils.LoadingThread(self._parent,show_tip=True,title="下载中")

    def download(self,url):
        resp = requests.get(url, stream=True)
        # content_size = int(resp.headers['content-length'])

        count = 0

        with open("update.zip", "wb") as f:
            for i in resp.iter_content(1024):
                if i:
                    f.write(i)
                    count += len(i)

        self.download_success.emit()

    def _call_restart(self):

        box = MessageBox("重启询问？"  ,
                         "更新包下载完成！是否现在重启？\n如果取消，将下次打开软件的时候自动更新！",
                         self._parent
                         )
        box.yesButton.setText("更新")
        box.cancelButton.setText("取消")

        box.exec_()
        if box.result() == 0:
            return
        utils.unzip()





    def _check_update(self):
        MessageManager.send_info_message("检查更新中...")


        try:
            headers={
                "User-Agent": "Awesome-Octocat-App"
            }
            # version_info = requests.get(RELEASES_API_URL,headers=headers).json()
            # print(version_info)
            version_info={'url': 'https://api.github.com/repos/aboys-cb/NepTrainKit/releases/185649649',
             'assets_url': 'https://api.github.com/repos/aboys-cb/NepTrainKit/releases/185649649/assets',
             'upload_url': 'https://uploads.github.com/repos/aboys-cb/NepTrainKit/releases/185649649/assets{?name,label}',
             'html_url': 'https://github.com/aboys-cb/NepTrainKit/releases/tag/v1.2.0', 'id': 185649649,
             'author': {'login': 'aboys-cb', 'id': 63503186, 'node_id': 'MDQ6VXNlcjYzNTAzMTg2',
                        'avatar_url': 'https://avatars.githubusercontent.com/u/63503186?v=4', 'gravatar_id': '',
                        'url': 'https://api.github.com/users/aboys-cb', 'html_url': 'https://github.com/aboys-cb',
                        'followers_url': 'https://api.github.com/users/aboys-cb/followers',
                        'following_url': 'https://api.github.com/users/aboys-cb/following{/other_user}',
                        'gists_url': 'https://api.github.com/users/aboys-cb/gists{/gist_id}',
                        'starred_url': 'https://api.github.com/users/aboys-cb/starred{/owner}{/repo}',
                        'subscriptions_url': 'https://api.github.com/users/aboys-cb/subscriptions',
                        'organizations_url': 'https://api.github.com/users/aboys-cb/orgs',
                        'repos_url': 'https://api.github.com/users/aboys-cb/repos',
                        'events_url': 'https://api.github.com/users/aboys-cb/events{/privacy}',
                        'received_events_url': 'https://api.github.com/users/aboys-cb/received_events', 'type': 'User',
                        'user_view_type': 'public', 'site_admin': False}, 'node_id': 'RE_kwDONBrO_84LEMnx',
             'tag_name': 'v1.2.0', 'target_commitish': 'master', 'name': '', 'draft': False, 'prerelease': False,
             'created_at': '2024-11-15T13:39:32Z', 'published_at': '2024-11-15T15:04:47Z', 'assets': [
                {'url': 'https://api.github.com/repos/aboys-cb/NepTrainKit/releases/assets/207130929', 'id': 207130929,
                 'node_id': 'RA_kwDONBrO_84MWJEx', 'name': 'NepTrainKit.zip', 'label': None,
                 'uploader': {'login': 'aboys-cb', 'id': 63503186, 'node_id': 'MDQ6VXNlcjYzNTAzMTg2',
                              'avatar_url': 'https://avatars.githubusercontent.com/u/63503186?v=4', 'gravatar_id': '',
                              'url': 'https://api.github.com/users/aboys-cb', 'html_url': 'https://github.com/aboys-cb',
                              'followers_url': 'https://api.github.com/users/aboys-cb/followers',
                              'following_url': 'https://api.github.com/users/aboys-cb/following{/other_user}',
                              'gists_url': 'https://api.github.com/users/aboys-cb/gists{/gist_id}',
                              'starred_url': 'https://api.github.com/users/aboys-cb/starred{/owner}{/repo}',
                              'subscriptions_url': 'https://api.github.com/users/aboys-cb/subscriptions',
                              'organizations_url': 'https://api.github.com/users/aboys-cb/orgs',
                              'repos_url': 'https://api.github.com/users/aboys-cb/repos',
                              'events_url': 'https://api.github.com/users/aboys-cb/events{/privacy}',
                              'received_events_url': 'https://api.github.com/users/aboys-cb/received_events',
                              'type': 'User', 'user_view_type': 'public', 'site_admin': False},
                 'content_type': 'application/x-zip-compressed', 'state': 'uploaded', 'size': 99321296,
                 'download_count': 14, 'created_at': '2024-11-17T15:35:14Z', 'updated_at': '2024-11-17T15:36:08Z',
                 'browser_download_url': 'https://github.com/aboys-cb/NepTrainKit/releases/download/v1.2.0/NepTrainKit.zip'}],
             'tarball_url': 'https://api.github.com/repos/aboys-cb/NepTrainKit/tarball/v1.2.0',
             'zipball_url': 'https://api.github.com/repos/aboys-cb/NepTrainKit/zipball/v1.2.0',
             'body': '新增删除后撤销 #2 '}

            self.version.emit(version_info)

        except:
            self.logger.error(traceback.format_exc())
            MessageManager.send_error_message("网络异常！")



    def _check_update_call_back(self,version_info):


        if "message" in version_info:
            MessageManager.send_warning_message(version_info['message'])
            return
        if version_info['tag_name'][1:] == __version__:
            MessageManager.send_success_message("当前版本已经是最新版了！")

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
        self.down_thread.start_work(self.download,version_info["assets"][0]["browser_download_url"])


    def check_update(self):
        self.update_thread.start_work(self._check_update)

