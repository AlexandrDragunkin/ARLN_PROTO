# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:        addFolderToSysPath
# Purpose:     Модуль добавляет в SysPAth пути
#
# Author:      Aleksandr Dragunkin
#
# Created:     08.10.2014
# Copyright:   (c) GEOS 2012 http://k3info.ru/
# Licence:     FREE
# -------------------------------------------------------------------------------
import wingdbstub
import k3
import sys
import os

protopath = k3.mpathexpand("<proto>") + '\\'

dvsyspath = [protopath + a for a in ['drawprof',
                            'dynaplansupport',
                            'ProjectsUtilites',
                            'Dbaccess',
                            'CNC',
                            'complexlabeldraw',
                            '_OpenCode_\script',
                            'site-packages',
                            'site-packages\\win32',
                            'site-packages\\win32\\lib',
                            'site-packages\\win32com',
                            'site-packages\\win32comext',
                            ]]

for tpath in dvsyspath:
    if tpath not in sys.path:
        sys.path.insert(0, tpath)

app = k3.mpathexpand("<app>") + '\\'

dvsyspath = [app + a for a in [ 'DLLs',
                                'Lib',
                                'Lib\\site-packages',
                                'tcl', 
                              ]
            ]

for tpath in dvsyspath:
    if tpath not in sys.path:
        sys.path.insert(0, tpath)
        
# data = "c:\\Python33\\"
# dvsyspath = [data + a for a in ['DLLs',
                                # 'Lib',
                                # 'Lib\\site-packages',
                                # 'Lib\\site-packages\\win32',
                                # 'Lib\\site-packages\\win32\\lib',
                                # 'Lib\\site-packages\\win32com',
                                # 'Lib\\site-packages\\win32comext',
                                # ]]
# for tpath in dvsyspath:
    # if tpath not in sys.path:
        # sys.path.insert(0, tpath)
# Версия python
py_ver=float(str(sys.version_info.major)+"."+str(sys.version_info.minor))

if py_ver==3.3:
    os.environ['TCL_LIBRARY'] = app + r"lib\tcl8.5"
    os.environ['TK_LIBRARY'] = app + r"lib\tk8.5"
elif py_ver==3.5:
    os.environ['TCL_LIBRARY'] = app + r"tcl\tcl8.6"
    os.environ['TK_LIBRARY'] = app + r"tcl\tk8.6"
