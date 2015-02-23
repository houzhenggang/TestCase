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

from PyQt4.QtGui import *

workdir = os.path.dirname(os.path.realpath(sys.argv[0]))

class Executor(object):

    def __init__(self, main):
        self.adb = main.adb
        self.workout = main.workout

    def title(self):
        return u'截图比较测试'

    def setup(self):
        pass

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
        self.adb.pull('{0}/out'.format(tmppath), os.path.join(os.path.dirname(self.workout),'screenshot'))
        print 'success pull chart'
        time.sleep(3)
        startcompare.main()
        uia.uninstall()
        

