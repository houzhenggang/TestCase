# -*- coding: utf-8 -*-

import getopt
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import zipfile

import adbkit
import common
import compat
import memory
import monkey
import launch
import scenes
import stress
import update
import uptime
import screenshot
import chart.run as runner

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from common import workdir, getconfig, importdata

class QueryDeviceThread(QThread):

    queryDeviceFinish = pyqtSignal(tuple)

    def __init__(self):
        super(QueryDeviceThread, self).__init__(None)

    def run(self):
        devices = adbkit.devices()
        self.queryDeviceFinish.emit(devices)

class ConnectDeviceThread(QThread):

    connectDeviceFinish = pyqtSignal(adbkit.Adb)

    def __init__(self, serialno):
        super(ConnectDeviceThread, self).__init__(None)
        self.serialno = serialno

    def run(self):
        adb = adbkit.Adb(self.serialno)
        if adb.adbreadline('get-state') == 'device' and not adb.ismonkey() and not adb.isuiautomator():
            self.connectDeviceFinish.emit(adb)
        else:
            self.connectDeviceFinish.emit(None)

class QueryPackageThread(QThread):

    queryPackageFinish = pyqtSignal(dict)

    def __init__(self, adb):
        super(QueryPackageThread, self).__init__(None)
        self.adb = adb

    def run(self):
        packages = self.adb.kit.getpackages()
        testpkgs = [line[8:].strip() for line in self.adb.shellreadlines('pm list package -s')]
        packages = dict([x for x in packages.items() if x[0] in testpkgs])
        self.queryPackageFinish.emit(packages)

class SetupExecuteThread(QThread):

    statusChange = pyqtSignal(unicode)

    def __init__(self, adb, selected, executor, login, datatype):
        super(SetupExecuteThread, self).__init__(None)
        self.adb = adb
        self.selected = selected
        self.executor = executor
        self.login = login
        self.datatype = datatype

    def run(self):
        self.statusChange.emit(u'正在唤醒设备')
        self.adb.kit.wakeup()

        self.statusChange.emit(u'正在设置屏幕不锁定')
        self.adb.kit.disablekeyguard()
        self.adb.kit.keepscreenon()

        if self.login:
            self.statusChange.emit(u'正在登录应用帐号')
            common.loginaccounts(self.adb)

        if self.datatype:
            self.statusChange.emit(u'正在导入用户数据')
            common.importdata(self.adb, self.datatype)

        self.statusChange.emit(u'正在执行测试')
        start = time.time()
        for i in self.selected:
            self.executor[i].execute()
        end = time.time()

        self.statusChange.emit(u'正在生成报告')
        runner.run(workout)

        self.statusChange.emit(u'完成')
        self.adb.kit.destroy()

class SelectTestDialog(QDialog):

    tests = (
        (u'系统升级', False),
        (u'应用启动时间测试', True),
        (u'流畅性测试', True),
        (u'Monkey测试', True),
        (u'兼容性测试', True),
        (u'系统启动时间测试', True),
        (u'压力测试', True),
        (u'内存测试', False),
        (u'截图比较测试', False)
    )

    def __init__(self, selected, parent=None):
        super(SelectTestDialog, self).__init__(parent)
        self.selected = selected
        self.initUI()

    def initUI(self):
        self.list = QListWidget(self)
        for i in range(len(self.tests)):
            item = QListWidgetItem(self.tests[i][0])
            item.setCheckState(Qt.Checked if self.tests[i][1] else Qt.Unchecked)
            item.setData(1, QVariant(i + 1))
            self.list.addItem(item)
        self.list.setCurrentRow(0)

        self.okButton = QPushButton(u'确定')
        self.okButton.clicked.connect(self.buttonClicked)
        self.okButton.setDefault(True)
        self.upButton = QPushButton(u'上移')
        self.upButton.clicked.connect(self.buttonClicked)
        self.downButton = QPushButton(u'下移')
        self.downButton.clicked.connect(self.buttonClicked)
        buttonBox = QDialogButtonBox(Qt.Vertical)
        buttonBox.addButton(self.okButton, QDialogButtonBox.ActionRole)
        buttonBox.addButton(self.upButton, QDialogButtonBox.ActionRole)
        buttonBox.addButton(self.downButton, QDialogButtonBox.ActionRole)

        hbox = QHBoxLayout()
        hbox.addWidget(self.list)
        hbox.addWidget(buttonBox)

        self.setLayout(hbox)
        self.setWindowTitle(u'选择测试项')

    def buttonClicked(self):
        sender = self.sender()

        if sender == self.okButton:
            for i in range(self.list.count()):
                item = self.list.item(i)
                if item.checkState() == Qt.Checked:
                    self.selected.append(item.data(1).toPyObject())
            self.accept()
        elif sender == self.upButton:
            row = self.list.currentRow()
            item = self.list.takeItem(row)
            self.list.insertItem(row - 1, item)
            self.list.setCurrentItem(item)
        elif sender == self.downButton:
            row = self.list.currentRow()
            item = self.list.takeItem(row)
            self.list.insertItem(row + 1, item)
            self.list.setCurrentItem(item)

class MainWindow(QMainWindow):

    def __init__(self):
        super(QMainWindow, self).__init__()

        self.initUI()

        self.setStatus(u'正在查询设备')
        self.qdt = QueryDeviceThread()
        self.qdt.queryDeviceFinish.connect(self.onDeviceQuery)
        self.qdt.start()

    def initUI(self):
        self.resize(600, 350)
        self.setStatus(u'就绪')
        self.setWindowTitle(u'自动化测试平台开发版')
        self.setWindowIcon(QIcon('logo.png'))
        self.show()

    def onDeviceQuery(self, devices):
        self.setStatus(u'就绪')
        if devices:
            if len(devices) == 1:
                self.serialno = devices[0]
            else:
                self.serialno, ok = QInputDialog.getItem(self, u'选择设备', u'设备列表：', devices, 0, False)
                if not ok:
                    sys.exit(2)
        else:
            QMessageBox.information(self, u'查询失败', u'<p>查询设备失败</p><p>请连接设备或安装驱动后重试</p>')
            sys.exit(2)

        self.setStatus(u'正在连接设备 {0}'.format(self.serialno))
        self.cat = ConnectDeviceThread(self.serialno)
        self.cat.connectDeviceFinish.connect(self.onDeviceConnect)
        self.cat.start()

    def onDeviceConnect(self, adb):
        self.adb = adb
        self.setStatus(u'就绪')

        if not self.adb:
            QMessageBox.information(self, '连接失败', u'<p>连接设备失败</p><p>请确保设备唯一在线且处理空闲状态</p>')
            sys.exit(2)

        self.selected = []
        dialog = SelectTestDialog(self.selected, self)
        if dialog.exec_():
            self.setStatus(u'正在查询设备信息')
            self.qpt = QueryPackageThread(adb)
            self.qpt.queryPackageFinish.connect(self.onPackageQuery)
            self.qpt.start()
        else:
            sys.exit(2)

    def onPackageQuery(self, packages):
        self.setStatus(u'就绪')

        workout = os.path.join(workdir, 'out')
        if not os.path.exists(workout):
            os.mkdir(workout)
        workout = os.path.join(workout, self.adb.getprop('ro.product.model'))
        if not os.path.exists(workout):
            os.mkdir(workout)
        workout = os.path.join(workout, self.adb.getprop('ro.build.display.id'))
        if not os.path.exists(workout):
            os.mkdir(workout)

        login = QMessageBox.question(self, u'登录帐号', u'<p>是否登录预置应用帐号</p><p>如需登录请先切换至英文输入法</p>',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes

        datadir = getconfig(1)
        datatype = None
        if os.path.exists(datadir):
            dirs = os.listdir(datadir)
            dirs = [x for x in dirs if os.path.isdir(os.path.join(datadir, x))]
            item, ok = QInputDialog.getItem(self, u'选择用户数据', u'用户数据类型：', dirs, 0, False)
            if ok and item:
                datatype = str(item)

        executor = {}
        for i in self.selected:
            if i == 1:
                executor[i] = update.Executor(self.adb, workout)
                executor[i].setup()
            elif i == 2:
                executor[i] = launch.Executor(self.adb, workout, packages)
                executor[i].setup()
            elif i == 3:
                executor[i] = scenes.Executor(self.adb, workout)
                executor[i].setup()
            elif i == 4:
                executor[i] = monkey.Executor(self.adb, workout, packages)
                executor[i].setup()
            elif i == 5:
                executor[i] = compat.Executor(self.adb, workout)
                executor[i].setup()
            elif i == 6:
                executor[i] = uptime.Executor(self.adb, workout)
                executor[i].setup()
            elif i == 7:
                executor[i] = stress.Executor(self.adb, workout)
                executor[i].setup()
            elif i == 8:
                executor[i] = memory.Executor(self.adb, workout, packages, datatype)
                executor[i].setup()
            elif i == 9:
                executor[i] = screenshot.Executor(self.adb, workout)
                executor[i].setup()

        self.set = SetupExecuteThread(self.adb, self.selected, executor, login, datatype)
        self.set.statusChange.connect(self.setStatus)
        self.set.start()

    def setStatus(self, text):
        self.statusBar().showMessage(text)

def main():
    remote = getconfig(3).encode('gb2312')
    if not os.path.exists(remote):
        print('Can\'t connect remote file server')
        sys.exit(2)

    zf = zipfile.ZipFile(os.path.join(remote, 'dist.zip'))
    newver = zf.open('v.txt').readline().strip()
    exefile = 'PlatformUpdate.exe' if os.name == 'nt' else 'PlatformUpdate'
    f = open(os.path.join(workdir, exefile), 'wb')
    f.write(zf.read(exefile))
    f.close()
    zf.close()
    lf = open(os.path.join(workdir, 'v.txt'), 'r')
    locver = lf.readline().strip()
    lf.close()

    y = lambda x: [int(i) for i in x.split('.')]
    if y(newver) > y(locver):
        subprocess.Popen('\"{0}\" start'.format(os.path.join(workdir, 'PlatformUpdate')))
        sys.exit(2)

    app = QApplication(sys.argv)
    win = MainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
