# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        holes_out_hide
# Purpose:     Погасить ответные отверстия (Вне панели)
#
# Author:      Aleksandr Dragunkin
#
# Created:     15.12.2015
# Copyright:   (c) GEOS 2012 http://k3info.ru/
# Licence:     FREE
#-------------------------------------------------------------------------------
import k3
# import wingdbstub
try:
    from DrawingSupp import GetListAllPanel
except:
    pass

#----------------------------------------------------------------------

    
def get_all_child_by_attr(obj, attrname=None):
    pnt = k3.Var()
    lchild = []
    n_list = k3.getcntobjga(obj)
    a_list = k3.VarArray(int(n_list))
    k3.scang(obj, a_list)
    for e in a_list:
        lchild.append(e.value)
    for e in lchild:
        if k3.getobjhold(e, pnt) > 0:
            if k3.compareobj(panel, obj) > 0:
                pass
            elif e not in lchild:
                lchild.append(e)
    lresult = []
    if not attrname is None:        
        for e in lchild:
            if k3.isassign(attrname, e) > 0:
                lresult.append(e)
    else:
        lresult = lchild
    return lresult

def get_allPanel():
    #pnt = k3.Var()
    try:
        allp = GetListAllPanel()
        return allp
    except:
        try:
            # включаем фильтр по панелям
            k3.fltrparamobj(1, 61)
            # выбираем панель (для демонстрации) и помещаем в pnt
            #k3.objident(k3.k_interact, pnt)
            #panel = pnt.value
            k3.select(k3.k_partly, k3.k_all)
            allp = []
            n = k3.sysvar(61)
            # выключаем фильтр
            k3.fltrparamobj(0)
            if  n > 0:
                for i in range(int(n)):
                    allp.append(k3.getselnum(i+1))
            return allp
        except Exception as inst:
            print(type(inst))    # the exception instance
            print(inst.args)     # arguments stored in .args
            print(inst)
            fltrparamobj(0)  # сбрасываем фильтр
            return None

def invisible_list_panhole(allp, get_all_child_by_attr):
    if not allp is None:    
        for panel in allp:
            # Ищем полотно панели
            k3.selbyattr('FurnType=="010000"', k3.k_child, panel)
            # Если нашли
            if k3.sysvar(61) > 0:        
                polotno = k3.getselnum(1)
                n = k3.getholes(polotno)
                arr = k3.VarArray(int(n*15), 'arr')
                n = k3.getholes(polotno, 'arr')
                # Список всех отверстий панели
                lholes = [a.value for a in arr]
                # Список всех деталей крепежа, которым принадлежат отверстия
                lfix = [lholes[i] for i in range(2, len(lholes), 15)]
                # Реальные дети панели
                # Крепеж
                child_pan_fix = []
                for e in lfix:
                    if (k3.findobjholdg(panel, e)) > 0:
                        child_pan_fix.append(e)        
                if len(child_pan_fix) > 0:
                    l_hole_rem = []
                    for e in child_pan_fix:
                        # список отверстий крепежа
                        c_hole_rem = get_all_child_by_attr(e, attrname='HoleType')
                        for h in c_hole_rem:
                            if not h in lfix:
                                l_hole_rem.append(h)
                                
                    for e in l_hole_rem:
                        if k3.penetrate(e, polotno) == 2:
                            k3.invisible(k3.k_partly, e)

        
allp = get_allPanel()
invisible_list_panhole(allp, get_all_child_by_attr)
                    
        

        