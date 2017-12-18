# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        mCounter
# Purpose:     Счетчик
#
# Author:      Aleksandr Dragunkin
#
# Created:     31.10.2012-2015
# изменения для версии 7.3 поддержка Python3
# Copyright:   (c) GEOS 2012-13
# Licence:     FREE
#-------------------------------------------------------------------------------
#import wingdbstub
import k3
from SingletonMetaClass import Singleton
#-----------------------------
class Userproperty(Singleton):
    '''всякие разные свойства'''

    def __init__(self):
        lRes = self.udGetEntity("DrawLineS")
        self.DrawLineS = lRes[2]
        self.colorCentralLine = 12  # цвет осевых линий или None если ненужен
        self.textPars = getParamsTextK3()

    def udGetEntity(self, Name=None):
        '''читает свойство из пользовательских умолчаний'''
        ValType, sVal, rVal = k3.Var(), k3.Var(), k3.Var()
        ValType.value, sVal.value, rVal.value = 0, '', 0
        err = k3.udgetentity(Name, ValType, rVal, sVal)
        return err, ValType.value, rVal.value, sVal.value
#-----------------------------
class Counter(Singleton):
    '''Счетчики объектов'''

    def __init__(self):
        self.drill = []
        self.drill_F = False
        self.drill_A = False
        self.note = []
        
        
    def reinit(self):
        self.drill = []
        self.drill_F = False
        self.drill_A = False
        self.note = []    

    def appender(self, Nm=None, Obj=None):

        def _cr(self, Nm):
            if not Nm in self.__dict__.keys():
                self.__setattr__(Nm, [])

        if (not Nm is None
            and not Obj is None):
            _cr(self, Nm)
            self.__dict__[Nm].append(Obj)
            return True
        elif (not Nm is None
            and  Obj is None):
            _cr(self, Nm)
            return True
        else:
            return False
    
def Central(xc1, yc1, zc1, xc2, yc2, zc2):
    '''-- Процедура построения осевой линии
     //-- Входные параметры:
     //-- xc1, yc1, zc1, xc2, yc2, zc2 - координаты концов линии
     //-- colcen - цвет линии
     '''
    userproperty = Userproperty()
    from DrawingSupp import Drawing
    drawing = Drawing()
    if (xc1, yc1, zc1) != (xc2, yc2, zc2) and (
                    (xc1, yc1, zc1) not in drawing.gab and (xc2, yc2, zc2) not in drawing.gab):
        lineObj = k3.line(xc1, yc1, zc1, xc2, yc2, zc2, k3.k_done)[0]
        if userproperty.colorCentralLine is not None:
            k3.chprop(k3.k_color, k3.k_last, 1, k3.k_done, userproperty.colorCentralLine)
        #k3.chprop(k3.k_lwidth,k3.k_last,1,k33.k_done,TilOs)
        k3.chprop(k3.k_ltype, k3.k_last, 1, k3.k_done, 5)
        #k3.chprop(k3.k_grfcoeff,k3.k_last,1,k3.k_done,1)
        return lineObj
    else:
        return None
    
#----------------------------------------------
def getParamsTextK3():
    """

    :rtype : list

    :return: Возвращает список текущие параметры текста:

     #. Имя шрифта STRING
     #. Высота символа DOUBLE
     #. Отношение ширины к высоте (в процентах) DOUBLE
     #. Угол наклона шрифта (в градусах) DOUBLE
     #. Разрядка  между  символами  по  горизонтали(в процентах)DOUBLE
     #. Разрядка  между  символами  по  вертикали  (впроцентах)DOUBLE
     #. Количество строк в объекте типа «Текст» INT
     #. Содержимое первой строки текста STRING
     """
    t = k3.text('a', k3.k_done, 0, 0, 0, k3.k_normal, 0, 0, 1, 1, 0, 0)
    ainfo = k3.VarArray(8)
    err = k3.gettextinfo(t[0], ainfo)
    k3.delete(t[0], k3.k_done)
    result = [a.value for a in ainfo]
    return result