# -*- coding: utf-8 -*-

import codecs
import csv
import glob
import os
import re
import shutil
import subprocess
import sys
import threading
import time

import monkey

from PyQt4.QtGui import *

from common import workdir

class Executor(object):

    def __init__(self, main):
        self.adb = main.adb
        self.workout = main.workout
        self.retry = False

    def title(self):
        return u'流畅性测试'

    def retryChecked(self, checked):
        self.retry = checked

    def setup(self):
        page = QWizardPage()
        page.setTitle(self.title())
        page.setSubTitle(u'流畅性测试说明')

        check = QCheckBox(u'继续上一次的流畅性测试')
        check.toggled[bool].connect(self.retryChecked)

        layout = QVBoxLayout()
        layout.addWidget(check)
        page.setLayout(layout)

        return page

    def execute(self):
        self.workout = os.path.join(self.workout, 'scenes')
        shutil.rmtree(self.workout, ignore_errors=True)
        if not os.path.exists(self.workout):
            os.mkdir(self.workout)

        tmppath = '/data/local/tmp/scenes'

        self.adb.reboot(5)
        self.adb.kit.disablekeyguard()
        self.adb.kit.trackframetime()

        if not self.retry:
            self.adb.shell('rm -rf {0}'.format(tmppath))
            self.adb.shell('mkdir -p {0}'.format(tmppath))
            self.adb.push(os.path.join(workdir, 'scenes'), tmppath)
            self.adb.shell('chmod 755 {0}/*.sh'.format(tmppath))
            self.adb.push(os.path.join(workdir, 'busybox'), tmppath)
            self.adb.shell('chmod 755 {0}/busybox'.format(tmppath))

        self.adb.shellreadlines('sh {0}/main.sh'.format(tmppath))
        pid = self.adb.shellreadline('cat {0}/pid.txt'.format(tmppath))
        self.adb.waitforproc(pid)

        self.adb.pull('{0}/out'.format(tmppath), self.workout)
        time.sleep(3)

        for dirpath, dirnames, names in os.walk(self.workout):
            for name in names:
                if name == 'gfxinfo.txt':
                    monkey.gfxinfo(dirpath)
                elif name == 'skpinfo.txt':
                    monkey.skpinfo(dirpath)
