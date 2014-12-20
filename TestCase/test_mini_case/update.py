# -*- coding:UTF-8 -*-

import os
import sys
import time

class Executor(object):

    def __init__(self, adb, workout):
        self.adb = adb
        self.workout = workout

    def setup(self):
        pass

    def execute(self):
        model = self.adb.getprop('ro.product.model')
        builddir = open(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'config.txt'), 'r').readlines()[7].strip()
        updates = []

        for dirpath, dirnames, names in os.walk(builddir):
            if os.path.basename(dirpath) == model:
                for name in names:
                    updates.append(os.path.join(dirpath, name))

        if updates:
            self.adb.push(max(updates, key=os.path.basename), '/sdcard/update.zip')
            self.adb.shellreadlines('uiautomator runtest automator.jar -c cn.nubia.systemupdate.SystemUpdateTestCase#testLocalUpdate')
            time.sleep(30)
            self.adb.waitforboot()
