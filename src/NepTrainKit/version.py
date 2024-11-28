#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/10/17 13:33
# @Author  : 兵
# @email    : 1747193328@qq.com
import sys
__version__="1.4.4"

OWNER="aboys-cb"
REPO="NepTrainKit"
HELP_URL=f"https://github.com/{OWNER}/{REPO}"
FEEDBACK_URL=f"https://github.com/{OWNER}/{REPO}/issues"
RELEASES_URL=f"https://github.com/{OWNER}/{REPO}/releases"

RELEASES_API_URL=f"https://api.github.com/repos/{OWNER}/{REPO}/releases/latest"


YEAR=2024
AUTHOR="陈成兵"
if sys.platform=="win32":
    UPDATE_FILE="update.zip"
    UPDATE_EXE="update.exe"
    NepTrainKit_EXE="NepTrainKit.exe"
else:
    UPDATE_FILE="update.tar.gz"
    UPDATE_EXE="update.bin"
    NepTrainKit_EXE="NepTrainKit.bin"
