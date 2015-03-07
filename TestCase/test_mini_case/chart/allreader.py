# -*- coding: utf-8 -*-

import os
import csv
import sys
import glob

import xlwt
from xlutils.copy import copy 
from xlrd import open_workbook 
from xlwt import easyxf

def get_monkey_info(path):
      filepath = path
      data = []
      rootdir = os.path.join(filepath, 'monkey')
      filenames = glob.glob(os.path.join(rootdir, '*'))
      if os.path.exists(os.path.join(rootdir, 'monkey.csv')):
            csvfile = file(os.path.join(rootdir, 'monkey.csv'), 'rb')
            reader = csv.reader((line.replace('\0', '')for line in csvfile), delimiter = ",");
            for line in reader:
                  data.append(line)
            data.pop(0)
      return data


def write_to_excel(path, name):
      
      #设置字体
      style = xlwt.XFStyle()
      font = xlwt.Font()
      font.name = 'Times New Roman'
      font.height = 250
      font.bold = True   
      #为样式设置字体 
      style.font = font
    
      filepath = path
      workdir = os.path.dirname(os.path.realpath(sys.argv[0]))
      chartdir = os.path.join(workdir, 'chart')
    
      monkeydata = get_monkey_info(filepath)
      
      rb = open_workbook(os.path.join(filepath, '('+name+')'+'performance.xls'), formatting_info=True)
      r_sheet = rb.sheet_by_index(0) 
      wb = copy(rb) 
      w_sheet2 = wb.add_sheet('monkey')
      
      for i in range(0,8):
            w_sheet2.col(i).width = 0x0d00 + 2000
            
      length2 = len(monkeydata)

      for i in range(0,length2-1):
            for j in range(len(monkeydata[i])):
                  w_sheet2.write(i+2, j+1, unicode(monkeydata[i][j], 'UTF-8'), style)
      wb.save(os.path.join(filepath, '('+name+')'+'performance.xls'))

      
def main(path, name):
      filepath = path
      write_to_excel(filepath, name)
      
if __name__=="__main__":
    try:
          main(path, name)
    except KeyboardInterrupt:
          pass
