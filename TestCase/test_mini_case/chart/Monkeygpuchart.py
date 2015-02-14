# -*- coding: cp936 -*-
import xlrd
import sys
import os
import csv
import glob

import matplotlib
import numpy as np
import matplotlib.backends
import matplotlib.pyplot as plt
from matplotlib.pyplot import savefig

import Scenesgpuchart
    
def getmonkeydata(path):
    rootdir = os.path.join(path, 'monkey')
    file_names = glob.glob(os.path.join(rootdir, '*'))
    for name in file_names:
        data = []
        if os.path.isdir(name):
            if os.path.exists(os.path.join(name, 'gfxinfo.csv')):
                csvfile = file(os.path.join(name, 'gfxinfo.csv'), 'rb')
                reader = csv.reader((line.replace('\0', '')for line in csvfile), delimiter = ",")
                for line in reader:
                    data.append(line)
                makechart = Scenesgpuchart.MakeGPUChart(name, data)
                makechart.makechart(name, data)
                
def main(path):
    getmonkeydata(path)
        
if __name__ == '__main__':
    try:
        main(path)
    except KeyboardInterrupt:
        pass   
