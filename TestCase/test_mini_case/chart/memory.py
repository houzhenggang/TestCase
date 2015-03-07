# -*- coding: utf-8 -*-
from __future__ import division
import os
import csv
import sys
import glob
import xlwt

from xlutils.copy import copy 
from xlrd import open_workbook 
from xlwt import easyxf
from xlwt import*

import setfont

reload(sys)
sys.setdefaultencoding('utf8')

class Memory(object):

      def __init__(self, path):
            self.path = path

      def get_memory_info(self, path, file_name):
            data = []
            root_dir = os.path.join(path, 'memory')
            file_names = glob.glob(os.path.join(root_dir, '*'))

            for name in file_names:
                  if os.path.exists(os.path.join(root_dir, file_name)):
                        csv_file = file(os.path.join(root_dir, file_name))
                        reader = csv.reader((line.replace('\0', '')for line in csv_file), delimiter = ',')
                        for line in reader:
                              data.append(line)
                        return data
                  else:
                        return None
                  
      def write_to_excel(self, path, excel_name):
            data = []
            
            f = setfont.Font(0, 250)
            f1 = setfont.Font(4, 300)
            f2 = setfont.Font(2, 250)
            
            style = xlwt.XFStyle()
            style1 = xlwt.XFStyle()
            style2 = xlwt.XFStyle()
            
            style.font = f.fontset(0, 250)
            style1.font = f.fontset(4, 250)
            style2.font = f.fontset(2, 250)

            root_dir = os.path.join(path, 'memory')
            
            if os.path.exists(os.path.join(root_dir, unicode('应用内存占用汇总表', 'utf-8').encode('gb2312')+'.csv')):
                  link = 'HYPERLINK'
                  data = []
                  memdir = os.path.join(path, 'memory')
                              
                  app_data = self.get_memory_info(path, unicode('应用内存占用汇总表', 'utf-8').encode('gb2312')+'.csv')
                  
                  rb = open_workbook(os.path.join(path, '('+excel_name+')'+'performance.xls'), formatting_info=True)
                  wb = copy(rb)
                  w_sheet2 = wb.add_sheet('appmemory')
                  
                  for i in range(0, 10):
                        w_sheet2.col(i).width = 0x0d00 + 3000
                        
                  w_sheet2.write(0, 1, u'应用内存占用测试报告', style1)
                  w_sheet2.write(1, 6, u'图形链接', style)
                  w_sheet2.write(1, 7, u'log链接', style)
                  
                  if os.path.exists(os.path.join(root_dir, unicode('应用内存占用汇总表', 'utf-8').encode('gb2312')+'.csv')):
                        length = len(app_data)
                  else:
                        length = 0

                  for i in range(length):
                        for j in range(len(app_data[i])):
                              w_sheet2.write(i+1, j, unicode(app_data[i][j], 'UTF-8'), style)
                  
                  wb.save(os.path.join(path, '('+excel_name+')'+'performance.xls'))

            if os.path.exists(os.path.join(root_dir, unicode('后台常驻进程及内存占用', 'utf-8').encode('gb2312')+'.csv')):
                  behind_data = self.get_memory_info(path, unicode('后台常驻进程及内存占用', 'utf-8').encode('gb2312')+'.csv')            
                  rb = open_workbook(os.path.join(path, '('+excel_name+')'+'performance.xls'), formatting_info=True)
                  wb = copy(rb)
                  w_sheet = wb.add_sheet('behindMemory')
                  
                  for i in range(0, 10):
                        w_sheet.col(i).width = 0x0d00 + 3000
                  
                  w_sheet.write(0, 1, u'后台常驻进程及内存占用测试报告', style1)
                  
                  if os.path.exists(os.path.join(root_dir, unicode('后台常驻进程及内存占用', 'utf-8').encode('gb2312')+'.csv')):
                        length = len(behind_data)
                  else:
                        length = 0

                  for i in range(length):
                        for j in range(len(behind_data[i])):
                              w_sheet.write(i+1, j, unicode(behind_data[i][j], 'UTF-8'), style)
                  wb.save(os.path.join(path, '('+excel_name+')'+'performance.xls'))
                              
            if os.path.exists(os.path.join(root_dir, unicode('开机启动进程及内存占用', 'utf-8').encode('gb2312')+'.csv')):
                  reboot_data = self.get_memory_info(path, unicode('开机启动进程及内存占用', 'utf-8').encode('gb2312')+'.csv')            
                  rb = open_workbook(os.path.join(path, '('+excel_name+')'+'performance.xls'), formatting_info=True)
                  wb = copy(rb)
                  w_sheet1 = wb.add_sheet('rebootmemory')
                  
                  for i in range(0 , 10):
                        w_sheet1.col(i).width = 0x0d00 + 3000
                        
                  w_sheet1.write(0, 1, u'开机启动进程及内存占用测试报告', style1)
                  
                  if os.path.exists(os.path.join(root_dir, unicode('开机启动进程及内存占用', 'utf-8').encode('gb2312')+'.csv')):
                        length = len(reboot_data)
                  else:
                        length = 0

                  for i in range(length):
                        for j in range(len(reboot_data[i])):
                              w_sheet1.write(i+1, j, unicode(reboot_data[i][j], 'UTF-8'), style)
                  wb.save(os.path.join(path, '('+excel_name+')'+'performance.xls'))

            if os.path.exists(os.path.join(root_dir, unicode('正常开机进程及内存占用', 'utf-8').encode('gb2312')+'.csv')):
                  reboot_data = self.get_memory_info(path, unicode('正常开机进程及内存占用', 'utf-8').encode('gb2312')+'.csv')            
                  rb = open_workbook(os.path.join(path, '('+excel_name+')'+'performance.xls'), formatting_info=True)
                  wb = copy(rb)
                  w_sheet1 = wb.add_sheet('normalmemory')
                  
                  for i in range(0 , 10):
                        w_sheet1.col(i).width = 0x0d00 + 3000
                        
                  w_sheet1.write(0, 1, u'正常开机进程及内存占用', style1)
                  
                  if os.path.exists(os.path.join(root_dir, unicode('正常开机进程及内存占用', 'utf-8').encode('gb2312')+'.csv')):
                        length = len(reboot_data)
                  else:
                        length = 0

                  for i in range(length):
                        for j in range(len(reboot_data[i])):
                              w_sheet1.write(i+1, j, unicode(reboot_data[i][j], 'UTF-8'), style)
                  wb.save(os.path.join(path, '('+excel_name+')'+'performance.xls'))
                              

                  
def main(path, name):

      memory = Memory(path)
      memory.write_to_excel(path, name)

if __name__=="__main__":
      try:
            main(path,name)
      except KeyboardInterrupt:
            pass

      
