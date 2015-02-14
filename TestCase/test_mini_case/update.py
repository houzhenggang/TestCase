# -*- coding: utf-8 -*-

import os
import sys
import time

from PyQt4.QtGui import *

from common import workdir

class Executor(object):

    def __init__(self, adb, workout):
        self.adb = adb
        self.workout = workout

    def title(self):
        return u'系统升级'

    def setup(self, win):
        configs = open(os.path.join(workdir, 'update', 'config.txt'), 'r')
        rootdir = configs.readlines()[1].strip()
        configs.close()

        self.buildfile = None
        sections = os.listdir(rootdir)
        if sections:
            item, ok = QInputDialog.getItem(win, u'系统升级', u'选择科室', sections, 0, False)
            if ok and item:
                builddir = os.path.join(rootdir, str(item))
                builddir = os.path.join(builddir, self.adb.getprop('ro.product.model'))

                if os.path.exists(builddir):
                    filelist = os.listdir(builddir)

                    if len(filelist) > 0:
                        self.buildfile = max(filelist, key=os.path.basename)
                        self.buildfile = os.path.join(builddir, self.buildfile)

    def execute(self):
        if self.buildfile:
            self.adb.push(self.buildfile, '/sdcard/update.zip')
            self.adb.kit.disablekeyguard()
            self.adb.kit.localupdate()
            time.sleep(30)
            self.adb.waitforboot()
