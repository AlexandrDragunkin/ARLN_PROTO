# -*- coding: cp1251 -*-
#-------------------------------------------------------------------------------
# Name:        LayerFun
# Purpose:
#
# Author:      Dragunkin Aleksandr
#
# Created:     11.04.2014
# Copyright:   (c) GEOS 2014
# Licence:     FREE
#-------------------------------------------------------------------------------
#import  wingdbstub
import k3



class LayerFun:
    def countLayers(self):
        '''������� ���������� ���������� ������������, �� ��������� �����'''
        return int(k3.countlayers())

    def getLayer(self, Obj):
        '''������� ���������� ��� ����, �������� ����������� ������ < Obj> '''
        return k3.getlayer(Obj)

    def getNameLayersAll(self):
        '''���������� ������ ������ ���� ����� � �� ��������� ���/���� '''
        arrname, arrprop = k3.VarArray(self.countLayers()), k3.VarArray(self.countLayers())
        result = k3.namelayers(arrname, arrprop)
        return ([a.value for a in arrname], [i.value for i in arrprop])

    def getExistsLayerAll(self):
        '''���������� ������� , ��� ������ �������� ��� ������������� ����, � ��������� �������� ������ ��������� �������, ����������'''
        layer_c=self.getNameLayersAll()
        layer_d = {}
        keyOFF, keyLOCK = k3.Var(), k3.Var()
        f = lambda name: int(k3.existslayer(name, keyOFF, keyLOCK))
        fIB = lambda I: False if abs(I-0.01) > 0.02 else True
        for l in  layer_c[0]:
            if f(l) > 0:
                layer_d[l] = (fIB(keyOFF.value), fIB(keyLOCK.value))
        return layer_d

    def getListFreeLayer(self):
        '''���������� ������ ������ �����'''
        from  Utilites_K3 import  getListArrayAllObjectsScene
        dLayerAll = self.getExistsLayerAll()
        lstLayerAll = dLayerAll.keys()
        lstObj = getListArrayAllObjectsScene()
        reservName = self.getListFreeName()
        reservName = list(set(reservName)) # ������� ���������
        if len(lstLayerAll) > 0:
            
            for nm in reservName:
                if nm in lstLayerAll:
                    lstLayerAll.remove(nm)
             
        for lobj in lstObj:
            for l in  lobj:
                nm = self.getLayer(l.value)
                if nm in lstLayerAll:
                    lstLayerAll.remove(nm)
        return lstLayerAll

    def getListFreeName(self):
        '''���������� ������ ���� �����, ������� ������ �������, ���� ���� ��� ���������.
        ���� ������� �� ����� '''
        file_name = k3.mpathexpand("<proto>")+"\\freelname.txt"
        resFFile = int(k3.fileexist(file_name)) # ��������� ���� �� ���� � �����������
        res = ['0']
        if resFFile==1: # ������ ���� ������
            nStr= int(k3.getcount(file_name))
            for i in range(1, nStr+1):
                s = k3.getstr(file_name,i).strip()
                if s not in ['', '0']:
                    res.append(s)
        return res

    def delListFreeLayerAll(self, nm):
        k3.layers(k3.k_delete, nm)

def delFreeLayer():
    lfun = LayerFun()
    layer_d = lfun.getExistsLayerAll()
    dd = lfun.getListFreeLayer()
    for ll in  dd:
        lfun.delListFreeLayerAll(ll)

#-------------------------------------------------------------------------------
if __name__ == '__main__':
    delFreeLayer()
