# -*- coding: cp1251 -*-
#-------------------------------------------------------------------------------
# Name:        gUtilitesK3
# Purpose:     ������� ������ ����������
#
# Author:      Aleksandr Dragunkin
#
# Created:     31.10.2012
# Copyright:   (c) GEOS 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
class DefaultProperty:
    '''����� ��� �������� ��������� � ���������� vDefProperty'''
    def __init__(self):
        pass
    def newAttr(self,NameAttr,v):
        '''������� ����� �������� ������
            ������� ���������
            -- NameAttr ��� ���������
            -- v ��������
        ��������: vDefProperty.newAttr('slot_property',__slot_property)
        '''
        if getattr(self,NameAttr,True):
            setattr(self, NameAttr,v)

vDefProperty=DefaultProperty() # ��� ���������� ��������� ���������

#-------------------------------------------------------------------------------
def is_permissible(val, t):
    '''���� val � ������ ��� ������ ������� t
    ��������� True ��� False'''
    if type(t)==list:
        try:
            i_el=t.index(val)
        except:
            return False
        return True
    elif type(t)==dict:
        return val in  t #t.has_key(val)
#-------------------------------------------------------------------------------

def setAttrToDict(self,Change_Default,attr_property,attr_permissible,attr_defvalue,dict_Attr):
    ''' �������� �������� ��������� ������ �� ������� ����������� �� ������ ������������� ����������.
        ���������� ������ � ������ �������������� ���������� ��� ���� � ������ ������

        ������� ���������:
        -- Change_Default �� ��������� False ��������� ������ ����������
            ��������� attr_defvalue ��� �������� ������ ���������� ������
        -- attr_property ������ ���������� ����
        -- attr_permissible ������� ���������� ��������
        -- attr_defvalue ���������� ��������� ���������
        -- dict_Attr ������� �������� ��������

        ������:

    '''
    try:
        for i in list(dict_Attr.items()): # ������� �������. ��������� �������� �������
            val = i[1]
            if is_permissible(i[0], attr_property): # ������� ������� �������� � �������
            #---
            # ������ ��������� �� ������ ������� ���������� ����������� ������� � �����

                if is_permissible(i[0], attr_permissible): # ���� �� ���������� �� ��������
                    if is_permissible(i[1], attr_permissible[i[0]]):
                        if type(i[1])==str:
                            val = attr_permissible[i[1]]
                    else:
                        print(('�������� ', i[0],' ������������.  ', i[1], ' ����������� � ������ ',attr_permissible[i[0]]))
                        break
            #----
                if Change_Default: attr_defvalue[i[0]]=i[1] # �������� �������� ���������
                setattr(self, i[0],val)  # ������ ��������� ������ �� ������� � ����� �������� �� ���������
            else:
                print((i[0], ' ����������� � ������ ', attr_property))
        return True
    except:
        return False
#-------------------------------------------------------------------------------
def change_attrs(objs=[], attrs=[], values=[]):
    '''����� �������� � ������ �������� �� ������ ���������'''
    for obj in objs: # �������� �� ������ ������� �� �������
        for a, v in zip(attrs, values): # a ��� ������� ������� �� ������ attrs v �� ������ values
            if a in obj.__dict__:  # obj.__dict__ ��� ������ �������� ������� ���� � ��� ���� �������, ��
                obj.__dict__[a] = v # ������ ��� �������� �� ��������

def main():
    pass

if __name__ == '__main__':
    main()
