# -*- coding:UTF-8 -*-

import codecs
import csv
import os
import re

import adbkit as adb

def startactivity(package, activity, cleartask=True):
    cmd = 'adb -s {3} shell am start --user 0 -W {2} -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -n {0}/{1}'.format(
            package, activity, '--activity-clear-task' if cleartask else '', adb.sno)
    lines = os.popen(cmd).readlines()
    for line in lines:
        if line.startswith('ThisTime:'):
            return int(line[10:])
    return 0

def appinfo(package, title, activity):
    os.system('adb -s {0} shell am force-stop {1}'.format(adb.sno, package))
    t = (
        startactivity(package, activity, False),
        startactivity(package, activity),
        startactivity(package, activity),
        startactivity(package, activity),
        startactivity(package, activity),
        startactivity(package, activity)
    )
    os.system('adb -s {0} shell am force-stop {1}'.format(adb.sno, package))

    line = os.popen('adb -s {0} shell pm path {1}'.format(adb.sno, package)).readline().strip()[8:]
    line = os.popen('adb -s {0} shell ls -l {1}'.format(adb.sno, line)).readline().strip()
    m = re.search('\s+(\d+)\s+', line)
    if m:
        size = m.groups()[0]
    else:
        size = '0'

    valid = [x for x in t[1:] if x > 0]
    return (title, size, t, min(valid), max(valid), round(float(sum(valid)) / len(valid), 1))

def execute(workout, packages, launchers):
    report = open(os.path.join(workout, 'launch.csv'), 'wb')
    report.write(codecs.BOM_UTF8)
    writer = csv.writer(report, quoting=csv.QUOTE_ALL)
    writer.writerow(['名称', '包大小', '第一次', '第二次', '第三次', '第四次', '第五次', '第六次', '最小值', '最大值', '平均值'])

    for package in packages:
        for item in launchers[package]:
            r = appinfo(package, item['title'], item['activity'])
            writer.writerow([r[0], r[1], r[2][0], r[2][1], r[2][2], r[2][3], r[2][4], r[2][5], r[3], r[4], r[5]])
            report.flush()
    report.close()
