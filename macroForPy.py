# -*- coding: cp1251 -*-

#-------------------------------------------------------------------------------
# Name:        macroForPy
# Purpose:     ����� �������� � ��� ��� � ��� ������� ��� python 3.3
#
# Author:      Aleksandr Dragunkin
#
# Created:     15.01.2014
# Copyright:   (c) GEOS 2013 http://k3info.ru/
# Licence:     FREE
#-------------------------------------------------------------------------------
import k3

def _ProtoPath():
    '''���������� �������� ���������� ���������� ProtoPath'''
    return k3.GlobalVar('ProtoPath').value

def _k3files():
    '''���������� �������� ��������� ���������� k3files'''
    return k3.mpathexpand("<k3files>")

def setk3Var(vt=[]):
    '''����������� ������ �������� � ������ ���������� k3 � ����������� ����� k3.k_byref'''
    def _lset(v):
        t = k3.Var()
        # print(type(v))
        if type(v) in [str, int, float]: 
            t.value = v 
            return (k3.k_byref, t)
        elif type(v) == k3.VarArray: 
            t = v 
            #return t
            return (k3.k_byref, t)
        elif isinstance(v,k3.K3Obj):
            t.value = v 
            return (k3.k_byref, t)
        elif type(v) == k3.Var:
            t = v
            return (k3.k_byref, t)
        else: 
          return None
    return [_lset(x) for x in vt]

def runMacro(Name, v=[], path=_ProtoPath()):
    '''��������� �� ����������� ������ �3 � ������ Name �� ����� path  � ����������� � ������ v'''
    # print(path+Name)
    # print(setk3Var(v))
    return k3.macro(path+Name, setk3Var(v), k3.k_done)