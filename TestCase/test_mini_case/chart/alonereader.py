# -*- coding: utf-8 -*-
import os
import csv
import sys
import glob
import xlwt

from xlutils.copy import copy 
from xlrd import open_workbook 
from xlwt import easyxf


def get_gfx_info(path):
      data = []
      root_dir = os.path.join(path, 'monkey')
      
      if os.path.exists(os.path.join(root_dir, 'gfxinfo.csv')):
            csvfile = file(os.path.join(root_dir, 'gfxinfo.csv'),'rb')
            reader = csv.reader((line.replace('\0', '')for line in csvfile), delimiter = ",");
            for line in reader:
                  data.append(line)
      return data


def get_monkey_info(path):
      data = []
      root_dir = os.path.join(path, 'monkey')
      
      if os.path.exists(os.path.join(root_dir, 'skpinfo.csv')):
            csvfile = file(os.path.join(root_dir, 'skpinfo.csv'), 'rb')
            reader = csv.reader((line.replace('\0', '')for line in csvfile), delimiter = ",");
            for line in reader:
                  data.append(line)
      return data


def write_to_excel(path, name):
      #初始化样式
      style = xlwt.XFStyle()
      #为样式创建字体
      font = xlwt.Font()
      font.name = 'Times New Roman'
      font.height = 220
      font.bold = True
      
      #为样式设置字体
      style.font = font
      gfx_data = get_gfx_info(path)
      
      rb = open_workbook(os.path.join(path, '('+name+')'+'performance.xls'), formatting_info=True)
      r_sheet = rb.sheet_by_index(0) 
      wb = copy(rb) 
      w_sheet = wb.get_sheet(4)
      
      for i in range(0, 8):
            w_sheet.col(i).width = 0x0d00 + 2000
      length = len(gfx_data)
      try:            
            for i in range(length):
                  for j in range(len(gfx_data[i])):
                       w_sheet.write(i, j, unicode(gfx_data[i][j], 'UTF-8'), style)
      except IndexError:
            pass
      wb.save(os.path.join(path, '('+name+')'+'performance.xls'))

      
def main(path, name):
      write_to_excel(path, name)
      
if __name__=="__main__":
    try:
          main(path,name)
    except KeyboardInterrupt:
          pass
