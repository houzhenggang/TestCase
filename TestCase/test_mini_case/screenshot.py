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
import startcompare
import adbkit

workdir = os.path.dirname(os.path.realpath(sys.argv[0]))

class Executor(object):

    def __init__(self, adb, workout):
        self.adb = adb
        self.workout = workout

    def setup(self):
        outpath = '/data/local/tmp/screenshot/out'
        self.adb.shell('mkdir -p {0}'.format(outpath))
        lines = self.adb.shellreadlines('ls -F {0}'.format(outpath))
        if len(lines) > 0:
            select = raw_input('Want to continue the last screenshot test? [N] ')
            print('')
            if select == 'Y' or select == 'y':
                self.restart = True
                return
        self.restart = False

    def execute(self):
        shutil.rmtree(self.workout, ignore_errors=True)
        if not os.path.exists(self.workout):
            os.mkdir(self.workout)
        if not os.path.exists(os.path.join(os.path.dirname(self.workout),'screenshot')):
            os.mkdir(os.path.join(os.path.dirname(self.workout),'screenshot'))
        uia = adbkit.Uia(self.adb,os.path.join(os.path.join(workdir, 'screenshot'), 'CompareTest.jar'))   
        uia.runtest('cn.nubia.test.ScreenShot', 'testDemo')
        print 'success screenshot'

        tmppath = '/data/local/tmp/screenshot'
        while True:
            for i in range(1):
                if self.adb.isuiautomator():
                    finish = False
                    break
                else:
                    finish = True
                    time.sleep(15)
            if finish:
                break
            time.sleep(30)

        self.adb.pull('{0}/out'.format(tmppath), os.path.join(os.path.dirname(self.workout),'screenshot'))
        print 'success pull chart'
        time.sleep(3)
        startcompare.main()
        uia.uninstall()
        

