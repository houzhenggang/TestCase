# -*- coding: utf-8 -*-

import codecs
import copy
import csv
import os
import re
import shutil
import subprocess
import sys
import threading
import time

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from common import workdir

def monkey(outdir, packages):
    data = {'seed': 0, 'count': 0, 'event': 0, 'time': 0, 'crash': 0, 'anr': 0}
    crashs = []
    anrs = []
    output = open(os.path.join(outdir, 'monkey.txt'), 'r')
    for line in output.readlines():
        if line.startswith(':Monkey:'):
            m = re.search(':Monkey: seed=(\d+) count=(\d+)', line)
            if m:
                data['seed']  = m.groups()[0]
                data['count'] = m.groups()[1]
        elif line.find('// Sending event #') > -1:
            m = re.search('// Sending event #(\d+)', line)
            if m:
                data['event'] = m.groups()[0]
        elif line.find('//[calendar_time:') > -1:
            m = re.search('system_uptime:(\d+)', line)
            if m:
                if 'start' in data:
                    data['time'] = int(m.groups()[0]) - data['start']
                else:
                    data['start'] = int(m.groups()[0])
        elif line.startswith('Events injected:'):
            m = re.search('Events injected: (\d+)', line)
            if m:
                data['event'] = m.groups()[0]
        elif line.startswith('## Network stats:'):
            m = re.search('elapsed time=(\d+)ms', line)
            if m:
                data['time'] = int(m.groups()[0])
        elif line.find('CRASH:') > -1:
            data['crash'] += 1
            m = re.search('((CRASH: (\S+)) \(pid \d+\))', line)
            if m:
                g = m.groups()
                crash = {'package': g[0], 'pkgnoid': g[1], 'pkgname': g[2]}
            else:
                crash = {}
            crashs.append(crash)
        elif line.find('Short Msg:') > -1:
            m = re.search('Short Msg: ([\w\.]+)', line)
            if m:
                crash['type'] = m.groups()[0]
        elif line.find('Long Msg:') > -1:
            m = re.search('Long Msg: ([\w\.]+)(: (.+))?', line)
            if m:
                g = m.groups()
                crash['type'] = g[0]
                crash['reason'] = g[2] if g[2] else 'no cause'
        elif line.find('NOT RESPONDING:') > -1:
            data['anr'] += 1
            m = re.search('((NOT RESPONDING: (\S+)) \(pid \d+\))', line)
            if m:
                g = m.groups()
                anr = {'package': g[0], 'pkgnoid': g[1], 'pkgname': g[2]}
            else:
                anr = {}
            anrs.append(anr)
        elif line.startswith('Reason:'):
            anr['reason'] = line[8:].strip()
    output.close()

    report = open(os.path.join(outdir, 'monkey.csv'), 'wb')
    report.write(codecs.BOM_UTF8)
    writer = csv.writer(report, quoting=csv.QUOTE_ALL)
    writer.writerow(['测试的随机数', '预期测试次数', '实际次数', '测试时间', 'CRASH次数', 'NOT RESPONDING次数'])
    writer.writerow([data['seed'], data['count'], data['event'], round(data['time'] / 3600000.0, 2), data['crash'], data['anr']])
    writer.writerow(['异常的模块名', '异常的模块版本', '异常的类型', '异常的原因', '不响应的模块名','不响应的模块版本',
            '不响应的原因', '异常的模块名不带PID用于汇总', '不响应的模块名不带PID用于汇总'])
    for i in range(max(len(crashs), len(anrs))):
        if i < len(crashs):
            crash_package = crashs[i].get('package')
            crash_pkgnoid = crashs[i].get('pkgnoid')
            crash_pkgname = crashs[i].get('pkgname')
            crash_version = packages[crash_pkgname]['versionName'] if crash_pkgname in packages else ''
            crash_type = crashs[i].get('type')
            crash_reason = crashs[i].get('reason')
        else:
            crash_package = ''
            crash_pkgnoid = ''
            crash_pkgname = ''
            crash_version = ''
            crash_type = ''
            crash_reason = ''

        if i < len(anrs):
            anr_package = anrs[i].get('package')
            anr_pkgnoid = anrs[i].get('pkgnoid')
            anr_pkgname = anrs[i].get('pkgname')
            anr_version = packages[anr_pkgname]['versionName'] if anr_pkgname in packages else ''
            anr_reason = anrs[i].get('reason')
        else:
            anr_package = ''
            anr_pkgnoid = ''
            anr_pkgname = ''
            anr_version = ''
            anr_reason = ''

        writer.writerow([crash_package, crash_version, crash_type, crash_reason, anr_package,
                anr_version, anr_reason, crash_pkgnoid, anr_pkgnoid])
    report.close()

def meminfo(outdir, outname='meminfo'):
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

    report = open(os.path.join(outdir, unicode(outname, 'utf-8').encode('gb2312') + '.csv'), 'wb')
    report.write(codecs.BOM_UTF8)
    writer = csv.writer(report, quoting=csv.QUOTE_ALL)
    writer.writerow(['pss total', 'pss private', 'dalvik heap', 'dalvik used', 'native heap', 'native used'])
    for data in list:
        writer.writerow([data.get('pss total', '0'), data.get('pss private', '0'), data.get('dalvik heap', '0'),
                data.get('dalvik used', '0'), data.get('native heap', '0'), data.get('native used', '0')])
    report.close()
    return list

def gfxinfo(outdir):
    list = []
    i = 0
    output = open(os.path.join(outdir, 'gfxinfo.txt'), 'r')
    for line in output.readlines():
        if line.startswith('Profile data in ms:') or line.startswith('No process found for:'):
            i += 1
        m = re.match('(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)', line.strip())
        if m:
            g = m.groups()
            list.append((float(g[0]), float(g[1]), float(g[2]), float(g[3]), i))
            continue
        m = re.match('(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)', line.strip())
        if m:
            g = m.groups()
            list.append((float(g[0]), 0, float(g[1]), float(g[2]), i))
    output.close()

    report = open(os.path.join(outdir, 'gfxinfo.csv'), 'wb')
    report.write(codecs.BOM_UTF8)
    writer = csv.writer(report, quoting=csv.QUOTE_ALL)
    writer.writerow(['Draw', 'Prepare', 'Process', 'Execute', 'No.'])
    for item in list:
        writer.writerow(item)
    report.close()

    file = os.path.join(os.path.dirname(outdir), 'gfxinfo.csv')
    if os.path.exists(file):
        report = open(file, 'ab+')
        writer = csv.writer(report, quoting=csv.QUOTE_ALL)
    else:
        report = open(file, 'wb')
        report.write(codecs.BOM_UTF8)
        writer = csv.writer(report, quoting=csv.QUOTE_ALL)
        writer.writerow(['项目', '绘制卡顿率'])
    if len(list) > 0:
        percent = round(len([x for x in list if sum(x[0:4]) > 16.0]) * 100.0 / len(list), 2)
    else:
        percent = 0
    writer.writerow([os.path.basename(outdir), '{0}%'.format(percent)])
    report.close()

def skpinfo(outdir):
    stat = {}
    output = open(os.path.join(outdir, 'skpinfo.txt'), 'r')
    for line in output.readlines():
        m = re.search('(\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}).*Skipped (\d+) frames!', line)
        if m:
            c = int(m.groups()[1])
            stat.setdefault(c, 0)
            stat[c] += 1
    output.close()

    report = open(os.path.join(outdir, 'skpinfo.csv'), 'wb')
    report.write(codecs.BOM_UTF8)
    writer = csv.writer(report, quoting=csv.QUOTE_ALL)
    writer.writerow(['丢帧数量', '丢帧次数'])
    if len(stat) > 0:
        for key in sorted(stat.keys(), reverse=True):
            writer.writerow([key, stat[key]])
    report.close()

    file = os.path.join(os.path.dirname(outdir), 'skpinfo.csv')
    if os.path.exists(file):
        report = open(file, 'ab+')
        writer = csv.writer(report, quoting=csv.QUOTE_ALL)
    else:
        report = open(file, 'wb')
        report.write(codecs.BOM_UTF8)
        writer = csv.writer(report, quoting=csv.QUOTE_ALL)
        writer.writerow(['项目', '丢帧数量', '丢帧次数'])
    writer.writerow([os.path.basename(outdir), sum([x * stat[x] for x in stat]), sum(stat.values())])
    report.close()

class SelectItemDialog(QDialog):

    def __init__(self, executor, parent=None):
        super(SelectItemDialog, self).__init__(parent)
        self.executor = executor
        self.tmppkgs = copy.copy(executor.usedpkgs)
        self.initUI()

    def initUI(self):
        self.radio1 = QRadioButton(u'整机Monkey测试')
        self.radio1.toggled[bool].connect(self.radioToggled)
        self.radio2 = QRadioButton(u'单包Monkey测试')
        self.radio2.setChecked(self.executor.single)
        self.radio2.toggled[bool].connect(self.radioToggled)
        self.edit1 = QLineEdit(str(self.executor.seed))
        self.edit1.setValidator(QIntValidator())
        self.edit1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.edit1.textChanged[str].connect(self.editChanged)
        self.edit2 = QLineEdit(str(self.executor.throttle))
        self.edit2.setValidator(QIntValidator())
        self.edit2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.edit2.textChanged[str].connect(self.editChanged)
        self.edit3 = QLineEdit(str(self.executor.count))
        self.edit3.setValidator(QIntValidator())
        self.edit3.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.edit3.textChanged[str].connect(self.editChanged)
        gridLayout = QGridLayout()
        gridLayout.addWidget(QLabel(u'种子数'), 0, 0)
        gridLayout.addWidget(self.edit1, 0, 1)
        gridLayout.addWidget(QLabel(u'事件间隔'), 1, 0)
        gridLayout.addWidget(self.edit2, 1, 1)
        gridLayout.addWidget(QLabel(u'事件次数'), 2, 0)
        gridLayout.addWidget(self.edit3, 2, 1)
        itemLayout = QVBoxLayout()
        itemLayout.addWidget(self.radio1)
        itemLayout.addWidget(self.radio2)
        itemLayout.addStretch()
        itemLayout.addLayout(gridLayout)
        itemGroup = QGroupBox(u'Monkey测试参数')
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
        listGroup = QGroupBox(u'单包Monkey测试可选包名')
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
        self.resize(540, 215)
        self.setWindowTitle(u'选择Monkey测试参数')

    def radioToggled(self, checked):
        sender = self.sender()

        if sender == self.radio1:
            self.executor.single = False
            self.executor.count = 1000000
        elif sender == self.radio2:
            self.executor.single = True
            self.executor.count = 200000
        self.edit3.setText(str(self.executor.count))

    def editChanged(self, text):
        sender = self.sender()

        if sender == self.edit1:
            if str(text).isdigit():
                self.executor.seed = int(text)
            else:
                self.edit1.undo()
        elif sender == self.edit2:
            if str(text).isdigit():
                self.executor.throttle = int(text)
            else:
                self.edit2.undo()
        elif sender == self.edit3:
            if str(text).isdigit():
                self.executor.count = int(text)
            else:
                self.edit3.undo()

    def itemChanged(self, item):
        pkg = str(item.data(1).toPyObject())
        if item.checkState() == Qt.Checked:
            self.executor.usedpkgs[pkg] = self.tmppkgs.get(pkg)
        else:
            self.executor.usedpkgs.pop(pkg, 'None')

class Executor(object):

    def __init__(self, adb, workout, packages):
        self.adb = adb
        self.workout = workout
        self.packages = packages
        self.usedpkgs = dict([x for x in packages.items() if x[1].get('activities')])

    def title(self):
        return u'Monkey测试'

    def setup(self, win):
        outpath = '/data/local/tmp/monkey/out'
        self.adb.shell('mkdir -p {0}'.format(outpath))
        lines = self.adb.shellreadlines('ls -F {0}'.format(outpath))
        lines = [line.split() for line in lines]
        if len(lines) > 0:
            self.single = ['-', 'monkey.txt'] not in lines
            self.retry = QMessageBox.question(win, u'Monkey测试', u'是否继续上一次的{0}Monkey测试'.format('单包' if self.single else '整机'),
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes
        else:
            self.retry = False

        if self.retry:
            return

        self.single = True
        self.seed = 10
        self.throttle = 50
        self.count = 200000 if self.single else 1000000

        dialog = SelectItemDialog(self, win)
        dialog.exec_()

    def execute(self):
        self.workout = os.path.join(self.workout, 'monkey')
        shutil.rmtree(self.workout, ignore_errors=True)
        if not os.path.exists(self.workout):
            os.mkdir(self.workout)

        if self.retry and self.single or not self.retry:
            if not self.retry:
                self.adb.reboot(30)
            self.adb.kit.disablekeyguard()
            self.adb.kit.trackframetime()

        tmppath = '/data/local/tmp/monkey'

        if self.retry:
            self.adb.shellreadlines('sh {0}/main.sh'.format(tmppath))
        else:
            pkgpath = os.path.join(self.workout, 'packages.txt')
            pkgfile = open(pkgpath, 'wb')
            pkgfile.write('{0}\n'.format('\n'.join(self.usedpkgs.keys())))
            pkgfile.close()

            self.adb.shell('rm -rf {0}'.format(tmppath))
            self.adb.shell('mkdir -p {0}'.format(tmppath))
            self.adb.push(os.path.join(workdir, 'monkey'), tmppath)
            self.adb.shell('chmod 755 {0}/*.sh'.format(tmppath))
            self.adb.push(os.path.join(workdir, 'busybox'), tmppath)
            self.adb.shell('chmod 755 {0}/busybox'.format(tmppath))
            self.adb.push(pkgpath, tmppath)
            os.remove(pkgpath)

            params = [str(self.seed), str(self.throttle), str(self.count), str(1 if self.single else 0)]
            self.adb.shellreadlines('sh {0}/main.sh {1}'.format(tmppath, ' '.join(params)))

        while True:
            for i in range(3):
                if self.adb.ismonkey():
                    finish = False
                    break
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
                if name == 'monkey.txt':
                    monkey(dirpath, self.packages)
                elif name == 'meminfo.txt' and self.single:
                    meminfo(dirpath)
                elif name == 'gfxinfo.txt':
                    gfxinfo(dirpath)
                elif name == 'skpinfo.txt':
                    skpinfo(dirpath)
