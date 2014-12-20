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

    def execute(self):
        report = open(os.path.join(self.workout, 'uptime.csv'), 'wb')
        report.write(codecs.BOM_UTF8)
        writer = csv.writer(report, quoting=csv.QUOTE_ALL)
        writer.writerow(['开机时间'])
        m = re.search('up time: (\d+):(\d{2}):(\d{2})', self.adb.shellreadline('uptime'))
        if m:
            g = m.groups()
            uptime = int(g[0]) * 3600 + int(g[1]) * 60 + int(g[2])
            writer.writerow(['{0:0.3f}s'.format(uptime + 2)])
        report.close()
