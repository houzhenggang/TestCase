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

#判断monkey是否有内存泄露
def MemLeak(path):
    filepath = path
    data = []
    memdata = []
    try:        
        if os.path.exists(os.path.join(filepath,'meminfo.csv')):
            csvfile = file(os.path.join(filepath,'meminfo.csv'))
            reader = csv.reader((line.replace('\0','')for line in csvfile),delimiter = ",");
            for line in reader:
                data.append(line)
            memdata = [x[2] for x in data]
            length = len(memdata)
            if length > 50:
                try:
                    slope = float((int(memdata[length-1])-int(memdata[50]))/int(memdata[50]))
                    if(slope > 0):
                        return True
                    else:
                        return False
                except ZeroDivisionError:
                    pass
            else:
                return False
    except KeyboardInterrupt:
        pass
    
#判断memory数据是否有内存泄露
def memoryTest(path):
    filepath = path
    data = []
    memdata = []
    try:        
        if os.path.exists(os.path.join(filepath,unicode('应用内存占用.csv', 'utf-8').encode('gb2312'))):
            csvfile = file(os.path.join(filepath,unicode('应用内存占用.csv', 'utf-8').encode('gb2312')))
            reader = csv.reader((line.replace('\0','')for line in csvfile),delimiter = ",");
            for line in reader:
                data.append(line)
            memdata = [x[0] for x in data]
            length = len(memdata)
            if length > 50:
                try:
                    slope = float((int(memdata[length-1])-int(memdata[50]))/int(memdata[50]))
                    if(slope > 0):
                        return True                    
                    else:
                        return False
                except ZeroDivisionError:
                    pass
            else:
                return False
    except KeyboardInterrupt:
        pass
    
#生成monkey GPU绘制超链接
def createMonkeyHype(path):
    getMonkeyName(path)
    filepath = path
    data = []
    dirdata = getMonkeyName(filepath)
    rootdir = os.path.join(filepath,'monkey')
    filename = 'gfxinfo.png'
    for i in range(len(dirdata)):
        judge = dataJudge(os.path.join(rootdir,dirdata[i]))
        if judge == 1:
            dirnames = os.path.join('monkey',dirdata[i])
            data.append(os.path.join(dirnames,filename))
        elif judge == 2:
            data.append('Data Deficiencies')
        else:
            data.append('No data')
    return data

#读取monkey GPU 绘制包名
def getMonkeyName(path):
    filepath = path
    data = []
    strdata = []
    rootdir = os.path.join(filepath,'monkey')
    if os.path.exists(os.path.join(rootdir,'gfxinfo.csv')):
        csvfile = file(os.path.join(rootdir,'gfxinfo.csv'),'rb')
        reader = csv.reader((line.replace('\0','')for line in csvfile),delimiter = ",");
        for line in reader:
            data.append(line)
        strdata = [x[0] for x in data]
        strdata.pop(0)
    return strdata

#生成scenes GPU绘制超链接
def createScenesHype(path):
    filepath = path
    data = []
    rootdir = os.path.join(filepath,'scenes')
    filename = 'gfxinfo.png'
    dirdata = scenesPackageName(filepath)
    
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
        
#生成monkey 内存占用超链接
def createMonkeyMemHype(path):
    filepath = path
    outdir = os.path.join(filepath,'monkey')
    filenames=glob.glob(os.path.join(outdir, '*'))
    data = []
    filename = 'meminfo.png'
    for parent,dirnames,filenames in os.walk(outdir):
        for dirname in dirnames:
            strdata = []
            #判断数据是否异常
            if os.path.exists(os.path.join(os.path.join(outdir,dirname),'meminfo.csv')):
                csvfile = file(os.path.join(os.path.join(outdir,dirname),'meminfo.csv'),'rb')
                reader = csv.reader((line.replace('\0','')for line in csvfile),delimiter = ",");
                for line in reader:
                    strdata.append(line)
                size = [x[0] for x in strdata]
                length = len(size)
                if length>50:
                    dirnames = os.path.join('monkey',dirname)
                    data.append(os.path.join(dirnames,filename))
                else:
                    data.append('Data Deficiencies')
            else:
                data.append('No data')
    return data
#生成内存log链接
def Memloglink(path):
    filepath = path
    outdir = os.path.join(filepath,'monkey')
    filenames=glob.glob(os.path.join(outdir, '*'))
    data = []
    filename = 'meminfo.txt'
    for parent,dirnames,filenames in os.walk(outdir):
        for dirname in dirnames:
            dirnames = os.path.join('monkey',dirname)
            data.append(os.path.join(dirnames,filename))
    return data
#生成crash log 链接
def Crashloglink(path):
    filepath = path
    outdir = os.path.join(filepath,'monkey')
    filenames=glob.glob(os.path.join(outdir, '*'))
    data = []
    filename = 'monkey.txt'
    for parent,dirnames,filenames in os.walk(outdir):
        for dirname in dirnames:
            dirnames = os.path.join('monkey',dirname)
            data.append(os.path.join(dirnames,filename))
    return data
#生成Scenes log 链接
def Scenesloglink(path):
    filepath = path
    outdir = os.path.join(filepath,'scenes')
    filenames=glob.glob(os.path.join(outdir, '*'))
    dirdata = scenesPackageName(filepath)
    data = []
    filename = 'gfxinfo.txt'
    for i in range(len(dirdata)):
            dirnames = os.path.join('scenes',dirdata[i])
            files = os.path.join(outdir,dirdata[i])
            if os.path.exists(os.path.join(files,filename)):
                data.append(os.path.join(dirnames,filename))
    return data
    
#生成GPU绘制log链接
def GPUloglink(path):
    filepath = path
    outdir = os.path.join(filepath,'monkey')
    filenames=glob.glob(os.path.join(outdir, '*'))
    data = []
    strdata = []
    filename = 'gfxinfo.txt'

    strdata = getMonkeyName(filepath)
    for i in range(len(strdata)):
        dirname = os.path.join('monkey',strdata[i])
        data.append(os.path.join(dirname,filename))
    return data
#生成整机Monkey测试log链接
def Monkeylink(path):
    filepath = path
    data = []
    filename = 'monkey.txt'
    outdir = os.path.join(filepath,'monkey')
    if os.path.exists(os.path.join(outdir,'monkey.csv')):
        data.append(os.path.join('monkey','monkey.csv'))
    return data

#memory log链接
def memoryLogLink(path):
    filepath = path
    outdir = os.path.join(filepath,'memory')
    data = []
    filename = '应用内存占用.csv'
    name = memPackageName(filepath)
    for i in range(len(name)):
        data.append(os.path.join(os.path.join('memory',name[i]),filename))
    return data

#读取scens应用包名
def scenesPackageName(path):
    filepath = path
    strdata = []
    name = []
    outdir = os.path.join(filepath,'scenes')
    if os.path.exists(os.path.join(outdir,'gfxinfo.csv')):
        csvfile = file(os.path.join(outdir,'gfxinfo.csv'))
        reader = csv.reader((line.replace('\0','')for line in csvfile),delimiter = ",");
        for line in reader:
            strdata.append(line)
        name = [x[0] for x in strdata]
        name.pop(0)
    return name

#读取memory 应用包名 
def memPackageName(path):
    filepath = path
    strdata = []
    name = []
    outdir = os.path.join(filepath,'memory')
    if os.path.exists(os.path.join(outdir,unicode('应用内存占用汇总表.csv','utf-8').encode('gb2312'))):
        csvfile = file(os.path.join(outdir,unicode('应用内存占用汇总表.csv', 'utf-8').encode('gb2312')))
        reader = csv.reader((line.replace('\0','')for line in csvfile),delimiter = ",");
        for line in reader:
            strdata.append(line)
        strdata.pop(0)
        for i in range(len(strdata)):
            if len(strdata[i]) == 0:
                strdata.pop(i)
        name = [x[0] for x in strdata]
    return name

            

#读取包名
def getPackageName(path):
    filepath = path
    rootdir = os.path.join(filepath,'monkey')
    data = []
    for parent,dirnames,filenames in os.walk(rootdir):
        for dirname in dirnames:
            data.append(dirname)
    return data

#memory 内存链接
def memoryChartLink(path):
    filepath = path
    outdir = os.path.join(filepath,'memory')
    filenames=glob.glob(os.path.join(outdir, '*'))
    data = []
    filename = 'meminfo.png'
    packagename = memPackageName(filepath)
    if packagename is not None:
        for i in range(len(packagename)):
            strdata = []
            dirnames = os.path.join('memory',packagename[i])
            if os.path.exists(os.path.join(os.path.join(outdir,packagename[i]),unicode('应用内存占用.csv', 'utf-8').encode('gb2312'))):
                csvfile = file(os.path.join(os.path.join(outdir,packagename[i]),unicode('应用内存占用.csv', 'utf-8').encode('gb2312')),'rb')
                reader = csv.reader((line.replace('\0','')for line in csvfile),delimiter = ",");
                for line in reader:
                    strdata.append(line)
                size = [x[0] for x in strdata]
                size.pop(0)
                nsum = 0
                average = 0
                for i in range(len(size)):
                    nsum = nsum+int(size[i])
                if len(size) is not 0:
                    average = int(nsum/len(size))
                else:
                    average = 0
                length = len(size)
                if (length>50) and (average is not 0):
                    data.append(os.path.join(dirnames,filename))
                elif average == 0:
                    data.append('Run Error')
                else:
                    data.append('Data Deficiencies')
            else:
                data.append('No data')
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
    
    data1 = []
    data2 = []
    
    filepath = path
    workdir = os.path.dirname(os.path.realpath(sys.argv[0]))
    monkeydir = os.path.join(filepath,'monkey')
    memdir = os.path.join(filepath,'memory')
    
    for parent,dirnames,filenames in os.walk(monkeydir):
        for dirname in dirnames:
            flag = MemLeak(os.path.join(monkeydir,dirname))
            data1.append(flag)
    #调用内存数据判断函数memoryTest       
    for parent,dirnames,filenames in os.walk(memdir):
        for dirname in dirnames:
            flag = memoryTest(os.path.join(memdir,dirname))
            data2.append(flag)
        
    chartdir = os.path.join(workdir,'chart')
    outdir = filepath
    if os.path.exists(os.path.join(outdir,'('+name+')'+'performance.xls')):
        rb = open_workbook(os.path.join(outdir,'('+name+')'+'performance.xls'),formatting_info=True)
        wb = copy(rb)
    else:
        print 'file not exists'
        
    package = getPackageName(filepath)
    gfxdata = createMonkeyHype(filepath)
    memdata = createMonkeyMemHype(filepath)
    memlogdata = Memloglink(filepath)
    gpulogdata = GPUloglink(filepath)
    crashlog = Crashloglink(filepath)
    scenesChartdata = createScenesHype(filepath)
    scenesloglink = Scenesloglink(filepath)
    monkeylog = Monkeylink(filepath)       
    if os.path.exists(os.path.join(filepath,'memory')):
        memchartdata = memoryChartLink(filepath)
    else:
        pass
    memorylog = memoryLogLink(filepath)
    
    w_sheet1 = wb.get_sheet(1)
    w_sheet2 = wb.get_sheet(2)
    w_sheet3 = wb.get_sheet(3)
    w_sheet4 = wb.get_sheet(4)
    w_sheet9 = wb.get_sheet(9)
    
    for i in range(0,8):
        w_sheet1.col(i).width = 0x0d00 + 2000
    for i in range(0,8):
        w_sheet2.col(i).width = 0x0d00 + 2500
    for i in range(0,8):
        w_sheet3.col(i).width = 0x0d00 + 2500
    for i in range(0,8):
        w_sheet4.col(i).width = 0x0d00 + 2500
    for i  in range(5,10):
        w_sheet9.col(i).width = 0x0d00 +2000

    length1 = len(crashlog)  
    length2 = len(gfxdata)
    length3 = len(memdata)
    length4 = len(package)
    length5 = len(memlogdata)
    length6 = len(gpulogdata)
    length7 = len(scenesChartdata)
    length8 = len(scenesloglink)
    if os.path.exists(os.path.join(filepath,'memory')):
        length9 = len(memchartdata)
        length10 = len(memorylog)

    
    link = 'HYPERLINK'
    try:
        for i in range(0,length1):
            w_sheet2.write(i+2,7,Formula(link +'("'+crashlog[i]+' ";"log link")'),style2)
    except IndexError:
        pass

    try:       
        for i in range(0,length2):
            if gfxdata[i] == 'Data Deficiencies':
                w_sheet4.write(i+1,2,unicode(gfxdata[i],'UTF-8'),style2)
            else:
                w_sheet4.write(i+1,2,Formula(link +'("'+gfxdata[i]+' ";"chart link")'),style2)
    except  IndexError:
        pass

    try:        
        for i in range(0,length3):
            if data1[i] is True:
                w_sheet3.write(i+1,1,Formula(link +'("'+memdata[i]+' ";"chart link")'),style1)
            elif memdata[i]== 'Data Deficiencies':
                w_sheet3.write(i+1,1,unicode(memdata[i],'UTF-8'),style2)
            else:
                w_sheet3.write(i+1,1,Formula(link +'("'+memdata[i]+' ";"chart link")'),style2)
    except  IndexError:
        pass

    try:            
        for i in range(0,length5):
            w_sheet3.write(i+1,2,Formula(link +'("'+memlogdata[i]+' ";"log link")'),style2)
    except IndexError:
        pass

    try:
        for i in range(0,length6):
            w_sheet4.write(i+1,3,Formula(link +'("'+gpulogdata[i]+' ";"log link")'),style2)
    except IndexError:
        pass

    try:            
        for i in range(0,length4):
            w_sheet3.write(i+1,0,unicode(package[i],'UTF-8'))
    except IndexError:
        pass

    try:            
        for i in range(0,length7):
            if scenesChartdata[i] == 'Data Deficiencies':
                w_sheet1.write(i+1,3,unicode(scenesChartdata[i],'UTF-8'),style2)
            else:
                w_sheet1.write(i+1,3,Formula(link +'("'+scenesChartdata[i]+' ";"chart link")'),style2)
    except IndexError:
        pass
    try:
        for i in range(0,length8):
            w_sheet1.write(i+1,4,Formula(link+'("'+scenesloglink[i]+' ";"log link")'),style2)
    except IndexError:
        pass
    
    try:
        w_sheet1.write(2,7,Formula(link+'("'+monkeylog[0]+' ";"log link")'),style2)
    except IndexError:
        pass
    
    try:
        if os.path.exists(os.path.join(filepath,'memory')):
            for i in range(0,length9):
                if memchartdata[i] == 'Data Deficiencies' or memchartdata[i] == 'Run Error':
                    w_sheet9.write(i+2,6,unicode(memchartdata[i],'UTF-8'),style3)
                elif memchartdata[i] == 'No data':
                    w_sheet9.write(i+2,6,unicode(memchartdata[i],'UTF-8'),style2)
                else:
                    if data2[i] is True:
                        w_sheet9.write(i+2,6,Formula(link +'("'+memchartdata[i]+' ";"chart link")'),style1)
                    else:
                        w_sheet9.write(i+2,6,Formula(link +'("'+memchartdata[i]+' ";"chart link")'),style2)
    except  IndexError:
        pass
    try:
        if os.path.exists(os.path.join(filepath,'memory')):
            for i in range(0,length10):
                w_sheet9.write(i+2,7,Formula(link +'("'+unicode(memorylog[i],'UTF-8')+' ";"log link")'),style2)
    except IndexError:
        pass
    wb.save(os.path.join(outdir,'('+name+')'+'performance.xls'))

if __name__ == '__main__':
    try:
        main(path,name)
    except KeyboardInterrupt:
        pass





