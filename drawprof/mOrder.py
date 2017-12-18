# -*- coding: utf-8 -*-
#---------------------------------------------------------------------
# Name:        mOrder.py
# Purpose:     Модуль работы с заказом в к3мебель
#
# Author:      Aleksandr Dragunkin
#
# Created:     25.09.2015
# Copyright:   (c) GEOS 2015 http://k3info.ru/
# Licence:     FREE
#----------------------------------------------------------------------
# import wingdbstub

from SingletonMetaClass import Singleton

import k3

class tOrderInfo:
    """
    from mOrder import (tOrderInfo, )
    
    ORDERINFO = tOrderInfo()
    
    sheet.Cells(3,2).value = ORDERINFO.info['Customer'] # Название объекта
    sheet.Cells(4,2).value = ORDERINFO.info['Number']   # Название позиции
    sheet.Cells(5,2).value = ORDERINFO.info['Name']     # Номер позиции
    sheet.Cells(6,2).value = ORDERINFO.info['Address']  # Количество
    """
    def __init__(self):
        self.geti()
        self.id_order = k3.sysvar(2).split('\\')[-2]
        self.path_order = k3.mpathexpand("<PROJECTS>")
        
    def geti(self):
        self.info = {}
        vName=['Name',
               'Number',
               'Customer',
               'Address',
               'Phone',
               'Date',
               'ExpDate',
               'Firm',
               'Salon',
               'Acceptor',
               'Executor',
               'AddInfo',
               'ToWorking',
               'NCurrency',
               'Discount',
               'Rate']
        for nm in vName:
            self.info[nm] = k3.getorderinfo(nm)
        return self.info
    
