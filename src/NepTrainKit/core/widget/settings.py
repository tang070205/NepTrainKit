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
from qfluentwidgets import SettingCardGroup, HyperlinkCard, PrimaryPushSettingCard, ExpandLayout, MessageBox, \
    OptionsSettingCard, OptionsConfigItem, OptionsValidator, EnumSerializer
from qfluentwidgets import FluentIcon as FIF

from NepTrainKit import utils
from NepTrainKit.core import MessageManager, Config
from NepTrainKit.core.custom_widget.settingscard import MyComboBoxSettingCard
from NepTrainKit.core.update import UpdateWoker
from NepTrainKit.version import HELP_URL, FEEDBACK_URL, __version__, YEAR, AUTHOR, RELEASES_URL
from NepTrainKit.core.types import ForcesMode
class SettingsWidget(QWidget):
    def __init__(self,parent):

        super().__init__(parent)
        self.setObjectName('SettingsWidget')
        self.expand_layout = ExpandLayout(self)
        self.setLayout(self.expand_layout)
        self.personal_group = SettingCardGroup(
             'Personalization' , self)


        default_forces = Config.get("widget","forces_data","Raw")
        if default_forces=="Row":
            #没什么用 替换以前的坑 之前写错单词了
            default_forces="Raw"
        self.optimization_forces_card = MyComboBoxSettingCard(
            OptionsConfigItem("forces","forces",ForcesMode(default_forces),OptionsValidator(ForcesMode), EnumSerializer(ForcesMode)),
            FIF.BRUSH,
            'Force data format',
            "Streamline data and speed up drawing",
            texts=[
                "Raw","Norm"
            ],
            default=default_forces,
            parent=self.personal_group
        )



        self.about_group = SettingCardGroup("About", self)
        self.help_card = HyperlinkCard(
            HELP_URL,
             'Open Help Page' ,
            FIF.HELP,
             'Help' ,
             'Discover new features and learn useful tips about NepTrainKit.' ,
            self.about_group
        )
        self.feedback_card = PrimaryPushSettingCard(
            "Submit Feedback",
            FIF.FEEDBACK,
            "Submit Feedback",

            'Help us improve NepTrainKit by providing feedback.',
            self.about_group
        )
        self.about_card = PrimaryPushSettingCard(
            'Check for Updates',
            FIF.INFO,
            "About",
            'Copyright ©' + f" {YEAR}, {AUTHOR}. " +
            "Version" + f" {__version__}",
            self.about_group
        )
        self.about_group.addSettingCard(self.help_card)
        self.about_group.addSettingCard(self.feedback_card)
        self.about_group.addSettingCard(self.about_card)
        self.init_layout()
        self.init_signal()
    def init_layout(self):
        self.expand_layout.setSpacing(28)
        self.expand_layout.setContentsMargins(60, 10, 60, 0)
        self.expand_layout.addWidget(self.personal_group)
        self.expand_layout.addWidget(self.about_group)


        self.personal_group.addSettingCard(self.optimization_forces_card)


    def init_signal(self):

        self.optimization_forces_card.optionChanged.connect(lambda option:Config.set("widget","forces_data",option ))
        self.about_card.clicked.connect(self.check_update)

        # self.about_card.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(RELEASES_URL)))
        self.feedback_card.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(FEEDBACK_URL)))

    def check_update(self):
        UpdateWoker(self).check_update()
