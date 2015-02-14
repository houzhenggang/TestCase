# -*- coding: utf-8 -*-

import codecs
import csv
import copy
import os
import re
import shutil
import sys
import threading
import time

import monkey

from PyQt4.QtCore import *
from PyQt4.QtGui import *

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

class SelectItemDialog(QDialog):

    def __init__(self, executor, parent=None):
        super(SelectItemDialog, self).__init__(parent)
        self.executor = executor
        self.initUI()

    def initUI(self):
        self.item1 = QCheckBox(u'开机启动内存')
        self.item1.setChecked(self.executor.sel1)
        self.item1.stateChanged[int].connect(self.setItemChecked)
        self.item2 = QCheckBox(u'正常开机内存')
        self.item2.setChecked(self.executor.sel2)
        self.item2.stateChanged[int].connect(self.setItemChecked)
        self.item3 = QCheckBox(u'后台常驻内存')
        self.item3.setChecked(self.executor.sel3)
        self.item3.stateChanged[int].connect(self.setItemChecked)
        self.item4 = QCheckBox(u'应用内存')
        self.item4.setChecked(self.executor.sel4)
        self.item4.stateChanged[int].connect(self.setItemChecked)
        itemLayout = QVBoxLayout()
        itemLayout.addWidget(self.item1)
        itemLayout.addWidget(self.item2)
        itemLayout.addWidget(self.item3)
        itemLayout.addWidget(self.item4)
        itemGroup = QGroupBox(u'内存测试项')
        itemGroup.setLayout(itemLayout)
        list = QListWidget(self)
        list.itemChanged.connect(self.itemChanged)
        for key in self.executor.usedpkgs.keys():
            item = QListWidgetItem(key)
            item.setCheckState(Qt.Checked)
            item.setData(1, QVariant(key))
            list.addItem(item)
        list.setCurrentRow(0)
        listLayout = QVBoxLayout()
        listLayout.addWidget(list)
        listGroup = QGroupBox(u'应用内存可选包名')
        listGroup.setLayout(listLayout)

        itemLayout = QHBoxLayout()
        itemLayout.addWidget(itemGroup)
        itemLayout.addWidget(listGroup)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(itemLayout)
        mainLayout.addWidget(buttonBox)

        self.setLayout(mainLayout)
        self.resize(450, 200)
        self.setWindowTitle(u'选择内存测试项')

    def setItemChecked(self, state):
        sender = self.sender()
        checked = state == int(Qt.Checked)

        if sender == self.item1:
            self.executor.sel1 = checked
        elif sender == self.item2:
            self.executor.sel2 = checked
        elif sender == self.item3:
            self.executor.sel3 = checked
        elif sender == self.item4:
            self.executor.sel4 = checked

    def itemChanged(self, item):
        pkg = str(item.data(1).toPyObject())
        if item.checkState() == Qt.Checked:
            self.executor.mempkgs[pkg] = self.executor.usedpkgs.get(pkg)
        else:
            self.executor.mempkgs.pop(pkg, 'None')

class Executor(object):

    def __init__(self, adb, workout, packages, datatype):
        self.adb = adb
        self.workout = workout
        self.packages = packages
        self.usedpkgs = dict([x for x in packages.items() if x[1].get('activities')])
        self.usedpkgs['com.android.systemui'] = None
        self.datatype = datatype

    def title(self):
        return u'内存测试'

    def setup(self, win):
        outpath = '/data/local/tmp/memory/out'
        self.adb.shell('mkdir -p {0}'.format(outpath))
        lines = self.adb.shellreadlines('ls -F {0}'.format(outpath))
        if len(lines) > 0:
            self.retry = QMessageBox.question(win, u'内存测试', u'是否继续上一次的内存测试',
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes
        else:
            self.retry = False

        if self.retry:
            return

        self.sel1, self.sel2, self.sel3, self.sel4 = True, True, True, False
        self.mempkgs = copy.copy(self.usedpkgs)
        dialog = SelectItemDialog(self, win)
        dialog.exec_()
        
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
            pkgfile.close()
            mempath = os.path.join(self.workout, 'mempkgs.txt')
            memfile = open(mempath, 'wb')
            memfile.write('{0}\n'.format('\n'.join(self.mempkgs.keys())))
            memfile.close()

            if self.sel1:
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
            self.adb.push(mempath, tmppath)
            os.remove(pkgpath)
            os.remove(mempath)

            if self.sel1:
                self.adb.shellreadlines('sh {0}/main.sh reset'.format(tmppath))

            def waitforfinish():
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

            if self.sel2:
                self.adb.shellreadline('sh {0}/monkey.sh'.format(tmppath))
                waitforfinish()
                self.adb.reboot(30)
                self.adb.shellreadlines('sh {0}/main.sh normal'.format(tmppath))
                self.adb.kit.disablekeyguard()

            if self.sel1 and self.sel3 or self.sel4:
                if self.datatype:
                    importdata(self.adb, self.datatype)

            if self.sel3:
                self.adb.reboot(30)
                self.adb.kit.disablekeyguard()
                self.adb.shellreadline('sh {0}/main.sh resident'.format(tmppath))
                waitforfinish()

            if self.sel4:
                self.adb.reboot(30)
                self.adb.kit.disablekeyguard()
                self.adb.shellreadline('sh {0}/main.sh memory'.format(tmppath))
                waitforfinish()

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
