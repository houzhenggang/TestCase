import os
import csv
import sys
import xlwt

from xlutils.copy import copy 
from xlrd import open_workbook
from xlwt import easyxf

class Font(object):

      def __init__(self, color, size):
            self.color = color
            self.size = size
           
      def fontset(self, color, size):
            font = xlwt.Font()
            font.name = 'Times New Roman'
            font.height = size
            font.colour_index = color
            font.bold = True
            return font


