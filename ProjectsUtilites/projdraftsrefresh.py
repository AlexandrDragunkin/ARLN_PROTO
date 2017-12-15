# -*- coding: utf-8 -*-
"""
Изменяет данные проекта во всех чертежах в соответствии с параметрами заказа
"""

import k3
#import wingdbstub
#import substdirs as SB
from Utilites_K3 import getListArrayAllObjectsScene



def main():
    Params = k3.getpar()
    if k3.fileexist(Params[0]):
        k3.append(fn)
        lt = getListArrayAllObjectsScene(AttrFilter='IPRLNDW0==1')