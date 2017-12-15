# -*- coding: cp1251 -*-
#-------------------------------------------------------------------------------
# Name:        mButts
# Purpose:     �������� ��������� � ������
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
    ''' �������� ��������� �� ������.
    //-- Side - ������� (1- B, 2 - C, 3 - D, 4 - E)
    //-- TypeFr - ��� �������� ���������:
    //--     0 - ��� ���������
    //--     1 - ������������� ���
    //--     2 - ����
    //--     3 - ����������
    //-- Map - ������ �������������
    //--     1 - ����� E (Y+)
    //--     2 - ����� D (Y-)
    //--     3 - ����� C (X+)
    //--     4 - ����� B (X-)
    //--     5 - ������ ������� (Z+)
    //--     6 - ������ ������ (Z-)
    //--     7 - ���� 1
    //--     8 - ���� 2
    //--     9 - ���� 3
    //--     10 - ���� 4
    //--     11 - ���������� ����� �� ������� ������
    //--     12 - ���������� ����� �� ������ ������
    //-- ShiftK - �������� �� ������ � � ����� �������
    //-- Dept - ������� ���� ��� �������� � �� ��� ����
    //-- Width - ������ ���� ��� ���� � ��������
    //-- Rz1 - ������
    //-- Rz2 - ������
    //-- Rz3 - ������
    '''
    def __init__(self):
        self.Side = None
        self.TypeFr = None
        self.Map = None
        self.ShiftK = None
        self.Dept = None
        self.Width = None
        self.__butt_property = ['Side','TypeFr','Map','ShiftK','Dept','Width','RZ1','RZ2','RZ3'] # ������������� ������, ������ � ���� ������������������ ��������� ���������� ��������� � �3
        __butt_defvalue = {'Side':1,'TypeFr':0,'Map':1,'ShiftK':0,'Dept':0,'Width':0,'RZ1':0,'RZ2':0,'RZ3':0}
        __butt_permissible = {self.__butt_property[0]:[1,2,3,4,'B','C','D','E'],
                            'D':3,'C':2,'E':4,'B':1,  # ������ ���������� �������� Side � ������� ��������� ��������
                            self.__butt_property[1]:[0,1,2,3,'Not','Slot','Chamfer','Fillet'],
                            'Not':0,'Slot':1,'Chamfer':2,'Fillet':3,  # ������ ���������� �������� TypeFr � ������� ��������� ��������
                            self.__butt_property[2]:[1,2,3,4,5,6,7,8,9,10,11,12,'mB','mC','mD','mE','mA','mF','mAng_1','mAng_2','mAng_3','mAng_4','mFrez_A','mFrez_F'],
                            'mB':4,'mC':3,'mD':2,'mE':1,'mA':5,'mF':6,'mAng_1':7,'mAng_2':8,'mAng_3':9,'mAng_4':10,'mFrez_A':11,'mFrez_F':12}
        # ����� ��������������������� ���� ��� �� ��������� � str.lower

        gU.vDefProperty.newAttr('butt_defvalue',__butt_defvalue)
        gU.vDefProperty.newAttr('butt_property',self.__butt_property)
        gU.vDefProperty.newAttr('butt_permissible',__butt_permissible)
        for i in list(gU.vDefProperty.butt_defvalue.items()): # ������ ��������� ������ �� ������� � ����� �������� �� ���������
                setattr(self, i[0],i[1])

    def __hash__(self):
      return hash((self.Side,self.TypeFr,self.Map,self.ShiftK,self.Dept,self.Width ))

    def setButt(self, Change_Default=False, **curr_butt):
        ''' -- �������� �������� �������� ���������
            -- ������� ���������:

            -- Change_Default �� ��������� False ��������� ������ ����������
            ��������� ��� �������� ������ ���������� ������ butt

            curr_butt �������, ������� ���� ����� ��������
            -- Side -  �������� �������� ���������
            --          1 - ������� D;
            --          3 - ������� C;
            --          5 - ������� E;
            --          7 - ������� B;
            ������:
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
