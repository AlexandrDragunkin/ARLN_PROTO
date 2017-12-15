# -*- coding: cp1251 -*-
#-------------------------------------------------------------------------------
# Name:        mfix
# Purpose:     Крепеж в панели
#
# Author:      Aleksandr Dragunkin
#
# Created:     31.10.2012
# Copyright:   (c) GEOS 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import k3
import gUtilitesK3 as gU
#-------------------------------------------------------------------------------

class Fix:
    ''' Крепеж на панель.
        По сторонам 'B','C','D','E' и углам 'Ang_1','Ang_2','Ang_3','Ang_4'

    '''
    def __init__(self):
        self.Side = 1
        self.fixID = 0
        self.fixMask = 0
        __fix_property = ['Side','fixID','fixMask'] # упорядоченный список, именно в этой последовательности требуется передавать параметры в К3
        __fix_defvalue = {'Side':self.Side,'fixID':self.fixID,'fixMask':self.fixMask}
        __fix_permissible = {__fix_property[0]:[1,2,3,4,5,6,7,8,'B','C','D','E','Ang_1','Ang_2','Ang_3','Ang_4'],
                            'D':3,'C':2,'E':4,'B':1,'Ang_1':5,'Ang_2':6,'Ang_3':7,'Ang_4':8}  # СПИСОК ДОПУСТИМЫХ ЗНАЧЕНИЙ Side и подмена строковых значений
        # нужна регистронезависимость надо что то придумать с str.lower

        gU.vDefProperty.newAttr('fix_defvalue',__fix_defvalue)
        gU.vDefProperty.newAttr('fix_property',__fix_property)
        gU.vDefProperty.newAttr('fix_permissible',__fix_permissible)
        for i in list(gU.vDefProperty.fix_defvalue.items()): # Создаю аттрибуты класса по словарю и задаю значения по умолчанию
                setattr(self, i[0],i[1])

    def __hash__(self):
        return hash((self.Side, self.fixID, self.fixMask))

    def setFix(self, Change_Default=False, **curr_fix):
        ''' -- Изменяет свойства крепежа
            -- Входные параметры:

            -- Change_Default по умолчанию False управляет сменой глобальных
            умолчаний при создании нового экземпляра класса fix

            curr_fix словарь, который може иметь значения
            -- Side -  Привязка крепежа
            --          1 - сторона D;
            --          3 - сторона C;
            --          5 - сторона E;
            --          7 - сторона B;
            --          2 - 'Ang_1' - угол 1
            --          4 - 'Ang_2' - угол 2
            --          6 - 'Ang_3' - угол 3
            --          8 - 'Ang_4' - угол 4
            Пример:
                vfix_B = fix()
                vfix_C = fix()
                vfix_B.setfix(True,Side='B',  fixID=51)
                vfix_C.setfix(fixID=74,  Side='C',)
            '''
        #print curr_fix
        result=gU.setAttrToDict(self,Change_Default,
                                    gU.vDefProperty.fix_property,
                                    gU.vDefProperty.fix_permissible,
                                    gU.vDefProperty.fix_defvalue,
                                    curr_fix)
#------------------------------------------------------------------------------------------
class Fixline:
    '''Свободная линия крепежа'''
    def __init__(self, xn=0, yn=0, zn=0,   #-- Начало линии крепежа
                 xv=0, yv=0, zv=0,         #-- точка на оси Z ЛСК линии крепежа
                 xt=0, yt=0, zt=0,         #-- Конец линии крепежа
                 FixType=0                 #-- Тип крепежа
                 ):
        self.FixLine = (xn, yn, zn,   #-- Начало линии крепежа
                        xv, yv, zv,   #-- точка на оси Z ЛСК линии крепежа
                        xt, yt, zt)  #-- Конец линии крепежа
        self.FixType = FixType
        self.listpos = []
        
    
    def add_FixGroup(self, par):
        if isinstance(par, list):
            if len(par) % 3 == 0:
                if True in map(lambda a: isinstance(a, k3.Var), par):
                    for e in par:
                        if  isinstance(e, k3.Var):
                            par[par.index(e)] = e.value
                self.listpos.extend(par)
    
    def make(self):
        return k3.fixing(k3.k_fix, k3.k_manual, k3.k_parameter, self.FixType, k3.k_free, self.FixLine, self.listpos)
    
    
def main():
    pass

if __name__ == '__main__':
    main()