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
                    shell=True, stdout=output, stderr=output).wait()
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
            report.write('Item,Percentage\n')
        if len(list) > 0:
            percent = round(len([x for x in list if sum(x) > 16.0]) * 100.0 / len(list), 2)
        else:
            percent = 0
        report.write('{0},{1}%\n'.format(os.path.basename(self.outdir), percent))
        report.close()

    def stop(self):
        self.loop = False

class LogcatSkpinfoThread(threading.Thread):

    def __init__(self, outdir):
        threading.Thread.__init__(self)
        self.outdir = outdir

    def run(self):
        stat = {}
        os.system('adb logcat -c')
        output = open(os.path.join(self.outdir, 'skpinfo.txt'), 'w')
        self.p = subprocess.Popen('adb logcat -v time -s Choreographer:I I:s',
                shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while True:
            line = self.p.stdout.readline()
            if not line:
                break
            m = re.search('(\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}).*Skipped (\d+) frames!', line)
            if m:
                screenshot(os.path.join(self.outdir, '{0}.png'.format('-'.join(m.groups()[0].split(':')))))
                c = int(m.groups()[1])
                stat.setdefault(c, 0)
                stat[c] += 1
                output.write(line)
                output.flush()
        output.close()

        report = open(os.path.join(self.outdir, 'skpinfo.csv'), 'w')
        report.write(codecs.BOM_UTF8)
        report.write('丢帧数量,出现次数\n')
        if len(stat) > 0:
            for key in sorted(stat.keys(), reverse=True):
                report.write('{0},{1}\n'.format(key, stat[key]))
            report.write(',{0}\n'.format(sum(stat.values())))
        report.close()

        file = os.path.join(os.path.dirname(self.outdir), 'skpinfo.csv')
        if os.path.exists(file):
            report = open(file, 'a+')
        else:
            report = open(file, 'w')
            report.write(codecs.BOM_UTF8)
            report.write('Item,Total\n')
        report.write('{0},{1}\n'.format(os.path.basename(self.outdir), sum(stat.values())))
        report.close()

    def stop(self):
        self.p.terminate()

def screenshot(file):
    os.system('adb shell screencap -p /data/local/tmp/screenshot.png')
    os.popen('adb pull /data/local/tmp/screenshot.png \"{0}\"'.format(file)).readline()

def startactivity(packageName, activityName, clearTask):
    cmd = 'adb shell am start --user 0 -W {2} -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -n {0}/{1}'.format(
            packageName, activityName, '--activity-clear-task' if clearTask else '')
    lines = os.popen(cmd).readlines()
    for line in lines:
        if line.startswith('ThisTime:'):
            return int(line[10:])
    return 0

def starttime(package, title, activity):
    os.system('adb shell am force-stop {0}'.format(package))
    t1 = startactivity(package, activity, False)
    t2 = startactivity(package, activity, True)
    t3 = startactivity(package, activity, True)
    t4 = startactivity(package, activity, True)
    t5 = startactivity(package, activity, True)
    t6 = startactivity(package, activity, True)
    os.system('adb shell am force-stop {0}'.format(package))
    t = (t1, t2, t3, t4, t5, t6)

    line = os.popen('adb shell pm path {0}'.format(package)).readline().strip()[8:]
    line = os.popen('adb shell ls -l {0}'.format(line)).readline().strip()
    m = re.search('\s+(\d+)\s+', line)
    size = m.groups()[0] if m else '0'

    path = os.path.join(workout, 'launch.csv')
    if not os.path.exists(path):
        output = open(path, 'w')
        output.write(codecs.BOM_UTF8)
        output.write('名称,包大小,第一次,第二次,第三次,第四次,第五次,第六次,最小值,最大值,平均值\n')
    else:
        output = open(path, 'a+')

    output.write('{0},{1},{2[0]},{2[1]},{2[2]},{2[3]},{2[4]},{2[5]},{3},{4},{5}\n'.format(
            title, size, t, min(t[1:]), max(t[1:]), round(float(sum(t[1:])) / (len(t) - 1), 1)))
    output.close()

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

def scene(name, package):
    outdir = os.path.join(workout, 'scenes')
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    outdir = os.path.join(outdir, name)
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    t1 = DumpsysGfxinfoThread(package, 1, outdir)
    t2 = LogcatSkpinfoThread(outdir)
    t1.start()
    t2.start()
    subprocess.Popen('adb shell uiautomator runtest scenes.jar -c cn.nubia.test.{0}'.format(name),
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).wait()
    t1.stop()
    t2.stop()
    t1.join()
    t2.join()

def scenes():
    # copy picture files
    os.popen('adb shell mkdir -p /sdcard/Pictures').readline()
    picturesdir = open(os.path.join(workdir, 'config.txt'), 'r').readlines()[5].strip()
    os.popen('adb push \"{0}\" /sdcard/Pictures'.format(unicode(picturesdir, 'utf-8').encode('GB2312'))).readlines()

    # copy pim files
    os.popen('adb shell rm -rf /sdcard/nubia/PIM/*').readline()
    os.popen('adb shell mkdir -p /sdcard/nubia/PIM').readline()
    pimdir = open(os.path.join(workdir, 'config.txt'), 'r').readlines()[3].strip()
    for filename in glob.glob(os.path.join(unicode(pimdir, 'utf-8'), '*')):
        realname = filename.encode('GB2312')
        if os.path.isdir(filename):
            os.popen('adb shell mkdir /sdcard/nubia/PIM/{0}'.format(os.path.basename(filename))).readline()
            os.popen('adb push \"{0}\" /sdcard/nubia/PIM/{1}'.format(realname, os.path.basename(filename))).readlines()
        elif os.path.isfile(filename):
            os.popen('adb push \"{0}\" /sdcard/nubia/PIM'.format(realname)).readlines()

    # restore the backup
    os.popen('adb shell am force-stop cn.nubia.databackup').readline()
    os.popen('adb shell uiautomator runtest automator.jar -c cn.nubia.databackup.RestoreTestCase#testRestore').readlines()

    # install ApiDemos
    os.popen('adb install -r \"{0}\"'.format(os.path.join(workdir, 'ApiDemos.apk'))).readlines()

    # get scene info
    os.popen('adb push \"{0}\" /data/local/tmp'.format(os.path.join(workdir, 'scenes.jar'))).readlines()
    scene('NativeListViewTest', 'com.example.android.apis')
    scene('ContactTest', 'com.android.contacts')
    scene('DeveloperTest', 'com.android.settings')
    scene('GalleryTest', 'com.android.gallery3d')
    scene('MultiTaskTest', 'com.android.systemui')
    scene('BrowserTest', 'com.android.browser')
    scene('NoteScaleTest', 'com.android.contacts')
    scene('LauncherTest', 'cn.nubia.launcher')
    scene('PressMenuTest', 'cn.nubia.launcher')

def uptime():
    os.system('adb reboot')
    os.system('adb wait-for-device')
    while os.popen('adb shell getprop sys.boot_completed').readline().strip() != '1':
        time.sleep(0.1)
    m = re.search('up time: (\d+):(\d{2}):(\d{2})', os.popen('adb shell uptime').readline())
    uptime = int(m.groups()[0]) * 3600 + int(m.groups()[1]) * 60 + int(m.groups()[2])

    report = open(os.path.join(workout, 'uptime.csv'), 'w')
    report.write(codecs.BOM_UTF8)
    report.write('开机时间\n')
    report.write('{0:0.3f}\n'.format(uptime + 2))
    report.close()

def compat():
    os.popen('adb shell am startservice --user 0 -W -n com.ztemt.test.common/.PackageService --es command getLauncherList').readline()
    time.sleep(3)

    topapkdir = os.path.join(workdir, 'TOPAPK')
    shutil.rmtree(topapkdir, ignore_errors=True)
    remotedir = open(os.path.join(workdir, 'config.txt'), 'r').readlines()[1].strip()
    shutil.copytree(unicode(remotedir, 'utf-8'), 'TOPAPK')

    report = open(os.path.join(workout, 'compat.csv'), 'w')
    report.write(codecs.BOM_UTF8)
    report.write('应用文件名,安装i,启动i,卸载i,安装s,启动s,卸载s,异常i-1,异常i-2,异常i-3,异常s-1,异常s-2,异常s-3\n')

    for filename in glob.glob(os.path.join(topapkdir, '*.apk')):
        result1 = install(filename)
        result2 = install(filename, True)
        report.write('{0},{1[0]},{1[1]},{1[2]},{2[0]},{2[1]},{2[2]},\"{1[3]}\",\"{1[4]}\",\"{1[5]}\",\"{2[3]}\",\"{2[4]}\",\"{2[5]}\"\n'.format(
                os.path.basename(filename), result1, result2))
        report.flush()
    report.close()

def install(filename, sdcard=False):
    lines = os.popen('adb install {0} -d -r \"{1}\"'.format('-s' if sdcard else '', filename)).readlines()
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
    return ('Pass' if install else 'Fail', 'Pass' if launch else 'Fail', 'Pass' if uninstall else 'Fail',
            except1 if except1 else '', crash if crash else anr if anr else '', except2 if except2 else '')

def main():
    state = os.popen('adb get-state').readlines()[-1].strip()
    if state == 'device':
        print('Module name choices are:')
        print('    1. start time')
        print('    2. fluency test')
        print('    3. monkey test')
        print('    4. compatibility test')
        print('    5. uptime')
        try:
            module = input('\nWhich would you like? [12345] ')
        except SyntaxError:
            module = 12345
        except NameError:
            sys.exit(2)

        if '3' in str(module):
            print('\nMonkey type choices are:')
            print('    1. monkey')
            print('    2. single')
            try:
                operation = input('\nWhich would you like? [1] ')
            except SyntaxError:
                operation = 1
            except NameError:
                sys.exit(2)

        global workout
        if not os.path.exists(workout):
            os.mkdir(workout)
        model = os.popen('adb shell getprop ro.product.model').readline().strip()
        workout = os.path.join(workout, model)
        shutil.rmtree(workout, ignore_errors=True)
        if not os.path.exists(workout):
            os.mkdir(workout)

        begin = time.time()
        os.popen('adb install -r \"{0}\"'.format(os.path.join(workdir, 'TestCommon.apk'))).readlines()
        os.popen('adb shell am startservice --user 0 -W -n com.ztemt.test.common/.PackageService --es command getLauncherList').readlines()
        time.sleep(3)
        jobj = eval(os.popen('adb shell cat /data/data/com.ztemt.test.common/files/launcher').readline())

        os.popen('adb push \"{0}\" /data/local/tmp'.format(os.path.join(workdir, 'automator.jar'))).readlines()
        os.popen('adb shell uiautomator runtest automator.jar -c com.android.settings.DevelopmentSettingsTestCase#testKeepScreenOn').readlines()
        os.popen('adb shell uiautomator runtest automator.jar -c com.android.settings.DevelopmentSettingsTestCase#testTrackFrameTimeDumpsysGfxinfo').readlines()

        packages = [line[8:].strip() for line in os.popen('adb shell pm list package -s').readlines()]
        packages = [package for package in packages if package in jobj]

        for i in str(module):
            if i == '1':
                for package in packages:
                    for item in jobj[package]:
                        starttime(package, item['title'], item['activity'])
            elif i == '2':
                scenes()
            elif i == '3':
                mkydir = os.path.join(workout, 'monkey')
                if operation == 1:
                    threads = []
                    if not os.path.exists(mkydir):
                        os.mkdir(mkydir)
                    for package in packages:
                        outdir = os.path.join(mkydir, package)
                        if not os.path.exists(outdir):
                            os.mkdir(outdir)
                        t1 = DumpsysMeminfoThread(package, 20, outdir)
                        t2 = DumpsysGfxinfoThread(package,  5, outdir)
                        threads.append(t1)
                        threads.append(t2)
                        t1.start()
                        t2.start()
                    monkey(mkydir)
                    for t in threads:
                        t.stop()
                    for t in threads:
                        t.join()
                elif operation == 2:
                    if not os.path.exists(mkydir):
                        os.mkdir(mkydir)
                    for package in packages:
                        outdir = os.path.join(mkydir, package)
                        if not os.path.exists(outdir):
                            os.mkdir(outdir)
                        t1 = DumpsysMeminfoThread(package, 20, outdir)
                        t2 = DumpsysGfxinfoThread(package,  5, outdir)
                        t1.start()
                        t2.start()
                        monkey(mkydir, package)
                        t1.stop()
                        t2.stop()
                        t1.join()
                        t2.join()
            elif i == '4':
                compat()
            elif i == '5':
                uptime()

        os.popen('adb uninstall com.ztemt.test.common').readlines()
        raw_input('\nAll test finished: elapsed time={0}s, press ENTER to exit.'.format(round(time.time() - begin, 2)))
    else:
        print('Please connect your device')

workdir = os.path.dirname(os.path.realpath(sys.argv[0]))
workout = os.path.join(workdir, 'out')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
