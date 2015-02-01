# -*- coding: cp936 -*-
import os
import shutil

def copyFiles(src, dst):
    srcFiles = os.listdir(src)
    dstFiles = dict(map(lambda x:[x, ''], os.listdir(dst)))
    filesCopiedNum = 0

    # 对源文件夹中的每个文件若不存在于目的文件夹则复制
    for file in srcFiles:
        src_path = os.path.join(src, file)
        dst_path = os.path.join(dst, file)
        # 若源路径为文件夹，若存在于目标文件夹，则递归调用本函数；否则先创建再递归。
        if os.path.isdir(src_path):
            if not os.path.isdir(dst_path):
                os.makedirs(dst_path) 
            filesCopiedNum += copyFiles(src_path, dst_path)
        # 若源路径为文件，不重复则复制，否则无操作。
        elif os.path.isfile(src_path):
            shutil.copyfile(src_path,dst_path)
            filesCopiedNum += 1
            '''if not dstFiles.has_key(file):
                shutil.copyfile(src_path, dst_path)
                filesCopiedNum += 1'''

    return filesCopiedNum

def copy(resourceDir,desDir):
    src_dir = os.path.abspath(resourceDir)
    if not os.path.isdir(src_dir):
        print 'Error: source folder does not exist!'
        return 0

    dst_dir = os.path.abspath(desDir)
    if os.path.isdir(dst_dir):
        num = copyFiles(src_dir, dst_dir)
    else:
        print 'Destination folder does not exist, a new one will be created.'
        os.makedirs(dst_dir)
        num = copyFiles(src_dir, dst_dir)

    print 'Copy complete:', num, 'files copied.'
