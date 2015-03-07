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

def getgfxinfo(path):
      data = []
      rootdir = os.path.join(path, 'scenes')
      if os.path.exists(os.path.join(rootdir, 'gfxinfo.csv')):
            csvfile = file(os.path.join(rootdir, 'gfxinfo.csv'), 'rb')
            reader = csv.reader((line.replace('\0', '')for line in csvfile), delimiter = ',')
            for line in reader:
                  data.append(line)
      if len(data) > 0:
            data.pop(0)
      return data


def writetoexcel(path, name, data=[]):
      #初始化样式
      style = xlwt.XFStyle()
      style1 = xlwt.XFStyle()
      style2 = xlwt.XFStyle()

      f = setfont.Font(0, 220)
      f1 = setfont.Font(4, 220)
      f2 = setfont.Font(4, 220)
      
      #为样式设置字体
      style.font = f.fontset(0, 220)
      style1.font = f1.fontset(4, 300)
      style2.font = f2.fontset(6, 220)
      
      rb = open_workbook(os.path.join(path, '('+name+')'+'performance.xls'), formatting_info=True)
      wb = copy(rb)
      
      w_sheet = wb.get_sheet(1)
      w_sheet.write(0, 0, u'流畅性测试报告', style1)
      w_sheet.write(1, 0, u'测试项目', style2)
      w_sheet.write(1, 1, u'绘制卡顿率', style2)
      w_sheet.write(1, 2, u'丢帧次数', style2)
      w_sheet.write(1, 3, u'图形链接', style2)
      w_sheet.write(1, 4, u'log 链接', style2)
      
      for i in range(0, 8):
            w_sheet.col(i).width = 0x0d00 + 2000
            
      #standard = [1.5,1.4,1.5,1.8,3.6,1.8,1.8,1.5,2.4]   
      for i in range(len(data)):
            for j in range(len(data[i])):
                  w_sheet.write(i+2, j, data[i][j], style)
            '''w_sheet.write(i+1,0,data[i][0], style)
            tmp = str(data[i][1]).replace('%','')
            if float(tmp) > float(standard[i]):
                  w_sheet.write(i+1,1,data[i][1]+'   warn',style)
            else:
                  w_sheet.write(i+1,1,data[i][1],style1)'''
      wb.save(os.path.join(path, '('+name+')'+'performance.xls'))

      
def main(path, name):
      data = getgfxinfo(path)
      writetoexcel(path, name, data)
      
      
if __name__=="__main__":
      try:
            main(path,name)
      except KeyboardInterrupt:
            pass
      
