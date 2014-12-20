# -*- coding:UTF-8 -*-

import codecs
import os
import sys
import time

from xml.etree.ElementTree import ElementTree, Element, SubElement

class Executor(object):

    def __init__(self, adb, workout):
        self.adb = adb
        self.workout = workout

    def execute(self):
        workdir = os.path.dirname(os.path.realpath(sys.argv[0]))
        workdir = os.path.join(workdir, 'stress')
        tags = self.adb.getprop('ro.build.tags')
        self.adb.uninstall('com.ztemt.test.stress')
        self.adb.install(os.path.join(workdir, 'SettingsTest_{0}.apk'.format(tags)))
        self.adb.install(os.path.join(workdir, 'StressTest_{0}.apk'.format(tags)))
        config = open(os.path.join(workdir, 'config.xml'), 'r')
        tree = ElementTree(file=config)
        params = []
        for item in tree.findall('item'):
            for param in item.findall('param'):
                params.append('{0} {1}'.format(param.attrib['extra'], param.text))
        extras = ' '.join(params)
        stress = os.path.join(self.workout, 'stress.csv')
        if os.path.exists(stress):
            os.remove(stress)
        self.adb.shellreadlines('am start --user 0 -n com.ztemt.test.stress/.AutoTestActivity --es mode auto {0}'.format(extras))
        while True:
            self.adb.waitforboot()
            self.adb.pull('/data/data/com.ztemt.test.stress/files/stress.csv', stress)
            if os.path.exists(stress):
                break
            time.sleep(15)
        lines = open(stress, 'r').readlines()
        report = open(stress, 'wb')
        report.write(codecs.BOM_UTF8)
        report.writelines(lines)
        report.close()
