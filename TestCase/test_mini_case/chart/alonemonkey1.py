# -*- coding: utf-8 -*-

import os
import csv
import sys
import xlwt

from xlutils.copy import copy # http://pypi.python.org/pypi/xlutils
from xlrd import open_workbook # http://pypi.python.org/pypi/xlrd
from xlwt import easyxf # http://pypi.python.org/pypi/xlwt


def get_monkey_info(rootDir):
    list_monkey=[]
    counter=1
    data=[]
    list_dirs = os.walk(rootDir)
    for root, dirs, files in list_dirs:
        for f in files: 
            if 'monkey.csv' in f:
                data.append(get_monkey_data(os.path.join(root, f)))
    return data


def get_monkey_data(filename):
    str=[]
    csvfile=file(filename, 'rb')
    reader=csv.reader(csvfile)    
    for line in reader:
           str.append(line)
    data=str[1]
    return data


def write_to_excel(path, name, data=[]):
    #设置字体
    style = xlwt.XFStyle()
    font = xlwt.Font()
    font.name = 'Times New Roman'
    font.height = 250
    font.bold = True
    
    #为样式设置字体 
    style.font = font
    
    filepath = os.path.dirname(os.path.realpath(sys.argv[0]))
    workdir = os.path.join(filepath, 'chart')
    try:        
        rb = open_workbook(os.path.join(path, '('+name+')'+'performance.xls'), formatting_info=True)
        r_sheet = rb.sheet_by_index(0)    
        wb = copy(rb) 
        w_sheet = wb.get_sheet(2)
    except StandardError:
        pass    
    for i in range(0, 8):
        w_sheet.col(i).width = 0x0d00 + 2000
    length=len(data)

    try:
        for i in range(length):
            for j in range(len(data[i])):
                w_sheet.write(i+2, j+1, data[i][j], style)
    except IndexError:
        pass
    wb.save(os.path.join(path, '('+name+')'+'performance.xls'))

    
def main(path, name):
    data = get_monkey_info(path)
    write_to_excel(path, name, data)

    
if __name__=="__main__":
    try:
        main(path, name)
    except KeyboardInterrupt:
        pass
        

