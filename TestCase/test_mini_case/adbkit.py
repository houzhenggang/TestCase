# -*- coding:UTF-8 -*-

import os
import re
import subprocess
import sys
import threading
import time

import compat

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
        workdir = os.path.dirname(os.path.realpath(sys.argv[0]))
        self.uia = Uia(self, os.path.join(workdir, 'automator.jar'))
        self.kit = Kit(self, os.path.join(workdir, 'TestKit.apk'))

    def __adbopen(self, cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT):
        return subprocess.Popen('{0} {1}'.format(self.prefix, cmd), shell=shell, stdout=stdout, stderr=stderr)

    def __shellopen(self, cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT):
        return self.__adbopen('shell {0}'.format(cmd), shell=shell, stdout=stdout, stderr=stderr)

    def __adbreadline(self, cmd):
        return self.__adbopen(cmd).stdout.readline().strip()

    def __shellreadline(self, cmd):
        return self.__shellopen(cmd).stdout.readline().strip()

    def __adbreadlines(self, cmd):
        return self.__adbopen(cmd).stdout.readlines()

    def __shellreadlines(self, cmd):
        return self.__shellopen(cmd).stdout.readlines()

    def __adb(self, cmd):
        self.__adbopen(cmd).wait()

    def __shell(self, cmd):
        self.__shellopen(cmd).wait()

    def adbopen(self, cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT):
        self.waitforboot()
        return self.__adbopen(cmd, shell, stdout, stderr)

    def shellopen(self, cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT):
        self.waitforboot()
        return self.__shellopen(cmd, shell, stdout, stderr)

    def adbreadline(self, cmd):
        self.waitforboot()
        return self.__adbreadline(cmd)

    def shellreadline(self, cmd):
        self.waitforboot()
        return self.__shellreadline(cmd)

    def adbreadlines(self, cmd):
        self.waitforboot()
        return self.__adbreadlines(cmd)

    def shellreadlines(self, cmd):
        self.waitforboot()
        return self.__shellreadlines(cmd)

    def adb(self, cmd):
        self.waitforboot()
        self.__adb(cmd)

    def shell(self, cmd):
        self.waitforboot()
        self.__shell(cmd)

    def push(self, local, remote):
        self.adbreadline('push \"{0}\" {1}'.format(local, remote))

    def pull(self, remote, local):
        self.adbreadline('pull {0} \"{1}\"'.format(remote, local))

    def install(self, local):
        return self.adbreadlines('install -r \"{0}\"'.format(local))

    def uninstall(self, package):
        return self.adbreadlines('uninstall {0}'.format(package))

    def __getprop(self, key):
        return self.__shellreadline('getprop {0}'.format(key))

    def getprop(self, key):
        self.waitforboot()
        return self.__getprop(key)

    def setprop(self, key, value):
        self.shellreadline('setprop {0} \"{1}\"'.format(key, value))

    def waitforboot(self, interval=30):
        while True:
            self.__adb('wait-for-device')
            if self.__getprop('sys.boot_completed') == '1':
                break
            time.sleep(interval)

    def reboot(self, interval=0.1):
        self.adb('reboot')
        self.waitforboot(interval)

    def __start(self, cmdstr, filename=None, interval=0.5):
        if filename:
            catfile = 'cat /data/data/com.ztemt.test.kit/files/{0}'.format(filename)
            pattern = re.compile('^(\d+)$')
            m = pattern.match(self.shellreadline(catfile))
            if m:
                tm1 = long(m.groups()[0])
            else:
                tm1 = 0
        p = self.shellopen('am {0}'.format(cmdstr))
        y = lambda x: x.terminate()
        t = threading.Timer(5, y, args=(p,))
        t.start()
        lines = p.stdout.readlines()
        t.cancel()
        while filename:
            lines = self.shellreadlines(catfile)
            m = pattern.match(lines[0].strip())
            if m:
                tm2 = long(m.groups()[0])
            else:
                tm2 = 0
            if not tm1 == tm2:
                lines = lines[1:]
                break
            time.sleep(interval)
        return [line.strip() for line in lines]

    def startactivity(self, intent, filename=None, interval=0.5):
        return self.__start('start --user 0 -W {0}'.format(intent), filename=filename, interval=interval)

    def startservice(self, intent, filename=None, interval=0.5):
        return self.__start('startservice --user 0 -W {0}'.format(intent), filename=filename, interval=interval)

    def pidof(self, name):
        return [x.split()[1] for x in self.shellreadlines('ps') if x.split()[-1] == name]

    def kill(self, proc):
        for pid in self.pidof(proc):
            self.shell('kill {0}'.format(pid))

    def ismonkey(self):
        return self.pidof('com.android.commands.monkey')

    def isuiautomator(self):
        return self.pidof('uiautomator')

class Uia(object):

    def __init__(self, adb, jar):
        self.adb = adb
        self.jar = jar
        self.install()

    def install(self):
        self.adb.push(self.jar, '/data/local/tmp')

    def runtest(self, clsname, method=None, extras=None):
        if not os.path.basename(self.jar) in [line.split()[-1] for line in self.adb.shellreadlines('ls -F /data/local/tmp')]:
            self.install()
        return self.adb.shellreadlines('uiautomator runtest {0} -c {1}{2} {3}'.format(os.path.basename(self.jar), clsname,
                '#' + method if method else '', ' '.join(extras) if extras else ''))

    def uninstall(self):
        self.adb.shell('rm -f /data/local/tmp/{0}'.format(os.path.basename(self.jar)))

class Kit(object):

    def __init__(self, adb, apk):
        self.adb = adb
        self.apk = apk
        self.install()

    def install(self):
        self.adb.install(self.apk)

    def __service(self, cmdname, filename=None, interval=0.5):
        return self.adb.startservice('-a com.ztemt.test.action.TEST_KIT --es command {0}'.format(cmdname), filename=filename, interval=interval)

    def disablekeyguard(self):
        self.__service('disableKeyguard')

    def packages(self):
        return eval(self.__service('getPackageList', 'packages')[0])

    def uninstall(self):
        self.adb.uninstall(compat.Apk(self.apk).package)

if __name__ == '__main__':
    print(devices())
