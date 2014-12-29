# -*- coding:UTF-8 -*-

import codecs
import csv
import os
import sys
import time

from xml.etree.ElementTree import ElementTree, Element, SubElement

import adbkit

class Executor(object):

    def __init__(self, adb, workout):
        self.adb = adb
        self.workout = workout
        self.workdir = os.path.dirname(os.path.realpath(sys.argv[0]))
        self.workdir = os.path.join(self.workdir, 'stress')

    def setup(self):
        config = open(os.path.join(self.workdir, 'config.xml'), 'r')
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
        self.uiauto = []
        for item in items:
            if item in selected:
                print('Parameters for {0}:'.format(item.attrib['name'].encode('gb2312')))
                if item.attrib['type'] == 'uia':
                    self.uiauto.append(item)
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
                    elif item.attrib['type'] == 'uia':
                        param.text = value
                print('')

    def execute(self):
        stress = os.path.join(self.workout, 'stress.csv')
        if os.path.exists(stress):
            os.remove(stress)

        if self.extras:
            tags = self.adb.getprop('ro.build.tags')
            self.adb.uninstall('com.ztemt.test.stress')
            self.adb.install(os.path.join(self.workdir, 'StressTest_{0}.apk'.format(tags)))
            lines = self.adb.startactivity('-n com.ztemt.test.stress/.AutoTestActivity --es mode auto {0}'.format(' '.join(self.extras)), 'stress.csv', 30)
            report = open(stress, 'wb')
            report.write(codecs.BOM_UTF8)
            report.writelines(lines)
            report.close()
            self.adb.uninstall('com.ztemt.test.stress')

        if self.uiauto:
            if os.path.exists(stress):
                report = open(stress, 'ab+')
                writer = csv.writer(report, quoting=csv.QUOTE_ALL)
            else:
                report = open(stress, 'wb')
                report.write(codecs.BOM_UTF8)
                writer = csv.writer(report, quoting=csv.QUOTE_ALL)
                writer.writerow(['测试项', '总次数', '测试次数', '成功次数', '失败次数'])
            for item in self.uiauto:
                es = []
                for param in item.findall('param'):
                    es.append('{0} {1}'.format(param.attrib['extra'], param.text))
                uia = adbkit.Uia(self.adb, os.path.join(self.workdir, item.find('jar').text))
                success = 0
                failure = 0
                total = 0
                for line in uia.runtest(item.find('class').text, item.find('method').text, es):
                    if line.startswith('RESULT='):
                        result = eval(line.split('=')[-1])
                        success = result['SUCCESS']
                        failure = result['FAILURE']
                        total = result['TOTAL']
                writer.writerow([item.attrib['name'].encode('utf-8'), total, success + failure, success, failure])
                report.flush()
                uia.destroy()
            report.close()
