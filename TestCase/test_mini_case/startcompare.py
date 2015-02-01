# -*- coding: utf-8 -*-
import os
import sys
import shutil
import CopyFile
from PIL import Image

reload(sys)
sys.setdefaultencoding('utf8')

workdir = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'screenshot')
remotedir = open(os.path.join(workdir, 'config.txt'), 'r')
rootdir = remotedir.readlines()[1].strip()
remotedir.close()

def cutImage(path,filename):
    img = Image.open(os.path.join(path,filename))
    img_size = img.size
    
    width = img_size[0]
    height = img_size[1]
    #剪切图片
    region = (0,470,width,height)
    img_copy = img.crop(region)
    img_copy.save(os.path.join(path,filename))
    
def cut(path):
    img_path = path    
    for parent,dirnames,filenames in os.walk(img_path):
        for filename in filenames:
            cutImage(img_path,filename)

def make_regalur_image(img, size=(256, 256)): 
    return img.resize(size).convert('RGB') 

def hist_similar(lh, rh): 
    assert len(lh) == len(rh) 
    return sum(1 - (0 if l == r else float(abs(l - r)) / max(l, r)) for l, r in zip(lh, rh)) / len(lh)

def compare(filepath1, filepath2):
    image1 = Image.open(filepath1)
    image2 = Image.open(filepath2)
    ret = hist_similar(image1.histogram(), image2.histogram()) 
    return ret

def WriteStrToFile(filename, content):
    f = open(filename, 'w+')
    f.write(content)
    f.close()

def makedir():
    source_file = os.path.join(unicode(rootdir, 'GBK'),'resource')
    screen_file = './screenshot/screen'
    path = os.path.dirname(os.path.realpath(sys.argv[0]))
    if not os.path.exists(os.path.join(path,'resourcetmp')):
        os.mkdir(os.path.join(path,'resourcetmp'))
    if not os.path.exists(os.path.join(path,'screentmp')):
        os.mkdir(os.path.join(path,'screentmp'))
        
def compareimage(model):
    res_path = os.path.join(os.path.join(unicode(rootdir, 'GBK'),'resource'),model)
    des_path = os.path.join('./screenshot/screen',model)

    makedir()
    CopyFile.copy(des_path,'screentmp')
    CopyFile.copy(res_path,'resourcetmp')

    des_files = os.listdir('./screentmp')

    for i in range(len(des_files)):
        if des_files[i].split('.')[-1] == 'db':
            os.remove(os.path.join('./screentmp',des_files[i]))
    res_files = os.listdir('./resourcetmp')
    for i in range(len(res_files)):
        if res_files[i].split('.')[-1] is  'db':
            os.remove(os.path.join('./resourcetmp',res_files[i]))

    cut('screentmp')
    cut('resourcetmp')
    
    resource_list = []
    screen_list = []
    
    for parent,dirnames,filenames in os.walk('./screentmp'):
        resource = parent
        resource_list = filenames
    resource_list.sort()
    print resource_list
    
    for parent,dirnames,filenames in os.walk('./resourcetmp'):
        screen = parent
        screen_list = filenames
    screen_list.sort()
    print screen_list

    result =model+ '\nCompare Result:\n'

    for imagefile in screen_list:
        if imagefile not in resource_list:
            result = os.path.join(os.path.join(result,imagefile),'\t not exists in resource_list\n')
        else:
            result = result+'compare ' + imagefile + '\tResult:' + str(compare(resource + '/' + imagefile, screen + '/' + imagefile)) + '\n'
    print result
    WriteStrToFile(model+'.txt', result)
    shutil.rmtree('./screentmp')
    shutil.rmtree('./resourcetmp')
        
def main():
    resPath = os.path.join(unicode(rootdir, 'GBK'),'resource')
    if  not os.path.exists('./screenshot/screen'):
        os.mkdir('./screenshot/screen')
    desPath = './screenshot/screen'
    
    des_name = os.listdir('./out')
    res_name = os.listdir(os.path.join(unicode(rootdir, 'GBK'),'resource'))

    des_length = len(des_name)
    res_length = len(res_name)

    if(des_length > res_length):
        tag_max = des_name
        tag_min = res_name
    else:
        tag_max = res_name
        tag_min = des_name
     #截图文件夹对比源文件夹   
    for i in range(len(tag_max)):
        for j in range(len(tag_min)):            
            if(tag_max[i] == tag_min[j]):
                if not os.path.exists(os.path.join('./screenshot/screen',tag_min[j])):
                    os.mkdir(os.path.join('./screenshot/screen',tag_min[j]))
                res_path = os.path.join(os.path.join('out',tag_min[j]),'screenshot')
                des_path = os.path.join('./screenshot/screen',tag_min[j])
                CopyFile.copy(res_path,des_path)                             
            else:
                pass    
    dirname = []
    res_list = os.listdir(resPath)
    des_list = os.listdir(desPath)

    if(len(des_list) is not None):
        for i in range(len(des_list)):
            if res_list[i] == des_list[i]:
                compareimage(res_list[i])
    for i in range(len(des_list)):
        shutil.rmtree(os.path.join('./screenshot/screen',des_list[i]))




