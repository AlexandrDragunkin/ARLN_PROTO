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

class Mpathexpand(Singleton):
    PROTOPATH = k3.mpathexpand("<Proto>")
    PROJECTS = k3.mpathexpand("<PROJECTS>")
    APPDATA = k3.mpathexpand("<AppData>")
    REPORTS = k3.mpathexpand("<reports>")
    K3FILESPATH = k3.mpathexpand("<k3files>")