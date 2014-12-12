# -*- coding:UTF-8 -*-

import getopt
import os
import shutil
import sys
import time

import compat
import launch
import scenes
import stress
import update
import uptime

def main():
    if os.popen('adb get-state').readlines()[-1].strip() != 'device':
        print('Please connect your device')
        sys.exit(2)

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'm:t:')
        opts = dict(opts)
    except getopt.GetoptError:
        sys.exit(2)

    module = 23456
    if '-m' in opts:
        try:
            module = int(opts['-m'])
        except ValueError:
            pass
    else:
        print('Module name choices are:')
        print('    1. system update')
        print('    2. start time')
        print('    3. fluency test')
        print('    4. monkey test')
        print('    5. compatibility test')
        print('    6. boot time')
        try:
            module = input('\nWhich would you like? [23456] ')
        except NameError:
            sys.exit(2)
        except SyntaxError:
            pass

    operation = 2
    if '4' in str(module):
        if '-t' in opts:
            try:
                operation = int(opts['-t'])
            except ValueError:
                pass
        else:
            print('\nMonkey type choices are:')
            print('    1. monkey')
            print('    2. single')
            try:
                operation = input('\nWhich would you like? [2] ')
            except NameError:
                sys.exit(2)
            except SyntaxError:
                pass

    workdir = os.path.dirname(os.path.realpath(sys.argv[0]))
    workout = os.path.join(workdir, 'out')
    if not os.path.exists(workout):
        os.mkdir(workout)
    model = os.popen('adb shell getprop ro.product.model').readline().strip()
    workout = os.path.join(workout, model)
    shutil.rmtree(workout, ignore_errors=True)
    if not os.path.exists(workout):
        os.mkdir(workout)

    os.popen('adb push \"{0}\" /data/local/tmp/tmp.apk'.format(os.path.join(workdir, 'TestKit.apk'))).readlines()
    os.popen('adb shell pm install -r /data/local/tmp/tmp.apk').readlines()
    os.popen('adb shell am startservice --user 0 -W -a com.ztemt.test.action.TEST_KIT --es command disableKeyguard').readlines()
    os.popen('adb shell am startservice --user 0 -W -a com.ztemt.test.action.TEST_KIT --es command getLauncherList').readlines()
    time.sleep(3)
    launchers = eval(os.popen('adb shell cat /data/data/com.ztemt.test.kit/files/launcher').readline())

    os.popen('adb push \"{0}\" /data/local/tmp'.format(os.path.join(workdir, 'automator.jar'))).readlines()
    os.popen('adb shell uiautomator runtest automator.jar -c com.android.settings.DevelopmentSettingsTestCase#testKeepScreenOn').readlines()

    packages = [line[8:].strip() for line in os.popen('adb shell pm list package -s').readlines()]
    packages = [package for package in packages if package in launchers]
    begin = time.time()

    for i in str(module):
        uptime.reboot()
        os.popen('adb shell am startservice --user 0 -W -a com.ztemt.test.action.TEST_KIT --es command disableKeyguard').readlines()
        if i == '1':
            update.update()
        elif i == '2':
            launch.launch(workout, packages, launchers)
        elif i == '3':
            os.popen('adb shell uiautomator runtest automator.jar -c com.android.settings.DevelopmentSettingsTestCase#testTrackFrameTimeDumpsysGfxinfo').readlines()
            scenes.scenes(workout)
        elif i == '4':
            os.popen('adb shell uiautomator runtest automator.jar -c com.android.settings.DevelopmentSettingsTestCase#testTrackFrameTimeDumpsysGfxinfo').readlines()
            stress.stress(workout, packages, operation == 2)
        elif i == '5':
            compat.compat(workout)
        elif i == '6':
            uptime.uptime(workout)

    raw_input('\nAll test finished: elapsed time {0}s, press ENTER to exit.'.format(round(time.time() - begin, 2)))
    os.popen('adb uninstall com.ztemt.test.kit').readlines()

    # generate chart author by guomengru
    try:
        import chart.run as runner
        runner.run(workdir)
    except ImportError:
        pass

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
