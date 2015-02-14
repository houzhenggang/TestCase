# -*- coding: utf-8 -*-

import collections
import copy
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
import compat
import memory
import monkey
import launch
import scenes
import stress
import update
import uptime
import screenshot
import chart.run as charter

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from common import workdir, getconfig, loginaccounts, importdata

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

    def __init__(self, adb, executor, login, datatype, workout):
        super(SetupExecuteThread, self).__init__(None)
        self.adb = adb
        self.executor = executor
        self.login = login
        self.datatype = datatype
        self.workout = workout

    def run(self):
        self.statusChange.emit(u'正在唤醒设备')
        self.adb.kit.wakeup()

        self.statusChange.emit(u'正在设置屏幕不锁定')
        self.adb.kit.disablekeyguard()
        self.adb.kit.keepscreenon()

        if self.login:
            self.statusChange.emit(u'正在登录应用帐号')
            loginaccounts(self.adb)

        if self.datatype:
            self.statusChange.emit(u'正在导入用户数据')
            importdata(self.adb, self.datatype)

        self.statusChange.emit(u'正在执行测试')
        start = time.time()
        for key in self.executor.keys():
            self.executor.get(key).execute()
        end = time.time()

        self.statusChange.emit(u'正在生成报告')
        charter.run(self.workout)

        self.statusChange.emit(u'完成')
        self.adb.kit.destroy()

class SelectTestDialog(QDialog):

    def __init__(self, executor, parent=None):
        super(SelectTestDialog, self).__init__(parent)
        self.executor = executor
        self.initUI()

    def initUI(self):
        self.list = QListWidget(self)
        for key in self.executor.keys():
            item = QListWidgetItem(self.executor.get(key).title())
            item.setCheckState(Qt.Unchecked)
            item.setData(1, QVariant(key))
            self.list.addItem(item)
        self.list.setCurrentRow(0)

        self.okButton = QPushButton(u'确定')
        self.okButton.clicked.connect(self.buttonClicked)
        self.okButton.setDefault(True)
        self.selallButton = QPushButton(u'全选')
        self.selallButton.clicked.connect(self.buttonClicked)
        self.disallButton = QPushButton(u'反选')
        self.disallButton.clicked.connect(self.buttonClicked)
        self.upButton = QPushButton(u'上移')
        self.upButton.clicked.connect(self.buttonClicked)
        self.downButton = QPushButton(u'下移')
        self.downButton.clicked.connect(self.buttonClicked)
        buttonBox = QDialogButtonBox(Qt.Vertical)
        buttonBox.addButton(self.okButton, QDialogButtonBox.ActionRole)
        buttonBox.addButton(self.selallButton, QDialogButtonBox.ActionRole)
        buttonBox.addButton(self.disallButton, QDialogButtonBox.ActionRole)
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
            tmpexec = copy.copy(self.executor)
            self.executor.clear()
            for i in range(self.list.count()):
                item = self.list.item(i)
                if item.checkState() == Qt.Checked:
                    key = item.data(1).toPyObject()
                    self.executor[key] = tmpexec.get(key)
            self.accept()
        elif sender == self.selallButton:
            for i in range(self.list.count()):
                self.list.item(i).setCheckState(Qt.Checked)
        elif sender == self.disallButton:
            for i in range(self.list.count()):
                self.list.item(i).setCheckState(Qt.Unchecked)
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
        self.createActions()
        self.createMenus()
        self.createToolBars()

        self.resize(600, 350)
        self.setStatus(u'就绪')
        self.setWindowTitle(u'自动化测试平台开发版')
        self.setWindowIcon(QIcon('logo.png'))
        self.show()

    def about(self):
        with open(os.path.join(workdir, 'v.txt'), 'r') as f:
            ver = f.readline().strip()
        QMessageBox.about(self, u'关于自动化测试平台',
                u'<p>自动化测试平台提供日常以及性能测试并支持用例扩展<p>'
                u'<p>技术支持：中兴移动软件一部一科自动化测试小组</p>'
                u'<p>软件版本：{0}'.format(ver))

    def createActions(self):
        self.loginAccountAct = QAction(u'登录帐号', self, triggered=self.about)
        self.importDataAct = QAction(u'导入用户数据', self, triggered=self.about)
        self.aboutAct = QAction(u'关于', self, shortcut='F1', triggered=self.about)
        self.aboutQtAct = QAction(u'关于Qt', self, triggered=qApp.aboutQt)

    def createMenus(self):
        self.helpMenu = self.menuBar().addMenu(u'帮助(&H)')
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

    def createToolBars(self):
        self.prepToolBar = self.addToolBar('PREP')
        self.prepToolBar.addAction(self.loginAccountAct)
        self.prepToolBar.addAction(self.importDataAct)

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
            QMessageBox.information(self, u'查询失败', u'<p>查询设备失败</p><p>请连接设备并打开USB调试后重试</p>')
            sys.exit(2)

        self.setStatus(u'正在连接设备 {0}'.format(self.serialno))
        self.cat = ConnectDeviceThread(self.serialno)
        self.cat.connectDeviceFinish.connect(self.onDeviceConnect)
        self.cat.start()

    def onDeviceConnect(self, adb):
        self.adb = adb
        self.setStatus(u'就绪')

        if not self.adb:
            QMessageBox.information(self, u'连接失败', u'<p>连接设备失败</p><p>请确保设备唯一在线且处理空闲状态</p>')
            sys.exit(2)

        self.setStatus(u'正在获取设备信息')
        self.qpt = QueryPackageThread(adb)
        self.qpt.queryPackageFinish.connect(self.onPackageQuery)
        self.qpt.start()

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

        datatype = None
        datadir = getconfig(1)
        dirs = os.listdir(datadir)
        dirs = [x for x in dirs if os.path.isdir(os.path.join(datadir, x))]
        item, ok = QInputDialog.getItem(self, u'选择用户数据', u'用户数据类型：', dirs, 0, False)
        if ok and item:
            datatype = str(item)

        executor = collections.OrderedDict()
        executor[0] = update.Executor(self.adb, workout)
        executor[1] = launch.Executor(self.adb, workout, packages)
        executor[2] = scenes.Executor(self.adb, workout)
        executor[3] = monkey.Executor(self.adb, workout, packages)
        executor[4] = compat.Executor(self.adb, workout)
        executor[5] = uptime.Executor(self.adb, workout)
        executor[6] = stress.Executor(self.adb, workout)
        executor[7] = memory.Executor(self.adb, workout, packages, datatype)
        executor[8] = screenshot.Executor(self.adb, workout)

        dialog = SelectTestDialog(executor, self)
        if not dialog.exec_() or not executor:
            sys.exit(2)

        for key in executor.keys():
            executor.get(key).setup(self)

        self.set = SetupExecuteThread(self.adb, executor, login, datatype, workout)
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
