# -*- coding:UTF-8 -*-

import codecs
import csv
import os
import re
import shutil
import sys
import threading
import time

def stat(outdir):
    list = []
    output = open(os.path.join(outdir, 'meminfo.txt'), 'r')
    for line in output.readlines():
        if line.strip().startswith('Native'):
            data = {}
            m = re.match('Native[ Heap]+\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)', line.strip())
            if m:
                data['native heap'] = m.groups()[4]
                data['native used'] = m.groups()[5]
        elif line.strip().startswith('Dalvik'):
            m = re.match('Dalvik[ Heap]+\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)', line.strip())
            if m:
                data['dalvik heap'] = m.groups()[4]
                data['dalvik used'] = m.groups()[5]
        elif line.strip().startswith('TOTAL'):
            m = re.match('TOTAL\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)', line.strip())
            if m:
                data['pss total']   = m.groups()[0]
                data['pss private'] = m.groups()[1]
            if not data.get('pss total', '0') == '0':
                list.append(data)
    output.close()

    report = open(os.path.join(outdir, unicode('应用内存占用', 'utf-8').encode('gb2312') + '.csv'), 'wb')
    report.write(codecs.BOM_UTF8)
    writer = csv.writer(report, quoting=csv.QUOTE_ALL)
    writer.writerow(['pss total', 'pss private', 'dalvik heap', 'dalvik used', 'native heap', 'native used'])
    for data in list:
        writer.writerow([data.get('pss total', '0'), data.get('pss private', '0'), data.get('dalvik heap', '0'),
                data.get('dalvik used', '0'), data.get('native heap', '0'), data.get('native used', '0')])
    report.close()

    crashs = anrs = 0
    output = os.path.join(outdir, 'monkey.txt')
    if os.path.exists(output):
        output = open(output, 'r')
        for line in output.readlines():
            if line.find('// CRASH:') > -1:
                crashs += 1
            elif line.find('// NOT RESPONDING:') > -1:
                anrs += 1
        output.close()

    file = os.path.join(os.path.dirname(outdir), unicode('应用内存占用汇总表', 'utf-8').encode('gb2312') + '.csv')
    if os.path.exists(file):
        report = open(file, 'ab+')
        writer = csv.writer(report, quoting=csv.QUOTE_ALL)
    else:
        report = open(file, 'wb')
        report.write(codecs.BOM_UTF8)
        writer = csv.writer(report, quoting=csv.QUOTE_ALL)
        writer.writerow(['进程名', '内存最大值', '内存最小值', '内存平均值', 'crash次数', 'ANR次数'])
    pss = [int(x.get('pss total', '0')) for x in list]
    if pss:
        writer.writerow([os.path.basename(outdir), max(pss), min(pss), sum(pss) / len(pss), crashs, anrs])
    else:
        writer.writerow([os.path.basename(outdir), 0, 0, 0, crashs, anrs])
    report.close()

class Executor(object):

    def __init__(self, adb, workout, packages):
        self.adb = adb
        self.workout = workout
        self.packages = packages

    def setup(self):
        outpath = '/data/local/tmp/memory/out'
        self.adb.shell('mkdir -p {0}'.format(outpath))
        lines = self.adb.shellreadlines('ls -F {0}'.format(outpath))
        if len(lines) > 0:
            select = raw_input('Want to continue the last memory test? [N] ')
            print('')
            if select == 'Y' or select == 'y':
                self.restart = True
                return
        self.restart = False

    def meminfo(self, name):
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
            elif line.startswith('Total RAM:'):
                m = re.search('Total RAM: (\d+) kB', line)
                if m:
                    total = m.groups()[0]
            elif line.startswith(' Free RAM:'):
                m = re.search('Free RAM: (\d+) kB', line)
                if m:
                    free = m.groups()[0]
            elif line.startswith(' Used RAM:'):
                m = re.search('Used RAM: (\d+) kB', line)
                if m:
                    used = m.groups()[0]
            elif start:
                m = re.search('([1-9][0-9]*) kB: (\S+) \(pid (\d+)', line)
                if m:
                    g = m.groups()
                    if g[1].startswith('cn.nubia') or g[1].startswith('com.android'):
                        usrprocs.append(g)
                    else:
                        sysprocs.append(g)
        sorted(sysprocs)
        sorted(usrprocs)

        report = open(os.path.join(self.workout, unicode(name, 'utf-8').encode('gb2312') + '.csv'), 'wb')
        report.write(codecs.BOM_UTF8)
        writer = csv.writer(report, quoting=csv.QUOTE_ALL)
        writer.writerow(['系统进程数', '应用进程数', '合计'])
        writer.writerow([len(sysprocs), len(usrprocs), len(sysprocs) + len(usrprocs)])
        writer.writerow(['总内存', '已用内存'])
        writer.writerow([total, used])
        writer.writerow(['系统进程名', '系统进程内存'])
        for x, y, z in sysprocs:
            writer.writerow([y, x])
        writer.writerow(['应用进程名', '应用进程内存'])
        for x, y, z in usrprocs:
            writer.writerow([y, x])
        report.close()

    def execute(self):
        self.workout = os.path.join(self.workout, 'memory')
        tmppath = '/data/local/tmp/memory'

        if self.restart:
            if not os.path.exists(self.workout):
                os.mkdir(self.workout)
        else:
            shutil.rmtree(self.workout, ignore_errors=True)
            if not os.path.exists(self.workout):
                os.mkdir(self.workout)

            self.adb.reboot(30)
            self.adb.kit.disablekeyguard()

            time.sleep(5)
            self.meminfo('开机启动进程及内存占用')

            pkgpath = os.path.join(self.workout, 'packages.txt')
            pkgfile = open(pkgpath, 'wb')
            pkgfile.write('{0}\n'.format('\n'.join(self.packages.keys())))
            pkgfile.close()

            self.adb.shell('rm -rf {0}'.format(tmppath))
            self.adb.shell('mkdir -p {0}'.format(tmppath))
            workdir = os.path.dirname(os.path.realpath(sys.argv[0]))
            self.adb.push(os.path.join(workdir, 'memory'), tmppath)
            self.adb.shell('chmod 755 {0}/*.sh'.format(tmppath))
            self.adb.push(os.path.join(workdir, 'busybox'), tmppath)
            self.adb.shell('chmod 755 {0}/busybox'.format(tmppath))
            self.adb.push(pkgpath, tmppath)
            os.remove(pkgpath)

            self.adb.shellreadline('{0}/busybox nohup sh {0}/main.sh &'.format(tmppath))

            while True:
                self.adb.waitforboot()
                for i in range(3):
                    if self.adb.ismonkey() or self.adb.pidof('uiautomator'):
                        finish = False
                    else:
                        finish = True
                        time.sleep(5)
                if finish:
                    break
                time.sleep(30)

        self.adb.waitforboot()
        self.adb.pull('{0}/out'.format(tmppath), self.workout)
        time.sleep(3)

        for dirpath, dirnames, names in os.walk(self.workout):
            for name in names:
                if name == 'meminfo.txt':
                    stat(dirpath)

        self.adb.kit.disablekeyguard()
        if int(self.adb.getprop('ro.build.version.sdk')) > 20:
            self.adb.uia.runtest('com.android.systemui.NotificationTestCase', 'testClickRecycle')
        else:
            self.adb.uia.runtest('com.android.systemui.MultiTaskTestCase', 'testRecycle')
        self.meminfo('后台常驻进程及内存占用')
