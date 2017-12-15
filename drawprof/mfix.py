# -*- coding: cp1251 -*-
#-------------------------------------------------------------------------------
# Name:        mfix
# Purpose:     ������ � ������
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
    ''' ������ �� ������.
        �� �������� 'B','C','D','E' � ����� 'Ang_1','Ang_2','Ang_3','Ang_4'

    '''
    def __init__(self):
        self.Side = 1
        self.fixID = 0
        self.fixMask = 0
        __fix_property = ['Side','fixID','fixMask'] # ������������� ������, ������ � ���� ������������������ ��������� ���������� ��������� � �3
        __fix_defvalue = {'Side':self.Side,'fixID':self.fixID,'fixMask':self.fixMask}
        __fix_permissible = {__fix_property[0]:[1,2,3,4,5,6,7,8,'B','C','D','E','Ang_1','Ang_2','Ang_3','Ang_4'],
                            'D':3,'C':2,'E':4,'B':1,'Ang_1':5,'Ang_2':6,'Ang_3':7,'Ang_4':8}  # ������ ���������� �������� Side � ������� ��������� ��������
        # ����� ��������������������� ���� ��� �� ��������� � str.lower

        gU.vDefProperty.newAttr('fix_defvalue',__fix_defvalue)
        gU.vDefProperty.newAttr('fix_property',__fix_property)
        gU.vDefProperty.newAttr('fix_permissible',__fix_permissible)
        for i in list(gU.vDefProperty.fix_defvalue.items()): # ������ ��������� ������ �� ������� � ����� �������� �� ���������
                setattr(self, i[0],i[1])

    def __hash__(self):
        return hash((self.Side, self.fixID, self.fixMask))

    def setFix(self, Change_Default=False, **curr_fix):
        ''' -- �������� �������� �������
            -- ������� ���������:

            -- Change_Default �� ��������� False ��������� ������ ����������
            ��������� ��� �������� ������ ���������� ������ fix

            curr_fix �������, ������� ���� ����� ��������
            -- Side -  �������� �������
            --          1 - ������� D;
            --          3 - ������� C;
            --          5 - ������� E;
            --          7 - ������� B;
            --          2 - 'Ang_1' - ���� 1
            --          4 - 'Ang_2' - ���� 2
            --          6 - 'Ang_3' - ���� 3
            --          8 - 'Ang_4' - ���� 4
            ������:
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
    '''��������� ����� �������'''
    def __init__(self, xn=0, yn=0, zn=0,   #-- ������ ����� �������
                 xv=0, yv=0, zv=0,         #-- ����� �� ��� Z ��� ����� �������
                 xt=0, yt=0, zt=0,         #-- ����� ����� �������
                 FixType=0                 #-- ��� �������
                 ):
        self.FixLine = (xn, yn, zn,   #-- ������ ����� �������
                        xv, yv, zv,   #-- ����� �� ��� Z ��� ����� �������
                        xt, yt, zt)  #-- ����� ����� �������
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