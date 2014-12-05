# -*- coding:UTF-8 -*-

import os
import sys
import time

def update():
    workdir = os.path.dirname(os.path.realpath(sys.argv[0]))
    model = os.popen('adb shell getprop ro.product.model').readline().strip()
    builddir = open(os.path.join(workdir, 'config.txt'), 'r').readlines()[7].strip()
    updates = []

    for dirpath, dirnames, names in os.walk(builddir):
        if os.path.basename(dirpath) == model:
            for name in names:
                updates.append(os.path.join(dirpath, name))

    if updates:
        os.popen('adb push \"{0}\" /sdcard/update.zip'.format(max(updates, key=os.path.basename))).readlines()
        os.popen('adb shell uiautomator runtest automator.jar -c cn.nubia.systemupdate.SystemUpdateTestCase#testLocalUpdate').readlines()
        time.sleep(30)
        os.system('adb wait-for-device')
        while os.popen('adb shell getprop sys.boot_completed').readline().strip() != '1':
            time.sleep(3)

if __name__ == '__main__':
    update()
