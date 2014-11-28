# -*- coding:UTF-8 -*-

import codecs
import glob
import os
import re
import subprocess
import sys
import threading

import stress

workdir = os.path.dirname(os.path.realpath(sys.argv[0]))

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
                file = '{0}.png'.format('-'.join(m.groups()[0].split(':')))
                os.system('adb shell screencap -p /data/local/tmp/screenshot.png')
                os.popen('adb pull /data/local/tmp/screenshot.png \"{0}\"'.format(file)).readline()
                c = int(m.groups()[1])
                stat.setdefault(c, 0)
                stat[c] += 1
                output.write(line)
                output.flush()
        output.close()

        report = open(os.path.join(self.outdir, 'skpinfo.csv'), 'w')
        report.write(codecs.BOM_UTF8)
        report.write('丢帧数量,丢帧次数\n')
        if len(stat) > 0:
            for key in sorted(stat.keys(), reverse=True):
                report.write('{0},{1}\n'.format(key, stat[key]))
        report.close()

        file = os.path.join(os.path.dirname(self.outdir), 'skpinfo.csv')
        if os.path.exists(file):
            report = open(file, 'a+')
        else:
            report = open(file, 'w')
            report.write(codecs.BOM_UTF8)
            report.write('项目,丢帧数量,丢帧次数\n')
        report.write('{0},{1},{2}\n'.format(os.path.basename(self.outdir), sum([x * stat[x] for x in stat]), sum(stat.values())))
        report.close()

    def stop(self):
        self.p.terminate()

def scene(name, package, workout):
    outdir = os.path.join(workout, 'scenes')
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    outdir = os.path.join(outdir, name)
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    t1 = stress.DumpsysGfxinfoThread(package, 1, outdir)
    t2 = LogcatSkpinfoThread(outdir)
    t1.start()
    t2.start()
    subprocess.Popen('adb shell uiautomator runtest scenes.jar -c cn.nubia.test.{0}'.format(name),
            shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).wait()
    t1.stop()
    t2.stop()
    t1.join()
    t2.join()

def scenes(workout):
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
    scene('NativeListViewTest', 'com.example.android.apis', workout)
    scene('ContactTest', 'com.android.contacts', workout)
    scene('DeveloperTest', 'com.android.settings', workout)
    scene('GalleryTest', 'com.android.gallery3d', workout)
    scene('MultiTaskTest', 'com.android.systemui', workout)
    scene('BrowserTest', 'com.android.browser', workout)
    scene('NoteScaleTest', 'com.android.contacts', workout)
    scene('LauncherTest', 'cn.nubia.launcher', workout)
    scene('PressMenuTest', 'cn.nubia.launcher', workout)
