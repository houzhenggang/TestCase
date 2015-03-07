# -*- coding: utf-8 -*-

import os
import csv
import sys
import xlwt
import glob

import xlrd
from xlutils.copy import copy # http://pypi.python.org/pypi/xlutils
from xlrd import open_workbook # http://pypi.python.org/pypi/xlrd
from xlwt import easyxf # http://pypi.python.org/pypi/xlwt
from xlwt import*

import setfont


class MonkeyCrash(object):

    def __init__(self, path, name):
        self.path = path
        self.name = name

    def get_monkey_info(self, path):
        data = []
        list_data = []
        list_dirs = os.walk(path)

        for parent, dirs, files in list_dirs:
            for f in files:
                if 'monkey.csv' in f:
                    data.append(self.get_monkey_data(os.path.join(parent, f)))
        return data

    def get_monkey_data(self, filename):
        data = []
        strdata = []
        csv_file = file(filename, 'rb')
        reader = csv.reader(csv_file)

        for line in reader:
            data.append(line)
        strdata = data[1]
        return strdata
    
    #生成crash log 链接
    def monkey_log(self, path):
        data = []
        filename = 'monkey.txt'
        outdir = os.path.join(path, 'monkey')
        file_names=glob.glob(os.path.join(outdir, '*'))
        
        for parent, dirnames, filenames in os.walk(outdir):
            for dirname in dirnames:
                dirnames = os.path.join('monkey', dirname)
                data.append(os.path.join(dirnames, filename))
        return data

    def get_package_name(self, path):
        data = []
        list_dirs = os.walk(os.path.join(path, 'monkey'))

        for parent, dirs, files in list_dirs:
            for name in dirs:
                data.append(name)
        return data

    def write_to_excel(self, path, pname):

        style = xlwt.XFStyle()
        style1 = xlwt.XFStyle()
        style2 = xlwt.XFStyle()
        
        f = setfont.Font(0, 220)
        f1 = setfont.Font(4, 220)
        f2 = setfont.Font(4, 300)
        
        style.font = f.fontset(0, 220)
        style1.font = f.fontset(4, 220)
        style2.font = f.fontset(4, 300)

        rb = xlrd.open_workbook(os.path.join(path, '('+pname+')'+'performance.xls'), formatting_info=True)
        wb = copy(rb)
        w_sheet = wb.add_sheet('monkeycrash')
        w_sheet.write(0, 2, u'单模块Monkey测试报告', style2)

        for i in range(0, 10):
               w_sheet.col(i).width = 0x0d00 + 3000

        name = self.get_package_name(path)
        title = [u'测试包名', u'测试随机数', u'预期测试次数', u'实际测试次数', u'测试时间', u'CRASH 次数', u'NOT RESPONDING次数', u'log链接']
        loglink = self.monkey_log(path)
        data = self.get_monkey_info(path)
        try:
            for i in range(len(title)):
                w_sheet.write(1, i, title[i], style)
        except IndexError:
            pass

        try:
            for i in range(len(name)):
                w_sheet.write(i+2, 0, name[i], style)
        except IndexError:
            pass        

        try:
            for i in range(len(data)):
                for j in range(len(data[i])):
                    w_sheet.write(i+2, j+1, data[i][j], style)
        except IndexError:
            pass
        link = 'HYPERLINK'
        
        try:
            for i in range(len(loglink)):
                w_sheet.write(i+2,7,Formula(link +'("'+loglink[i]+' ";"log link")'), style1)
        except IndexError:
            pass
        
        wb.save(os.path.join(path, '('+pname+')'+'performance.xls'))
            
def main(path, name):
    mc = MonkeyCrash(path, name)
    mc.write_to_excel(path, name)
    
if __name__=="__main__":
    try:
        main(path, name)
    except KeyboardInterrupt:
        pass
        

