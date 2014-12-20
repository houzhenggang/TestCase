# -*- coding:UTF-8 -*-

import codecs
import csv
import os
import re
import subprocess
import threading

class Executor(object):

    def __init__(self, adb, workout):
        self.adb = adb
        self.workout = workout

    def startactivity(self, package, activity, cleartask=True):
        cmd = 'am start --user 0 -W {0} -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -n {1}/{2}'.format(
                '--activity-clear-task' if cleartask else '', package, activity)
        p = self.adb.shellopen(cmd)
        y = lambda x: x.terminate()
        t = threading.Timer(5, y, args=(p,))
        t.start()
        lines = p.stdout.readlines()
        t.cancel()
        for line in lines:
            if line.startswith('ThisTime:'):
                return int(line[10:])
        return 0

    def appinfo(self, package, title, activity):
        self.adb.shell('am force-stop {0}'.format(package))
        t = (
            self.startactivity(package, activity, False),
            self.startactivity(package, activity),
            self.startactivity(package, activity),
            self.startactivity(package, activity),
            self.startactivity(package, activity),
            self.startactivity(package, activity)
        )
        self.adb.shell('am force-stop {0}'.format(package))

        line = self.adb.shellreadline('pm path {0}'.format(package))[8:]
        line = self.adb.shellreadline('ls -l {0}'.format(line))
        m = re.search('\s+(\d+)\s+', line)
        if m:
            size = m.groups()[0]
        else:
            size = '0'

        valid = [x for x in t[1:] if x > 0]
        valid = valid if valid else [0]
        return (title, size, t, min(valid), max(valid), round(float(sum(valid)) / len(valid), 1))

    def execute(self, packages, launchers):
        report = open(os.path.join(self.workout, 'launch.csv'), 'wb')
        report.write(codecs.BOM_UTF8)
        writer = csv.writer(report, quoting=csv.QUOTE_ALL)
        writer.writerow(['名称', '包大小', '第一次', '第二次', '第三次', '第四次', '第五次', '第六次', '最小值', '最大值', '平均值'])

        for package in packages:
            for item in launchers[package]:
                r = self.appinfo(package, item['title'], item['activity'])
                writer.writerow([r[0], r[1], r[2][0], r[2][1], r[2][2], r[2][3], r[2][4], r[2][5], r[3], r[4], r[5]])
                report.flush()
        report.close()
