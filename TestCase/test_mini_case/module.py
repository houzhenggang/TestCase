# -*- coding: utf-8 -*-

import os
import shutil
import time
import zipfile

from xml.etree.ElementTree import ElementTree
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from common import workdir, getconfig

def parse(filename):
    info = dict()
    with zipfile.ZipFile(unicode(filename, 'utf-8')) as zf:
        for name in zf.namelist():
            if os.path.basename(name) == 'module.xml':
                et = ElementTree(file=zf.open(name))
                info['name'] = et.find('name').text
                info['version'] = et.find('version').text
                info['desc'] = et.find('description').text
                break
    return info

class Executor(object):

    def __init__(self, adb, workout, testname, filename, params):
        self.adb = adb
        self.workout = workout
        self.testname = testname
        self.filename = filename
        self.params = params

    def title(self):
        return self.testname

    def setup(self):
        pass

    def execute(self, log):
        workout = os.path.join(self.workout, 'extras')
        if not os.path.exists(workout):
            os.mkdir(workout)
        suffix = unicode(self.filename, 'utf-8')[len(getconfig(5)) + 1:]
        workout = os.path.join(workout, os.path.splitext(suffix)[0])
        shutil.rmtree(workout, ignore_errors=True)
        if not os.path.exists(workout):
            os.makedirs(workout)

        log(self.msg(u'正在解压缩测试用例'))
        zf = zipfile.ZipFile(unicode(self.filename, 'utf-8'))
        for name in zf.namelist():
            if os.path.basename(name) == 'module.xml':
                prefixdir = os.path.dirname(name)
                break
        for name in zf.namelist():
            if os.path.dirname(name).startswith(prefixdir):
                file = os.path.join(workout, name[len(prefixdir) + 1:])
                dirname = os.path.dirname(file)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
                try:
                    f = open(file, 'wb')
                    f.write(zf.read(name))
                    f.close()
                except IOError as e:
                    pass
        zf.close()

        log(self.msg(u'正在复制测试脚本'))
        tmppath = '/data/local/tmp/module'
        self.adb.shell('rm -rf {0}'.format(tmppath))
        self.adb.shell('mkdir -p {0}'.format(tmppath))
        self.adb.push(os.path.join(workdir, 'busybox'), tmppath)
        self.adb.shell('chmod 755 {0}/busybox'.format(tmppath))
        self.adb.push(os.path.join(workdir, 'main.sh'), tmppath)
        self.adb.push(workout.encode('gb2312'), tmppath)
        self.adb.shell('chmod 755 {0}/*.sh'.format(tmppath))

        shutil.rmtree(workout, ignore_errors=True)
        if not os.path.exists(workout):
            os.mkdir(workout)

        log(self.msg(u'正在执行测试脚本'))
        self.adb.shellreadlines('sh {0}/main.sh start {0} {0}/out {1}'.format(tmppath, self.params))
        while self.adb.shellreadline('sh {0}/main.sh wait {0} {0}/out'.format(tmppath)) == '1':
            time.sleep(5)
        self.adb.shellreadlines('sh {0}/main.sh exit {0} {0}/out'.format(tmppath))

        log(self.msg(u'正在导出测试结果'))
        self.adb.pull('{0}/out'.format(tmppath), workout.encode('gb2312'))

    def msg(self, text):
        return u'[{0}] {1}'.format(self.title(), text)
