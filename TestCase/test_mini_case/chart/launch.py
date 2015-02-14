# -*- coding: cp936 -*-
from xlutils.copy import copy # http://pypi.python.org/pypi/xlutils
from xlrd import open_workbook # http://pypi.python.org/pypi/xlrd
from xlwt import easyxf # http://pypi.python.org/pypi/xlwt
import xlwt
import os
import csv
import sys

def getMonkeyDataFromCsv(filename):
    csvfile=file(filename,'rb')
    reader = csv.reader((line.replace('\0','') for line in csvfile),delimiter = ",");  
    str=[]
    for line in reader:
           str.append(line)
    return str

def main(path,name):
    #初始化字体样式    
    style = xlwt.XFStyle()
    #为样式创建字体
    font = xlwt.Font()
    font.name = 'Times New Roman'
    font.height = 220
    font.bold = True
    style.font = font
    
    filepath = path
    workdir = os.path.dirname(os.path.realpath(sys.argv[0]))
    chartdir = os.path.join(workdir,'chart')
    appinfo = getMonkeyDataFromCsv(os.path.join(filepath,'launch.csv'))
    rb = open_workbook(os.path.join(filepath,'('+name+')'+'performance.xls'),formatting_info=True)
    wb = copy(rb) 
    w_sheet0 = wb.get_sheet(0)
    for i in range(0,15):
            w_sheet0.col(i).width = 0x0d00 + 1000
    length1 = len(appinfo)
    for i in range(length1):
        for j in range(len(appinfo[i])):
            w_sheet0.write(i,j,appinfo[i][j].decode('UTF-8'),style)
    wb.save(os.path.join(filepath,'('+name+')'+'performance.xls'))
if __name__=="__main__":
    try:
        main(path,name)
    except KeyboardInterrupt:
        pass
        
        


    
