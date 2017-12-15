# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:        unArc
# Purpose:     Модуль дуги
#
# Author:      Aleksandr Dragunkin
#
# Created:     19.06.2015
# Изменения для версии 7.3 поддержка Python3
# Copyright:   (c) GEOS 2012 http://k3info.ru/
# Licence:     FREE
# ------------------------------------------------------------------------------

#import wingdbstub
import k3
from Utilites_K3 import (VarArray,
                         str_random_name)

class unArc():
    """
    < A r r [ 1 ] >  - Коор дината X це нтр а дуги
    < A r r [ 2 ] >  - Коор дината Y це нтр а дуги
    < A r r [ 3 ] >  - Радиус дуги
    < A r r [ 4 ] >   -  Ориентация  дуги  (1  -  положительная  -  против  часовой  стрелки,  0  -отрицательная - по часовой стрелке)
    < A r r [ 5 ] >  - Угол до начала дуги (в радианах)
    < A r r [ 6 ] >  - Угол раствора дуги (в радианах)
    Функция  возвращает  число  заполненных  эл"""
    def __init__(self, e):
        self.unxcentr = None
        self.unycentr = None
        self.unradius = None
        self.unorient = None
        self.unstangle = None
        self.unendangle = None
        self.unrstagle = None
        self.xmax = None
        self.ymax = None
        self.xmin = None
        self.ymin = None
        
        if e.__class__.__name__ == 'ElemsInfo':
            if e.TypeElem == 2:
                arr = VarArray()
                un = self.add_unobj(arr, typeun=2, 
                                         lst = [e.GeoInfo[0],
                                                e.GeoInfo[1],
                                                e.GeoInfo[6],
                                                e.GeoInfo[7],
                                                e.GeoInfo[3],
                                                e.GeoInfo[4]])  
                rs = k3.getacunobj2d(un, arr.array)
                if rs > 0:
                    self.unxcentr = arr.array[0].value
                    self.unycentr = arr.array[1].value
                    self.unradius = arr.array[2].value
                    self.unorient = arr.array[3].value
                    self.unstangle = self.norm_angle(arr.array[4].value)
                    
                    self.unrstagle = 2 * k3.asin(k3.sqrt((e.GeoInfo[6]-e.GeoInfo[0])**2+(e.GeoInfo[7]-e.GeoInfo[1])**2) / (round(self.unradius, 2) * 2))
                    self.unendangle = self.norm_angle(arr.array[4].value + self.unrstagle) #arr.array[5].value
                    # Угол раствора меньше Pi/2
                    qst = self.getnumqadrant(self.unstangle)
                    qend = self.getnumqadrant(self.unendangle)
                    qrst = self.getnumqadrant(self.unrstagle)

                    unx = self.add_unobj(arr, typeun=1, 
                                         lst = [self.unxcentr - 1.2 * self.unradius,
                                                self.unycentr,
                                                self.unxcentr + 1.2 * self.unradius,
                                                self.unycentr])
                    uny = self.add_unobj(arr, typeun=1, 
                                         lst = [self.unxcentr,
                                                self.unycentr - 1.2 * self.unradius,
                                                self.unxcentr,
                                                self.unycentr + 1.2 * self.unradius])
                    nm1 = str_random_name()
                    nm2 = str_random_name()
                    res1 = k3.interunobj2d(un, 1, unx, 1, nm1)
                    res2 = k3.interunobj2d(un, 1, uny, 1, nm2)
                    arr1, arr2 = k3.VarArray(4, nm1),  k3.VarArray(4, nm2)
                    
                    lstx = [e.GeoInfo[0], e.GeoInfo[6]]
                    if res1 > 0:
                        n1 = int(k3.getdimarray(arr1))
                        arr1 = k3.VarArray(n1, nm1)
                        lstx.append(arr1[0].value)
                        if n1 > 2:
                            lstx.append(arr1[2].value)
                    lstx.sort()

                    lsty = [e.GeoInfo[1], e.GeoInfo[7]]
                    if res1 > 0:
                        n2 = int(k3.getdimarray(arr2))
                        arr2 = k3.VarArray(n2, nm2)
                        lsty.append(arr2[1].value)
                        if n2 > 2:
                            lsty.append(arr2[3].value)
                    lsty.sort()
                    k3.freeunobj2d(unx)
                    k3.freeunobj2d(uny)
                    self.xmax = lstx[-1]
                    self.ymax = lsty[-1]
                    self.xmin = lstx[0]
                    self.ymin = lsty[0]
                    self.length = self.unradius * self.unrstagle
                k3.freeunobj2d(un)

    def add_unobj(self, arr, typeun, lst):
        arr.transform_list_to_array(list(map(lambda x:round(x, 2), lst)))
        unx = k3.addunobj2d(typeun, 0, arr.array)
        return unx
                
                
    def getnumqadrant(self, ang):
        """
        Возвращае номер квадранта в котором расположен угол
        """
        qwd = None
        if -0.01 < ang < (k3.pi() + 0.01) / 2:
            qwd = 1
        elif k3.pi() / 2 < ang < (k3.pi() + 0.01):
            qwd = 2
        elif k3.pi()< ang < (k3.pi() * 2/ 3 + 0.01):
            qwd = 3
        elif (k3.pi() * 2/ 3)< ang < (2 * k3.pi()):
            qwd = 4
        return qwd
    
    def norm_angle(self, ang_e):
        """
        Приводит значение угла ang_e в диапазон от 0, до 2 пи
        """
        while abs(ang_e) - k3.pi()*2 > -0.01:
            ang_e = ang_e - k3.sgn(ang_e) *k3.pi()*2
        if -0.01<ang_e<0.01:
            ang_e = 0.0
        return ang_e