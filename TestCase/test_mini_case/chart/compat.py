# -*- coding: utf-8 -*-
import os
import csv
import sys

import xlwt
from xlutils.copy import copy # http://pypi.python.org/pypi/xlutils
from xlrd import open_workbook # http://pypi.python.org/pypi/xlrd
from xlwt import easyxf # http://pypi.python.org/pypi/xlwt


def get_monkey_data(filename):
    data = []
    csvfile=file(filename, 'rb')
    reader = csv.reader((line.replace('\0', '') for line in csvfile), delimiter = ",");  
    for line in reader:
           data.append(line)
    return data


def main(path, name):
    #初始化字体样式    
    style = xlwt.XFStyle()
    #为样式创建字体
    font = xlwt.Font()
    font.name = 'Times New Roman'
    font.height = 200
    font.bold = True
    
    style.font = font

    cam_data= get_monkey_data(os.path.join(path, 'compat.csv'))
    
    rb = open_workbook(os.path.join(path, '('+name+')'+'performance.xls'), formatting_info=True)
    wb = copy(rb) 
    w_sheet5 = wb.get_sheet(5)
    w_sheet5.col(0).width = 0x0d00 +2500
    
    for i in range(1,15):
            w_sheet5.col(i).width = 0x0d00 + 1000
    length5 = len(cam_data)

    try:
        for i in range(length5):
            for j in range(len(cam_data[i])):
                w_sheet5.write(i+1, j, cam_data[i][j].decode('UTF-8'), style)
    except IndexError:
        pass
    wb.save(os.path.join(path, '('+name+')'+'performance.xls'))

    
if __name__=="__main__":
    try:
        main(path, name)
    except KeyboardInterrupt:
        pass
        
        


    
