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
                list.append((m.groups()[0], m.groups()[1], m.groups()[2]))
        output.close()

        report = open(os.path.join(self.outdir, 'gfxinfo.csv'), 'w')
        report.write(codecs.BOM_UTF8)
        report.write(','.join(('Draw', 'Process', 'Execute')) + '\n')
        if len(list) > 0:
            for item in list:
                report.write(','.join(item) + '\n')
        report.close()

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
        report = open(os.path.join(self.outdir if self.package else workout, 'cpuinfo.csv'), 'w')
        report.write(codecs.BOM_UTF8)
        report.write('当前频率,当前温度\n')
        report.flush()
        while self.loop:
            time.sleep(self.interval)
            curfreq = os.popen('adb shell cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq').readline().strip()
            curtemp = os.popen('adb shell cat /sys/class/thermal/thermal_zone0/temp').readline().strip()
            if curfreq and curtemp:
                report.write('{0},{1}\n'.format(curfreq, curtemp))
                report.flush()
        report.close()

    def stop(self):
        self.loop = False

class LogcatGfxinfoThread(threading.Thread):

    def __init__(self, outdir):
        threading.Thread.__init__(self)
        self.outdir = outdir

    def run(self):
        os.system('adb logcat -c')
        output = open(os.path.join(self.outdir, 'gfxinfo.txt'), 'w')
        self.p = subprocess.Popen('adb logcat -v time -s HardwareRenderer:D I:s',
                shell=False, stdout=output, stderr=output)
        self.p.wait()
        output.close()

        output = open(os.path.join(self.outdir, 'gfxinfo.txt'), 'r')
        gfxinfo = []
        for line in output.readlines():
            m = re.search('\((\d+)\): gfxinfo\[(\d+)\+?(\d?)\]=\S+=(\d+\.\d+)', line)
            if m:
                g = m.groups()
                gfxinfo.append((int(g[0]), int(g[1]), int(g[2]) if g[2] else 0, float(g[3])))
        output.close()

        data = {}
        gfxinfo = sorted(gfxinfo)
        pids = set([i[0] for i in gfxinfo])
        for pid in pids:
            m = max([i[1] for i in gfxinfo if i[0] == pid])
            item = [[0 for i in range(3)] for i in range(m + 1)]
            for i in [i for i in gfxinfo if i[0] == pid]:
                item[i[1]][i[2]] = i[3]
            data[pid] = item

        report = open(os.path.join(self.outdir, 'gfxinfo.csv'), 'w')
        report.write(codecs.BOM_UTF8)
        report.write('PID,ID,Draw,Process,Execute,Total\n')
        for pid in data:
            i = 0
            for item in data[pid]:
                if any(item):
                    report.write('{0},{1},{2},{3},{4},{5}\n'.format(pid, i, item[0] if item[0] else '',
                            item[1] if item[1] else '', item[2] if item[2] else '', sum(item)))
                i += 1
        report.close()

    def stop(self):
        self.p.terminate()

class LogcatSkpinfoThread(threading.Thread):

    def __init__(self, outdir):
        threading.Thread.__init__(self)
        self.outdir = outdir

    def run(self):
        os.system('adb logcat -c')
        output = open(os.path.join(self.outdir, 'skpinfo.txt'), 'w')
        self.p = subprocess.Popen('adb logcat -v time -s Choreographer:I I:s',
                shell=False, stdout=output, stderr=output)
        self.p.wait()
        output.close()

        output = open(os.path.join(self.outdir, 'skpinfo.txt'), 'r')
        stat = {}
        for line in output.readlines():
            m = re.search('Skipped (\d+) frames!', line)
            if m:
                c = int(m.groups()[0])
                stat.setdefault(c, 0)
                stat[c] += 1
        output.close()

        report = open(os.path.join(self.outdir, 'skpinfo.csv'), 'w')
        report.write(codecs.BOM_UTF8)
        report.write('丢帧数量,出现次数\n')
        if len(stat) > 0:
            for key in sorted(stat.keys(), reverse=True):
                report.write('{0},{1}\n'.format(key, stat[key]))
            report.write(',{0}\n'.format(sum(stat.values())))
        report.close()

    def stop(self):
        self.p.terminate()

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

def monkey(package=None):
    if package:
        outdir = os.path.join(workout, package)
        if not os.path.exists(outdir):
            os.mkdir(outdir)
    else:
        outdir = workout

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
    report.write('测试的随机数{0},预期测试次数{1},实际次数{2},测试时间{3},CRASH次数{4},NOT RESPONDING次数{5}\n'.format(data['seed'],
            data['count'], data['event'], round(data['time'] / 3600000.0, 2), data['crash'], data['anr']))
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

def getSceneInfo(name):
    outdir = os.path.join(workout, name)
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    t1 = LogcatGfxinfoThread(outdir)
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
    getSceneInfo('NativeListViewTest')
    getSceneInfo('ContactTest')
    getSceneInfo('DeveloperTest')
    getSceneInfo('GalleryTest')
    getSceneInfo('MultiTaskTest')
    getSceneInfo('BrowserTest')
    getSceneInfo('NoteScaleTest')
    getSceneInfo('LauncherTest')
    getSceneInfo('PressMenuTest')

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

def install(sdcard):
    os.popen('adb shell am startservice --user 0 -W -n com.ztemt.test.common/.PackageService --es command getLauncherList').readline()
    time.sleep(3)

    report = open(os.path.join(workout, 'install.csv'), 'w')
    report.write(codecs.BOM_UTF8)
    report.write('应用文件名,安装,启动,卸载,异常1,异常2,异常3\n')

    topapkdir = open(os.path.join(workdir, 'config.txt'), 'r').readlines()[1].strip()
    pattern = os.path.join(unicode(topapkdir, 'utf-8'), '*.apk')
    for filename in [x.encode('GB2312') for x in glob.glob(pattern)]:
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

        report.write('{0},{1},{2},{3},{4}\n'.format(os.path.basename(filename), 'Pass' if install else 'Fail',
                'Pass' if launch else 'Fail', 'Pass' if uninstall else 'Fail', except1 if except1 else '',
                crash if crash else anr if anr else '', except2 if except2 else ''))
        report.flush()
    report.close()

def main():
    state = os.popen('adb get-state').readlines()[-1].strip()
    if state == 'device':
        print('Operation type choices are:')
        print('    1. monkey')
        print('    2. single')
        print('    3. scenes')
        try:
            operation = input('\nWhich would you like? [1] ')
        except SyntaxError:
            operation = 1
        except NameError:
            sys.exit(2)

        print('\nInstall location choices are:')
        print('    1. internal storage')
        print('    2. sdcard')
        try:
            location = input('\nWhich would you like? [1] ')
        except SyntaxError:
            location = 1
        except NameError:
            sys.exit(2)

        global workout
        if not os.path.exists(workout):
            os.mkdir(workout)
        if operation == 1:
            workout = os.path.join(workout, 'monkey')
        elif operation == 2:
            workout = os.path.join(workout, 'single')
        elif operation == 3:
            workout = os.path.join(workout, 'scenes')
        else:
            sys.exit(2)
        if not os.path.exists(workout):
            os.mkdir(workout)

        model = os.popen('adb shell getprop ro.product.model').readline().strip()
        workout = os.path.join(workout, model)
        shutil.rmtree(workout, ignore_errors=True)
        if not os.path.exists(workout):
            os.mkdir(workout)

        os.popen('adb install -r \"{0}\"'.format(os.path.join(workdir, 'TestCommon.apk'))).readlines()
        os.popen('adb shell am startservice --user 0 -W -n com.ztemt.test.common/.PackageService --es command getLauncherList').readlines()
        time.sleep(3)
        jobj = eval(os.popen('adb shell cat /data/data/com.ztemt.test.common/files/launcher').readline())

        os.popen('adb push \"{0}\" /data/local/tmp'.format(os.path.join(workdir, 'automator.jar'))).readlines()
        os.popen('adb shell uiautomator runtest automator.jar -c com.android.settings.DevelopmentSettingsTestCase#testKeepScreenOn').readlines()
        os.popen('adb shell uiautomator runtest automator.jar -c com.android.settings.DevelopmentSettingsTestCase#testTrackFrameTimeDumpsysGfxinfo').readlines()

        packages = [line[8:].strip() for line in os.popen('adb shell pm list package -s').readlines()]
        packages = [package for package in packages if package in jobj]
        for package in packages:
            for item in jobj[package]:
                getAppsInfo(package, item['title'], item['activity'])
        if operation == 1:
            threads = []
            for package in packages:
                outdir = os.path.join(workout, package)
                if not os.path.exists(outdir):
                    os.mkdir(outdir)
                t1 = DumpsysMeminfoThread(package, 20, outdir)
                t2 = DumpsysGfxinfoThread(package,  5, outdir)
                threads.append(t1)
                threads.append(t2)
                t1.start()
                t2.start()
            t3 = DumpsysCpuinfoThread(None, 10, outdir)
            t3.start()
            monkey()
            for t in threads:
                t.stop()
            t3.stop()
            for t in threads:
                t.join()
            t3.join()
        elif operation == 2:
            for package in packages:
                outdir = os.path.join(workout, package)
                if not os.path.exists(outdir):
                    os.mkdir(outdir)
                t1 = DumpsysMeminfoThread(package, 20, outdir)
                t2 = DumpsysGfxinfoThread(package,  5, outdir)
                t3 = DumpsysCpuinfoThread(package, 10, outdir)
                t1.start()
                t2.start()
                t3.start()
                monkey(package)
                t1.stop()
                t2.stop()
                t3.stop()
                t1.join()
                t2.join()
                t3.join()
        elif operation == 3:
            scenes()

        install(location == 2)
        reboot()

        os.popen('adb uninstall com.ztemt.test.common').readlines()
    else:
        print('Please connect your device')

workdir = os.path.dirname(os.path.realpath(sys.argv[0]))
workout = os.path.join(workdir, 'out')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
