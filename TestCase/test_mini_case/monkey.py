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

class DumpsysMeminfoThread(threading.Thread):

    def __init__(self, adb, outdir, package, interval):
        threading.Thread.__init__(self)
        self.adb = adb
        self.outdir = outdir
        self.package = package
        self.interval = interval
        self.loop = True

    def run(self):
        output = open(os.path.join(self.outdir, 'meminfo.txt'), 'w')
        while self.loop:
            time.sleep(self.interval)
            self.adb.shellopen('dumpsys meminfo {0}'.format(self.package), stdout=output, stderr=output).wait()
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

        report = open(os.path.join(self.outdir, 'meminfo.csv'), 'wb')
        report.write(codecs.BOM_UTF8)
        writer = csv.writer(report, quoting=csv.QUOTE_ALL)
        writer.writerow(['Native Heap Size', 'Native Heap Alloc', 'Native Heap Free', 'Dalvik Heap Size', 'Dalvik Heap Alloc', 'Dalvik Heap Free'])
        if len(list) > 0:
            for item in list:
                writer.writerow([item['native_heap_size'], item['native_heap_alloc'], item['native_heap_free'], item['dalvik_heap_size'], item['dalvik_heap_alloc'], item['dalvik_heap_free']])
        report.close()

    def stop(self):
        self.loop = False

class DumpsysGfxinfoThread(threading.Thread):

    def __init__(self, adb, outdir, package, interval):
        threading.Thread.__init__(self)
        self.adb = adb
        self.outdir = outdir
        self.package = package
        self.interval = interval
        self.loop = True

    def run(self):
        self.adb.shellreadlines('dumpsys gfxinfo {0}'.format(self.package))

        output = open(os.path.join(self.outdir, 'gfxinfo.txt'), 'w')
        while self.loop:
            time.sleep(self.interval)
            self.adb.shellopen('dumpsys gfxinfo {0}'.format(self.package), stdout=output, stderr=output).wait()
        output.close()

        output = open(os.path.join(self.outdir, 'gfxinfo.txt'), 'r')
        list = []
        i = 0
        for line in output.readlines():
            if line.startswith('Profile data in ms:') or line.startswith('No process found for:'):
                i += 1
            m = re.match('(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)', line.strip())
            if m:
                list.append((float(m.groups()[0]), float(m.groups()[1]), float(m.groups()[2]), i))
        output.close()

        report = open(os.path.join(self.outdir, 'gfxinfo.csv'), 'wb')
        report.write(codecs.BOM_UTF8)
        writer = csv.writer(report, quoting=csv.QUOTE_ALL)
        writer.writerow(['Draw', 'Process', 'Execute', 'No.'])
        if len(list) > 0:
            for item in list:
                writer.writerow(item)
        report.close()

        file = os.path.join(os.path.dirname(self.outdir), 'gfxinfo.csv')
        if os.path.exists(file):
            report = open(file, 'ab+')
            writer = csv.writer(report, quoting=csv.QUOTE_ALL)
        else:
            report = open(file, 'wb')
            report.write(codecs.BOM_UTF8)
            writer = csv.writer(report, quoting=csv.QUOTE_ALL)
            writer.writerow(['项目', '绘制卡顿率'])
        if len(list) > 0:
            percent = round(len([x for x in list if sum(x[0:3]) > 16.0]) * 100.0 / len(list), 2)
        else:
            percent = 0
        writer.writerow([os.path.basename(self.outdir), '{0}%'.format(percent)])
        report.close()

    def stop(self):
        self.loop = False

class LogcatSkpinfoThread(threading.Thread):

    def __init__(self, adb, outdir):
        threading.Thread.__init__(self)
        self.adb = adb
        self.outdir = outdir

    def run(self):
        stat = {}
        self.adb.adb('logcat -c')
        output = open(os.path.join(self.outdir, 'skpinfo.txt'), 'w')
        self.p = self.adb.adbopen('logcat -v time -s Choreographer:I I:s')
        while True:
            line = self.p.stdout.readline()
            if not line:
                break
            m = re.search('(\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}).*Skipped (\d+) frames!', line)
            if m:
                file = os.path.join(self.outdir, '{0}.png'.format('-'.join(m.groups()[0].split(':'))))
                self.adb.screenshot(file)
                c = int(m.groups()[1])
                stat.setdefault(c, 0)
                stat[c] += 1
                output.write(line)
                output.flush()
        output.close()

        report = open(os.path.join(self.outdir, 'skpinfo.csv'), 'wb')
        report.write(codecs.BOM_UTF8)
        writer = csv.writer(report, quoting=csv.QUOTE_ALL)
        writer.writerow(['丢帧数量', '丢帧次数'])
        if len(stat) > 0:
            for key in sorted(stat.keys(), reverse=True):
                writer.writerow([key, stat[key]])
        report.close()

        if os.path.basename(self.outdir) == 'monkey':
            file = os.path.join(self.outdir, 'skpinfo.csv')
            os.remove(file)
        else:
            file = os.path.join(os.path.dirname(self.outdir), 'skpinfo.csv')

        if os.path.exists(file):
            report = open(file, 'ab+')
            writer = csv.writer(report, quoting=csv.QUOTE_ALL)
        else:
            report = open(file, 'wb')
            report.write(codecs.BOM_UTF8)
            writer = csv.writer(report, quoting=csv.QUOTE_ALL)
            writer.writerow(['项目', '丢帧数量', '丢帧次数'])
        writer.writerow([os.path.basename(self.outdir), sum([x * stat[x] for x in stat]), sum(stat.values())])
        report.close()

    def stop(self):
        self.p.terminate()

class Executor(object):

    def __init__(self, adb, workout, packages):
        self.adb = adb
        self.workout = workout
        self.packages = packages

    def setup(self):
        print('Monkey type choices are:')
        print('    1. monkey')
        print('    2. single')
        try:
            self.single = input('\nWhich would you like? [2] ') == 2
        except SyntaxError:
            self.single = True
        except NameError:
            sys.exit(2)
        print('')

        self.seed = 10
        try:
            self.seed = input('Monkey seed? [{0}] '.format(self.seed))
        except SyntaxError:
            pass
        except NameError:
            pass
        print('')

        self.throttle = 50
        try:
            self.throttle = input('Monkey throttle in milliseconds? [{0}] '.format(self.throttle))
        except SyntaxError:
            pass
        except NameError:
            pass
        print('')

        self.count = 200000 if self.single else 1000000
        try:
            self.count = input('Monkey count? [{0}] '.format(self.count))
        except SynctaxError:
            pass
        except NameError:
            pass
        print('')

        selected = []
        print('Monkey package choices are:')
        for i in range(len(self.packages)):
            print('    {0:>2}. {1}'.format(i + 1, self.packages[i]))
        options = ','.join([str(x) for x in range(1, len(self.packages) + 1)])
        selects = raw_input('\nWhich would you like? [{0}] '.format(options)).split(',')
        for select in selects:
            try:
                index = int(select.strip()) - 1
                index = divmod(index, len(self.packages))[1]
                selected.append(self.packages[index])
            except ValueError:
                continue
        self.packages = selected if selected else self.packages
        print('')

    def monkey(self, pardir, package=None):
        if package:
            outdir = os.path.join(pardir, package)
            if not os.path.exists(outdir):
                os.mkdir(outdir)
        else:
            outdir = pardir

        self.adb.push(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'monkey.sh'), '/data/local/tmp')
        if package:
            self.adb.shell('sh /data/local/tmp/monkey.sh {0} {1} {2} {3}'.format(self.seed, self.throttle, self.count, package))
        else:
            self.adb.shell('sh /data/local/tmp/monkey.sh {0} {1} {2}'.format(self.seed, self.throttle, self.count))

        while True:
            self.adb.waitforboot(30)
            if 'com.android.commands.monkey' not in [x.split()[-1] for x in self.adb.shellreadlines('ps')]:
                break
            time.sleep(30)

        self.adb.pull('/data/local/tmp/monkey.txt', outdir)
        output = open(os.path.join(outdir, 'monkey.txt'), 'r')
        data = {'seed': 0, 'count': 0, 'event': 0, 'time': 0, 'crash': 0, 'anr': 0}
        crashs = []
        anrs = []
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
        writer.writerow(['异常的模块名', '异常的类型', '异常的原因', '不响应的模块名', '不响应的原因', '异常的模块名不带PID用于汇总', '不响应的模块名不带PID用于汇总'])
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
            writer.writerow([crash_package, crash_type, crash_reason, anr_package, anr_reason, crash_package.split(' (')[0], anr_package.split(' (')[0]])
        report.close()

    def execute(self):
        # eanble dumpsys gfxinfo
        self.adb.shellreadlines('uiautomator runtest automator.jar -c com.android.settings.DevelopmentSettingsTestCase#testTrackFrameTimeDumpsysGfxinfo')

        pardir = os.path.join(self.workout, 'monkey')
        shutil.rmtree(pardir, ignore_errors=True)
        if not os.path.exists(pardir):
            os.mkdir(pardir)

        if self.single:
            for package in self.packages:
                outdir = os.path.join(pardir, package)
                if not os.path.exists(outdir):
                    os.mkdir(outdir)
                t1 = DumpsysMeminfoThread(self.adb, outdir, package, 20)
                t2 = DumpsysGfxinfoThread(self.adb, outdir, package,  5)
                t3 = LogcatSkpinfoThread(self.adb, outdir)
                t1.start()
                t2.start()
                t3.start()
                self.monkey(pardir, package)
                t1.stop()
                t2.stop()
                t3.stop()
                t1.join()
                t2.join()
                t3.join()
        else:
            threads = []
            for package in self.packages:
                outdir = os.path.join(pardir, package)
                if not os.path.exists(outdir):
                    os.mkdir(outdir)
                t1 = DumpsysMeminfoThread(self.adb, outdir, package, 20)
                t2 = DumpsysGfxinfoThread(self.adb, outdir, package,  5)
                threads.append(t1)
                threads.append(t2)
                t1.start()
                t2.start()
            self.monkey(pardir)
            for t in threads:
                t.stop()
            for t in threads:
                t.join()
