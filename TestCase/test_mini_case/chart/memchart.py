# -*- coding: cp936 -*-
import xlrd
import os
import csv
import glob
import matplotlib
from matplotlib import pylab
import numpy as np
import matplotlib.backends
import matplotlib.pyplot as plt
from matplotlib.pyplot import savefig
import sys

def makeChart(path,data):
    filepath = path
    #set Agg for save picture
     
    #get data
    
    psstotal = [x[0] for x in data]
    pssprivate = [x[1] for x in data]
    dalvikheap = [x[2] for x in data]
    dalvikused = [x[3] for x in data]
    nativeheap = [x[4] for x in data]
    nativeused = [x[5] for x in data]
    
    length = len(psstotal)
    
    #drop the 1st line of the data, which is the name of the data.
    psstotal.pop(0)
    pssprivate.pop(0)
    dalvikheap.pop(0)
    dalvikused.pop(0)
    nativeheap.pop(0)
    nativeused.pop(0)
    nsum = 0
    for i in range(len(psstotal)):
        nsum = nsum+int(psstotal[i])
    if len(psstotal) is not 0:
        average = int(nsum/len(psstotal))
        standard = [average]*len(psstotal)
    else:
        print 'ZeroDivisionError'
        
    try:
        if length >10:        
            #declare a figure object to plot
            fig = plt.figure(figsize=(16,12))
            
            #plot chart
            plt.plot(standard,label = 'average',color = 'k',linewidth=2)
            plt.plot(psstotal,label = 'psstotal',color = 'r')
            plt.plot(pssprivate,label = 'pssprivate',color = 'g') 
            plt.plot(dalvikheap,label = 'dalvikheap',color = 'b')
            plt.plot(dalvikused,label = 'dalvikused',color = 'y')
            plt.plot(nativeheap,label = 'nativeheap',color = 'm')
            plt.plot(nativeused,label = 'nativeused',color = 'c')
            
            plt.xlabel(u'次数(单位：2S)',fontproperties='SimHei')
            #plt.ylabel('Memory')
            plt.xlim(0.0,len(data))
            plt.ylabel(u'内存大小(单位：KB)',fontproperties='SimHei')
            plt.grid(True)
            #advance settings
            plt.title(u'内存占用',fontproperties='SimHei')
            #show the figure
            plt.legend(loc=2,bbox_to_anchor=(1.01,1.00),borderaxespad=0.)
            plt.legend()
            #save chart
            workdir = os.path.dirname(sys.argv[0])
            plt.savefig(os.path.join(filepath,'meminfo.png'))
            #plt.show()
        else:
            print 'memory data lack'
    except KeyboardInterrupt:
        pass
    
def getData(path):
    filepath = path
    rootdir = os.path.join(filepath,'memory')
    filenames = glob.glob(os.path.join(rootdir,'*'))
    for name in filenames:
        data = []
        if os.path.isdir(name):
            if os.path.exists(os.path.join(name,'应用内存占用.csv')):
                csvfile = file(os.path.join(name,'应用内存占用.csv'),'rb')
                reader = csv.reader((line.replace('\0','')for line in csvfile),delimiter = ",")
                for line in reader:
                    data.append(line)
                makeChart(name,data)
            else:
                pass
        
if __name__ == '__main__':
    try:
        getData(path)
    except KeyboardInterrupt:
        pass   
