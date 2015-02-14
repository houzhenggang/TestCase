# -*- coding: utf-8 -*-

import os
import re
import sys
import subprocess

workdir = os.path.dirname(os.path.realpath(sys.argv[0]))

class Apk(object):

    def __init__(self, apkfile):
        self.package = ''
        self.version = ''
        self.label = ''
        self.launcher = ''

        p = subprocess.Popen('\"{0}\" d badging \"{1}\"'.format(os.path.join(workdir, 'aapt'), apkfile), stdout=subprocess.PIPE)
        for line in p.stdout.readlines():
            if line.startswith('package:'):
                m = re.search('name=\'(.*)\' versionCode=\'.*\' versionName=\'(.*)\'', line)
                if m:
                    g = m.groups()
                    self.package = g[0]
                    self.version = g[1]
            elif line.startswith('application-label:'):
                m = re.search('application-label:\'(.*)\'', line)
                if m:
                    self.label = m.groups()[0]
            elif line.startswith('application-label-zh_CN:'):
                m = re.search('application-label-zh_CN:\'(.*)\'', line)
                if m:
                    self.label = m.groups()[0]
            elif line.startswith('launchable-activity:'):
                m = re.search('name=\'(.*)\' +label=\'(.*)\'', line)
                if m:
                    self.launcher = m.groups()[0]

def getconfig(linenum):
    with open(os.path.join(workdir, 'config.txt'), 'r') as f:
        return unicode(f.readlines()[linenum].strip(), 'utf-8')

def loginaccounts(adb):
    adb.kit.runtest('cn.nubia.accounts.NubiaAccountTestCase', 'testLogin')
    adb.kit.runtest('com.tencent.mobileqq.MobileQQTestCase', 'testLogin')
    adb.kit.runtest('com.tencent.mm.WeixinTestCase', 'testLogin')
    adb.kit.runtest('com.sina.weibo.WeiboTestCase', 'testLogin')
    adb.kit.runtest('com.baidu.tieba.TiebaTestCase', 'testLogin')
    adb.kit.runtest('com.jingdong.app.mall.JDMallTestCase', 'testLogin')
    adb.kit.runtest('com.chaozh.iReader.ReaderTestCase', 'testLogin')
    adb.kit.runtest('com.Qunar.QunarTestCase', 'testLogin')
    adb.kit.runtest('com.qihoo.appstore.AppStoreTestCase', 'testLogin')

def importdata(adb, datatype):
    data = []
    seldir = os.path.join(getconfig(1).encode('gb2312'), datatype.encode('gb2312'))
    for name in os.listdir(seldir):
        size = 0L
        path = os.path.join(seldir, name)
        pimdir = mediadir = None
        for dirpath, dirnames, names in os.walk(path):
            dirname = os.path.basename(dirpath)
            if dirname == 'PIM':
                pimdir = dirpath
            elif dirname == 'Media':
                mediadir = dirpath
            size += sum([os.path.getsize(os.path.join(dirpath, name)) for name in names])
        if pimdir or mediadir:
            data.append((size, pimdir, mediadir))

    if data:
        m = re.search('[ ]+(\d+\.\d+)(\S+)[ ]+(\d+\.\d+)(\S+)[ ]+(\d+\.\d+)(\S+)[ ]+\d+', adb.shellreadlines('df data')[-1])
        if m:
            z = lambda x, y: x * pow(1024, 'BKMGT'.find(y))
            g = m.groups()
            s = z(float(g[0]), g[1])
        else:
            s = 0
        if s > 2.5 * pow(1024, 3):
            data = [x for x in data if x[0] == max([i[0] for i in data])]
        else:
            data = [x for x in data if x[0] == min([i[0] for i in data])]

        pimdir = '/sdcard/nubia/PIM'
        mediadir = '/sdcard/Media'

        adb.shell('rm -rf {0}'.format(pimdir))
        adb.shell('rm -rf {0}'.format(mediadir))

        if data[0][1]:
            adb.shell('mkdir -p {0}'.format(pimdir))
            adb.push(data[0][1], pimdir)

        adb.shell('am force-stop cn.nubia.databackup')
        adb.kit.restoredata()

        adb.shell('rm -rf {0}'.format(pimdir))
        adb.shell('rm -rf {0}'.format(mediadir))

        if data[0][2]:
            adb.shell('mkdir -p {0}'.format(mediadir))
            adb.push(data[0][2], mediadir)

if __name__ == '__main__':
    apk = Apk(os.path.join(workdir, 'TestKit.apk'))
    print(apk.package)
    print(apk.version)
    print(apk.label)
    print(apk.launcher)
