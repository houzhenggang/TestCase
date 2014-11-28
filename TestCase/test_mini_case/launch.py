# -*- coding:UTF-8 -*-

import codecs
import os
import re

def startactivity(package, activity, cleartask=True):
    cmd = 'adb shell am start --user 0 -W {2} -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -n {0}/{1}'.format(
            package, activity, '--activity-clear-task' if cleartask else '')
    lines = os.popen(cmd).readlines()
    for line in lines:
        if line.startswith('ThisTime:'):
            return int(line[10:])
    return 0

def appinfo(package, title, activity):
    os.system('adb shell am force-stop {0}'.format(package))
    t = (
        startactivity(package, activity, False),
        startactivity(package, activity),
        startactivity(package, activity),
        startactivity(package, activity),
        startactivity(package, activity),
        startactivity(package, activity)
    )
    os.system('adb shell am force-stop {0}'.format(package))

    line = os.popen('adb shell pm path {0}'.format(package)).readline().strip()[8:]
    line = os.popen('adb shell ls -l {0}'.format(line)).readline().strip()
    m = re.search('\s+(\d+)\s+', line)
    if m:
        size = m.groups()[0]
    else:
        size = '0'

    return (title, size, t, min(t[1:]), max(t[1:]), round(float(sum(t[1:])) / (len(t) - 1), 1))

def launch(workout, packages, launchers):
    report = open(os.path.join(workout, 'launch.csv'), 'w')
    report.write(codecs.BOM_UTF8)
    report.write('名称,包大小,第一次,第二次,第三次,第四次,第五次,第六次,最小值,最大值,平均值\n')

    for package in packages:
        for item in launchers[package]:
            result = appinfo(package, item['title'], item['activity'])
            report.write('{0[0]},{0[1]},{0[2][0]},{0[2][1]},{0[2][2]},{0[2][3]},{0[2][4]},{0[2][5]},{0[3]},{0[4]},{0[5]}\n'.format(result))
            report.flush()
    report.close()
