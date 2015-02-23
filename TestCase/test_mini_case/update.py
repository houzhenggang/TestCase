# -*- coding: utf-8 -*-

import os
import sys
import time

from PyQt4.QtGui import *

from common import workdir

class Executor(object):

    def __init__(self, main):
        self.adb = main.adb
        self.section = None

    def title(self):
        return u'系统升级'

    def sectionChanged(self, text):
        self.section = text

    def setup(self):
        with open(os.path.join(workdir, 'update', 'config.txt'), 'r') as f:
            self.rootdir = f.readlines()[1].strip()
        sections = os.listdir(self.rootdir)

        if sections:
            page = QWizardPage()
            page.setTitle(self.title())
            page.setSubTitle(u'系统升级说明')

            label = QLabel(u'选择科室')
            combo = QComboBox()
            combo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            combo.addItems(sections)
            combo.activated[str].connect(self.sectionChanged)

            self.section = str(combo.currentText())

            layout = QHBoxLayout()
            layout.addWidget(label)
            layout.addWidget(combo)
            page.setLayout(layout)

            return page

    def execute(self):
        if self.section:
            builddir = os.path.join(self.rootdir, self.section)
            builddir = os.path.join(builddir, self.adb.getprop('ro.product.model'))

            if os.path.exists(builddir):
                filelist = os.listdir(builddir)

                if filelist:
                    buildfile = max(filelist, key=os.path.basename)
                    buildfile = os.path.join(builddir, buildfile)
                    
                    self.adb.push(buildfile, '/sdcard/update.zip')
                    self.adb.kit.disablekeyguard()
                    self.adb.kit.localupdate()
                    time.sleep(30)
                    self.adb.waitforboot()
