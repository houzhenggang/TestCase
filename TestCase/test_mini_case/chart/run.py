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
import alonemonkey
import monkeygfx
import monkeygpuchart
import monkeymemchart
import scenesgpuchart
import memory
import memchart
import skinfo
import gfxinfo
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
            if os.path.exists(os.path.join(workdir, 'scenes')):                  
                  scenesgpuchart.main(workdir)
                  gfxinfo.main(workdir, name)
                  skinfo.main(workdir, name)                    
      except KeyboardInterrupt:
            pass
      try:
            if os.path.exists(os.path.join(workdir, 'memory')):
                  memory.main(workdir, name)
                  memchart.getData(workdir)
      except KeyboardInterrupt:
            pass

      try:
            if os.path.exists(os.path.join(workdir, 'monkey')):
                  if os.path.exists(os.path.join(os.path.join(workdir, 'monkey'), 'monkey.csv')):
                        allreader.main(workdir, name)
                  else:
                        monkeygpuchart.main(workdir)
                        monkeymemchart.getData(workdir)
                        alonemonkey.main(workdir, name)
                        monkeygfx.main(workdir, name)

      except KeyboardInterrupt:
            pass
                  
      try:
            if os.path.exists(os.path.join(workdir, 'stress.csv')):
                  stress.main(workdir, name)
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
            hypelink.main(workdir, name)
            print 'ok'
      except KeyboardInterrupt:
            pass
      print 'alltest finish'
      
            
            

      
            
