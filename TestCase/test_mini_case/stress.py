# -*- coding:UTF-8 -*-

import codecs
import os
import re
import subprocess
import sys
import threading
import time

import scenes

workdir = os.path.dirname(os.path.realpath(sys.argv[0]))

class DumpsysMeminfoThread(threading.Thread):

    def __init__(self, package, interval, outdir):
        threading.Thread.__init__(self)
        self.package = package
        self.interval = interval
        self.outdir = outdir
        self.loop = True

    def run(self):
        output = open(os.path.join(self.outdir, 'meminfo.txt'), 'w')
        while self.loop:
            time.sleep(self.interval)
            subprocess.Popen('adb shell dumpsys meminfo {0}'.format(self.package),
                    shell=False, stdout=output, stderr=output).wait()
        output.close()

        output = open(os.path.join(self.outdir, 'meminfo.txt'), 'r')
        list = []
        data = {}
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

        report = open(os.path.join(self.outdir, 'meminfo.csv'), 'w')
        report.write(codecs.BOM_UTF8)
        report.write(','.join(('Native Heap Size', 'Native Heap Alloc', 'Native Heap Free',
                'Dalvik Heap Size', 'Dalvik Heap Alloc', 'Dalvik Heap Free')) + '\n')
        if len(list) > 0:
            for item in list:
                report.write(','.join((item['native_heap_size'], item['native_heap_alloc'], item['native_heap_free'],
                        item['dalvik_heap_size'], item['dalvik_heap_alloc'], item['dalvik_heap_free'])) + '\n')
        report.close()

    def stop(self):
        self.loop = False

class DumpsysGfxinfoThread(threading.Thread):

    def __init__(self, package, interval, outdir):
        threading.Thread.__init__(self)
        self.package = package
        self.interval = interval
        self.outdir = outdir
        self.loop = True

    def run(self):
        os.popen('adb shell dumpsys gfxinfo {0}'.format(self.package)).readlines()

        output = open(os.path.join(self.outdir, 'gfxinfo.txt'), 'w')
        while self.loop:
            time.sleep(self.interval)
            subprocess.Popen('adb shell dumpsys gfxinfo {0}'.format(self.package),
                    shell=False, stdout=output, stderr=output).wait()
        output.close()

        output = open(os.path.join(self.outdir, 'gfxinfo.txt'), 'r')
        list = []
        for line in output.readlines():
            m = re.match('(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)', line.strip())
            if m:
                list.append((float(m.groups()[0]), float(m.groups()[1]), float(m.groups()[2])))
        output.close()

        report = open(os.path.join(self.outdir, 'gfxinfo.csv'), 'w')
        report.write(codecs.BOM_UTF8)
        report.write(','.join(('Draw', 'Process', 'Execute')) + '\n')
        if len(list) > 0:
            for item in list:
                report.write('{0[0]},{0[1]},{0[2]}\n'.format(item))
        report.close()

        file = os.path.join(os.path.dirname(self.outdir), 'gfxinfo.csv')
        if os.path.exists(file):
            report = open(file, 'a+')
        else:
            report = open(file, 'w')
            report.write(codecs.BOM_UTF8)
            report.write('项目,绘制卡顿率\n')
        if len(list) > 0:
            percent = round(len([x for x in list if sum(x) > 16.0]) * 100.0 / len(list), 2)
        else:
            percent = 0
        report.write('{0},{1}%\n'.format(os.path.basename(self.outdir), percent))
        report.close()

    def stop(self):
        self.loop = False

def monkey(pardir, package=None):
    if package:
        outdir = os.path.join(pardir, package)
        if not os.path.exists(outdir):
            os.mkdir(outdir)
    else:
        outdir = pardir

    os.popen('adb push \"{0}\" /data/local/tmp'.format(os.path.join(workdir, 'monkey.sh'))).readlines()
    if package:
        os.system('adb shell sh /data/local/tmp/monkey.sh {0}'.format(package))
    else:
        os.system('adb shell sh /data/local/tmp/monkey.sh')

    while True:
        os.system('adb wait-for-device')
        if not os.popen('adb shell ps | grep com.android.commands.monkey').readline().strip():
            break
        time.sleep(20)

    os.popen('adb pull /data/local/tmp/monkey.txt \"{0}\"'.format(outdir)).readlines()
    output = open(os.path.join(outdir, 'monkey.txt'), 'r')
    data = {'seed': 0, 'count': 0, 'event': 0, 'time': 0, 'crash': 0, 'anr': 0}
    crashs = []
    anrs = []
    for line in output.readlines():
        if line.startswith(':Monkey:'):
            m = re.search(':Monkey: seed=(\d+) count=(\d+)', line)
            data['seed']  = m.groups()[0]
            data['count'] = m.groups()[1]
        elif line.find('// Sending event #') > -1:
            m = re.search('// Sending event #(\d+)', line)
            data['event'] = m.groups()[0]
        elif line.find('//[calendar_time:') > -1:
            m = re.search('system_uptime:(\d+)', line)
            if 'start' in data:
                data['time'] = int(m.groups()[0]) - data['start']
            else:
                data['start'] = int(m.groups()[0])
        elif line.startswith('Events injected:'):
            m = re.search('Events injected: (\d+)', line)
            data['event'] = m.groups()[0]
        elif line.startswith('## Network stats:'):
            m = re.search('elapsed time=(\d+)ms', line)
            data['time'] = int(m.groups()[0])
        elif line.find('// CRASH:') > -1:
            data['crash'] = data['crash'] + 1
            crash = {'package': line.strip()[3:]}
            crashs.append(crash)
        elif line.startswith('// Long Msg:'):
            ss = line.strip().split(': ')
            crash['type'] = ss[1]
            if len(ss) > 2:
                crash['reason'] = ss[2]
            else:
                crash['reason'] = 'no cause'
        elif line.find('// NOT RESPONDING:') > -1:
            data['anr'] = data['anr'] + 1
            m = re.search('// (NOT RESPONDING: .+ \(pid \d+\))', line)
            anr = {'package': m.groups()[0]}
            anrs.append(anr)
        elif line.startswith('Reason:'):
            anr['reason'] = line[8:].strip()
    output.close()

    report = open(os.path.join(outdir, 'monkey.csv'), 'w')
    report.write(codecs.BOM_UTF8)
    report.write('测试的随机数,预期测试次数,实际次数,测试时间,CRASH次数,NOT RESPONDING次数\n')
    report.write('{0},{1},{2},{3},{4},{5}\n'.format(data['seed'], data['count'], data['event'],
            round(data['time'] / 3600000.0, 2), data['crash'], data['anr']))
    report.write('异常的模块名,异常的类型,异常的原因,不响应的模块名,不响应的原因,异常的模块名不带PID用于汇总,不响应的模块名不带PID用于汇总\n')
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
        report.write('{0},{1},\"{2}\",{3},\"{4}\",{5},{6}\n'.format(crash_package, crash_type, crash_reason, anr_package, anr_reason,
                crash_package.split(' (')[0], anr_package.split(' (')[0]))
    report.close()

def stress(workout, packages, single=False):
    pardir = os.path.join(workout, 'monkey')
    if not os.path.exists(pardir):
        os.mkdir(pardir)

    if not single:
        threads = []
        for package in packages:
            outdir = os.path.join(pardir, package)
            if not os.path.exists(outdir):
                os.mkdir(outdir)
            t1 = DumpsysMeminfoThread(package, 20, outdir)
            t2 = DumpsysGfxinfoThread(package,  5, outdir)
            threads.append(t1)
            threads.append(t2)
            t1.start()
            t2.start()
        t3 = scenes.LogcatSkpinfoThread(pardir)
        t3.start()
        monkey(pardir)
        t3.stop()
        t3.join()
        for t in threads:
            t.stop()
        for t in threads:
            t.join()
    else:
        for package in packages:
            outdir = os.path.join(pardir, package)
            if not os.path.exists(outdir):
                os.mkdir(outdir)
            t1 = DumpsysMeminfoThread(package, 20, outdir)
            t2 = DumpsysGfxinfoThread(package,  5, outdir)
            t3 = scenes.LogcatSkpinfoThread(outdir)
            t1.start()
            t2.start()
            t3.start()
            monkey(pardir, package)
            t1.stop()
            t2.stop()
            t3.stop()
            t1.join()
            t2.join()
            t3.join()
