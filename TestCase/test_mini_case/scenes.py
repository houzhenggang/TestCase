# -*- coding:UTF-8 -*-

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

class Executor(object):

    def __init__(self, adb, workout):
        self.adb = adb
        self.workout = workout

    def setup(self):
        outpath = '/data/local/tmp/scenes/out'
        self.adb.shell('mkdir -p {0}'.format(outpath))
        lines = self.adb.shellreadlines('ls -F {0}'.format(outpath))
        if len(lines) > 0:
            select = raw_input('Want to continue the last fluency test? [N] ')
            print('')
            if select == 'Y' or select == 'y':
                self.restart = True
                return
        self.restart = False

    def execute(self):
        self.workout = os.path.join(self.workout, 'scenes')
        shutil.rmtree(self.workout, ignore_errors=True)
        if not os.path.exists(self.workout):
            os.mkdir(self.workout)

        self.adb.reboot(30)
        self.adb.kit.disablekeyguard()
        self.adb.uia.runtest('com.android.settings.DevelopmentSettingsTestCase', 'testTrackFrameTimeDumpsysGfxinfo')

        tmppath = '/data/local/tmp/scenes'
        if not self.restart:
            workdir = os.path.dirname(os.path.realpath(sys.argv[0]))
            self.adb.waitforboot()
            self.adb.shell('rm -rf {0}'.format(tmppath))
            self.adb.shell('mkdir -p {0}'.format(tmppath))
            self.adb.push(os.path.join(workdir, 'scenes'), tmppath)
            self.adb.shell('chmod 755 {0}/*.sh'.format(tmppath))
            self.adb.push(os.path.join(workdir, 'busybox'), tmppath)
            self.adb.shell('chmod 755 {0}/busybox'.format(tmppath))

        self.adb.shellreadline('{0}/busybox nohup sh {0}/main.sh &'.format(tmppath))

        while True:
            self.adb.waitforboot()
            for i in range(3):
                if self.adb.isuiautomator():
                    finish = False
                    break
                else:
                    finish = True
                    time.sleep(5)
            if finish:
                break
            time.sleep(30)

        self.adb.waitforboot()
        self.adb.pull('{0}/out'.format(tmppath), self.workout)
        time.sleep(3)

        for dirpath, dirnames, names in os.walk(self.workout):
            for name in names:
                if name == 'gfxinfo.txt':
                    monkey.gfxinfo(dirpath)
                elif name == 'skpinfo.txt':
                    monkey.skpinfo(dirpath)
