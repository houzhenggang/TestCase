# -*- coding: utf-8 -*-
import os
import csv
import sys
import glob
import xlwt
from xlutils.copy import copy 
from xlrd import open_workbook 
from xlwt import easyxf

def getGfxInfo(path):
      filepath = path
      data = []
      str = []
      rootdir = os.path.join(filepath, 'scenes')
      if os.path.exists(os.path.join(rootdir, 'gfxinfo.csv')):
            csvfile = file(os.path.join(rootdir, 'gfxinfo.csv'), 'rb')
            reader = csv.reader((line.replace('\0', '')for line in csvfile), delimiter = ",")
            for line in reader:
                  data.append(line)
      if len(data) > 0:
            data.pop(0)
      return data

def writeToExcel(path,name,data=[]):
      #初始化样式
      style = xlwt.XFStyle()
      style1 = xlwt.XFStyle()
      #为样式创建字体
      font = xlwt.Font()
      font.name = 'Times New Roman'
      font.height = 220
      font.bold = True

      font1 = xlwt.Font()
      font1.name = 'Times New Roman'
      font1.height = 220
      font1.color_index = 2
      font1.bold = True
      #为样式设置字体
      style.font = font
      style1.font = font1
      
      filepath = path
      workdir = os.path.dirname(os.path.realpath(sys.argv[0]))
      chartdir = os.path.join(workdir,'chart')
      rb = open_workbook(os.path.join(filepath,'('+name+')'+'performance.xls'),formatting_info=True)
      r_sheet = rb.sheet_by_index(0) 
      wb = copy(rb) 
      w_sheet = wb.get_sheet(1)
      for i in range(0,8):
            w_sheet.col(i).width = 0x0d00 + 2000
      length=len(data)
      standard = [1.5,1.4,1.5,1.8,3.6,1.8,1.8,1.5,2.4]   
      for i in range(0,length):
            w_sheet.write(i+1,0,data[i][0], style)
            tmp = str(data[i][1]).replace('%','')
            if float(tmp) > float(standard[i]):
                  w_sheet.write(i+1,1,data[i][1]+'   warn',style)
            else:
                  w_sheet.write(i+1,1,data[i][1],style1)
      wb.save(os.path.join(filepath,'('+name+')'+'performance.xls'))
def main(path,name):
      filepath = path
      data = getGfxInfo(filepath)
      writeToExcel(filepath,name,data)
if __name__=="__main__":
      try:
            main(path,name)
      except KeyboardInterrupt:
            pass
      
