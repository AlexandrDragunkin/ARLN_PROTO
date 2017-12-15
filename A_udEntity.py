# -*- coding: utf-8 -*-

# Переделать бы на работу без К3

import k3
from dbaccessforK3 import (RecordSet_ACCESS,
                           DataBase_ACCESS, )

base = DataBase_ACCESS()
base.adbCon(3)

# ID	Name
# 1	    Целое число
# 2	    Вещественное число
# 3	    Логическое значение
# 4	    Строка текста
# 5	    Набор значений (TProtoSubst ComboBox)
# 6	    Номер цвета (0..239) Диалог выбора цвета
# 7	    Набор значений (TProtoSubst CDialog от KindID)
# 8	    Набор значений (MPS-TProtoSubst CDialog от KindID)
# 9	    Набор файлов (Диалог выбора по картинке)
# 10	Номер типа линии (0..n) Диалог выбора типа линии
# 11	Текстурный материал Lb.pkm6_3_iml.#11
# 12	Комбинированный список (ComboBox)
# 13	32-разрядная битовая маска
# 14	ComboBox из записей NVirt с Furntype like <Property>
# 15	ComboBox из значений многозначого свойства <Property> назначенного значению параметра <DependenceName>
# 16	ComboBox из записей NGoods с Furntype like <Property>
# 17	ComboBox из значений многозначного свойства <Property> назначенного значению параметра <DependenceName>
# 18	ComboBox из select SValue from [Orders.mdb].Substs where Name = <udEntity.Property>

KeyReLoad = False

dGroupName = {
"ARLine" : "Арлиные умолчания",
"Decors" : "Отделки",
}
k3.setyadsubst(83,338)
dGroup = {
"ARLine" :
  {
  'FullPorting' : { "Name" : "Полная присадка на заказ",
                    "VarType" : 3,
                    "data2" : 0,
                    "Sort" : 1
                  } 
                  
                  ,
  'ExtraRate1'  : { "Name" : "Дополнительная скидка1",
                    "VarType" : 3,
                    "data2" : 0,
                    "Sort" : 2
                  },
  'ExtraRate2'  : { "Name" : "Дополнительная скидка2",
                    "VarType" : 3,
                    "data2" : 0,
                    "Sort" : 3
                  },
  'ExtraRate3'  : { "Name" : "Дополнительная скидка3",
                    "VarType" : 3,
                    "data2" : 0,
                    "Sort" : 4
                  },
  },
"Decors" :
  {
  'u69_FoilBMA' : { "Name" : "Эмаль A",
                    "VarType" : 7,
                    "data2" : 47,
                    "Sort" : 1
                  } ,
  'u69_FoilEFA' : { "Name" : "Лак A",
                    "VarType" : 5,
                    "data2" : 338,
                    "Sort" : 2
                  } ,
  'u69_FoilBLA' : { "Name" : "Тонировка A",
                    "VarType" : 5,
                    "data2" : 337,
                    "Sort" : 3
                  } ,
  'u69_FoilORA' : { "Name" : "Фрезеровка A",
                    "VarType" : 5,
                    "data2" : 340,
                    "Sort" : 4
                  } ,
  'u69_FoilPTA' : { "Name" : "Патина A",
                    "VarType" : 7,
                    "data2" : 341,
                    "Sort" : 5
                  } ,
  'u69_FoilFPA' : { "Name" : "Фотопечать A",
                    "VarType" : 7,
                    "data2" : 336,
                    "Sort" : 6
                  } ,
  'u69_FoilTPA' : { "Name" : "Трафаретная печать A",
                    "VarType" : 7,
                    "data2" : 339,
                    "Sort" : 7
                  } ,
  'u69_FoilSKA' : { "Name" : "Кожа A",
                    "VarType" : 7,
                    "data2" : 347,
                    "Sort" : 8
                  } ,
                  
  'u69_FoilBMF' : { "Name" : "Эмаль F",
                    "VarType" : 7,
                    "data2" : 335,
                    "Sort" : 11
                  } ,
  'u69_FoilEFF' : { "Name" : "Лак F",
                    "VarType" : 5,
                    "data2" : 338,
                    "Sort" : 12
                  } ,
  'u69_FoilBLF' : { "Name" : "Тонировка F",
                    "VarType" : 5,
                    "data2" : 337,
                    "Sort" : 13
                  } ,
  'u69_FoilORF' : { "Name" : "Фрезеровка F",
                    "VarType" : 5,
                    "data2" : 340,
                    "Sort" : 14
                  } ,
  'u69_FoilPTF' : { "Name" : "Патина F",
                    "VarType" : 7,
                    "data2" : 341,
                    "Sort" : 15
                  } ,
  'u69_FoilFPF' : { "Name" : "Фотопечать F",
                    "VarType" : 7,
                    "data2" : 336,
                    "Sort" : 16
                  } ,
  'u69_FoilTPF' : { "Name" : "Трафаретная печать F",
                    "VarType" : 7,
                    "data2" : 339,
                    "Sort" : 17
                  } ,
  'u69_FoilSKF' : { "Name" : "Кожа F",
                    "VarType" : 7,
                    "data2" : 347,
                    "Sort" : 18
                  } ,  
  }
}

for gr in dGroup:
    IDGr = 0
    try:
        # Проверка на наличие группы умолчания
        SQLStr = "SELECT ID, Name FROM udCategory WHERE Query=\"{}\"".format(gr)
        RS = base.RecordSetOpen(SQLStr)
        if round(RS.count) != 1:
            # Максимальный ID группы
            RS1 = base.RecordSetOpen("SELECT max(b.ID) AS maxID FROM udCategory b")
            k3.adbmovefirst(RS1.idRS)
            IDGr = int(k3.adbgetvalue(RS1.idRS, "maxID"))
            IDGr += 1
            SQL = '''INSERT into udCategory (ID, Name, Query, ParentID, Sort)
            SELECT top 1 {0}, '{1}', '{2}', NULL,
            (SELECT max(c.Sort) from udCategory c WHERE c.ParentID is Null)+1
            FROM udCategory a
            WHERE ParentID is Null'''.format(IDGr, dGroupName.get(gr,"None"), gr)
            base.RecordSetModify(SQL)
            print("Создали")
            KeyReLoad = True
            RS1.Close()
        else:
            k3.adbmovefirst(RS.idRS)
            IDGr = int(k3.adbgetvalue(RS.idRS, "ID"))
        RS.Close()
        print('Группа',gr,dGroupName.get(gr,"None"),'ID=', IDGr)
        for ent in dGroup[gr]:
            print(ent)
            # Проверим наличие свойства, удалим и создадим по новой
            SQL = "SELECT * FROM udEntity WHERE CategoryID = {0} AND Query = '{1}'".format(IDGr, ent)
            RS1 = base.RecordSetOpen(SQL)
            if round(RS1.count)>0:
                SQL = "DELETE FROM udEntity WHERE CategoryID = {0} AND Query = '{1}'".format(IDGr, ent)
                base.RecordSetModify(SQL)
                print('DELETE')
            RS1.Close()    
            SQL = '''INSERT into udEntity (CategoryID, Name, Query, VarType, data2, dVal, sort)
            SELECT ID, '{0}', '{1}', {2}, {3}, 0, {4} FROM udCategory WHERE ID = {5}
            '''.format(dGroup[gr][ent]['Name'],
            ent,
            dGroup[gr][ent]['VarType'],
            dGroup[gr][ent]['data2'],
            # "(SELECT Switch(Max(sort) Is Not Null,Max(sort)+1,Max(sort) Is Null,0) \
            # FROM udEntity e WHERE e.CategoryID={})".format(IDGr),
            dGroup[gr][ent]['Sort'],
            IDGr
            )
            base.RecordSetModify(SQL)
            print('INSERT')
            KeyReLoad = True

    except Exception as exc:
        print("exception:",exc)
            
base.adbDisCon()
if KeyReLoad:
    k3.loadorder(k3.k_last)

