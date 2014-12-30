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
        pass

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

    def execute(self):
        self.workout = os.path.join(self.workout, 'scenes')
        shutil.rmtree(self.workout, ignore_errors=True)
        if not os.path.exists(self.workout):
            os.mkdir(self.workout)

        workdir = os.path.dirname(os.path.realpath(sys.argv[0]))
        workdir = os.path.join(workdir, 'scenes')

        self.adb.reboot(30)
        self.adb.kit.disablekeyguard()
        self.adb.uia.runtest('com.android.settings.DevelopmentSettingsTestCase', 'testTrackFrameTimeDumpsysGfxinfo')

        self.adb.install(os.path.join(workdir, 'ApiDemos.apk'))
        self.adb.push(os.path.join(workdir, 'scenes.jar'), '/data/local/tmp')
        model = self.adb.getprop('ro.product.model')

        if model == 'L50w':
            self.scene('NativeListViewTest', 'com.example.android.apis', 'cn.sony.test.NativeListViewTest')
            self.scene('ContactTest', 'com.sonyericsson.android.socialphonebook', 'cn.sony.test.ContactTest')
            self.scene('DeveloperTest', 'com.android.settings', 'cn.sony.test.DeveloperTest')
            self.scene('MultiTaskTest', 'com.android.systemui', 'cn.sony.test.MultiTaskTest')
            self.scene('BrowserTest', 'com.android.browser', 'cn.sony.test.BrowserTest')
            self.scene('LauncherTest', 'com.sonyericsson.home', 'cn.sony.test.LauncherTest')
        elif model == 'SM-G9008V':
            self.scene('NativeListViewTest', 'com.example.android.apis', 'cn.sung.test.NativeListViewTest')
            self.scene('ContactTest', 'com.android.contacts', 'cn.sung.test.ContactTest')
            self.scene('DeveloperTest', '', 'cn.sung.test.DeveloperTest')
            self.scene('MultiTaskTest', '', 'cn.sung.test.MultiTaskTest')
            self.scene('BrowserTest', 'com.sec.android.app.sbrowser', 'cn.sung.test.BrowserTest')
            self.scene('NoteScaleTest', 'com.android.mms', 'cn.sung.test.NoteScaleTest')
            self.scene('LauncherTest', '', 'cn.sung.test.LauncherTest')
        else:
            self.scene('NativeListViewTest', 'com.example.android.apis', 'cn.nubia.test.NativeListViewTest')
            self.scene('ContactTest', 'com.android.contacts', 'cn.nubia.test.ContactTest')
            self.scene('DeveloperTest', 'com.android.settings', 'cn.nubia.test.DeveloperTest')
            self.scene('GalleryTest', 'com.android.gallery3d', 'cn.nubia.test.GalleryTest')
            self.scene('MultiTaskTest', 'com.android.systemui', 'cn.nubia.test.MultiTaskTest')
            self.scene('BrowserTest', 'com.android.browser', 'cn.nubia.test.BrowserTest')
            self.scene('NoteScaleTest', 'com.android.contacts', 'cn.nubia.test.NoteScaleTest')
            self.scene('LauncherTest', 'cn.nubia.launcher', 'cn.nubia.test.LauncherTest')
            self.scene('PressMenuTest', 'cn.nubia.launcher', 'cn.nubia.test.PressMenuTest')
