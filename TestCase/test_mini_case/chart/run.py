# -*- coding: cp936 -*-
import os
import xlrd
import xlwt
import xlutils
import sys

from xlrd import open_workbook
from xlutils.copy import copy
from xlwt import easyxf

import stress
import compat  #读取compat/compatibility/launch
import launch
import uptime
import allreader       #整机monkey读取monkey下gfxinfo/monkeyinfo
import alonereader
import alonemonkey
import alonemonkey1
import reader2      #读取scens下gfxinfo
import Monkeygpuchart
import Monkeymemchart
import Scenesgpuchart
import ScenesLogLink
import memory
import memchart
import skinfo
import hypelink     #超链接生成

def run(workout):
      workdir = workout
      name = os.path.basename(workdir)
      chartdir = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'chart')
      
      try:
            if not os.path.exists(os.path.join(workdir, '('+name+')'+'performace.xls')):
                  wb = open_workbook(os.path.join(chartdir, 'performance.xls'), formatting_info=True)
                  rb = copy(wb)
                  rb.save(os.path.join(workdir, '('+name+')'+'performance.xls'))
            else:
                  print 'file already exists'
                  
      except KeyboardInterrupt:
            pass
                  
      try:
            if os.path.exists(os.path.join(workdir, 'stress.csv')):
                  stress.main(workdir, name)
      except KeyboardInterrupt:
            pass
      
      try:
            if os.path.exists(os.path.join(workdir, 'memory')):
                  memory.main(workdir, name)
                  memchart.getData(workdir)
      except KeyboardInterrupt:
            pass
      
      try:
            if os.path.exists(os.path.join(workdir, 'compat.csv')):
                  compat.main(workdir, name)
      except KeyboardInterrupt:
            pass
      
      try:
            if os.path.exists(os.path.join(workdir, 'launch.csv')):
                  launch.main(workdir, name)
      except KeyboardInterrupt:
            pass
      
      try:
            if os.path.exists(os.path.join(workdir, 'uptime.csv')):
                  uptime.main(workdir, name)
      except KeyboardInterrupt:
            pass
      
      try:
            if os.path.exists(os.path.join(workdir,'scenes')):                  
                  reader2.main(workdir, name)
                  skinfo.main(workdir, name)
                  Scenesgpuchart.main(workdir)
                  
      except KeyboardInterrupt:
            pass
      
      try:
            if os.path.exists(os.path.join(workdir, 'monkey')):
                  if os.path.exists(os.path.join(os.path.join(workdir, 'monkey'), 'monkey.csv')):
                        allreader.main(workdir, name)
                  else:
                        alonereader.main(workdir, name)
                        alonemonkey.main(workdir, name)
                        alonemonkey1.main(workdir, name)
                        Monkeygpuchart.main(workdir)
                        Monkeymemchart.getData(workdir)
      except KeyboardInterrupt:
            pass
      
      try:
            hypelink.main(workdir, name)
            print 'ok'
      except KeyboardInterrupt:
            pass
      print 'alltest finish'
      
            
            

      
            
            


      
