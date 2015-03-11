# -*- coding: utf-8 -*-

import glob
import os
import shutil

import adbkit

from PIL import Image

from common import workdir

def hist_similar(lh, rh):
    assert len(lh) == len(rh)
    return sum(1 - (0 if l == r else float(abs(l - r)) / max(l, r)) for l, r in zip(lh, rh)) / len(lh)

def compare(image1, image2):
    return hist_similar(image1.histogram(), image2.histogram())

class Executor(object):

    def __init__(self, adb, workout):
        self.adb = adb
        self.workout = workout

    def title(self):
        return u'截图比较测试'

    def setup(self):
        pass

    def execute(self, log):
        self.workout = os.path.join(self.workout, 'compar')
        shutil.rmtree(self.workout, ignore_errors=True)
        if not os.path.exists(self.workout):
            os.mkdir(self.workout)

        with open(os.path.join(workdir, 'compar', 'config.txt'), 'r') as f:
            respath = f.readlines()[1].strip().encode('gb2312')
        respath = os.path.join(respath, self.adb.getprop('ro.product.model'))

        if os.path.exists(respath):
            log(self.msg(u'正在执行截图'))
            tmppath = '/data/local/tmp/screenshot/out'
            self.adb.shell('rm -rf {0}'.format(tmppath))
            self.adb.shell('mkdir -p {0}'.format(tmppath))
            uia = adbkit.Uia(self.adb, os.path.join(workdir, 'compar', 'CompareTest.jar'))
            uia.runtest('cn.nubia.test.ScreenShot', 'testDemo')
            uia.uninstall()

            log(self.msg(u'正在导出截图'))
            self.adb.pull(tmppath, self.workout)

            log(self.msg(u'正在比较截图'))
            lines = ['Compare Result:']
            for image in glob.glob(os.path.join(respath, '*.png')):
                name = os.path.basename(image)
                screenshot = os.path.join(self.workout, name)
                if os.path.exists(screenshot):
                    image1 = Image.open(image)
                    image1 = image1.crop((0, 470, image1.size[0], image1.size[1]))
                    image2 = Image.open(screenshot)
                    image2 = image2.crop((0, 470, image2.size[0], image2.size[1]))
                    similar = round(compare(image1, image2) * 100, 2)
                    lines.append('compare {0} result: {1}%'.format(name, similar))
                else:
                    lines.append('{0} is not exists'.format(name))

            log(self.msg(u'正在生成结果'))
            with open(os.path.join(self.workout, 'result.txt'), 'w') as f:
                f.write('\n'.join(lines))

    def msg(self, text):
        return u'[{0}] {1}'.format(self.title(), text)
