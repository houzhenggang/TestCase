# -*- coding:UTF-8 -*-

import getopt
import os
import re
import shutil
import sys
import time

import adbkit
import compat
import memory
import monkey
import launch
import scenes
import stress
import update
import uptime

def importdata(adb, type, p1, p2, p3, p4):
    pimdir = '/sdcard/nubia/PIM'
    mediadir = '/sdcard/Media'

    adb.shell('rm -rf {0}'.format(pimdir))
    adb.shell('rm -rf {0}'.format(mediadir))

    adb.shell('mkdir -p {0}'.format(pimdir))
    if type == 1:
        adb.push(unicode(p1.strip(), 'utf-8').encode('gb2312'), pimdir)
    elif type == 2:
        adb.push(unicode(p2.strip(), 'utf-8').encode('gb2312'), pimdir)

    adb.shell('am force-stop cn.nubia.databackup')
    adb.kit.restoredata()

    adb.shell('rm -rf {0}'.format(pimdir))
    adb.shell('rm -rf {0}'.format(mediadir))

    adb.shell('mkdir -p {0}'.format(mediadir))
    if type == 1:
        adb.push(unicode(p3.strip(), 'utf-8').encode('gb2312'), mediadir)
    elif type == 2:
        adb.push(unicode(p4.strip(), 'utf-8').encode('gb2312'), mediadir)

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
                print('    {0:>2}. {1}'.format(i + 1, devices[i]))
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
            raw_input('Make sure your device {0} only online. '.format(serialno))
        else:
            raw_input('Please connect your device. ')
        sys.exit(2)

    if adb.ismonkey() or adb.isuiautomator():
        raw_input('Please wait for the current test completed. ')
        sys.exit(2)

    workdir = os.path.dirname(os.path.realpath(sys.argv[0]))
    workout = os.path.join(workdir, 'out')
    if not os.path.exists(workout):
        os.mkdir(workout)
    workout = os.path.join(workout, adb.getprop('ro.product.model'))
    if not os.path.exists(workout):
        os.mkdir(workout)
    workout = os.path.join(workout, adb.getprop('ro.build.display.id'))
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
        print('     1. system update')
        print('     2. start time')
        print('     3. fluency test')
        print('     4. monkey test')
        print('     5. compatibility test')
        print('     6. boot time')
        print('     7. stress test')
        print('     8. memory test')
        selects = raw_input('\nWhich would you like? [2,3,4,5,6] ').split(',')
        for select in selects:
            try:
                selected.append(int(select.strip()))
            except ValueError:
                continue
        module = selected if selected else module
        print('')

    packages = adb.kit.getpackages()
    testpkgs = [line[8:].strip() for line in adb.shellreadlines('pm list package -s')]
    packages = dict([x for x in packages.items() if x[0] in testpkgs])

    executor = {}
    for i in module:
        if i == 1:
            executor[i] = update.Executor(adb, workout)
            executor[i].setup()
        elif i == 2:
            executor[i] = launch.Executor(adb, workout, packages)
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
        elif i == 8:
            executor[i] = memory.Executor(adb, workout, packages)
            executor[i].setup()

    raw_input('Login your apps, press ENTER to continue after finished. ')

    print('\nImported user data type choices are:')
    print('     1.  general condition')
    print('     2.  stress condition')
    print('     3.  none')
    try:
        selected = input('\nWhich would you like? [1] ')
    except SyntaxError:
        selected = 1
    except NameError:
        sys.exit(2)
    print('')

    adb.kit.wakeup()
    adb.kit.disablekeyguard()
    adb.kit.keepscreenon()

    # import user data
    if not selected == 3:
        m = re.search('[ ]+(\d+\.\d+)(\S+)[ ]+(\d+\.\d+)(\S+)[ ]+(\d+\.\d+)(\S+)[ ]+\d+', adb.shellreadlines('df data')[-1])
        if m:
            z = lambda x, y: x * pow(1024, 'BKMGT'.find(y))
            g = m.groups()
            s = z(float(g[0]), g[1])
        else:
            s = 0

        configs = open(os.path.join(workdir, 'config.txt'), 'r').readlines()
        if s > 2.5 * pow(1024, 3):
            importdata(adb, selected, configs[1], configs[5], configs[3], configs[7])
        else:
            importdata(adb, selected, configs[9], configs[13], configs[11], configs[15])

    start = time.time()
    for i in module:
        executor[i].execute()
    end = time.time()

    # generate chart author by guomengru
    try:
        import chart.run as runner
        runner.run(workout)
    except ImportError:
        pass

    raw_input('All test finished: elapsed time {0}s, press ENTER to exit.'.format(round(end - start, 2)))
    adb.kit.destroy()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
