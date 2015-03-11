# -*- coding: utf-8 -*-

import collections
import copy
import os
import time

import chart.run as chart
import common
import compar
import compat
import memory
import module
import monkey
import launch
import scenes
import stress
import update
import uptime

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from common import workdir, getconfig, loginaccounts, importdata

class BuildAddDialog(QDialog):

    def __init__(self, parent):
        super(BuildAddDialog, self).__init__(parent)

        self.initUI()

    def initUI(self):
        self.fileNameEdit = QLineEdit()
        self.fileNameEdit.setReadOnly(True)
        self.fileNameButton = QPushButton(u'打开')
        self.fileNameButton.clicked.connect(self.buttonClicked)
        self.testNameEdit = QLineEdit()
        self.testNameEdit.setReadOnly(True)
        self.testVersionEdit = QLineEdit()
        self.testVersionEdit.setReadOnly(True)
        self.testParamsEdit = QLineEdit()
        self.testParamsEdit.textChanged.connect(self.textChanged)
        self.testDescEdit = QTextEdit()
        self.testDescEdit.setReadOnly(True)

        layout = QGridLayout()
        layout.addWidget(QLabel(u'文件名'), 0, 0)
        layout.addWidget(self.fileNameEdit, 0, 1)
        layout.addWidget(self.fileNameButton, 0, 2)
        layout.addWidget(QLabel(u'测试名'), 1, 0)
        layout.addWidget(self.testNameEdit, 1, 1, 1, 2)
        layout.addWidget(QLabel(u'版本'), 2, 0)
        layout.addWidget(self.testVersionEdit, 2, 1, 1, 2)
        layout.addWidget(QLabel(u'参数'), 3, 0)
        layout.addWidget(self.testParamsEdit, 3, 1, 1, 2)
        layout.addWidget(QLabel(u'说明'), 4, 0)
        layout.addWidget(self.testDescEdit, 4, 1, 1, 2)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(layout)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)
        self.resize(400, 250)
        self.setWindowTitle(u'添加用例')

    def buttonClicked(self):
        sender = self.sender()

        if sender == self.fileNameButton:
            filename = QFileDialog.getOpenFileName(self, u'添加用例',
                    getconfig(5), u'压缩文件 (*.zip)')
            if filename:
                self.fillContent(filename)

    def fillContent(self, filename):
        self.fileNameEdit.setText(filename)
        self.filename = str(filename)
        info = module.parse(self.filename)
        self.testname = info.get('name', '')
        self.testNameEdit.setText(self.testname)
        self.testVersionEdit.setText(info.get('version', ''))
        self.params = ''
        self.testParamsEdit.clear()
        self.testDescEdit.setText(info.get('desc', ''))
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True if info else False)

    def textChanged(self, text):
        self.params = text

class BuildSetupWizard(QWizard):

    def __init__(self, parent):
        super(BuildSetupWizard, self).__init__(parent)

        self.tempexec = copy.copy(self.parentWidget().executor)
        self.parentWidget().executor.clear()

        self.initUI()

    def initUI(self):
        self.setWindowTitle(u'测试用例设置向导')
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
        page.setSubTitle(u'选择测试开始前的准备动作。')
        page.setFinalPage(True)

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

        if sender == self.addButton:
            dialog = BuildAddDialog(self)
            if dialog.exec_():
                key = max(self.tempexec.keys()) + 1
                self.tempexec[key] = module.Executor(self.parentWidget().adb,
                        self.parentWidget().workout, dialog.testname,
                        dialog.filename, dialog.params)
                item = QListWidgetItem(self.tempexec.get(key).title())
                item.setCheckState(Qt.Unchecked)
                item.setData(1, QVariant(key))
                self.list.addItem(item)
                self.list.setCurrentItem(item)
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

    def createSelectPage(self):
        page = QWizardPage()
        page.setTitle(u'选择用例')
        page.setSubTitle(u'选择和添加需要执行的测试用例。')
        page.setFinalPage(True)

        self.list = QListWidget(self)
        for key in self.tempexec.keys():
            item = QListWidgetItem(self.tempexec.get(key).title())
            item.setCheckState(Qt.Unchecked)
            item.setData(1, QVariant(key))
            self.list.addItem(item)
        self.list.itemChanged.connect(self.itemChanged)
        self.list.currentItemChanged.connect(self.itemChanged)
        self.addButton = QPushButton(u'添加')
        self.addButton.clicked.connect(self.buttonClicked)
        self.selallButton = QPushButton(u'全选')
        self.selallButton.clicked.connect(self.buttonClicked)
        self.disallButton = QPushButton(u'反选')
        self.disallButton.clicked.connect(self.buttonClicked)
        self.upButton = QPushButton(u'上移')
        self.upButton.clicked.connect(self.buttonClicked)
        self.downButton = QPushButton(u'下移')
        self.downButton.clicked.connect(self.buttonClicked)
        buttonBox = QDialogButtonBox(Qt.Vertical)
        buttonBox.addButton(self.addButton, QDialogButtonBox.ActionRole)
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

    logged = pyqtSignal(unicode, str)

    def __init__(self, adb, **args):
        super(SetupExecuteThread, self).__init__()

        self.adb = adb
        self.login = args.get('login')
        self.datatype = args.get('datatype')
        self.executor = args.get('executor')
        self.workout = args.get('workout')

    def run(self):
        self.log(u'正在设置设备')
        self.adb.kit.wakeup()
        self.adb.kit.disablekeyguard()
        self.adb.kit.keepscreenon()

        start = time.time()

        if self.login:
            self.log(u'正在登录预置的应用帐号')
            loginaccounts(self.adb)

        if self.datatype:
            self.log(u'正在导入预置的用户数据')
            importdata(self.adb, self.datatype)

        if self.executor:
            for value in self.executor.values():
                self.log(u'正在执行{0}'.format(value.title()))
                value.execute(self.log)

            self.log(u'正在生成测试报告')
            chart.run(self.workout)

        self.log(u'所有任务完成，共耗时{0}秒'.format(round(time.time() - start, 3)))

    def log(self, msg, color='black'):
        self.logged.emit(msg, color)

class ChildWindow(QWidget):

    def __init__(self, adb, packages):
        super(ChildWindow, self).__init__()

        self.adb = adb
        self.packages = packages

        self.info = collections.OrderedDict()
        self.info['序列号'] = self.adb.getprop('ro.boot.serialno')
        self.info['型号'] = self.adb.getprop('ro.product.model')
        self.info['Android版本'] = self.adb.getprop('ro.build.version.release')
        self.info['版本号'] = self.adb.getprop('ro.build.display.id')
        self.info['内部版本'] = self.adb.getprop('ro.build.internal.id')
        self.info['版本类型'] = self.adb.getprop('ro.build.type')
        self.info['制造商'] = self.adb.getprop('ro.product.manufacturer')
        self.info['平台'] = self.adb.getprop('ro.board.platform')

        self.workout = os.path.join(workdir, 'out')
        if not os.path.exists(self.workout):
            os.mkdir(self.workout)
        self.workout = os.path.join(self.workout, self.info['型号'])
        if not os.path.exists(self.workout):
            os.mkdir(self.workout)
        self.workout = os.path.join(self.workout, self.info['版本号'])
        if not os.path.exists(self.workout):
            os.mkdir(self.workout)

        self.initUI()

    def initUI(self):
        self.message = QTextEdit()
        self.message.setReadOnly(True)
        self.devinfo = QTableWidget(8, 2)
        self.devinfo.setEditTriggers(QTableWidget.NoEditTriggers)
        self.devinfo.setSelectionBehavior(QTableWidget.SelectRows)
        self.devinfo.setSelectionMode(QTableWidget.SingleSelection)
        self.devinfo.setAlternatingRowColors(True)
        self.devinfo.verticalHeader().setVisible(False)
        self.devinfo.horizontalHeader().setStretchLastSection(True)
        self.devinfo.horizontalHeader().setVisible(False)
        for i, (key, value) in enumerate(self.info.items()):
            self.devinfo.setItem(i, 0, QTableWidgetItem(unicode(key)))
            self.devinfo.setItem(i, 1, QTableWidgetItem(value))

        splitter1 = QSplitter(Qt.Vertical)
        splitter1.addWidget(self.devinfo)
        splitter1.addWidget(self.message)

        layout = QHBoxLayout()
        layout.addWidget(splitter1)
        self.setLayout(layout)

        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle(self.userFriendlyCurrentDevice())

    def loginAccounts(self):
        if QMessageBox.question(self, u'登录帐号', u'<p>是否登录预置应用帐号</p><p>如需登录请先切换至英文输入法</p>',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes) == QMessageBox.Yes:
            self.t = SetupExecuteThread(self.adb, login=True)
            self.t.logged.connect(self.log)
            self.t.start()

    def importData(self):
        datadir = getconfig(1)
        if os.path.exists(datadir):
            items = os.listdir(datadir)
            items = [x for x in items if os.path.isdir(os.path.join(datadir, x))]
            item, ok = QInputDialog.getItem(self, u'导入数据', u'选择数据类型：', items, 0, False)
            if ok and item:
                self.t = SetupExecuteThread(self.adb, datatype=str(item))
                self.t.logged.connect(self.log)
                self.t.start()

    def executeBuildTest(self):
        self.executor = collections.OrderedDict()
        self.executor[0] = update.Executor(self.adb)
        self.executor[1] = launch.Executor(self.adb, self.workout, self.packages)
        self.executor[2] = scenes.Executor(self.adb, self.workout)
        self.executor[3] = monkey.Executor(self.adb, self.workout, self.packages)
        self.executor[4] = compat.Executor(self.adb, self.workout)
        self.executor[5] = uptime.Executor(self.adb, self.workout)
        self.executor[6] = stress.Executor(self.adb, self.workout)
        self.executor[7] = memory.Executor(self.adb, self.workout, self.packages, self)
        self.executor[8] = compar.Executor(self.adb, self.workout)

        self.login = False
        self.datatype = None
        wizard = BuildSetupWizard(self)
        if wizard.exec_() and self.executor:
            self.t = SetupExecuteThread(self.adb, executor=self.executor, login=self.login,
                    datatype=self.datatype, workout=self.workout)
            self.t.logged.connect(self.log)
            self.t.start()

    def userFriendlyCurrentDevice(self):
        return self.info.get('序列号')

    def log(self, msg, color='black'):
        strft = time.strftime('%Y-%m-%d %H:%M:%S')
        line = u'<font color="{0}">{1} {2}</font>\n'.format(color, strft, msg)
        self.message.append(line)
