# -*- coding: utf-8 -*-

import codecs
import csv
import os
import sys
import threading
import time

import adbkit

from xml.etree.ElementTree import ElementTree, Element, SubElement
from PyQt4.QtGui import *
from PyQt4.QtCore import *

from common import workdir

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

    def __init__(self, main):
        self.adb = main.adb
        self.workout = main.workout

    def title(self):
        return u'压力测试'

    def paramClicked(self, param, column):
        if column == 1 and not param.childCount():
            param.setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable)
        else:
            param.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)

    def paramChanged(self, param, column):
        if column == 0 and param.childCount():
            self.items[param.data(0, 1).toPyObject()].attrib['selected'] = param.checkState(column) == Qt.Checked
        elif column == 1 and not param.childCount():
            if param.parent():
                text = unicode(param.text(column))
                p = self.items[param.parent().data(0, 1).toPyObject()].findall('param')[param.data(0, 1).toPyObject()]
                if p.attrib['type'] == 'int':
                    if text.isdigit():
                        p.text = text
                    else:
                        param.setText(1, p.text)
                else:
                    p.text = text

    def setup(self):
        with open(os.path.join(workdir, 'stress', 'config.xml'), 'r') as f:
            self.items = ElementTree(file=f).findall('item')

        page = QWizardPage()
        page.setTitle(self.title())
        page.setSubTitle(u'压力测试说明')

        tree = QTreeWidget()
        tree.setColumnCount(2)
        tree.setHeaderLabels([u'测试项', u'描述'])
        tree.setColumnWidth(0, 180)
        tree.itemClicked.connect(self.paramClicked)
        tree.itemChanged.connect(self.paramChanged)

        for i in range(len(self.items)):
            item = QTreeWidgetItem(tree)
            item.setData(0, 1, QVariant(i))
            item.setCheckState(0, Qt.Unchecked)
            item.setText(0, self.items[i].attrib['name'])
            item.setText(1, self.items[i].find('desc').text)

            params = self.items[i].findall('param')
            for j in range(len(params)):
                param = QTreeWidgetItem(item)
                param.setData(0, 1, QVariant(j))
                param.setText(0, params[j].attrib['name'])
                param.setText(1, params[j].text)

            tree.addTopLevelItem(item)

        layout = QVBoxLayout()
        layout.addWidget(tree)
        page.setLayout(layout)

        return page

    def execute(self):
        stress = os.path.join(self.workout, 'stress.csv')
        if os.path.exists(stress):
            os.remove(stress)

        extras = []
        pyfunc = []
        for item in [item for item in self.items if 'selected' in item.keys() and item.attrib['selected']]:
            if item.attrib['type'] == 'pyf':
                pyfunc.append(item)
            elif item.attrib['type'] == 'apk':
                for param in item.findall('param'):
                    extras.append('{0} {1}'.format(param.attrib['extra'], param.text))

        if extras:
            tags = self.adb.getprop('ro.build.tags')
            self.adb.install(os.path.join(workdir, 'stress', 'StressTest_{0}.apk'.format(tags)))
            t = StressMonitorThread(self.adb)
            t.start()
            lines = self.adb.startactivity('-n com.ztemt.test.stress/.AutoTestActivity --es mode auto {0}'.format(' '.join(extras)), 'stress.csv', 30)
            t.stop()
            t.join()
            report = open(stress, 'wb')
            report.write(codecs.BOM_UTF8)
            report.write('{0}{1}'.format(os.linesep.join(lines), os.linesep))
            report.close()
            self.adb.uninstall('com.ztemt.test.stress')

        if pyfunc:
            if os.path.exists(stress):
                report = open(stress, 'ab+')
                writer = csv.writer(report, quoting=csv.QUOTE_ALL)
            else:
                report = open(stress, 'wb')
                report.write(codecs.BOM_UTF8)
                writer = csv.writer(report, quoting=csv.QUOTE_ALL)
                writer.writerow(['测试项', '总次数', '测试次数', '成功次数', '失败次数'])
            for item in pyfunc:
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
        uia = adbkit.Uia(self.adb, os.path.join(workdir, 'stress', 'WakeUpStressTest.jar'))
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
