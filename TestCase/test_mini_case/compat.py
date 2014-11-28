# -*- coding:UTF-8 -*-

import codecs
import glob
import os
import shutil
import sys
import time

workdir = os.path.dirname(os.path.realpath(sys.argv[0]))

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

def compat(workout):
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
