# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:        cp_save.py
# Purpose:     Фиксация номеров панелей у прототипа
#
# Author:      Aleksandr Dragunkin
#
# Created:     09.10.2015
# поддержка Python3
# Copyright:   (c) GEOS 2015 http://k3info.ru/
# Licence:     FREE
# ------------------------------------------------------------------------------
#try:
    #import pydevd
    #pydevd.settrace('localhost', port=51764, stdoutToServer=True, stderrToServer=True)
#except:
    #pass

#import wingdbstub
import k3
from mPanel import (PanelRectangle,
                    ElemsInfo)
from mCounter import Counter
counter = Counter()
counter.reinit()
#----------------------------------------------------------------------
def holes_create_all():
    """Выполняет сверловку всей сцены"""
    try:
        k3.holes(k3.k_create, k3.k_all)
        result = True
    except:
        result = False
    return result
#----------------------------------------------------------------------
def get_pnt_interact():
    """Возвращает указатель на мебельную панель в интерактиве"""
    try:
        pnt = k3.Var()
        k3.fltrparamobj(1, 61)
        k3.objident(k3.k_partly, k3.k_interact, pnt)
        pan = pnt.value
    except:
        pan = None
    k3.fltrparamobj(0)
    return pan
#----------------------------------------------------------------------
def hash_panel(pan):
    """"""
    Panel = PanelRectangle()
    Panel.getPanelProperty(pan)
    Panel.getPanelPathInfo(pan)
    #arr = k3.VarArray(int(k3.getcntobjga(Panel.holder)))
    #k3.scang(Panel.holder, arr)
    #for a in arr:
        #try:
            #if a.value.get_attr('FurnType') == '010000':
                #Panel.polotno = a.value
                #break
        #except:
            #pass

    #n_drill = int(k3.getholes(Panel.polotno))
    #n = k3.Var()
    #n.value = n_drill
    #if n_drill > 0:
        #a_drill = k3.VarArray(n_drill* 15, 'a_drill')
        #k3.getholes(Panel.polotno, 'a_drill')
        ##ss = group([a.value for a in a_drill], 15)
        #drill_finder([a_drill, n], Panel)
    for  p in Panel.paths:
        print(p.__hash__())
    print(Panel.__hash__())
    print('*******************------------------***************')
    #for a in Panel.holes:
        #print(a, ' ', a.Side, a.Diameter, a.Hohe, a.Xc, a.Yc, a.Zc, a.__hash__())
    #print('*******************------------------***************')
    #for a in sorted(Panel.holes):
        #print(a, ' ', a.Side, a.Diameter, a.Hohe, a.Xc, a.Yc, a.Zc,  a.__hash__())    

        
def group(iterable, count):
    """ Группировка элементов последовательности по count элементов """
    return zip(*[iter(iterable)] * count)

if __name__ == '__main__':
    holes_create_all()
    pan = get_pnt_interact()
    hash_panel(pan)