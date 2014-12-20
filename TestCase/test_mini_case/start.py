# -*- coding:UTF-8 -*-

import getopt
import os
import shutil
import sys
import time

import adbkit
import compat
import monkey
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

    devices = adbkit.devices()
    serialno = opts['-s'] if '-s' in opts else ''
    if not serialno and len(devices) > 0:
        index = 0
        if len(devices) > 1:
            print('Device serial number choices are:')
            for i in range(len(devices)):
                print('    {0}. {1}'.format(i + 1, devices[i]))
            try:
                index = input('\nWhich would you like? [1] ') - 1
                index = divmod(index, len(devices))[1]
            except SyntaxError:
                pass
            except NameError:
                pass
            print('')
        serialno = devices[index]

    adb = adbkit.Adb(serialno)
    if adb.adbreadline('get-state') != 'device':
        if serialno:
            print('Make sure your device {0} only online'.format(serialno))
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
        print('    7. stress test')
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

    adb.shellreadlines('uiautomator runtest automator.jar -c com.android.systemui.SleepWakeupTestCase#testWakeup')
    adb.shellreadlines('am startservice --user 0 -W -a com.ztemt.test.action.TEST_KIT --es command disableKeyguard')
    adb.shellreadlines('uiautomator runtest automator.jar -c com.android.settings.DevelopmentSettingsTestCase#testKeepScreenOn')

    adb.shellreadlines('am startservice --user 0 -W -a com.ztemt.test.action.TEST_KIT --es command getLauncherList')
    time.sleep(3)
    launchers = eval(adb.shellreadline('cat /data/data/com.ztemt.test.kit/files/launcher'))

    packages = [line[8:].strip() for line in adb.shellreadlines('pm list package -s')]
    packages = [package for package in packages if package in launchers]
    begin = time.time()

    for i in str(module):
        adb.reboot()
        adb.shellreadlines('am startservice --user 0 -W -a com.ztemt.test.action.TEST_KIT --es command disableKeyguard')
        if i == '1':
            update.Executor(adb, workout).execute()
        elif i == '2':
            launch.Executor(adb, workout).execute(packages, launchers)
        elif i == '3':
            scenes.Executor(adb, workout).execute()
        elif i == '4':
            monkey.Executor(adb, workout).execute(packages, operation == 2)
        elif i == '5':
            compat.Executor(adb, workout).execute()
        elif i == '6':
            uptime.Executor(adb, workout).execute()
        elif i == '7':
            stress.Executor(adb, workout).execute()

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
