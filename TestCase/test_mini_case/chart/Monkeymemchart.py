# -*- coding: cp936 -*-
import xlrd
import sys
import os
import csv
import glob
from matplotlib import *
from matplotlib import pylab
import numpy as np
import matplotlib
import matplotlib.backends
import matplotlib.pyplot as plt
from matplotlib.pyplot import savefig

def makeChart(path,data):
    filepath = path
    #get datas
    size = [x[0] for x in data]
    alloc = [x[1] for x in data]
    free = [x[2] for x in data]
    length = len(size)
    #drop the 1st line of the data, which is the name of the data.
    size.pop(0)
    alloc.pop(0)
    free.pop(0)
    try:
        if length >10:        
            #declare a figure object to plot
            fig = plt.figure(figsize=(12,8))
            #plot chart
            plt.plot(size,label = 'Total')
            plt.plot(alloc,label = 'Alloc') 
            plt.plot(free,label = 'Free')
            plt.xlabel(u'次数(单位：20S)',fontproperties='SimHei')
            #plt.ylabel('Memory')
            plt.xlim(0.0,len(data))
            plt.ylabel(u'内存大小（单位：KB）',fontproperties='SimHei')
            plt.grid(True)
            #advance settings
            plt.title('Native Heap')
            #show the figure
            plt.legend(loc=2,bbox_to_anchor=(1.01,1.00),borderaxespad=0.)
            plt.legend()
            #save chart
            workdir = os.path.dirname(sys.argv[0])
            plt.savefig(os.path.join(filepath,'meminfo.png'))
            #plt.show()
    except KeyboardInterrupt:
        pass
    
def getData(path):
    filepath = path
    rootdir = os.path.join(filepath,'monkey')
    filenames = glob.glob(os.path.join(rootdir,'*'))
    for name in filenames:
        data = []
        if os.path.isdir(name):
            if os.path.exists(os.path.join(name,'meminfo.csv')):
                csvfile = file(os.path.join(name,'meminfo.csv'),'rb')
                reader = csv.reader((line.replace('\0','')for line in csvfile),delimiter = ",")
            for line in reader:
                data.append(line)
            makeChart(name,data)
        
if __name__ == '__main__':
    try:
        getData(path)
    except KeyboardInterrupt:
        pass   
