# -*- coding:UTF-8 -*-

import codecs
import csv
import glob
import os
import shutil
import subprocess
import sys
import threading
import time

class Executor(object):

    def __init__(self, adb, workout):
        self.adb = adb
        self.workout = workout

    def install(self, sdcard=False):
        launch = True
        except1 = except2 = except3 = None
        uninstall = False

        lines = self.adb.install(None, downgrade=True, sdcard=sdcard)
        install = 'Success' in [line.strip() for line in lines]
        if install:
            time.sleep(3)
            package = self.adb.shellreadline('cat /data/data/com.ztemt.test.kit/files/package')
            self.adb.shellreadlines('am startservice --user 0 -W -a com.ztemt.test.action.TEST_KIT --es command disableKeyguard')
            lines = self.adb.shellreadlines('monkey -p {0} -s 10 --throttle 10000 --ignore-timeouts --ignore-crashes -v 10'.format(package))
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
            p = self.adb.shellopen('pm uninstall {0}'.format(package))
            y = lambda x: x.terminate()
            t = threading.Timer(15, y, args=(p,))
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
        return (y(install), y(launch), y(uninstall), z(except1), z(except2), z(except3))

    def execute(self):
        remotedir = open(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'config.txt'), 'r').readlines()[1].strip()

        report = open(os.path.join(self.workout, 'compat.csv'), 'wb')
        report.write(codecs.BOM_UTF8)
        writer = csv.writer(report, quoting=csv.QUOTE_ALL)
        writer.writerow(['应用文件名', '安装i', '启动i', '卸载i', '安装s', '启动s', '卸载s', '异常i-1', '异常i-2', '异常i-3', '异常s-1', '异常s-2', '异常s-3'])

        for filename in glob.glob(os.path.join(unicode(remotedir, 'utf-8'), '*.apk')):
            self.adb.push(filename.encode('gb2312'), '/data/local/tmp/tmp.apk')
            r1 = self.install()
            r2 = self.install(True)
            writer.writerow([os.path.basename(filename), r1[0], r1[1], r1[2], r2[0], r2[1], r2[2], r1[3], r1[4], r1[5], r2[3], r2[4], r2[5]])
            report.flush()
        report.close()
