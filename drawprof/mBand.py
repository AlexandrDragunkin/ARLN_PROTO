# -*- coding: cp1251 -*-
#-------------------------------------------------------------------------------
# Name:        mBand
# Purpose:     ������ � ������
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
    ''' ������ �� ������.
        �� �������� 'B','C','D','E' � ����� 'Ang_1','Ang_2','Ang_3','Ang_4'

    '''
    def __init__(self):
        self.Side = None
        self.Material = None
        self.BandMask = None
        __band_property = ['Side','Material'] # ������������� ������, ������ � ���� ������������������ ��������� ���������� ��������� � �3
        __band_defvalue = {'Side':1,'Material':0}
        __band_permissible = {__band_property[0]:[1,2,3,4,5,6,7,8,'B','C','D','E','Ang_1','Ang_2','Ang_3','Ang_4'],
                            'D':1,'C':3,'E':5,'B':7,'Ang_1':2,'Ang_2':4,'Ang_3':6,'Ang_4':8}  # ������ ���������� �������� Side � ������� ��������� ��������
        # ����� ��������������������� ���� ��� �� ��������� � str.lower

        gU.vDefProperty.newAttr('band_defvalue',__band_defvalue)
        gU.vDefProperty.newAttr('band_property',__band_property)
        gU.vDefProperty.newAttr('band_permissible',__band_permissible)
        for i in list(gU.vDefProperty.band_defvalue.items()): # ������ ��������� ������ �� ������� � ����� �������� �� ���������
                setattr(self, i[0],i[1])

    def __hash__(self):
        return hash((self.Side, self.Material, self.BandMask))

    def setBand(self, Change_Default=False, **curr_band):
        ''' -- �������� �������� ������
            -- ������� ���������:

            -- Change_Default �� ��������� False ��������� ������ ����������
            ��������� ��� �������� ������ ���������� ������ band

            curr_band �������, ������� ���� ����� ��������
            -- Side -  �������� ������
            --          1 - ������� D;
            --          3 - ������� C;
            --          5 - ������� E;
            --          7 - ������� B;
            --          2 - 'Ang_1' - ���� 1
            --          4 - 'Ang_2' - ���� 2
            --          6 - 'Ang_3' - ���� 3
            --          8 - 'Ang_4' - ���� 4
            -- Material - ID ������ �� ����������� ������������

            ������:
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
