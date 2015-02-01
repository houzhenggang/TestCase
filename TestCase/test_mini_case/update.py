# -*- coding: utf-8 -*-

import os
import sys
import time

from Tkinter import *

from common import workdir

class Executor(object):

    def __init__(self, adb, workout):
        self.adb = adb
        self.workout = workout
        self.buildfile = None

    def setup(self):
        configs = open(os.path.join(workdir, 'update', 'config.txt'), 'r')
        rootdir = configs.readlines()[1].strip()
        configs.close()

        sections = os.listdir(rootdir)
        if sections:
            root = Tk()
            root.title('系统升级')
            frame = LabelFrame(root, text='请选择部门科室')
            var = IntVar()
            for i in range(len(sections)):
                Radiobutton(frame, text=sections[i], variable=var, value=i).pack(anchor=W)
            frame.pack(anchor=W)
            Button(root, text='确定', command=root.destroy).pack(anchor=E)
            root.mainloop()

            builddir = os.path.join(rootdir, sections[var.get()])
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
