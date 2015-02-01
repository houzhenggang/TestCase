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

from common import workdir, getconfig

if pyqtlib:
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
            self.setWindowTitle(u'自动化测试平台升级')
            self.setWindowIcon(QIcon('logo.png'))

        def showEvent(self, event):
            t = threading.Thread(target=main, args=(self.onProgressUpdate,))
            t.start()

        def closeEvent(self, event):
            event.ignore()

        def onProgressUpdate(self, value, text):
            self.pbar.setValue(value)
            self.status.setText(text)
            time.sleep(0.5)
            if value >= 100:
                sys.exit(2)

def main(updatecallback=None):
    # download dist file
    if updatecallback:
        updatecallback(10, u'正在下载升级包')
    distfile = os.path.join(getconfig(3).encode('gb2312'), 'dist.zip')
    if os.name == 'nt':
        subprocess.Popen('copy \"{0}\" \"{1}\"'.format(distfile, workdir), shell=True).wait()
    else:
        shutil.copy(distfile, workdir)

    # unzip dist file
    if updatecallback:
        updatecallback(40, u'正在解压缩升级包')
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
    if updatecallback:
        updatecallback(90, u'正在删除升级包')
    os.remove(distfile)

    # startup
    if updatecallback:
        updatecallback(100, u'升级完成')
    if len(sys.argv) > 1 and sys.argv[1] == 'start':
        subprocess.Popen('\"{0}\" {1}'.format(os.path.join(workdir, 'TestPlatform')))

if __name__ == '__main__':
    if pyqtlib:
        app = QApplication(sys.argv)
        dlg = UpdateDialog()
        dlg.show()
        sys.exit(app.exec_())
    else:
        main()
