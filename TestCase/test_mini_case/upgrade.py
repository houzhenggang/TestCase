# -*- coding: utf-8 -*-

import os
import shutil
import subprocess
import sys
import threading
import time
import zipfile

try:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *
    pyqtlib = True
except ImportError:
    pyqtlib = False

if pyqtlib:
    class UpdateThread(QThread):

        progressUpdate = pyqtSignal(int, unicode)

        def __init__(self):
            super(UpdateThread, self).__init__(None)

        def run(self):
            main(self.progressUpdate)

    class UpdateDialog(QDialog):

        def __init__(self, parent=None):
            super(UpdateDialog, self).__init__(parent)
            self.initUI()

        def initUI(self):
            self.pbar = QProgressBar(self)
            self.pbar.setTextVisible(False)
            self.status = QLabel(u'就绪')

            vbox = QVBoxLayout()
            vbox.setSizeConstraint(QLayout.SetMaximumSize)
            vbox.addStretch(1)
            vbox.addWidget(self.pbar)
            vbox.addWidget(self.status)
            vbox.addStretch(1)

            self.setLayout(vbox)
            self.resize(250, 120)
            self.setWindowTitle(u'自动化测试平台升级程序')
            self.setWindowIcon(QIcon('logo.png'))

        def showEvent(self, event):
            self.t = UpdateThread()
            self.t.progressUpdate.connect(self.onProgressUpdate)
            self.t.start()

        def closeEvent(self, event):
            event.ignore()

        def onProgressUpdate(self, progress, status):
            self.pbar.setValue(progress)
            self.status.setText(status)
            time.sleep(0.5)
            if progress >= 100:
                QCoreApplication.instance().quit()

def main(updatesignal=None):
    workdir = os.path.dirname(os.path.realpath(sys.argv[0]))

    # download dist file
    if updatesignal:
        updatesignal.emit(10, u'正在下载升级包')
    with open(os.path.join(workdir, 'config.txt'), 'r') as f:
        remote = unicode(f.readlines()[3].strip(), 'utf-8').encode('gb2312')
    distfile = os.path.join(remote, 'dist.zip')
    if os.name == 'nt':
        subprocess.Popen('copy \"{0}\" \"{1}\"'.format(distfile, workdir), shell=True).wait()
    else:
        shutil.copy(distfile, workdir)

    # unzip dist file
    if updatesignal:
        updatesignal.emit(40, u'正在解压缩升级包')
    distfile = os.path.join(workdir, 'dist.zip')
    zf = zipfile.ZipFile(distfile)
    for name in zf.namelist():
        filename = os.path.join(workdir, name)
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        try:
            f = open(filename, 'wb')
            f.write(zf.read(name))
            f.close()
        except IOError as e:
            print e
    zf.close()

    # delete dist file
    if updatesignal:
        updatesignal.emit(90, u'正在删除升级包')
    os.remove(distfile)

    # startup
    if updatesignal:
        updatesignal.emit(100, u'升级完成')
    if len(sys.argv) > 1 and sys.argv[1] == 'start':
        subprocess.Popen('\"{0}\"'.format(os.path.join(workdir, 'TestPlatform')))

if __name__ == '__main__':
    if pyqtlib:
        app = QApplication(sys.argv)
        dlg = UpdateDialog()
        dlg.show()
        sys.exit(app.exec_())
    else:
        main()
