# -*- coding: utf-8 -*-
import os
import csv
import sys

import xlwt
from xlutils.copy import copy 
from xlrd import open_workbook 
from xlwt import easyxf 

import setfont

def get_monkey_data(filename):
    data = []
    csvfile=file(filename, 'rb')
    reader = csv.reader((line.replace('\0', '') for line in csvfile), delimiter = ",");  
    for line in reader:
           data.append(line)
    return data


def main(path, name):
          
    f = setfont.Font(0, 200)
    f1 = setfont.Font(4, 200)
    f2 = setfont.Font(2, 300)
      
    style = xlwt.XFStyle()
    style1 = xlwt.XFStyle()
    style2 = xlwt.XFStyle()
                  
    style.font = f.fontset(0, 200)
    style1.font = f.fontset(2, 200)
    style2.font = f.fontset(4, 300)

    cam_data= get_monkey_data(os.path.join(path, 'compat.csv'))
    
    rb = open_workbook(os.path.join(path, '('+name+')'+'performance.xls'), formatting_info=True)
    wb = copy(rb) 
    w_sheet = wb.add_sheet('compat')
    w_sheet.col(0).width = 0x0d00 +2500
    
    for i in range(1, 15):
            w_sheet.col(i).width = 0x0d00 + 1000
    length = len(cam_data)
    w_sheet.write(0, 0, u'兼容性测试报告', style2)

    try:
        for i in range(length):
            for j in range(len(cam_data[i])):
                if cam_data[i][j] == 'Fail':
                    w_sheet.write(i+1, j, cam_data[i][j].decode('UTF-8'), style1)
                else:
                    w_sheet.write(i+1, j, cam_data[i][j].decode('UTF-8'), style)
                
                    
    except IndexError:
        pass
    wb.save(os.path.join(path, '('+name+')'+'performance.xls'))

    
if __name__=="__main__":
    try:
        main(path, name)
    except KeyboardInterrupt:
        pass
        
        


    
