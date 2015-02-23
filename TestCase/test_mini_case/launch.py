# -*- coding: utf-8 -*-

import codecs
import csv
import os
import re
import subprocess
import threading

class Executor(object):

    def __init__(self, main):
        self.adb = main.adb
        self.workout = main.workout
        self.packages = main.packages

    def title(self):
        return u'应用启动时间测试'

    def setup(self):
        self.count = 11

    def startactivity(self, package, activity, cleartask=True):
        lines = self.adb.startactivity('{0} -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -n {1}/{2}'.format(
                '--activity-clear-task' if cleartask else '-S', package, activity))
        self.adb.shell('input keyevent KEYCODE_BACK')
        for line in lines:
            if line.startswith('ThisTime:'):
                return int(line[10:])
        return 0

    def appinfo(self, package, title, activity):
        sample = []
        for i in range(self.count):
            sample.append(self.startactivity(package, activity, i > 0))
        self.adb.shell('am force-stop {0}'.format(package))

        line = self.adb.shellreadline('pm path {0}'.format(package))[8:]
        line = self.adb.shellreadline('ls -l {0}'.format(line))
        m = re.search('\s+(\d+)\s+', line)
        if m:
            size = m.groups()[0]
        else:
            size = '0'

        values = [x for x in sample[1:] if x > 0]
        values = values if values else [0]
        minval = min(values)
        maxval = max(values)
        if len(values) > 3:
            values.remove(minval)
            values.remove(maxval)
        avgval = round(float(sum(values)) / len(values), 1)
        return title, size, sample, minval, maxval, avgval

    def execute(self):
        self.adb.reboot(5)
        self.adb.kit.wakeup()
        self.adb.kit.disablekeyguard()

        report = open(os.path.join(self.workout, 'launch.csv'), 'wb')
        report.write(codecs.BOM_UTF8)
        writer = csv.writer(report, quoting=csv.QUOTE_ALL)
        titles = ['名称', '包大小']
        titles.extend(['第{0}次'.format(i) for i in range(1, self.count + 1)])
        titles.extend(['最小值', '最大值', '平均值'])
        writer.writerow(titles)

        for key, value in self.packages.items():
            for activity in value['activities']:
                if activity.get('category') == 'android.intent.category.LAUNCHER':
                    r = self.appinfo(key, activity['title'], activity['name'])
                    values = [r[0], r[1]]
                    values.extend(r[2])
                    values.extend([r[3], r[4], r[5]])
                    writer.writerow(values)
                    report.flush()
        report.close()
