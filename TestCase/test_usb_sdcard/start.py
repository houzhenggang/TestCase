# -*- coding:UTF-8 -*-

import os
import re
import shutil
import sys
import time

def test_emmc():
    pass

def test_usb():
    os.popen('adb shell uiautomator runtest SystemUITest.jar -c com.android.systemui.test.UsbConnectOptionsTestCase#testEnableUMS')
    os.system('adb wait-for-device')
    os.popen('adb shell uiautomator runtest SystemUITest.jar -c com.android.systemui.test.UsbConnectOptionsTestCase#testDisableUMS')
    os.system('adb wait-for-device')
    os.popen('adb shell uiautomator runtest SystemUITest.jar -c com.android.systemui.test.UsbConnectOptionsTestCase#testEnableMTP')
    os.system('adb wait-for-device')
    os.popen('adb shell uiautomator runtest SystemUITest.jar -c com.android.systemui.test.UsbConnectOptionsTestCase#testDisableMTP')
    os.system('adb wait-for-device')
    os.popen('adb shell uiautomator runtest SystemUITest.jar -c com.android.systemui.test.UsbConnectOptionsTestCase#testEnablePTP')
    os.system('adb wait-for-device')
    os.popen('adb shell uiautomator runtest SystemUITest.jar -c com.android.systemui.test.UsbConnectOptionsTestCase#testDisablePTP')
    os.system('adb wait-for-device')

def test_usb_emmc():
    os.popen('adb shell uiautomator runtest SystemUITest.jar -c com.android.systemui.test.UsbConnectOptionsTestCase#testEnableUMS')
    os.system('adb wait-for-device')
    os.popen('adb shell uiautomator runtest SystemUITest.jar -c com.android.systemui.test.UsbConnectOptionsTestCase#testDisableUMS')
    os.system('adb wait-for-device')
    os.popen('adb shell uiautomator runtest SystemUITest.jar -c com.android.systemui.test.UsbConnectOptionsTestCase#testEnableMTP')
    os.system('adb wait-for-device')
    os.popen('adb shell uiautomator runtest SystemUITest.jar -c com.android.systemui.test.UsbConnectOptionsTestCase#testDisableMTP')
    os.system('adb wait-for-device')
    os.popen('adb shell uiautomator runtest SystemUITest.jar -c com.android.systemui.test.UsbConnectOptionsTestCase#testEnablePTP')
    os.system('adb wait-for-device')
    os.popen('adb shell uiautomator runtest SystemUITest.jar -c com.android.systemui.test.UsbConnectOptionsTestCase#testDisablePTP')
    os.system('adb wait-for-device')

def main():
    state = os.popen('adb get-state').readlines()[-1].strip()
    if state == 'device':
        m = re.search('uid=(\d+)', os.popen('adb shell id').readline())
        if m and m.groups()[0] == '0':
            global workout
            if not os.path.exists(workout):
                os.mkdir(workout)
            model = os.popen('adb shell getprop ro.product.model').readline().strip()
            workout = os.path.join(workout, model)
            shutil.rmtree(workout, ignore_errors=True)
            if not os.path.exists(workout):
                os.mkdir(workout)

            os.popen('adb push \"{0}\" /data/local/tmp'.format(os.path.join(workdir, 'SystemUITest.jar')))
            test_usb()
            os.popen('adb shell rm /data/local/tmp/SystemUITest.jar')
        else:
            print('Please provide root version')
    else:
        print('Please connect your device')

workdir = os.path.dirname(os.path.realpath(sys.argv[0]))
workout = os.path.join(workdir, 'out')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
