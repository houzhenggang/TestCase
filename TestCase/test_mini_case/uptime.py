# -*- coding:UTF-8 -*-

import codecs
import csv
import os
import re
import time

import adbkit as adb

def reboot():
    os.system('adb -s {0} reboot'.format(adb.sno))
    os.system('adb -s {0} wait-for-device'.format(adb.sno))
    while os.popen('adb -s {0} shell getprop sys.boot_completed'.format(adb.sno)).readline().strip() != '1':
        time.sleep(0.1)

def execute(workout):
    report = open(os.path.join(workout, 'uptime.csv'), 'wb')
    report.write(codecs.BOM_UTF8)
    writer = csv.writer(report, quoting=csv.QUOTE_ALL)
    writer.writerow(['开机时间'])
    m = re.search('up time: (\d+):(\d{2}):(\d{2})', os.popen('adb -s {0} shell uptime'.format(adb.sno)).readline())
    if m:
        g = m.groups()
        uptime = int(g[0]) * 3600 + int(g[1]) * 60 + int(g[2])
        writer.writerow(['{0:0.3f}s'.format(uptime + 2)])
    report.close()
