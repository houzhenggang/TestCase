# -*- coding: utf-8 -*-

import codecs
import csv
import glob
import os
import re
import shutil
import subprocess
import sys
import threading
import time

from common import Apk, workdir

class Executor(object):

    def __init__(self, adb, workout):
        self.adb = adb
        self.workout = workout

    def title(self):
        return u'兼容性测试'

    def setup(self):
        pass

    def install(self, package, sdcard=False):
        launch = True
        except1 = except2 = except3 = None
        uninstall = False

        p = self.adb.shellopen('pm install -r -d {0} /data/local/tmp/tmp.apk'.format('-s' if sdcard else ''))
        y = lambda x: x.terminate()
        t = threading.Timer(90, y, args=(p,))
        t.start()
        lines = p.stdout.readlines()
        t.cancel()

        install = 'Success' in [line.strip() for line in lines]
        if install:
            p = self.adb.shellopen('monkey -p {0} -s 10 --throttle 10000 --ignore-timeouts --ignore-crashes -v 10'.format(package))
            y = lambda x: self.adb.kill('com.android.commands.monkey')
            t = threading.Timer(60, y, args=(p,))
            t.start()
            for line in p.stdout.readlines():
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
            t.cancel()

            time.sleep(3)
            p = self.adb.shellopen('pm uninstall {0}'.format(package))
            y = lambda x: x.terminate()
            t = threading.Timer(60, y, args=(p,))
            t.start()
            lines = p.stdout.readlines()
            t.cancel()

            uninstall = 'Success' in [line.strip() for line in lines]
            if not uninstall:
                except3 = lines[-1].strip() if lines else 'Unknown'
        else:
            except1 = lines[-1].strip() if lines else 'Unknown'
            launch = False

        y = lambda x: 'Pass' if x else 'Fail'
        z = lambda x: x if x else ''
        return y(install), y(launch), y(uninstall), z(except1), z(except2), z(except3)

    def execute(self, log):
        log(self.msg(u'正在重启'))
        self.adb.reboot(5)
        self.adb.kit.disablekeyguard()
        remotedir = open(os.path.join(workdir, 'compat', 'config.txt'), 'r').readlines()[1].strip()

        pattern = re.compile('[ ]+(\d+\.\d+)(\S+)[ ]+(\d+\.\d+)(\S+)[ ]+(\d+\.\d+)(\S+)[ ]+\d+')
        m1 = pattern.search(self.adb.shellreadlines('df data')[-1])
        m2 = pattern.search(self.adb.shellreadlines('df sdcard')[-1])
        shareddata = m1 and m2 and m1.groups() == m2.groups()

        report = open(os.path.join(self.workout, 'compat.csv'), 'wb')
        report.write(codecs.BOM_UTF8)
        writer = csv.writer(report, quoting=csv.QUOTE_ALL)
        if shareddata:
            writer.writerow(['文件名', '应用名', '包名', '版本', '安装', '启动', '卸载', '异常1', '异常2', '异常3'])
        else:
            writer.writerow(['文件名', '应用名', '包名', '版本', '安装i', '启动i', '卸载i', '安装s', '启动s', '卸载s',
                    '异常i-1', '异常i-2', '异常i-3', '异常s-1', '异常s-2', '异常s-3'])

        filenames = glob.glob(os.path.join(unicode(remotedir, 'utf-8'), '*.apk'))
        for i, filename in enumerate(filenames, 1):
            apkfile = filename.encode('gb2312')
            apk = Apk(apkfile)
            apkname = os.path.basename(filename)
            if apk.package:
                log(self.msg(u'正在检查 {0} {1}/{2}'.format(apkname, i, len(filenames))))
                self.adb.push(apkfile, '/data/local/tmp/tmp.apk')
                r1 = self.install(apk.package)
                if shareddata:
                    writer.writerow([apkname, apk.label, apk.package, apk.version, r1[0], r1[1], r1[2],
                            r1[3], r1[4], r1[5]])
                else:
                    r2 = self.install(apk.package, True)
                    writer.writerow([apkname, apk.label, apk.package, apk.version, r1[0], r1[1], r1[2],
                            r2[0], r2[1], r2[2], r1[3], r1[4], r1[5], r2[3], r2[4], r2[5]])
                report.flush()
            else:
                log(self.msg(u'无法解析 {0} {1}/{2}'.format(apkname, i, len(filenames))), 'red')
        report.close()

    def msg(self, text):
        return u'[{0}] {1}'.format(self.title(), text)
