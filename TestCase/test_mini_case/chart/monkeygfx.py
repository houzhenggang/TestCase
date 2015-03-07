# -*- coding: utf-8 -*-
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

class MonkeySkp(object):

      def __init__(self, path, name):
            self.path = path
            self.name = name

            
      def get_gfx_info(self, path):
            data = []
            root_dir = os.path.join(path, 'monkey')
            
            if os.path.exists(os.path.join(root_dir, 'gfxinfo.csv')):
                  csv_file = file(os.path.join(root_dir, 'gfxinfo.csv'), 'rb')
                  reader = csv.reader((line.replace('\0', '')for line in csv_file), delimiter = ',')
                  for line in reader:
                        data.append(line)
            if len(data) > 0:
                  data.pop(0)
            return data
      
      
      #生成monkey GPU绘制超链接
      def monkey_gfx_link(self, path):
          data = []
          dir_data = self.get_package_name(path)
          root_dir = os.path.join(path, 'monkey')
          chart_name = 'gfxinfo.png'
          
          for i in range(len(dir_data)):
              judge = self.data_judge(os.path.join(root_dir, dir_data[i]))
              if judge == 1:
                  dir_names = os.path.join('monkey', dir_data[i])
                  data.append(os.path.join(dir_names, chart_name))
              elif judge == 2:
                  data.append('Data Deficiencies')
              else:
                  data.append('No data')
          return data
      
      #生成GPU绘制log链接
      def gfx_log_link(self, path):
          data = []
          str_data = []
          out_dir = os.path.join(path, 'monkey')
          file_names=glob.glob(os.path.join(out_dir, '*'))
          
          file_name = 'gfxinfo.txt'
          str_data = self.get_package_name(path)
          
          for i in range(len(str_data)):
              dir_name = os.path.join('monkey', str_data[i])
              data.append(os.path.join(dir_name, file_name))
          return data
      
      #判断GPU数据是否异常
      def data_judge(self, path):
          data = []
          if os.path.exists(os.path.join(path, 'gfxinfo.csv')):
              csv_file = file(os.path.join(path, 'gfxinfo.csv'), 'rb')
              reader = csv.reader((line.replace('\0', '')for line in csv_file), delimiter = ',')
              for line in reader:
                  data.append(line)
              size = [x[0] for x in data]
              length = len(size)
              
              if length>50:
                  return 1
              elif length < 50:
                  return 2
              else:
                  return 0
      
      #读取monkey GPU 绘制包名
      def get_package_name(self, path):
          data = []
          str_data = []
          root_dir = os.path.join(path, 'monkey')
          
          if os.path.exists(os.path.join(root_dir, 'gfxinfo.csv')):
              csv_file = file(os.path.join(root_dir, 'gfxinfo.csv'), 'rb')
              reader = csv.reader((line.replace('\0', '')for line in csv_file), delimiter = ',')
              for line in reader:
                  data.append(line)
              str_data = [x[0] for x in data]
              str_data.pop(0)
          return str_data
      
      def write_to_excel(self, path, name):
            #初始化样式
            style = xlwt.XFStyle()
            style1 = xlwt.XFStyle()
            style2 = xlwt.XFStyle()

            f = setfont.Font(0, 220)
            f1 = setfont.Font(6, 220)
            f2 = setfont.Font(2, 220)
            
            #为样式设置字体
            style.font = f.fontset(0, 220)
            style1.font = f1.fontset(6, 220)
            style2.font = f1.fontset(4, 220)
            
            rb = open_workbook(os.path.join(path, '('+name+')'+'performance.xls'), formatting_info=True)
            wb = copy(rb)
            w_sheet = wb.add_sheet('monkeyskp', cell_overwrite_ok=True)
            
            w_sheet.write(0, 1, u'monkey 测试GPU绘制报告', style2)
            
            w_sheet.write(1, 0, u'测试包名', style1)
            w_sheet.write(1, 1, u'绘制卡顿率', style1)
            w_sheet.write(1, 2 , u'图形链接', style1)
            w_sheet.write(1, 3, u'log链接', style1)

            link = 'HYPERLINK'
            
            for i in range(0, 10):
                  w_sheet.col(i).width = 0x0d00 + 2000

            gfx_data = self.get_gfx_info(path)
            chart_data = self.monkey_gfx_link(path)
            log_data = self.gfx_log_link(path)
            
            
            for i in range(len(gfx_data)):
                  for j in range(len(gfx_data[i])):
                        w_sheet.write(i+2, j, gfx_data[i][j], style)
            try:       
              for i in range(len(chart_data)):
                  if chart_data[i] == 'Data Deficiencies':
                      w_sheet.write(i+2, 2, chart_data[i], style2)
                  else:
                      w_sheet.write(i+2, 2, Formula(link +'("'+chart_data[i]+' ";"chart link")'), style2)
            except  IndexError:
                  pass
            
            try:       
              for i in range(len(log_data)):
                      w_sheet.write(i+2, 3, Formula(link +'("'+log_data[i]+' ";"log link")'), style2)
            except  IndexError:
                  pass
                  
            wb.save(os.path.join(path, '('+name+')'+'performance.xls'))
      
def main(path, name):
      ms = MonkeySkp(path, name)
      ms.write_to_excel(path, name) 
      
if __name__=="__main__":
    try:
          main(path,name)
    except KeyboardInterrupt:
          pass
