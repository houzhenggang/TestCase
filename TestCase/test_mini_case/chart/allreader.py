# -*- coding: utf-8 -*-

import os
import csv
import sys
import glob

import setfont

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
        #初始化样式
      style = xlwt.XFStyle()
      style1 = xlwt.XFStyle()
      
      f = setfont.Font(0, 220)
      f1 = setfont.Font(4, 300)
      style.font = f.fontset(0, 220)
      style1.font = f1.fontset(4, 300)
    
      filepath = path
      workdir = os.path.dirname(os.path.realpath(sys.argv[0]))
      chartdir = os.path.join(workdir, 'chart')
    
      monkeydata = get_monkey_info(filepath)
      
      rb = open_workbook(os.path.join(filepath, '('+name+')'+'performance.xls'), formatting_info=True)
      r_sheet = rb.sheet_by_index(0) 
      wb = copy(rb) 
      w_sheet = wb.add_sheet('monkey')
      
      for i in range(0,8):
            w_sheet.col(i).width = 0x0d00 + 2000
      w_sheet.write(0, 0, u'整机Monkey测试报告', style1)
      title = [u'测试随机数', u'预期测试次数', u'实际测试次数', u'测试时间', u'CRASH 次数', u'NOT RESPONDING次数', u'log链接']
      
      try:
            for i in range(len(title)):
                w_sheet.write(1, i, title[i], style)
      except IndexError:
            pass
            
      length2 = len(monkeydata)

      for i in range(0,length2-1):
            for j in range(len(monkeydata[i])):
                  w_sheet.write(i+2, j, unicode(monkeydata[i][j], 'UTF-8'), style)
      wb.save(os.path.join(filepath, '('+name+')'+'performance.xls'))

      
def main(path, name):
      filepath = path
      write_to_excel(filepath, name)
      
if __name__=="__main__":
    try:
          main(path, name)
    except KeyboardInterrupt:
          pass
