# -*- coding:UTF-8 -*-

import codecs
import getopt
import glob
import os
import re
import shutil
import subprocess
import sys
import threading
import time

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
                    shell=True, stdout=output, stderr=output).wait()
        output.close()

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
        output = open(os.path.join(self.outdir, 'gfxinfo.txt'), 'w')
        while self.loop:
            time.sleep(self.interval)
            subprocess.Popen('adb shell dumpsys gfxinfo {0}'.format(self.package),
                    shell=True, stdout=output, stderr=output).wait()
        output.close()

    def stop(self):
        self.loop = False

class DumpsysCpuinfoThread(threading.Thread):

    def __init__(self, package, interval, outdir):
        threading.Thread.__init__(self)
        self.package = package
        self.interval = interval
        self.outdir = outdir
        self.loop = True

    def run(self):
        output = open(os.path.join(self.outdir, 'cpuinfo.csv'), 'w')
        output.write(codecs.BOM_UTF8)
        output.write('当前频率,当前温度\n')
        output.flush()
        while self.loop:
            time.sleep(self.interval)
            curfreq = os.popen('adb shell cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq').readline().strip()
            curtemp = os.popen('adb shell cat /sys/class/thermal/thermal_zone0/temp').readline().strip()
            output.write('{0},{1}\n'.format(curfreq, curtemp))
            output.flush()
        output.close()

    def stop(self):
        self.loop = False

def startActivity(packageName, activityName, clearTask):
    cmd = 'adb shell am start --user 0 -W {2} -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -n {0}/{1}'.format(
            packageName, activityName, '--activity-clear-task' if clearTask else '')
    lines = os.popen(cmd).readlines()
    for line in lines:
        if line.startswith('ThisTime:'):
            return int(line[10:])
    return 0

def getAppsInfo(package, title, activity):
    os.system('adb shell am force-stop {0}'.format(package))
    t1 = startActivity(package, activity, False)
    t2 = startActivity(package, activity, True)
    t3 = startActivity(package, activity, True)
    t4 = startActivity(package, activity, True)
    t5 = startActivity(package, activity, True)
    t6 = startActivity(package, activity, True)
    os.system('adb shell am force-stop {0}'.format(package))
    t = (t1, t2, t3, t4, t5, t6)

    line = os.popen('adb shell pm path {0}'.format(package)).readline().strip()[8:]
    line = os.popen('adb shell ls -l {0}'.format(line)).readline().strip()
    m = re.search('\s+(\d+)\s+', line)
    size = m.groups()[0] if m else '0'

    path = os.path.join(workout, 'appsinfo.csv')
    if not os.path.exists(path):
        output = open(path, 'w')
        output.write(codecs.BOM_UTF8)
        output.write('名称,包大小,第一次,第二次,第三次,第四次,第五次,第六次,最小值,最大值,平均值\n')
    else:
        output = open(path, 'a+')

    output.write('{0},{1},{2[0]},{2[1]},{2[2]},{2[3]},{2[4]},{2[5]},{3},{4},{5}\n'.format(
            title, size, t, min(t[1:]), max(t[1:]), round(float(sum(t[1:])) / (len(t) - 1), 1)))
    output.close()

def monkey(package):
    outdir = os.path.join(workout, 'monkey-{0}'.format(package))
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    t1 = DumpsysMeminfoThread(package, 20, outdir)
    t2 = DumpsysGfxinfoThread(package, 10, outdir)
    t3 = DumpsysCpuinfoThread(package, 10, outdir)
    t1.start()
    t2.start()
    t3.start()
    monkey = open(os.path.join(outdir, 'monkey.txt'), 'w+')
    subprocess.Popen('adb shell monkey -p {0} -s 10 --throttle 100 --pct-anyevent 0 --ignore-timeouts --ignore-crashes -v 100000'.format(
            package), shell=True, stdout=monkey, stderr=monkey).wait()
    monkey.close()
    t1.stop()
    t2.stop()
    t3.stop()
    t1.join()
    t2.join()
    t3.join()

    monkey = open(os.path.join(outdir, 'monkey.txt'), 'r')
    data = {'count': 0, 'event': 0, 'crash': 0, 'anr': 0}
    for line in monkey.readlines():
        if line.startswith(':Monkey:'):
            m = re.match(':Monkey: seed=(\d+) count=(\d+)', line)
            data['count'] = m.groups()[1]
        elif line.startswith('    // Sending event #'):
            m = re.match('    // Sending event #(\d+)', line)
            data['event'] = m.groups()[0]
        elif line.startswith('Events injected:'):
            m = re.match('Events injected: (\d+)', line)
            data['event'] = m.groups()[0]
        elif line.startswith('// CRASH:'):
            data['crash'] = data['crash'] + 1
        elif line.startswith('// NOT RESPONDING:'):
            data['anr'] = data['anr'] + 1
    monkey.close()

    report = open(os.path.join(outdir, 'monkey.csv'), 'w')
    report.write(codecs.BOM_UTF8)
    report.write('预期次数,实际次数,CRASH次数,ANR次数\n')
    report.write('{0},{1},{2},{3}\n'.format(data['count'], data['event'], data['crash'], data['anr']))
    report.close()

    meminfo = open(os.path.join(outdir, 'meminfo.txt'), 'r')
    list = []
    data = {}
    for line in meminfo.readlines():
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
    meminfo.close()

    report = open(os.path.join(outdir, 'meminfo.csv'), 'w')
    report.write(codecs.BOM_UTF8)
    report.write(','.join(('Native Heap Size', 'Native Heap Alloc', 'Native Heap Free',
            'Dalvik Heap Size', 'Dalvik Heap Alloc', 'Dalvik Heap Free')) + '\n')
    if len(list) > 0:
        for item in list:
            report.write(','.join((item['native_heap_size'], item['native_heap_alloc'], item['native_heap_free'],
                    item['dalvik_heap_size'], item['dalvik_heap_alloc'], item['dalvik_heap_free'])) + '\n')
    report.close()

    gfxinfo = open(os.path.join(outdir, 'gfxinfo.txt'), 'r')
    list = []
    for line in gfxinfo.readlines():
        m = re.match('(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)', line.strip())
        if m:
            list.append((m.groups()[0], m.groups()[1], m.groups()[2]))
    gfxinfo.close()

    report = open(os.path.join(outdir, 'gfxinfo.csv'), 'w')
    report.write(codecs.BOM_UTF8)
    report.write(','.join(('Draw', 'Process', 'Execute')) + '\n')
    if len(list) > 0:
        for item in list:
            report.write(','.join(item) + '\n')
    report.close()

def reboot():
    os.system('adb reboot')
    os.system('adb wait-for-device')
    while os.popen('adb shell getprop sys.boot_completed').readline().strip() != '1':
        time.sleep(0.1)
    m = re.search('up time: (\d+):(\d{2}):(\d{2})', os.popen('adb shell uptime').readline())
    uptime = int(m.groups()[0]) * 3600 + int(m.groups()[1]) * 60 + int(m.groups()[2])

    report = open(os.path.join(workout, 'reboot.csv'), 'w')
    report.write(codecs.BOM_UTF8)
    report.write('开机时间\n')
    report.write('{0:0.3f}\n'.format(uptime + 2))
    report.close()

def install():
    os.popen('adb shell am startservice --user 0 -W -n com.ztemt.test.common/.PackageService --es command getLauncherList').readline()
    time.sleep(3)

    report = open(os.path.join(workout, 'install.csv'), 'w')
    report.write(codecs.BOM_UTF8)
    report.write('应用文件名,安装,启动,卸载,异常1,异常2,异常3\n')

    pattern = os.path.join(os.path.join(workdir, 'TOP10APK'), '*.apk')
    for filename in glob.glob(pattern):
        lines = os.popen('adb install -r \"{0}\"'.format(filename)).readlines()
        install = 'Success' in [line.strip() for line in lines]
        launch = True
        except1 = crash = anr = except2 = None
        uninstall = False
        if install:
            time.sleep(3)
            package = os.popen('adb shell cat /data/data/com.ztemt.test.common/files/package').readline()
            lines = os.popen('adb shell monkey -p {0} -s 10 --throttle 10000 --ignore-timeouts --ignore-crashes -v 10'.format(package)).readlines()
            for line in lines:
                if line.startswith('// CRASH: {0}'.format(package)):
                    launch = False
                elif not launch and line.startswith('// Long Msg:'):
                    crash = 'CRASH: {0}'.format(line[13:].strip())
                    break
                elif line.startswith('// NOT RESPONDING: {0}'.format(package)):
                    launch = False
                elif not launch and line.startswith('Reason:'):
                    anr = 'ANR: {0}'.format(line[8:].strip())
                    break
            time.sleep(3)
            lines = os.popen('adb uninstall {0}'.format(package)).readlines()
            uninstall = 'Success' in [line.strip() for line in lines]
            if not uninstall:
                except2 = lines[-1].strip()
        else:
            except1 = lines[-1].strip()
            launch = False

        report.write('{0},{1},{2},{3},{4}\n'.format(os.path.basename(filename), 'Pass' if install else 'Fail',
                'Pass' if launch else 'Fail', 'Pass' if uninstall else 'Fail', except1 if except1 else '',
                crash if crash else anr if anr else '', except2 if except2 else ''))
        report.flush()
    report.close()

def main():
    shutil.rmtree(workout, ignore_errors=True)
    if not os.path.exists(workout):
        os.mkdir(workout)

    os.popen('adb install -r \"{0}\"'.format(os.path.join(workdir, 'TestCommon.apk'))).readlines()
    os.popen('adb install -r \"{0}\"'.format(os.path.join(workdir, 'SettingsTest.apk'))).readlines()

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'p:')
    except getopt.GetoptError:
        sys.exit(2)

    packages = []
    for option, value in opts:
        if option == '-p':
            packages.append(value)

    if len(packages) == 0:
        packages = [line[8:].strip() for line in os.popen('adb shell pm list package -s').readlines()]

    os.popen('adb shell am startservice --user 0 -W -n com.ztemt.test.common/.PackageService --es command getLauncherList').readlines()
    time.sleep(3)
    jobj = eval(os.popen('adb shell cat /data/data/com.ztemt.test.common/files/launcher').readline())
    os.popen('adb shell am instrument -w -e class com.android.settings.test.DevelopmentSettingsTestCase#testTrackFrameTimeIsDumpsysGfxinfo com.android.settings.test/com.google.android.apps.common.testing.testrunner.GoogleInstrumentationTestRunner').readlines()

    for package in packages:
        if package in jobj:
            for item in jobj[package]:
                getAppsInfo(package, item['title'], item['activity'])
            monkey(package)

    install()

    reboot()

    os.popen('adb uninstall com.ztemt.test.common').readlines()
    os.popen('adb uninstall com.android.settings.test').readlines()

workdir = os.path.dirname(os.path.realpath(sys.argv[0]))
workout = os.path.join(workdir, 'out')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
