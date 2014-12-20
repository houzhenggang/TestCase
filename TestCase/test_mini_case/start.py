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

    workdir = os.path.dirname(os.path.realpath(sys.argv[0]))
    workout = os.path.join(workdir, 'out')
    if not os.path.exists(workout):
        os.mkdir(workout)
    workout = os.path.join(workout, adb.getprop('ro.product.model'))
    if not os.path.exists(workout):
        os.mkdir(workout)

    module = [2, 3, 4, 5, 6]
    selected = []
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
        selects = raw_input('\nWhich would you like? [2,3,4,5,6] ').split(',')
        for select in selects:
            try:
                selected.append(int(select.strip()))
            except ValueError:
                continue
        module = selected if selected else module
        print('')

    adb.install(os.path.join(workdir, 'TestKit.apk'))
    adb.shellreadlines('am startservice --user 0 -W -a com.ztemt.test.action.TEST_KIT --es command getLauncherList')
    time.sleep(3)
    launchers = eval(adb.shellreadline('cat /data/data/com.ztemt.test.kit/files/launcher'))
    packages = [line[8:].strip() for line in adb.shellreadlines('pm list package -s')]
    packages = [package for package in packages if package in launchers]

    executor = {}
    for i in module:
        if i == 1:
            executor[i] = update.Executor(adb, workout)
            executor[i].setup()
        elif i == 2:
            executor[i] = launch.Executor(adb, workout, packages, launchers)
            executor[i].setup()
        elif i == 3:
            executor[i] = scenes.Executor(adb, workout)
            executor[i].setup()
        elif i == 4:
            executor[i] = monkey.Executor(adb, workout, packages)
            executor[i].setup()
        elif i == 5:
            executor[i] = compat.Executor(adb, workout)
            executor[i].setup()
        elif i == 6:
            executor[i] = uptime.Executor(adb, workout)
            executor[i].setup()
        elif i == 7:
            executor[i] = stress.Executor(adb, workout)
            executor[i].setup()

    adb.push(os.path.join(workdir, 'automator.jar'), '/data/local/tmp')
    adb.shellreadlines('uiautomator runtest automator.jar -c com.android.systemui.SleepWakeupTestCase#testWakeup')
    adb.shellreadlines('am startservice --user 0 -W -a com.ztemt.test.action.TEST_KIT --es command disableKeyguard')
    adb.shellreadlines('uiautomator runtest automator.jar -c com.android.settings.DevelopmentSettingsTestCase#testKeepScreenOn')

    start = time.time()
    for i in module:
        adb.reboot()
        adb.shellreadlines('am startservice --user 0 -W -a com.ztemt.test.action.TEST_KIT --es command disableKeyguard')
        executor[i].execute()
    end = time.time()

    # generate chart author by guomengru
    try:
        import chart.run as runner
        runner.run(workout)
    except ImportError:
        pass

    raw_input('All test finished: elapsed time {0}s, press ENTER to exit.'.format(round(end - start, 2)))
    adb.uninstall('com.ztemt.test.kit')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
