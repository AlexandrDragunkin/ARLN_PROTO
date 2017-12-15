# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        mMatrix
# Purpose:     Модуль аффинных преобразований и функций по работе с матрицами
#
# Author:      Aleksandr Dragunkin
#
# Created:     16.02.2015
# Для версии 7.3 поддержка Python3
# Copyright:   (c) GEOS 2012 http://k3info.ru/
# Licence:     FREE
#-------------------------------------------------------------------------------

import k3
#import wingdbstub

class Matrix:
    def __init__(self):
        self.matr = self._array(16)
        self.Ohcunit()

    def _array(self, n):
        '''Возвращает VarArray в n элементов'''
        return k3.VarArray(n)
    
    def Ohcunit(self):
        ''' Функция устанавливает единичную матрицу в заносит ее в массив self.matr  '''
        return k3.ohcunit(self.matr)
    
    def Otdtran(self, v):
        '''добавляет в матрицу <self.matr> преобразования сдвига на величину вектора <V>.
        При этом предыдущее значение матрицы <self.matr> умножается на преобразование сдвига. То
        есть, в матрице <self.matr> накапливаются преобразования, последовательно заданные функциями
        аффинных преобразований. '''
        a = self._list_to_array(v)
        return k3.otdtran(self.matr, a)
    
    def Otdrot(self, Naxes, Alpha):
        '''добавляет преобразование поворота в матрицу <self.matr>. При этом предыдущее
        значение матрицы <self.matr> умножается на преобразование поворота. То есть, в матрице <self.matr>
        накапливаются преобразования, последовательно заданные функциями аффинных
        преобразований. Входные параметры:
        <Naxes> - номер оси поворота (1-X, 2-Y, 3-Z). Берется по модулю.
        <Alpha> - угол поворота. Если <Naxes> меньше нуля, угол задаётся в радианах, иначе - в
        градусах.
        <self.matr> - исходная матрица
        Результат заносится в матрицу <self.matr> . Функция возвращает:
        1 - успешно
        0 - ошибка
        2 - неверный номер оси
        '''
        return k3.otdrot(self.matr, Naxes, Alpha)
    
    def Otdrotxyz(self,  P, A, Alpha):
        '''добавляет в матрицу <self.matr> преобразование поворота на угол <Alpha> в
        радианах вокруг произвольной оси, задаваемой точкой с координатами в списке <P> и
        направлением в пространстве, заданным вектором в списке <A>. При этом предыдущее
        значение матрицы <self.matr> умножается на преобразование поворота. То есть, в матрице <self.matr>
        накапливаются преобразования, последовательно заданные функциями аффинных
        преобразований. Функция возвращает:
        1 - успешно
        0 - ошибка'''
        p = self._list_to_array(P)
        a = self._list_to_array(A)
        return k3.otdrotxyz(self.matr, p, a, Alpha)

    def _list_to_array(self, P):
        if  isinstance(P, k3.VarArray):
            p = P
        else:
            p = self._array(len(P))
            for i, e in enumerate(P):
                p[i].value = e
        return p
    
    def Ohcmult(self, A,B):
        '''осуществляет умножение матрицы <A> на матрицу <B> и заносит результат в
        матрицу <C>'''
        a = self._list_to_array(A)
        b = self._list_to_array(B)
        c = self._array(16)
        res = k3.ohcmult(a, b, c)
        return [e.value for e in c]
    
    def Otrans(self, handle):
        '''Функция преобразует объект <Obj> матрицей <self.matr>'''
        try:
            return k3.otrans(handle, self.matr)
        except:
            return None
    
    def Ominv(self):
        '''обращает матрицу <self.matr> и записывает результат в матрицу <c>. Функция
        возвращает обращеную матрицу'''
        c = self._array(16)
        k3.ominv(self.matr, c)
        return [e.value for e in c]
    
    def matrixPoint(self, pin):
        '''Вычисляем координаты точки pin после преобразования матрицей trans'''
        if isinstance(self.matr, k3.VarArray):
            trans = [t.value for t in self.matr]
        else:
            trans = self.matr
        
        if isinstance(pin, k3.Point):
            pns = k3.Point()
            pns.set(pin.x*trans[0]+ pin.y*trans[1]+ pin.z*trans[2]+trans[3] , 
                        pin.x*trans[4]+ pin.y*trans[5]+ pin.z*trans[6]+trans[7], 
                        pin.x*trans[8]+ pin.y*trans[9]+ pin.z*trans[10]+trans[11])
            return pns
            
        else:
            return (pin[0]*trans[0]+ pin[1]*trans[1]+ pin[2]*trans[2]+trans[3] , 
            pin[0]*trans[4]+ pin[1]*trans[5]+ pin[2]*trans[6]+trans[7], 
            pin[0]*trans[8]+ pin[1]*trans[9]+ pin[2]*trans[10]+trans[11])
    