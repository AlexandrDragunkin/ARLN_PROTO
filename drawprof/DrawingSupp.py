# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:        DrawingSupp
# Purpose:     Модуль Чертежей панелей
#
# Author:      Aleksandr Dragunkin
#
# Created:     14.02.2013
# Изменения для версии 7.3 поддержка Python3
# Copyright:   (c) GEOS 2012 http://k3info.ru/
# Licence:     FREE
# ------------------------------------------------------------------------------
# Коммент по просьбе Дениса
#try:
    #import pydevd
    #pydevd.settrace('localhost', port=51764, stdoutToServer=True, stderrToServer=True)
#except:
    #pass
try:
    import wingdbstub
except:
    pass
# import logging
import k3
import time
import datetime

import cProfile
import random
import re

import Utilites_K3 as Ut
from mLayerfun import LayerFun
import pickle as Pickle
import substdirs
from Utilites_K3 import VarArray
from mPanel import (PanelRectangle,
                    ElemsInfo)
from SingletonMetaClass import Singleton
from dbaccessforK3 import (adbFunktion, )
from mCounter import (Counter, Userproperty, Central)
from k3 import sgn as sign

import isFront

PROTOPATH = k3.GlobalVar('ProtoPath')
AppDataPath = k3.mpathexpand("<AppData>")
k3filesPath = k3.mpathexpand("<k3files>")
FININAME = str(AppDataPath) + '\\Drawing.ini'
LAYERTODXF = False  # Формировать имена слоев в DXF

global PANEL
if not 'PANEL' in globals().keys():
    PANEL = PanelRectangle()
global Panel    
if 'Panel' in globals().keys():
    del(Panel)
Panel = PanelRectangle()

#--------модули для отладки---------------------
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
#logging.debug('Сообщение для отладки.')
#-----------------------------------------------


def profile(func):
    """Decorator for run function profile"""

    def wrapper(*args, **kwargs):
        profile_filename = func.__name__ + '.prof'
        profiler = cProfile.Profile()
        result = profiler.runcall(func, *args, **kwargs)
        profiler.dump_stats(profile_filename)
        return result

    return wrapper

#----------------------------------------------
iif = lambda cond, iftrue, iffalse: iftrue if cond else iffalse

transform_logical_k3_to_python = lambda val: True if val > 0 else False

f_round = lambda x: round(x, 3)
#----------------------------------------------

# Тут оставить только определяемые в этом макро переменные
Krav = False 
D_H_in_Name = iif(Krav, True, False)  # Размеры отверстий с учетом маски имени DxH
Rastr32 = iif(Krav, True, False)  # Размеры с учетом растра 32
Legenda_Alias = iif(Krav, True, False)  # Наименование в легенде по Alias
IsFlagPoints = iif(Krav, True, False)  # Исключать флаги из цепочки
IsPanFormaFreeNoDrillDraw = True  # Если форма панели по свободному контуру игнорировать отверстия
NDrillIgnoreForPanFormaFree = 8  # Число отверстий на панели по cвободному контуру при превышении которого сетка для отверстий не строится
DOWNZNAK = iif(Krav, False, True)  # Подпись Низ
keyDXF = iif(Krav, True, False)  # Создавать DXF
IsNameSide = iif(Krav, False, True)  # Подписывать выводимую сторону панели
UnionDrawPathAndDrill = iif(Krav, False, True)  # Объединять размерные точки контура и сверловки в один чертеж
STDARTICUL = iif(Krav, k3.getorderinfo('Phone'), '')
if len(STDARTICUL) > 0:
    STDARTICUL += '-'
#-----------------------------

Krav = transform_logical_k3_to_python(k3.GlobalVar('g_Krav').value)  #Специальный комплекс Да/Нет
if Krav:
    D_H_in_Name = True  # Размеры отверстий с учетом маски имени DxH
    Rastr32 = False  # Размеры с учетом растра 32
    Legenda_Alias = True  # Наименование в легенде по Alias
    IsFlagPoints = False  # Исключать флаги из цепочки
    IsPanFormaFreeNoDrillDraw = False  # Если форма панели по свободному контуру игнорировать отверстия
    NDrillIgnoreForPanFormaFree = 8  # Число отверстий на панели по cвободному контуру при превышении которого сетка для отверстий не строится
    DOWNZNAK = True  # Подпись Низ
    keyDXF = False  # Создавать DXF
    IsNameSide = True  # Подписывать выводимую сторону панели
    UnionDrawPathAndDrill = True  # Объединять размерные точки контура и сверловки в один чертеж
    STDARTICUL = ''

class DrawingPage():
    '''Чертежный лист'''

    def __init__(self):
        self.handle = None  # Указатель на объект К3 (группу) подлежащий выгрузке в отдельный файл и выводу на печать
        self.list_view = []  # список чертежных видов объектов типа DrawingView, Legenda


    def draw(self, gab_3=[]):
        for view in self.list_view:
            angle_rotate = {'A': -90, 'F': 90}
            if k3.GlobalVar('g_stoi').value > 0:
                rotateDrawObj(view.handle, angle_rotate[view.side])
            gab_3 = moveDrawPos(view.handle, delta=real_h_text, v_gab=gab_3)
            if view.title is not None:
                view.title.draw(view.handle)
            if self.handle is None:
                self.handle = k3.group(view.handle, k3.k_done)[0]
            else:
                k3.add(self.handle, view.handle, k3.k_done)
        return gab_3


#-----------------------------
class DrawingView():
    '''Чертежный вид'''

    def __init__(self):
        self.handle = None  # Указатель на объект К3 (группу) чертежный вид
        self.title = None  # заголовок над видом
        self.legenda = None  # Легенда под видом
        self.side = None
        self.nmattr = "dsview"
        self.crattr()
    
    def crattr(self):
        '''Атрибут '''
        if k3.isattrdef(self.nmattr) == 0 :
            k3.attribute( k3.k_create,  self.nmattr, self.nmattr, k3.k_real, 5, 0)

#-----------------------------
class DrawTitle():
    '''Заголовок над чертежным видом'''

    def __init__(self, StringTitle=None):
        self.value = StringTitle
        self.handle = None  # ссылка на объект к3 после отрисовки методом draw

    def draw(self, page=None):
        if self.value is None:
            return None
        if len(self.value) > 0:
            ts = k3.text(self.value, k3.k_done, 0, 0, 0, k3.k_normal, (0, 0, 1), -1, 0, 0)
            self.handle = ts[0]
            if isinstance(page, k3.K3Obj):
                self.clue(page)
            return ts[0]
        else:
            return None

    def clue(self, page):
        if self.handle is not None:
            gab_page = obj_k3_gab3(page)
            gab_title = obj_k3_gab3(self.handle)
            dx = (gab_page[0] + (gab_page[3] - gab_page[0]) / 2) - (gab_title[0] + (gab_title[3] - gab_title[0]) / 2)
            dy = gab_page[1] + gab_title[4] - real_h_text
            k3.move(k3.k_nocopy, self.handle, k3.k_done, dx, dy, 0)
            k3.add(page, self.handle, k3.k_done)


#-----------------------------
class Legenda():
    ''' Легенда относящаяся к чертежному объекту располагающаяся снизу'''

    def __init__(self):
        self.global_titile = '%%uУсловные обозначения'
        self.dict_subsection = {}
        self.handle = None  # ссылка на объект к3 после отрисовки методом draw
        self.nmattr = "dslegenda"
        self.crattr()
    
    def crattr(self):
        '''Атрибут легенды'''
        if k3.isattrdef(self.nmattr) == 0 :
            k3.attribute( k3.k_create,  self.nmattr, self.nmattr, k3.k_real, 5, 0)


    def getSubsection(self, arg=None):
        '''Возвращает список заголовков легенды если arg не задан
          или возвращает число частей заголовка'''
        if arg is None:
            return list(self.dict_subsection.keys())
        else:
            if findInList(list(self.dict_subsection.keys()), arg) is None:
                self.dict_subsection[arg] = []
            return len(self.dict_subsection[arg])

    def addPartInSubsection(self, name_subsection, part):
        '''Добавляет элемент в часть легенды'''
        n = self.getSubsection(arg=name_subsection)
        s = [t.comment for t in self.dict_subsection[name_subsection]]
        if part.comment not in s:
            self.dict_subsection[name_subsection].append(part)

    def draw(self):
        '''Печатает легенду '''
        plegenda = None
        StartPoz = 0
        keyGroup = False
        n_object_scene = k3.sysvar(60)
        for p in self.dict_subsection.items():
            tstring = k3.text(p[0], k3.k_done, 0, StartPoz, 0, k3.k_normal, (0, 0, 1), -1, StartPoz, 0)
            egab = obj_k3_gab3(tstring[0])
            kDopSdY = 1.2 * (egab[4] - egab[1])
            if not keyGroup:
                tgroup = k3.group(tstring[0], k3.k_done)
                keyGroup = True
            else:
                k3.move(k3.k_nocopy, tgroup[0], k3.k_done, 0, -1.35 * (egab[4] - egab[1]), 0)
                k3.add(tgroup[0], tstring[0], k3.k_done)
            for e in p[1]:
                if 'draw' in e.__class__.__dict__.keys():
                    eobj = e.draw()
                    if not eobj is None:
                        egab = obj_k3_gab3(eobj)
                        k3.move(k3.k_nocopy, tgroup[0], k3.k_done, 0, -1.2 * (egab[4] - egab[1]), 0)
                        k3.add(tgroup[0], eobj, k3.k_done)

        n_object_scene = k3.sysvar(60) - n_object_scene
        if n_object_scene > 0:
            t = k3.group(k3.k_last, n_object_scene, k3.k_done)
            plegenda = t[0]
            self.handle = plegenda
            k3.attrobj(k3.k_attach, self.nmattr, k3.k_done, self.handle, 1)
        return plegenda

    def clue(self, page):
        gab_page = obj_k3_gab3(page)
        if self.handle is not None:
            gab_legend = obj_k3_gab3(self.handle)

            dx = (gab_page[0] + (gab_page[3] - gab_page[0]) / 2) - (gab_legend[0] + (gab_legend[3] - gab_legend[0]) / 2)
            dy = gab_page[4] - gab_legend[1] + real_h_text
            k3.move(k3.k_nocopy, self.handle, k3.k_done, dx, dy, 0)
            k3.add(page, self.handle, k3.k_done)
            
    def clue_x(self, page):
        gab_page = obj_k3_gab3(page)
        if self.handle is not None:
            gab_legend = obj_k3_gab3(self.handle)
            dx = gab_page[0]  - (gab_legend[3] ) - real_h_text
            dy = (gab_page[1] + (gab_page[4] - gab_page[1]) / 2) - (gab_legend[1] + (gab_legend[4] - gab_legend[1]) / 2)
            #gab_page[4] - gab_legend[1] + real_h_text
            k3.move(k3.k_nocopy, self.handle, k3.k_done, dx, dy, 0)
            k3.add(page, self.handle, k3.k_done)    


#-----------------------------
#legenda = Legenda()
#-----------------------------

class TechLegenda():
    def __init__(self, znak=None, comment=None):
        self.znak = znak  #номер обозначения
        self.comment = comment  # комментарий знаку

    def __eq__(self, other):
        return self.znak == other.znak


    def draw(self):
        n = k3.sysvar(60)
        obj_handle = None
        lgab = [0, 0, 0, 0, 0, 0]
        if self.comment is not None:
            tcomment = k3.text(self.znak + '. ' + self.comment, k3.k_done, lgab[0] - 10, 0, 0, k3.k_normal, (0, 0, 1),
                               lgab[0] - 20, 0, 0)  # Пишем комментарий
        n = k3.sysvar(60) - n
        if n > 0:
            t = k3.group(k3.k_last, n, k3.k_done)
            obj_handle = t[0]
        return obj_handle


#-----------------------------
class PartLegenda():
    def __init__(self, znak=None, comment=None, ptype=None):
        self.ptype = ptype
        self.znak = znak  #знак обозначения
        self.comment = comment  # комментарий знаку

    def __eq__(self, other):
        result = self.znak == other.znak
        if self.ptype == 'Cover':
            result = result and self.comment == other.comment
        return result

    def draw(self):
        n = k3.sysvar(60)
        obj_handle = None
        lgab = [0, 0, 0, 0, 0, 0]
        if self.znak is not None:
            k3.setucs(k3.k_save, "t25r69fg")  # чтобы знак в легенде был расположен читабельно
            k3.setucs(k3.k_rotate, k3.k_2points, 0, 0, 0, 0, 0, 1,
                      180)  # чтобы знак в легенде был расположен читабельно
            
            if 'real_h_text' in globals():
                Y1 = real_h_text / 2
            else:
                Y1 = -1
            tznak = KROMZNAK.drawKromZnak(Znak=self.znak[0], X=0, Y=0, Z=0, X1=0, Y1=Y1, Z1=0,
                                          duble_zn=self.znak[1], index=self.znak[2])  # чертим знак
            k3.setucs(k3.k_restore, "t25r69fg")  # чтобы знак в легенде был расположен читабельно
            k3.setucs(k3.k_delete, "t25r69fg")  # чтобы знак в легенде был расположен читабельно
            lgab = obj_k3_gab3(tznak)
            k3.move(k3.k_nocopy, tznak, k3.k_done, 0, -lgab[3], 0)
        if self.comment.strip():
            tcomment = k3.text(self.comment, k3.k_done, lgab[0] - 10, 0, 0, k3.k_normal, (0, 0, 1), lgab[0] - 20, 0,
                               0)  # Пишем комментарий
        n = k3.sysvar(60) - n
        if n > 0:
            t = k3.group(k3.k_last, n, k3.k_done)
            obj_handle = t[0]
        return obj_handle


#-----------------------------
class Note():
    def __init__(self, normal=(0, 0, 1), Text1="", Text2="", point1=(0, 0, 0), relativ1=(10, 10, 0),
                 relativ2=(20, 20, 0)):
        self.normal = normal
        self.Text1 = Text1
        self.Text2 = Text2
        self.point1 = point1
        self.relativ1 = relativ1
        self.relativ2 = relativ2
        self.qPlace, self.sPlace = None, None
        self.dAngle = [45.0, 45.0 + 360.0]  # диапазон углов
        self.dVector = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0)]
        self.flip = True
        aTemp = k3.VarArray(13)
        k3.sysarr(43, aTemp)
        self.grcoef = [k3.sysvar(76), aTemp]
        self.GRCOEF = self.grcoef[0] * self.grcoef[1][2].value        
        
    def getinfo(self):
        """
        """
        arr = k3.VarArray(50)
        res= k3.getnoteinfo(self.holder, arr)
        self.info = [a.value for a in arr]
    
    def getinfodefault(self):
        """
        """
        arr = k3.VarArray(30)
        self.infodefault = {}
        for i in [0, 1, 2, 3]:
            res= k3.getnoteinfo(i, arr)
            self.infodefault[i] = [a.value for a in arr]
    
    def getrealsizetext(self):
        self.getinfodefault()
        return self.GRCOEF * self.infodefault[0][14] * (1+(0.02 * self.infodefault[0][18]))

    def draw(self, key=''):
        tObj = k3.Var()
        vNote = k3.note(k3.k_normal, self.normal, k3.k_arrow, 4, k3.k_type, 0,
                        self.Text1, self.Text2,
                        self.point1, k3.k_relative, self.relativ1, k3.k_relative, self.relativ2)
        k3.objident(k3.k_last, 1, tObj)
        self.holder = tObj.value

        if self.flip:
            result = k3.editobject(tObj.value, k3.k_flip, k3.k_done)
            k3.objident(k3.k_last, 1, tObj)
            pass


        if key == 'mirror':
            k3.editobject(tObj.value, k3.k_mirror, k3.k_done)
            k3.objident(k3.k_last, 1, tObj)
            if self.normal[2] == -1:
                k3.editobject(tObj.value, k3.k_mirror, k3.k_done)
                k3.objident(k3.k_last, 1, tObj)
        return tObj.value

    def _getListPointPosition(self, delta, gabs):
        '''Возвращает список  доступных вариантов размещения точек для указателя в зависимости от положения точки указателя в пределах прямоугольника описанного списком gabs и отступом delta отступ создает граничный пояс'''
        issign = lambda S: 1 if S >= 0 else -1
        lPoint = []
        gabs = [round(a, 1) for a in gabs]
        gab_min_place = [gabs[0] + delta, gabs[1] + delta, gabs[3] - delta, gabs[4] - delta]
        gab_max_place = [gabs[0], gabs[1], gabs[3], gabs[4]]

        mid_position = (gabs[3] - gabs[0]) / 2, (gabs[4] - gabs[1]) / 2, 0
        rs = []
        for i in range(len(mid_position)):
            rs.append(issign(self.point1[i] - mid_position[
                i]))  # получаем +1 +1 для первого квадранта -1 -1 третий , -1 +1 второй +1 -1 четвертый
        # определяем принадлежность граничному поясу
        rest = range(8)
        if gab_min_place[2] - gab_min_place[0] > 0 and gab_min_place[3] - gab_min_place[1] > 0:
            # имеет минимальную зону и граничный пояс
            pt = self.point1[:2]
            if gab_min_place[0] <= pt[0] <= gab_min_place[2] and gab_min_place[1] <= pt[1] <= gab_min_place[3]:
                # принадлежит минимальной зоне. может иметь 8 положений
                rest = range(8)
            else:
                # граничный пояс угол 0 1 2 3 или сторона 4 5 6 7
                self.dAngle = [45.0, 45.0 + 360.0]  # диапазон углов
                self.dVector = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0)]
                if gab_min_place[0] > pt[0] and gab_min_place[1] > pt[1]:
                    #print 'Угол 0'
                    self.dAngle = [30, 61]  # диапазон углов
                    self.dVector = [(1, 0, 0), (0, 1, 0)]
                    rest = [0]
                elif gab_min_place[0] > pt[0] and gab_min_place[3] < pt[1]:
                    #print  'Угол 3'
                    self.dAngle = [270 + 30, 360 - 29]  # диапазон углов
                    self.dVector = [(1, 0, 0), (0, -1, 0)]
                    rest = [3]
                elif gab_min_place[2] < pt[0] and gab_min_place[3] < pt[1]:
                    #print  'Угол 2'
                    self.dAngle = [180 + 30, 270 - 29]  # диапазон углов
                    self.dVector = [(-1, 0, 0), (0, -1, 0)]
                    rest = [2]
                elif gab_min_place[2] < pt[0] and gab_min_place[1] > pt[1]:
                    #print  'Угол 1'
                    self.dAngle = [90 + 30, 180 - 29]  # диапазон углов
                    self.dVector = [(-1, 0, 0), (0, 1, 0)]
                    rest = [1]
                elif gab_min_place[0] > pt[0]:
                    #print  'Сторона 7'
                    self.dAngle = [270 + 30, 90 - 29]  # диапазон углов
                    self.dVector = [(1, 0, 0), (0, 1, 0), (0, -1, 0)]
                    rest = [7]
                elif gab_min_place[2] < pt[0]:
                    #print  'Сторона 5'
                    self.dAngle = [90 + 30, 270 - 29]  # диапазон углов
                    self.dVector = [(-1, 0, 0), (0, 1, 0), (0, -1, 0)]
                    rest = [5]
                elif gab_min_place[1] > pt[1]:
                    #print  'Сторона 4'
                    self.dAngle = [30, 180 - 29]  # диапазон углов
                    self.dVector = [(-1, 0, 0), (1, 0, 0), (0, 1, 0)]
                    rest = [4]
                elif gab_min_place[3] < pt[1]:
                    #print  'Сторона 6'
                    self.dAngle = [90 + 30, 270 - 29]  # диапазон углов
                    self.dVector = [(-1, 0, 0), (0, 1, 0), (0, -1, 0)]
                    rest = [6]
        return rs, rest


#-----------------------------
class ObjtoDxfCounter():
    def __init__(self):
        self.Counter = []

    def addCounterHandle(self, obj):

        if type(obj) == list or type(obj) == tuple:
            self.Counter.extend(obj)
        elif isinstance(obj, k3.K3Obj):
            self.Counter.append(obj)
        elif type(obj) == k3.Var:
            objv = obj.value
            self.addCounterHandle(objv)
        else:
            pass

#-----------------------------
OBJ_DXF = ObjtoDxfCounter()
#-----------------------------
class Dimension:
    def __init__(self):
        self.nLeader = 0  # счтчик числа размеров на выноске
        self.maxLeader = 0
        self._aInf = k3.VarArray(54)
        self.list_handle = None
        self.SystemDimInfo = {'ldim': [], 'adim': [], 'rdim': [], 'ddim': []}
        self.DimInfo = []
        aTemp = k3.VarArray(13)
        k3.sysarr(43, aTemp)
        self.grcoef = [k3.sysvar(76), aTemp]
        self.GRCOEF = self.grcoef[0] * self.grcoef[1][2].value
        self.getSystemDimInfo()
        self.realhightext = self.GRCOEF * self.SystemDimInfo['ldim'][0] * (1 + self.SystemDimInfo['ldim'][4] / 100)
        self.base = None


    def defaultDimCreate(self):
        '''Определяет параметры размера по умолчанию'''
        tempDim = self.create('ldim', 'continue', [(0, 0, 0), (100, 0, 0), (0, 20, 0)])
        self.getDimPar(tempDim[0])
        k3.delete(tempDim)


    def create(self, Type=None, Base=None, tP=[]):
        '''Создает единичный размер или несколько размеров по точкам списка tP'''
        objects = []
        BaseStart = Base
        if BaseStart == 'dinamic':
            Base = 'continue'
        cP = None
        getPforDist = lambda v, ls: (ls[0], 0, 0) if v == 0 else (0, ls[1], 0)
        self.base = Base
        if Type == 'ldim' and tP[0]!=tP[2]:
            ps = k3.ldim(k3.k_3ddim, k3.k_normal, (0, 0, 1), k3.k_no, tP[0], tP[1], k3.k_free, tP[2])
            self.basedPoint = tP[0]
            self.firstPoint = tP[2]
            self.edDimBaseLeader(Base, ps, True, tP)
            self.chDimTextLeader(ps)
            dimTwinsValue = -99  # значение близнеца(близнец это размер в перфорации например 32 32 32 32 32 надо ставить, как 160=32*5)
            continueBased = tP[1]  # Начальная точка след размера
            twinsContinueBased = False  # Признак того что размер является близнецом предыдущего в цепочке
            countTwinsContinueBased = 0  # счетчик текущих близнецов
            iTwins = 1
            objects.extend([p for p in ps])
            if Base is not None:  # Base == 'base':
                for cP in tP[3:]:
                    distP = round(k3.distance(getPforDist(self.tyAxe, cP), getPforDist(self.tyAxe, continueBased))[0],
                                  1)  # Значение размера
                    twinsContinueBased = abs(distP - dimTwinsValue) < 0.1 and distP < 65
                    if Base == 'base':
                        try:
                            pp = k3.ldim(k3.k_base, k3.k_select, k3.k_separately, objects[-1], self.basedPoint,
                                         cP)  #k3.ldim(k3.k_base,cP)
                            self.edDimBaseLeader(Base, pp, False, tP)
                            objects.extend([p for p in pp])
                        except:
                            print(str('Не смогли построить размер в точку '), cP)
                            pass
                    else:
                        if twinsContinueBased:
                            iTwins += 1
                            self.editDimText(pp, '<>=' + str(int(round(dimTwinsValue))) + 'x' + str(iTwins))
                            self.editDimSize(pp, continueBased, cP)
                            if self.nLeader == 0:
                                self.chDimTextLeader(pp)
                        else:
                            try:
                                pp = k3.ldim(k3.k_continue, cP)
                                self.chDimTextLeader(pp)
                                objects.extend([p for p in pp])
                                iTwins = 1
                            except:
                                print(str('Не смогли построить размер в точку '), cP)
                                pass
                        #twinsContinueBased = abs(distP-dimTwinsValue) < 0.1 and distP < 65
                        dimTwinsValue = distP
                        continueBased = cP
                    cPprev = cP
                if len(objects) == 2 and k3.distance(tP[0], tP[-1])[0] < 100:
                    k3.delete(objects[1])
                    del (objects[1])
                self.list_handle = objects
        return objects

    def chDimTextLeader(self, pp):
        '''Eсли размерный текст выступает за пределы измерения делаем его на выноске
        pp - объект типа размер
        '''
        Arr = Ut.GetRectText(pp)
        if not Ut.isTextSizeLarge(pp, Arr):
            self.setDimTextLeader(pp)
            self.maxLeader = self.nLeader
        else:
            self.setDimBitMask_33(pp)
            self.nLeader = 0

    def getGroupBase(self, tP):
        global g_basegr
        try:
            type(g_basegr)
        except:
            g_basegr = int(k3.GlobalVar('g_basegr').value)
        if len(tP[3:]) > g_basegr:
            groupBase = True
        else:
            groupBase = False
        return groupBase

    def getP(self, objDim):
        adiminfo = VarArray(54, 'adimv')
        return adiminfo

    def edDimBaseLeader(self, Base, ps, firstdim, tP):
        if not self.getGroupBase(tP):
            return None
        if Base == 'base':
            ainfo = k3.VarArray(54)
            self.getDimPar(ps[0])
            d_s = k3.distance(self.basedPoint, self.DimInfo[8:11])
            d_e = k3.distance(self.basedPoint, self.DimInfo[11:14])
            if d_s > d_e:
                plead = (2, 3, 4)
                Plead = (8, 9, 10)
            else:
                plead = (5, 6, 7)
                Plead = (11, 12, 13)
            # определяем ось вдоль которой расположен размер
            if self.isDimAxeX():
                # значит вдоль X
                isx = True
                # определяем в какой стороне - или +
                tsign = self.getSignatureDim()
                if not firstdim:
                    self.DimInfo[3] = self.firstPoint[1]
                    self.DimInfo[6] = self.firstPoint[1]

            else:
                # Значит вдоль Y
                isx = False
                # определяем в какой стороне - или +
                tsign = self.getSignatureDim()
                tsign = sign(self.DimInfo[2] - self.DimInfo[8])
                if not firstdim:
                    self.DimInfo[2] = self.firstPoint[0]
                    self.DimInfo[5] = self.firstPoint[0]

            # Обработка со случаем положения базовой точки
            if self.DimInfo[2:4] == list(self.firstPoint[0:2]):
                dindex_DimInfo = 3
                arrowindexNull = 36
                leaderposit = 1
            else:
                dindex_DimInfo = 0
                arrowindexNull = 37
                leaderposit = 0

            deltaSd = self.GRCOEF * self.SystemDimInfo['ldim'][0]  # Величина сдвига
            #self.DimInfo[2:4]=self.firstPoint[0:2]
            self.DimInfo[32] = k3.nbitclear(ainfo[32], 9)
            self.DimInfo[33] = 5
            self.DimInfo[arrowindexNull] = 0
            self.DimInfo[38] = leaderposit
            self.DimInfo[39] = 2
            self.DimInfo[40] = self.DimInfo[2 + dindex_DimInfo] + tsign * (deltaSd if not isx else 0) / 2
            self.DimInfo[41] = self.DimInfo[3 + dindex_DimInfo] + tsign * (deltaSd if isx else 0) / 2
            self.DimInfo[42] = self.DimInfo[4 + dindex_DimInfo]
            self.DimInfo[43] = self.DimInfo[2 + dindex_DimInfo] + tsign * (deltaSd if not isx else 0)
            self.DimInfo[44] = self.DimInfo[3 + dindex_DimInfo] + tsign * (deltaSd if isx else 0)
            self.DimInfo[45] = self.DimInfo[4 + dindex_DimInfo]
            for i in range(len(self.DimInfo)):
                ainfo[i].value = self.DimInfo[i]
            k3.putdiminfo(ps[0], ainfo)

            pass

    def getSignatureDim(self):
        '''Возвращает + или - положения размера в зависимости от оси'''
        return sign(self.DimInfo[3] - self.DimInfo[9]) if self.isDimAxeX() else sign(self.DimInfo[2] - self.DimInfo[8])

    def isDimAxeX(self):
        '''Возвращает True если размер параллелен X'''
        return abs(self.DimInfo[2] - self.DimInfo[5]) > abs(self.DimInfo[3] - self.DimInfo[6])

        #k3.dimedit(ps[0], k3.k_place, k3.k_leader, 0, (self.DimInfo[2], self.DimInfo[3], self.DimInfo[4]), (self.DimInfo[2], self.DimInfo[3]+1, self.DimInfo[4]) )

    def editDimSize(self, objDim, p1, p2):
        '''Изменяет положение размерной линии размера objDim из измерямой точки p1 в p2'''
        adiminfo = VarArray(54, 'adimv')
        k3.getdiminfo(objDim, adiminfo.array)
        vx, vy, vz = k3.Var(), k3.Var(), k3.Var()
        l_adiminfo = [round(a, 1) if type(a) == float else a for a in [a.value for a in adiminfo.array]]
        tl = list(map(lambda a, b: round(a, 1) - round(b, 1), l_adiminfo[2:5],
                      l_adiminfo[5:8]))  # Вектор существующей размерной линии

        tv = (p2[0] - p1[0], 0, 0) if tl[0] != 0 else (0, p2[1] - p1[1], 0)

        k3.vtranscs(2, 3, tv, vx, vy, vz)
        xv, yv, zv = self.getNormal(vx.value, vy.value, vz.value)

        adiminfo.array[2].value += (xv * vx.value)
        adiminfo.array[3].value += (yv * vy.value)
        adiminfo.array[4].value += (zv * vz.value)

        adiminfo.array[8].value += (xv * vx.value)
        adiminfo.array[9].value += (yv * vy.value)
        adiminfo.array[10].value += (zv * vz.value)
        k3.putdiminfo(objDim, adiminfo.array)


    def getNormal(self, XV, YV, ZV):
        '''Нормируем вектор направления'''
        nor = k3.sqrt(XV * XV + YV * YV + ZV * ZV)
        xv = XV / nor
        yv = YV / nor
        zv = ZV / nor
        return xv, yv, zv


    def editDimText(self, objDim=None, dimText=None):
        '''Изменяет значение текста dimText размера objDim '''
        if objDim is not None and dimText is not None:
            self.getDimPar(objDim)
            adiminfo = self.getP(objDim)
            self.DimInfo[18] = dimText
            for i in range(len(self.DimInfo)):
                adiminfo.array[i].value = self.DimInfo[i]
            k3.putdiminfo(objDim, adiminfo.array)

    def setDimBitMask_33(self, objDim=None):
        '''измеяет из на выноске в автоматом'''
        if (objDim is not None):
            self.getDimPar(objDim)
            if (self.DimInfo[33] == 5 ):  # тип текста на выноске
                self.DimInfo[32] = int(k3.nbitset(int(self.DimInfo[32]), 9))
                self.DimInfo[33] = 0  # тип текста по центру
                for i in range(len(self.DimInfo)):
                    self._aInf[i].value = self.DimInfo[i]
                k3.putdiminfo(objDim, self._aInf)
                self.nLeader -= 1


    def setDimTextLeader(self, objDim=None):
        '''Редактирует пложение размера текста на выноску'''
        if objDim is not None:
            self.getDimPar(objDim)
            adiminfo = self.getP(objDim)
            self.isX = self.isDimAxeX()
            self.tsign = self.getSignatureDim()
            xv, yv, zv = self.getNormal(round(self.DimInfo[5] - self.DimInfo[2], 2),
                                        round(self.DimInfo[6] - self.DimInfo[3], 2),
                                        round(self.DimInfo[7] - self.DimInfo[4], 2))
            nor = k3.sqrt((self.DimInfo[5] - self.DimInfo[2]) ** 2 + (self.DimInfo[6] - self.DimInfo[3]) ** 2 + (
                self.DimInfo[7] - self.DimInfo[4]) ** 2)
            self.mPoint = (
                round(self.DimInfo[2] + nor / 2 * xv, 2),
                round(self.DimInfo[3] + nor / 2 * yv, 2),
                round(self.DimInfo[4] + nor / 2 * zv, 2))
            self.dPoint = []  # первая точка полки выноски
            self.nLeader += 1
            self.dPoint.append(
                round(self.mPoint[0] + self.tsign * self.realhightext * (self.nLeader if not self.isX else 0.25), 2))
            self.dPoint.append(round(self.mPoint[1] + self.tsign * self.realhightext * (self.nLeader if self.isX else 0.25), 2))
            self.dPoint.append(round(self.mPoint[2], 2))
            self.tPoint = [round(a, 1) for a in self.dPoint]  # Вторая точка
            if self.isX:
                self.tPoint[0] += self.tsign
            else:
                self.tPoint[1] += self.tsign
            #lObj = k3.dimedit(objDim[0], k3.k_place, k3.k_leader, 0.5, self.dPoint, self.tPoint)
            self.DimInfo[32] = int(k3.nbitclear(int(self.DimInfo[32]), 9))
            self.DimInfo[33] = 5  # тип текста на выноске
            self.DimInfo[39] = 2  #2-е точки для выноски
            self.DimInfo[38] = 0.5  # из середины
            self.DimInfo[40:43] = self.dPoint
            self.DimInfo[43:46] = self.tPoint
            for i in range(len(self.DimInfo)):
                adiminfo.array[i].value = self.DimInfo[i]
            k3.putdiminfo(objDim, adiminfo.array)
            #return lObj[0]

    def getSystemDimInfo(self):
        aInf = k3.VarArray(21)
        err = k3.sysarr(80, aInf)  # Информация о текущих установках размеров для разных типов
        #(линейный, угловой, радиус, диаметр):
        #1 - Высота символа
        #2 - Отношение ширины к высоте (в процентах)
        #3 - Угол наклона шрифта (в градусах)
        #4 - Разрядка между символами по горизонтали (в процентах)
        #5 - Разрядка между символами по вертикали (в процентах)
        #21-й элемент - величина отступа между размерами от базы
        j = 0
        for nm in ['ldim', 'adim', 'rdim', 'ddim']:
            for i in range(5):
                self.SystemDimInfo[nm].append(aInf[j + i].value)
            j += 5
        self.SystemDimInfo['basedy'] = aInf[20].value


    def getDimPar(self, objDim=None):
        '''Заполняем свойства экземпляра класса по созданному размеру'''

        if objDim is not None:
            nEls = k3.getdiminfo(objDim, self._aInf)
        self.DimInfo = []
        if nEls > 0:  # значит массив заполнен и пришедший объект это размер
            for i in range(int(nEls)):
                self.DimInfo.append(self._aInf[i].value)

    def getListTypeDimText(self, index=0):
        '''возвращает список свойств размеров в существующем экзкемпляре'''
        l = []
        for d in self.list_handle:
            self.getDimPar(d)
            l.append(self.DimInfo[int(index)])
        return l


gVarSide = False
#-----------------------------
class Dimchain:
    '''Цепочка размеров'''

    def __init__(self, Type=['continue', 'continue', 'continue', 'continue']):
        self.Type = Type  # общий тип цепочки размеров Base или Continue
        self.Links = []  # указатели на сами объекты к3 размеры
        self.vDims = []  # указатели на сами объекты Dimension экземпляры класса
        self.VarSide = not gVarSide
        self.flagXmin = False
        self.flagXmax = False
        self.flagYmin = False
        self.flagYmax = False
        try:
            self.base_point = G_BASE  # 1,2,3,4
        except:
            self.base_point = 1
        self.dTrail = {'tXmax': [], 'tXmin': [], 'tYmax': [],
                       'tYmin': []}  # следы построенных цепочек (лекарство от повторов)

    def checkVisibleDimText(self):
        '''Исправляет положение размерного текста сдвигая его если текст не виден
          в случае если исправить невозможно оставляет как есть'''
        #self.Links.reverse()
        for dimObj in self.Links:
            # перебираем список размеров и проверяем на видимость
            for s in self.vDims:  # определяем тип цепочки base/continue
                try:
                    for h in s.list_handle:
                        if h == dimObj:
                            base = s.base
                except:
                    pass
            Arr = Ut.GetRectText(dimObj)
            keyChek = False
            for j in range(1, 12):
                for sign in [1, -1]:
                    Arr = Ut.GetRectText(dimObj)
                    if Ut.isTextSizeLarge(dimObj, Arr) or base == 'base':

                        k3.invisible(k3.k_partly, dimObj, k3.k_done)

                        vis = Ut.IsVsblRect(nVport=k3.sysvar(51), Arr=Arr)
                        k3.visible(k3.k_partly, dimObj, k3.k_done)

                        if vis:
                            # место занято
                            err = self.editDimPlace(dimObj, (0.5 + sign * j / 10.0))
                        else:
                            keyChek = True
                            break
                    else:
                        keyChek = True
                        break
                if keyChek == True:
                    break

    def editDimPlace(self, dim, kf):
        '''Смещает текст вдоль размерной линии'''
        adiminfo = VarArray(54, 'adimv')
        k3.getdiminfo(dim, adiminfo.array)
        if adiminfo.array[33].value != 5.0:  # Если размер вдоль линии
            adiminfo.array[32].value = k3.nbitclear(int(adiminfo.array[32].value), 9)
            adiminfo.array[33].value = 3
            adiminfo.array[38].value = kf
        else:  # Если размер на выноске
            # определяем ось вдоль которой расположен размер
            if abs(adiminfo.array[2].value - adiminfo.array[5].value) > abs(
                            adiminfo.array[3].value - adiminfo.array[6].value):
                # значит вдоль X
                isx = True
                # определяем в какой стороне - или +
                tsign = sign(adiminfo.array[3].value - adiminfo.array[9].value)
            else:
                # Значит вдоль Y
                isx = False
                # определяем в какой стороне - или +
                tsign = sign(adiminfo.array[2].value - adiminfo.array[8].value)
            deltaSd = self.vDims[0].GRCOEF * self.vDims[0].SystemDimInfo['ldim'][0] * (abs(kf) + 1)  # Величина сдвига
            adiminfo.array[40].value = adiminfo.array[40].value + tsign * (deltaSd if not isx else 0) / 2
            adiminfo.array[41].value = adiminfo.array[41].value + tsign * (deltaSd if isx else 0) / 2

            adiminfo.array[43].value = adiminfo.array[43].value + tsign * (deltaSd if not isx else 0)
            adiminfo.array[44].value = adiminfo.array[44].value + tsign * (deltaSd if isx else 0)

        k3.putdiminfo(dim, adiminfo.array)

    def invisAllDimLine(self, lstDim):
        '''Гасит все линии в размерах списка lstDim'''
        adiminfo = VarArray(54, 'adim')
        for td in lstDim:
            k3.getdiminfo(td, adiminfo.array)
            adiminfo.array[32].value = k3.nbitset(int(adiminfo.array[32].value), 1)  # Размерная линия не отображается
            adiminfo.array[32].value = k3.nbitset(int(adiminfo.array[32].value), 2)
            adiminfo.array[32].value = k3.nbitset(int(adiminfo.array[32].value), 3)
            k3.putdiminfo(td, adiminfo.array)

    def visibleAllDimLine(self, lstDim):
        '''Высвечивает все линии в размерах списка lstDim'''
        adiminfo = VarArray(54, 'adim')
        for td in lstDim:
            k3.getdiminfo(td, adiminfo.array)
            adiminfo.array[32].value = k3.nbitclear(int(adiminfo.array[32].value), 1)
            adiminfo.array[32].value = k3.nbitclear(int(adiminfo.array[32].value), 2)
            adiminfo.array[32].value = k3.nbitclear(int(adiminfo.array[32].value), 3)
            k3.putdiminfo(td, adiminfo.array)

    def exDablCoord(self, Ax='X', Val=[], pDrawNet=[], vMin=True):
        '''Возвращает список точек с добавленным экстримальным значением второй координаты'''
        result = []
        for val in Val:
            if Ax == 'X':
                pt = (val, min(drawing.dTx[val]), 0) if vMin == True else (val, max(drawing.dTx[val]), 0)
                result.append(pt)
            else:
                pt = (min(drawing.dTy[val]), val, 0) if vMin == True else (max(drawing.dTy[val]), val, 0)
                result.append(pt)

        return result

    def _getFreePointPosition(self, delta, gabs, pElements, axe, hdelta):
        '''Возвращает точку для размещения текста размерной цепи
          в зависимости от положения
          point1 - точки цепи в пределах
          gabs - прямоугольника описанного списком  и отступом
          delta - отступ создает граничный пояс
          axe - ось вдоль которой строится цепочка X или Y
          hdelta - шаг поиска свободной зоны '''
        issign = lambda S: 1 if S >= -0.001 else -1
        lPoint = (pElements[0], pElements)
        point1 = (pElements[0][0], (pElements[1][1] - pElements[1][0]) / 2 + pElements[1][0], 0) if axe in ['y', 'Y',
                                                                                                            1] else (
            (pElements[1][1] - pElements[1][0]) / 2 + pElements[1][0], pElements[0][0], 0)
        deltaX = delta if axe in ['y', 'Y', 1] else 0
        deltaY = delta if axe in ['x', 'X', 0] else 0
        gabs = [round(a, 1) for a in gabs]

        if gabs[3] - gabs[0] < 2 * deltaX or gabs[4] - gabs[
            1] < 2 * deltaY:  # если габарит меньше двух границ возвращаем None
            return None

        gab_min_place = [gabs[0] + deltaX, gabs[1] + deltaY, gabs[3] - deltaX, gabs[4] - deltaY]
        gab_max_place = [gabs[0], gabs[1], gabs[3], gabs[4]]

        mid_position = (gabs[3] - gabs[0]) / 2, (gabs[4] - gabs[1]) / 2, 0

        # определяем принадлежность граничному поясу
        rest = range(4)
        if gab_min_place[2] - gab_min_place[0] > 0 and gab_min_place[3] - gab_min_place[1] > 0:
            # имеет минимальную зону и граничный пояс
            pt = point1[:2]
            if gab_min_place[0] <= pt[0] <= gab_min_place[2] and gab_min_place[1] <= pt[1] <= gab_min_place[3]:
                # принадлежит минимальной зоне. может иметь 4 положения 2 внешних и 2 внутренних
                vis = True
                aRect = VarArray(Size=9, Name='arr')
                for i in range(1, 1000, 1):

                    for j in range(0, 2, 1):
                        hdelta = hdelta * (-1)
                        if axe in ['y', 'Y', 1]:
                            #Arr[1..3] - первая задает нижний левый угол прямоугольника
                            #Arr[4..6] - вторая задает верхний левый угол прямоугольника
                            #Arr[7..9] - третья задает нижний правый угол прямоугольника
                            dblCord = pElements[0][0] + i * hdelta
                            dblCord = dblCord if abs(dblCord - gabs[0]) > 0.001 else dblCord + 10  # Добавил 03/04/2014
                            dblCord = dblCord if abs(dblCord - gabs[3]) > 0.001 else dblCord + 10  # Добавил 03/04/2014
                            if gab_min_place[1] <= dblCord <= gab_min_place[3]:
                                lRect = []
                                lRect.append(dblCord)
                                lRect.append(pElements[1][0])
                                lRect.append(0)

                                lRect.append(dblCord)
                                lRect.append(pElements[1][1])
                                lRect.append(0)

                                lRect.append(pElements[0][0] + i * 2 * hdelta)
                                lRect.append(pElements[1][0])
                                lRect.append(0)

                                lRect = ptransPcsToGsc(lRect)
                                aRect.index = 0
                                nullout = [aRect.append(tValArr) for tValArr in lRect]
                                del (lRect)
                            else:
                                # Вышли за пределы допустимой области
                                rest = None
                                return rest
                        vis = Ut.IsVsblRect(nVport=k3.sysvar(51), Arr=aRect.array)
                        if vis == False:
                            break
                    if vis == False:
                        break
                rest = dblCord
            else:
                # граничный пояс доступно только внешнее расположение
                rest = None
        if type(rest) == range:
            rest = None
        return rest

    def create(self, sdvigDim=[80, 80, 80, 80], tGab=[0, 0, 0, 0, 0, 0], cDOBJECT=[],
               lRevisia=[[], []]):
        #tXmax,tXmin,tYmax,tYmin
        '''Создает сеть размеров'''
        pDrawNet = []
        tDim = Dimension()  # Объект класса
        startSD = [tDim.realhightext] * 4  # Сдвиги по сторонам равны tDim.realhightext
        # Перебираем все объекты которые хотим образмерить и читаем координаты точек
        for tdobj in cDOBJECT:
            if 'getPointForDrawing' in tdobj.__class__.__dict__:
                ttObj = tdobj.getPointForDrawing()
                if type(ttObj) == tuple:
                    ppt = tupleToPoint(ttObj)
                    pDrawNet.append(ppt)
                elif type(ttObj) == list:
                    for elist in ttObj:
                        ppt = tupleToPoint(elist)
                        if ppt is not None:
                            pDrawNet.append(ppt)

        oDim = k3.sysvar(60)
        #------------------------------------------------------------
        vBase_Xmin = self.Type[2]
        vBase_Xmax = self.Type[3]
        vBase_Ymin = self.Type[0]
        vBase_Ymax = self.Type[1]
        sGab = [(tGab[0], tGab[1], 0), (tGab[0], tGab[4], 0), (tGab[3], tGab[4], 0), (tGab[3], tGab[1], 0)]

        if len(pDrawNet) > 0:
            for eGab in sGab:
                ppt = tupleToPoint(eGab)
                pDrawNet.append(ppt)

        tXmax, tXmin, tYmax, tYmin, lRevisia = drawing.sortPointsArround(pDrawNet, (tGab[3] - tGab[0]),
                                                                         (tGab[4] - tGab[1]), lRevisia=lRevisia,
                                                                         VarSide=self.VarSide)

        tXmin = delElemsList(tXmin)
        tYmin = delElemsList(tYmin)
        tXmax = delElemsList(tXmax)
        tYmax = delElemsList(tYmax)

        # ---- если размеры от базы и в цепочках по min и max встречается один размер происходит дублирование. Чистим списки
        # ---- Но все зависит от базовой точки
        if vBase_Xmin == vBase_Xmax == 'base':
            if G_BASE in [1, 4]:
                tXmin, tXmax = self.delLastElemsTuple(tXmin, tXmax)
            else:
                tXmin, tXmax = self.delFirstElemsTuple(tXmin, tXmax)
        if vBase_Xmin == vBase_Xmax == 'base':
            if G_BASE in [2, 1]:
                tYmin, tYmax = self.delLastElemsTuple(tYmin, tYmax)
            else:
                tYmin, tYmax = self.delFirstElemsTuple(tYmin, tYmax)

        f = lambda x, y, z: (x, y, z)

        yy = [tGab[1]]
        zz = [0]
        if len(tXmin) > 0:  # По стороне D
            if len(tXmin) > 1:
                if len(tXmin) == 2 and abs((tXmin[0]) - tGab[0]) < 0.1 and abs((tXmin[1]) - tGab[3]) < 0.1:
                    pass
                elif not self.isInTrail('tXmin', tXmin):
                    if tGab[3] in [round(a, 3) for a in tXmin] and self.flagXmin == False:
                        self.flagXmin = True
                    tXmin = self.exDablCoord(Val=tXmin, pDrawNet=pDrawNet, vMin=True)
                    cExtr = getExtrCoordPoint(pos=0, listPoint=tXmin,
                                              checklist=[tGab[0], tGab[3]])  # экстремумы второй координаты цепочки
                    s = [a[1] for a in tXmin]
                    s = [s[1], s[-2]]
                    vDim = Dimension()
                    vDim.tyAxe = 0
                    tt = []
                    tt.extend(tXmin[0:2])

                    tt.extend(tXmin[2:])
                    if self.base_point in [3, 2]:
                        tt.reverse()

                    tt.insert(2, (tt[0][0], sGab[0][1] - sdvigDim[3],
                                  tt[0][2]))  # Справедливо если тащим все размеры наружу как в случае базового размера
                    # Для случая continue лучше разместить в свободной зоне

                    objDims = vDim.create(Type='ldim', Base=vBase_Xmin,
                                          tP=tt)  #строим сетку вдоль X в минимальной зоне по Y
                    self.Links.extend(objDims)
                    self.vDims.append(vDim)

                    sdvigDim[3] = sdvigDim[3] + startSD[3] * (vDim.maxLeader + 1 )

        yy = [tGab[4]]
        zz = [0]
        if len(tXmax) > 0:  # По стороне E
            if len(tXmax) > 1:
                if len(tXmax) == 2 and abs((tXmax[0]) - tGab[0]) < 0.1 and abs((tXmax[1]) - tGab[3]) < 0.1:
                    pass
                elif not self.isInTrail('tXmax', tXmax):
                    if tGab[3] in [round(a, 3) for a in tXmax] and self.flagXmax == False:
                        self.flagXmax = True
                    tXmax = self.exDablCoord(Val=tXmax, pDrawNet=pDrawNet, vMin=False)
                    cExtr = getExtrCoordPoint(pos=0, listPoint=tXmax,
                                              checklist=[tGab[0], tGab[3]])  # экстремумы второй координаты цепочки
                    s = [a[1] for a in tXmax]
                    s = [s[1], s[-2]]
                    vDim = Dimension()
                    vDim.tyAxe = 0
                    tt = []
                    tt.extend(tXmax[0:2])

                    tt.extend(tXmax[2:])
                    if self.base_point in [3, 2]:
                        tt.reverse()

                    tt.insert(2, (tt[0][0], sGab[1][1] + sdvigDim[2], tt[0][2]))
                    objDims = vDim.create(Type='ldim', Base=vBase_Xmax, tP=tt)
                    self.Links.extend(objDims)
                    self.vDims.append(vDim)
                    sdvigDim[2] = sdvigDim[2] + startSD[2] * (vDim.maxLeader + 1 )

        xx = [tGab[0]]
        zz = [0]
        if len(tYmin) > 0:  # По стороне B
            if len(tYmin) > 1:
                if len(tYmin) == 2 and abs((tYmin[0]) - tGab[1]) < 0.1 and abs((tYmin[1]) - tGab[4]) < 0.1:
                    pass
                elif not self.isInTrail('tYmin', tYmin):
                    if tGab[4] in [round(a, 3) for a in tYmin] and self.flagYmin == False:
                        self.flagYmin = True
                    tYmin = self.exDablCoord(Ax='Y', Val=tYmin, pDrawNet=pDrawNet, vMin=True)
                    dblCord = self.getDblCord(pos='Y', listPoint=tYmin, tGab=tGab)
                    s = [a[0] for a in tYmin]
                    s = [s[1], s[-2]]
                    vDim = Dimension()
                    vDim.tyAxe = 1
                    tt = []
                    tt.extend(tYmin[0:2])

                    tt.extend(tYmin[2:])
                    if self.base_point in [4, 3]:
                        tt.reverse()

                    #----------------------------------------------------------------
                    keysdvigDim = False
                    if (vBase_Ymin == 'continue') and (dblCord is not None):
                        tt.insert(2, (dblCord, tt[0][1], tt[0][2]))
                    else:
                        tt.insert(2, (sGab[0][0] - sdvigDim[1], tt[0][1], tt[0][2]))
                        keysdvigDim = True

                    objDims = vDim.create(Type='ldim', Base=vBase_Ymin, tP=tt)
                    self.Links.extend(objDims)
                    self.vDims.append(vDim)

                    if keysdvigDim:
                        sdvigDim[1] = sdvigDim[1] + startSD[1] * (vDim.maxLeader + 1 )

        xx = [tGab[3]]
        zz = [0]
        if len(tYmax) > 0:  # По стороне С
            if len(tYmax) > 1:
                if len(tYmax) == 2 and abs((tYmax[0]) - tGab[1]) < 0.1 and abs((tYmax[1]) - tGab[4]) < 0.1:
                    pass
                elif not self.isInTrail('tYmax', tYmax):
                    if tGab[4] in [round(a, 3) for a in tYmax] and self.flagYmax == False:
                        self.flagYmax = True
                    tYmax = self.exDablCoord(Ax='Y', Val=tYmax, pDrawNet=pDrawNet, vMin=False)
                    dblCord = self.getDblCord(pos='Y', listPoint=tYmax, tGab=tGab)
                    vDim = Dimension()
                    vDim.tyAxe = 1
                    tt = []
                    tt.extend(tYmax[0:2])
                    tt.extend(tYmax[2:])
                    if self.base_point in [4, 3]:
                        tt.reverse()

                    #tt[2:1] = [(sGab[2][0]+sdvigDim[0],tt[0][1],tt[0][2])]
                    keysdvigDim = False
                    if (vBase_Ymax == 'continue') and (dblCord is not None):
                        tt.insert(2, (dblCord, tt[0][1], tt[0][2]))
                    else:
                        tt.insert(2, (sGab[2][0] + sdvigDim[0], tt[0][1], tt[0][2]))
                        keysdvigDim = True

                    objDims = vDim.create(Type='ldim', Base=vBase_Ymax, tP=tt)
                    self.Links.extend(objDims)
                    self.vDims.append(vDim)
                    if (dblCord is not None):
                        if dblCord > tGab[3]:
                            sdvigDim[0] = sdvigDim[0] + (dblCord - tGab[4]) * (vDim.maxLeader + 1 )
                    if keysdvigDim:
                        sdvigDim[0] = sdvigDim[0] + startSD[0] * (vDim.maxLeader + 1 )
        #k3.interact()
        return sGab, tXmax, tXmin, tYmax, tYmin, sdvigDim, lRevisia

    def isInTrail(self, name, list_value):
        '''Проверяет в словаре self.dTrail[name] наличие списка. При совпадении спискa list_value с точностью 0.1 возвращает True
          Если списка нет, о возвращает False и добавляет его в список словаря self.dTrail[name] '''
        if list_value in self.dTrail[name]:
            result = True  # Такой список есть

        elif len(self.dTrail[name]) > 0:
            for dt in self.dTrail[name]:  # Такого списка нет, но надо проверить поточнее  0.1
                if len(dt) == len(list_value):  # Если длины одинаковые
                    lRevResult = list(map(lambda arg1, arg2: abs(arg1 - arg2), dt,
                                          list_value))  # список абсолютных значений разностей элементов списков
                    result = True not in [0.1 < v for v in
                                          lRevResult]  # если все разности меньше 0.1, Значит такой список есть
                else:
                    result = False

                if result:  # если список найден выходим
                    break

        else:
            result = False  # Такого списка нет
        if not result:
            self.dTrail[name].append(list_value)
        return result

    def getDblCord(self, pos, listPoint, tGab):
        ''' Надстройка над _getFreePointPosition
          готовит данные для вызова этой функции и вызывает ее
          Возвращает вторую координату плоской точки для позиционирования размерной цепи
          для цепи вдоль Y это координата  X для цепи вдоль X Это Y
          ПАРАМЕТРЫ:
          pos-определяет ось вдоль которой строится цепь 'y','Y',1 или 'x','X',0
          listPoint список точек tYmax tYmin tXmax tXmin
          tGab 6-координат габарита'''
        checklist = [tGab[1], tGab[4]] if pos in ['y', 'Y', 1] else [tGab[0], tGab[3]]
        cExtr = getExtrCoordPoint(pos, listPoint, checklist)  # экстремумы второй координаты цепочки
        index = 0 if pos in ['y', 'Y', 1] else 1
        s = [a[index] for a in listPoint]
        s = [s[1], s[-2]]
        dblCord = self._getFreePointPosition(delta=real_h_text * 2, gabs=tGab, pElements=[s, cExtr], axe=pos,
                                             hdelta=real_h_text)
        return dblCord

    def delLastElemsTuple(self, tLmin, tLmax):
        '''Удаляет последний элемент в более длинном списке или во втором если их длины равные'''
        lenMin = len(tLmin)  # определяем длину списков
        lenMax = len(tLmax)
        if lenMin > 0 and lenMax > 0:  #   если оба имеют содержимое
            if abs(tLmin[int(lenMin) - 1] - tLmax[int(
                    lenMax) - 1]) < 0.01:  # Если максимальные значения в списке близки, то из более короткого убираем последний элемент
                if lenMin > lenMax:
                    del (tLmin[int(lenMin) - 1])
                else:
                    del (tLmax[int(lenMax) - 1])
        return tLmin, tLmax

    def delFirstElemsTuple(self, tLmin, tLmax):
        '''Удаляет первый элемент в более длинном списке или во втором если их длины равные'''
        lenMin = len(tLmin)  # определяем длину списков
        lenMax = len(tLmax)
        if lenMin > 0 and lenMax > 0:  #   если оба имеют содержимое
            if abs(tLmin[0] - tLmax[
                0]) < 0.01:  # Если минимальные значения в списке близки, то из более короткого убираем последний элемент
                if lenMin > lenMax:
                    del (tLmin[0])
                else:
                    del (tLmax[0])
        return tLmin, tLmax
    
class Drawproperty(Singleton):
    """
    Свойства панели для чертежа.
    """
    def __init__(self):
        self._getProjPath()
        self.g_name = k3.GlobalVar('g_name')
        self.g_draw = k3.GlobalVar('g_draw')

        
        g_legenda = k3.GlobalVar('g_legenda')
        self.g_legenda = True if g_legenda.value > 0 else False
        
        self.substdirs = substdirs.Substdirs()

    def __call__(self, *kw):
        self._setproperty(kw[0])

    def _getProjPath(self):
        self.ProjPath = k3.getfilepath(k3.sysvar(2))
        return self.ProjPath
    
    def _setproperty(self, Panel):
        ds = int(Panel.CommonPos) if Panel.CommonPos - int(Panel.CommonPos) < 0.0001 else Panel.CommonPos
        ts = {1: '000', 2: '00', 3: '0', 4: '', 5: '', 6: '', 7: '', 8: '', 9: '', }
        self.g_name.value = ts[len(str(int(ds)))] + str(ds) + '_' +  self.rev_name_file_exsimbol(Panel.Name)
        self.title = k3.getfiletitle(k3.sysvar(2))[:-3] + "_" + Panel.Name + '_' + str(int(Panel.CommonPos))
        self._setfld()
        self.numTxt = self.fldTxt + self.g_name.value
        self.list_files_numTxt = self._get_draws(self.fldTxt, self.numTxt+"*.k3")
        self.numJpg = self.fldJpg + self.g_name.value
        self.list_files_numJpg = self._get_draws(self.fldJpg, self.numJpg+"*.jpg")
        self.numWmf = self.fldJpg + self.g_name.value + ".wmf"
    
    def _setfld(self):
        """
        """
        self.fldJpg = self.ProjPath + "Reports\\WMF_Drafts\\"
        self.fldTxt = self.ProjPath + "Reports\\K3_Drafts\\"
    
    def _get_draws(self, root, mask):
        sb = self.substdirs
        sb(cdir=root)
        sb(mask=mask)
        return sb.list_mask_files
    
    @classmethod    
    def rev_name_file_exsimbol(self, nm_file):
        '''ревизия имени файла на допустимые символы'''
        print(nm_file)
        return re.sub('[\s\*\?\"\<\>\|/\\\]', '_', nm_file)
    
drawproperty = Drawproperty()

def getExtrCoordPoint(pos=1, listPoint=[], checklist=[]):
    '''Возвращает  кординаты смещенных середин pos 0,1,2 , что соответствует (X,Y,Z) в списке точек
     listPoint
     listPoint имеет структуру [(x,y,z),(x,y,z),(x,y,z),......,(x,y,z)]

     '''
    dPos = {'y': 1, 'Y': 1, 1: 1, 'x': 0, 'X': 0, 0: 0, 'z': 2, 'Z': 2, 2: 2}
    pos = dPos[pos]
    res = []
    check = []
    dCoord = [a[pos] for a in listPoint]
    for r in dCoord:
        key = True
        for t in checklist:
            if abs(r - t) < 0.1:
                key = False
        if key:
            res.append(r)
        else:
            check.append(r)
    res = list(set(res))  # удаляем дубликаты
    res.sort()
    if len(check) > 0:
        check = list(set(check))  # удаляем дубликаты
        check.sort()
        mn = (min(res) - check[0]) / 2.2 + check[0]
        mx = (check[-1] - max(res)) / 2.2 + max(res)
    else:
        mn = min(res)
        mx = max(res)
    return [mn, mx]


class UniObject:
    def __init__(self):
        self.index_dict = {}  # Элементы

    def addElement(self, elem, index=0):
        '''Создает универсальный плоский объект и сохраняет о нем информацию
          elem - (<тип объекта  1-отрезок 2-дуга>,( 2d-координаты точек ))
          index - имя в словаре куда следует помещать сведения об элементе
          {0:[[(elem),1],[(elem),2],.....],......,5:[[(elem),121],[(elem),122]]}
          '''
        aSize = 6 if elem[0] == 2 else 4
        aAr = k3.VarArray(aSize)
        if elem[0] == 2:  # Если дуга
            elem[1][0:7] = elem[1][0:2] + elem[1][4:6] + elem[1][
                                                         2:4]  # Меняем местами 2,3 и 5,6 (средняя и конечная точка)
        for i in range(aSize):
            aAr[i].value = elem[1][i]
        ln = self.index_dict.keys()
        if index not in ln:
            self.index_dict[index] = []
        tval = int(k3.addunobj2d(elem[0], 0, aAr))
        self.index_dict[index].append([elem, tval])
        return tval

    def freeElements(self):
        ln = self.index_dict.keys()
        for ls in ln:
            for el in self.index_dict[ls]:
                k3.freeunobj2d(el[1])

    def interPoint(self, el1, el2):
        '''Находит точки пересечения между двумя универсальными 2d объектами
          возвращает список парных координат [X,Y,X1,Y1]
          если точек пересечения нет длина списка равна 1
          длина списка равна число найденых точек * 2
          по идее их может быть максимум 2
          '''
        aAr = k3.VarArray(4)
        n = int(k3.interunobj2d(el1, 1, el2, 1, aAr))
        if n > 0:
            #aAr = k3.VarArray(n*2,"aAr")
            aArr = [a.value for a in aAr]
            result = aArr[:n * 2]
            return result
        else:
            return None


class Drawing(Singleton):
    def __init__(self):
        self.cDOBJECT = []  # Объекты чертежа
        self.gab = []  # список точек габарита
        self.paths = []
        self.dTx = {}  # Словарь для построения осевых по отверстиям
        self.dTy = {}  # Словарь для построения осевых по отверстиям
        self.DrawingBandType = 0  # вариант обозначения кромки
        self.dimchain2base = False  # строить замкнутые размерные цепи
        self.ListExceptionsPointsDrill = []  # список "имен" цепей , которые образмеривать не надо. например [(15,13,'A'),(15,13,'F')]
        self.first_side = True

    def getPointForDrawing(self, side='A', objectDraw=[]):
        '''Возвращает список точек для построения размерной цепи '''
        tPoints = []
        for tP in tPoints:
            type(tP)
        return tPoints

    def findSortHols(self, lHoles=[], Axe=None, Rastr32=False, D_H_in_Name=False):
        '''Возвращает упорядоченный 1-словарь отверстий
          {(диаметр, глубина, сторона):[список объектов-отверстий ],(диаметр, глубина, сторона):[список объектов-отверстий ]}
          Введем учет принадлежности оси Axe. 'Y' или 'X'
          Если Axe не None pyfxbn возвращаем список еще и лежащий на одной оси. В этом случае ось и значение попадает в имя
          (диаметр, глубина, сторона, 'X/Y',значение ):[список объектов-отверстий ]

          при этом должна быть кратность между центрами 32 мм Rastr32=True
          (в этом случае в имя потребуется добавить стартовый коэффициент координата/32-int(координата/32))

          Если отверстие (в пласти) располагается от кромки ПВХ 0,4мм на расстоянии 8 мм-не указывать.
          Если отверстие (в пласти) располагается от кромки ПВХ 2мм на расстоянии 10 мм-не указывать.

          2-й словарь используется для построения указателей отверстий типа 2х15 4 отв
          {(диаметр, глубина, сторона):[список объектов-отверстий ],...
          D_H_in_Name - Учитывать особенность геометрии {(диаметр, глубина, сторона):[список объектов-отверстий ],....
          или только {(сторона):[список объектов-отверстий ],...
          '''
        fCMP = lambda a, b: abs(a - b) < 0.01

        def rename_kname(ind, t, ndHoles):
            rr = [r for r in ndHoles[ind][:5]]
            rr.append(t)
            return rr

        #---------------------
        dHoles = {}
        nHoles = {}
        log_sX = False
        log_sY = False
        for hole in lHoles:
            Trough = hole.Through
            diameter = hole.Diameter
            hohe = hole.Hohe
            if  hohe < 0.9:
                continue
            side = iif(Trough, 'AF', hole.Side)
            s_hohe = iif(Trough, Panel.panelThickness, hohe)
            Xc = round(hole.Xc, 6)
            Yc = round(hole.Yc, 6)

            if Axe is None:
                name = (diameter, s_hohe, side) if D_H_in_Name else (side)
                self.add_dict(dHoles, name, hole)
            else:
                if type(Axe) == str:
                    tAxe = Axe
                    Axe = []
                    Axe.append(tAxe)
                if type(Axe) == list:
                    for axe in Axe:
                        if Rastr32:
                            if axe == "Y":
                                RastrCoef = round(Yc / 32 - int(Yc / 32), 6)
                                name = (diameter, s_hohe, side, 'Y', Yc, RastrCoef) if D_H_in_Name else (
                                    side, 'Y', Yc, RastrCoef)

                            elif axe == "X":
                                RastrCoef = round(Xc / 32 - int(Xc / 32), 6)
                                name = (diameter, s_hohe, side, 'X', Xc, RastrCoef) if D_H_in_Name else (
                                    side, 'X', Xc, RastrCoef)
                        else:
                            if axe == "Y":
                                name = (diameter, s_hohe, side, 'Y', Yc) if D_H_in_Name else (side, 'Y', Yc)
                            elif axe == "X":
                                name = (diameter, s_hohe, side, 'X', Xc) if D_H_in_Name else (side, 'X', Xc)

                        self.add_dict(dHoles, name, hole)
                else:

                    raise

            if side in ['B', 'C', 'D', 'E']:
                S_side = 'T'
            else:
                S_side = side

            name = (diameter, s_hohe, S_side)
            nHoles = self.add_dict(nHoles, name, hole)
        # Если вдруг есть несколько рядов отверстий, то их следует образмеривать только по одной оси
        # Например есть два ряда отверстий параллельно оси X  с размерами позиционирования на Y 548 и 68
        #(5, 10, 'F', 'Y', 548.0, 0.234375)
        #(5, 10, 'F', 'Y', 68.0, 0.234375)
        #(5, 10, 'F', 'X', 1447.5, 0.125)
        #(5, 10, 'F', 'X', 1415.5, 0.125)
        #0.234375 -растровый коэфиициент по нему надо объединить списки
        ndHoles = list(dHoles.keys())
        ndHoles.sort()
        if len(ndHoles) == 0:
            return dHoles, nHoles
        list_rastr32 = [list(dh)[:4] + list(dh)[5:] for dh in ndHoles]
        #---------ищем растр-----------
        if len(ndHoles[0]) == 6:
            def rename_kname(ind, t, ndHoles):
                rr = [r for r in ndHoles[ind][:5]]
                rr.append(t)
                return rr

            newKeysName = []
            sskey = 1597.0  # Число фибоначчи
            skey = 0.0  # Стартовое значение
            delta_key = -9999.0
            key = 0
            for ind in range(1, len(ndHoles)):
                t = ndHoles[ind][5]
                # ищем список значений второй координаты
                if ndHoles[ind][3] == 'X':  # Для 'X' Y центра
                    c_base = [th.Yc for th in dHoles[ndHoles[ind]]]  # Для текущего значения
                    t_base = [th.Yc for th in dHoles[ndHoles[ind - 1]]]  # Для предыдущего
                else:
                    c_base = [th.Xc for th in dHoles[ndHoles[ind]]]
                    t_base = [th.Xc for th in dHoles[ndHoles[ind - 1]]]
                key = 0
                if list_rastr32.count(list(ndHoles[ind])[:4] + list(ndHoles[ind])[5:]) < 4:
                    # пренебрегаем растром 32 если можно объединить в растр по межосевому
                    linecenter = True
                    if ndHoles[ind][5] != ndHoles[ind - 1][5]:
                        isCMP = False  # Наличие той же второй координаты
                        for a in c_base:
                            if True in [fCMP(a, b) for b in t_base]:
                                isCMP = True
                                break
                        linecenter = t_base[
                                         0] in c_base  # если вторая координата отверстия совпадает со следующим  True
                        if ndHoles[ind][:4] == ndHoles[ind - 1][:4] and isCMP:
                            t = round(ndHoles[ind][4] - ndHoles[ind - 1][4], 3)
                            if abs(delta_key - t) > 0.001:
                                skey = skey + sskey
                                key = 0
                            else:
                                key = 1
                            delta_key = t
                        else:
                            pass

                    if ind == 1:
                        rr = rename_kname(ind - 1, t + skey, ndHoles) if linecenter else ndHoles[ind - 1]
                        newKeysName.append(tuple(rr))

                    rr = rename_kname(ind, t + skey, ndHoles)
                    newKeysName.append(tuple(rr))
                    #delta_key = -9999.0

                    if key == 1:
                        rr = rename_kname(ind - 2, t + skey, ndHoles)
                        newKeysName[-3] = tuple(rr)
                else:
                    if ind == 1:
                        newKeysName.append(ndHoles[ind - 1])
                    rr = rename_kname(ind, t, ndHoles)
                    newKeysName.append(tuple(rr))
                    delta_key = -9999.0

            for ind in range(len(ndHoles)):
                tv = dHoles[ndHoles[ind]]
                del (dHoles[ndHoles[ind]])
                dHoles[newKeysName[ind]] = tv
            ndHoles = newKeysName
        #---------------------------
        dsTwins = {}  # dsTwins - Список близнецов например (5, 10, 'F', 'Y', 548.0, 0.234375) и (5, 10, 'F', 'Y', 68.0, 0.234375) они совпадают по 5, 10, 'F', 'Y',0.234375      {(5, 10, 'A', 'X', 0.125): [(5, 10, 'A', 'X', 871.5, 0.125), (5, 10, 'A', 'X', 903.5, 0.125), (5, 10, 'A', 'X', 935.5, 0.125), (5, 10, 'A', 'X', 1127.5, 0.125), (5, 10, 'A', 'X', 1159.5, 0.125)]}
        if len(ndHoles[0]) == 6:
            for lHoles in ndHoles:
                nd = list(dsTwins.keys())
                name = (lHoles[0], lHoles[1], lHoles[2], lHoles[3], lHoles[5])
                if findInList(nd, name) is None:
                    dsTwins[name] = []
                dsTwins[name].extend(dHoles[lHoles])
            nd = list(dsTwins.keys())
            dHoles = dsTwins
            # ищем длинной в одно отверстие и стараемся объединить
            self.unionOneDrilllist(dHoles)
        return dHoles, nHoles

    def unionOneDrilllist(self, dHoles):
        '''Объединяет единичные списки отверстий одного типа если у них есть общая координата'''
        dictOneDrill = {}
        for hh in dHoles.items():
            if len(hh[1]) == 1:
                nm = tuple(list(hh[0][:4]) + [hh[1][0].Yc] if hh[0][3] == 'X' else [hh[1][0].Xc])
                dictOneDrill = self.add_dict(dictOneDrill, nm, hh[0])
        for hh in dictOneDrill.items():
            if len(hh[1]) > 1:
                tn = hh[1][0]
                for e in hh[1][1:]:
                    dHoles[tn].extend(dHoles[e])
                    del (dHoles[e])

    def add_dict(self, dHoles, name, hole):
        ''' Пополняем список по ключу'''
        findInList(list(dHoles.keys()), name)
        if next((key for key in list(dHoles.keys()) if key == name), None) == None:
            dHoles[name] = []
        dHoles[name].append(hole)
        return dHoles

    def sortPointsArround(self, tPoints=[], SizeX=0, SizeY=0, lRevisia=[[], []], VarSide=True, axe_only=['X', 'Y']):
        #tXmax,tXmin,tYmax,tYmin
        ''' Вариант когда точки следует поделить по принадлежности сторонам +X -X +Y -Y'''
        tMaxX, tMinX, tMaxY, tMinY = [], [], [], []
        tMaxXO, tMinXO, tMaxYO, tMinYO = [], [], [], []
        tListRevisia = [[], []]
        tMaxYO = [ob for ob in tPoints if ob.x > SizeX / 2.0]
        tMinYO = [ob for ob in tPoints if ob.x <= SizeX / 2.0]
        tMaxXO = [ob for ob in tPoints if ob.y > SizeY / 2.0]
        tMinXO = [ob for ob in tPoints if ob.y <= SizeY / 2.0]
        if VarSide:
            tMaxX, tMinX, tMaxY, tMinY = self.SortListPointAllSide(lRevisia, tMaxXO, tMinXO, tMaxYO, tMinYO)
            aMaxX, aMinX, aMaxY, aMinY = self.SortListPointAllSide(tListRevisia, tMaxXO, tMinXO, tMaxYO, tMinYO)
        else:
            tMaxX, tMinX, tMaxY, tMinY = self.SortListPointAllSide(lRevisia, tMinXO, tMaxXO, tMinYO, tMaxYO)
            aMaxX, aMinX, aMaxY, aMinY = self.SortListPointAllSide(tListRevisia, tMinXO, tMaxXO, tMinYO, tMaxYO)

        # Исключаем из tMinY объекты схожие с
        lRevisia[0] = lRevisia[0] + iif('Y' in axe_only, tMaxX + tMinX, [])
        lRevisia[1] = lRevisia[1] + iif('X' in axe_only, tMaxY + tMinY, [])
        #-------------------------------------
        # данные для построения сетки осевых линий
        tX = aMaxX + aMinX
        tY = aMaxY + aMinY
        self.dTx = {}
        self.dTy = {}
        for tPnt in tPoints:
            if len(tX) > 0:
                for vl in tX:
                    if abs(tPnt.x - vl) < 0.1:
                        self.dTx[vl] = self.dTx.get(vl, [])
                        self.dTx[vl].append(round(tPnt.y, 2))
                        self.dTx[vl] = list(set(self.dTx[vl]))
        for tPnt in tPoints:
            for vl in tY:
                if len(tY) > 0:
                    if abs(tPnt.y - vl) < 0.1:
                        self.dTy[vl] = self.dTy.get(vl, [])
                        self.dTy[vl].append(round(tPnt.x, 2))
                        self.dTy[vl] = list(set(self.dTy[vl]))
                        #self.dTy[vl].sort()
        #-------------------------------------
        return tMaxX, tMinX, tMaxY, tMinY, lRevisia

    def SortListPointAllSide(self, lRevisia, MaxXO, MinXO, MaxYO, MinYO):
        tMinX = self.SortListPoint(MinXO, tRevisia=lRevisia[0])  # Размерная сетка вдоль X
        tMaxX = self.SortListPoint(MaxXO, tRevisia=tMinX + lRevisia[0])  # Размерная сетка вдоль X

        tMaxY = self.SortListPoint(MaxYO, side=0, tRevisia=lRevisia[1])  # Размерная сетка вдоль Y
        tMinY = self.SortListPoint(MinYO, side=0, tRevisia=tMaxY + lRevisia[1])  # Размерная сетка вдоль Y

        return tMaxX, tMinX, tMaxY, tMinY

    def SortListPoint(self, tdd=[], side=1, tRevisia=[]):
        '''Сортирует список tdd объектов экземпляров класса Point по координате X если side==1 или по Y в другом случае
          возвращает только список координат вдоль заданой оси исключая элементы, присутствующие в tRevisia '''
        tss = []
        tnn = []
        if len(tdd) > 0:
            tdd = list(set(tdd))
            #tss=sorted(tdd, key = lambda ob: [ob.x, ob.y] if side == 1 else lambda ob: [ob.y, ob.x])
            #t_1=map(lambda ob: ob.x if side == 1 else lambda ob: ob.y ,tss)
            #t_2=[ob.x if side == 1 else ob.y for ob in tss]
            if side == 1:
                tss = sorted(tdd, key=lambda ob: [ob.x, ob.y])
                t_1 = list(map(lambda ob: ob.x, tss))
                t_2 = [ob.x for ob in tss]
            else:
                tss = sorted(tdd, key=lambda ob: [ob.y, ob.x])
                t_1 = list(map(lambda ob: ob.y, tss))
                t_2 = [ob.y for ob in tss]
            tss = sorted(list(set(t_2)))
            if len(tRevisia) > 0:
                tnn = []
                sBasedP = tss[0]
                eBasedP = tss[-1]
                if len(tss) > 2:
                    tnn.append(tss[0])
                for val in tss:  #[1:-1]
                    result = findInList(tRevisia, val)  #next((x for x in tRevisia if x == val), None)
                    if result is None:
                        tnn.append(val)
                if len(tss) > 2 and self.dimchain2base:
                    tnn.append(tss[-1])  # Добавляет точку габарита
                if len(tnn) == 2 and tnn[0] == sBasedP and tnn[1] == eBasedP:  # в списке только габаритный размер
                    tnn = []
                if tnn is None:
                    tnn = []
                return tnn
            else:
                if tss is None:
                    tss = []
                return tss
        return tnn

if 'drawing' in globals().keys():
    del(drawing)
drawing = Drawing()

#-----------------------------
def findInList(seq=[], name=None):
    '''Ищет значение name в списке seq если не найдено возвращает None'''
    result = next((val for val in seq if val == name), None)
    return result


#-----------------------------
class Slot:
    '''пропил в панели K3'''

    def __init__(self, ps):
        self.Plane = ps.Plane  # Пласть
        self.Side = ps.Side  # Сторона 9-свободная
        self.Shift = ps.Shift  # Сдвиг вглубь или Y коорд
        self.Width = ps.Width  # Ширина пропила
        self.Depth = ps.Depth  # Глубина пропила
        self.Beg = ps.Beg  # Сдвиг
        self.Length = ps.Length  # Длина
        self.Angle = ps.Angle  # Угол
        self.Map = ps.Map  # номер секции раскраш
        self.Xs = None  # Координата X начала оси в ЛСК панели
        self.Ys = None  # Координата Y начала оси  в ЛСК панели
        self.Xe = None  # Координата X конца оси в ЛСК панели
        self.Ye = None  # Координата Y конца оси в ЛСК панели


    def getPointForDrawing(self):
        '''Возвращает координаты точки для размерной цепи'''
        result = []
        result.append((self.Xs, self.Ys, 0))
        result.append((self.Xe, self.Ye, 0))

        return result

    def Draw(self, Side="F", pS=None, t_pk=[]):
        '''Изображение пропила'''
        SideSlot = {'B': 7, 'C': 3, 'D': 1, 'E': 5, 'N': 9}
        result = False
        tempObj = k3.Var()
        k3.setucs(k3.k_save, 'tempPrect')
        if (pS is not None):
            if pS.Shift > -0.01 or pS.Length < 1:
                if pS.Length == -1:
                    pS.Length = 10000
    
                if pS.Length == 0:
                    pS.Length = 10000
                    #if pS.Side!=SideSlot['N']:
                    #pS.Beg = -2000
    
                if pS.Side == SideSlot['B']:
                    coord_X = pS.Shift  # Сдвиг  пропила  вглубь  панели  или  координата  Y пропила в ЛСК панели
                    coord_Y = Panel.plength - pS.Beg  # Сдвиг пропила вдоль торца или координата X
                    vector = [0, -1, 0]
    
                if pS.Side == SideSlot['C']:
                    coord_X = Panel.pwidth - pS.Shift  # Сдвиг  пропила  вглубь  панели  или  координата  Y пропила в ЛСК панели
                    coord_Y = pS.Beg  # Сдвиг пропила вдоль торца или координата X
                    vector = [0, 1, 0]
    
                if pS.Side == SideSlot['D']:
                    coord_Y = pS.Shift  # Сдвиг  пропила  вглубь  панели  или  координата  Y пропила в ЛСК панели
                    coord_X = pS.Beg  # Сдвиг пропила вдоль торца или координата X
                    vector = [1, 0, 0]
    
                if pS.Side == SideSlot['E']:
                    coord_Y = Panel.plength - pS.Shift  # Сдвиг  пропила  вглубь  панели  или  координата  Y пропила в ЛСК панели
                    coord_X = Panel.pwidth - pS.Beg  # Сдвиг пропила вдоль торца или координата X
                    vector = [-1, 0, 0]
    
                if pS.Side == SideSlot['N']:  # это вариант свободной привязки
                    vector = [1, 0, 0]
                    k3.setucs(pS.Beg, pS.Shift, 0, k3.k_relative, vector, k3.k_oz, k3.k_relative, 0, 0, 1)
                    k3.setucs(k3.k_rotate, k3.k_2points, 0, 0, 0, 0, 0, 1, pS.Angle)
                else:
                    k3.setucs(coord_X, coord_Y, 0, k3.k_relative, vector, k3.k_oz, k3.k_relative, 0, 0, 1)
                    k3.setucs(k3.k_rotate, k3.k_2points, 0, 0, 0, 0, 0, 1, pS.Angle)
    
                if pS.Length > 9000:
                    k3.setucs(k3.k_move, -2000, 0, 0)
                #print pS.Width, 'Ширина пропила'
                #print pS.Depth, 'Глубина пропила'
                #print pS.Length, ' Длина  пропила' #  (для  ограниченных  пропилов):  Если пропил сквозной, параметр  равен 0, если пропил полусквозной, параметр  равен - 1.
                objRec, objPline, objPdomain, t_obj = k3.Var(), k3.Var(), k3.Var(), k3.Var()
                k3.rectangle(k3.k_3points, 0, 0, 0,
                             pS.Length, 0, 0, 0,
                             pS.Width, 0)
                k3.objident(k3.k_last, 1, objRec)
                gV = k3.group(objRec.value)
                #pS.Angle  # Угол поворота пропила
                #pS.Map
                Panel.Otrans(gV[0])
                k3.setucs(k3.k_lcs, gV[0])
                k3.explode(gV[0])
                # если пропил сквозной, то надо сделать булеву операцию
                if pS.Length > 9000:
                    # коррекция прямоугольника внешним контуром
                    if rect_out_cont_correction(objRec, objPline, t_pk, t_obj) is None:
                        k3.delete(objPline.value)
                        k3.setucs(k3.k_restore, 'tempPrect')
                        k3.setucs(k3.k_delete, 'tempPrect')                        
                        return False
                # Рисуем осевую у пропила
                gabSlot = obj_k3_gab3(objRec)
                lineSlot = k3.line(gabSlot[0], ((gabSlot[4] - gabSlot[1]) / 2, 0), k3.k_relative,
                                   (gabSlot[3] - gabSlot[0], 0, 0), k3.k_done)
                OBJ_DXF.addCounterHandle(lineSlot)
                Xs = gabSlot[0]
                Xe = gabSlot[3]
                Ys = (gabSlot[4] - gabSlot[1]) / 2
                Ye = (gabSlot[4] - gabSlot[1]) / 2
                lPSlot = ptransPcsToGsc([Xs, Ys, 0, Xe, Ye, 0])
    
                if len(lineSlot) > 0:
                    k3.chprop(k3.k_ltype, lineSlot, k3.k_done, 5)
                    rad = pS.Width / 2
                    sign_Note = 1
                    # подпись
                    sting1 = "Паз." + str(float2int(pS.Width)) + "x" + str(float2int(pS.Depth))
                    vNote = k3.note(k3.k_normal, (0, 0, 1), k3.k_arrow, 1, k3.k_type, 0,
                                    sting1, "",
                                    (gabSlot[0] + (gabSlot[3] - gabSlot[0]) / 5,
                                     pS.Width / 2 + sign_Note * rad * k3.sin(k3.radian(60)), 0), k3.k_relative,
                                    (sign_Note * real_h_text * k3.cos(k3.radian(60)),
                                     sign_Note * real_h_text * k3.sin(k3.radian(60)), 0), k3.k_relative, (sign_Note, 0, 0))
                    #if Side == 'F':
                    vNote = k3.editobject(vNote[0],k3.k_flip,k3.k_done)
                k3.setucs(k3.k_restore, 'tempPrect')
                k3.setucs(k3.k_delete, 'tempPrect')
                lPSlot = ptransGcsToPsc(lPSlot)
                self.Xs = lPSlot[0]
                self.Ys = lPSlot[1]
                self.Xe = lPSlot[3]
                self.Ye = lPSlot[4]
                result = True
        return result


def rect_out_cont_correction(objRec, objPline, t_pk, t_obj):
    '''коррекция прямоугольника внешним контуром'''
    k3.pline(k3.k_path, objRec.value)
    k3.objident(k3.k_last, 1, objPline)
    k3.move(t_pk[0].value, k3.k_done, (0, 0, 0), k3.k_copy, 1)
    k3.objident(k3.k_last, 1, t_obj)
    if isinstance(k3.polybool(k3.k_inter, t_obj.value, objPline.value)[0], k3.K3Obj):
        k3.delete(objRec.value, k3.k_done)
        k3.objident(k3.k_last, 1, objRec)
        return objRec
    else:
        k3.delete(objRec.value, k3.k_done)
        return None


#-----------------------------


#-----------------------------
class layerToDXF(Ut.Layer):
    '''CNC BIESSE'''

    def layerPars(self, Zp):
        replPoint = lambda s: s.replace('.', 'K')
        if Zp != int(Zp):
            s_Zp = str(Zp)
            s_Zp = replPoint(s_Zp)
        else:
            s_Zp = str(int(Zp))
        return s_Zp

    def set_name_layer_drill(self):
        name_layers = {'AF': 'VERTICA', 'T': 'LATO', 'A': 'VERTICA', 'F': 'VERTICA', 'B': 'LATO3', 'C': 'LATO1',
                       'D': 'LATO4', 'E': 'LATO2'}
        if self.Side in ['B', 'C', 'D', 'E']:
            Zp = Panel.panelThickness - self.Zc
            s_Zp = self.layerPars(Zp)
            nm = name_layers[self.Side] + s_Zp
        elif self.Side in ['A', 'F']:
            Zp = self.Hohe
            s_Zp = self.layerPars(Zp)
            nm = name_layers[self.Side] + s_Zp
        elif self.Side in ['AF']:
            nm = ''
        else:
            nm = ''
        return nm

    def set_name_layer_panel(self):
        nm = 'PANNELLO' + self.layerPars(Panel.panelThickness)
        return nm





#----------------------------------------------
#@Singleton
class KromZnak(Singleton, LayerFun):
    def __init__(self):
        self.startlist = self.sFindKrzn()
        self.BandScene = self.sKromGInit()
        self.OrderID = self.getCurrOrderID()
        self.setTimeCreate()
        self.set_time_refresh_def(5)
        self.time_refresh_interval = self.get_time_refresh_def() # Время ожидания для пересоздания 

    def get_time_refresh_def(self):
        """
        Возвращает время обновления по умолчанию
        """
        return self.time_refresh_default

    def set_time_refresh_def(self, val):
        """
        Устанавливает время обновления по умолчанию
        """
        if isinstance(val, tuple):
            self.time_refresh_default = round(val[0], 0)
        elif isinstance(val, float):
            self.time_refresh_default = round(val, 0)
        else:
            self.time_refresh_default = val

    def refresh(self):
        self.BandScene = self.sKromGInit()
        self.OrderID = self.getCurrOrderID()
        self.setTimeCreate()

    def getCurrOrderID(self):
        fullNm = k3.sysvar(2)
        if len(fullNm) > 3:
            return fullNm.split('\\')[-1].split('.')[0]
        else:
            return ""

    def setTimeCreate(self):
        self.timecreate = time.time()

    def getTimeCreate(self):
        return self.timecreate

    #поиск Номеров значков кромки
    def sFindKrzn(self):
        laZnromB = []
        iZnkrom = 6
        strZNK = "14|15|13|12|10|11"
        if transform_logical_k3_to_python(k3.fileexist(FININAME)) == False:
            k3.putmsg("Файл " + FININAME + " отсутствует. Будет создан автоматически", 0)
            err = k3.putstr(FININAME, "[KromZnak]", 0)
            err = k3.putstr(FININAME, " номера стрелок используемых в качестве обозначения кромки", 0)
            err = k3.putstr(FININAME, "14", 0)
            err = k3.putstr(FININAME, "15", 0)
            err = k3.putstr(FININAME, "13", 0)
            err = k3.putstr(FININAME, "12", 0)
            err = k3.putstr(FININAME, "10", 0)
            err = k3.putstr(FININAME, "11", 0)
            #err=k3.putstr(FININAME,"9",0)
            err = k3.putstr(FININAME, "[", 0)
        else:
            nStr = k3.getcount(FININAME)
            if nStr > 0:
                psection = int(k3.findstring(FININAME, "[KromZnak]", 1,
                                             0))  # ищем нужную секцию и получаем номер строки с которой она начинается
                # теперь проверяем является ли строка коментарием или концом секции коментарием является символ  концом секции символ [
                iZnkrom = 0
                if psection > 0:
                    pstr = psection + 1
                    strZNK = ""
                    while (next((key for key in k3.getstr(FININAME, pstr) if key == '['),
                                None) == None and pstr < nStr):
                        errComm = k3.findstring(FININAME, ";", pstr, 0)  # эта строка содержит комментарий
                        if errComm == 0:  # Это номер значка кромки
                            strZNK = strZNK + iif(len(strZNK) > 0, "|", "") + k3.getstr(FININAME, pstr)
                            iZnkrom = iZnkrom + 1
                        pstr = pstr + 1
        if iZnkrom > 0:
            aZnromB = VarArray(iZnkrom, 'aZnromB')
            res = int(k3.splitbydelim(strZNK, "|", aZnromB.array))
            aZnromB.index = res
            laZnromB = aZnromB.transform_to_list()
            laZnromB = [ff.value for ff in laZnromB]
        return laZnromB

    #==============================================================================

    def sKromGInit(self):
        """Заполняет массивы значками кромок по всему заказу"""

        def get_index_band_(lArr1, self, layer_d, _addInfoInBandScene, index_zn, duble_zn, BandScene, listKromZnak):
            if 'getlistmat' in k3.__dict__:
                nels = k3.getlistmat(1, "arrbd")
                arrbd = k3.VarArray(int(nels), "arrbd")
                lbd = [int(a.value) for a in arrbd]
                t = []
                for Material in lbd:
                    Color = 256
                    Thickness = k3.priceinfo(Material ,'Dept',k3.priceinfo(Material ,'Thickness',0,1),1)
                    element = ElemsInfo()
                    element.Band.Material = Material
                    element.Band.Thickness = Thickness
                    element.Band.Color = int(k3.priceinfo(element.Band.Material ,'Color',0,1))+256
                    element.Band.znak = k3.priceinfo(element.Band.Material ,'znakKrom',0,1)
                    element.Band.znakduble = int(k3.priceinfo(element.Band.Material ,'znakKromDuble',0,1))
                    element.Band.znakindex = int(k3.priceinfo(element.Band.Material ,'znakKromIndex',0,1))
                    put_band_scene(BandScene, element)
                    del(element)
            else:
                lCommonPpos = []
                for el in lArr1:
                    PANEL.dict_pathinfo = {}   # Очищаем информацию по результирующему полилайну
                    ccp = k3.getattr(el, "CommonPos", -99)
                    log_ccp = ccp > 0 and ccp not in lCommonPpos
                    if self.getLayer(el) in ['', ' ']:
                        logL = (True, True)
                    else:
                        logL = layer_d[self.getLayer(el)] if self.getLayer(el) in layer_d.keys() else (False, False)
                    if (False not in logL) and log_ccp:
                        lCommonPpos.append(ccp)
                        pInfo = PANEL.getPanelPathInfo(el)
                        if pInfo is not None:
                            index_zn, duble_zn = _addInfoInBandScene(pInfo, BandScene, index_zn, listKromZnak, duble_zn)
            return index_zn

        def _isExistPickFile(pickle_file_name):
            result = False
            resFFile = int(k3.fileexist(pickle_file_name))  # проверяем есть ли файл с результатом
            if resFFile == 1:  # Значит файл найден
                if k3.getcount(pickle_file_name) > 2:
                    result = True
                else:
                    k3.removefile(pickle_file_name)
                    result = False
            return result
        
        def put_band_scene(BandScene, e):
            name = (e.Band.Material, e.Band.Color, e.Band.Thickness)
            result = findInList(BandScene.keys(), name)
            if result is None and e.Band.Material:
                BandScene[name] = []
                if e.Band.znak > 0:
                    BandScene[name].extend([e.Band.znak, e.Band.znakduble, e.Band.znakindex])
                        
        def _addInfoInBandScene(pInfo, BandScene, index_zn, listKromZnak, duble_zn):
            """Заполняет BandScene """
            for p in pInfo.paths:
                for e in p.elems:
                    put_band_scene(BandScene, e)
            return index_zn, duble_zn

        # определяем сколько в текущем заказе зарегестрировано кромок
        # Что бы не вызывать эту функцию сотни раз для каждой панели пишем результат в Pickle
        # При старте чертежей если файл существует его требуется удалить k3.mpathexpand("<AppData>")+"listkrom.txt"
        layer_d = self.getExistsLayerAll()
        pickle_file_name = k3.mpathexpand("<AppData>") + "\\listkrom.txt"
        if _isExistPickFile(pickle_file_name):
            return LoaderPickle(pickle_file_name)
        else:
            listKromZnak = self.startlist
            lArr1 = GetListAllPanel()  # Получаем список указателей на все панели сцены
            BandScene = {}  # Словарь кромок в сцене
            index_zn = 0
            duble_zn = 0  # признак дублирования значка кромки их всего 6, а кромок может быть больше
            if lArr1 is not None:
                index_zn = get_index_band_(lArr1, self, layer_d, _addInfoInBandScene, index_zn, duble_zn, BandScene, listKromZnak)
                l_nm = list(BandScene.keys())
                l_nm.sort()
                for nm in l_nm:
                    if index_zn > len(listKromZnak) - 1:  # Если индекс превышает число значков
                        duble_zn += 1  # Создаем признак дубля
                        index_zn = 0  # Обнуляем счетчик и начинаем ставить значки сначала
                    if len(BandScene[nm]) == 0:
                        BandScene[nm].extend([listKromZnak[index_zn], duble_zn, 0])
                        index_zn += 1
                DumperPickle(BandScene, pickle_file_name)
            return BandScene

    def drawKromZnak(self, Znak, X, Y, Z, X1, Y1, Z1, key='', duble_zn=0,  index = 0):
        #try:
        g_dopInfKr = k3.GlobalVar('g_dopInfKr').value
        vtx = [" ", ""]
        for b in self.BandScene.items():
            if b[1] == [Znak, duble_zn, index]:
                currentKrom = b[0]
                if b[1][1] > 0:
                    #duble_zn = int(b[1][1])
                    pass
                if b[1][2] > 0:
                    vtx = [str(b[1][2]), '']
                break
        tx_note = {"Нет": [" ", ""],
                   "Толщина": [str(delZero(currentKrom[2])), ""],
                   "Тип": [" ", ""], }
        pNote = k3.Var()
        aXM = [0, 0, 0, 0, 0, 0]
        keyGroup = True
        r_ci = range(int(duble_zn) + 1)
        for dubl in r_ci:
            if dubl == r_ci[-1]:
                if vtx[0] > ' ' and tx_note[g_dopInfKr][0]> ' ':
                    tx[0] =  vtx[0] + '_' + tx_note[g_dopInfKr][0]
                elif vtx[0]> ' ':
                    tx = list(vtx)
                else:
                    tx = tx_note[g_dopInfKr]
                k3.theight(userproperty.textPars[1] / 2)
            else:
                tx = [" ", ""]
                k3.theight(userproperty.textPars[1] / 10)
            delta = (aXM[3] - aXM[0])  #*getGrfCoef()
            delta = userproperty.textPars[1] * getGrfCoef() if (aXM[3] - aXM[0]) > 0 else 0

            vNote = k3.note(k3.k_normal, (0, 0, 1), k3.k_arrow, Znak, k3.k_type, 0,
                            tx, (X + dubl*delta, Y, Z), (X1 + dubl*delta, Y1, Z1), k3.k_relative, (0, 1, 0))
            vNote = k3.editobject(vNote[0],k3.k_flip,k3.k_done)
            if keyGroup:
                k3.group(k3.k_last, 1, k3.k_done)
                k3.objident(k3.k_last, 1, pNote)
                keyGroup = False
            else:
                k3.add(pNote.value, k3.k_last, 1, k3.k_done)
            aXM = obj_k3_gab3(pNote.value)

        k3.theight(userproperty.textPars[1])
        return pNote.value


def creator_kromznak():
    """
     Работает с глобальной переменной KROMZNAK
     Создает если нет
     Освежает если сменился номер заказа или время жизни больше (25 секунд) KROMZNAK.time_refresh_interval
     """
    global KROMZNAK
    if not 'KROMZNAK' in globals().keys():
        KROMZNAK = KromZnak()
    elif (time.time() - KROMZNAK.getTimeCreate() > KROMZNAK.time_refresh_interval
          or KROMZNAK.getCurrOrderID() != KROMZNAK.OrderID):
        KROMZNAK.refresh()
    else:
        KROMZNAK.setTimeCreate()  # Освежаем только время создания
    return KROMZNAK


def DumperPickle(pan, filename):
    '''пишет объекты из списка pan в файл'''
    filer = open(filename, "wb")
    fil = Pickle.dump(pan, filer)
    filer.close()


def LoaderPickle(fname):
    '''Читает объекты из файла'''
    if k3.fileexist(fname) > 0:
        pkl_file = open(fname, 'rb')
        pn = Pickle.load(pkl_file)
        pkl_file.close()
        return pn
    else:
        return []


def GetListAllPanel(dopattr=''):
    nn = int(k3.sysvar(62))
    if nn < 1:
        return []
    lArr1 = []
    listArrAllObjects = Ut.getListArrayAllObjectsScene(AttrFilter='left(furntype,2)==\"01\"')
    for Arr in listArrAllObjects:
        for elem in Arr:
            if isinstance(elem.value, k3.K3Obj):
                if k3.isassign("FurnType", elem.value):
                    tt = k3.getattr(elem.value, "FurnType", "")
                    bdt = True
                    if len(dopattr) > 3 and isinstance(dopattr, str):
                        try:
                            dt = k3.getattr(elem.value, dopattr, 0)
                            bdt = bool(dt)
                        except:
                            dt = k3.getattr(elem.value, dopattr, 'x')
                            bdt = dt != 'x'
                            
                else:
                    tt = 'xxxxxx'
                if bdt:
                    if tt[:2] == '01' and tt[2:] not in ['0000', '1000']:  # находим панели, но не полотна панелей
                        lArr1.append(elem.value)  # добавляем в массив
    return lArr1


def getRandomNameK3(pref='a_'):
    import random
    import string
    nameArrK3 = pref + ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(8))
    while k3.isvardef(nameArrK3) > 0:
        nameArrK3 = 'a_' + ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(8))
    return nameArrK3

    #except:
    #raise BaseException('\nОшибка вызова функции. Слишком много типов кромок')


#----------------------------------------------
#KROMZNAK = KromZnak()
#----------------------------------------------
def getGrfCoef():
    '''возвращает значение текущего графического коэффициента'''
    aR = k3.VarArray(13)
    err = k3.sysarr(43, aR)
    result = [a.value for a in aR]
    return result[2]

#----------------------------------------------
delZero = lambda X: int(X) if X - int(X) < 0.099 else X  # убирает нули первращает вещественное в целое если можно

userproperty = Userproperty()

counter = Counter()
counter.reinit()

#-----------------------------
def PointOutListPoint(args):
    '''Возвращает список из трех превых элементов списка args и изменяет список args укорачивачивая его '''
    return list(map(f_round, args[:3])), args[3:]


#-----------------------------
def ptransPcsToGsc(args=[]):
    '''Принимает на вход список кратный 3 и преобразует точки из текущей системы в ГСК'''
    result = []
    Xc, Yc, Zc = k3.Var(), k3.Var(), k3.Var()
    while len(args) > 0:
        point, args = PointOutListPoint(args)
        #print 'PointOutListPoint1  ',point
        k3.ptranscs(0, 3, point, Xc, Yc, Zc)
        #print 'gooooooood'
        result.append(Xc.value)
        result.append(Yc.value)
        result.append(Zc.value)
    return list(map(f_round, result))


#-----------------------------
def ptransPcsToVcs(args=[]):
    '''Принимает на вход список кратный 3 и преобразует точки из текущей системы в ВСК'''
    result = []
    Xc, Yc, Zc = k3.Var(), k3.Var(), k3.Var()
    while len(args) > 0:
        point, args = PointOutListPoint(args)
        #print 'PointOutListPoint1  ',point
        k3.ptranscs(0, 1, point, Xc, Yc, Zc)
        #print 'gooooooood'
        result.append(Xc.value)
        result.append(Yc.value)
        result.append(Zc.value)
    return list(map(f_round, result))


#---------------------------------
def ptransGcsToVcs(args=[]):
    '''Принимает на вход список кратный 3 и преобразует точки из текущей системы в ВСК'''
    result = []
    Xc, Yc, Zc = k3.Var(), k3.Var(), k3.Var()
    while len(args) > 0:
        point, args = PointOutListPoint(args)
        #print 'PointOutListPoint1  ',point
        k3.ptranscs(3, 1, point, Xc, Yc, Zc)
        #print 'gooooooood'
        result.append(Xc.value)
        result.append(Yc.value)
        result.append(Zc.value)
    return list(map(f_round, result))


#---------------------------------
def ptransGcsToPsc(args=[]):
    '''Принимает на вход список кратный 3 и преобразует точки из ГСК системы в ПСК'''
    result = []
    Xc, Yc, Zc = k3.Var(), k3.Var(), k3.Var()
    while len(args) > 0:
        point, args = PointOutListPoint(args)
        #print 'PointOutListPoint2  ',point
        k3.ptranscs(3, 0, point, Xc, Yc, Zc)
        result.append(Xc.value)
        result.append(Yc.value)
        result.append(Zc.value)
    return list(map(f_round, result))


#-----------------------------
def findMinValInDict(vDict={}, val=0):
    '''Находим минимальное подходящие значение в словаре vDict для величины val'''
    result = None
    tTName = list(vDict.keys())
    tTName.sort()
    for i in tTName:
        rr = i
        if val <= i:
            break
    result = vDict[rr]
    return result


#-----------------------------
def addGeoInfoGCS(pp):
    '''Добавляем значения координат в ГСК'''
    for el in pp.elems:
        el.GeoInfoGCS = ptransPcsToGsc(el.GeoInfo)


#-----------------------------
def drawRadElems(pp, Side):
    '''Расставляет значки радиуса на контуре'''
    tempObj = k3.Var()
    vx, vy, vz = k3.Var(), k3.Var(), k3.Var()

    for el in pp.elems:
        if len(el.GeoInfoGCS) > 0:
            GeoInfoGCS = el.GeoInfoGCS
        else:
            GeoInfoGCS = ptransPcsToGsc(el.GeoInfo)
            el.GeoInfoGCS = GeoInfoGCS
        if el.TypeElem == 2:  # arc
            k3.setucs(el.GeoInfo[6], el.GeoInfo[7], el.GeoInfo[8], el.GeoInfo[0], el.GeoInfo[1], el.GeoInfo[2],
                      el.GeoInfo[3], el.GeoInfo[4], el.GeoInfo[5])
            GeoInfoPCS = ptransGcsToPsc(GeoInfoGCS)
            c_arc = max(GeoInfoPCS[0], GeoInfoPCS[6])  # хорда
            h_arc = GeoInfoPCS[4]  # высота
            r_arc = ((c_arc / 2.0) * (c_arc / 2.0) + h_arc * h_arc) / (2 * h_arc)  # радиус
            ang_arc = k3.acos((r_arc - h_arc) / r_arc)  # половина угла

            #-----
            kf = 0.5
            af = kf * ang_arc
            dy = h_arc - (r_arc - ( r_arc * k3.cos(af)))
            dx = c_arc / 2.0 + r_arc * k3.sin(af)
            dy_1 = dy + 1 * k3.cos(af)
            dx_1 = dx + 1 * k3.sin(af)
            dy_2 = dy + 2 * k3.cos(af)
            dx_2 = dx + 2 * k3.sin(af)
            notePointGsc = ptransPcsToGsc([dx, dy, 0, dx_1, dy_1, 0, dx_2, dy_2, 0])
            k3.setucs(k3.k_previous)
            notePointPsc = ptransGcsToPsc(notePointGsc)

            dx = notePointPsc[0]
            dy = notePointPsc[1]

            dx_1 = notePointPsc[3] - dx
            dy_1 = notePointPsc[4] - dy

            dx_2 = notePointPsc[6] - dx
            dy_2 = notePointPsc[7] - dy

            s_tx = -1
            if Side == 'F':
                s_tx = -1 if el.IdPoly == 1 else 1
            # тупое округление значения радиуса . Надо исправить на реально заданое
            note = Note(normal=(0, 0, 1), Text1="R" + str(delZero(round(r_arc, 0))), Text2="",
                        point1=(dx, dy, 0), relativ1=(dx_1, dy_1, 0), relativ2=(dx_2, dy_2, 0))
            #if Side == 'F':
            #tt = k3.editobject(note,k3.k_mirror,k3.k_done)
            counter.note.append(note)

            #-----

            #k3.text(tx,k3.k_done,GeoInfoPCS[3]-5,GeoInfoPCS[4]+3*s_tx,GeoInfoPCS[5],k3.k_normal,(0,0,s_tx),GeoInfoPCS[3]+5,GeoInfoPCS[4]+3*s_tx,GeoInfoPCS[5])


#-----------------------------
def DrawingBandLab(pp, Side, pk):
    """
    Расставляет значки кромки на контуре
    """
    # ставим значок на кромки
    for el in pp.elems:
        # print(el.IdLine)
        tx = None
        t_txv = '.'
        t_tx = {0.9: 'x', 1.7: 'xxx', 10: 'xx'}
        if el.Band.Thickness is None:
            continue
        tx = findMinValInDict(t_tx, el.Band.Thickness)
        nameBandForDict = (el.Band.Material, el.Band.Color, el.Band.Thickness)
        def_name = lambda nm: (nm[0], nm[2])
        result = findInList(KROMZNAK.BandScene.keys(), nameBandForDict)
        if result is None and nameBandForDict[0] > 1:
            if not(nameBandForDict in KROMZNAK.BandScene.keys()):                
                for e_nm in KROMZNAK.BandScene.keys():
                    if def_name(nameBandForDict) == def_name(e_nm):
                        KROMZNAK.BandScene[nameBandForDict] = KROMZNAK.BandScene[e_nm]
                        break
            else:
                try:
                    KROMZNAK.BandScene[nameBandForDict][0] = KROMZNAK.startlist[len(KROMZNAK.BandScene)]
                except:
                    pass
            
        if drawing.DrawingBandType == 0:
            tx = findMinValInDict(t_tx, el.Band.Thickness)
        elif drawing.DrawingBandType == 1:
            tx = k3.priceinfo(el.Band.Material, "MATNAME", ".", 1)
        if tx is None:
            tx = t_txv

        #if len(el.GeoInfoGCS) > 0:
            #GeoInfoGCS = el.GeoInfoGCS
        #else:
        GeoInfoGCS = ptransPcsToGsc(el.GeoInfo)
        el.GeoInfoGCS = GeoInfoGCS

        if Side == 'F':
            s_tx = -1 if el.IdPoly == 1 else 1
            s_side = -1
        else:
            s_tx = 1 if el.IdPoly == 1 else -1
            s_side = 1

        if el.Band.Material > 0:

            k3.setucs(k3.k_save, 'tDrawSupp')
            if el.TypeElem == 2:  # arc
                k3.setucs(el.GeoInfo[6], el.GeoInfo[7], el.GeoInfo[8], el.GeoInfo[0], el.GeoInfo[1], el.GeoInfo[2],
                          el.GeoInfo[3], el.GeoInfo[4], el.GeoInfo[5])
                GeoInfoPCS = ptransGcsToPsc(GeoInfoGCS)
                testDistPlus = k3.distance(GeoInfoPCS[3], GeoInfoPCS[4] + .2, GeoInfoPCS[5], k3.k_object, pk.value)
                testDistMinus = k3.distance(GeoInfoPCS[3], GeoInfoPCS[4] - .2, GeoInfoPCS[5], k3.k_object, pk.value)
                sgn = iif(testDistPlus > testDistMinus, 1, -1)
                if drawing.DrawingBandType < 2:
                    k3.text(tx, k3.k_done,
                            GeoInfoPCS[3] - 5 * s_side, GeoInfoPCS[4] + 3 * s_tx, GeoInfoPCS[5],
                            k3.k_normal, (0, 0, s_tx),
                            GeoInfoPCS[3] + 5 * s_side, GeoInfoPCS[4] + 3 * s_tx * sgn, GeoInfoPCS[5])
                else:
                    KROMZNAK.drawKromZnak(KROMZNAK.BandScene[nameBandForDict][0],
                                          GeoInfoPCS[3], GeoInfoPCS[4], GeoInfoPCS[5],
                                          GeoInfoPCS[3], GeoInfoPCS[4] + real_h_text / 3 * sgn, GeoInfoPCS[5],
                                          duble_zn=KROMZNAK.BandScene[nameBandForDict][
                                              1], index=KROMZNAK.BandScene[nameBandForDict][
                                              2])  #,key=iif(Side=='F','mirror','')
                    legendaSectionKromka.add(KROMZNAK.BandScene[nameBandForDict])
                k3.setucs(k3.k_restore, 'tDrawSupp')
                k3.setucs(k3.k_delete, 'tDrawSupp')

            if el.TypeElem == 1:  # line
                k3.setucs(el.GeoInfo[3], el.GeoInfo[4], el.GeoInfo[5], k3.k_oz, k3.k_relative, (0, 0, 1), el.GeoInfo[0],
                          el.GeoInfo[1], el.GeoInfo[2])
                GeoInfoPCS = ptransGcsToPsc(GeoInfoGCS)
                if drawing.DrawingBandType < 2:
                    k3.text(tx, k3.k_done, GeoInfoPCS[0] / 2 - 5 * s_side, GeoInfoPCS[4] + 3, GeoInfoPCS[5],
                            k3.k_normal, (0, 0, s_tx), GeoInfoPCS[0] / 2 + 5 * s_side, GeoInfoPCS[4] + 3, GeoInfoPCS[5])
                else:
                    KROMZNAK.drawKromZnak(KROMZNAK.BandScene[nameBandForDict][0],
                                          GeoInfoPCS[0] / 2.3, GeoInfoPCS[4], GeoInfoPCS[5],
                                          GeoInfoPCS[0] / 2.3, GeoInfoPCS[4] + real_h_text / 2, GeoInfoPCS[5],
                                          duble_zn=KROMZNAK.BandScene[nameBandForDict][1],
                                          index=KROMZNAK.BandScene[nameBandForDict][2])  #,key=iif(Side=='F','mirror','')
                    legendaSectionKromka.add(KROMZNAK.BandScene[nameBandForDict])
                k3.setucs(k3.k_restore, 'tDrawSupp')
                k3.setucs(k3.k_delete, 'tDrawSupp')


#-----------------------------
def float2int(arg):
    '''если тип аргумента float и его дробная часть <0.01 преобразуем в int'''
    if abs(arg-int(arg))<0.01:
        arg = int(arg)
    else:
        arg=round(arg, 2)
    return arg

#-----------------------------
tDim = Dimension()

real_h_text = tDim.grcoef[1][2].value * tDim.SystemDimInfo['basedy']  #tDim.realhightext
##-----------------------------

def AddTechLegenda(techs=[]):
    name_sub = '%%uТехнические требования'
    for i in range(len(techs)):
        znak = str(i + 1)
        comment = techs[i]
        ptTech = TechLegenda(znak, comment)
        legenda.addPartInSubsection(name_subsection=name_sub, part=ptTech)


#-----------------------------
class LegendaFromKromka():
    def __init__(self):
        self.BandPanel = {}
        self.name_sub = '%%uУсловные обозначения кромок'

    def add(self, znak):
        for kromka in KROMZNAK.BandScene.items():
            if kromka[1] == znak:
                
                v_matname = k3.priceinfo(kromka[0][0], 'matname', '***', 1)
                v_article = k3.priceinfo(kromka[0][0], 'article', '***', 1)
                
                if len(v_article) > 1 and v_article != '***':
                    matname = v_article
                else:
                    matname = v_matname
               
                alias = k3.priceinfo(kromka[0][0], 'Alias', matname, 1)
                
                comment = ' - ' + (matname + ' (' + alias + ')' if Legenda_Alias else matname)
                ptKrom = PartLegenda(znak, comment)

                if findInList(legenda.dict_subsection.keys(), self.name_sub) is None:
                    legenda.addPartInSubsection(name_subsection=self.name_sub, part=ptKrom)

                elif findInList(legenda.dict_subsection[self.name_sub], ptKrom) is None:
                    legenda.addPartInSubsection(name_subsection=self.name_sub, part=ptKrom)
                else:
                    pass  # значит уже есть


#-----------------------------

#-----------------------------
#legendaSectionKromka = LegendaFromKromka()
#-----------------------------

class LegendaFromCover(adbFunktion):
    def __init__(self):
        self.CoverPanel = {}
        self.name_sub = '%%uОтделки'

    def add(self, legenda, Side=None):
        '''
          Side сторона A a F f

           o 1  - сторона E  (Y+);
           o 2 - сторона D (Y-);
           o 3 - сторона C (X+);
           o 4 - сторона B (X-);
           o 5  - пласть A (Z+);
           o 6 - пласть F (Z-);
           o 7 - угол 1;
           o 8 - угол 2;
           o 9 - угол 3;
           o 10 - угол 4;
           o 11 - дополнение  1;
           o 12 - дополнение  2. '''
        dSide = {'A': 5, 'a': 5, 'F': 6, 'f': 6}
        iCover = 0
        for cover in Panel.cover_info.items():
            
            if (cover[1][0]) in drawing.ListNoGroupCover:
                continue
                
            iCover += 1
            
            znakSide = 'Лицо'
            res = (cover[0]==5, drawing.FrontF)
            if res==(True, True) or res==(False, False):
                znakSide = 'Тыл'
                
            # if cover[0] != dSide[Side]:
                # znakSide = ' Обратная сторона'
            # else:
                # znakSide = ''
                
            matname = self.NmPropInfo(cover[1][1], 'matname', '***') #k3.priceinfo(cover[1][1], 'matname', '***', 1)
            alias = self.NmPropInfo(cover[1][1], 'Alias', matname) # k3.priceinfo(cover[1][1], 'Alias', matname, 1)
            comment = str(iCover) + ' - ' + (matname + ' (' + alias + ')' if Legenda_Alias else matname) + znakSide
            ptCover = PartLegenda(znak=None, comment=comment, ptype='Cover')

            if findInList(legenda.dict_subsection.keys(), self.name_sub) is None:
                legenda.addPartInSubsection(name_subsection=self.name_sub, part=ptCover)

            elif findInList(legenda.dict_subsection[self.name_sub], ptCover) is None:
                legenda.addPartInSubsection(name_subsection=self.name_sub, part=ptCover)
            else:
                pass  # значит уже есть

#-----------------------------
#legendaSectionPrimM = LegendaFromPrimM()
#-----------------------------

class LegendaFromPrimM(adbFunktion):
    def __init__(self):
        self.PrimMPanel = {}
        self.name_sub = '%%uПримечания'

    def add(self, legenda, Side=None):
        '''
          Side сторона A a F 
          '''
        # Почему из рабочей записи???
        n = k3.getattrtext(0, 'PrimM', 'aPrimM')
        # if n > 0:
            # aPrimM = k3.VarArray(int(n), 'aPrimM')
            # for prim in aPrimM:
                # prim.value = "." if len(prim.value) < 1 else prim.value
                # ptPrimM = PartLegenda(znak=None, comment=prim.value, ptype='PrimM')
    
                # if findInList(legenda.dict_subsection.keys(), self.name_sub) is None:
                    # legenda.addPartInSubsection(name_subsection=self.name_sub, part=ptPrimM)
    
                # else :  
                    # legenda.addPartInSubsection(name_subsection=self.name_sub, part=ptPrimM)


#-----------------------------
#-----------------------------
legendside = {'A': Legenda(), 'F': Legenda()}
legenda = Legenda()
legendaSectionKromka = LegendaFromKromka()
legendaSectionPrimM = LegendaFromPrimM()
legendaSectionPrimM.add(legenda)
#-----------------------------
#-----------------------------
f_mid_coord = lambda v1, v2: (v1 + v2) / 2.0
#-----------------------------
def addPanDirSimbol(resultPoly, Panel=Panel):
    """Рисует стрелку направления текстуры панели по середине (центра габаритов)
    результирующего полилайна.
    
    """
    if not Panel.pandir is None:
        t = [None, ]
        if Panel.pandir > -1:
            t = k3.text('%%025==%%023', k3.k_done, 0, 0, 0, k3.k_normal, 0, 0, 1, 1, 0, 0)
            gabT = obj_k3_gab3(t[0])
            midT = list(map(f_mid_coord, gabT[3:], gabT[:3]))
            k3.rotate(k3.k_nocopy, t[0], k3.k_done, k3.k_2points, 0, 0, 0, 0, 0, 1, 180 - Panel.pandir)
            Panel.Otrans(t[0])
            ph = Panel.paths[0].paths[0].holder if resultPoly is None else resultPoly
            gabT = obj_k3_gab3(t[0])
            gabH = obj_k3_gab3(ph)
            midT = list(map(f_mid_coord, gabT[3:], gabT[:3]))
            midH = list(map(f_mid_coord, gabH[3:], gabH[:3]))
            s = k3.extrusion(ph, k3.k_done, 1)
            Panel.amass_locale_ph = ptransGcsToPsc(list(k3.amass(s))[1:])
            if len(Panel.amass_locale_ph) > 0:
                midH = Panel.amass_locale_ph
                midH[2] = 0.
            k3.delete(s)
            k3.move(k3.k_nocopy, t[0], k3.k_done, k3.k_2points, midT, midH)

    return t[0]


def DrawingPanSide(params=[],
                   Side='A',
                   PathIn=1,
                   holes=[],
                   dopTxt='',
                   DimPath=1,
                   nHoles={},
                   TypeDC=['continue', 'continue', 'continue', 'continue'],
                   D_H_in_Name=False,
                   IsFlagPoints=False,
                   Is_Drill_CentralLine=False,
                   IsDrawBasePoint=False,
                   lRevisia=[[], []],
                   dHolRevisia={},
                   is_not_holesdimchain=True
                   ):
    '''Создание чертежа стороны панели

     params  - список парметров передаваемых из макроса
             массив отверстий подготовленный функцией nels=getholes(pnt,"aHoles") 
             число отверстий
             указатель на панель

     Side - это указатель на то какую сторону чертим A или F

     PathIn - вариант чертежа контуров с учетом кромки или без 0-с учетом кромки 1-без учета кромки

     DimPath - 1 - образмеривать контура

     D_H_in_Name - False учитывать или нет маску (диаметр х  глубина) отверстий

     Is_Drill_CentralLine=False - общие оси отверстий

     IsDrawBasePoint=False - указывать базовую точку панели
     lRevisia =[[],[]] точки которые не надо образмеривать
     dHolRevisia = {}  словарь точек отверстий которые не надо образмеривать
     '''

    def set_sGab(InfoPoly):
        pathGabs = obj_k3_gab3(InfoPoly.paths[0].holder)
        InfoPoly.paths[0].gabs = pathGabs
        tGab = InfoPoly.paths[0].gabs
        sGab = [(tGab[0], tGab[1], 0), (tGab[0], tGab[4], 0), (tGab[3], tGab[4], 0), (tGab[3], tGab[1], 0)]
        list_base_point = [sGab[0], sGab[3], sGab[2], sGab[1]]
        dict_base_point = {1: [sGab[0], sGab[1], sGab[3]],
                           4: [sGab[1], sGab[2], sGab[0]],
                           3: [sGab[2], sGab[3], sGab[1]],
                           2: [sGab[3], sGab[0], sGab[2]]}
        drawing.gab = sGab
        return sGab, tGab, list_base_point, dict_base_point

    def _isDimPath(paths, DimPath):
        '''Если в контуре встречаются подряд 3 дуги, контура образмеривать не надо'''
        if DimPath > 0:
            for pp in paths:  # пошли по контурам
                tElsList = [a.TypeElem for a in pp.elems]
                if '2, 2, 2' in str(tElsList):
                    DimPath = 0
        return DimPath

    def _DrawPath(paths, PathIn, DimPath, Side, t_pk, uo):
        r_pk = None

        for i, pp in enumerate(paths):  # пошли по контурам
            pk = pp.draw()
            if isinstance(pk.value, k3.K3Obj):
                pathGabs = obj_k3_gab3(pk.value)
                pp.gabs = pathGabs
                if i == 0:
                    g_pathGabs = pathGabs
                    r_pk = pk.value
                else:
                    if k3.distance(pathGabs[:3], pathGabs[3:])[0] > k3.distance(g_pathGabs[:3], g_pathGabs[3:])[0]:
                        r_pk = pk.value
                k3.chprop(k3.k_lwidth, pk.value, k3.k_done, userproperty.DrawLineS)
                if (pp.cutSide is not None):
                    if (pp.cutSide != Side):
                        k3.chprop(k3.k_lwidth, pk.value, k3.k_done, userproperty.DrawLineS / 2)
                        k3.chprop(k3.k_ltype, pk.value, k3.k_done, 4)
                # Добавляем элементы контура в список универсальных плоских объектов
                if DimPath == 1:
                    drawRadElems(pp, Side)  # Образмериваем радиуса

                DrawingBandLab(pp, Side, pk)  # Ставим значки кромки

                t_pk.append(pk)  # Добавляем контур в список

                for el in pp.elems:
                    geo_inf_elem = [el.GeoInfo[0], el.GeoInfo[1], el.GeoInfo[3],
                                    el.GeoInfo[4]] if el.TypeElem == 1 else [el.GeoInfo[0], el.GeoInfo[1],
                                                                             el.GeoInfo[3], el.GeoInfo[4],
                                                                             el.GeoInfo[6], el.GeoInfo[7]]
                    uo.addElement((el.TypeElem, geo_inf_elem), index=0)

                if (not (Panel.rectangle_forma and i == 0) or i > 0 or pp.cutSide == Side) or (pp.depth is not None):
                    OBJ_DXF.addCounterHandle(pk)
        return r_pk

    legendaSectionCover = LegendaFromCover()
    uo = UniObject()  # Объект работы с универсальными плоскими объектами

    pTxt, tempObj = k3.Var(), k3.Var()
    sdvigDim = [real_h_text, real_h_text, real_h_text, real_h_text]  # #tXmax,tXmin,tYmax,tYmin

    k3.getsnap()
    objects = k3.sysvar(60)
    OBJ_DXF.Counter = []
    listHolDraw = []
    k3.visible(params[2].value)
    k3.setucs(k3.k_lcs, k3.k_partly, params[2].value)

    #k3.invisible(params[2].value)

    list_obj_visible = Ut.getListObjVisual()
    k3.invisible(list_obj_visible, k3.k_done)
    #k3.interact()
    cDOBJECT = []
    listDimchain = []

    if Panel.cover_count > 0:
        legendaSectionCover.add(legendside[Side], Side)

    InfoPoly = Panel.getPanelPathInfo(params[2],
                                      PathIn,
                                      IsCuts=False)  # Получаем информацию по результирующему полилайну
    
    DimPath = _isDimPath(InfoPoly.paths, DimPath)
    if DimPath == 1:
        cDOBJECT.append(InfoPoly)  # добавляем контура  в список объектов чертежа
    t_pk = []
    counter.note = []
    #resultPolyLine

    resultPoly = _DrawPath(InfoPoly.paths, PathIn, DimPath, Side, t_pk, uo)
    drawing.paths = t_pk

    sGab, tGab, list_base_point, dict_base_point = set_sGab(InfoPoly)

    if len(Panel.pSlots) > 0:  #если есть пропилы
        PlaneSlot = {'A': 1, 'F': 0}
        lSlots = []
        for pS in Panel.pSlots:
            if pS.Plane == PlaneSlot[Side]:  #0-F 1-A
                pps = Slot(pS)
                pps.matr = Panel.matr
                pps.Draw(Side=Side, pS=pS, t_pk=t_pk)
                lSlots.append(pps)

    InfoCuts = Panel.getPanelPathInfo(params[2],
                                      PathIn,
                                      IsCuts=True)  # Получаем информацию по глухим вырезам
    Panel.iscuts = len(InfoCuts.paths) > 0 # формируем свойство, что есть глухие вырезы
    DimPath = _isDimPath(InfoCuts.paths, DimPath)
    if DimPath == 1:
        cDOBJECT.append(InfoCuts)  # добавляем контура  в список объектов чертежа
    cutsPoly = _DrawPath(InfoCuts.paths, PathIn, DimPath, Side, t_pk, uo)
    t = addPanDirSimbol(resultPoly)
    objects2 = k3.sysvar(60) - objects

    if objects2 > 0:
        pnt = k3.group(k3.k_last, objects2, k3.k_done)[0]
        k3.setucs(k3.k_gcs)
        k3.place(pnt)
        for note in counter.note:
            obj_note = note.draw()  #key='mirror'
            k3.add(pnt, obj_note, k3.k_done)

            #--------------------------------------------
            #--------------------------------------------
        tXmax, tXmin, tYmax, tYmin = [], [], [], []

        objects2 = k3.sysvar(60)
        if len(Panel.pSlots) > 0:  #если есть пропилы
            sllRevisia = [[], []]
            sllRevisia[0] = [a for a in lRevisia[0]]
            sllRevisia[1] = [a for a in lRevisia[1]]
            if 'continue' not in TypeDC[:2]:
                sllRevisia[0].extend([drawing.gab[0][0], drawing.gab[2][0]])  # список точек которые уже образмерены
            if 'continue' not in TypeDC[2:]:
                sllRevisia[1].extend([drawing.gab[0][1], drawing.gab[1][1]])  # список точек которые уже образмерены
            dimchain = Dimchain(Type=TypeDC)
            listDimchain.append(dimchain)  # Добавляем цепочку в список цепочек.

            sGab, tXmax, tXmin, tYmax, tYmin, sdvigDim, lRevisia = dimchain.create(sdvigDim=sdvigDim, tGab=tGab,
                                                                                   cDOBJECT=lSlots, lRevisia=sllRevisia)
            if len(dimchain.Links) > 0:
                k3.add(pnt, dimchain.Links, k3.k_done)

        # Исключаем точки по Флагам (Точки по условию размеры к которым не ставятся см mPanel.getPanelPathInfo
        # Для Кравцова ДизайнВектор 10 если кромка 2 и 8 если 0,4
        if IsFlagPoints:
            if InfoPoly.FlagXmin is not None:
                lRevisia[0].extend(InfoPoly.FlagXmin)
            if InfoPoly.FlagXmax is not None:
                for t in InfoPoly.FlagXmax: lRevisia[0].append(tGab[3] - t)
            if InfoPoly.FlagYmin is not None:
                lRevisia[1].extend(InfoPoly.FlagYmin)
            if InfoPoly.FlagYmax is not None:
                for t in InfoPoly.FlagYmax: lRevisia[1].append(tGab[4] - t)
        #-----------------------------------------------------

        lRevisia[0].sort()
        lRevisia[1].sort()


        #--------------------------------HOLES
        for h in nHoles.keys():
            if h[2] == 'T':  # T значит торец
                for drl in nHoles[h]:
                    Xe, Ye = drl.getEndPointTHole()
                    Xc, Yc = drl.moveStartPointTHole(10)
                    geo_inf_elem = [Xc, Yc, Xe, Ye]
                    el2 = uo.addElement((1, geo_inf_elem), index=1)
                    for el in uo.index_dict[0]:
                        r = uo.interPoint(el[1], el2)
                        if r is not None:
                            drl.Xc = r[0]
                            drl.Yc = r[1]
        if type(holes) == list:
            noteName = nHoles.items()  # Словарь списков отверстий
            draw_hole_in_tlholes(holes, PathIn, Side, cDOBJECT)
            result_note_Holes = note_Holes(noteName, D_H_in_Name, Side, tempObj)  # Указатели полочки к отверстиям
            # если есть флаг по запросу базовой точки
            getUserBP(list_base_point)
            if result_note_Holes[0]:
                k3.add(pnt, k3.k_last, result_note_Holes[1], k3.k_done)

            dimchain = Dimchain(Type=TypeDC)
            listDimchain.append(dimchain)  # Добавляем цепочку в список цепочек.

            #уточняем габарит чертежа поскольку он теперь имеет выступающие указатели прочую херь
            sdvigDim = setSdvigDim(pnt, tGab, sdvigDim)

            # Чертим отверстия по списку
            if is_not_holesdimchain:
                tt = dimchain_listHoles(holes,
                                        PathIn,
                                        Side,
                                        cDOBJECT,
                                        sdvigDim,
                                        tGab,
                                        dimchain,
                                        Is_Drill_CentralLine,
                                        lRevisia=lRevisia)

            if len(dimchain.Links) > 0:
                k3.add(pnt, dimchain.Links, k3.k_done)

        elif type(holes) == dict:
            holes = holes.items()
            holes = sorted(holes, key=lambda v: (v[0][:4], len(v[1])), reverse=True)
            # оказывается надо ставить размеры цепочкой если!!!!
            # расположены на одной осевой линии, имеют одинаковые размеры (диаметр и глубину сверловки), шаг между отверстиями кратен 32мм
            # 15x13 по пласти исключить из размерных цепей
            noteName = nHoles.items()  # Словарь списков отверстий
            kDOBJECT = []
            for lHoles in holes:
                # Чертим сами отверстия
                tlHoles = lHoles[1]
                tcDOBJECT = []
                
                if (lHoles[0][:3]) in drawing.ListNoNotePointsDrill:
                    for al in lHoles[1]:
                        al.DrawNote = False
                draw_hole_in_tlholes(tlHoles, PathIn, Side, tcDOBJECT)  # чертим сами кружочки и прямоугольники
                if (lHoles[0][:3]) not in drawing.ListExceptionsPointsDrill:
                    kDOBJECT.append((lHoles[0], lHoles[1], tcDOBJECT))


            # если есть флаг по запросу базовой точки
            getUserBP(list_base_point)
            for arg in [i[0] for i in noteName]:
                if findInList(dHolRevisia.keys(), arg) is None:
                    dHolRevisia[arg] = [i for i in lRevisia]

            dimchain = Dimchain(Type=TypeDC)
            dict_dimchain = dimchain.dTrail
            listDimchain.append(dimchain)  # Добавляем цепочку в список цепочек.

            #уточняем габарит чертежа поскольку он теперь имеет выступающие указатели
            sdvigDim = setSdvigDim(pnt, tGab, sdvigDim)

            #for lHoles in holes:
            lstDim = []  # список указателей на все размеры
            kDOBJECT = sorted(kDOBJECT, key=lambda e: [e[0][2:]])
            n_kDOBJECT = listHole_centrPoint_revisia(
                kDOBJECT)  # удаляем отверстия у которых центра совпадают из списка построения размерной цепи

            # Если панель по свободному контуру 
            # и количество отверстий больше допустимого 
            # и условие не выводить, то обнуляем список точек для построения размерной цепочки
            if (
                    (
                        (IsPanFormaFreeNoDrillDraw
                        and Panel.forma == 1
                        and real_len_list(n_kDOBJECT) > NDrillIgnoreForPanFormaFree
                        )
                        or (
                            (IsPanFormaFreeNoDrillDraw
                            and Panel.forma == 2
                            and real_len_list(n_kDOBJECT) > NDrillIgnoreForPanFormaFree
                            ) and (Panel.CurvePath > 0
                                     and (not Panel.rectangle_forma)
                                    )
                        )
                    )
                    or (not is_not_holesdimchain)
                ):
                n_kDOBJECT = []
                AddTechLegenda(techs=['Присадку выполнять по программе ЧПУ'])
                for hole in tcDOBJECT:
                    hole.DrawDim = True
                    listHolDraw.append(hole)

            for lHoles in n_kDOBJECT:
                # отверстия  строим по ним размерные сетки
                tlHoles = lHoles[1]
                tcDOBJECT = []
                dimchain = Dimchain(Type=TypeDC)
                dimchain.dTrail = dict_dimchain
                listDimchain.append(dimchain)  # Добавляем цепочку в список цепочек.

                #draw_hole_in_tlholes(tlHoles, PathIn, Side, tcDOBJECT) # чертим сами кружочки и прямоугольники
                tcDOBJECT = lHoles[2]
                # Чертим отверстия по списку
                if iif(lHoles[0][2] in ['A', 'F', 'AF'], lHoles[0][2], 'T') in [Side, 'AF', 'T', 'X']:
                    #try:
                    # Сеть размеров по отверстиям. Создавать или не создавать - вот в чем вопрос! Иногда не надо. Для этого ставим условие.
                    tt = dimchain_listHoles(tlHoles, PathIn, Side, tcDOBJECT, sdvigDim, tGab, dimchain,
                                            Is_Drill_CentralLine, lRevisia=dHolRevisia[(
                            lHoles[0][0], lHoles[0][1], iif(lHoles[0][2] in ['A', 'F', 'AF', 'X'], lHoles[0][2], 'T'))])
                    
                    #print lHoles[0]
                    dict_dimchain = dimchain.dTrail
                    dHolRevisia[
                        (lHoles[0][0], lHoles[0][1], iif(lHoles[0][2] in ['A', 'F', 'AF', 'X'], lHoles[0][2], 'T'))] = [
                        i for i in tt]

                    for hole in tcDOBJECT:
                        hole.DrawDim = False
                        listHolDraw.append(hole)

                    if len(dimchain.Links) > 0:
                        k3.add(pnt, dimchain.Links, k3.k_done)
                        lstDim.extend(dimchain.Links)  # список указателей на все размеры
                        dimchain.invisAllDimLine(dimchain.Links)  # Гасим размерные линии

            dimchain.visibleAllDimLine(lstDim)  # Высвечиваем размерные линии
            #print 'gggg'
        for dch in listDimchain:
            dch.checkVisibleDimText()  # пробегаем по всем размерам и редактируем положение текста с учетом  видимости

        rectagleObj = k3.rectangle(k3.k_3points, sGab[1], sGab[2], sGab[3])[0]
        if LAYERTODXF:
            lk = layerToDXF()
            lk.Change(obj=rectagleObj, Name=lk.set_name_layer_panel())
        if Panel.CurvePath < 1 or (Panel.CurvePath > 0 and Panel.rectangle_forma):
            OBJ_DXF.addCounterHandle(rectagleObj)
        result_note_Holes = note_Holes(noteName, D_H_in_Name, Side,
                                       tempObj)  # Указатели полочки к отверстиям перенес 13,05,2014 после цепей
        if result_note_Holes[0]:
            k3.add(pnt, k3.k_last, result_note_Holes[1], k3.k_done)

        if IsDrawBasePoint:  # чертим базовую точку

            TUCS = k3.setucs(dict_base_point[G_BASE])
            NameFileBase = (k3.mpathexpand("<K3Files>") + '\Штампы\BaseZn.k3')

            if k3.fileexist(NameFileBase) > 0:
                bzn = k3.append(NameFileBase, -20, -20, 0, k3.k_done)
            k3.setucs(k3.k_previous)

        objects2 = k3.sysvar(60) - objects2
        k3.add(pnt, k3.k_last, objects2, k3.k_done)
        gabDraw = obj_k3_gab3(pnt)

        hDim, vDim, kDim = Dimension(), Dimension(), k3.Var()
        # Добавляем габаритные размеры по необходимости
        if dimchain.Type[2:] == ['continue', 'continue'] or (
                        dimchain.flagXmax == False and dimchain.flagXmin == False ):
            dims = hDim.create(Type='ldim', tP=[sGab[0], sGab[3], (sGab[0][0], gabDraw[1] - real_h_text, 0)])
            if len(dims) > 0:
                k3.add(pnt, dims, k3.k_done)
        if dimchain.Type[:2] == ['continue', 'continue'] or (
                        dimchain.flagYmax == False and dimchain.flagYmin == False ):
            dims = vDim.create(Type='ldim', tP=[sGab[0], sGab[1], (gabDraw[0] - real_h_text, sGab[0][1], 0)])
            if len(dims) > 0:
                k3.add(pnt, dims, k3.k_done)

        if Side == 'F':
            pnt = mirrorObject(obj_k3=pnt, Axis='Y')

    objects = k3.sysvar(60) - objects

    if objects > 0 and len(dopTxt) > 1:
        arr = obj_k3_gab3(pnt)

        pTxt = k3.text(dopTxt, k3.k_done, (arr[0], arr[4] + 100, arr[2]), k3.k_normal, (0, 0, 1),
                       (arr[0] + 100, arr[4] + 100, arr[2]))
        k3.add(pnt, pTxt, k3.k_done)
    k3.resnap()
    k3.attrobj(k3.k_attach, 'dsview', k3.k_done, pnt, 1)
    k3.visible(list_obj_visible, k3.k_done)
    list_obj_visible = []
    uo.freeElements()  # Освобождаем память от плоских объектов
    if objects > 0:
        return pnt, t_pk, listHolDraw, lRevisia
    else:
        return None, None, None, lRevisia

def real_len_list(lnkd):
    """
    Возвращает реальную длину списка списков отверстий lnkd
    """
    a_sum = 0
    len_sum_tuple = lambda l: len(l)-1
    for a in map(len_sum_tuple, lnkd): a_sum += a
    return a_sum


def getUserBP(list_base_point):
    global G_BASE
    if g_DrawBase == 1:
        ttp1, ttp2, ttp3, res = k3.Var(), k3.Var(), k3.Var(), k3.Var()
        k3.zoom(k3.k_all)
        try:
            k3.get(("Укажите курсором базовый угол ( Текущий базовый угол = " + str(G_BASE) + " или нажмите Esc )"),
                   k3.k_point, k3.k_missing, ttp1, ttp2, ttp3, k3.k_interact)
            #k3.macro(PROTOPATH.value+'DRWZIP.ZK3|getpoint.mac',  k3.k_byref, ttp1, k3.k_byref, ttp2, k3.k_byref, ttp3, k3.k_byref, res, k3.k_done)       # определяем базы"Укажите сторону базы"
            #if res.value > 0:
            pbUser = k3.Point(ttp1.value, ttp2.value, ttp3.value)
            bds = 999999999
            for ip in range(4):
                ds = k3.distance(list_base_point[ip], pbUser)
                if ds[0] < bds:
                    numb = ip
                    bds = ds[0]

            G_BASE = numb + 1
        except:
            pass


def listHole_centrPoint_revisia(kDOBJECT):
    '''Удаляет отверстия у которых центра совпадают из списка построения размерной цепи
     ((12, 1025, 'AF', 'X', 0.0), [<__main__.Drill instance at 0x1875FA58>, <__main__.Drill instance at 0x1875F2D8>], [<__main__.Drill instance at 0x1875FA58>, <__main__.Drill instance at 0x1875F2D8>])
'''
    temp_rev = []
    n_kDOBJECT = []
    for th in kDOBJECT:
        t_0 = th[0]
        t_1 = []
        for t in th[1]:
            res = (t.Xc, t.Yc)
            if res in temp_rev:
                pass
            else:
                temp_rev.append(res)
                t_1.append(t)
            if len(t_1) > 0:
                n_kDOBJECT.append((th[0], t_1, t_1))
    return n_kDOBJECT


def setSdvigDim(pnt, tGab, sdvigDim):
    '''уточняем габарит объекта pnt
     tGab - список старых координат
     sdvigDim - размер сдвига по сторонам'''
    nGab = obj_k3_gab3(pnt)
    sdvigDim[0] = sdvigDim[0] + nGab[3] - tGab[3]  #tXmax,tXmin,tYmax,tYmin
    sdvigDim[1] = sdvigDim[1] - nGab[0] - tGab[0]  #tXmax,tXmin,tYmax,tYmin
    sdvigDim[2] = sdvigDim[2] + nGab[4] - tGab[4]  #tXmax,tXmin,tYmax,tYmin
    sdvigDim[3] = sdvigDim[3] - nGab[1] - tGab[1]  #tXmax,tXmin,tYmax,tYmin
    return sdvigDim


def dimchain_listHoles(tlHoles, PathIn, Side, tcDOBJECT, sdvigDim, tGab, dimchain, Is_Drill_CentralLine,
                       lRevisia=[[], []]):
    '''Чертим отверстия по списку'''

    #draw_hole_in_tlholes(tlHoles, PathIn, Side, tcDOBJECT)

    tsGab, tXmax, tXmin, tYmax, tYmin, sdvigDim, lRevisia = dimchain.create(sdvigDim=sdvigDim, tGab=tGab,
                                                                            cDOBJECT=tcDOBJECT, lRevisia=lRevisia)
    if Is_Drill_CentralLine:
        k = drawing.dTx.items()
        for x in k:
            if len(x[1]) > 1:
                Central(x[0], min(x[1]), 0, x[0], max(x[1]), 0)
        k = drawing.dTy.items()
        for y in k:
            if len(y[1]) > 1:
                Central(min(y[1]), y[0], 0, max(y[1]), y[0], 0)
    return lRevisia


def draw_hole_in_tlholes(tlHoles, PathIn, Side, tcDOBJECT):
    for hole in tlHoles:
        if hole.DrawDim:
            if hole.Draw(Side=Side, PathIn=PathIn,  LAYERTODXF=LAYERTODXF, OBJ_DXF=OBJ_DXF):  # Чертим отверстия
                if (hole.Diameter, hole.Hohe, hole.Side) not in drawing.ListExceptionsPointsDrill:
                    tcDOBJECT.append(hole)  # добавляем отверстие  в список объектов чертежа


def note_Holes(noteName, D_H_in_Name, Side, tempObj):
    '''Обозначает отверстия на чертеже указателем'''

    def _getSpos(len_tlHoles, s_pos):
        if len_tlHoles == 1:
            s_pos = 0
        elif len_tlHoles == 2:
            s_pos = 0 if s_pos > 0 else -1
        else:
            s_pos = s_pos / -1 if s_pos > 0 else 1
        return s_pos

    s_pos = 0
    result = False
    objs_n = 0
    nObj = k3.sysvar(60)

    for lHoles in noteName:
        #ставим размеры (диаметры х глубины) отверстий
        tlHoles = lHoles[1]
        len_tlHoles = len(tlHoles)
        i_pos = 0  #random.randrange(len(tlHoles))
        #s_pos = _getSpos(len_tlHoles, s_pos)
        Mask = lHoles[0][2] in [Side, 'B', 'C', 'D', 'E', 'T']  #if D_H_in_Name else lHoles[0]
        if tlHoles[i_pos].DrawNote and ((Mask) or tlHoles[i_pos].Through):
            # обозначаем отверстие только если оно еще не подписано
            i_pos_key = False
            for Dci in [a * 0.01 for a in range(100, 500, 25)]:
                vAngStart = 45  # стартовое значение угла

                i_pos = int(len_tlHoles / 2.0) + s_pos
                isV = False
                rad = tlHoles[i_pos].Diameter / 2.0
                alias = tlHoles[i_pos].Alias
                while i_pos < len_tlHoles:
                    vAng = 1 * vAngStart
                    if i_pos_key:
                        k3.delete(obj, k3.k_done)
                    numQadrant = Ut.getNumQadrant(vAng)  # номер квадранта в котором лежит угол
                    sign_NoteX = 1 if numQadrant in [1, 4] else -1
                    #sign_NoteY = 1 if numQadrant in [1,2] else -1
                    note = init_note_hole(i_pos, tlHoles, rad, (sign_NoteX, 0, 0), vAng)
                    #if Side == 'F':
                        #note.flip = True
                    #else:
                        #note.flip = False
                    obj = note.draw()
                    vAngStart = min(note.dAngle)
                    vAng = vAngStart
                    while vAng < max(note.dAngle):
                        numQadrant = Ut.getNumQadrant(vAng)  # номер квадранта в котором лежит угол
                        sign_NoteX = 1 if numQadrant in [1, 4] else -1
                        sign_NoteY = 1 if numQadrant in [1, 2] else -1
                        ndVector = [(sign_NoteX, 0, 0), (0, sign_NoteY, 0)]
                        for dVector in note.dVector:
                            if dVector in ndVector:
                                k3.delete(obj, k3.k_done)
                                note = init_note_hole(i_pos, tlHoles, rad, dVector, vAng, kDelta=1.25 * Dci)
                                #if Side == 'F':
                                    #note.flip = True
                                    #pass
                                obj = note.draw()
                            i_pos_key = True
                            arr = Ut.GetRectText(obj)  # получаем прямоугольник текста
                            k3.invisible(k3.k_partly, obj, k3.k_done)
                            isV = Ut.IsVsblRect(nVport=k3.sysvar(51),
                                                Arr=arr)  # определяем есть ли в этом прямоугольнике видимые объекты
                            k3.visible(k3.k_partly, obj, k3.k_done)

                            if not isV:
                                break
                        if not isV:
                            break
                        vAng += 15  # наращиваем значение на ... градусов
                    if not isV:
                        break
                    i_pos += 1  # берем следующее из списка
                if not isV:
                    break

            for tH in tlHoles:
                tH.DrawNote = False  # изменяем статус подписанности отверстия
            objs_n += 1
            result = True
    return result, objs_n


def init_note_hole(i_pos, tlHoles, rad, rv2, vAng, kDelta=1.25):
    '''Создает указатель(полочку выноску) отверстия на чертеже'''

    sting1 = "%%c" + str(tlHoles[i_pos].Diameter) + (
        "" if tlHoles[i_pos].Through else "x" + str(tlHoles[i_pos].Hohe))  #+str(alias)
    sting2 = str(len(tlHoles)) + " отв."
    sting2 = iif(len(tlHoles) > 1, str(len(tlHoles)) + " отв.", '')
    note = Note(normal=(0, 0, 1), Text1=sting1, Text2=sting2,
                point1=(tlHoles[i_pos].Xc + 1 * rad * k3.cos(k3.radian(vAng)),
                        tlHoles[i_pos].Yc + 1 * rad * k3.sin(k3.radian(vAng)), 0),
                relativ1=(kDelta * real_h_text * k3.cos(k3.radian(vAng)),
                          kDelta * real_h_text * k3.sin(k3.radian(vAng)), 0),
                relativ2=rv2)
    if note.qPlace is None:
        note.qPlace, note.sPlace = note._getListPointPosition(2.6 * real_h_text, Panel.gabpoint)
    return note


#-----------------------------
def delElemsList(aa, Tolerans=0.1):
    aa.append(-999 * 1000000)
    rr = zip(aa[:-1], aa[1:])
    f = lambda a: a[0] if abs(a[0] - a[1]) > Tolerans else None
    aa = list(map(f, rr))
    aaa = []
    for a in aa:
        if a is not None:
            aaa.append(a)
    return aaa


#-----------
def tupleToPoint(tP):
    if None not in tP:
        try:
            pnt = k3.Point()
            pnt.set(tP[0], tP[1], tP[2])
            return pnt
        except:
            return None
    return None


#------------------------------
def moveDrawPos(vVid=None, delta=0, v_gab=[]):
    '''Размещает чертежный вид на свободном месте текущего вида'''

    k3.getsnap()
    #k3.setucs(k3.k_vcs)
    k3.setucs(k3.k_gcs)
    k3.view(0, 0, 1, k3.k_done)
    k3.setucs(k3.k_vcs)
    if len(v_gab) == 0:
        gabs = Ut.findgabscene([0, 0, 0, 0, 0, 0])
    else:
        gabs = v_gab
    k3.setucs(k3.k_move, gabs[3] + delta, 0, 0)
    pnt = k3.Var()
    if vVid is None:
        k3.objident(k3.k_last, 1, pnt)
        pnt = pnt.value
    else:
        pnt = vVid
    gab = obj_k3_gab3(pnt)
    k3.move(k3.k_nocopy, pnt, k3.k_done, k3.k_2points, (gab[0], gab[1], gab[2]), (0, 0, 0))
    k3.setucs(k3.k_vcs)
    gab = obj_k3_gab3(pnt)
    gabs[3] = gab[3]
    k3.resnap()
    return gabs


#-----------------------------
def obj_k3_gab3(obj_k3):
    """
    Измеряет габарит объекта obj_k3 или списка объектов obj_k3
    Возвращает список из 6-ти координат

    :param obj_k3: Единичный объект  или список объектов к3.
    :return: Cписок из 6-ти координат.
    """
    arr = k3.VarArray(6)
    gr = None
    if type(obj_k3) == list:
        if False not in [isinstance(a, k3.K3Obj) for a in obj_k3]:  # если в списке только объекты к3
            tmpLnObj = k3.line(0, 0, 0, 1, 0, 0)
            k3.delete(k3.k_wholly, tmpLnObj, k3.k_done)
            gr = k3.group(obj_k3)
            k3.objgab3(gr[0], arr)
            k3.explode(gr[0])
    elif type(obj_k3) == k3.Var:
        gr = obj_k3.value
        k3.objgab3(gr, arr)
    elif isinstance(obj_k3, k3.K3Obj):
        k3.objgab3(obj_k3, arr)
    return [round(a.value, 1) for a in arr]


#-----------------------------
def mirrorObject(obj_k3, Axis='X'):
    """
    Создает зеркальное отражение объекта.

    :param obj_k3: Ссылка на объект
    :param Axis:  Имя Оси X или Y. По умолчанию X
    """
    if type(obj_k3) == k3.Var:
        obj_k3 = obj_k3.value
    arr = obj_k3_gab3(obj_k3)

    objects2 = k3.sysvar(60)

    if Axis == 'X':
        k3.mirror(k3.k_nocopy, obj_k3, k3.k_done, k3.k_3points,
                  (arr[0], (arr[4] - arr[1]) / 2 + arr[1], arr[2]),
                  (arr[3], (arr[4] - arr[1]) / 2 + arr[1], arr[2]),
                  (arr[0], (arr[4] - arr[1]) / 2 + arr[1], arr[2] + 1))
    elif Axis == 'Y':
        k3.mirror(k3.k_nocopy, obj_k3, k3.k_done, k3.k_3points,
                  ((arr[3] - arr[0]) / 2 + arr[0], arr[1], arr[2]),
                  ((arr[3] - arr[0]) / 2 + arr[0], arr[4], arr[2]),
                  ((arr[3] - arr[0]) / 2 + arr[0], arr[4], arr[2] + 1))


        ##    elif Axis=='Z':
        ##        k3.mirror(k3.k_nocopy,obj_k3.value,k3.k_done,k3.k_3points,
        ##        ((arr[3]-arr[0])/2+arr[0],arr[1],arr[2]),
        ##            ((arr[3]-arr[0])/2+arr[0],arr[4],arr[2]),
        ##                ((arr[3]-arr[0])/2+arr[0],arr[4],arr[2]+1))
        #lobj = selectFltr("Note")
        #k3.explode(obj_k3,k3.k_done)
        #keyCh = False
        #for obj in lobj:
        #k3.editobject(obj,k3.k_flip,k3.k_done)
        #keyCh = True
    objects2 = k3.sysvar(60) - (objects2 - 1)
    if objects2 > 1:
        obj_k3 = k3.group(k3.k_last, objects2, k3.k_done)[0]

    return obj_k3


def selectFltr(stringfltr):
    lisObjSel = []
    try:
        rs = k3.fltrtype(stringfltr)
        if rs > 0:
            k3.select(k3.k_partly, k3.k_all)
        k3.fltrtype(0)

        if k3.sysvar(61) > 0:
            n = int(k3.sysvar(61))
            for i in range(n):
                lisObjSel.append(k3.getselnum(int(i + 1)))
    except:
        k3.fltrtype(0)
    return lisObjSel

 

#-----------------------------
def draw_Save(list_obj_k3):
    """
    Записывает чертеж в отдельный файл.

    :param list_obj_k3: Список объектов образующих чертеж
    """
    dp = drawproperty
    dp(Panel)
    g_draw = dp.g_draw
    numWmf = dp.numWmf
    if type(list_obj_k3) == list:
        i = 1
        for obj in list_obj_k3:
            k3.attrobj(k3.k_attach, 'IDRWN', k3.k_done, obj, i)
            i += 1
    else:
        k3.attrobj(k3.k_attach, 'IDRWN', k3.k_done, obj, 1)
    k3.group(list_obj_k3, k3.k_done)
    k3.objident(k3.k_last, 1, g_draw)
    k3.zoom(k3.k_byobject, g_draw.value, k3.k_done)
    if (k3.fileexist(numWmf)):
        NULLOUT = k3.removefile(numWmf)
    k3.exp2d(k3.k_wmf, k3.k_header, k3.k_yes, k3.k_mono, k3.k_yes, k3.k_inscribe, k3.k_no, k3.k_fit, k3.k_no,
             k3.k_height, 30000, k3.k_width, 32000, k3.k_continue, numWmf, k3.k_overwrite)

def getProjPath():
    """
    :return: Возвращает путь к текущему файлу проекта.
    """
    ProjPath = k3.getfilepath(k3.sysvar(2))
    return ProjPath

#-----------------------------

def DrawPanel(params=[], PathIn=1):
    """
    Создает чертеж  панели.

    :param params: список парметров передаваемых из макроса
             массив отверстий подготовленный функцией nels=getholes(pnt,"aHoles") 
             число отверстий
             указатель на панель
             переменная для передачи результата построения чертежа
    :param PathIn: вариант чертежа контуров с учетом кромки или без 1-с учетом кромки 0-без учета кромки
    """

    def _app_draw_in_page(index_page, result_find_draws, list_del, list_save, var=1):
        if var==1:
            cf_name_draw = drawproperty.numTxt + '_' + str(index_page) + '.k3'
            if cf_name_draw in drawproperty.list_files_numTxt:
                #print('''   Найден готовый документ! Будет обновлен только штамп.
#Если надо создать чертежи, удалите старые документы или измените вызов DrawingSupp.DrawPanel._app_draw_in_page. Вместо var=1 поставьте var=0  .''')
                pos = k3.udgetpos('Drawings')
                ps = k3.udgetpos('u99_IsRefreshDraws')
                
                if ps > 0:
                    vt, dv,  sv = k3.Var(), k3.Var(), k3.Var() 
                    ps = k3.udgetentity('u99_IsRefreshDraws', vt, dv, sv)
                    res_ud = True if dv.value > 0 else False
                else:
                    k3.udaddentity(pos,"Всегда создавать чертежи",'u99_IsRefreshDraws',3,1,0,100)
                    res_ud = True
                vDrawDial = k3.Var()
                k3.getvarinst(1, "vDrawDial", vDrawDial, 0)
                if not res_ud :
                    if vDrawDial.value < 3:
                        ok_flag = k3.alternative( "Найден готовый документ!",
                                       k3.k_msgbox, k3.k_picture, 2, k3.k_beep, 2, k3.k_text, k3.k_left,
                                       """Укажите вариант действий """,
                                       """Файл: """ + cf_name_draw, 
                                       k3.k_done,
                                       "Обновить только штамп", "Создать чертеж полностью", "Обновить штамп у всех", "Создать чертеж для всех", 
                                       k3.k_done)
                    
                        if ok_flag[0] > 2:
                            k3.setvarinst(1, "vDrawDial", ok_flag[0])
                            
                    else:
                        ok_flag = (vDrawDial.value - 2, )
                else:
                    ok_flag = (2, )
                    k3.setvarinst(2, "vDrawDial", ok_flag[0])
                

                if ok_flag[0] in [1.0, 3.0]:
                    result_find_draws[index_page-1] = True
                    n_objs = k3.sysvar(60)
                    k3.append(cf_name_draw, 0, 0, 0)
                    n_objs = int(k3.sysvar(60) - n_objs)
                    ls_o = []
                    for i_els in range(int(k3.sysvar(60))-n_objs+1, int(k3.sysvar(60)+1), 1):
                        p = k3.getobjnum(i_els)
                        if k3.getattr(p, 'IPRLNDW0', -99) > 0:
                            list_del.append(p)
                        else:
                            ls_o.append(p)
                    if len(ls_o) > 0:
                        p = k3.group(ls_o)
                        list_save.append(p[0])

    def _drwSide(sortHoles,
                 g_DrawPTyp,
                 TypeDC_forDrill,
                 lRevisia,
                 Is_Drill_CentralLine,
                 noteHoles,
                 DimPath,
                 params,
                 IsDrawBasePoint,
                 g_vidUnic,
                 listdrw,
                 drawing_page,
                 holes,
                 keyDXF,
                 IsNameSide,
                 nameView='',
                 currSide='A'
                 ):
        drawing_view = DrawingView()
        drawing_view.side = currSide
        pntemp, t_pk, listHolDraw, lRevisia = DrawingPanSide(params = params,
                                                             Side = drawing_view.side,
                                                             PathIn = g_DrawPTyp,
                                                             holes = sortHoles,
                                                             DimPath = DimPath,
                                                             nHoles = noteHoles,
                                                             TypeDC = TypeDC_forDrill,
                                                             D_H_in_Name = D_H_in_Name,
                                                             IsFlagPoints = IsFlagPoints,
                                                             Is_Drill_CentralLine = Is_Drill_CentralLine,
                                                             IsDrawBasePoint = IsDrawBasePoint,
                                                             lRevisia=lRevisia,
                                                             is_not_holesdimchain=True)
        drawing_view.handle = pntemp
        drawing_view.title = iif(IsNameSide, DrawTitle(StringTitle=(nameView)), None)
        if g_vidUnic:  # Каждый вид на своем листе
            l_drawing_page = DrawingPage()  # Создаем объект чертежный лист. На нем может располагаться несколько видов
            listdrw.append(l_drawing_page)  # Добавляем лист в список листов
            l_drawing_page.list_view.append(drawing_view)
        else:
            drawing_page.list_view.append(drawing_view)
        # DXF стороны
        dDXF = (nameView)
        if not bool(dDXF.count('Сторона')):
            dDXF = dDXF.replace('%%u', '_')
        else:
            dDXF = ''
        if keyDXF:
            drawing_view_dxf = DrawingView()
            drawing_view_dxf.side = currSide
            for hole in listHolDraw:
                hole.DrawDim = True
            pntemp, t_pk, listHolDraw, nullout = DrawingPanSide(params=params,
                                                                Side=drawing_view_dxf.side,
                                                                PathIn=0,
                                                                holes=holes,
                                                                DimPath=DimPath,
                                                                nHoles=noteHoles,
                                                                TypeDC=TypeDC_forDrill,
                                                                D_H_in_Name=False,
                                                                is_not_holesdimchain=False)
            expDXF(pntemp=pntemp, t_pk=OBJ_DXF.Counter, Side=drawing_view_dxf.side + dDXF, PathIn=0)
            for hole in listHolDraw:
                hole.DrawDim = True
            pntemp, t_pk, listHolDraw, nullout = DrawingPanSide(params=params,
                                                                Side=drawing_view.side,
                                                                PathIn=1,
                                                                holes=holes,
                                                                DimPath=DimPath,
                                                                nHoles=noteHoles,
                                                                TypeDC=TypeDC_forDrill,
                                                                D_H_in_Name=False,
                                                                is_not_holesdimchain=False)
            expDXF(pntemp=pntemp, t_pk=OBJ_DXF.Counter, Side=drawing_view_dxf.side + dDXF, PathIn=1)
            #keyDXF = False
        return lRevisia, keyDXF

    Panel.getPanelProperty(Params[2])
    InfoPoly = Panel.getPanelPathInfo()
    
    #-- Кусок определения для рамки габаритов заготовки с вычетом прифуговки
    Pl_SizeZag = k3.GlobalVar('Pl_SizeZag')
    E = k3.Var()
    D = k3.Var()
    C = k3.Var()
    B = k3.Var()
    E.value = 0
    D.value = 0
    C.value = 0
    B.value = 0
    cutLen = k3.Var()
    cutWdh = k3.Var()
    cutLen.value = 0
    cutWdh.value = 0
    for i, pp in enumerate(InfoPoly.paths):
        for el in pp.elems:
            # print(el.Band.__dict__)
            if    el.IdLine == 1:        # D
                D.value = el.Band.Thickness
            elif  el.IdLine == 3:        # C
                C.value = el.Band.Thickness
            elif  el.IdLine == 5:        # E
                E.value = el.Band.Thickness
            elif  el.IdLine == 7:        # B
                B.value = el.Band.Thickness
    # print(D.value, C.value, E.value, B.value)
    
    k3.macro(protopath+"\\ProjectsUtilites\\ARCut.py",k3.k_byref,E, k3.k_byref,D,
    k3.k_byref,C, k3.k_byref,B, k3.k_byref,cutLen, k3.k_byref,cutWdh)
    
    Pl_SizeZag.value = "{}x{}".format(
    int(int(round(k3.getattr(0, "ZgUnitX", (Panel.gabpoint[3] - Panel.gabpoint[0])), 0)) - cutLen.value),
    int(int(round(k3.getattr(0, "ZgUnitY", (Panel.gabpoint[4] - Panel.gabpoint[1])), 0)) - cutWdh.value)
    )
    #--------------------
    drawproperty(Panel)
    global Krav  # Если нужен стандартный вариант поставьте False
    global D_H_in_Name  # Размеры отверстий с учетом маски имени DxH
    global Rastr32  # Размеры с учетом растра 32
    #global Is_Drill_CentralLine #Чертить центральные линии отверстиям на одной оси X или Y
    global IsFlagPoints  # Исключать флаги из цепочки
    #global IsDrawBasePoint # Чертить базовую точку
    global keyDXF  #Создавать DXF
    global IsNameSide  # Подписывать выводимую сторону панели
    global UnionDrawPathAndDrill  # Объединять размерные точки контура и сверловки в один чертеж
    global g_upr
    g_upr = k3.GlobalVar('g_upr')
    if not Krav:
        g_chb, g_chc, g_chd, g_che = k3.GlobalVar('g_chb'), k3.GlobalVar('g_chc'), k3.GlobalVar('g_chd'), k3.GlobalVar(
            'g_che')
    else:
        g_chb, g_chc, g_chd, g_che = k3.Var(), k3.Var(), k3.Var(), k3.Var()
        g_chb.value, g_chc.value, g_chd.value, g_che.value = 0, 0, 0, 0
    g_vidUnic = transform_logical_k3_to_python(k3.GlobalVar(
        'g_vidUnic').value) if Panel.cover_count == 0 else True  # Каждый вид на своем листе если есть отделки , то всегда кажы на своем листе

    global G_BASE
    G_BASE = int(k3.GlobalVar('g_base').value)
    global g_DrawBase
    g_DrawBase = int(k3.GlobalVar('g_DrawBase').value)
    global g_basegr
    g_basegr = int(k3.GlobalVar('g_basegr').value)
    global g_dSide
    g_dSide = k3.GlobalVar('g_dSide').value

    IsDrawBasePoint = transform_logical_k3_to_python(k3.GlobalVar('g_bazeZn').value)  # Чертить базовую точку
    Is_Drill_CentralLine = transform_logical_k3_to_python(
        k3.GlobalVar('g_drwosy').value)  #Чертить центральные линии отверстиям на одной оси X или Y
    g_ch = lambda ch: 'base' if ch == 1 else 'continue'

    chb = g_ch(g_chb.value)
    chc = g_ch(g_chc.value)
    chd = g_ch(g_chd.value)
    che = g_ch(g_che.value)
    #---------------------

    TypeDC_forDrill = [chb, chc, chd, che]  # Тип размера на чертеже'continue','continue'
    TypeDC_forPath = ['base', 'base', 'base', 'base']  # Тип размера на чертеже полотна панели
    drawing.dimchain2base = iif(Krav, True, True)  # строить замкнутые размерные цепи
    drawing.DrawingBandType = 2  # Вариант с легендой
    # Добавить сюда, если нужно будет исключить
    # drawing.ListExceptionsPointsDrill = iif(Krav, [(15, 13, 'F'), (15, 13, 'A'), (4, 5, 'A'), (4, 5, 'F'), (4, 1.5, 'A'), (4, 1.5, 'F')],
        # [])  # список "имен" цепей , которые образмеривать не надо
    drawing.ListExceptionsPointsDrill = iif(Krav, [], [])  # список "имен" цепей , которые образмеривать не надо
    # drawing.ListNoNotePointsDrill =  iif(Krav, [(4, 5, 'A'), (4, 5, 'F'), (4, 1.5, 'A'), (4, 1.5, 'F')], []) # Список отверстий, которые обозначать не надо
    drawing.ListNoNotePointsDrill =  iif(Krav, [], []) # Список отверстий, которые обозначать не надо
    drawing.ListNoGroupCover = [ 334., ]
    g_DrawPTyp = k3.GlobalVar('g_DrawPTyp').value

    #-------------------

    k3.getsnap()
    aArrVi = k3.VarArray(3)
    k3.sysarr(54, aArrVi)
    listdrw = []
    pntemp = k3.Var()

    if k3.GlobalVar('g_lza').value > 0:  # Подбираем графический коэффициент (масштаб)
        grf = 5
        if max(Panel.plength, Panel.pwidth) < 201:
            grf = 1
        if max(Panel.plength, Panel.pwidth) < 501:
            grf = 3
        k3.grfcoeff(grf)
    #------------------------------------
    global tDim
    tDim = Dimension()
    tDim.defaultDimCreate()
    global real_h_text
    real_h_text = tDim.grcoef[1][2].value * tDim.SystemDimInfo['basedy']  #tDim.realhightext
    holes, sortHoles, noteHoles = [], [], {}
    if params[1].value > 0:
        holes = Panel.holes #drill_finder(params=Params)  # Находим все отверстия в панели
        sortHoles, noteHoles = drawing.findSortHols(holes, Axe=['X', 'Y'], Rastr32=Rastr32,
                                                    D_H_in_Name=True)  # сложный алгоритм сортировки отверстий по размерным цепям
        if not D_H_in_Name:
            sortHoles = holes
            
    if len(Panel.pSlots) > 0:  #если есть пропилы
        PlaneSlot = {'A': 1, 'F': 0}
        SideSlot = {'B': 7, 'C': 3, 'D': 1, 'E': 5, 'N': 9}
        for pS in Panel.pSlots:
            if pS.Plane == PlaneSlot['A']: counter.drill_A = True  #0-F 1-A
            if pS.Plane == PlaneSlot['F']: counter.drill_F = True  #0-F 1-A

    obj = k3.Var()

    if not UnionDrawPathAndDrill:
        if (len(holes) > 0 and Panel.rectangle_forma) or len(holes) == 0 :
            UnionDrawPathAndDrill = True
            
    if Panel.CurvePath == 1 and not UnionDrawPathAndDrill and len(holes) > 0:
        DimPath = 0
    else:
        DimPath = 1
    #***********************************************

    drawing_page = DrawingPage()  # Создаем объект чертежный лист. На нем может располагаться несколько видов
    listdrw.append(drawing_page)  # Добавляем лист в список листов
    lRevisia = [[], []]

    drawing.FrontF = isFront.isfront(Panel) # Является ли пласть F лицом
    # print('drawing.FrontF=',drawing.FrontF)
    #***********************************************
    ifSide = [False, False, 'F', 'A', 'F', '', '' ]
    # print('g_dSide=',g_dSide)
    if g_dSide == 'F':
        ifSide[0] = (counter.drill_A == True)
        ifSide[1] = ((counter.drill_F == True)
                     or ((counter.drill_F == False)
                         and (counter.drill_A == False))
                     )
        ifSide[2] = iif(counter.drill_A == True, 'A', 'F')
        ifSide[3] = 'A'
        ifSide[4] = 'F'
        ifSide[5] = iif(drawing.FrontF[0], 'Тыл', 'Лицо')
        ifSide[6] = iif(drawing.FrontF[0], 'Лицо', 'Тыл')
    else:
        ifSide[0] = (counter.drill_F == True)
        ifSide[1] = ((counter.drill_A == True)
                     or ((counter.drill_A == False)
                         and (counter.drill_F == False))
                     )
        ifSide[2] = iif(counter.drill_F == True, 'F', 'A')
        ifSide[3] = 'F'
        ifSide[4] = 'A'
        ifSide[5] = iif(drawing.FrontF[0], 'Лицо', 'Тыл')
        ifSide[6] = iif(drawing.FrontF[0], 'Тыл', 'Лицо')
    
    list_save = []
    list_del = []
    index_page = 0
    result_find_draws = [False, False, False]
    #***********************************************
    # Чертеж первой стороны A
    if ifSide[0]:
        index_page += 1
        _app_draw_in_page(index_page, result_find_draws, list_del, list_save)
        if not result_find_draws[index_page-1]:
            lRevisia, keyDXFA = _drwSide(sortHoles,
                                         g_DrawPTyp,
                                         TypeDC_forDrill,
                                         lRevisia,
                                         Is_Drill_CentralLine,
                                         noteHoles,
                                         DimPath,
                                         params,
                                         IsDrawBasePoint,
                                         g_vidUnic,
                                         listdrw,
                                         drawing_page,
                                         holes,
                                         keyDXF,
                                         IsNameSide,
                                         nameView='%%uСторона ' + ifSide[5], currSide=ifSide[3])

    #***********************************************
    # Чертеж второй стороны  F
    if ifSide[1]:
        index_page += 1
        _app_draw_in_page(index_page, result_find_draws, list_del, list_save)
        if not result_find_draws[index_page-1]:
            lRevisia, keyDXFF = _drwSide(sortHoles,
                                         g_DrawPTyp,
                                         TypeDC_forDrill,
                                         lRevisia,
                                         Is_Drill_CentralLine,
                                         noteHoles,
                                         DimPath,
                                         params,
                                         IsDrawBasePoint,
                                         g_vidUnic,
                                         listdrw,
                                         drawing_page,
                                         holes,
                                         keyDXF,
                                         IsNameSide,
                                         nameView='%%uСторона ' + ifSide[6], currSide=ifSide[4])

    #***********************************************
    # Чертеж полотна панели
    if Panel.CurvePath == 1 and not UnionDrawPathAndDrill:
        index_page += 1
        _app_draw_in_page(index_page, result_find_draws, list_del, list_save)
        if not result_find_draws[index_page-1]:
            tlRevisia, keyDXF = _drwSide([],
                                     0,
                                     TypeDC_forPath,
                                     [[], []],
                                     False,
                                     {},
                                     1,
                                     params,
                                     IsDrawBasePoint,
                                     True,
                                     listdrw,
                                     drawing_page,
                                     [],
                                     keyDXF,
                                     True,
                                     nameView='%%uПолотно панели ',
                                     currSide=ifSide[2])
    if not (True in result_find_draws):
        a_vgabs = k3.VarArray(6)
        if k3.findarrinst(1, "v_gabs") < 1:
            k3.setarrinst(1, "v_gabs", a_vgabs)
        else:
            k3.getarrinst(1, "v_gabs", a_vgabs)
        v_gabs = [a.value for a in a_vgabs]
        for pg in listdrw:
            # pg имеет тип DrawingPage который имеет список видов
            v_gabs = pg.draw(gab_3=v_gabs)  # Чертим лист
            for i, a in enumerate(a_vgabs):
                a_vgabs[i].value = v_gabs[i]
            k3.setarrinst(1, "v_gabs", a_vgabs)
            if pg.handle is not None and drawproperty.g_legenda:
                legenda.draw()  # Пишем легенду
                legenda.clue(pg.handle)  # Стыкуем легенду
                legendside[pg.list_view[0].side].draw()
                legendside[pg.list_view[0].side].clue(pg.handle)
                list_save.append(pg.handle)  # Добавляем в список сохраняемых объектов
    draw_Save(list_save)
    k3.view(k3.k_cartesian, k3.k_none, k3.k_gcs, aArrVi[0].value, aArrVi[1].value, aArrVi[2].value)
    Pl_SizeDet = k3.GlobalVar('Pl_SizeDet')
    Pl_SizeDet.value = str(
        int(round(k3.getattr(0, "ZgUnitX", (Panel.gabpoint[3] - Panel.gabpoint[0])), 0))) + 'x' + str(
        int(round(k3.getattr(0, "ZgUnitY", (Panel.gabpoint[4] - Panel.gabpoint[1])), 0)))
    
    if len(list_del) > 0:
        k3.delete(list_del)
    k3.resnap()


def addListObjInvisible(list_obj_visible):
    '''Гасит все видимые объекты сцены и добавляет их list_obj_visible'''
    list_obj_visible_t = Ut.getListObjVisual()
    if len(list_obj_visible_t) > 0:
        list_obj_visible.extend(list_obj_visible_t)
        k3.invisible(list_obj_visible_t, k3.k_done)
    return list_obj_visible


def rotateDrawObj(hObj, Ang=90):
    '''Поворачивает hObj на 90 если длинная сторона расположена по X, а gVertDraw ==1'''
    gab = obj_k3_gab3(hObj)
    gab_X = gab[3] - gab[0]
    gab_Y = gab[4] - gab[1]
    gVertDraw = k3.GlobalVar('gVertDraw').value  # 1 чертеж дб вертикальным 0 горизонтальным
    if (gVertDraw == 1 and gab_Y < gab_X) or (gVertDraw == 0 and gab_Y > gab_X):
        k3.rotate(k3.k_nocopy, hObj, k3.k_done, k3.k_2points, gab[0] + gab_X / 2, gab[1] + gab_Y / 2, 0,
                  gab[0] + gab_X / 2, gab[1] + gab_Y / 2, 10, Ang)


def expDXF(pntemp=[], t_pk=[], Side='A', PathIn=1,  Panel=Panel, title=None):

    def _remove_dxf(fld_dop, Panel, title, PathIn, Side):
        f_name = k3.sysvar(2)
        f_path = k3.getfilepath(f_name) + 'DXF' + fld_dop + '\\'
        if k3.folderexist(f_path) == 0:
            k3.createfolder(f_path)
        Panel.CommonPos = int(Panel.CommonPos) if (Panel.CommonPos - int(Panel.CommonPos)) < 0.01 else  Panel.CommonPos
        if title is None:
            title = str(STDARTICUL) + str(Panel.CommonPos) + '_' + Side + str(PathIn)
        fullName = f_path + title + '.dxf'
        if k3.fileexist(fullName) == 1:
            k3.removefile(fullName)
        return fullName

    ht_pk = []
    fld_dop = '' if PathIn == 0 else 'KR'
    for pp in t_pk:
        if isinstance(pp, k3.K3Obj):
            ht_pk.append(pp)
        elif isinstance(pp.value, k3.K3Obj):
            ht_pk.append(pp.value)
    fullName = _remove_dxf(fld_dop, Panel, title, PathIn, Side)
    if len(ht_pk) > 0:
        tGab = obj_k3_gab3(pntemp)
        l1 = k3.line(tGab[0], tGab[1], tGab[2], tGab[0]+1, tGab[1], tGab[2])
        k3.add(pntemp, l1, k3.k_done)
        k3.extract(pntemp, ht_pk, k3.k_done)
        
        tGab = obj_k3_gab3(ht_pk)
        k3.move(k3.k_nocopy, ht_pk, k3.k_done, (-1 * tGab[0], -1 * tGab[1], -1 * tGab[2]))
        k3.chprop(k3.k_lwidth, ht_pk, k3.k_done, 0)
        k3.exp3d(k3.k_dxf, k3.k_flat, k3.k_yes, k3.k_select, k3.k_done, fullName, ht_pk, k3.k_done)
        k3.add(pntemp, ht_pk, k3.k_done)
        k3.delete(k3.k_partly, l1)


# запуск построителя графа gprof2dot -f pstats startDrawPanel.prof | dot -Tpng -o startDrawPanel71.png
#@profile
def startDrawPanel():

    def getispath():
        """True если число контуров результирующего полилайна больше 1 """
        isnpaths = False
        try:
            isnpaths = Panel.dict_pathinfo[(0, False)].n_paths>1
        except:
            pass
        return isnpaths

    global Panel
    global Params
    global KROMZNAK
    Params = k3.getpar()
    #KROMZNAK = creator_kromznak()
    koefAproc = k3.sysvar(74)
    k3.approximation(k3.k_c_approximation, 0.2)
    DrawPanel(params=Params)
    isnpaths = getispath()
    result = (Panel.iscuts, isnpaths,
              Panel.rectangle_forma,
              max(len(Panel.slots), len(Panel.pSlots)),
              'holes' in Panel.__dict__.keys())
    if result == (False, False,
                  True,
                  0,
                  False):
        Params[3].value = 0
        print(
    '''--------------------------------------------------------------------------------------------------
    Панель прямоугольная, нет обработок, нет присадки - значит, чертеж выводить нет смысла.
    Это просто прямоугольник и два размера.
    В целях сохранения: ресурсов бумаги, лесных массивов и картриджа принтера. Такие чертежи - не выводим!
    ----------------------------------------------------------------------------------------------------''')
    else:
        Params[3].value = 1
    del(Panel)
    k3.approximation(k3.k_c_approximation, koefAproc)


if __name__ == '__main__':
    start_time=time.time()
    startDrawPanel()
    end_time=time.time()-start_time
    print('Чертеж создан за: ' if Params[3].value>0 else 'Анализ панели выполнен за: ', str(datetime.timedelta(seconds = end_time)), ' сек.')    






