# -*- coding: utf-8 -*-

import os
import sys
import time

from PyQt4.QtGui import *

from common import workdir

class Executor(object):

    def __init__(self, adb):
        self.adb = adb
        self.model = self.adb.getprop('ro.product.model')
        self.section = None
        self.update = None

    def title(self):
        return u'系统升级'

    def listUpdateDir(self):
        path = os.path.join(self.rootdir, self.section, self.model)
        if os.path.exists(path):
            updates = os.listdir(path)
        else:
            updates = []
        return sorted(updates, reverse=True)

    def sectionChanged(self, text):
        self.section = str(text)
        self.combo2.clear()
        self.combo2.addItems(self.listUpdateDir())
        self.update = str(self.combo2.currentText())

    def updateChanged(self, text):
        self.update = str(text)

    def setup(self):
        with open(os.path.join(workdir, 'update', 'config.txt'), 'r') as f:
            self.rootdir = f.readlines()[1].strip()

        if os.path.exists(self.rootdir):
            page = QWizardPage()
            page.setTitle(self.title())
            page.setSubTitle(u'本地升级包下载更新。')
            page.setFinalPage(True)

            label1 = QLabel(u'选择科室')
            self.combo1 = QComboBox()
            self.combo1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.combo1.addItems(os.listdir(self.rootdir))
            self.combo1.activated[str].connect(self.sectionChanged)
            self.section = str(self.combo1.currentText())
            label2 = QLabel(u'选择构建')
            self.combo2 = QComboBox()
            self.combo2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.combo2.addItems(self.listUpdateDir())
            self.combo2.activated[str].connect(self.updateChanged)
            self.update = str(self.combo2.currentText())

            layout1 = QHBoxLayout()
            layout1.addWidget(label1)
            layout1.addWidget(self.combo1)
            layout1.addStretch()
            layout2 = QHBoxLayout()
            layout2.addWidget(label2)
            layout2.addWidget(self.combo2)
            layout2.addStretch()

            layout = QVBoxLayout()
            layout.addLayout(layout1)
            layout.addLayout(layout2)
            page.setLayout(layout)

            return page

    def execute(self, log):
        if self.rootdir and self.section and self.model and self.update:
            updatefile = os.path.join(self.rootdir, self.section, self.model, self.update)
            if os.path.exists(updatefile):
                log(self.msg(u'正在复制升级包 {0}'.format(updatefile)))
                self.adb.push(updatefile, '/sdcard/update.zip')
                log(self.msg(u'正在执行本地安装包更新'))
                self.adb.kit.disablekeyguard()
                self.adb.kit.localupdate()
                log(self.msg(u'正在等待更新完成'))
                time.sleep(30)
                self.adb.waitforboot()
            else:
                log(self.msg(u'升级包 {0} 不存在'.format(updatefile)), 'red')

    def msg(self, text):
        return u'[{0}] {1}'.format(self.title(), text)
