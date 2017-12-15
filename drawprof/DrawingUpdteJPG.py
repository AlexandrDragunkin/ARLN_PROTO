# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:        DrawingUpdteJPG
# Purpose:     Модуль Чертежей панелей
#
# Author:      Aleksandr Dragunkin
#
# Created:     29.08.2016
# Изменения для версии 7.3 поддержка Python3
# Copyright:   (c) GEOS 2012 http://k3info.ru/
# Licence:     FREE
# ------------------------------------------------------------------------------
#try:
    #import pydevd
    #pydevd.settrace('localhost', port=51764, stdoutToServer=True, stderrToServer=True)
#except:
    #pass
try:
    import wingdbstub
except:
    pass
# import logging
import k3
#from substdirs import Substdirs


def main():
    params  = k3.getpar()
    if len(params)==0:
        ref_drafts()
    else:
        namedef = params[0].lower()
        f = globals().get(namedef, None)
        if f is None or not hasattr(f, '__call__'):
            raise '\nНе найдена вызываемая функция с именем '
        else:
            if len(params)==1:
                f()
            elif len(params)>1: f(params[1:])    
    

def ref_drafts():
    nm_file = k3.sysvar(2)
    subname = 'K3_Drafts'
    j_name = '\\WMF_Drafts\\'
    ref_pictures(subname, nm_file, j_name)

def ref_complex():
    nm_file = k3.sysvar(2)
    subname = 'K3_Complex'
    j_name = '\\WMF_Complex\\'
    ref_pictures(subname, nm_file, j_name)


def ref_pictures(subname, nm_file, j_name):
    if subname in nm_file:
        abs_ph = k3.sysvar(2).split('\\'+subname+'\\')[0] + j_name
        abs_nm = k3.sysvar(2).split('\\'+subname+'\\')[-1].split('.')[:-1][0]
        full_nm = abs_ph + abs_nm+".jpg"
        if k3.fileexist(full_nm) > 0:
            k3.removefile(full_nm)        
        e = k3.exp2d(k3.k_jpeg, k3.k_mono , k3.k_inscribe, k3.k_yes, k3.k_vport, 3, k3.k_size, 2500, 1500, k3.k_continue, full_nm, k3.k_overwrite )
    else:
        k3.putmsg('Ошибка размещения файла! Доступно только для файлов чертежей в папке '+subname, 0)
    
if __name__ == '__main__':
    main()