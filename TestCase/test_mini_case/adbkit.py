# -*- coding:UTF-8 -*-

import os
import re
import subprocess
import time

def devices():
    results = []
    p = subprocess.Popen('adb devices', shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        m = re.search('^(\S+)\s+device', line)
        if m:
            results.append(m.groups()[0])
    return tuple(results)

class Adb(object):

    def __init__(self, serialno):
        self.prefix = 'adb -s {0}'.format(serialno) if serialno else 'adb'

    def adbopen(self, cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT):
        return subprocess.Popen('{0} {1}'.format(self.prefix, cmd), shell=shell, stdout=stdout, stderr=stderr)

    def shellopen(self, cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT):
        return self.adbopen('shell {0}'.format(cmd), shell=shell, stdout=stdout, stderr=stderr)

    def adbreadline(self, cmd):
        return os.popen('{0} {1}'.format(self.prefix, cmd)).readline().strip()

    def shellreadline(self, cmd):
        return self.adbreadline('shell {0}'.format(cmd))

    def adbreadlines(self, cmd):
        return os.popen('{0} {1}'.format(self.prefix, cmd)).readlines()

    def shellreadlines(self, cmd):
        return self.adbreadlines('shell {0}'.format(cmd))

    def adb(self, cmd):
        os.system('{0} {1}'.format(self.prefix, cmd))

    def shell(self, cmd):
        self.adb('shell {0}'.format(cmd))

    def push(self, local, remote):
        self.adbreadline('push \"{0}\" {1}'.format(local, remote))

    def pull(self, remote, local):
        self.adbreadline('pull {0} \"{1}\"'.format(remote, local))

    def install(self, local, reinstall=True, downgrade=False, sdcard=False):
        tmpapk = '/data/local/tmp/tmp.apk'
        if local:
            self.push(local, tmpapk)
        z = lambda y, z: z if y else ''
        return self.shellreadlines('pm install {0} {1} {2} {3}'.format(z(reinstall, '-r'), z(downgrade, '-d'), z(sdcard, '-s'), tmpapk))

    def uninstall(self, package):
        return self.shellreadline('pm uninstall {0}'.format(package))

    def getprop(self, key):
        return self.shellreadline('getprop {0}'.format(key))

    def setprop(self, key, value):
        self.shellreadline('setprop {0} \"{1}\"'.format(key, value))

    def waitfordevice(self):
        self.adb('wait-for-device')

    def waitforboot(self, interval=3):
        self.waitfordevice()
        while not self.bootcompleted():
            time.sleep(interval)

    def bootcompleted(self):
        return self.getprop('sys.boot_completed') == '1'

    def reboot(self):
        self.adb('reboot')
        self.waitforboot(0.1)

    def screenshot(self, local):
        screenshot = '/data/local/tmp/screenshot.png'
        self.shell('screencap -p {0}'.format(screenshot))
        self.pull(screenshot, local)

    def kill(self, proc):
        for pid in [x.split()[1] for x in self.shellreadlines('ps') if x.split()[-1] == proc]:
            self.shell('kill {0}'.format(pid))

if __name__ == '__main__':
    print(devices())
