# -*- coding: cp1251 -*-

#-------------------------------------------------------------------------------
# Name:        mKarcas
# Purpose:      Каркас
#
# Author:      Aleksandr Dragunkin
#
# Created:     10.12.2012
# Copyright:   (c) GEOS 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from k3 import *

class Karkas:
    def __init__(self,TypKar = 0, Orient = 0,
                        W = 1000, T = 650, H = 2000,
                                    Wmins = 0, Tmins = 0, MaskContact=0):
        self.typkar = TypKar
        self.orient = Orient
        self.wd = W
        self.th = T
        self.hi = H
        self.wmins = Wmins
        self.tmins = Tmins
        self.mskCont = MaskContact

    def make(self, X=0, Y=0, Z=0):
        kArr = VarArray(10)
        nullout = initarray(kArr,0.0)
        nullout = setcarcpar(1.0,kArr)
        kArr[0].value = self.typkar
        nullout = setcarcpar(2.0,kArr)
        kArr[0].value = self.orient
        kArr[1].value = self.wd
        kArr[2].value = self.th
        kArr[3].value = self.hi
        kArr[4].value = self.wmins
        kArr[5].value = self.tmins
        nullout = setcarcpar(3.0,kArr)
        kArr[0].value = self.mskCont
        nullout = setcarcpar(4.0,kArr)

        err = mbcarcase(k_create,X,Y,Z)
        nullout = initarray(kArr,0.0)
        nullout = setcarcpar(999,kArr)


def main():
    pass

if __name__ == '__main__':
    main()
