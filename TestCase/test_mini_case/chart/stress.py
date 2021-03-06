# -*- coding: utf-8 -*-
import os
import csv
import sys
import glob
import xlwt

from xlutils.copy import copy 
from xlrd import open_workbook 
from xlwt import easyxf

import setfont

#读取stress数据
class Stress(object):
      
      def __init__(self, path, name):
            self.path = path
            self.name = name
            self.getstress(path, name)
            
      def getstressdata(self, path):
            data = []
            file_names = glob.glob(os.path.join(path,'*'))

            try:
                  for name in file_names:
                        if os.path.isfile(name):
                              if os.path.exists(os.path.join(path, 'stress.csv')):
                                    csv_file = file(os.path.join(path, 'stress.csv'), 'rb')
                                    reader = csv.reader((line.replace('\0', '')for line in csv_file), delimiter = ',')
                  for line in reader:
                        data.append(line)
            except KeyboardInterrupt:
                  pass
            return data
      
      def getstress(self, path, name):           
            f = setfont.Font(0, 250)
            f1 = setfont.Font(4, 300)
            
            style = xlwt.XFStyle()
            style1 = xlwt.XFStyle()
            
            style.font = f.fontset(0, 250)
            style1.font = f.fontset(4, 300)
            
            try:
                  stress = self.getstressdata(path)     
                  rb = open_workbook(os.path.join(path, '('+name+')'+'performance.xls'), formatting_info=True)       
                  wb = copy(rb) 
                  w_sheet = wb.add_sheet('stress')
                  w_sheet.write(0, 0, u'压力测试报告', style1)
                  
            except KeyboardInterrupt:
                  pass
            try:                  
                  for i in range(0,10):
                        w_sheet.col(i).width = 0x0d00 + 2500    
                 
                  for i in range(len(stress)):
                        for j in range(len(stress[i])):
                                    w_sheet.write(i+1, j, unicode(stress[i][j], 'UTF-8'), style)
            except KeyboardInterrupt:
                  pass
            wb.save(os.path.join(path, '('+name+')'+'performance.xls'))

def main(path,name):
      stress = Stress(path, name)
      
if __name__=="__main__":
      try:
            main(path,name)
      except KeyboardInterrupt:
            pass

      
