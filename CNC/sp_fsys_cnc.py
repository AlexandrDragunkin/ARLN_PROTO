# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:        sp_fsys_cnc
# Purpose:     Модуль по работе с файлами CNC 
#
# Author:      Aleksandr Dragunkin
#
# Created:     25.01.2016
# Copyright:   (c) GEOS 2012-16 http://k3info.ru/
# Licence:     FREE
#-------------------------------------------------------------------------------
'''
   Формирует файловую структуру в папке CNC
'''

#import wingdbstub
import os
import fnmatch
import k3
import glob
import shutil
from sp_fsys import *

class File_CNC:
    def __init__(self, fnm):
        self.fulname = fnm
        self.filename = k3.getfiletitle(fnm)[:-4]
        self.filetype = k3.getfiletitle(fnm)[-3:]

ProjPath = k3.getfilepath(k3.sysvar(2))
CNCPATH=ProjPath+'CNC\\'
LISTSUBPATH=['Livra-5','Livra-5\\Выполнено','Livra-5\\Доп','Livra-5\\Доп\\Выполнено',
             'Rover-20','Rover-20\\Выполнено','Rover-20\\Доп','Rover-20\\Доп\\Выполнено',
             'Документы',
             'Задание'
         ]
# удаляем директории
# каталоги исключения 
exclude = set(('photo',
        'report',
        'сотрудники'))
 
dirs = (d for d in glob.iglob(os.path.join(CNCPATH, '*'))
        if os.path.isdir(d) and
           os.path.basename(d) not in exclude)
 
for f in dirs:
    shutil.rmtree(f)
 
dirs, files=getsubs(CNCPATH) #'''Возвращает списки дирректорий и файлов расположенных в дирректории ProjPath+'CNC\\''''

for e in LISTSUBPATH:
    if type(e)==str:
        create_folder(CNCPATH,e)
    else:
        pass

def addfcnc(a):
    return File_CNC(a)

def findf(l, e):
    '''Ищем объект е в списке l'''
    t = None
    for t in l:
        if not t is None:
            if t.filename == e.filename:
                break
    return t

files_pd4 = list(map(addfcnc, getfilemask(files, '*.pd4')))
files_bpp = list(map(addfcnc, getfilemask(files, '*.bpp')))

# перносим файлы в папку Livra-5 и их близнецы в Livra-5
for e in files_pd4:
    t = findf(files_bpp, e)
    rs = k3.movefile(e.fulname, CNCPATH+LISTSUBPATH[0]+'\\'+e.filename+'.'+e.filetype) # в Livra-5
    files_pd4[files_pd4.index(e)] = None
    if not t is None:
        rs = k3.movefile(t.fulname, CNCPATH+LISTSUBPATH[6]+'\\'+t.filename+'.'+t.filetype) # в 'Rover-20\\Доп'
        files_bpp[files_bpp.index(t)] = None
        
# перносим файлы в папку Rover-20 из тех что несмогли обработать на Livra
for t in files_bpp:
    if not t is None:
        rs = k3.movefile(t.fulname, CNCPATH+LISTSUBPATH[4]+'\\'+t.filename+'.'+t.filetype) # в 'Rover-20'
    



