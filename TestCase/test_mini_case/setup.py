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
    with open('v.txt', 'r') as f:
        version = f.readline().strip()

    options = {
        'py2exe': {
            'includes': [
                'matplotlib.backends',
                'matplotlib.backends.backend_qt4agg',
                'matplotlib.figure',
                'pylab',
                'numpy',
                'PIL.Image',
                'sip'
            ],
            'excludes': [
                '_gtkagg',
                '_tkagg',
                '_agg2',
                '_cairo',
                '_cocoaagg',
                '_fltkagg',
                '_gtk',
                '_gtkcairo',
                'tcl',
                'Tkconstants',
                'Tkinter'
            ],
            'dll_excludes': [
                'MSVCP90.dll',
                'libgdk-win32-2.0-0.dll',
                'libgobject-2.0-0.dll',
                'tcl85.dll',
                'tk85.dll'
            ]
        }
    }

    data_files = []
    data_files.append(('.', [
        'busybox',
        'main.sh',
        'config.txt',
        'TestKit.apk',
        'automator.jar',
        'adb.exe',
        'aapt.exe',
        'AdbWinApi.dll',
        'AdbWinUsbApi.dll',
        'logo.png',
        'v.txt'
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
    data_files.append(('compar', glob(join('compar', '*'))))
    data_files.append(('images', glob(join('images', '*'))))

    # add matplotlib data files
    #data_files.extend(matplotlib.get_py2exe_datafiles())
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
        join('mpl-data', 'stylelib'),
        glob(join(matplotlibdir, 'mpl-data', 'stylelib', '*.*'))
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
        version=version,
        console=[{
            'script': 'start.py',
            'icon_resources': [(1, 'logo.ico')]
        }],
        windows=[{
            'script': 'upgrade.py',
            'icon_resources': [(1, 'logo.ico')]
        }],
        options=options,
        data_files=data_files
    )

    # rename files
    shutil.move(join('dist', 'start.exe'), join('dist', 'TestPlatform.exe'))
    shutil.move(join('dist', 'upgrade.exe'), join('dist', 'PlatformUpdate.exe'))

if sys.argv[1] in ['dist', 'publish']:
    f = zipfile.ZipFile('dist.zip', 'w', zipfile.ZIP_DEFLATED)
    for dirpath, dirnames, names in os.walk('dist'):
        if not dirpath == join('dist', 'out'):
            for name in names:
                zippath = os.sep.join(dirpath.split(os.sep)[1:])
                f.write(join(dirpath, name), join(zippath, name))
    f.close()

if sys.argv[1] in ['publish']:
    f = open('config.txt', 'r')
    remote = unicode(f.readlines()[3].strip(), 'utf-8').encode('gb2312')
    shutil.copy('dist.zip', remote)
    shutil.copy('sync.bat', remote)
    f.close()
