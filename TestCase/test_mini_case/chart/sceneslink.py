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


#生成scenes GPU绘制超链接
def createScenesHype(path):
    filepath = path
    data = []
    rootdir = os.path.join(filepath,'scenes')
    filename = 'gfxinfo.png'
    dirdata = ['ContactTest','DeveloperTest','LauncherTest','MultiTaskTest',\
               'NativeListViewTest','NoteScaleTest','PressMenuTest']
    for i in range(len(dirdata)):
        judge = dataJudge(os.path.join(rootdir,dirdata[i]))
        if judge == 1:
            dirnames = os.path.join('scenes',dirdata[i])
            data.append(os.path.join(dirnames,filename))
        elif judge == 2:
            data.append('Data Deficiencies')
        else:
            data.append('No data')
    return data

#判断GPU数据是否异常
def dataJudge(path):
    filepath = path
    strdata = []
    if os.path.exists(os.path.join(filepath,'gfxinfo.csv')):
        csvfile = file(os.path.join(filepath,'gfxinfo.csv'),'rb')
        reader = csv.reader((line.replace('\0','')for line in csvfile),delimiter = ",");
        for line in reader:
            strdata.append(line)
        size = [x[0] for x in strdata]
        length = len(size)
        if length>50:
            return 1
        elif length < 50:
            return 2
        else:
            return 0
#生成Scenes log 链接
def Scenesloglink(path):
    filepath = path
    outdir = os.path.join(filepath,'scenes')
    filenames=glob.glob(os.path.join(outdir, '*'))
    dirdata = ['ContactTest','DeveloperTest','LauncherTest','MultiTaskTest',\
               'NativeListViewTest','NoteScaleTest','PressMenuTest']
    data = []
    filename = 'gfxinfo.txt'
    for i in range(len(dirdata)):
            dirnames = os.path.join('scenes',dirdata[i])
            files = os.path.join(outdir,dirdata[i])
            if os.path.exists(os.path.join(files,filename)):
                data.append(os.path.join(dirnames,filename))
    return data

def main(path,name):
    #设置字体颜色
    
    #初始化样式
    style1 = xlwt.XFStyle()
    style2 = xlwt.XFStyle()
    style3 = xlwt.XFStyle()
    #为样式创建字体
    font = xlwt.Font()
    font.name = 'Times New Roman'
    font.colour_index= 2
    font.height = 300
    font.bold = True
    
    font1 = xlwt.Font()
    font1.colour_index= 4
    font1.name = 'Times New Roman'
    font1.height = 250
    font1.bold = True

    font2 = xlwt.Font()
    font2.name = 'Times New Roman'
    font2.height = 300
    font2.bold = True
    #为样式设置字体
    style1.font = font
    style2.font = font1
    style3 .font = font2

    filepath = path
    workdir = os.path.dirname(os.path.realpath(sys.argv[0]))
            
    chartdir = os.path.join(workdir,'chart')
    outdir = filepath
    if os.path.exists(os.path.join(outdir,'('+name+')'+'performance.xls')):
        rb = open_workbook(os.path.join(outdir,'('+name+')'+'performance.xls'),formatting_info=True)
        wb = copy(rb)
    else:
        print 'file not exists'

    scenesChartdata = createScenesHype(filepath)
    scenesloglink = Scenesloglink(filepath)
    
    w_sheet1 = wb.get_sheet(1)

    for i in range(0,8):
        w_sheet1.col(i).width = 0x0d00 + 2000

    length7 = len(scenesChartdata)
    length8 = len(scenesloglink)
    
    link = 'HYPERLINK'

    try:            
        for i in range(0,length7):
            if scenesChartdata[i] == 'Data Deficiencies':
                w_sheet1.write(i+1,4,unicode(scenesChartdata[i],'UTF-8'),style2)
            else:
                w_sheet1.write(i+1,4,Formula(link +'("'+scenesChartdata[i]+' ";"chart link")'),style2)
    except IndexError:
        pass
    try:
        for i in range(0,length8):
            w_sheet1.write(i+1,5,Formula(link+'("'+scenesloglink[i]+' ";"log link")'),style2)
    except IndexError:
        pass
    wb.save(os.path.join(outdir,'('+name+')'+'performance.xls'))

if __name__ == '__main__':
    try:
        main(path,name)
    except KeyboardInterrupt:
        pass


