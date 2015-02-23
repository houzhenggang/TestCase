# -*- coding: utf-8 -*-

import os
import sys

import adbkit
import child
import common

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from common import workdir

class QueryDeviceThread(QThread):

    queryDeviceDone = pyqtSignal(tuple)

    def __init__(self):
        super(QueryDeviceThread, self).__init__()

    def run(self):
        self.queryDeviceDone.emit(adbkit.devices())

class ConnectDeviceThread(QThread):

    connectDeviceDone = pyqtSignal(str, adbkit.Adb)

    def __init__(self, serialno):
        super(ConnectDeviceThread, self).__init__()
        self.serialno = serialno

    def run(self):
        adb = adbkit.Adb(self.serialno)
        if adb.adbreadline('get-state') != 'device' or adb.pidof('com.android.commands.monkey') or adb.pidof('uiautomator'):
            adb = None
        self.connectDeviceDone.emit(self.serialno, adb)

class QueryPackageThread(QThread):

    queryPackageDone = pyqtSignal(adbkit.Adb, dict)

    def __init__(self, adb):
        super(QueryPackageThread, self).__init__()
        self.adb = adb

    def run(self):
        packages = self.adb.kit.getpackages()
        testpkgs = [line[8:].strip() for line in self.adb.shellreadlines('pm list package -s')]
        packages = dict([x for x in packages.items() if x[0] in testpkgs])
        self.queryPackageDone.emit(self.adb, packages)

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.initUI()

    def initUI(self):
        self.mdiArea = QMdiArea()
        self.mdiArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setCentralWidget(self.mdiArea)

        self.mdiArea.subWindowActivated.connect(self.updateMenus)
        self.windowMapper = QSignalMapper(self)
        self.windowMapper.mapped[QWidget].connect(self.setActiveSubWindow)

        self.createActions()
        self.createMenus()
        self.createStatusBar()
        #self.updateMenus()

        #self.readSettings()

        self.setWindowTitle(u'自动化测试平台开发版')
        self.setWindowIcon(QIcon('logo.png'))
        self.setUnifiedTitleAndToolBarOnMac(True)

    def closeEvent(self, event):
        self.mdiArea.closeAllSubWindows()
        if self.mdiArea.currentSubWindow():
            event.ignore()
        else:
            #self.writeSettings()
            event.accept()

    def connectDevice(self):
        print(u'正在获取在线设备列表')
        self.t = QueryDeviceThread()
        self.t.queryDeviceDone.connect(self.onDeviceQuery)
        self.t.start()

    def onDeviceQuery(self, devices):
        if devices:
            if len(devices) == 1:
                serialno = devices[0]
            else:
                serialno, ok = QInputDialog.getItem(self, u'选择设备', u'设备列表：', devices, 0, False)

            if serialno:
                print(u'正在连接设备 {0}'.format(serialno))
                self.t = ConnectDeviceThread(serialno)
                self.t.connectDeviceDone.connect(self.onDeviceConnect)
                self.t.start()
        else:
            print(u'无法获取在线设备列表，请连接设备并打开USB调试后重试')

    def onDeviceConnect(self, serialno, adb):
        if adb:
            print(u'正在获取设备信息')
            self.t = QueryPackageThread(adb)
            self.t.queryPackageDone.connect(self.onPackageQuery)
            self.t.start()
        else:
            print(u'无法连接设备 {0}，请确保该设备唯一在线且处于空闲状态'.format(serialno))

    def onPackageQuery(self, adb, packages):
        print(u'初始设备完成')
        self.child = child.ChildWindow(adb, packages)
        self.mdiArea.addSubWindow(self.child)
        self.child.show()

    def loginAccounts(self):
        pass

    def importData(self):
        pass

    def executeBuildTest(self):
        pass

    def about(self):
        with open(os.path.join(workdir, 'v.txt'), 'r') as f:
            ver = f.readline().strip()
        QMessageBox.about(self, u'关于自动化测试平台',
                u'<p>自动化测试平台提供日常功能及性能测试并支持用例扩展<p>'
                u'<p>技术支持：中兴移动软件一部一科自动化测试小组</p>'
                u'<p>软件版本：{0}'.format(ver))

    def updateMenus(self):
        pass

    def createActions(self):
        self.connectDeviceAct = QAction(u'连接设备', self, shortcut='Ctrl+C',
                statusTip=u'连接在线的设备', triggered=self.connectDevice)
        self.uploadCaseAct = QAction(u'上传用例', self, shortcut='Ctrl+U',
                statusTip=u'上传测试用例至服务器', triggered=self.about)
        self.loginAccountsAct = QAction(u'登录帐号', self, shortcut='Ctrl+L',
                statusTip=u'登录预置的应用帐号', triggered=self.loginAccounts)
        self.loginAccountsAct.setDisabled(True)
        self.importDataAct = QAction(u'导入数据', self, shortcut='Ctrl+I',
                statusTip=u'导入预置的用户数据', triggered=self.importData)
        self.importDataAct.setDisabled(True)
        self.buildTestAct = QAction(u'日常测试', self, shortcut='Ctrl+B',
                statusTip=u'运行自带的功能及性能测试', triggered=self.executeBuildTest)
        self.buildTestAct.setDisabled(True)
        self.extendTestAct = QAction(u'扩展用例', self, shortcut='Ctrl+E',
                statusTip=u'运行扩展和上传的测试用例', triggered=self.about)
        self.extendTestAct.setDisabled(True)
        self.aboutAct = QAction(u'关于', self, shortcut='F1', triggered=self.about)
        self.aboutQtAct = QAction(u'关于Qt', self, triggered=qApp.aboutQt)

    def createMenus(self):
        self.deviceMenu = self.menuBar().addMenu(u'设备(&D)')
        self.deviceMenu.addAction(self.connectDeviceAct)
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

    def createStatusBar(self):
        self.statusBar().showMessage(u'就绪')

    def setActiveSubWindow(self, window):
        if window:
            self.mdiArea.setActiveSubWindow(window)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
