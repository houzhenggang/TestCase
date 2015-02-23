# -*- coding: utf-8 -*-

import collections
import copy
import os
import time

import common
import compat
import memory
import monkey
import launch
import scenes
import screenshot
import stress
import update
import uptime
import chart.run as chart

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from common import workdir, getconfig, loginaccounts, importdata

class BuildSetupWizard(QWizard):

    def __init__(self, parent):
        super(BuildSetupWizard, self).__init__(parent)

        self.tempexec = copy.copy(self.parentWidget().executor)
        self.parentWidget().executor.clear()

        self.initUI()

    def initUI(self):
        self.setWindowTitle(u'日常测试设置向导')
        self.currentIdChanged[int].connect(self.pageIdChanged)
        self.addPage(self.createPreparePage())
        self.addPage(self.createSelectPage())
        for key in self.tempexec.keys():
            page = self.tempexec.get(key).setup()
            if page:
                setattr(page, 'key', key)
                self.addPage(page)

    def pageIdChanged(self, id):
        page = self.page(id)
        if id > 1:
            page.setEnabled(getattr(page, 'key', -1) in self.parentWidget().executor.keys())

    def stateToggled(self, state):
        sender = self.sender()

        if sender == self.loginAccountsCheck:
            self.parentWidget().login = state
        elif sender == self.importDataCheck:
            self.importDataCombo.setEnabled(state)
            if state:
                self.parentWidget().datatype = str(self.importDataCombo.currentText())
            else:
                self.parentWidget().datatype = None

    def itemActivated(self, item):
        sender = self.sender()

        if sender == self.importDataCombo:
            self.parentWidget().datatype = str(item)

    def createPreparePage(self):
        datadir = getconfig(1)
        if os.path.exists(datadir):
            items = os.listdir(datadir)
            items = [x for x in items if os.path.isdir(os.path.join(datadir, x))]
        else:
            items = []

        page = QWizardPage()
        page.setTitle(u'测试准备')
        page.setSubTitle(u'设置测试开始前动作')

        self.loginAccountsCheck = QCheckBox(u'登录帐号')
        self.loginAccountsCheck.setChecked(self.parentWidget().login)
        self.loginAccountsCheck.toggled[bool].connect(self.stateToggled)
        self.importDataCombo = QComboBox()
        self.importDataCombo.addItems(items)
        self.importDataCombo.activated[str].connect(self.itemActivated)
        self.importDataCombo.setEnabled(False)
        self.importDataCombo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.importDataCheck = QCheckBox(u'导入数据')
        self.importDataCheck.setEnabled(len(items) > 0)
        self.importDataCheck.toggled[bool].connect(self.stateToggled)

        layout = QGridLayout()
        layout.addWidget(self.loginAccountsCheck, 0, 0)
        layout.addWidget(self.importDataCheck, 1, 0)
        layout.addWidget(self.importDataCombo, 1, 1)
        page.setLayout(layout)

        return page

    def itemChanged(self, item):
        sender = self.sender()

        if sender == self.list:
            self.parentWidget().executor.clear()
            for i in range(self.list.count()):
                item = self.list.item(i)
                if item.checkState() == Qt.Checked:
                    key = item.data(1).toPyObject()
                    self.parentWidget().executor[key] = self.tempexec.get(key)

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
        page = QWizardPage()
        page.setTitle(u'测试项')
        page.setSubTitle(u'选择需要测试的项')

        self.list = QListWidget(self)
        for key in self.tempexec.keys():
            item = QListWidgetItem(self.tempexec.get(key).title())
            item.setCheckState(Qt.Unchecked)
            item.setData(1, QVariant(key))
            self.list.addItem(item)
        self.list.itemChanged.connect(self.itemChanged)
        self.list.currentItemChanged.connect(self.itemChanged)
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

class SetupExecuteThread(QThread):

    statusChanged = pyqtSignal(unicode)

    def __init__(self, adb, **args):
        super(SetupExecuteThread, self).__init__()

        self.adb = adb
        self.login = args.get('login')
        self.datatype = args.get('datatype')
        self.executor = args.get('executor')
        self.workout = args.get('workout')

    def run(self):
        self.statusChanged.emit(u'正在唤醒设备')
        self.adb.kit.wakeup()

        self.statusChanged.emit(u'正在设置屏幕不锁定')
        self.adb.kit.disablekeyguard()
        self.adb.kit.keepscreenon()

        if self.login:
            self.statusChanged.emit(u'正在登录预置的应用帐号')
            loginaccounts(self.adb)
            self.statusChanged.emit(u'登录预置的应用帐号完成')

        if self.datatype:
            self.statusChanged.emit(u'正在导入预置的用户数据')
            importdata(self.adb, self.datatype)
            self.statusChanged.emit(u'导入预置的用户数据完成')

        if self.executor:
            self.statusChanged.emit(u'正在执行测试')
            for key in self.executor.keys():
                self.executor.get(key).execute()
            self.statusChanged.emit(u'执行测试完成')

            self.statusChanged.emit(u'正在生成报告')
            chart.run(self.workout)
            self.statusChanged.emit(u'生成报告完成')

class ChildWindow(QTextEdit):

    def __init__(self, adb, packages):
        super(ChildWindow, self).__init__()

        self.adb = adb
        self.packages = packages

        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle(self.adb.getprop('ro.boot.serialno'))

    def loginAccounts(self):
        if QMessageBox.question(self, u'登录帐号', u'<p>是否登录预置应用帐号</p><p>如需登录请先切换至英文输入法</p>',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes) == QMessageBox.Yes:
            self.t = SetupExecuteThread(self.adb, login=True)
            self.t.statusChanged.connect(self.log)
            self.t.start()

    def importData(self):
        datadir = getconfig(1)
        if os.path.exists(datadir):
            items = os.listdir(datadir)
            items = [x for x in items if os.path.isdir(os.path.join(datadir, x))]
            item, ok = QInputDialog.getItem(self, u'导入数据', u'选择数据类型：', items, 0, False)
            if ok and item:
                self.t = SetupExecuteThread(self.adb, datatype=str(item))
                self.t.statusChanged.connect(self.log)
                self.t.start()

    def executeBuildTest(self):
        workout = os.path.join(workdir, 'out')
        if not os.path.exists(workout):
            os.mkdir(workout)
        workout = os.path.join(workout, self.adb.getprop('ro.product.model'))
        if not os.path.exists(workout):
            os.mkdir(workout)
        workout = os.path.join(workout, self.adb.getprop('ro.build.display.id'))
        if not os.path.exists(workout):
            os.mkdir(workout)
        self.workout = workout

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

        self.login = False
        self.datatype = None
        wizard = BuildSetupWizard(self)
        if wizard.exec_() and self.executor:
            self.t = SetupExecuteThread(self.adb, executor=self.executor, login=self.login, datatype=self.datatype, workout=self.workout)
            self.t.statusChanged.connect(self.log)
            self.t.start()

    def executeExtendTest(self):
        pass

    def log(self, msg, color='black'):
        strft = time.strftime('%Y-%m-%d %H:%M:%S')
        line = u'<font color="{0}">{1} {2}</font>\n'.format(color, strft, msg)
        self.append(line)

    def loge(self, msg):
        self.log(msg, 'red')

    def logw(self, msg):
        self.log(msg, 'yellow')
