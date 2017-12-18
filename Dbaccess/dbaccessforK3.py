# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        dbaccessforK3.py
# Purpose:     Модуль связи K3Мебель с базами  MS Access
#
# Author:      Aleksandr Dragunkin
#
# Created:     07.10.2013-2015
# Copyright:   (c) GEOS 2015 http://k3info.ru/
# Licence:     FREE
#-------------------------------------------------------------------------------
"""
Позволяет работать с базами mdb MS Access из среды геометрического редактора К3 Мебель версии 7.3

>>> from dbaccessforK3 import (RecordSet_ACCESS,
...                            DataBase_ACCESS)
... NGuides = DataBase_ACCESS()
... NGuides.adbCon(2)


>>> tab_place=NAME_TEMP_BASE
... Orders = DataBase_ACCESS()
... Orders.adbCon(tab_place)

>>> prc= 'CREATE PROC '+name_table[1:]+' AS '+ prc
... RS = Orders.RecordSetOpen(prc)
... RS.Close()
... SQL_str = ['SELECT * FROM ' + name_table[1:] + ';']
... RS = Orders.RecordSetOpen(SQL_str)

... if RS.count > 0:
...     Orders.modifyQuestToTable(RS, name_table[1:])
... SQL_str = ['DROP TABLE ' + name_table[1:]]
... drpRS = k3.adbmodify(Orders.index,SQL_str[0] )

>>> Orders.adbDisCon() # Разрываем коннект к базе
"""
import k3
import random

import os, sys
from list_reserve_word_access import List_reserve_word_access

class RecordSet_ACCESS(List_reserve_word_access):
    def __init__(self, IdCon=0, SQLStr=[]):
        self.idRS = 0
        self.IdCon = IdCon
        self.count = 0  # число записей
        self.fldcount = 0  # число полей
        self.fldStructure = {}  # индекс: (имя поля, тип, размер)
        if len(SQLStr) > 0:
            self.Open(SQLStr)

    def Open(self, SQLStr):
        if isinstance(SQLStr, str):
            sSQLStr = []
            sSQLStr.append(SQLStr)
            SQLStr = sSQLStr
        self._split_stringSQL(SQLStr)
        N_str = len(SQLStr)
        isPROC = SQLStr[0].split(' ')
        is_proc = isPROC[0] == 'CREATE' and isPROC[1] == 'PROC'
        if self.IdCon > 0 and N_str > 0:
            aTEMP = k3.VarArray(N_str)
            for i in range(N_str):
                aTEMP[i].value = SQLStr[i]
            if is_proc:
                k3.adbdiagnoz(0)            
            self.idRS= k3.adbopen(self.IdCon,aTEMP,N_str)
            if is_proc:
                k3.adbdiagnoz(1)
            if is_proc:
                self.Close()
                self.idRS= k3.adbopen(self.IdCon,'SELECT * FROM '+isPROC[2])
            f1 = k3.adbmovefirst(self.idRS)
            if k3.adbiseof(self.idRS) < 1:
                l1 = k3.adbmovelast(self.idRS)
                f2 = k3.adbmovefirst(self.idRS)
            self.count = self.getRecCount()
            self.fldcount = self.getFldCount()
            self.getFldStructure()

    def _split_stringSQL(self, SQLStr, n_els = 255):
        '''Находит в списке строк SQLStr строки длиннее n_els и делит до тех пор пока в списке не останется строк длиннее n_els'''
        key = True
        while key:
            for s in range(len(SQLStr)):
                l = len(SQLStr[s])
                if l > n_els:
                    oldV = SQLStr[s][:n_els]
                    newV = SQLStr[s][n_els:]
                    SQLStr[s] = oldV
                    SQLStr.insert( s+1, newV)
                    key = True
                    break
                key = False

    def Close(self):
        if self.idRS > 0:
            k3.adbclose(self.idRS)
            self.idRS = 0

    def Modify(self, SQLStr):
        if isinstance(SQLStr, str):
            sSQLStr = []
            sSQLStr.append(SQLStr)
            SQLStr = sSQLStr
        self._split_stringSQL(SQLStr)
        N_str = len(SQLStr)
        if self.IdCon > 0 and N_str > 0:
            aTEMP = k3.VarArray(N_str)
            for i in range(N_str):
                aTEMP[i].value = SQLStr[i]
            self.idRS= k3.adbmodify(self.IdCon,aTEMP,N_str)
            self.Close()

    def getRecCount(self):
        '''возвращает число записей'''
        count = k3.adbreccount(self.idRS)
        return count

    def getFldCount(self):
        '''возвращает число полей'''
        count = k3.adbfldcount(self.idRS)
        return count

    def getFldType(self, i):
        '''возвращает тип поля'''
        res = k3.adbfldtype(self.idRS, i)
        lTypeFld = {'N': 'INTEGER', 'F': 'REAL', 'C': 'VARCHAR', 'L': 'LOGICAL', 'R': 'REAL', 'D':'D', 'B':'B'}
        if res in  list(lTypeFld.keys()):
            result = lTypeFld[res]
        else:
            result = res
        return result

    def getFldSize(self, i):
        '''возвращает размер поля'''
        res = k3.adbfldsize(self.idRS, i)
        return res

    def getFldName(self, i):
        '''возвращает имя поля'''
        res = k3.adbfldname(self.idRS, i)
        if res.upper() in self.list_reserve_word_access():
            res = '[' + res + ']'
        return res

    def getFldStructure(self):
        '''заполняет словарь структурой набора'''
        self.fldStructure = {}  # индекс: (имя поля, тип, размер)
        if self.fldcount is not None:
            for i in range(int(self.fldcount)):
                tp = self.getFldType(i)
                if tp == '?':
                    tp = 'INTEGER'
                self.fldStructure[i] = (self.getFldName(i), tp, int(self.getFldSize(i)),)
                if len(self.fldStructure) == 0:
                    pass
        return  self.fldStructure

#----------------------------------------------
class DataBase_ACCESS(List_reserve_word_access):
    def __init__(self):
        self.tab_place = None    # Положение на диске (полный путь к файлу)
        self.index =  None       # Индекс соединения
        self.list_recordset = [] # Список наборов записей
        self.system_base = {2: 'Proto.mdb', 3: 'App.mdb',}
        self.app_base_path = k3.mpathexpand('<app>')
        self.table = [] # Список таблиц в базе
        
    def adbCon(self, tab_place):
        '''Создает подключение к базе данных MS ACCESS
        
        tab_place - полный путь к базе данных или  2 <NGuides.mdb>, 3<M73Main.mdb>
        index - внутренний индекс соединения
        '''
        try:
            if str(tab_place).isdigit():
                if tab_place in [2, 3]:
                    szSrc = int(tab_place)
                if tab_place == 2:
                    ind = k3.adbcon(3)
                    sqlstr = """SELECT CorePaths.Path FROM CorePaths WHERE (((CorePaths.Name)='Proto'));"""
                    indrs = k3.adbopen(ind, sqlstr)
                    self.tab_place = k3.adbgetvalue(indrs, 0, '0')
                    indrs = k3.adbclose(indrs)
                    result = k3.adbdiscon(ind)
                elif tab_place == 3:
                    self.tab_place = k3.mpathexpand('<commonappdata>') + '\\M73Main.mdb'
            else:
                szSrc="Provider=Microsoft.Jet.OLEDB.4.0;Data Source="+tab_place
                self.tab_place = tab_place
            self.index = k3.adbcon(szSrc)
        except :
            if (k3.fileexist(str(tab_place))==0):
                k3.putmsg("База по адресу "+str(tab_place)+" не обнаружена",0)
                
        return self.index

    def Chkmdb(self, tbl):
        nmbase = self.tab_place
        ex = k3.adbchkmdbtbl(nmbase, tbl)
        return True if int(ex)==1 else False
        
    def adbDisCon(self):
        '''Разрывает текущее соединение'''
        result = None
        # print(self.index)
        if self.index is not None:
            for rs in self.list_recordset:
                rs.Close()
            result = k3.adbdiscon(self.index)
            # print('result=',result)
            self.index = None
        
        return result
    
    def addIndex(self, index=0):
        '''Добавляем уже существующий индекс подключения'''
        # print(index)
        self.index = index
    
    def str_random_name(self, qty = 8):
            symbols = ''
            for i in range(qty):
                num = int(random.random() * (122 - 97 + 1)) + 97
                symbols = symbols + chr(num)
            return symbols
        
    def getStructure(self, nmbase=''):
        nm = self.str_random_name()
        if len(nmbase) == 0 :
            nmbase = self.tab_place
        n = int(k3.adblisttable(nmbase, nm)) # Получаем список таблиц базы заказа
        aTable = k3.VarArray(n, nm)
        list_table = [aTable[j].value for j in list(range(n)) ] # превращаем массив к3 в список
        self.table = list_table
        return list_table

    def RecordSetOpen(self, list_SQL_Str):
        '''Возвращает набор записей'''
        if len(list_SQL_Str) > 0:
            RS = RecordSet_ACCESS(self.index, list_SQL_Str)
            self.list_recordset.append(RS)
            return RS
        else:
            return 0

    def RecordSetModify(self, list_SQL_Str):
        '''Возвращает набор записей'''
        if len(list_SQL_Str) > 0:
            RS = RecordSet_ACCESS(self.index)
            RS.Modify(list_SQL_Str)
            return True
        else:
            return False

    def RecordSetClose(self, RS):
        if RS in self.list_recordset:
            RS.Close()
            self.list_recordset.remove(RS)

    def getFieldInfo(self,nameTable):
        '''возвращает список кортежей полей таблицы
        имя поля, Тип поля'''
        RS = self.RecordSetOpen(['SELECT * FROM '+nameTable])
        n_fld = int(k3.adbfldcount(RS.idRS)) # Число полей
        res = []
        for i_fld in range(n_fld):
            fldname = k3.adbfldname(RS.idRS, i_fld)
            fldname = self.reserved_word(fldname)
            fldtype = k3.adbfldtype(RS.idRS, i_fld)
            res.append((fldname, fldtype))
        RS.Close()
        return res

    def reserved_word(self, fldname):
        if fldname.upper() in  self.list_reserve_word_access():
            fldname = '[' + fldname + ']'
        return fldname

    def modifyQuestToTable(self, RS, NameTable):
        '''Преобразует запрос в таблицу'''
        result = False
        if len(NameTable) > 0:
            dps = 'T'
            isid_AUTO = ''  if 'id_AUTO' in [i_rs[0] for i_rs in RS.fldStructure.values()] else 'id_AUTO AUTOINCREMENT PRIMARY  KEY, '
            if NameTable in ['Slots','TSlots' ]:
                pass
            if dps + NameTable not in self.getStructure(nmbase=self.tab_place):
                SQLStr = 'CREATE TABLE T' + NameTable + ' ('+ isid_AUTO
                for i in list(RS.fldStructure.keys()):
                    vSize = '('+ str(RS.fldStructure[i][2])+ ')' if RS.fldStructure[i][1] == 'VARCHAR' else ''
                    SQLStr=SQLStr + self.reserved_word(RS.fldStructure[i][0])+ ' '+ RS.fldStructure[i][1]+ vSize+ ', '
                SQLStr = SQLStr[:-2] + ');'
                result = self.RecordSetModify(SQLStr)
            if RS.count > 0:
                tSS = self.RecordSetOpen([' SELECT * FROM ' + NameTable])
                tSS.Close()
                l_id_AUTO = 'id_AUTO' in [i_rs[0] for i_rs in tSS.fldStructure.values()]
                k3.adbdiagnoz(0)
                if not l_id_AUTO:
                    self.RecordSetModify('ALTER TABLE T' + NameTable + ' ADD COLUMN id_AUTO AUTOINCREMENT')
                else:
                    self.RecordSetModify('ALTER TABLE T' + NameTable + ' ALTER COLUMN id_AUTO AUTOINCREMENT')
                
                self.RecordSetModify('ALTER TABLE T' + NameTable + ' ADD PRIMARY KEY (id_AUTO)')
                k3.adbdiagnoz(1)
                if l_id_AUTO:
                    s = ''
                    for ts in tSS.fldStructure.values():
                        s = s + (ts[0] + ', ' if ts[0] !='id_AUTO' else '')
                    s = s[:-2]
                    SQLStr = 'INSERT INTO ' + dps + NameTable + '('+ s + ')' ' SELECT '+ s + ' FROM ' + NameTable
                else:
                    s = ' * '
                    SQLStr = 'INSERT INTO ' + dps + NameTable + ' SELECT '+ s + ' FROM ' + NameTable
                result = self.RecordSetModify(SQLStr)
        return result

#---------------------------------------------------
class adbFunktion:
    def PropInfo(self,ID,Name, defVal=0, Typ=1):
        '''возвращает значение свойство Name изделия с ID из базы'''
        result=None
        #try:
        result=k3.Var()
        result=k3.priceinfo(ID,Name,defVal,Typ)
        #except KeyError, ID,Name:
            #raise AttributeError, ID
        return result

    def NmPropInfo(self,ID,Name, defVal=1):
        '''возвращает значение свойства номенклатуры из базы'''
        return self.PropInfo(ID, Name, defVal, 1)

    def GoodsPropInfo(self,ID,Name):
        '''возвращает значение свойства сборки из базы'''
        return self.PropInfo(ID, Name, 0, 2)

    def getThicknessMaterial(self, ID):
        '''возвращает толщину материала из базы'''
        return self.NmPropInfo(ID,'Thickness')