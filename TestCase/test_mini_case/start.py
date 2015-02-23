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
        if adb.adbreadline('get-state') == 'device' and not adb.pidof('com.android.commands.monkey') and not adb.pidof('uiautomator'):
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
            self.statusChange.emit(u'正在登录预置的应用帐号')
            loginaccounts(self.adb)
            self.statusChange.emit(u'登录预置的应用帐号完成')

        if self.datatype:
            self.statusChange.emit(u'正在导入预置的用户数据')
            importdata(self.adb, self.datatype)
            self.statusChange.emit(u'导入预置的用户数据完成')

        if self.executor:
            self.statusChange.emit(u'正在执行测试')
            for key in self.executor.keys():
                self.executor.get(key).execute()
            self.statusChange.emit(u'执行测试完成')

            self.statusChange.emit(u'正在生成报告')
            charter.run(self.workout)
            self.statusChange.emit(u'生成报告完成')

        self.adb.kit.destroy()

class MainWindow(QMainWindow):

    def __init__(self):
        super(QMainWindow, self).__init__()
        self.adb = None
        self.initUI()

    def initUI(self):
        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createDockWindows()

        self.textEdit = QTextEdit()
        self.textEdit.setReadOnly(True)
        self.setCentralWidget(self.textEdit)
        self.resize(800, 530)
        self.statusBar().showMessage(u'就绪')
        self.setWindowTitle(u'自动化测试平台开发版')
        self.setWindowIcon(QIcon('logo.png'))
        self.show()

    def connDevice(self):
        self.adb = None
        self.log(u'正在获取在线设备列表')
        self.qdt = QueryDeviceThread()
        self.qdt.queryDeviceFinish.connect(self.onDeviceQuery)
        self.qdt.start()

    def loginAccounts(self):
        if QMessageBox.question(self, u'登录帐号', u'<p>是否登录预置应用帐号</p><p>如需登录请先切换至英文输入法</p>',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes) == QMessageBox.Yes:
            self.set = SetupExecuteThread(self.adb, None, True, None, None)
            self.set.statusChange.connect(self.log)
            self.set.start()

    def importData(self):
        datadir = getconfig(1)
        if os.path.exists(datadir):
            dirs = os.listdir(datadir)
            dirs = [x for x in dirs if os.path.isdir(os.path.join(datadir, x))]
            item, ok = QInputDialog.getItem(self, u'导入数据', u'选择数据类型：', dirs, 0, False)
            if ok and item:
                self.set = SetupExecuteThread(self.adb, None, False, str(item), None)
                self.set.statusChange.connect(self.log)
                self.set.start()

    def createPreparePage(self):
        def loginChecked(checked):
            self.login = checked
        def typeChecked(checked):
            importDataCombo.setEnabled(checked)
            if checked:
                self.datatype = str(importDataCombo.currentText())
            else:
                self.datatype = None
        def typeChanged(text):
            self.datatype = str(text)

        datadir = getconfig(1)
        if os.path.exists(datadir):
            dirs = os.listdir(datadir)
            dirs = [x for x in dirs if os.path.isdir(os.path.join(datadir, x))]
        else:
            dirs = []

        page = QWizardPage()
        page.setTitle(u'测试准备')
        page.setSubTitle(u'设置测试开始前动作')

        loginAccountsCheck = QCheckBox(u'登录帐号')
        loginAccountsCheck.setChecked(self.login)
        loginAccountsCheck.toggled[bool].connect(loginChecked)
        importDataCombo = QComboBox()
        importDataCombo.addItems(dirs)
        importDataCombo.activated[str].connect(typeChanged)
        importDataCombo.setEnabled(False)
        importDataCombo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        importDataCheck = QCheckBox(u'导入数据')
        importDataCheck.setEnabled(len(dirs) > 0)
        importDataCheck.toggled[bool].connect(typeChecked)

        layout = QGridLayout()
        layout.addWidget(loginAccountsCheck, 0, 0)
        layout.addWidget(importDataCheck, 1, 0)
        layout.addWidget(importDataCombo, 1, 1)
        page.setLayout(layout)

        return page

    def buttonClicked(self):
        sender = self.sender()

        if sender == self.selallButton:
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

    def createSelectPage(self):
        def itemChanged(item):
            self.executor.clear()
            for i in range(self.list.count()):
                item = self.list.item(i)
                if item.checkState() == Qt.Checked:
                    key = item.data(1).toPyObject()
                    self.executor[key] = self.tempexec.get(key)

        page = QWizardPage()
        page.setTitle(u'测试项')
        page.setSubTitle(u'选择需要测试的项')

        self.list = QListWidget(self)
        for key in self.tempexec.keys():
            item = QListWidgetItem(self.tempexec.get(key).title())
            item.setCheckState(Qt.Unchecked)
            item.setData(1, QVariant(key))
            self.list.addItem(item)
        self.list.itemChanged.connect(itemChanged)
        self.list.currentItemChanged.connect(itemChanged)
        self.selallButton = QPushButton(u'全选')
        self.selallButton.clicked.connect(self.buttonClicked)
        self.disallButton = QPushButton(u'反选')
        self.disallButton.clicked.connect(self.buttonClicked)
        self.upButton = QPushButton(u'上移')
        self.upButton.clicked.connect(self.buttonClicked)
        self.downButton = QPushButton(u'下移')
        self.downButton.clicked.connect(self.buttonClicked)
        buttonBox = QDialogButtonBox(Qt.Vertical)
        buttonBox.addButton(self.selallButton, QDialogButtonBox.ActionRole)
        buttonBox.addButton(self.disallButton, QDialogButtonBox.ActionRole)
        buttonBox.addButton(self.upButton, QDialogButtonBox.ActionRole)
        buttonBox.addButton(self.downButton, QDialogButtonBox.ActionRole)

        layout = QHBoxLayout()
        layout.addWidget(self.list)
        layout.addWidget(buttonBox)
        page.setLayout(layout)

        return page

    def pageIdChanged(self, id):
        page = self.wizard.page(id)
        if id > 1:
            page.setEnabled(getattr(page, 'key', -1) in self.executor.keys())

    def runBuildTest(self):
        workout = os.path.join(workdir, 'out')
        if not os.path.exists(workout):
            os.mkdir(workout)
        workout = os.path.join(workout, self.adb.getprop('ro.product.model'))
        if not os.path.exists(workout):
            os.mkdir(workout)
        self.workout = os.path.join(workout, self.adb.getprop('ro.build.display.id'))
        if not os.path.exists(self.workout):
            os.mkdir(self.workout)

        self.executor = collections.OrderedDict()
        self.executor[0] = update.Executor(self)
        self.executor[1] = launch.Executor(self)
        self.executor[2] = scenes.Executor(self)
        self.executor[3] = monkey.Executor(self)
        self.executor[4] = compat.Executor(self)
        self.executor[5] = uptime.Executor(self)
        self.executor[6] = stress.Executor(self)
        self.executor[7] = memory.Executor(self)
        self.executor[8] = screenshot.Executor(self)
        self.tempexec = copy.copy(self.executor)
        self.executor.clear()

        self.login = False
        self.datatype = None
        self.wizard = QWizard(self)
        self.wizard.currentIdChanged[int].connect(self.pageIdChanged)
        self.wizard.addPage(self.createPreparePage())
        self.wizard.addPage(self.createSelectPage())
        for key in self.tempexec.keys():
            page = self.tempexec.get(key).setup()
            if page:
                setattr(page, 'key', key)
                self.wizard.addPage(page)
        self.wizard.setWindowTitle(u'日常测试设置向导')
        if self.wizard.exec_() and self.executor:
            self.set = SetupExecuteThread(self.adb, self.executor, self.login, self.datatype, self.workout)
            self.set.statusChange.connect(self.log)
            self.set.start()

    def about(self):
        with open(os.path.join(workdir, 'v.txt'), 'r') as f:
            ver = f.readline().strip()
        QMessageBox.about(self, u'关于自动化测试平台',
                u'<p>自动化测试平台提供日常功能及性能测试并支持用例扩展<p>'
                u'<p>技术支持：中兴移动软件一部一科自动化测试小组</p>'
                u'<p>软件版本：{0}'.format(ver))

    def createActions(self):
        self.connDeviceAct = QAction(u'连接设备', self, shortcut='Ctrl+C',
                statusTip=u'连接在线的设备', triggered=self.connDevice)
        self.uploadCaseAct = QAction(u'上传用例', self, shortcut='Ctrl+U',
                statusTip=u'上传测试用例至服务器', triggered=self.about)
        self.loginAccountsAct = QAction(u'登录帐号', self, shortcut='Ctrl+L',
                statusTip=u'登录预置的应用帐号', triggered=self.loginAccounts)
        self.loginAccountsAct.setDisabled(True)
        self.importDataAct = QAction(u'导入数据', self, shortcut='Ctrl+I',
                statusTip=u'导入预置的用户数据', triggered=self.importData)
        self.importDataAct.setDisabled(True)
        self.buildTestAct = QAction(u'日常测试', self, shortcut='Ctrl+B',
                statusTip=u'运行自带的功能及性能测试', triggered=self.runBuildTest)
        self.buildTestAct.setDisabled(True)
        self.extendTestAct = QAction(u'扩展用例', self, shortcut='Ctrl+E',
                statusTip=u'运行扩展和上传的测试用例', triggered=self.about)
        self.extendTestAct.setDisabled(True)
        self.aboutAct = QAction(u'关于', self, shortcut='F1', triggered=self.about)
        self.aboutQtAct = QAction(u'关于Qt', self, triggered=qApp.aboutQt)

    def createMenus(self):
        self.deviceMenu = self.menuBar().addMenu(u'设备(&D)')
        self.deviceMenu.addAction(self.connDeviceAct)
        self.caseMenu = self.menuBar().addMenu(u'用例(&C)')
        self.caseMenu.addAction(self.uploadCaseAct)
        self.runMenu = self.menuBar().addMenu(u'运行(&R)')
        self.runMenu.addAction(self.loginAccountsAct)
        self.runMenu.addAction(self.importDataAct)
        self.runMenu.addSeparator()
        self.runMenu.addAction(self.buildTestAct)
        self.runMenu.addAction(self.extendTestAct)
        self.viewMenu = self.menuBar().addMenu(u'视图(&V)')
        self.helpMenu = self.menuBar().addMenu(u'帮助(&H)')
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

    def createToolBars(self):
        '''self.runToolBar = self.addToolBar('RUN')
        self.runToolBar.addAction(self.loginAccountsAct)
        self.runToolBar.addAction(self.importDataAct)
        self.runToolBar.addAction(self.buildTestAct)
        self.runToolBar.addAction(self.userTestAct)'''

    def createDockWindows(self):
        dock = QDockWidget(u'设备信息', self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.deviceInfo = QTableWidget(8, 2)
        self.deviceInfo.setEditTriggers(QTableWidget.NoEditTriggers)
        self.deviceInfo.setSelectionBehavior(QTableWidget.SelectRows)
        self.deviceInfo.setSelectionMode(QTableWidget.SingleSelection)
        self.deviceInfo.setAlternatingRowColors(True)
        self.deviceInfo.verticalHeader().setVisible(False)
        self.deviceInfo.horizontalHeader().setStretchLastSection(True)
        self.deviceInfo.horizontalHeader().setVisible(False)

        self.deviceInfo.setItem(0, 0, QTableWidgetItem(u'序列号'))
        self.deviceInfo.setItem(1, 0, QTableWidgetItem(u'型号'))
        self.deviceInfo.setItem(2, 0, QTableWidgetItem(u'Android版本'))
        self.deviceInfo.setItem(3, 0, QTableWidgetItem(u'版本号'))
        self.deviceInfo.setItem(4, 0, QTableWidgetItem(u'内部版本'))
        self.deviceInfo.setItem(5, 0, QTableWidgetItem(u'版本类型'))
        self.deviceInfo.setItem(6, 0, QTableWidgetItem(u'制造商'))
        self.deviceInfo.setItem(7, 0, QTableWidgetItem(u'平台'))

        dock.setWidget(self.deviceInfo)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())

    def onDeviceQuery(self, devices):
        if devices:
            if len(devices) == 1:
                self.serialno = devices[0]
            else:
                self.serialno, ok = QInputDialog.getItem(self, u'选择设备', u'设备列表：', devices, 0, False)

            if self.serialno:
                self.log(u'正在连接设备 {0}'.format(self.serialno))
                self.cat = ConnectDeviceThread(self.serialno)
                self.cat.connectDeviceFinish.connect(self.onDeviceConnect)
                self.cat.start()
        else:
            self.loge(u'无法获取在线设备列表，请连接设备并打开USB调试后重试')

    def onDeviceConnect(self, adb):
        self.adb = adb

        if self.adb:
            self.log(u'正在获取设备信息')
            self.qpt = QueryPackageThread(adb)
            self.qpt.queryPackageFinish.connect(self.onPackageQuery)
            self.qpt.start()
        else:
            self.loge(u'无法连接设备 {0}，请确保该设备唯一在线且处于空闲状态'.format(self.serialno))

    def onPackageQuery(self, packages):
        self.packages = packages
        self.log(u'初始设备完成')
        self.runMenu.setEnabled(True)
        self.loginAccountsAct.setEnabled(True)
        self.importDataAct.setEnabled(True)
        self.buildTestAct.setEnabled(True)
        self.extendTestAct.setEnabled(True)
        self.deviceInfo.setItem(0, 1, QTableWidgetItem(self.serialno))
        self.deviceInfo.setItem(1, 1, QTableWidgetItem(self.adb.getprop('ro.product.model')))
        self.deviceInfo.setItem(2, 1, QTableWidgetItem(self.adb.getprop('ro.build.version.release')))
        self.deviceInfo.setItem(3, 1, QTableWidgetItem(self.adb.getprop('ro.build.display.id')))
        self.deviceInfo.setItem(4, 1, QTableWidgetItem(self.adb.getprop('ro.build.internal.id')))
        self.deviceInfo.setItem(5, 1, QTableWidgetItem(self.adb.getprop('ro.build.type')))
        self.deviceInfo.setItem(6, 1, QTableWidgetItem(self.adb.getprop('ro.product.manufacturer')))
        self.deviceInfo.setItem(7, 1, QTableWidgetItem(self.adb.getprop('ro.board.platform')))

    def log(self, text, color='black'):
        strt = time.strftime('%Y-%m-%d %H:%M:%S')
        if self.adb:
            text = u'<font color="{0}">{1} [{2}] {3}</font>\n'.format(color, strt, self.serialno, text)
        else:
            text = u'<font color="{0}">{1} {2}</font>\n'.format(color, strt, text)
        self.textEdit.append(text)

    def loge(self, text):
        self.log(text, color='red')

def main():
    remote = getconfig(3).encode('gb2312')
    if os.path.exists(remote):
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
