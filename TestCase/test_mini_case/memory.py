# -*- coding:UTF-8 -*-

import codecs
import csv
import os
import re
import time

class Executor(object):

    def __init__(self, adb, workout):
        self.adb = adb
        self.workout = workout

    def setup(self):
        pass

    def procs(self):
        start = False
        usrprocs = []
        sysprocs = []
        for line in self.adb.shellreadlines('dumpsys meminfo'):
            if line.startswith('Total PSS by process:'):
                start = True
            elif line.startswith('Total PSS by OOM adjustment:'):
                start = False
            elif line.startswith('Total PSS by category:'):
                start = False
            elif start:
                m = re.search('([1-9][0-9]*) kB: (\S+) \(pid (\d+)', line)
                if m:
                    g = m.groups()
                    if g[1].startswith('cn.nubia') or g[1].startswith('com.android'):
                        usrprocs.append(g)
                    else:
                        sysprocs.append(g)
        sorted(usrprocs)
        sorted(sysprocs)
        return {'usr': usrprocs, 'sys': sysprocs}

    def execute(self):
        pl = []
        pl.append(self.procs())
        self.adb.reboot()
        pl.append(self.procs())
        self.adb.reboot()
        pl.append(self.procs())
        self.adb.shellreadlines('uiautomator runtest automator.jar -c com.android.systemui.MultiTaskTestCase#testRecycle')
        pl.append(self.procs())
        print(pl)

if __name__ == '__main__':
    import adbkit
    adb = adbkit.Adb('0123456789')
    executor = Executor(adb, None)
    executor.execute()
