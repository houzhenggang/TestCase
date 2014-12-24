# -*- coding:UTF-8 -*-

import codecs
import csv
import os
import re
import shutil
import sys
import threading
import time

import adbkit
import monkey

class DumpsysMeminfoThread(threading.Thread):

    def __init__(self, adb, outdir, package, interval):
        threading.Thread.__init__(self)
        self.adb = adb
        self.outdir = outdir
        self.package = package
        self.interval = interval
        self.loop = True

    def run(self):
        self.memlist = []
        report = open(os.path.join(self.outdir, unicode('应用内存占用.csv', 'utf-8')), 'wb')
        report.write(codecs.BOM_UTF8)
        writer = csv.writer(report, quoting=csv.QUOTE_ALL)
        writer.writerow(['pss total', 'pss private', 'dalvik heap', 'dalvik used', 'native heap', 'native used'])
        while self.loop:
            time.sleep(self.interval)
            data = {}
            for line in self.adb.shellreadlines('dumpsys meminfo {0}'.format(self.package)):
                if line.strip().startswith('Native'):
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
            self.memlist.append(data)
            writer.writerow([data.get('pss total', '0'), data.get('pss private', '0'), data.get('dalvik heap', '0'),
                    data.get('dalvik used', '0'), data.get('native heap', '0'), data.get('native used', '0')])
            report.flush()
        report.close()

    def stat(self):
        pss = [int(x.get('pss total', '0')) for x in self.memlist]
        if pss:
            return (max(pss), min(pss), sum(pss) / len(pss))
        else:
            return (0, 0, 0)

    def stop(self):
        self.loop = False

class Executor(object):

    def __init__(self, adb, workout, packages):
        self.adb = adb
        self.workout = workout
        self.packages = packages
        self.packages.append('com.android.systemui')

    def setup(self):
        pass

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

        report = open(os.path.join(self.workout, unicode(name + '.csv', 'utf-8')), 'wb')
        report.write(codecs.BOM_UTF8)
        writer = csv.writer(report, quoting=csv.QUOTE_ALL)
        writer.writerow(['开机自启动系统进程数', '开机自启动应用进程数', '合计'])
        writer.writerow([len(sysprocs), len(usrprocs), len(sysprocs) + len(usrprocs)])
        writer.writerow(['开机总内存', '开机已用内存'])
        writer.writerow([total, used])
        writer.writerow(['开机自启动系统进程名', '开机自启动系统进程内存'])
        for x, y, z in sysprocs:
            writer.writerow([y, x])
        writer.writerow(['应用进程名', '应用进程内存'])
        for x, y, z in usrprocs:
            writer.writerow([y, x])
        report.close()

    def monkey(self, outdir, package):
        self.adb.shellreadlines('am startservice --user 0 -W -a com.ztemt.test.action.TEST_KIT --es command disableKeyguard')
        workdir = os.path.dirname(os.path.realpath(sys.argv[0]))
        crashs = 0
        anrs = 0
        if package == 'com.android.systemui':
            uia = adbkit.Uia(self.adb, os.path.join(workdir, 'memory', 'systemui.jar'))
            uia.runtest('cn.nubia.systemui.test.StatusBar', extras=['-e Cycle 10'])
            uia.runtest('cn.nubia.systemui.test.MultiTaskTest', extras=['-e Cycle 10'])
            uia.destroy()
        else:
            self.adb.push(os.path.join(workdir, 'monkey.sh'), '/data/local/tmp')
            t = monkey.MonkeyMonitorThread(self.adb, [package], 600)
            t.start()
            self.adb.shell('sh /data/local/tmp/monkey.sh 13 100 200000 {0}'.format(package))
            while True:
                self.adb.waitforboot()
                if 'com.android.commands.monkey' not in [x.split()[-1] for x in self.adb.shellreadlines('ps')]:
                    break
                time.sleep(30)
            t.stop()
            file = os.path.join(outdir, 'monkey.txt')
            self.adb.pull('/data/local/tmp/monkey.txt', file)
            output = open(file, 'r')
            for line in output.readlines():
                if line.find('// CRASH:') > -1:
                    crashs += 1
                elif line.find('// NOT RESPONDING:') > -1:
                    anrs += 1
            output.close()
            os.remove(file)
        return (crashs, anrs)

    def execute(self):
        self.workout = os.path.join(self.workout, 'memory')
        shutil.rmtree(self.workout, ignore_errors=True)
        if not os.path.exists(self.workout):
            os.mkdir(self.workout)

        time.sleep(5)
        self.meminfo('开机启动进程及内存占用')

        for package in self.packages:
            outdir = os.path.join(self.workout, package)
            if not os.path.exists(outdir):
                os.mkdir(outdir)
            t = DumpsysMeminfoThread(self.adb, outdir, package, 2)
            t.start()
            crashs, anrs = self.monkey(outdir, package)
            t.stop()
            t.join()
            maxpss, minpss, avgpss = t.stat()

            file = unicode(os.path.join(self.workout, '应用内存占用汇总表.csv'), 'utf-8')
            if os.path.exists(file):
                report = open(file, 'ab+')
                writer = csv.writer(report, quoting=csv.QUOTE_ALL)
            else:
                report = open(file, 'wb')
                report.write(codecs.BOM_UTF8)
                writer = csv.writer(report, quoting=csv.QUOTE_ALL)
                writer.writerow(['进程名', '内存最大值', '内存最小值', '内存平均值', 'crash次数', 'ANR次数'])
            writer.writerow([package, maxpss, minpss, avgpss, crashs, anrs])
            report.close()

        self.adb.shellreadlines('uiautomator runtest automator.jar -c com.android.systemui.MultiTaskTestCase#testRecycle')
        self.meminfo('后台常驻进程及内存占用')
