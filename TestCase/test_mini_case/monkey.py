# -*- coding:UTF-8 -*-

import codecs
import csv
import os
import re
import shutil
import subprocess
import sys
import threading
import time

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
        elif line.find('// CRASH:') > -1:
            data['crash'] = data['crash'] + 1
            crash = {'package': line.strip()[3:]}
            crashs.append(crash)
        elif line.startswith('// Long Msg:'):
            ss = line.strip().split(': ')
            if 'crash' in locals():
                crash['type'] = ss[1]
                if len(ss) > 2:
                    crash['reason'] = ss[2]
                else:
                    crash['reason'] = 'no cause'
        elif line.find('// NOT RESPONDING:') > -1:
            m = re.search('// (NOT RESPONDING: .+ \(pid \d+\))', line)
            if m:
                data['anr'] = data['anr'] + 1
                anr = {'package': m.groups()[0]}
                anrs.append(anr)
        elif line.startswith('Reason:'):
            if 'anr' in locals():
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
            crash_package = crashs[i]['package']
            crash_type = crashs[i].get('type', '')
            crash_reason = crashs[i].get('reason', '')
        else:
            crash_package = ''
            crash_type = ''
            crash_reason = ''
        if i < len(anrs):
            anr_package = anrs[i]['package']
            anr_reason = anrs[i].get('reason', '')
        else:
            anr_package = ''
            anr_reason = ''
        crash_package_no_pid = crash_package.split(' (')[0]
        crash_package_real = crash_package_no_pid.split(':')[-1].strip()
        if crash_package_real in packages:
            crash_package_version = packages[crash_package_real]['versionName']
        else:
            crash_package_version = ''
        anr_package_no_pid = anr_package.split(' (')[0]
        anr_package_real = anr_package_no_pid.split(':')[-1].strip()
        if anr_package_real in packages:
            anr_package_version = packages[anr_package_real]['versionName']
        else:
            anr_package_version = ''
        writer.writerow([crash_package, crash_package_version, crash_type, crash_reason, anr_package,
                anr_package_version, anr_reason, crash_package_no_pid, anr_package_no_pid])
    report.close()

def meminfo(outdir):
    list = []
    data = {}
    output = open(os.path.join(outdir, 'meminfo.txt'), 'r')
    for line in output.readlines():
        if line.strip().startswith('Native'):
            m = re.match('Native[ Heap]+\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)', line.strip())
            if m:
                data['native_heap_size'] = m.groups()[4]
                data['native_heap_alloc'] = m.groups()[5]
                data['native_heap_free'] = m.groups()[6]
        elif line.strip().startswith('Dalvik'):
            m = re.match('Dalvik[ Heap]+\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)', line.strip())
            if m:
                data['dalvik_heap_size'] = m.groups()[4]
                data['dalvik_heap_alloc'] = m.groups()[5]
                data['dalvik_heap_free'] = m.groups()[6]
        if len(data) == 6:
            list.append(data.copy())
            data.clear()
    output.close()

    report = open(os.path.join(outdir, 'meminfo.csv'), 'wb')
    report.write(codecs.BOM_UTF8)
    writer = csv.writer(report, quoting=csv.QUOTE_ALL)
    writer.writerow(['Native Heap Size', 'Native Heap Alloc', 'Native Heap Free', 'Dalvik Heap Size', 'Dalvik Heap Alloc', 'Dalvik Heap Free'])
    if len(list) > 0:
        for item in list:
            writer.writerow([item['native_heap_size'], item['native_heap_alloc'], item['native_heap_free'], item['dalvik_heap_size'], item['dalvik_heap_alloc'], item['dalvik_heap_free']])
    report.close()

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

class Executor(object):

    def __init__(self, adb, workout, packages):
        self.adb = adb
        self.workout = workout
        self.packages = dict([x for x in packages.items() if x[1].get('activities')])

    def setup(self):
        outpath = '/data/local/tmp/monkey/out'
        self.adb.shell('mkdir -p {0}'.format(outpath))
        lines = self.adb.shellreadlines('ls -F {0}'.format(outpath))
        lines = [line.split() for line in lines]
        if len(lines) > 0:
            self.single = ['-', 'monkey.txt'] not in lines
            select = raw_input('Want to continue the last {0} test? [N] '.format('single monkey' if self.single else 'monkey'))
            print('')
            if select == 'Y' or select == 'y':
                self.restart = True
                return
        self.restart = False

        print('Monkey type choices are:')
        print('     1. monkey')
        print('     2. single')
        try:
            self.single = input('\nWhich would you like? [2] ') == 2
        except SyntaxError:
            self.single = True
        except NameError:
            sys.exit(2)
        print('')

        print('Parameters for monkey:')
        self.seed = 10
        try:
            self.seed = input('Monkey seed? [{0}] '.format(self.seed))
        except SyntaxError:
            pass
        except NameError:
            pass
        self.throttle = 50
        try:
            self.throttle = input('Monkey throttle in milliseconds? [{0}] '.format(self.throttle))
        except SyntaxError:
            pass
        except NameError:
            pass
        self.count = 200000 if self.single else 1000000
        try:
            self.count = input('Monkey count? [{0}] '.format(self.count))
        except SyntaxError:
            pass
        except NameError:
            pass
        print('')

        if self.single:
            selected = []
            print('Monkey package choices are:')
            pkgkeys = self.packages.keys()
            for i in range(len(pkgkeys)):
                print('    {0:>2}. {1}'.format(i + 1, pkgkeys[i]))
            options = ','.join([str(x) for x in range(1, len(pkgkeys) + 1)])
            selects = raw_input('\nWhich would you like? [{0}] '.format(options)).split(',')
            for select in selects:
                try:
                    index = int(select.strip()) - 1
                    index = divmod(index, len(pkgkeys))[1]
                    selected.append((pkgkeys[index], self.packages[pkgkeys[index]]))
                except ValueError:
                    continue
            self.packages = dict(selected) if selected else self.packages
            print('')

    def execute(self):
        self.workout = os.path.join(self.workout, 'monkey')
        shutil.rmtree(self.workout, ignore_errors=True)
        if not os.path.exists(self.workout):
            os.mkdir(self.workout)

        if self.restart and self.single or not self.restart:
            if not self.restart:
                self.adb.reboot(30)
            self.adb.kit.disablekeyguard()
            self.adb.uia.runtest('com.android.settings.DevelopmentSettingsTestCase', 'testTrackFrameTimeDumpsysGfxinfo')

        tmppath = '/data/local/tmp/monkey'
        if self.restart:
            self.adb.shellreadline('{0}/busybox nohup sh {0}/main.sh &'.format(tmppath))
        else:
            pkgpath = os.path.join(self.workout, 'packages.txt')
            pkgfile = open(pkgpath, 'wb')
            pkgfile.write('{0}\n'.format('\n'.join(self.packages.keys())))
            pkgfile.close()

            workdir = os.path.dirname(os.path.realpath(sys.argv[0]))
            self.adb.shell('rm -rf {0}'.format(tmppath))
            self.adb.shell('mkdir -p {0}'.format(tmppath))
            self.adb.push(os.path.join(workdir, 'monkey'), tmppath)
            self.adb.shell('chmod 755 {0}/*.sh'.format(tmppath))
            self.adb.push(os.path.join(workdir, 'busybox'), tmppath)
            self.adb.shell('chmod 755 {0}/busybox'.format(tmppath))
            self.adb.push(pkgpath, tmppath)
            os.remove(pkgpath)

            params = [str(self.seed), str(self.throttle), str(self.count), str(1 if self.single else 0)]
            self.adb.shellreadline('{0}/busybox nohup sh {0}/main.sh {1} &'.format(tmppath, ' '.join(params)))

        while True:
            self.adb.waitforboot()
            for i in range(3):
                if self.adb.ismonkey():
                    finish = False
                    break
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
                if name == 'monkey.txt':
                    monkey(dirpath, self.packages)
                elif name == 'meminfo.txt':
                    meminfo(dirpath)
                elif name == 'gfxinfo.txt':
                    gfxinfo(dirpath)
                elif name == 'skpinfo.txt':
                    skpinfo(dirpath)
