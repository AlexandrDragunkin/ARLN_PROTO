# -*- coding: cp1251 -*-
#-------------------------------------------------------------------------------
# Name:        mBand
# Purpose:     Кромки в панели
#
# Author:      Aleksandr Dragunkin
#
# Created:     31.10.2012
# Copyright:   (c) GEOS 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import gUtilitesK3 as gU
#-------------------------------------------------------------------------------

class Band:
    ''' Кромка на панель.
        По сторонам 'B','C','D','E' и углам 'Ang_1','Ang_2','Ang_3','Ang_4'

    '''
    def __init__(self):
        self.Side = None
        self.Material = None
        self.BandMask = None
        __band_property = ['Side','Material'] # упорядоченный список, именно в этой последовательности требуется передавать параметры в К3
        __band_defvalue = {'Side':1,'Material':0}
        __band_permissible = {__band_property[0]:[1,2,3,4,5,6,7,8,'B','C','D','E','Ang_1','Ang_2','Ang_3','Ang_4'],
                            'D':1,'C':3,'E':5,'B':7,'Ang_1':2,'Ang_2':4,'Ang_3':6,'Ang_4':8}  # СПИСОК ДОПУСТИМЫХ ЗНАЧЕНИЙ Side и подмена строковых значений
        # нужна регистронезависимость надо что то придумать с str.lower

        gU.vDefProperty.newAttr('band_defvalue',__band_defvalue)
        gU.vDefProperty.newAttr('band_property',__band_property)
        gU.vDefProperty.newAttr('band_permissible',__band_permissible)
        for i in list(gU.vDefProperty.band_defvalue.items()): # Создаю аттрибуты класса по словарю и задаю значения по умолчанию
                setattr(self, i[0],i[1])

    def __hash__(self):
        return hash((self.Side, self.Material, self.BandMask))

    def setBand(self, Change_Default=False, **curr_band):
        ''' -- Изменяет свойства кромки
            -- Входные параметры:

            -- Change_Default по умолчанию False управляет сменой глобальных
            умолчаний при создании нового экземпляра класса band

            curr_band словарь, который може иметь значения
            -- Side -  Привязка кромки
            --          1 - сторона D;
            --          3 - сторона C;
            --          5 - сторона E;
            --          7 - сторона B;
            --          2 - 'Ang_1' - угол 1
            --          4 - 'Ang_2' - угол 2
            --          6 - 'Ang_3' - угол 3
            --          8 - 'Ang_4' - угол 4
            -- Material - ID кромки из справочника номенклатуры

            Пример:
                vband_B = Band()
                vband_C = Band()
                vband_B.setBand(True,Side='B',  Material=5030)
                vband_C.setBand(Material=5025,  Side='C',)
            '''
        result=gU.setAttrToDict(self,Change_Default,
                                    gU.vDefProperty.band_property,
                                    gU.vDefProperty.band_permissible,
                                    gU.vDefProperty.band_defvalue,
                                    curr_band)


#------------------------------------------------------------------------------------------

def main():
    pass

if __name__ == '__main__':
    main()
