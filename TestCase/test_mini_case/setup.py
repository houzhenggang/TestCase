# -*- coding: utf-8 -*-

import py2exe
import matplotlib
import os
import shutil
import sys
import zipfile

from distutils.core import setup
from glob import glob
from os.path import dirname, join

if len(sys.argv) == 1:
    sys.exit(2)

if sys.argv[1] == 'py2exe':
    options = {
        'py2exe': {
            'includes': [
                'matplotlib.backends',
                'matplotlib.figure',
                'pylab',
                'numpy',
                'matplotlib.backends.backend_tkagg'
            ],
            'excludes': [
                '_gtkagg',
                '_tkagg',
                '_agg2',
                '_cairo',
                '_cocoaagg',
                '_fltkagg',
                '_gtk',
                '_gtkcairo'
            ],
            'dll_excludes': [
                'MSVCP90.dll',
                'libgdk-win32-2.0-0.dll',
                'libgobject-2.0-0.dll'
            ]
        }
    }

    data_files = []
    data_files.append(('.', [
        'busybox',
        'config.txt',
        'TestKit.apk',
        'automator.jar',
        'adb.exe',
        'AdbWinApi.dll',
        'AdbWinUsbApi.dll'
    ]))
    data_files.append(('chart', [
        join('chart', 'performance.xls')
    ]))
    data_files.append(('compat', glob(join('compat', '*'))))
    data_files.append(('memory', glob(join('memory', '*'))))
    data_files.append(('monkey', glob(join('monkey', '*'))))
    data_files.append(('scenes', glob(join('scenes', '*'))))
    data_files.append(('stress', glob(join('stress', '*'))))
    data_files.append(('update', glob(join('update', '*'))))

    # add matplotlib data files
    matplotlibdir = dirname(matplotlib.__file__)
    data_files.append((
        'mpl-data',
        glob(join(matplotlibdir, 'mpl-data', '*.*'))
    ))
    data_files.append((
        'mpl-data',
        glob(join(matplotlibdir, 'mpl-data', 'matplotlibrc'))
    ))
    data_files.append((
        join('mpl-data', 'images'),
        glob(join(matplotlibdir, 'mpl-data', 'images', '*.*'))
    ))
    data_files.append((
        join('mpl-data', 'fonts'),
        glob(join(matplotlibdir, 'mpl-data', 'fonts', '*.*'))
    ))

    setup(
        name='testplat',
        version='1.0.0.1',
        console=[{
            'script': 'start.py',
            'icon_resources': [(1, 'logo.ico')]
        }],
        options=options,
        data_files=data_files
    )

    # rename file
    shutil.move(join('dist', 'start.exe'), join('dist', 'TestPlatform.exe'))

if sys.argv[1] in ['dist', 'publish']:
    f = zipfile.ZipFile('dist.zip', 'w', zipfile.ZIP_DEFLATED)
    for dirpath, dirnames, names in os.walk('dist'):
        for name in names:
            f.write(join(dirpath, name))
    f.close()

if sys.argv[1] in ['publish']:
    f = open('config.txt', 'r')
    remote = unicode(f.readlines()[3], 'utf-8').encode('gb2312')
    shutil.copy('dist.zip', remote)
    shutil.copy('sync.bat', remote)
    f.close()
