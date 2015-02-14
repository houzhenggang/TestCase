# -*- coding: UTF-8 -*-
from __future__ import division
from xlutils.copy import copy
from xlrd import open_workbook 
from xlwt import easyxf
from xlwt import*
import xlwt
import os
import sys
import csv
import glob

#生成sences超链接
def createSencesHype(path):
    filepath = path
    data = []
    rootdir = os.path.join(filepath,'scenes')
    filename = 'gfxinfo.png'
    for parent,dirnames,filenames in os.walk(rootdir):
        for dirname in dirnames:
            strdata = []
            #判断数据是否异常
            if os.path.exists(os.path.join(os.path.join(rootdir,dirname),'gfxinfo.csv')):
                csvfile = file(os.path.join(os.path.join(rootdir,dirname),'gfxinfo.csv'),'rb')
                reader = csv.reader((line.replace('\0','')for line in csvfile),delimiter = ",");
                for line in reader:
                    strdata.append(line)
                draw = [x[0] for x in strdata]
                length = len(draw)
                if length > 50:
                    dirnames = os.path.join('scenes',dirname)
                    data.append(os.path.join(dirnames,filename))
                else:
                    data.append('数据不足')
            else:
                    data.append('无数据')
    return data

#生成GPU绘制log链接
def GPUloglink(path):
    filepath = path
    outdir = os.path.join(filepath,'scenes')
    filenames=glob.glob(os.path.join(outdir, '*'))
    data = []
    filename = 'gfxinfo.txt'
    for parent,dirnames,filenames in os.walk(outdir):
        for dirname in dirnames:
            dirnames = os.path.join('scenes',dirname)
            data.append(os.path.join(dirnames,filename))
    return data

def main(path):
    #设置字体颜色
    style2 = xlwt.XFStyle()
    font1 = xlwt.Font()
    font1.colour_index= 4
    font1.name = 'Times New Roman'
    font1.height = 250
    font1.bold = True
    #为样式设置字体
    style2.font = font1
    data = []                     
    filepath = path
    workdir = os.path.dirname(os.path.realpath(sys.argv[0]))
    outdir = filepath
    if os.path.exists(os.path.join(outdir,'performance.xls')):
        rb = open_workbook(os.path.join(outdir,'performance.xls'))
        wb = copy(rb)
    else:
        print 'file not exists'
        
    sendata = createSencesHype(filepath)
    gpulogdata = GPUloglink(filepath)
    
    w_sheet1 = wb.get_sheet(1)
    for i in range(0,8):
        w_sheet1.col(i).width = 0x0d00 + 2000

    length1 = len(sendata)
    length2 = len(gpulogdata)
    
    link = 'HYPERLINK'
    for i in range(0,length1):
        if sendata[i].decode('GBK') == '数据不足'.decode('GBK'):
            w_sheet1.write(i+1,4,unicode(sendata[i], 'UTF-8'),style2)
        else:
            w_sheet1.write(i+1,4,Formula(link +'("'+sendata[i]+' ";"chart link")'),style2)
    for i in range(0,length2):
        w_sheet1.write(i+1,5,Formula(link +'("'+gpulogdata[i]+' ";"log link")'),style2)
    wb.save(os.path.join(outdir,'performance.xls'))

if __name__ == '__main__':
    try:
        main(path)
    except KeyboardInterrupt:
        pass





