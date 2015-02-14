# -*- coding: utf-8 -*-

import os
import csv
import sys
import glob

import xlwt
from xlutils.copy import copy
from xlrd import open_workbook 
from xlwt import easyxf

def  get_package_name(path):
      data = []
      work_dir = os.path.join(path, 'monkey')
      list_dir = os.listdir(work_dir)
      length = len(list_dir)
      for i in range(length-2):
            data.append(list_dir[i])
      return data


def write_package_to_excel(path, name):
      #设置字体
      style = xlwt.XFStyle()
      font = xlwt.Font()
      font.name = 'Times New Roman'
      font.height = 250
      font.bold = True   
      #为样式设置字体
      style.font = font
      
      package = get_package_name(path)
      
      rb = open_workbook(os.path.join(path, '('+name+')'+'performance.xls'), formatting_info=True)
      r_sheet = rb.sheet_by_index(2) 
      wb = copy(rb) 
      w_sheet = wb.get_sheet(2) 
      length=len(package)

      try:
            for i in range(length):
                  w_sheet.write(i+2,0,package[i], style)
      except IndexError:
            pass
      wb.save(os.path.join(path, '('+name+')'+'performance.xls'))

      
def main(path, name):
      write_package_to_excel(path, name)

      
if __name__ == '__main__':
      try:
            main(path, name)
      except KeyboardInterrupt:
            pass
