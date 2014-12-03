# -*- coding:UTF-8 -*-

import os
import re
import shutil
import sys
import time

def test_emmc():
    for c in [chr(n) for n in range(67, 91)]:
        if os.path.exists(os.path.join(c + ':' + os.sep + 'system_lost_file_test', 'adb_test.cmd')):
            print(c)
            break

def test_usb():
    os.popen('adb shell uiautomator runtest automator.jar -c com.android.systemui.UsbConnectOptionsTestCase#testEnableUMS')
    os.system('adb wait-for-device')
    os.popen('adb shell uiautomator runtest automator.jar -c com.android.systemui.UsbConnectOptionsTestCase#testDisableUMS')
    os.system('adb wait-for-device')
    os.popen('adb shell uiautomator runtest automator.jar -c com.android.systemui.UsbConnectOptionsTestCase#testEnableMTP')
    os.system('adb wait-for-device')
    os.popen('adb shell uiautomator runtest automator.jar -c com.android.systemui.UsbConnectOptionsTestCase#testDisableMTP')
    os.system('adb wait-for-device')
    os.popen('adb shell uiautomator runtest automator.jar -c com.android.systemui.UsbConnectOptionsTestCase#testEnablePTP')
    os.system('adb wait-for-device')
    os.popen('adb shell uiautomator runtest automator.jar -c com.android.systemui.UsbConnectOptionsTestCase#testDisablePTP')
    os.system('adb wait-for-device')

def test_usb_emmc():
    os.popen('adb shell uiautomator runtest automator.jar -c com.android.systemui.UsbConnectOptionsTestCase#testEnableUMS')
    os.system('adb wait-for-device')
    os.popen('adb shell uiautomator runtest automator.jar -c com.android.systemui.UsbConnectOptionsTestCase#testDisableUMS')
    os.system('adb wait-for-device')
    os.popen('adb shell uiautomator runtest automator.jar -c com.android.systemui.UsbConnectOptionsTestCase#testEnableMTP')
    os.system('adb wait-for-device')
    os.popen('adb shell uiautomator runtest automator.jar -c com.android.systemui.UsbConnectOptionsTestCase#testDisableMTP')
    os.system('adb wait-for-device')
    os.popen('adb shell uiautomator runtest automator.jar -c com.android.systemui.UsbConnectOptionsTestCase#testEnablePTP')
    os.system('adb wait-for-device')
    os.popen('adb shell uiautomator runtest automator.jar -c com.android.systemui.UsbConnectOptionsTestCase#testDisablePTP')
    os.system('adb wait-for-device')

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

    workdir = os.path.dirname(os.path.realpath(sys.argv[0]))
    workout = os.path.join(workdir, 'out')
    if not os.path.exists(workout):
        os.mkdir(workout)
    model = os.popen('adb shell getprop ro.product.model').readline().strip()
    workout = os.path.join(workout, model)
    shutil.rmtree(workout, ignore_errors=True)
    if not os.path.exists(workout):
        os.mkdir(workout)

    os.popen('adb push \"{0}\" /data/local/tmp'.format(os.path.join(workdir, 'automator.jar')))
    test_emmc()
    os.popen('adb shell rm /data/local/tmp/automator.jar')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
