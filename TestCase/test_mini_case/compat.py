# -*- coding:UTF-8 -*-

import codecs
import glob
import os
import shutil
import sys
import time

workdir = os.path.dirname(os.path.realpath(sys.argv[0]))

def install(filename, sdcard=False):
    os.popen('adb shell am startservice --user 0 -W -a com.ztemt.test.action.TEST_KIT --es command disableKeyguard').readlines()
    time.sleep(3)

    launch = True
    except1 = except2 = except3 = None
    uninstall = False

    os.popen('adb push \"{0}\" /data/local/tmp/tmp.apk'.format(filename)).readlines()
    lines = os.popen('adb shell pm install {0} -d -r /data/local/tmp/tmp.apk'.format('-s' if sdcard else '')).readlines()
    install = 'Success' in [line.strip() for line in lines]
    if install:
        time.sleep(3)
        package = os.popen('adb shell cat /data/data/com.ztemt.test.kit/files/package').readline()
        lines = os.popen('adb shell monkey -p {0} -s 10 --throttle 10000 --ignore-timeouts --ignore-crashes -v 10'.format(package)).readlines()
        for line in lines:
            if line.startswith('// CRASH: {0}'.format(package)):
                launch = False
            elif not launch and line.startswith('// Long Msg:'):
                except2 = 'CRASH: {0}'.format(line[13:].strip())
                break
            elif line.startswith('// NOT RESPONDING: {0}'.format(package)):
                launch = False
            elif not launch and line.startswith('Reason:'):
                except2 = 'ANR: {0}'.format(line[8:].strip())
                break
        time.sleep(3)
        lines = os.popen('adb uninstall {0}'.format(package)).readlines()
        uninstall = 'Success' in [line.strip() for line in lines]
        if not uninstall:
            except3 = lines[-1].strip()
    else:
        except1 = lines[-1].strip()
        launch = False

    y = lambda x: 'Pass' if x else 'Fail'
    z = lambda x: x if x else ''
    return (y(install), y(launch), y(uninstall), z(except1), z(except2), z(except3))

def compat(workout):
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
