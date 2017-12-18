# -*- coding: cp1251 -*-
#-------------------------------------------------------------------------------
# Name:        mSlot
# Purpose:     ������(���) � ������
#
# Author:      Aleksandr Dragunkin
#
# Created:     31.10.2012
# Copyright:   (c) GEOS 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
import gUtilitesK3 as gU
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
class Slot:
    '''������ � ������'''
    def __init__(self):
        self.Plane = None
        self.Side = None
        self.Shift = None
        self.Width = None
        self.Depth = None
        self.Beg = None
        self.Length = None
        self.Angle = None
        self.Map = None
        self.__slot_property = ['Plane','Side','Shift','Width','Depth','Beg','Length','Angle','Map'] # ������������� ������, ������ � ���� ������������������ ��������� ���������� ��������� � �3
        __slot_defvalue = {'Plane':0,'Side':1,'Shift':15,'Width':4,'Depth':8,'Beg':0,'Length':0,'Angle':0,'Map':1}
        __slot_permissible = {self.__slot_property[1]:[1,3,5,7,9,0,'D','C','E','B'],
                            self.__slot_property[0]:[1,0,'A','F'],
                            'A':1,'F':0,'D':1,'C':3,'E':5,'B':7}  # ������ ���������� �������� Side � Plane
        # ����� ��������������������� ���� ��� �� ��������� � str.lower

        gU.vDefProperty.newAttr('slot_defvalue',__slot_defvalue)
        gU.vDefProperty.newAttr('slot_property',self.__slot_property)
        gU.vDefProperty.newAttr('slot_permissible',__slot_permissible)
        for i in list(gU.vDefProperty.slot_defvalue.items()): # ������ ��������� ������ �� ������� � ����� �������� �� ���������
                setattr(self, i[0],i[1])

    def setSlot(self, Change_Default=False,  **curr_slot):
        ''' -- �������� �������� �������
            -- ������� ��������� curr_slot �������, ������� ���� ����� ��������
            -- Plane - ������ ������� (1 - �, 0 - F)
            -- Side -  �������� �������
            --          1 - ������� D;
            --          3 - ������� C;
            --          5 - ������� E;
            --          7 - ������� B;
            --          9 - ��������� ��������;
            --          0 - ������� ��� �������
            -- Shift - ������ �� �������
            -- Width - ������
            -- Depth - �������
            -- Beg - ����� �� ������
            -- Length - �����. 0 - ��� ������������, -1 - ��� �������������
            -- Angle - ����
            -- Map - ����� ������ �������������

            -- Change_Default �� ��������� False ��������� ������ ����������
            ��������� ��� �������� ������ ���������� ������ Slot

            ������:
                vSlot_A = mS.Slot()
                vSlot_F = mS.Slot()
                vSlot_A.setSlot(True,Plane='A',
                               Side='B')
                vSlot_F.setSlot(False,
                Plane='F',
                Side='D')
            '''
        result=gU.setAttrToDict(self,Change_Default,
                                    gU.vDefProperty.slot_property,
                                    gU.vDefProperty.slot_permissible,
                                    gU.vDefProperty.slot_defvalue,
                                    curr_slot)

def main():
    pass

if __name__ == '__main__':
    main()
