#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/10/21 19:44
# @Author  : 兵
# @email    : 1747193328@qq.com
import traceback

import requests
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QWidget
from qfluentwidgets import SettingCardGroup, HyperlinkCard, PrimaryPushSettingCard, ExpandLayout, MessageBox
from qfluentwidgets import FluentIcon as FIF

from NepTrainKit import utils
from NepTrainKit.core import MessageManager
from NepTrainKit.core.update import UpdateWoker
from NepTrainKit.version import HELP_URL, FEEDBACK_URL, __version__, YEAR, AUTHOR, RELEASES_URL

@utils.loghandle
class SettingsWidget(QWidget):
    def __init__(self,parent):

        super().__init__(parent)
        self.setObjectName('SettingsWidget')
        self.expand_layout = ExpandLayout(self)
        self.setLayout(self.expand_layout)
        self.aboutGroup = SettingCardGroup("关于", self)
        self.helpCard = HyperlinkCard(
            HELP_URL,
             '打开帮助页面' ,
            FIF.HELP,
             '帮助' ,
             '发现新功能并学习有关NepTrainKit的有用提示' ,
            self.aboutGroup
        )
        self.feedbackCard = PrimaryPushSettingCard(
            "提供反馈",
            FIF.FEEDBACK,
            "提供反馈",

            '通过提供反馈帮助我们改进NepTrainKit',
            self.aboutGroup
        )
        self.aboutCard = PrimaryPushSettingCard(
            '检查更新',
            FIF.INFO,
            "关于",
            '© ' + '版权' + f" {YEAR}, {AUTHOR}. " +
            "版本" + f" {__version__}",
            self.aboutGroup
        )
        self.aboutGroup.addSettingCard(self.helpCard)
        self.aboutGroup.addSettingCard(self.feedbackCard)
        self.aboutGroup.addSettingCard(self.aboutCard)
        self.init_layout()
        self.init_signal()
    def init_layout(self):
        self.expand_layout.setSpacing(28)
        self.expand_layout.setContentsMargins(60, 10, 60, 0)
        self.expand_layout.addWidget(self.aboutGroup)
    def init_signal(self):
        self.aboutCard.clicked.connect(self.check_update)

        # self.aboutCard.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(RELEASES_URL)))
        self.feedbackCard.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(FEEDBACK_URL)))

    def check_update(self):
        UpdateWoker(self).check_update()
