# -*- coding:UTF-8 -*-

import os
import re
import subprocess
import time

sno = None

def devices():
    results = []
    p = subprocess.Popen('adb devices -l', shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        m = re.search('(\S+)\s+device product:(\S+) model:(\S+) device:(\S+)', line)
        if m:
            g = m.groups()
            results.append((g[0], {'product': g[1], 'model': g[2], 'device': g[3]}))
    return tuple(results)

def adbopen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT):
    prefix = 'adb -s {0}'.format(sno) if sno else 'adb'
    return subprocess.Popen('{0} {1}'.format(prefix, cmd), shell=shell, stdout=stdout, stderr=stderr)

def shellopen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT):
    return adbopen('shell {0}'.format(cmd), shell=shell, stdout=stdout, stderr=stderr)

def adb(cmd, shell=False):
    return adbopen(cmd, shell=shell).stdout.readlines()

def shell(cmd, shell=False):
    return shellopen(cmd, shell=shell).stdout.readlines()

def push(local, remote):
    adb('push \"{0}\" {1}'.format(local, remote))

def pull(remote, local):
    adb('pull {0} \"{1}\"'.format(remote, local))

def install(local, reinstall=True, downgrade=False, sdcard=False):
    push(local, '/data/local/tmp/tmp.apk')
    lines = shell('pm install {0} {1} {2} /data/local/tmp/tmp.apk'.format('-r' if reinstall else '', '-d' if downgrade else '', '-s' if sdcard else ''))
    shell('rm -f /data/local/tmp/tmp.apk')
    return lines

def uninstall(package):
    return adb('uninstall {0}'.format(package))

def getprop(key):
    return shell('getprop {0}'.format(key))[0].strip()

def setprop(key, value):
    shell('setprop {0} {1}'.format(key, value))

def wait(interval=3):
    adb('wait-for-device')
    while getprop('sys.boot_completed') != '1':
        time.sleep(interval)

def reboot():
    adb('reboot')
    wait(0.1)

def screenshot(local):
    shell('screencap -p /data/local/tmp/screenshot.png')
    pull('/data/local/tmp/screenshot.png', local)

def kill(proc):
    for pid in [x.split()[1] for x in shell('ps') if x.split()[-1] == proc]:
        shell('kill {0}'.format(pid))

if __name__ == '__main__':
    print(devices())
