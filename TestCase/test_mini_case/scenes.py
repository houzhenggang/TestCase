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

    def __init__(self, adb, workout):
        self.adb = adb
        self.workout = workout
        self.retry = False

    def title(self):
        return u'流畅性测试'

    def retryChecked(self, checked):
        self.retry = checked

    def setup(self):
        page = QWizardPage()
        page.setTitle(self.title())
        page.setSubTitle(u'模拟典型用户场景，抓取GPU绘制信息，测试开始后可离线。')
        page.setFinalPage(True)

        check = QCheckBox(u'继续上一次的流畅性测试')
        check.toggled[bool].connect(self.retryChecked)

        layout = QVBoxLayout()
        layout.addWidget(check)
        page.setLayout(layout)

        return page

    def execute(self, log):
        self.workout = os.path.join(self.workout, 'scenes')
        shutil.rmtree(self.workout, ignore_errors=True)
        if not os.path.exists(self.workout):
            os.mkdir(self.workout)

        tmppath = '/data/local/tmp/scenes'

        log(self.msg(u'正在重启'))
        self.adb.reboot(5)
        self.adb.kit.disablekeyguard()
        log(self.msg(u'正在开启GPU呈现模式分析'))
        self.adb.kit.trackframetime()

        if not self.retry:
            log(self.msg(u'正在复制测试脚本'))
            self.adb.shell('rm -rf {0}'.format(tmppath))
            self.adb.shell('mkdir -p {0}'.format(tmppath))
            self.adb.push(os.path.join(workdir, 'scenes'), tmppath)
            self.adb.shell('chmod 755 {0}/*.sh'.format(tmppath))
            self.adb.push(os.path.join(workdir, 'busybox'), tmppath)
            self.adb.shell('chmod 755 {0}/busybox'.format(tmppath))

        log(self.msg(u'正在执行测试脚本'))
        self.adb.shellreadlines('sh {0}/main.sh'.format(tmppath))
        pid = self.adb.shellreadline('cat {0}/pid.txt'.format(tmppath))
        self.adb.waitforproc(pid)

        log(self.msg('正在导出测试结果'))
        self.adb.pull('{0}/out'.format(tmppath), self.workout)
        time.sleep(3)

        log(self.msg('正在分析测试结果'))
        for dirpath, dirnames, names in os.walk(self.workout):
            for name in names:
                if name == 'gfxinfo.txt':
                    monkey.gfxinfo(dirpath)
                elif name == 'skpinfo.txt':
                    monkey.skpinfo(dirpath)

    def msg(self, text):
        return u'[{0}] {1}'.format(self.title(), text)
