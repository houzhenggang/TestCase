# -*- coding:UTF-8 -*-

import codecs
import csv
import glob
import os
import re
import shutil
import subprocess
import sys
import threading

import monkey

class Executor(object):

    def __init__(self, adb, workout):
        self.adb = adb
        self.workout = workout

    def setup(self):
        print('Imported user data type choices are:')
        print('    1. 	general condition')
        print('    2.  stress condition')
        print('    3.  none')
        try:
            self.option = input('\nWhich would you like? [1] ')
        except SyntaxError:
            self.option = 1
        except NameError:
            sys.exit(2)
        print('')

    def scene(self, name, package, clsname):
        outdir = os.path.join(self.workout, name)
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        t1 = monkey.DumpsysGfxinfoThread(self.adb, outdir, package, 1)
        t2 = monkey.LogcatSkpinfoThread(self.adb, outdir)
        t1.start()
        t2.start()
        self.adb.shellopen('uiautomator runtest scenes.jar -c {0}'.format(clsname)).wait()
        t1.stop()
        t2.stop()
        t1.join()
        t2.join()

    def getpartstat(self, name):
        m = re.search('[ ]+(\d+\.\d+)(\S+)[ ]+(\d+\.\d+)(\S+)[ ]+(\d+\.\d+)(\S+)[ ]+\d+', self.adb.shellreadlines('df {0}'.format(name))[-1])
        if m:
            z = lambda x, y: x * pow(1024, 'BKMGT'.find(y))
            g = m.groups()
            return z(float(g[0]), g[1]), z(float(g[2]), g[3]), z(float(g[4]), g[5])
        else:
            return 0, 0, 0

    def importdata(self, p1, p2, p3, p4):
        pimdir = '/sdcard/nubia/PIM'
        mediadir = '/sdcard/Media'

        self.adb.shell('rm -rf {0}'.format(pimdir))
        self.adb.shell('rm -rf {0}'.format(mediadir))

        self.adb.shell('mkdir -p {0}'.format(pimdir))
        if self.option == 1:
            self.adb.push(unicode(p1.strip(), 'utf-8').encode('gb2312'), pimdir)
        elif self.option == 2:
            self.adb.push(unicode(p2.strip(), 'utf-8').encode('gb2312'), pimdir)

        # restore the backup
        self.adb.shell('am force-stop cn.nubia.databackup')
        self.adb.shellreadlines('uiautomator runtest automator.jar -c cn.nubia.databackup.RestoreTestCase#testRestore')

        self.adb.shell('rm -rf {0}'.format(pimdir))
        self.adb.shell('rm -rf {0}'.format(mediadir))

        self.adb.shell('mkdir -p {0}'.format(mediadir))
        if self.option == 1:
            self.adb.push(unicode(p3.strip(), 'utf-8').encode('gb2312'), mediadir)
        elif self.option == 2:
            self.adb.push(unicode(p4.strip(), 'utf-8').encode('gb2312'), mediadir)

        self.adb.reboot(30)
        self.adb.shellreadlines('am startservice --user 0 -W -a com.ztemt.test.action.TEST_KIT --es command disableKeyguard')

    def execute(self):
        self.workout = os.path.join(self.workout, 'scenes')
        shutil.rmtree(self.workout, ignore_errors=True)
        if not os.path.exists(self.workout):
            os.mkdir(self.workout)

        workdir = os.path.dirname(os.path.realpath(sys.argv[0]))
        workdir = os.path.join(workdir, 'scenes')

        self.adb.install(os.path.join(workdir, 'ApiDemos.apk'))
        self.adb.push(os.path.join(workdir, 'scenes.jar'), '/data/local/tmp')

        model = self.adb.getprop('ro.product.model')
        if model == 'L50w':
            self.adb.shellreadlines('uiautomator runtest automator.jar -c com.android.settings.DevelopmentSettingsTestCase#testTrackFrameTimeDumpsysGfxinfo')
            self.scene('NativeListViewTest', 'com.example.android.apis', 'cn.sony.test.NativeListViewTest')
            self.scene('ContactTest', 'com.sonyericsson.android.socialphonebook', 'cn.sony.test.ContactTest')
            self.scene('DeveloperTest', 'com.android.settings', 'cn.sony.test.DeveloperTest')
            self.scene('MultiTaskTest', 'com.android.systemui', 'cn.sony.test.MultiTaskTest')
            self.scene('BrowserTest', 'com.android.browser', 'cn.sony.test.BrowserTest')
            self.scene('LauncherTest', 'com.sonyericsson.home', 'cn.sony.test.LauncherTest')
        elif model == 'SM-G9008V':
            self.adb.shellreadlines('uiautomator runtest automator.jar -c com.android.settings.DevelopmentSettingsTestCase#testTrackFrameTimeDumpsysGfxinfo')
            self.scene('NativeListViewTest', 'com.example.android.apis', 'cn.sung.test.NativeListViewTest')
            self.scene('ContactTest', 'com.android.contacts', 'cn.sung.test.ContactTest')
            self.scene('DeveloperTest', '', 'cn.sung.test.DeveloperTest')
            self.scene('MultiTaskTest', '', 'cn.sung.test.MultiTaskTest')
            self.scene('BrowserTest', 'com.sec.android.app.sbrowser', 'cn.sung.test.BrowserTest')
            self.scene('NoteScaleTest', 'com.android.mms', 'cn.sung.test.NoteScaleTest')
            self.scene('LauncherTest', '', 'cn.sung.test.LauncherTest')
        else:
            if self.option != 3:
                configs = open(os.path.join(workdir, 'config.txt'), 'r').readlines()
                if self.getpartstat('data')[0] > 2.5 * pow(1024, 3):
                    self.importdata(configs[1], configs[5], configs[3], configs[7])
                else:
                    self.importdata(configs[9], configs[13], configs[11], configs[15])

            self.adb.shellreadlines('uiautomator runtest automator.jar -c com.android.settings.DevelopmentSettingsTestCase#testTrackFrameTimeDumpsysGfxinfo')
            self.scene('NativeListViewTest', 'com.example.android.apis', 'cn.nubia.test.NativeListViewTest')
            self.scene('ContactTest', 'com.android.contacts', 'cn.nubia.test.ContactTest')
            self.scene('DeveloperTest', 'com.android.settings', 'cn.nubia.test.DeveloperTest')
            self.scene('GalleryTest', 'com.android.gallery3d', 'cn.nubia.test.GalleryTest')
            self.scene('MultiTaskTest', 'com.android.systemui', 'cn.nubia.test.MultiTaskTest')
            self.scene('BrowserTest', 'com.android.browser', 'cn.nubia.test.BrowserTest')
            self.scene('NoteScaleTest', 'com.android.contacts', 'cn.nubia.test.NoteScaleTest')
            self.scene('LauncherTest', 'cn.nubia.launcher', 'cn.nubia.test.LauncherTest')
            self.scene('PressMenuTest', 'cn.nubia.launcher', 'cn.nubia.test.PressMenuTest')
