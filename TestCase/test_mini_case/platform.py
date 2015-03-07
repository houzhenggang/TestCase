# -*- coding: utf-8 -*-

import os
import subprocess
import sys
import zipfile

import adbkit
import executor

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from common import workdir, getconfig

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

class QueryUpdateThread(QThread):

    queryUpdateDone = pyqtSignal(str, str)

    def __init__(self):
        super(QueryUpdateThread, self).__init__()

    def run(self):
        remote = getconfig(3).encode('gb2312')
        exefile = 'PlatformUpdate.exe' if sys.platform == 'win32' else 'PlatformUpdate'

        if os.path.exists(remote):
            with zipfile.ZipFile(os.path.join(remote, 'dist.zip')) as zf:
                newver = zf.open('v.txt').readline().strip()
                with open(os.path.join(workdir, exefile), 'wb') as f:
                    f.write(zf.read(exefile))
            with open(os.path.join(workdir, 'v.txt'), 'r') as f:
                locver = f.readline().strip()

            self.queryUpdateDone.emit(locver, newver)

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.initUI()
        self.update()

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
        self.createToolBars()
        self.createStatusBar()
        self.updateMenus()

        self.readSettings()

        self.setWindowTitle(u'自动化测试平台开发版')
        self.setWindowIcon(QIcon('logo.png'))
        self.setUnifiedTitleAndToolBarOnMac(True)

    def closeEvent(self, event):
        self.mdiArea.closeAllSubWindows()
        if self.mdiArea.currentSubWindow():
            event.ignore()
        else:
            self.writeSettings()
            event.accept()

    def connectDevice(self):
        self.qdt = QueryDeviceThread()
        self.qdt.queryDeviceDone.connect(self.onDeviceQuery)
        self.qdt.start()

    def onDeviceQuery(self, devices):
        if devices:
            if len(devices) == 1:
                serialno = devices[0]
            else:
                item, ok = QInputDialog.getItem(self, u'选择设备', u'设备列表：', devices, 0, False)
                serialno = item if ok and item else None

            if serialno:
                self.statusLabel.setText(u'正在连接设备 {0}'.format(serialno))
                self.cdt = ConnectDeviceThread(serialno)
                self.cdt.connectDeviceDone.connect(self.onDeviceConnect)
                self.cdt.start()
        else:
            QMessageBox.information(self, u'提示', u'无法获取在线设备列表，请连接设备并打开USB调试后重试')

    def onDeviceConnect(self, serialno, adb):
        if adb:
            self.qpt = QueryPackageThread(adb)
            self.qpt.queryPackageDone.connect(self.onPackageQuery)
            self.qpt.start()
        else:
            QMessageBox.information(self, u'提示', u'无法连接设备 {0}，请确保该设备唯一在线且处于空闲状态'.format(serialno))

    def onPackageQuery(self, adb, packages):
        self.statusLabel.clear()
        mdiChild = self.createMdiChild(adb, packages)
        mdiChild.show()

    def onUpdateQuery(self, locver, newver):
        y = lambda x: [int(i) for i in x.split('.')]
        if y(newver) > y(locver) and QMessageBox.question(self, u'升级',
                u'<p><b>发现新版本!</b></p><p>是否要从当前版本 {0} 升级至新版本 {1}</p>'.format(locver, newver),
                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            subprocess.Popen('\"{0}\" start'.format(os.path.join(workdir, 'PlatformUpdate')))
            sys.exit(2)

    def loginAccounts(self):
        if self.activeMdiChild():
            self.activeMdiChild().loginAccounts()

    def importData(self):
        if self.activeMdiChild():
            self.activeMdiChild().importData()

    def executeBuildTest(self):
        if self.activeMdiChild():
            self.activeMdiChild().executeBuildTest()

    def update(self):
        self.qut = QueryUpdateThread()
        self.qut.queryUpdateDone.connect(self.onUpdateQuery)
        self.qut.start()

    def about(self):
        with open(os.path.join(workdir, 'v.txt'), 'r') as f:
            ver = f.readline().strip()
        QMessageBox.about(self, u'关于自动化测试平台',
                u'<p>自动化测试平台提供日常功能及性能测试并支持用例扩展<p>'
                u'<p>技术支持：中兴移动软件一部一科自动化测试小组</p>'
                u'<p>平台版本：{0}'.format(ver))

    def updateMenus(self):
        hasMdiChild = (self.activeMdiChild() is not None)
        self.loginAccountsAct.setEnabled(hasMdiChild)
        self.importDataAct.setEnabled(hasMdiChild)
        self.buildTestAct.setEnabled(hasMdiChild)
        self.backupRestoreAct.setEnabled(hasMdiChild)
        self.separatorAct.setVisible(hasMdiChild)

    def updateWindowMenu(self):
        self.windowMenu.clear()
        self.windowMenu.addAction(self.closeAct)
        self.windowMenu.addAction(self.closeAllAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.tileAct)
        self.windowMenu.addAction(self.cascadeAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.nextAct)
        self.windowMenu.addAction(self.previousAct)
        self.windowMenu.addAction(self.separatorAct)

        windows = self.mdiArea.subWindowList()
        self.separatorAct.setVisible(len(windows) != 0)

        for i, window in enumerate(windows):
            child = window.widget()

            text = '%d %s' % (i + 1, child.userFriendlyCurrentDevice())
            if i < 9:
                text = '&' + text

            action = self.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child is self.activeMdiChild())
            action.triggered.connect(self.windowMapper.map)
            self.windowMapper.setMapping(action, window)

    def createMdiChild(self, adb, packages):
        mdiChild = executor.ChildWindow(adb, packages)
        self.mdiArea.addSubWindow(mdiChild)
        return mdiChild

    def createActions(self):
        self.connectDeviceAct = QAction(QIcon('./images/android.png'), u'连接设备', self,
                shortcut='Ctrl+C',
                statusTip=u'连接在线的设备',
                triggered=self.connectDevice)

        self.loginAccountsAct = QAction(QIcon('./images/lock.png'), u'登录帐号', self,
                shortcut='Ctrl+L',
                statusTip=u'登录预置的应用帐号',
                triggered=self.loginAccounts)
        self.importDataAct = QAction(QIcon('./images/data.png'), u'导入数据', self,
                shortcut='Ctrl+I',
                statusTip=u'导入预置的用户数据',
                triggered=self.importData)
        self.buildTestAct = QAction(QIcon('./images/run.png'), u'测试用例', self,
                shortcut='Ctrl+X',
                statusTip=u'执行内置及扩展的测试用例',
                triggered=self.executeBuildTest)

        self.backupRestoreAct = QAction(u'备份还原', self,
                statusTip=u'备份还原存储卡')

        self.closeAct = QAction("Cl&ose", self,
                statusTip="Close the active window",
                triggered=self.mdiArea.closeActiveSubWindow)
        self.closeAllAct = QAction("Close &All", self,
                statusTip="Close all the windows",
                triggered=self.mdiArea.closeAllSubWindows)
        self.tileAct = QAction("&Tile", self,
                statusTip="Tile the windows",
                triggered=self.mdiArea.tileSubWindows)
        self.cascadeAct = QAction("&Cascade", self,
                statusTip="Cascade the windows",
                triggered=self.mdiArea.cascadeSubWindows)
        self.nextAct = QAction("Ne&xt", self,
                shortcut=QKeySequence.NextChild,
                statusTip="Move the focus to the next window",
                triggered=self.mdiArea.activateNextSubWindow)
        self.previousAct = QAction("Pre&vious", self,
                shortcut=QKeySequence.PreviousChild,
                statusTip="Move the focus to the previous window",
                triggered=self.mdiArea.activatePreviousSubWindow)
        self.separatorAct = QAction(self)
        self.separatorAct.setSeparator(True)

        self.updateAct = QAction(u'升级', self,
                triggered=self.update)
        self.aboutAct = QAction(u'关于', self,
                shortcut='F1',
                triggered=self.about)
        self.aboutQtAct = QAction(u'关于Qt', self,
                triggered=qApp.aboutQt)

    def createMenus(self):
        self.deviceMenu = self.menuBar().addMenu(u'设备(&D)')
        self.deviceMenu.addAction(self.connectDeviceAct)

        self.runMenu = self.menuBar().addMenu(u'运行(&R)')
        self.runMenu.addAction(self.loginAccountsAct)
        self.runMenu.addAction(self.importDataAct)
        self.runMenu.addSeparator()
        self.runMenu.addAction(self.buildTestAct)

        self.toolMenu = self.menuBar().addMenu(u'工具(&T)')
        self.toolMenu.addAction(self.backupRestoreAct)

        self.windowMenu = self.menuBar().addMenu(u'窗口(&W)')
        self.updateWindowMenu()
        self.windowMenu.aboutToShow.connect(self.updateWindowMenu)

        self.helpMenu = self.menuBar().addMenu(u'帮助(&H)')
        self.helpMenu.addAction(self.updateAct)
        self.helpMenu.addSeparator()
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

    def createToolBars(self):
        self.deviceToolBar = self.addToolBar('Device')
        self.deviceToolBar.addAction(self.connectDeviceAct)

        self.runToolBar = self.addToolBar('Run')
        self.runToolBar.addAction(self.loginAccountsAct)
        self.runToolBar.addAction(self.importDataAct)
        self.runToolBar.addAction(self.buildTestAct)

    def createStatusBar(self):
        self.statusLabel = QLabel()
        self.statusBar().addPermanentWidget(self.statusLabel)
        self.statusBar().showMessage(u'就绪')

    def readSettings(self):
        settings = QSettings('ZTEMT', 'TestPlatform')
        pos = settings.value('pos', QPoint(200, 200))
        size = settings.value('size', QSize(600, 400))
        self.move(pos.toPyObject())
        self.resize(size.toPyObject())

    def writeSettings(self):
        settings = QSettings('ZTEMT', 'TestPlatform')
        settings.setValue('pos', self.pos())
        settings.setValue('size', self.size())

    def activeMdiChild(self):
        activeSubWindow = self.mdiArea.activeSubWindow()
        if activeSubWindow:
            return activeSubWindow.widget()
        return None

    def setActiveSubWindow(self, window):
        if window:
            self.mdiArea.setActiveSubWindow(window)
