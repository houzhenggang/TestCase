# -*- coding: cp936 -*-
import os
import shutil

def copyFiles(src, dst):
    srcFiles = os.listdir(src)
    dstFiles = dict(map(lambda x:[x, ''], os.listdir(dst)))
    filesCopiedNum = 0

    # ��Դ�ļ����е�ÿ���ļ�����������Ŀ���ļ�������
    for file in srcFiles:
        src_path = os.path.join(src, file)
        dst_path = os.path.join(dst, file)
        # ��Դ·��Ϊ�ļ��У���������Ŀ���ļ��У���ݹ���ñ������������ȴ����ٵݹ顣
        if os.path.isdir(src_path):
            if not os.path.isdir(dst_path):
                os.makedirs(dst_path) 
            filesCopiedNum += copyFiles(src_path, dst_path)
        # ��Դ·��Ϊ�ļ������ظ����ƣ������޲�����
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
