# -*- coding:UTF-8 -*-

import codecs
import csv
import os
import sys
import threading
import time

from xml.etree.ElementTree import ElementTree, Element, SubElement
from Tkinter import *

import adbkit

class StressMonitorThread(threading.Thread):

    def __init__(self, adb):
        threading.Thread.__init__(self)
        self.adb = adb
        self.loop = True

    def run(self):
        while self.loop:
            i = 0
            while self.loop and i < 30:
                time.sleep(1)
                i += 1
            if not [x for x in self.adb.shellreadlines('ps') if x.split()[-1] == 'com.ztemt.test.stress']:
                self.adb.startactivity('-n com.ztemt.test.stress/.AutoTestActivity')

    def stop(self):
        self.loop = False

class Executor(object):

    def __init__(self, adb, workout):
        self.adb = adb
        self.workout = workout
        self.workdir = os.path.dirname(os.path.realpath(sys.argv[0]))

    def setup(self):
        config = open(os.path.join(self.workdir, 'stress', 'config.xml'), 'r')
        tree = ElementTree(file=config)
        items = tree.findall('item')

        def callcheck(event):
            getattr(event.widget, 'item').attrib['selected'] = getattr(event.widget, 'var').get()

        def callinput(event):
            var = getattr(event.widget, 'var')
            param = getattr(event.widget, 'param')
            if param.attrib['type'] == 'int' and not var.get().isdigit():
                var.set(param.text)
            else:
                param.text = var.get()

        root = Tk()
        root.title('压力测试')
        left = Frame(root)
        left.grid(row=0, column=0, sticky=NW)
        right = Frame(root)
        right.grid(row=0, column=1, sticky=NW)
        button = Button(root, text='确定', command=root.destroy)
        button.grid(row=1, column=1, sticky=E)

        for i in range(len(items)):
            dm = divmod(i, 2)
            side = left if dm[1] == 0 else right
            c = IntVar()
            cb = Checkbutton(side, variable=c, text=items[i].attrib['name'])
            cb.grid(row=dm[0], column=0, sticky=NW)
            cb.bind('<Leave>', callcheck)
            setattr(cb, 'var', c)
            setattr(cb, 'item', items[i])
            panel = Frame(side)
            params = items[i].findall('param')
            for j in range(len(params)):
                Label(panel, text=params[j].attrib['name']).grid(row=j, column=0, sticky=W)
                v = StringVar()
                v.set(params[j].text)
                en = Entry(panel, textvariable=v)
                en.grid(row=j, column=1, sticky=W)
                en.bind('<KeyRelease>', callinput)
                setattr(en, 'var', v)
                setattr(en, 'param', params[j])
            panel.grid(row=dm[0], column=1, sticky=NW)
            Label(side, text=items[i].find('desc').text).grid(row=dm[0], column=2, sticky=NW)
        root.mainloop()

        self.extras = []
        self.pyfunc = []
        for item in [item for item in items if 'selected' in item.keys() and item.attrib['selected']]:
            if item.attrib['type'] == 'pyf':
                self.pyfunc.append(item)
            elif item.attrib['type'] == 'apk':
                for param in item.findall('param'):
                    self.extras.append('{0} {1}'.format(param.attrib['extra'], param.text))

    def execute(self):
        stress = os.path.join(self.workout, 'stress.csv')
        if os.path.exists(stress):
            os.remove(stress)

        if self.extras:
            tags = self.adb.getprop('ro.build.tags')
            self.adb.install(os.path.join(self.workdir, 'stress', 'StressTest_{0}.apk'.format(tags)))
            t = StressMonitorThread(self.adb)
            t.start()
            lines = self.adb.startactivity('-n com.ztemt.test.stress/.AutoTestActivity --es mode auto {0}'.format(' '.join(self.extras)), 'stress.csv', 30)
            t.stop()
            t.join()
            report = open(stress, 'wb')
            report.write(codecs.BOM_UTF8)
            report.write('{0}{1}'.format(os.linesep.join(lines), os.linesep))
            report.close()
            self.adb.uninstall('com.ztemt.test.stress')

        if self.pyfunc:
            if os.path.exists(stress):
                report = open(stress, 'ab+')
                writer = csv.writer(report, quoting=csv.QUOTE_ALL)
            else:
                report = open(stress, 'wb')
                report.write(codecs.BOM_UTF8)
                writer = csv.writer(report, quoting=csv.QUOTE_ALL)
                writer.writerow(['测试项', '总次数', '测试次数', '成功次数', '失败次数'])
            for item in self.pyfunc:
                es = []
                for param in item.findall('param'):
                    es.append((param.attrib['extra'], param.text))
                result = getattr(self, item.find('func').text)(**dict(es))
                writer.writerow([item.attrib['name'].encode('utf-8'), result[0], result[1] + result[2], result[1], result[2]])
                report.flush()
            report.close()

    def usbwakeup(self, **args):
        loop = int(args['loop'])
        success = failure = 0
        uia = adbkit.Uia(self.adb, os.path.join(self.workdir, 'stress', 'WakeUpStressTest.jar'))
        for line in uia.runtest('cn.nubia.WakeUpTest', extras=['-e Cycle {0}'.format(loop)]):
            if line.startswith('RESULT='):
                result = eval(line.split('=')[-1])
                success = result['SUCCESS']
                failure = result['FAILURE']
        uia.uninstall()
        self.adb.kit.wakeup()
        return loop, success, failure

    def masterclear(self, **args):
        loop = int(args['loop'])
        success = failure = 0
        if self.adb.getprop('ro.build.type') == 'user':
            failure = loop
        else:
            for i in range(loop):
                self.adb.kit.masterclear()
                time.sleep(30)
                self.adb.waitforboot()
                success += 1
                self.adb.kit.setupwizard()
            self.adb.kit.keepscreenon()
        return loop, success, failure
