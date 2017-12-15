# -*- coding: cp1251 -*-
#-------------------------------------------------------------------------------
# Name:        gUtilitesK3
# Purpose:     Утилиты общего назначения
#
# Author:      Aleksandr Dragunkin
#
# Created:     31.10.2012
# Copyright:   (c) GEOS 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
class DefaultProperty:
    '''Класс для хранения умолчаний в экземпляре vDefProperty'''
    def __init__(self):
        pass
    def newAttr(self,NameAttr,v):
        '''Создает новый аттрибут класса
            Входные параметры
            -- NameAttr имя аттрибута
            -- v значение
        Например: vDefProperty.newAttr('slot_property',__slot_property)
        '''
        if getattr(self,NameAttr,True):
            setattr(self, NameAttr,v)

vDefProperty=DefaultProperty() # Это глобальное хранилище умолчаний

#-------------------------------------------------------------------------------
def is_permissible(val, t):
    '''Ищет val в списке или ключах словаря t
    возвращае True или False'''
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
    ''' Изменяет свойства атрибутов класса по словарю полученному из списка неименованных аргументов.
        Возвращает Истина в случае благополучного завершения или Ложь в случае ошибки

        Входные параметры:
        -- Change_Default по умолчанию False управляет сменой глобальных
            умолчаний attr_defvalue при создании нового экземпляра класса
        -- attr_property список допустимых имен
        -- attr_permissible словарь допустимых значений
        -- attr_defvalue глобальное хранилище умолчаний
        -- dict_Attr словарь аргумент значение

        Пример:

    '''
    try:
        for i in list(dict_Attr.items()): # Наводим порядок. Проверяем значения словаря
            val = i[1]
            if is_permissible(i[0], attr_property): # смотрим наличие элемента в словаре
            #---
            # дальше накручено по поводу подмены буквенного обозначения стороны и грани

                if is_permissible(i[0], attr_permissible): # есть ли условность на значение
                    if is_permissible(i[1], attr_permissible[i[0]]):
                        if type(i[1])==str:
                            val = attr_permissible[i[1]]
                    else:
                        print(('Значение ', i[0],' недопустимое.  ', i[1], ' отсутствует в списке ',attr_permissible[i[0]]))
                        break
            #----
                if Change_Default: attr_defvalue[i[0]]=i[1] # изменяем значения умолчаний
                setattr(self, i[0],val)  # Создаю аттрибуты класса по словарю и задаю значения по умолчанию
            else:
                print((i[0], ' отсутствует в списке ', attr_property))
        return True
    except:
        return False
#-------------------------------------------------------------------------------
def change_attrs(objs=[], attrs=[], values=[]):
    '''Смена значений у списка объектов по списку атрибутов'''
    for obj in objs: # выбираем из списка объекты по очереди
        for a, v in zip(attrs, values): # a это атрибут объекта из списка attrs v из списка values
            if a in obj.__dict__:  # obj.__dict__ это список атибутов объекта если в нем есть искомый, то
                obj.__dict__[a] = v # меняем его значение на заданное

def main():
    pass

if __name__ == '__main__':
    main()
