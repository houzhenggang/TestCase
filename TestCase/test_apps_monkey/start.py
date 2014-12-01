# -*- coding:UTF-8 -*-

import glob
import os
import shutil
import subprocess
import sys
import time

def main():
    state = os.popen('adb get-state').readlines()[-1].strip()
    if state == 'device':
        try:
            count = input('\nPlease input monkey count. [300000] ')
        except SyntaxError:
            count = 300000
        except NameError:
            sys.exit(2)

        global workout
        if not os.path.exists(workout):
            os.mkdir(workout)
        model = os.popen('adb shell getprop ro.product.model').readline().strip()
        workout = os.path.join(workout, model)
        shutil.rmtree(workout, ignore_errors=True)
        if not os.path.exists(workout):
            os.mkdir(workout)

        os.popen('adb install -r \"{0}\"'.format(os.path.join(workdir, 'TestKit.apk'))).readlines()

        pattern = os.path.join(os.path.join(workdir, 'apk'), '*.apk')
        for filename in glob.glob(pattern):
            os.popen('adb shell am startservice --user 0 -W -a com.ztemt.test.action.TEST_KIT').readlines()
            time.sleep(3)
            lines = os.popen('adb install -r \"{0}\"'.format(filename)).readlines()
            if 'Success' in [line.strip() for line in lines]:
                time.sleep(3)
                package = os.popen('adb shell cat /data/data/com.ztemt.test.kit/files/package').readline()
                output = open(os.path.join(workout, '{0}.txt'.format(os.path.basename(filename)[:-4])), 'w+')
                command = 'adb shell monkey -p {0} -s 13 --ignore-timeouts --ignore-crashes -v {1}'.format(package, count)
                subprocess.Popen(command, shell=True, stdout=output, stderr=output).wait()
                output.close()
                while True:
                    os.system('adb wait-for-device')
                    if not os.popen('adb shell ps | grep com.android.commands.monkey').readline().strip():
                        break
                    time.sleep(3)
                os.popen('adb uninstall {0}'.format(package)).readlines()
            else:
                print('{0} {1}'.format(os.path.basename(filename), lines[-1]))

        os.popen('adb uninstall com.ztemt.test.kit').readlines()
    else:
        print('Please connect your device')

workdir = os.path.dirname(os.path.realpath(sys.argv[0]))
workout = os.path.join(workdir, 'out')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
