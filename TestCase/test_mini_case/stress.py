# -*- coding:UTF-8 -*-

import codecs
import csv
import os
import sys
import threading
import time

from xml.etree.ElementTree import ElementTree, Element, SubElement

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

        selected = []
        print('Stress test choices are:')
        for i in range(len(items)):
            print('    {0:>2}. {1:<18} [{2}]'.format(i + 1, items[i].attrib['name'].encode('gb2312'), items[i].find('desc').text.encode('gb2312')))
        options = ','.join([str(x) for x in range(1, len(items) + 1)])
        selects = raw_input('\nWhich would you like? [{0}] '.format(options)).split(',')
        for select in selects:
            try:
                index = int(select.strip()) - 1
                index = divmod(index, len(items))[1]
                selected.append(items[index])
            except ValueError:
                continue
        selected = selected if selected else items
        print('')

        self.extras = []
        self.pyfunc = []
        for item in items:
            if item in selected:
                print('Parameters for {0}:'.format(item.attrib['name'].encode('gb2312')))
                if item.attrib['type'] == 'pyf':
                    self.pyfunc.append(item)
                for param in item.findall('param'):
                    if param.attrib['type'] == 'int':
                        value = int(param.text)
                        try:
                            value = input('{0}? [{1}] '.format(param.attrib['name'].encode('gb2312'), value))
                        except SyntaxError:
                            pass
                        except NameError:
                            pass
                    elif param.attrib['type'] == 'str':
                        value = raw_input('{0}? [{1}] '.format(param.attrib['name'].encode('gb2312'), param.text))
                        value = value if value else param.text
                    if item.attrib['type'] == 'apk':
                        self.extras.append('{0} {1}'.format(param.attrib['extra'], value))
                    elif item.attrib['type'] == 'pyf':
                        param.text = value
                print('')

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
        self.adb.uia.runtest('com.android.systemui.SleepWakeupTestCase', 'testWakeup')
        return loop, success, failure

    def masterclear(self, **args):
        loop = int(args['loop'])
        success = failure = 0
        for i in range(loop):
            self.adb.uia.runtest('com.android.settings.MasterClearTestCase', 'testMasterClear')
            time.sleep(30)
            self.adb.waitforboot()
            success += 1
            self.adb.uia.runtest('cn.nubia.setupwizard.SetupWizardTestCase', 'testSetupWizard')
        self.adb.uia.runtest('com.android.settings.DevelopmentSettingsTestCase', 'testKeepScreenOn')
        return loop, success, failure
