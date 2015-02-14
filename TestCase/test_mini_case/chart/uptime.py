# -*- coding: utf-8 -*-

import os
import csv
import sys
import xlwt

from xlutils.copy import copy 
from xlrd import open_workbook 
from xlwt import easyxf 


class UpTime(object):
    
    def __init__(self, path, name):
        self.path = path
        self.name = name
        self.getuptime(path, name)
        
    def getmonkeydata(self, filename):
        data = []
        csv_file = file(filename, 'rb')
        reader = csv.reader((line.replace('\0', '') for line in csv_file), delimiter = ",")
        for line in reader:
            data.append(line)
        return data

    def getuptime(self, path, name):
        #初始化样式
        style = xlwt.XFStyle()
        #为样式创建字体
        font = xlwt.Font()
        font.name = 'Times New Roman'
        font.height = 220
        font.bold = True
        
        style.font = font
        work_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
        chart_dir = os.path.join(work_dir, 'chart')
        
        if os.path.exists(os.path.join(path, 'uptime.csv')):           
            reboot = self.getmonkeydata(os.path.join(path, 'uptime.csv'))
            rb = open_workbook(os.path.join(path, '('+name+')'+'performance.xls'), formatting_info=True)
            wb = copy(rb)
            w_sheet6 = wb.get_sheet(6)

            for i in range(0, 10):
                w_sheet6.col(i).width = 0x0d00 + 2000
            
            try:                
                for i in range(len(reboot)):
                    w_sheet6.write(i, 0, reboot[i][0].decode('UTF-8'), style)
            except IndexError:
                pass
        
            wb.save(os.path.join(path, '('+name+')'+'performance.xls'))
        else:
            pass

def main(path, name):
    uptime = UpTime(path, name)    

if __name__ == '__main__':
    try:
        main(path, name)
    except KeyboardInterrupt:
        pass
        
        
        


    
