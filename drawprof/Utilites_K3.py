# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        Utilites_K3
# Purpose:
#
# Author:      Dragunkin Aleksandr
#
# Created:     15.11.2012
# изменения для версии 7.3 поддержка Python3
# Copyright:   (c) GEOS 2012-2015
# Licence:     FREE
#-------------------------------------------------------------------------------
"""
Реализует классы и набор функций для работы с объектами К3. Используется для импорта в другие модули и для вызова функций из макросов и коммандной строки  К3 Мебель.

В случае использования функций из среды макро или геометрического редактора К3 Мебель
предоставляет возможность вызывать функции модуля в среде К3 используя следующий синтаксис:

*macro protopath+"Utilites_K3.py" "<имя функции>" byref <1-я переменная к3 > byref <2-я переменная к3 >...byref <n-я переменная к3 > done ;*

.. attention::
    Вы можете писать имя вызываемой функции в любом регистре, но в модуле эта функция всегда определена в нижнем регистре.
       + macro protopath+"Utilites_K3.py" "isOrder" byref err  done ;
       + macro protopath+"Utilites_K3.py" "ISORDER" byref err  done ;

    Функция  isorder. Будет вызвана в любом случае.
   
    Если вызов модуля будет производится без узания функции или имя указано с ошибкой получим сообщение об ошибке :
    
    *Требуется указать имя вызываемой функции в модуле*
    
    или
    
    *Не найдена вызываемая функция с именем  <namedef> в модуле Utilites_K3.py'*
"""
#import wingdbstub
import k3
import os
import random
import time
import mLayerfun

vpi=3.1415926530119026040722614947737 # Число Пи

#----------------------------------------------
class VarArray:
    """
    Класс для работы с объектами типа k3.VarArray
    
    Позволяет создавать массив, добавлять в него элементы и трансформировать в список (list)
    """
    def __init__(self,Size=1,Name=None):
        size = Size if type(Size) == int else int(Size)
        self.array = k3.VarArray(size)
        self.index = 0

    def append(self,value=0):
        '''повышаем индекс на 1 и добавляет элемент в массив'''
        self.array[self.index] = value
        self.index +=  1 # повышаем индекс на 1

    def transform_to_list(self):
        '''преобразует массив к3 в список'''
        nlst = []
        if self.index == 0:
            return None
        for index in range(int(self.index)):
            nlst.append(self.array[index])
        return nlst
    
    def transform_list_to_array(self, lst=[]):
        idx = len(lst)
        if idx > 0:
            self.array = k3.VarArray(idx)
            self.index = idx
            for a in zip(self.array, lst):
                a[0].value = a[1]
    
    
def __init__():
    params  = k3.getpar()
    if len(params)==0:
        print(('\nТребуется указать имя вызываемой функции в модуле ' + __file__))

    else:
        namedef = params[0].lower()
        f = globals().get(namedef, None)
        if f is None or not hasattr(f, '__call__'):
            print(('\nНе найдена вызываемая функция с именем ' + namedef + ' в модуле ' + __file__))
        else:
            if len(params)==1:
                print(( f.__doc__ ))
                return
            elif len(params)>1: f(params[1:])
#-------------------------------------------------------------------------------
class Layer:
    """
    Реализует методы работы со слоями в среде К3.
    """
    def __init__(self):
        """
        Конструктор класса. Определяе свойство count - количество существующих, не удаленных слоев
        
        layer = Layer()
        
        """
        self.count = self.CountLayers()
        
    def CountLayers(self):
        '''Возвращает количество существующих, не удаленных слоев.'''
        return k3.countlayers()
    
    def NameLayers(self):
        '''
        Определяет имена существующих, не удаленных слоёв.
        
        Возвращает список <list> всех имен слоев.
        '''
        arr = VarArray(Size=self.count)
        aNM = k3.namelayers(arr.array)
        return aNM.transform_to_list()
    
    def ExistsLayer(self, NameLayer=''):
        '''Функция  определяет  существование  слоя  по  его  имени.  < NameLayer >  -  строка с названием  слоя  (регистр  букв  не важен).'''
        t = k3.existslayer(NameLayer)
        return True if t > 0 else False
    def GetLayer(self, obj):
        '''Функция возвращает имя слоя, которому принадлежит объект < Obj > .'''
        return k3.getlayer(obj)
    
    def New(self, Name=''):
        '''создает новый слой в списке слое в с именем <Name>. Текущим при этом остается слой, который был до создания нового. Максимальное число созданных слоев - 255'''
        if len(Name) > 0:
            if  not self.ExistsLayer(NameLayer=Name):
                k3.layers(k3.k_new, Name)
                
    def Change(self, obj, Name):
        '''Изменяет слой объекта <obj>'''
        self.New(Name)
        k3.chprop(k3.k_layer, obj, k3.k_done, Name)
        
#-------------------------------------------------------------------------------
def sortapanelstocommonpos(params):
    '''
    Cортирует массив содержащий ссылки на полотно панели по возрастанию атрибута CommonPos.
    
    Параметр: params - кортеж
        + Число панелей params[0] - k3.VarArray().
        + Cсылки на полотно панели params[1] - k3.Var()
    '''
    nEl = params[0] # Передаем переменную К3 внутрь Python
    aPanels = params[1]
    cp_save = params[2] if len(params) > 2 else -1
    lPanels = [aPanels[a].value for a in  range(int(nEl))]
    dPan = {}
    for pan in lPanels:
        i=0
        err = 1.0
        h = k3.Var()
        hd = k3.Var()
        h.value = pan
        while err==1.0 and i<10:
            i+=1
            err=k3.getobjhold(h,hd)
            cp=k3.getattr(hd.value,"FurnType",'010000');

            if cp!='010000':

                break
            h = k3.Var()
            h.value = hd.value

        cp = k3.getattr(hd.value, "Commonpos", -99)
        if cp != -99:
            if (cp not in list(dPan.keys())):
                dPan[cp] = []
            dPan[cp].append(pan)
    keys_dPan = list(dPan.keys())
    keys_dPan.sort()
    i = 0
    for pan in keys_dPan:
        for s in dPan[pan]:
            aPanels[i].value = s
            i += 1
#-------------------------------------------------------------------------------
def isorder(params):
    '''
    Возвращает информацио текущем состоянии сцены.
        + 0 - текущее состояние ФАЙЛ
        + 1 - текущее состояние ЗАКАЗ

    Варианты вызова из K3Mebel:
    
        macro protopath+"Utilites_K3.py" "isorder" byref err  done ;

    '''
    if len(params)!= 1 :
        raise BaseException('\nНеверное число аргументов\nТребуется передать перменную в качестве аргумента'+str(len(params)))
    if type(params[0]) != k3.Var:
        raise BaseException('\nНеверный тип аргументов\nТребуется передать перменную в качестве аргумента'+str(len(params)))
    try:
        curfile = k3.sysvar(2)
        basedate = 0
        if curfile[-2:] == 'k3':
            if k3.fileexist(curfile)==1:
                basedate = os.stat(curfile).st_mtime
            bx = k3.box(0,0,0,1,1,1)
            k3.delete(bx,k3.k_done)
            time.sleep(0.1)
            k3.saveorder(0)
            curdate = os.stat(curfile).st_mtime
            if basedate!=curdate:
                params[0].value = 1.0
            else:
                params[0].value = 0.0
        else:
            params[0].value = 0.0
    except:
        raise BaseException('При выполнении ISORDER возникли ошибки!')
#-------------------------------------------------------------------------------
sign = lambda vl : 1 if vl>=0 else -1

def getNumQadrant(Angle=0):
    '''Возвращает номер квадранта <INT> 1,2,3,4 по переданному углу Angle градусы'''
    numQ=None
    rAngle = checkAngle(Angle) if abs(Angle)>360 else Angle
    if Angle<0.0:
        # Число отрицательное
        Angle = 360.0-Angle
    if Angle>=0 and Angle<=90:
        numQ = 1
    elif Angle>90 and Angle<=180:
        numQ = 2
    elif Angle>180 and Angle<=270:
        numQ = 3
    else:
        numQ = 4
    return numQ

def checkAngle(Angle):
    '''
    Приводит угол Angle в пределы 360 градусов
    
    Если его значение выходит за пределы 0...360
    '''
    sgAngle = sign(Angle) # Знак угла
    t=float(Angle)/360.0
    dt=abs(t)-int(abs(t))
    dt = sgAngle * dt
    return dt*360 # реальный угол

#-------------------------------------------------------------------------------
def getlistarrayallobjectsscene(AttrFilter=''):
    '''
    Возвращает массив к3 заполненных всеми объектами сцены.
    Предназначен для вызова из макро.
    '''    
    result = getListArrayAllObjectsScene(AttrFilter)
    return result[0]

def getListArrayAllObjectsScene(AttrFilter=''):
    '''
    Возвращает список массивов к3 заполненных всеми объектами сцены
    '''
    listArr = []
    ng=k3.sysvar(62)
    if ng>0:
        nn=32767 if ng>32767 else int(ng)
        arr = k3.VarArray(nn)
        if len(AttrFilter) < 3:
            m=k3.scanscene(arr)
        else:
            m=k3.scan_scene(arr, AttrFilter)[0]
        # print(m)
        if m > 0:
            arr_1 = k3.VarArray(int(m))
            k3.copyarray(arr_1, 1, arr, 1, int(m))
            listArr.append(arr_1)
        m1 = 0
        i = 0
        while ng>nn :
            i=i+1
            nt = ng-nn
            nt=32767 if nt>32767 else nt
            arr=k3.VarArray(int(nt))
            m1=k3.scanscene(arr,m+1)
            nn=nt+nn
            m = m + m1
            listArr.append(arr)
    return listArr
#-------------------------------------------------------------------------------
def getListObjVisual():
    '''Возвращает список видимых объектов'''
    lObj = []
    k3.select(k3.k_all,k3.k_done)
    n = int(k3.sysvar(61))
    if n>0:
        for i in range(1,n+1):
            lObj.append(k3.getselnum(i))
    return lObj
#-------------------------------------------------------------------------------
def findgabscene(params = []):
    """
    :param params: Список указателей на объекты сцены.

    :return: Возвращает массив из 6-ти элементов или 6 координат минимальных и максимальных габаритов сцены.

    .. hint:: **Варианты вызова из K3Mebel:**

        ::

        ...macro protopath+"Utilites_K3.py" "FindGabScene" byref x1 byref y1 byref z1 byref x2 byref y2 byref z2 done ;

        или

        ::

        ...defarr xm[6];
        ...macro protopath+"Utilites_K3.py" "FindGabScene" byref xm done;
    """
    if len(params) not in [1,6] :  raise BaseException('\nНеверное число аргументов\nТребуется передать массив из 6-ти элементов или 6 переменных в качестве аргументов'+str(len(params)))
    maxPoint = [k3.Var() for i in range(6)]
    for i in range(6):
        maxPoint[i].value = 999999999 if i < 3 else -999999999
    xm =   k3.VarArray(6)
    nobj = k3.sysvar(62)
    m = getListArrayAllObjectsScene()
    tobj=[]
    for mi in m:
        try:
            for a in mi:
                tobj.append(a.value)
        except:
            k3.putmsg('Число '+str(len(tobj))+' из '+str(int(nobj)))
            pass
    for i in tobj:
        try:
            err = k3.objgab3(i,xm)
            for j in range(6):
                maxPoint[j].value = min(maxPoint[j].value, xm[j].value) if j<3 else max(maxPoint[j].value, xm[j].value)
        except:
            pass
    if type(params[0]) == k3.VarArray:
        for i in range(6): params[0][i].value = maxPoint[i].value
    elif type(params[0]) == k3.Var:
        for i in range(6): params[i].value = maxPoint[i].value
    else:
        for i in range(6): params[i] = maxPoint[i].value
    return params
 
def GetRectText(Obj):
    """Вычислить координаты в ГСК 3-х вершин прямоугольника текста в объекте выноска с примечанием Obj
    с учетом текущего и общего граф.коэффициентов.

    :param Obj: Объект выноска с примечанием

    :return: Возвращает массив к3.VarArray из 9-ти элементов:

        + Arr - массив размерности 9 задающий координаты трех точек прямоугольника в ГСК:
        + Arr[1..3] - первая задает нижний левый угол прямоугольника
        + Arr[4..6] - вторая задает верхний левый угол прямоугольника
        + Arr[7..9] - третья задает нижний правый угол прямоугольника
    """
    Arr = k3.VarArray(9)
    nEl = k3.getrecttext(Obj,Arr)
    return Arr

#--------------------------------------------
def IsVsblRect(nVport, Arr):
    """
    :type nVport: k3.sysvar(51)- номер видеопорта, в проекции на картинную плоскость которого определяем видимость по умолчанию текущий

    :type Arr: k3.VarArray(9)- массив размерности 9 задающий координаты трех точек прямоугольника в ГСК:

        + Arr[1..3] - первая задает нижний левый угол прямоугольника
        + Arr[4..6] - вторая задает верхний левый угол прямоугольника
        + Arr[7..9] - третья задает нижний правый угол прямоугольника

    :return:

        + False - внутрь прямоугльника изображение не попадает 1
        + True - внутрь прямоугольника изображение попадает 0
        + None - какая-то ошибка -1

        """
    result = {-1:None,0:True,1:False}
    rs = k3.isvsblrect(nVport,Arr)
    return result[rs]

#-------------------------------------------
f_round = lambda x: round(x,3) 

#-----------------------------
def PointOutListPoint(args):
    '''
    Возвращает список из трех превых элементов списка args и изменяет список args укорачивачивая его.
    
    ::
    
    ...point,args = PointOutListPoint(args)
        
    ,где
    
    На входе
    
    args - список вида [Real,Real,Real,Real,Real,Real,....,Real,Real,Real,]
    
    На выходе
    
    point - список вида [Real,Real,Real]
    
    args - список вида [Real,Real,Real,....,Real,Real,Real,]
    '''
    return list(map(f_round,args[:3])),args[3:]

#-----------------------------
def ptransPcsToGsc(args=[]):
    '''
    Принимает на вход список чисел кратный 3 и преобразует точки из текущей системы в ГСК.
    
    ::
    
    ...point = ptransPcsToGsc(args)
        
    ,где
    
    На входе
    
    args - список вида [Real,Real,Real,Real,Real,Real,....,Real,Real,Real,]
    
    На выходе
    
    args - список вида [Real,Real,Real,Real,Real,Real,....,Real,Real,Real,]
    
    '''
    result=[]
    Xc,Yc,Zc=k3.Var(),k3.Var(),k3.Var()
    while len(args)>0:
        point,args = PointOutListPoint(args)
        k3.ptranscs(0,3,point,Xc,Yc,Zc)
        result.append(Xc.value)
        result.append(Yc.value)
        result.append(Zc.value)
    return list(map(f_round,result))

#-----------------------------
def ptransPcsToVcs(args=[]):
    '''
    Принимает на вход список чисел кратный 3 и преобразует точки из текущей системы в ВСК.
        
    ::
    
    ...point = ptransPcsToVcs(args)
        
    ,где
    
    На входе
    
    args - список вида [Real,Real,Real,Real,Real,Real,....,Real,Real,Real,]
    
    На выходе
    
    args - список вида [Real,Real,Real,Real,Real,Real,....,Real,Real,Real,]
    '''
    result=[]
    Xc,Yc,Zc=k3.Var(),k3.Var(),k3.Var()
    while len(args)>0:
        point,args = PointOutListPoint(args)
        k3.ptranscs(0,1,point,Xc,Yc,Zc)
        result.append(Xc.value)
        result.append(Yc.value)
        result.append(Zc.value)
    return list(map(f_round,result))

#---------------------------------
def ptransGcsToVcs(args=[]):
    '''
    Принимает на вход список чисел кратный 3 и преобразует точки из текущей системы в ВСК.
        
    ::
    
    ...point = ptransGcsToVcs(args)
        
    ,где
    
    На входе
    
    args - список вида [Real,Real,Real,Real,Real,Real,....,Real,Real,Real,]
    
    На выходе
    
    args - список вида [Real,Real,Real,Real,Real,Real,....,Real,Real,Real,]    
    '''
    result=[]
    Xc,Yc,Zc=k3.Var(),k3.Var(),k3.Var()
    while len(args)>0:
        point,args = PointOutListPoint(args)
        k3.ptranscs(3,1,point,Xc,Yc,Zc)
        result.append(Xc.value)
        result.append(Yc.value)
        result.append(Zc.value)
    return list(map(f_round,result))

#---------------------------------
def ptransGcsToPsc(args=[]):
    '''
    Принимает на вход список кратный 3 и преобразует точки из ГСК системы в ПСК.
        
    ::
    
    ...point = ptransGcsToPsc(args)
        
    ,где
    
    На входе
    
    args - список вида [Real,Real,Real,Real,Real,Real,....,Real,Real,Real,]
    
    На выходе
    
    args - список вида [Real,Real,Real,Real,Real,Real,....,Real,Real,Real,]   
    '''
    result=[]
    Xc,Yc,Zc=k3.Var(),k3.Var(),k3.Var()
    while len(args)>0:
        point,args = PointOutListPoint(args)
        k3.ptranscs(3,0,point,Xc,Yc,Zc)
        result.append(Xc.value)
        result.append(Yc.value)
        result.append(Zc.value)
    return list(map(f_round,result))
#-----------------------------
def tanimoto(st1, st2):
    '''
    Степень схожести строк (коэффициент Танимото).
    
    Определяет степень схожести двух строк, т. е., насколько одна строка похожа на другую.
    
    Возвращает коэффциент схожести <Real>'''
    a, b, c = len(st1), len(st2), 0.0
    for sym in st1:
        if sym in st2:
            c += 1
    return c / (a + b - c)

def str_random_name(qty = 8):
    """
    Возвращает символическую рандомную строку из qty символов
    """
    symbols = ''
    for i in range(qty):
        num = int(random.random() * (122 - 97 + 1)) + 97
        symbols = symbols + chr(num)
    return symbols  

def isTextSizeLarge(dimObj, Arr):
    '''
    Если размер диагонали текста меньше самой величины возвращает True.
    
    '''
    dist = k3.distance([a.value for a in Arr][3:])
    result = False
    adiminfo=VarArray(54,'adimv')
    k3.getdiminfo(dimObj,adiminfo.array)
    if dist[0] <= adiminfo.array[0].value:
        result = True
    return result

def getPathNguides():
    '''
    Возвращает полный путь к Nguides.mdb
    
    '''
    con=k3.adbcon(3)
    SQLSTR = '''SELECT CorePaths.Path
    FROM CorePaths
    WHERE (((CorePaths.Name)="Proto"));'''
    r = k3.adbopen(con,SQLSTR)
    ij=k3.adbreccount(r)
    path = k3.adbgetvalue(r,'path',"xxx") if ij>0 else None    
    con = k3.adbdiscon(con)
    return path

def set_time_refresh_interval(val):
    """
    Изменяет значение свойства time_refresh_default (интервал проверки обновления) у объекта KROMZNAK <DrawingSupp.Kromznak()>
    """
    global KROMZNAK
    try:
        KROMZNAK.set_time_refresh_def(val)
    except:
        pass

def get_info(*wards):
    """
    Возвращае словарь значений свойств объекта KROMZNAK
    """
    d_res = {}
    global KROMZNAK
    try:
        for w in wards:
            try:
                d_res[w] = getattr(KROMZNAK, w)
            except:
                pass
    except:
        pass
    return d_res

#-----------------------------
def main():
    __init__()
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    main()

