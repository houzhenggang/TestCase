# -*- coding: utf-8 -*-
import os
import csv
import sys
import glob
import xlwt
import re

from xlutils.copy import copy 
from xlrd import open_workbook 
from xlwt import easyxf

class Skiinfo(object):

      def __init__(self, path, name):
            self.path = path
            self.name = name

      def getgfxinfo(self, path, pname):
            gfx_data = []            
            root_dir = os.path.join(path, 'scenes')
            file_names = glob.glob(os.path.join(root_dir, '*'))

            for name in file_names:
                  data = []
                  if os.path.isdir(name):                        
                        if os.path.exists(os.path.join(name, 'gfxinfo.csv')):
                              csv_file = file(os.path.join(name, 'gfxinfo.csv'), 'rb')
                              reader = csv.reader((line.replace('\0', '') for line in csv_file),delimiter = ',')
                              for line in reader:
                                    data.append(line)
                              data.pop(0)
                              if len(data) > 0:
                                    gfx_data.append(self.gfxcalculate(data))                                    
                              else:
                                    gfx_data.append(0)
                  csv_file.close()
            self.writetoexcel(path, pname, gfx_data)
                                    
                  
      def gfxcalculate(self, data):
            dict_gfx = {}
            gfx_sum = []
            time_sum = 0

            draw = [x[0] for x in data]
            prepare = [x[1] for x in data]
            process = [x[2] for x in data]
            execute = [x[3] for x in data]
                  
            for i in range(len(draw)):
                  num =float(draw[i].strip())+float(prepare[i].strip())+float(process[i].strip())+float(execute[i].strip())
                  if num > 30:
                        time_sum += 1
            return time_sum

      
      def writetoexcel(self, path, pname, data):
            style = xlwt.XFStyle()
            font = xlwt.Font()
            font.name = 'Times New Roman'
            font.height = 220
            font.bold = True

            style.font = font
            rb = open_workbook(os.path.join(path, '('+pname+')'+'performance.xls'), formatting_info=True)
            wb = copy(rb)
            w_sheet = wb.get_sheet(1)

            for i in range(0, 10):
                  w_sheet.col(i).width = 0x0d00 + 2000
                  
            for i in range(len(data)):
                  w_sheet.write(i+2, 2, data[i], style)
            wb.save(os.path.join(path,'('+pname+')'+'performance.xls'))
      
def main(path,name):
      sk = Skiinfo(path, name)
      sk.getgfxinfo(path, name) 
      
if __name__=="__main__":
      try:
            main(path,name)
      except KeyboardInterrupt:
            pass
      
