# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:        sp_fsys
# Purpose:     Модуль по работе с файлами
#
# Author:      Aleksandr Dragunkin
#
# Created:     25.01.2016
# Copyright:   (c) GEOS 2012-16 http://k3info.ru/
# Licence:     FREE
#-------------------------------------------------------------------------------
#!/usr/bin/env python
#import wingdbstub
import os, fnmatch, k3

#------------------------------------------------------------------------------
def getsubs(dir):
    '''Возвращает списки дирректорий и файлов расположенных в дирректории dir'''
    # get all
    dirs = []
    files = []
    for dirname, dirnames, filenames in os.walk(dir):
        dirs.append(dirname)
        for subdirname in dirnames:
            dirs.append(os.path.join(dirname, subdirname))
        for filename in filenames:
            files.append(os.path.join(dirname, filename))
    return dirs, files

#------------------------------------------------------------------------------
def getsubdirs(dir):
    '''Возвращает списки дирректорий  расположенных в дирректории dir'''
    # get all
    dirs = []
    files = []
    for dirname, dirnames, filenames in os.walk(dir):
        dirs.append(dirname)
        for subdirname in dirnames:
            dirs.append(os.path.join(dirname, subdirname))
    return dirs

#------------------------------------------------------------------------------
def getfilemask(f,mask):
    '''Возвращает список файлов удовлетворяющих mask из списка файлов f'''
    tt=[]
    for i in f:
        if fnmatch.fnmatch(i,mask):
            tt.append(i)
    return tt

#------------------------------------------------------------------------------
def getungfiles(listfiles):
    '''Находит в списке listfiles самый свежий файл'''
    tdatapr = None
    filename = None
    for i in listfiles:
        tdata = os.stat(i).st_mtime
        if  tdatapr is None:
            tdatapr = tdata
            filename = i
        elif tdatapr < tdata:
            tdatapr = tdata
            filename = i
    return filename

#------------------------------------------------------------------------------
def create_folder(path, date):
    '''Создает новую папку'''
    os.chdir(path)
    os.mkdir(str(date))