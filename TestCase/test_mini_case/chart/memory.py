# -*- coding: utf-8 -*-
import os
import csv
import sys
import glob
import xlwt
from xlutils.copy import copy 
from xlrd import open_workbook 
from xlwt import easyxf

reload(sys)
sys.setdefaultencoding('utf8')

#读取后台常驻进程及内存占用
def getbehindInfo(path):
      filepath = path
      data = []
      rootdir = os.path.join(filepath,'memory')
      filenames=glob.glob(os.path.join(rootdir, '*'))
      for name in filenames:
            if os.path.exists(os.path.join(rootdir,unicode('后台常驻进程及内存占用', 'utf-8').encode('gb2312')+'.csv')):
                  csvfile = file(os.path.join(rootdir,unicode('后台常驻进程及内存占用', 'utf-8').encode('gb2312')+'.csv'),'rb')
                  reader = csv.reader((line.replace('\0','')for line in csvfile),delimiter = ",");
                  for line in reader:
                        data.append(line)
                  return data
            else:
                  return None
#读取开机启动进程及内存占用
def getrebootInfo(path):
      filepath = path
      data = []
      rootdir = os.path.join(filepath,'memory')
      filenames=glob.glob(os.path.join(rootdir, '*'))
      for name in filenames:
            if os.path.exists(os.path.join(rootdir,unicode('开机启动进程及内存占用', 'utf-8').encode('gb2312')+'.csv')):
                  csvfile = file(os.path.join(rootdir,unicode('开机启动进程及内存占用', 'utf-8').encode('gb2312')+'.csv'),'rb')
                  reader = csv.reader((line.replace('\0','')for line in csvfile),delimiter = ",");
                  for line in reader:
                        data.append(line)
                  return data
            else:
                  return None
#读取应用内存占用汇总表
def getallInfo(path):
      filepath = path
      data = []
      rootdir = os.path.join(filepath,'memory')
      filenames=glob.glob(os.path.join(rootdir, '*'))
      for name in filenames:
            if os.path.exists(os.path.join(rootdir,unicode('应用内存占用汇总表', 'utf-8').encode('gb2312')+'.csv')):
                  csvfile = file(os.path.join(rootdir,unicode('应用内存占用汇总表', 'utf-8').encode('gb2312')+'.csv'),'rb')
                  reader = csv.reader((line.replace('\0','')for line in csvfile),delimiter = ",");
                  for line in reader:
                        data.append(line)
                  return data

def writeToExcel(path,name):
      #设置字体颜色
      #初始化样式
      style1 = xlwt.XFStyle()
      style2 = xlwt.XFStyle()
      #为样式创建字体
      font = xlwt.Font()
      font.name = 'Times New Roman'
      font.height = 220
      font.bold = True
      font1 = xlwt.Font()
      font1.colour_index= 4
      font1.name = 'Times New Roman'
      font1.height = 220
      font1.bold = True
      #为样式设置字体
      style1.font = font
      style2.font = font1
    
      filepath = path
      rootdir = os.path.join(filepath,'memory')
      behind = getbehindInfo(filepath)
      reboot = getrebootInfo(filepath)
      alldata = getallInfo(filepath)
      rb = open_workbook(os.path.join(filepath,'('+name+')'+'performance.xls'),formatting_info=True)
      r_sheet = rb.sheet_by_index(0)
      wb = copy(rb) 
      w_sheet7 = wb.get_sheet(7)
      w_sheet8 = wb.get_sheet(8)
      w_sheet9 = wb.get_sheet(9)

      for i in range(0,10):
            w_sheet7.col(i).width = 0x0d00 + 3000
      for i in range(0,10):
            w_sheet8.col(i).width = 0x0d00 + 3000
      for i in range(0,10):
            w_sheet9.col(i).width = 0x0d00 + 3000
      if os.path.exists(os.path.join(rootdir,unicode('后台常驻进程及内存占用', 'utf-8').encode('gb2312')+'.csv')):       
            length1 = len(behind)
      else:
            length1 = 0
      if os.path.exists(os.path.join(rootdir,unicode('开机启动进程及内存占用', 'utf-8').encode('gb2312')+'.csv')):
            length2 = len(reboot)
      else:
            length2 = 0
      if os.path.exists(os.path.join(rootdir,unicode('应用内存占用汇总表', 'utf-8').encode('gb2312')+'.csv')):
            length3 = len(alldata)
      else:
            length3 = 0
      
      for i in range(length1):
            for j in range(len(behind[i])):
                  w_sheet7.write(i+1,j,unicode(behind[i][j],'UTF-8'),style1)
      for i in range(length2):
            for j in range(len(reboot[i])):
                  w_sheet8.write(i+1,j,unicode(reboot[i][j],'UTF-8'),style1)
      for i in range(length3):
            for j in range(len(alldata[i])):
                  w_sheet9.write(i+1,j,unicode(alldata[i][j],'UTF-8'),style1)
      wb.save(os.path.join(filepath,'('+name+')'+'performance.xls'))
def main(path,name):
      filepath = path
      writeToExcel(filepath,name)

if __name__=="__main__":
      try:
            main(path,name)
      except KeyboardInterrupt:
            pass

      
