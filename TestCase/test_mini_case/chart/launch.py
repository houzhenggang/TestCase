# -*- coding: cp936 -*-
from xlutils.copy import copy # http://pypi.python.org/pypi/xlutils
from xlrd import open_workbook # http://pypi.python.org/pypi/xlrd
from xlwt import easyxf # http://pypi.python.org/pypi/xlwt
import xlwt
import os
import csv
import sys

def get_launch_data(filename):
    data = []
    csvfile=file(filename, 'rb')
    reader = csv.reader((line.replace('\0', '') for line in csvfile), delimiter = ',')
    for line in reader:
           data.append(line)
    return data

def main(path,name):
    #初始化字体样式    
    style = xlwt.XFStyle()
    #为样式创建字体
    font = xlwt.Font()
    font.name = 'Times New Roman'
    font.height = 220
    font.bold = True
    style.font = font
    
    style1 = xlwt.XFStyle()
    font1 = xlwt.Font()
    font1.name = 'Times New Roman'
    font1.height = 300
    font1.colour_index = 4
    font1.bold = True
    style1.font = font1

    style2 = xlwt.XFStyle()
    font2 = xlwt.Font()
    font2.name = 'Times New Roman'
    font2.height = 220
    font2.colour_index = 2
    font2.bold = True
    style2.font = font2
    
    
    workdir = os.path.dirname(os.path.realpath(sys.argv[0]))
    chartdir = os.path.join(workdir, 'chart')
    appinfo = get_launch_data(os.path.join(path, 'launch.csv'))
    rb = open_workbook(os.path.join(path, '('+name+')'+'performance.xls'), formatting_info=True)
    wb = copy(rb) 
    w_sheet = wb.add_sheet('launch')
    w_sheet.write(0, 0, u'应用启动时间测试报告', style1)
    for i in range(0, 15):
            w_sheet.col(i).width = 0x0d00 + 1000

    for i in range(len(appinfo)):
        for j in range(len(appinfo[i])):
            if appinfo[i][j] == '0':
                w_sheet.write(i+1, j, appinfo[i][j].decode('UTF-8'), style2)
            else:
                w_sheet.write(i+1, j, appinfo[i][j].decode('UTF-8'), style)
    wb.save(os.path.join(path, '('+name+')'+'performance.xls'))
if __name__=="__main__":
    try:
        main(path,name)
    except KeyboardInterrupt:
        pass
        
        


    
