# -*- coding: cp1251 -*-
#-------------------------------------------------------------------------------
# Name:        mButts
# Purpose:     Торцевые обработки в панели
#
# Author:      Aleksandr Dragunkin
#
# Created:     06.03.2013
# Copyright:   (c) GEOS 2012
# Licence:     FREE
#-------------------------------------------------------------------------------

import gUtilitesK3 as gU
#-------------------------------------------------------------------------------

class Butt:
    ''' Торцевая обработка на панель.
    //-- Side - сторона (1- B, 2 - C, 3 - D, 4 - E)
    //-- TypeFr - Тип торцевой обработки:
    //--     0 - нет обработки
    //--     1 - прямоугольный паз
    //--     2 - скос
    //--     3 - скругление
    //-- Map - Секция раскрашивания
    //--     1 - торец E (Y+)
    //--     2 - торец D (Y-)
    //--     3 - торец C (X+)
    //--     4 - торец B (X-)
    //--     5 - пласть верхняя (Z+)
    //--     6 - пласть нижняя (Z-)
    //--     7 - Угол 1
    //--     8 - Угол 2
    //--     9 - Угол 3
    //--     10 - Угол 4
    //--     11 - несквозной вырез на верхней пласти
    //--     12 - несквозной вырез на нижней пласти
    //-- ShiftK - Смещение от пласти А в долях толщины
    //-- Dept - Глубина паза или смещение в мм для угла
    //-- Width - Ширина паза или угол в градусах
    //-- Rz1 - Резерв
    //-- Rz2 - Резерв
    //-- Rz3 - Резерв
    '''
    def __init__(self):
        self.Side = None
        self.TypeFr = None
        self.Map = None
        self.ShiftK = None
        self.Dept = None
        self.Width = None
        self.__butt_property = ['Side','TypeFr','Map','ShiftK','Dept','Width','RZ1','RZ2','RZ3'] # упорядоченный список, именно в этой последовательности требуется передавать параметры в К3
        __butt_defvalue = {'Side':1,'TypeFr':0,'Map':1,'ShiftK':0,'Dept':0,'Width':0,'RZ1':0,'RZ2':0,'RZ3':0}
        __butt_permissible = {self.__butt_property[0]:[1,2,3,4,'B','C','D','E'],
                            'D':3,'C':2,'E':4,'B':1,  # СПИСОК ДОПУСТИМЫХ ЗНАЧЕНИЙ Side и подмена строковых значений
                            self.__butt_property[1]:[0,1,2,3,'Not','Slot','Chamfer','Fillet'],
                            'Not':0,'Slot':1,'Chamfer':2,'Fillet':3,  # СПИСОК ДОПУСТИМЫХ ЗНАЧЕНИЙ TypeFr и подмена строковых значений
                            self.__butt_property[2]:[1,2,3,4,5,6,7,8,9,10,11,12,'mB','mC','mD','mE','mA','mF','mAng_1','mAng_2','mAng_3','mAng_4','mFrez_A','mFrez_F'],
                            'mB':4,'mC':3,'mD':2,'mE':1,'mA':5,'mF':6,'mAng_1':7,'mAng_2':8,'mAng_3':9,'mAng_4':10,'mFrez_A':11,'mFrez_F':12}
        # нужна регистронезависимость надо что то придумать с str.lower

        gU.vDefProperty.newAttr('butt_defvalue',__butt_defvalue)
        gU.vDefProperty.newAttr('butt_property',self.__butt_property)
        gU.vDefProperty.newAttr('butt_permissible',__butt_permissible)
        for i in list(gU.vDefProperty.butt_defvalue.items()): # Создаю аттрибуты класса по словарю и задаю значения по умолчанию
                setattr(self, i[0],i[1])

    def __hash__(self):
      return hash((self.Side,self.TypeFr,self.Map,self.ShiftK,self.Dept,self.Width ))

    def setButt(self, Change_Default=False, **curr_butt):
        ''' -- Изменяет свойства торцевой обработки
            -- Входные параметры:

            -- Change_Default по умолчанию False управляет сменой глобальных
            умолчаний при создании нового экземпляра класса butt

            curr_butt словарь, который може иметь значения
            -- Side -  Привязка торцевой обработки
            --          1 - сторона D;
            --          3 - сторона C;
            --          5 - сторона E;
            --          7 - сторона B;
            Пример:
                vbutt_B = butt()
                vbutt_C = butt()
                vbutt_B.setbutt(True,Side='B',  TypeFr='Chamfer')
                vbutt_C.setbutt(TypeFr='Chamfer',  Side='C',)
            '''
        result=gU.setAttrToDict(self,Change_Default,
                                    gU.vDefProperty.butt_property,
                                    gU.vDefProperty.butt_permissible,
                                    gU.vDefProperty.butt_defvalue,
                                    curr_butt)


#------------------------------------------------------------------------------------------

def main():
    pass

if __name__ == '__main__':
    main()
