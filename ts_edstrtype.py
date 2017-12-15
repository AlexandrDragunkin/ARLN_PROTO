# -*- coding: cp1251 -*-
#-------------------------------------------------------------------------------
# Name:        ts_edstrtype.py
# Purpose:     Модуль Чертежей панелей
#
# Author:      Aleksandr Dragunkin
#
# Created:     13.08.2013
# Copyright:   (c) GEOS 2012 http://k3info.ru/
# Licence:     FREE
#-------------------------------------------------------------------------------
'''
Возвращает строку pl_pnt полученную в результате выполнения операций с первыми nElStr элементами массива aNAtr
Выполняет expression для строки с разделителями ;
Например: '{a=getattr(0,"priceid",0);priceinfo(a,"MATTYPENAM",1)+" "+STR(priceinfo(a,"THICKNESS",1))+" мм"'

'''
#import wingdbstub
import k3 # Подключаем модуль k3

params=k3.getpar()
pl_pnt,nElStr,aNAtr = params[0],params[1],params[2]

S_val = ''
v_result,v_error = k3.Var(), k3.Var()
for i in range(int(nElStr)):
    elem = aNAtr[i]
    vv = elem.value if type(elem.value)==float else k3.getattr(0,elem.value,elem.value)
    if type(vv) in [int, float]:
        if abs(vv-int(vv))<0.0001:
            vv = int(vv)
    else:         
        pos = k3.instr(1,vv,"{",1)
        if pos>0:
            l_vv=len(vv)
            cod = k3.right(vv,l_vv-pos)            
            lcod=cod.split(';')
            if len(lcod)>0:
                for cod in lcod:
                    k3.expression(cod,v_result,v_error) 
                    if len(v_error.value)>1:
                        print ('Stamp.dbf ' + v_error.value + ' в выражении: '+cod)

            vv = v_result.value    
    S_val = S_val + str(vv)
if len(S_val)>0:
    pl_pnt.value = S_val