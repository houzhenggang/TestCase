# -*- coding:UTF-8 -*-

import getopt
import os
import shutil
import sys
import time

import adbkit as adb
import compat
import launch
import scenes
import stress
import update
import uptime

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 's:m:t:')
        opts = dict(opts)
    except getopt.GetoptError:
        sys.exit(2)

    devices = adb.devices()
    adb.sno = opts['-s'] if '-s' in opts else ''
    if not adb.sno:
        index = 0
        if len(devices) > 1:
            print('Device serial number choices are:')
            for i in range(len(devices)):
                print('    {0}. {1}'.format(i + 1, devices[i][0]))
            try:
                index = input('\nWhich would you like? [1] ') - 1
                index = divmod(index, len(devices))[1]
            except SyntaxError:
                pass
            except NameError:
                pass
            print('')
        adb.sno = devices[index][0]

    if adb.adb('get-state')[-1].strip() != 'device':
        if adb.sno:
            print('Make sure your device {0} only online'.format(adb.sno))
        else:
            print('Please connect your device')
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
        except SyntaxError:
            pass
        except NameError:
            sys.exit(2)
        print('')

    operation = 2
    if '4' in str(module):
        if '-t' in opts:
            try:
                operation = int(opts['-t'])
            except ValueError:
                pass
        else:
            print('Monkey type choices are:')
            print('    1. monkey')
            print('    2. single')
            try:
                operation = input('\nWhich would you like? [2] ')
            except SyntaxError:
                pass
            except NameError:
                sys.exit(2)
            print('')

    workdir = os.path.dirname(os.path.realpath(sys.argv[0]))
    workout = os.path.join(workdir, 'out')
    if not os.path.exists(workout):
        os.mkdir(workout)

    workout = os.path.join(workout, adb.getprop('ro.product.model'))
    #shutil.rmtree(workout, ignore_errors=True)
    if not os.path.exists(workout):
        os.mkdir(workout)

    adb.install(os.path.join(workdir, 'TestKit.apk'))
    adb.push(os.path.join(workdir, 'automator.jar'), '/data/local/tmp')

    adb.shell('uiautomator runtest automator.jar -c com.android.systemui.SleepWakeupTestCase#testWakeup')
    adb.shell('am startservice --user 0 -W -a com.ztemt.test.action.TEST_KIT --es command disableKeyguard')
    adb.shell('uiautomator runtest automator.jar -c com.android.settings.DevelopmentSettingsTestCase#testKeepScreenOn')

    adb.shell('am startservice --user 0 -W -a com.ztemt.test.action.TEST_KIT --es command getLauncherList')
    time.sleep(3)
    launchers = eval(adb.shell('cat /data/data/com.ztemt.test.kit/files/launcher')[0])

    packages = [line[8:].strip() for line in adb.shell('pm list package -s')]
    packages = [package for package in packages if package in launchers]
    begin = time.time()

    for i in str(module):
        adb.reboot()
        adb.shell('am startservice --user 0 -W -a com.ztemt.test.action.TEST_KIT --es command disableKeyguard')
        if i == '1':
            update.execute(workout)
        elif i == '2':
            launch.execute(workout, packages, launchers)
        elif i == '3':
            scenes.execute(workout)
        elif i == '4':
            stress.execute(workout, packages, operation == 2)
        elif i == '5':
            compat.execute(workout)
        elif i == '6':
            uptime.execute(workout)

    raw_input('All test finished: elapsed time {0}s, press ENTER to exit.'.format(round(time.time() - begin, 2)))
    adb.uninstall('com.ztemt.test.kit')

    # generate chart author by guomengru
    try:
        import chart.run as runner
        runner.run(workout)
    except ImportError:
        pass

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
