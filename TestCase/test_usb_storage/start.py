# -*- coding:UTF-8 -*-

import codecs
import os
import re
import shutil
import string
import sys
import time

from win32com.shell import shell, shellcon
import win32file

workdir = os.path.dirname(os.path.realpath(sys.argv[0]))

def test_storage():
    os.popen('adb install -r \"{0}\"'.format(os.path.join(workdir, 'TestKit.apk'))).readlines()
    os.popen('adb shell am startservice --user 0 -W -a com.ztemt.test.action.TEST_KIT --es command disableKeyguard').readlines()
    os.popen('adb push \"{0}\" /data/local/tmp'.format(os.path.join(workdir, 'automator.jar'))).readlines()
    os.popen('adb shell uiautomator runtest automator.jar -c com.android.settings.DevelopmentSettingsTestCase#testKeepScreenOn').readlines()
    os.popen('adb install -r \"{0}\"'.format(os.path.join(workdir, 'A1SDBench.apk'))).readlines()
    os.popen('adb shell uiautomator runtest automator.jar -c com.a1dev.sdbench.A1SDBenchTestCase#testBenchmark').readlines()
    lines = os.popen('adb shell cat /data/local/tmp/a1sdbenchmark').readlines()
    lines = [line.strip() + '\n' for line in lines if re.search('(.*),(.*)', line)]
    os.popen('adb uninstall com.a1dev.sdbench').readlines()
    os.popen('adb uninstall com.ztemt.test.kit').readlines()
    os.system('adb shell rm /data/local/tmp/automator.jar')
    return lines

def test_usb(type, fmt=False):
    if fmt:
        os.system('adb reboot')
        os.system('adb wait-for-device')
        while os.popen('adb shell getprop sys.boot_completed').readline().strip() != '1':
            time.sleep(3)
    os.popen('adb push \"{0}\" /data/local/tmp'.format(os.path.join(workdir, 'ramdisk.sh'))).readlines()
    os.popen('adb shell sh /data/local/tmp/ramdisk.sh').readlines()
    os.system('adb shell setprop sys.usb.config {0},adb'.format(type))
    os.system('adb wait-for-device')
    drive = None
    loop = 1
    read = 0
    write = 0
    while not drive:
        if loop > 20:
            break
        r = win32file.GetLogicalDrives()
        for d in range(26):
            if r>>d & 1 and win32file.GetDriveType(string.ascii_letters[d] + ':\\') == 2:
                drive = string.ascii_letters[d]
                break
        time.sleep(3)
        loop += 1
    if drive:
        if fmt:
            os.system('echo y | format {0}: /fs:fat32 /q'.format(drive))

        file1 = os.path.join(workdir, 'test.zip')
        file2 = os.path.join(drive + ':' + os.sep, 'test.zip')
        if os.path.exists(file2):
            os.remove(file2)

        st = time.time()
        shell.SHFileOperation((0, shellcon.FO_COPY, file1, file2, 0, None, None))
        write = round(os.path.getsize(file1) / 1048576.0 / (time.time() - st), 2)

        file3 = os.path.join(workdir, 'tmp.zip')
        if os.path.exists(file3):
            os.remove(file3)

        st = time.time()
        shell.SHFileOperation((0, shellcon.FO_COPY, file2, file3, 0, None, None))
        read = round(os.path.getsize(file2) / 1048576.0 / (time.time() - st), 2)

        os.remove(file2)
        os.remove(file3)
    os.popen('adb shell rm /data/local/tmp/ramdisk.sh').readlines()
    return (read, write)

def main():
    if os.name != 'nt':
        print('Please run on windows platform')
        sys.exit(2)

    if os.popen('adb get-state').readlines()[-1].strip() != 'device':
        print('Please connect your device')
        sys.exit(2)

    m = re.search('uid=(\d+)', os.popen('adb shell id').readline())
    if not m or m.groups()[0] != '0':
        print('Please provide the root version')
        sys.exit(2)

    workout = os.path.join(workdir, 'out')
    if not os.path.exists(workout):
        os.mkdir(workout)
    model = os.popen('adb shell getprop ro.product.model').readline().strip()
    workout = os.path.join(workout, model)
    if not os.path.exists(workout):
        os.mkdir(workout)
    workout = os.path.join(workout, time.strftime('%Y-%m-%d-%H-%M', time.localtime()))
    shutil.rmtree(workout, ignore_errors=True)
    if not os.path.exists(workout):
        os.mkdir(workout)

    pattern = '{0},Read {1[0]}MB/s Write {1[1]}MB/s\n'

    report = open(os.path.join(workout, 'benchmark.csv'), 'w')
    report.write(codecs.BOM_UTF8)
    report.writelines(test_storage())
    report.flush()
    report.write(pattern.format('ums', test_usb('mass_storage', True)))
    report.flush()
    report.write(pattern.format('mtp', test_usb('mtp')))
    report.flush()
    report.write(pattern.format('ptp', test_usb('ptp')))
    report.flush()
    report.close()

    os.system('adb reboot')
    os.system('adb wait-for-device')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
