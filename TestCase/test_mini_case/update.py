# -*- coding:UTF-8 -*-

import os
import sys
import time

import adbkit as adb

def execute(workout):
    workdir = os.path.dirname(os.path.realpath(sys.argv[0]))
    model = os.popen('adb -s {0} shell getprop ro.product.model'.format(adb.sno)).readline().strip()
    builddir = open(os.path.join(workdir, 'config.txt'), 'r').readlines()[7].strip()
    updates = []

    for dirpath, dirnames, names in os.walk(builddir):
        if os.path.basename(dirpath) == model:
            for name in names:
                updates.append(os.path.join(dirpath, name))

    if updates:
        os.popen('adb -s {0} push \"{1}\" /sdcard/update.zip'.format(adb.sno, max(updates, key=os.path.basename))).readlines()
        os.popen('adb -s {0} shell uiautomator runtest automator.jar -c cn.nubia.systemupdate.SystemUpdateTestCase#testLocalUpdate'.format(adb.sno)).readlines()
        time.sleep(30)
        os.system('adb -s {0} wait-for-device'.format(adb.sno))
        while os.popen('adb -s {0} shell getprop sys.boot_completed'.format(adb.sno)).readline().strip() != '1':
            time.sleep(3)
