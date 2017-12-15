# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        numerator
# Purpose:     Поиск панелей с левым базисом
#
# Author:      Aleksandr Dragunkin
#
# Created:     16.06.2015
# Copyright:   (c) GEOS 2012-15
# Licence:     FREE
#-------------------------------------------------------------------------------
# import wingdbstub
import k3
from DrawingSupp import GetListAllPanel



if 'ARRGAB' in globals():
    del(ARRGAB)
if 'llbasis' in globals():
    del(llbasis)
ARRGAB = k3.VarArray(6)
llbasis = [] 

def get_list_panel():
    """Возвращает список всех панелей сцены"""
    return [a for a in GetListAllPanel()]

def get_basis_lsc(p):
    """Возвращает результат проверки левого базиса панели"""
    try:
        cp = k3.getattr(p, 'commonpos', 0)
        k3.getsnap()
        k3.setucs(k3.k_lcs, k3.k_partly, p)
        k3.initarray(ARRGAB, 0)
        k3.selbyattr('FurnType==\"010000\"', k3.k_child, p)
        ps = k3.getselnum(1)
        k3.objgab3(ps, ARRGAB)
        h_difference = lambda v1, v2: (max(v1, v2) - min(v1, v2)) / 2.0 + min(v1, v2)
        log_minus =  lambda v: v < 0
        agab = [a.value for a in ARRGAB]
        lpcen = list(map(h_difference, agab[:3], agab[3:]))
        
        result = True in map(log_minus, lpcen)
        if result:
            k3.putmsg(str(cp)+'  Это номер с левой базой', 0)
            llbasis.append(p)
        k3.resnap()
    except:
        result =  False
        k3.putmsg(str(cp)+'  Это номер скорее всего погашен.')
    return result

def get_lbasis_allpanel():
    return True in [get_basis_lsc(p) for p in get_list_panel()]

def dialog():
    vFailColor = k3.Var()
    k3.getvarinst(2,"FailColor", vFailColor,12)
    FailColor = vFailColor.value
    k3.select(k3.k_stayblink, k3.k_partly, llbasis, k3.k_done)
    ok_flag = k3.alternative( "Поиск панелей с левой базой", 
    k3.k_msgbox, k3.k_picture, 1, k3.k_beep, 1, k3.k_text, k3.k_left, 
    "Панели с левой базой выделены мерцанием", 
    "", 
    "Отключить мерцание найденных объектов?", 
    k3.k_done, 
    "Да",  "Нет", "Изменить цвет", 
    k3.k_done)
    if (ok_flag[0]==1):
        k3.select(k3.k_all, k3.k_done)
    elif (ok_flag[0]==3):
        k3.chprop( k3.k_color, k3.k_partly , k3.k_previous, k3.k_done, FailColor) 

def start():
    global ARRGAB
    ARRGAB = k3.VarArray(6)
    global llbasis
    llbasis = []    
    t = get_lbasis_allpanel()
    if t:
        dialog()
    

if __name__ == '__main__':
    start()