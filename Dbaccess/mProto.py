# -*- coding: utf-8 -*-
#---------------------------------------------------------------------
# Name:        mProto.py
# Purpose:     Модуль работы с прототипом в к3мебель
#
# Author:      Aleksandr Dragunkin
#
# Created:     22.07.2015
# Copyright:   (c) GEOS 2015 http://k3info.ru/
# Licence:     FREE
#----------------------------------------------------------------------
# import wingdbstub

from dbaccessforK3 import (RecordSet_ACCESS,
                           DataBase_ACCESS)

from SingletonMetaClass import Singleton

import k3

class Prop_nomenclature(Singleton):
    def __init__(self):
        self.list_prop_ient = self.get_nomenclature_property()
    #----------------------------------------------------------------------
    def get_nomenclature_property(self):
        """Определяем список доступных имен (идентификаторов) свойств номенклатуры"""
        NGuides = DataBase_ACCESS()
        NGuides.adbCon(2)    
        sqlstr = ["""SELECT NProperties.Ident FROM NProperties;"""]
        rs = NGuides.RecordSetOpen(sqlstr)
        lrs = []
        if rs.count > 0:
            k3.adbmovefirst(rs.idRS)
            while k3.adbiseof(rs.idRS) == 0:
                lrs.append(k3.adbgetvalue(rs.idRS,'Ident','0'))
                k3.adbmovenext(rs.idRS)
        rs.Close()
        NGuides.adbDisCon()
        return lrs

#----------------------------------------------------------------------
def get_proto_property(con, id_proto):
    """Определяем список свойств прототипа"""
    
    sqlstr = ["""SELECT TProtoPar.ParName, TProtoPar.ParPrompt, TProtoCategory.Category, TProtoCategory.ID AS IDCategory FROM TProtoCategory INNER JOIN TProtoPar ON TProtoCategory.ID = TProtoPar.CategoryID WHERE (((TProtoPar.ProtoID)="""+ str(int(id_proto))+"""))
    ORDER BY TProtoPar.ParName;"""]
    rs = con.RecordSetOpen(sqlstr)
    lrs = []
    if rs.count > 0:
        k3.adbmovefirst(rs.idRS)
        while k3.adbiseof(rs.idRS) == 0:
            lrs.append([k3.adbgetvalue(rs.idRS,'ParName','0'), k3.adbgetvalue(rs.idRS,'ParPrompt','0'), k3.adbgetvalue(rs.idRS,'Category','0'), k3.adbgetvalue(rs.idRS,'IDCategory',0)])
            k3.adbmovenext(rs.idRS)
    rs.Close()
    return lrs

#----------------------------------------------------------------------
def read_current_property_proto(id_proto):
    """Читает текущие параметры прототипа"""
    NGuides = DataBase_ACCESS()
    NGuides.adbCon(2)
    NGuides.getStructure()
    try:
        lrs = get_proto_property(NGuides, id_proto)
    except:
        print('Похоже, что нет такого прототипа')
    NGuides.adbDisCon()
    if len(lrs)>0:
        for pr in lrs:
            pr.append(k3.dbvar(pr[0], 0))    
    return lrs

#----------------------------------------------------------------------
def getprotoval(h, name):
    v = k3.Var()
    if k3.getprotoval(h, name, v) > 0:
        return v.value
    else:
        return None