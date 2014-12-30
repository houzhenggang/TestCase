# -*- coding:UTF-8 -*-

import os
import sys
import time

class Executor(object):

    def __init__(self, adb, workout):
        self.adb = adb
        self.workout = workout
        self.buildfile = None

    def setup(self):
        workdir = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])))
        workdir = os.path.join(workdir, 'update')

        configs = open(os.path.join(workdir, 'config.txt'), 'r')
        rootdir = configs.readlines()[1].strip()
        configs.close()

        sections = os.listdir(rootdir)
        print('Department section choices are:')
        for i in range(len(sections)):
            print('    {0:>2}. {1}'.format(i + 1, sections[i]))
        try:
            select = input('\nWhich would you like? ') - 1
            select = divmod(select, len(sections))[1]
        except SyntaxError:
            sys.exit(2)
        except NameError:
            sys.exit(2)
        print('')

        builddir = os.path.join(rootdir, sections[select])
        builddir = os.path.join(builddir, self.adb.getprop('ro.product.model'))

        if os.path.exists(builddir):
            filelist = os.listdir(builddir)

            if len(filelist) > 0:
                self.buildfile = max(filelist, key=os.path.basename)
                self.buildfile = os.path.join(builddir, self.buildfile)

    def execute(self):
        if self.buildfile:
            self.adb.push(self.buildfile, '/sdcard/update.zip')
            self.adb.kit.disablekeyguard()
            self.adb.uia.runtest('cn.nubia.systemupdate.SystemUpdateTestCase', 'testLocalUpdate')
            time.sleep(30)
            self.adb.waitforboot()
