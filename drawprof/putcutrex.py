# -*- coding: utf-8 -*-
#---------------------------------------------------------------------
# Name:        putcutrex
# Purpose:     Модуль работы с вырезами
#
# Author:      Aleksandr Dragunkin
#
# Created:     29.06.2016
# Copyright:   (c) GEOS 2016 http://k3info.ru/
# Licence:     FREE
#----------------------------------------------------------------------
import wingdbstub
import k3
import sys

def putcutrex(Panel=0, Pat=None, CutType=1, Dept=0, Map=5, ShiftX=0, ShiftY=0, Ang=0):
    """
    
    #-- Добавить вырез на панель с параметрами положения
    
    #-- Входные параметры:
    
    #-- Panel - объект "Панель"
    #--         или 0 - если панель не надо инициализировать
    
    #-- Pat - объект "Контур выреза"
    
    *-- CutType - тип выреза:
    
    *--           0 - линия маркировки
    
    *--           1 - вырез
    
    *--           8 - нарост
    
    *--           2 - симметрия относительно оси X
    
    *--           4 - симметрия относительно оси Y)
    
    #-- Dept - глубина выреза:
    
    #--           0 - если вырез сквозной
    
    #--           > 0 - не сквозной со стороны пласти A
    
    #--           < 0 - не сквозной со стороны пласти F
    
    #-- Map - секция раскрашивания
    
    #-- Параметры положения:
    
    #-- ShiftX - сдвиг вдольоси Х
    
    #-- ShiftY - сдвиг вдольоси Y
    
    #-- Ang - угол поворота
    
    #-- Зачастую приходится добавлять по многу вырезов в панель. Если при этом
    #-- перестраивать панель после каждого выреза, то получится очень долго
    #-- Поэтому инициализируем панель в вызывающем макросе и там же ее перестраиваем.
    #-- А вырезы добавляем здесь.
    
>>> pan = k3.Var()
... k3.objident(k3.k_prompt, 'Укажите ...', k3.k_interact, pan)
... pat = k3.Var()
... k3.objident(k3.k_prompt, 'Укажите ...', k3.k_interact, pat)    
... putcutrex(Panel=pan.value, Pat=pat, Dept=12)
... k3.mbpanel(k3.k_execute,pan.value )    
    
    """
    ifVar = lambda v: v.value if isinstance(v, k3.Var) else v
    (Panel, Pat, CutType, Dept, Map, ShiftX, ShiftY, Ang) = map(ifVar, (Panel, Pat, CutType, Dept, Map, ShiftX, ShiftY, Ang))
    str_err = ("Неожиданная ошибка:", sys.exc_info()[0])
    try:
        arr = k3.VarArray(24)
        #-- Если панель задана, то ее инициализируем.
        if isinstance(Panel,k3.Group ):
            arr[0].value=Panel
            if k3.getpan6par(1,arr) == -1.0:
                str_err = ('Ошибка! Несмогли инициализировать мебельную панель!')
                raise TypeError()
        
        if Pat is None:
            str_err = ('Контур выреза неопределен!')
            raise TypeError()
        
        ty_pat = k3.getobjtype(Pat)
        if ty_pat == 5 :
            #-- Контур, превращаем в полилинию
            Pat = k3.pline( k3.k_path, Pat)[0]
        elif ty_pat == -12 :
            #-- полилиния
            pass
        else:
            str_err = ('Ошибка! [%i] Недопустимый тип контура выреза! Допустимы замкнутые контур или полилиния [5] [-12]' %ty_pat)
            raise TypeError()
            
        #-- Параметры формы выреза
        k3.initarray(arr,0)
        arr[0].value=CutType #-- Тип выреза
        arr[1].value=1       #-- Форма выреза
        arr[2].value=Pat     #-- Полилиния
        k3.setpan6par(7,arr)
        #-- Параметры положения выреза
        k3.initarray(arr,0)
        arr[0].value=9    #-- Привязка выреза к одному из торцев (1,3,5,7) или свободная привязка (9)
        arr[1].value=ShiftX#-- Если привязка к торцу, то сдвиг вдоль торца, иначе - абсолютная координата X в ЛСК панели
        arr[2].value=ShiftY  #-- Если привязка к торцу, то сдвиг вглубь панели, иначе - абсолютная координата Y в ЛСК панели
        arr[3].value=Ang    #-- Угол поворота выреза в градусах
        arr[4].value=Dept  #-- Глубина выреза: 0, если вырез сквозной > 0 - не сквозной со стороны пласти A < 0 - не сквозной со стороны пласти F
        
        k3.setpan6par(8,arr)
        arr[0].value=Map     #-- Секция раскрашивания
        g_OutPar = k3.GlobalVar('g_OutPar')
        g_OutPar.value=k3.setpan6par(9,arr)  #-- Добавить вырез, параметры которого определены кодами 7 и 8

    except TypeError:
        print(str_err)
    except:
        print(str_err)    
        
def test():
    pan = k3.Var()
    k3.objident(k3.k_prompt, 'Укажите панель', k3.k_interact, pan)
    pat = k3.Var()
    k3.objident(k3.k_prompt, 'Укажите контур выреза', k3.k_interact, pat)    
    putcutrex(Panel=pan.value, Pat=pat, Dept=12)
    k3.mbpanel(k3.k_execute,pan.value )
def main():
    pass
if __name__ == '__main__':
    main()