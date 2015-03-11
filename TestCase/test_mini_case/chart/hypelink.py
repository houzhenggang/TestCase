# -*- coding: UTF-8 -*-
from __future__ import division

import os
import sys
import csv
import glob

import xlwt
from xlwt import*
from xlwt import easyxf
from xlutils.copy import copy
from xlrd import open_workbook

import setfont

class Memory(object):

      def __init__(self, path):
            self.path = path


      def mem_judge(self, path):
            data = []
            mem_data = []

            if os.path.exists(os.path.join(path,unicode('应用内存占用.csv', 'utf-8').encode('gb2312'))):
                  csv_file = file(os.path.join(path,unicode('应用内存占用.csv', 'utf-8').encode('gb2312')))
                  reader = csv.reader((line.replace('\0', '')for line in csv_file), delimiter = ',')
                  for line in reader:
                        data.append(line)
                  memdata = [x[2] for x in data]
                  length = len(memdata)

                  if length > 50:
                        try:
                              slope = float((int(memdata[length - 1]) - int(memdata[50])) / int(memdata[50]))
                              if(slope > 0):
                                    return True
                              else:
                                    return False
                        except ZeroDivisionError:
                              pass
                  else:
                        return False

                  
      def log_link(self, path):
            data = []
            out_dir = os.path.join(path,'memory')
            filename = u'应用内存占用.csv'
            name = self.get_package_name(path)
            for i in range(len(name)):
                data.append(os.path.join(os.path.join('memory', name[i]), filename))
            return data

      
      #读取memory 应用包名 
      def get_package_name(self, path):
            data = []
            name = []
            out_dir = os.path.join(path, 'memory')
            if os.path.exists(os.path.join(out_dir, unicode('应用内存占用汇总表.csv', 'utf-8').encode('gb2312'))):
                csv_file = file(os.path.join(out_dir, unicode('应用内存占用汇总表.csv', 'utf-8').encode('gb2312')))
                reader = csv.reader((line.replace('\0','')for line in csv_file), delimiter = ',')
                for line in reader:
                    data.append(line)
                name = [x[0] for x in data]
                name.pop(0)
            return name

      
      def create_chart_link(self, path):
            data = []
            out_dir = os.path.join(path, 'memory')
            filenames=glob.glob(os.path.join(out_dir, '*'))
            file_name = 'meminfo.png'
            package_name = self.get_package_name(path)
            if package_name is not None:
                for i in range(len(package_name)):
                    strdata = []
                    dirnames = os.path.join('memory', package_name[i])
                    if os.path.exists(os.path.join(os.path.join(out_dir, package_name[i]), unicode('应用内存占用.csv', 'utf-8').encode('gb2312'))):
                        csvfile = file(os.path.join(os.path.join(out_dir, package_name[i]), unicode('应用内存占用.csv', 'utf-8').encode('gb2312')), 'rb')
                        reader = csv.reader((line.replace('\0', '')for line in csvfile), delimiter = ',')
                        for line in reader:
                            strdata.append(line)
                        size = [x[0] for x in strdata]
                        size.pop(0)
                        nsum = 0
                        average = 0
                        for i in range(len(size)):
                            nsum = nsum+int(size[i])
                        if len(size) is not 0:
                            average = int(nsum / len(size))
                        else:
                            average = 0
                        length = len(size)
                        if (length>50) and (average is not 0):
                            data.append(os.path.join(dirnames, file_name))
                        elif average == 0:
                            data.append('Run Error')
                        else:
                            data.append('Data Deficiencies')
                    else:
                        data.append('No data')
                return data
class Scenes(object):

      def __init__(self, path):
            self.path = path

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

      #生成scenes GPU绘制超链接
      def chart_link(self, path):
            data = []
            rootdir = os.path.join(path, 'scenes')
            filename = 'gfxinfo.png'
            package_name = self.get_package_name(path)
          
            for i in range(len(package_name)):
                  judge = self.data_judge(os.path.join(rootdir, package_name[i]))
                  if judge == 1:
                        dirnames = os.path.join('scenes', package_name[i])
                        data.append(os.path.join(dirnames, filename))
                  elif judge == 2:
                        data.append('Data Deficiencies')
                  else:
                        data.append('No data')
            return data

            
      #读取scens应用包名
      def get_package_name(self, path):
            data = []
            name = []
            out_dir = os.path.join(path, 'scenes')
            if os.path.exists(os.path.join(out_dir, 'gfxinfo.csv')):
                  csv_file = file(os.path.join(out_dir,'gfxinfo.csv'))
                  reader = csv.reader((line.replace('\0','')for line in csv_file),delimiter = ",");
                  for line in reader:
                        data.append(line)
                  name = [x[0] for x in data]
                  name.pop(0)
            return name

            
      #生成Scenes log 链接
      def log_link(self, path):
            data = []
            out_dir = os.path.join(path,'scenes')
            dir_data = self.get_package_name(path)
            file_name = 'gfxinfo.txt'
            for i in range(len(dir_data)):
                  dir_names = os.path.join('scenes', dir_data[i])
                  files = os.path.join(out_dir, dir_data[i])
                  if os.path.exists(os.path.join(files, file_name)):
                      data.append(os.path.join(dir_names, file_name))
            return data

      
class Monkey(object):
      def __init__(self, path):
            self.path = path
            
      #生成monkey GPU绘制超链接
      def chart_link(self, path):
            data = []
            dirdata = self.get_package_name(path)
            rootdir = os.path.join(path, 'monkey')
            filename = 'gfxinfo.png'
            
            for i in range(len(dirdata)):
                judge = self.data_judge(os.path.join(rootdir, dirdata[i]))
                if judge == 1:
                    dirnames = os.path.join('monkey', dirdata[i])
                    data.append(os.path.join(dirnames, filename))
                elif judge == 2:
                    data.append('Data Deficiencies')
                else:
                    data.append('No data')
            return data

      #读取monkey GPU 绘制包名
      def get_package_name(self, path):
            data = []
            strdata = []
            rootdir = os.path.join(path, 'monkey')
            if os.path.exists(os.path.join(rootdir, 'gfxinfo.csv')):
                csvfile = file(os.path.join(rootdir, 'gfxinfo.csv'), 'rb')
                reader = csv.reader((line.replace('\0', '')for line in csvfile), delimiter = ',')
                for line in reader:
                    data.append(line)
                strdata = [x[0] for x in data]
                strdata.pop(0)
            return strdata
      
      #判断GPU数据是否异常
      def data_judge(self, path):
            data = []
            if os.path.exists(os.path.join(path, 'gfxinfo.csv')):
                csvfile = file(os.path.join(path, 'gfxinfo.csv'), 'rb')
                reader = csv.reader((line.replace('\0', '')for line in csvfile),delimiter = ',')
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
                  
      #生成crash log 链接
      def crash_log(self, path):
            data = []
            outdir = os.path.join(path, 'monkey')
            filenames=glob.glob(os.path.join(outdir, '*'))
            filename = 'monkey.txt'
            for parent, dirnames, filenames in os.walk(outdir):
                for dirname in dirnames:
                    dirnames = os.path.join('monkey', dirname)
                    data.append(os.path.join(dirnames, filename))
            return data      
      
      #生成GPU绘制log链接
      def gpu_log_link(self, path):
            data = []
            outdir = os.path.join(path,'monkey')
            filenames=glob.glob(os.path.join(outdir, '*'))

            strdata = []
            filename = 'gfxinfo.txt'

            strdata = self.get_package_name(path)
            for i in range(len(strdata)):
                dirname = os.path.join('monkey', strdata[i])
                data.append(os.path.join(dirname, filename))
            return data

def main(path, name):
      f = setfont.Font(0, 250)
      f1 = setfont.Font(4, 250)
      f2 = setfont.Font(2, 250)
      style = xlwt.XFStyle()
      style1 = xlwt.XFStyle()
      style2 = xlwt.XFStyle()
                  
      style.font = f.fontset(0, 250)
      style1.font = f.fontset(4, 250)
      style2.font = f.fontset(2, 250)
      
      link = 'HYPERLINK'
      
      if os.path.exists(os.path.join(path,'('+name+')'+'performance.xls')):
            rb = open_workbook(os.path.join(path, '('+name+')'+'performance.xls'), formatting_info=True)
            wb = copy(rb)
      else:
            print 'file not exists'

      workdir = os.path.dirname(os.path.realpath(sys.argv[0]))

      #memory
      if os.path.exists(os.path.join(path, 'memory')):
            data = []
            memdir = os.path.join(path, 'memory')
            memory = Memory(path)
            
            #调用内存数据判断
            for parent, dirnames, filenames in os.walk(memdir):
                  for dirname in dirnames:
                        flag = memory.mem_judge(os.path.join(memdir, dirname))
                        data.append(flag)
                        
            mem_chart_link = memory.create_chart_link(path)
            mem_log_link = memory.log_link(path)

            w_sheet_mem = wb.get_sheet(2)

            for i in range(10):
                  w_sheet_mem.col(i).width = 0x0d00 + 2000

            try:
                  for i in range(len(mem_chart_link)):
                        if data[i] is True:
                              w_sheet_mem.write(i+2, 6, Formula(link +'("'+mem_chart_link[i]+' ";"chart link")'), style2)
                        elif data[i]== 'Data Deficiencies':
                            w_sheet_mem.write(i+2, 6, unicode(mem_chart_link[i], 'UTF-8'), style1)
                        else:
                            w_sheet_mem.write(i+2, 6, Formula(link +'("'+mem_chart_link[i]+' ";"chart link")'), style1)
            except  IndexError:
                  pass
            try:
                  for i in range(len(mem_log_link)):
                        w_sheet_mem.write(i+2, 7, Formula(link +'("'+mem_log_link[i]+' ";"log link")'), style1)
            except  IndexError:
                  pass
      #scenes    
      if os.path.exists(os.path.join(path, 'scenes')):
            scenes = Scenes(path)
            scenes_chart_link = scenes.chart_link(path)
            scenes_log_link = scenes.log_link(path)

            w_sheet_scenes = wb.get_sheet(1)
            for i in range(10):
                  w_sheet_scenes.col(i).width = 0x0d00 + 2000

            try:
                  for i in range(len(scenes_chart_link)):
                        if scenes_chart_link[i] == 'Data Deficiencies':
                              w_sheet_scenes.write(i+2,3,unicode(scenes_chart_link[i],'UTF-8'), style)
                        else:
                              w_sheet_scenes.write(i+2, 3, Formula(link +'("'+scenes_chart_link[i]+' ";"chart link")'), style1)
            except IndexError:
                  pass

            try:
                  for i in range(len(scenes_log_link)):
                        w_sheet_scenes.write(i+2, 4, Formula(link +'("'+scenes_chart_link[i]+' ";"log link")'), style1)
            except IndexError:
                  pass
      #monkey
      if os.path.exists(os.path.join(path, 'monkey')):
            if os.path.exists(os.path.join(os.path.join(path, 'monkey'), 'monkey.csv')):
                  pass
            else:
                  monkey = Monkey(path)
                  crash_log = monkey.crash_log(path)
                  chart_link = monkey.chart_link(path)
                  gpu_log = monkey.gpu_log_link(path)

                  if os.path.exists(os.path.join(path, 'memory')):
                        w_sheet_crash = wb.get_sheet(6)
                        w_sheet_gpu = wb.get_sheet(7)
                  else:
                        w_sheet_crash = wb.get_sheet(2)
                        w_sheet_gpu = wb.get_sheet(3)
                  for i in range(10):
                        w_sheet_crash.col(i).width = 0x0d00 + 2000
                        w_sheet_gpu.col(i).width = 0x0d00 + 2000
                  try:
                        for i in range(len(crash_log)):
                              w_sheet_crash.write(i+2, 7, Formula(link +'("'+crash_log[i]+' ";"log link")'), style1)
                  except IndexError:
                        pass

                  try:
                        for i in range(len(chart_link)):
                              w_sheet_gpu.write(i+2, 2, Formula(link +'("'+chart_link[i]+' ";"chart link")'), style1)
                              w_sheet_gpu.write(i+2, 3, Formula(link +'("'+gpu_log[i]+' ";"log link")'), style1)
                  except IndexError:
                        pass
            
      wb.save(os.path.join(path,'('+name+')'+'performance.xls'))

if __name__ == '__main__':
    try:
        main(path,name)
    except KeyboardInterrupt:
        pass

            
            

                        
                        
            
            
