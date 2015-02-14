# -*- coding: utf-8 -*-

import xlrd
import sys
import os
import csv
import glob

import matplotlib
import numpy as np
import matplotlib.backends
import matplotlib.pyplot as plt

from matplotlib import pylab as pl
from matplotlib.pyplot import savefig


class MakeGPUChart(object):

    def __init__(self, path, data):
        self.path = path
        self.data = data

    def makechart(self, path,data):
        standard = [16]*len(data)
        draw = [x[0] for x in data]
        prepare = [x[1] for x in data]
        process = [x[2] for x in data]
        execute = [x[3] for x in data]
        time = [x[4] for x in data]
        
        draw.pop(0)
        prepare.pop(0)
        process.pop(0)
        execute.pop(0)

        if len(draw) == len(process) and len(draw) == len(execute):
            for i in range(len(draw)):
                prepare[i] = float(prepare[i])+float(draw[i])
                process[i] = float(process[i])+float(prepare[i])
                execute[i] = float(execute[i]) + float(process[i])
            time_len = len(time)

        try:
            if time_len > 10:            
                #declare a figure object to plot
                fig = plt.figure(figsize=(12,8))
                fig.patch.set_color("r")
                fig.canvas.draw()
                #plot chart
                plt.plot(standard, label = 'Standard', linewidth = 2,color = 'green')
                plt.plot(draw, label = 'Draw', linewidth = 2,color = 'blue')
                plt.plot(prepare,label = 'Prepare',linewidth = 2,color = 'magenta')
                plt.plot(process, label = 'Process', linewidth = 2,color = 'red') 
                plt.plot(execute, label = 'Execute', linewidth = 2,color = 'orange')
                plt.xlabel(u'时间(单位：s)', fontproperties='SimHei')
                plt.ylabel(u'绘制时间（单位：ms）', fontproperties='SimHei')
                plt.xlim(0, int(time[time_len-1]))
                plt.ylim(0, 100)
                #plt.ylabel(u'内存大小',fontproperties='SimHei')
                plt.grid(True)
                #advance settings
                plt.title('GPU Chart')
                #show the figure
                plt.legend(loc=2, bbox_to_anchor=(1.01,1.00), borderaxespad=0.)
                plt.legend()
                #save chart
                workdir = os.path.dirname(sys.argv[0])
                plt.savefig(os.path.join(path, 'gfxinfo.png'))
                #plt.show()
        except KeyboardInterrupt:
                pass

def getscenes(path):
    root_dir = os.path.join(path, 'scenes')
    file_names = glob.glob(os.path.join(root_dir, '*'))

    for name in file_names:
        data = []
        if os.path.isdir(name):
            if os.path.exists(os.path.join(name, 'gfxinfo.csv')):
                csv_file = file(os.path.join(name, 'gfxinfo.csv'), 'rb')
                reader = csv.reader((line.replace('\0', '')for line in csv_file), delimiter = ',')
                for line in reader:
                    data.append(line)
                chart = MakeGPUChart(name, data)
                chart.makechart(name, data)
def main(path):
    getscenes(path)
        
if __name__ == '__main__':
    try:
        main(path)
    except KeyboardInterrupt:
        pass   
