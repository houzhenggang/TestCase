# -*- coding: utf-8 -*-

import codecs
import csv
import os
import re
import shutil
import sys
import threading
import time

import monkey

from Tkinter import *
from tkMessageBox import *

from common import workdir, importdata

def meminfo(outdir, name, outname):
    start = False
    total = used = 0
    usrprocs = []
    sysprocs = []
    outpath = os.path.join(outdir, name)
    output = open(outpath, 'r')
    for line in output.readlines():
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
    output.close()
    os.rename(outpath, os.path.join(outdir, unicode(outname, 'utf-8').encode('gb2312') + '.txt'))

    sorted(sysprocs)
    sorted(usrprocs)

    report = open(os.path.join(outdir, unicode(outname, 'utf-8').encode('gb2312') + '.csv'), 'wb')
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

def stat(outdir):
    list = monkey.meminfo(outdir, '应用内存占用')

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

    def __init__(self, adb, workout, packages, datatype):
        self.adb = adb
        self.workout = workout
        self.packages = packages
        self.usedpkgs = dict([x for x in packages.items() if x[1].get('activities')])
        self.datatype = datatype

    def setup(self):
        outpath = '/data/local/tmp/memory/out'
        self.adb.shell('mkdir -p {0}'.format(outpath))
        lines = self.adb.shellreadlines('ls -F {0}'.format(outpath))
        if len(lines) > 0:
            root = Tk()
            self.retry = askyesno('内存测试', '是否继续上一次的测试', default=NO)
            root.destroy()
        else:
            self.retry = False

    def execute(self):
        self.workout = os.path.join(self.workout, 'memory')
        shutil.rmtree(self.workout, ignore_errors=True)
        if not os.path.exists(self.workout):
            os.mkdir(self.workout)

        tmppath = '/data/local/tmp/memory'

        if not self.retry:
            pkgpath = os.path.join(self.workout, 'packages.txt')
            pkgfile = open(pkgpath, 'wb')
            pkgfile.write('{0}\n'.format('\n'.join(self.usedpkgs.keys())))
            pkgfile.write('{0}\n'.format('com.android.systemui'))
            pkgfile.close()

            self.adb.kit.masterclear()
            time.sleep(30)
            self.adb.waitforboot()
            if not self.adb.getprop('ro.build.type') == 'user':
                self.adb.kit.disablekeyguard()
                self.adb.kit.setupwizard()
            self.adb.kit.keepscreenon()

            self.adb.shell('rm -rf {0}'.format(tmppath))
            self.adb.shell('mkdir -p {0}'.format(tmppath))
            self.adb.push(os.path.join(workdir, 'memory'), tmppath)
            self.adb.shell('chmod 755 {0}/*.sh'.format(tmppath))
            self.adb.push(os.path.join(workdir, 'busybox'), tmppath)
            self.adb.shell('chmod 755 {0}/busybox'.format(tmppath))
            self.adb.push(pkgpath, tmppath)
            os.remove(pkgpath)

            self.adb.shellreadlines('sh {0}/main.sh reset'.format(tmppath))

            while True:
                for i in range(3):
                    if self.adb.ismonkey():
                        finish = False
                    else:
                        finish = True
                        time.sleep(15)
                if finish:
                    break
                time.sleep(30)

            # import user data again
            importdata(self.adb, self.datatype)
            self.adb.reboot(30)
            self.adb.kit.disablekeyguard()

            self.adb.shellreadlines('sh {0}/main.sh memory'.format(tmppath))

            while True:
                for i in range(3):
                    if self.adb.ismonkey() or self.adb.isuiautomator():
                        finish = False
                    else:
                        finish = True
                        time.sleep(15)
                if finish:
                    break
                time.sleep(30)

        self.adb.pull('{0}/out'.format(tmppath), self.workout)
        time.sleep(3)

        for dirpath, dirnames, names in os.walk(self.workout):
            for name in names:
                if name == 'meminfo.txt':
                    stat(dirpath)
                elif name == 'meminfo-1.txt':
                    meminfo(dirpath, name, '开机启动进程及内存占用')
                elif name == 'meminfo-2.txt':
                    meminfo(dirpath, name, '正常开机进程及内存占用')
                elif name == 'meminfo-3.txt':
                    meminfo(dirpath, name, '后台常驻进程及内存占用')
