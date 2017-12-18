# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        mPanel
# Purpose:     Панель
#
# Author:      Aleksandr Dragunkin
#
# Created:     31.10.2012
# изменения для версии 7.3 поддержка Python3
# Copyright:   (c) GEOS 2012-13
# Licence:     FREE
#-------------------------------------------------------------------------------
#import wingdbstub
import mButts as mBu
import mBand as mB
import mfix  as mF
import mSlot as mS
import k3
import gUtilitesK3 as gU
import Utilites_K3 as UK
import mMatrix
import hashlib
from functools import reduce
from drill_sp import Drill_SP
import BitMask as bm


#-----------------------------


#-------------------------------------------------------------------------------
class PolyInfo:
    '''Класс информации по результирующему полилайну'''

    def __init__(self):
        self.n_paths = None
        self.paths = []
        self.PathIn = 0 #  - вариант чертежа контуров с учетом кромки или без 0-с учетом кромки 1-без учета кромки
        self.FlagYmin = [8.]
        self.FlagYmax = [8.]
        self.FlagXmin = [8.]
        self.FlagXmax = [8.]
    #----------------------------------------------------------------------
    def __hash__(self, numpath=None):
        m = hashlib.new('md5')
        dhj = str(self.get_lrs(numpath))
        m.update(bytes(dhj.encode()))
        hhh = m.hexdigest()
        
        return hhh
    
    def get_lrs(self, numpath):
        return sorted(self.getPointForDrawing(numpath))

    def __cmp__(self,other):
        return cmp(self.get_lrs(), other.get_lrs())
    
    def __eq__(self,other):
        return self.get_lrs() == other.get_lrs()
    
    def __gt__(self, other):
        return self.get_lrs() > other.get_lrs()
    
    def __lt__(self, other):
        return self.get_lrs() < other.get_lrs()

    def getPointForDrawing(self, numpath=None):
        '''Возвращает координату точки для размерной цепи'''

        def _put_path_in_list(path, lPoints):
            for element in path.elems:
                typeElem = element.TypeElem
                geoInfo = element.GeoInfo
                if typeElem==1: # Линия
                    lPoints.extend([(geoInfo[0],geoInfo[1],0),(geoInfo[3],geoInfo[4],0)])
                elif typeElem == 2: # Дуга
                    lPoints.extend([(geoInfo[0],geoInfo[1],0),(geoInfo[6],geoInfo[7],0)])

        lPoints =[]
        tPoints = {}
        if numpath is None:
            for path in self.paths:
                _put_path_in_list(path, lPoints)
        elif isinstance(numpath, (int, float)):
            _put_path_in_list(self.paths[int(numpath)], lPoints)
        elif isinstance(numpath, (tuple, list)):
            for i in numpath:
                _put_path_in_list(self.paths[int(i)], lPoints)
        return lPoints
    
class PathInfo:
    '''Класс информации по контуру'''

    def __init__(self):
        self.index = None
        self.n_elems = None
        self.elems = []
        self.gabs = []
        self.depth   = None # глубина (для глухих вырезов )
        self.cutSide = None # сторона положения (для глухих вырезов )
        self.holder = None
           
            
    def _getOneLineInPath(self, t):
        # определяем число объектов в контуре
        newT = []
        nObjInPath = k3.getcntobjg(t)
        # если объект один и это линия
        if nObjInPath == 1.0:
            arr = k3.VarArray(1)
            err = k3.getarrobjg(t, arr)
            typeObjK3 = k3.getobjtype(arr[0].value)
            if typeObjK3 == 2.0:  # отрезок
                arrGeo = k3.VarArray(6)
                n = k3.getobjgeo(arr[0].value, arrGeo)
                newT = UK.ptransGcsToPsc([a.value for a in arrGeo])
        return newT

    def draw(self):
        result = k3.Var()
        ainf = k3.VarArray(5)
        if len(self.elems) > 0:
            l_elems = []
            for elem in self.elems:
                p = elem.draw()
                l_elems.append(p)
            # Если список элеменов больше 0
            if len(l_elems) > 0:
                # Создаем контур
                t = k3.path(k3.k_select, l_elems, k3.k_done, l_elems[0])
                rt = k3.contstatus(t[0], ainf)
                # Если 1 контур  замкнутый;  0 контур  не  замкнутый;
                if ainf[1].value > 0:
                    # Создаем плоскую область
                    t1 = k3.pline(k3.k_path, t[0], k3.k_done) #k3.k_pdomain, 
                else:
                    try:
                        # Определяем список объектов в контуре
                        newT = self._getOneLineInPath(t[0])
                        if len(newT) > 0:
                            # Создаем полилинию и Исправляем нормаль. Это надо что бы получались правильные DXF
                            t1 = k3.pline(k3.k_normal, 0, 0, 1, newT)
                        else:
                            # Создаем полилинию
                            t1 = k3.pline( k3.k_path, t[0], k3.k_done)
                    except:
                        result.value = t[0]
                        return result
                k3.delete(t[0], k3.k_done)
                self.holder = t1[0]
                result.value = t1[0]
        return result

class ElemsInfo(object):
    '''Класс информации по элементу контура'''

    def __init__(self):
        self.IdPoly = None
        self.IdLine = None
        self.TypeElem = None
        self.GeoInfo = []
        self.length = None
        self.ArcInfo = None
        self.GeoInfoGCS = []
        self.Band = BandInfoElems()
        self.Fixs = FixInfoElems()
        
    #----------------------------------------------------------------------
    def __hash__(self):
        m = hashlib.new('md5')
        dhj = str(self.get_lrs())
        m.update(bytes(dhj.encode()))
        hhh = m.hexdigest()
        return hhh
    
    def get_lrs(self):
        return [self.GeoInfo, self.Band]        

    def __cmp__(self,other):
        return cmp(self.get_lrs(), other.get_lrs())
    
    def __eq__(self,other):
        return self.get_lrs() == other.get_lrs()
    
    def __gt__(self, other):
        return self.get_lrs() > other.get_lrs()
    
    def __lt__(self, other):
        return self.get_lrs() < other.get_lrs()
    
    def __setattr__(self, name, value):
        super(ElemsInfo, self).__setattr__(name, value)
        if name == 'GeoInfo':
            super(ElemsInfo, self).__setattr__('GeoInfoGCS', self._setGeoInfoGCS())
            super(ElemsInfo, self).__setattr__('length', self.getlength())

    def _setGeoInfoGCS(self):
        if len(self.GeoInfo) in [6, 9]:
            list_tl = self.GeoInfo if self.TypeElem == 2 else self.GeoInfo[:6]
            result = UK.ptransPcsToGsc(list_tl)
        else:
            result = []
        return result

    def getGeoInfoPCS(self):
        '''Возвращает информацию в виде списка координат в текущей системе координат'''
        if len(self.GeoInfo) in [6, 9]:
            list_tl = self.GeoInfo if self.TypeElem == 2 else self.GeoInfo[:6]
            result = UK.ptransGcsToPsc(list_tl)
        else:
            result = []
        return result

    def draw(self):
        result =  None
        if self.TypeElem  is not None:
            if self.TypeElem == 1:
                t = k3.line(self.GeoInfo[:6], k3.k_done)
            elif self.TypeElem == 2:
                t = k3.arc(self.GeoInfo[:3],self.GeoInfo[6:] , self.GeoInfo[3:6], k3.k_done)
            result = t[0]
        return result
    #----------------------------------------------------------------------
    def getlength(self):
        """"""
        if self.TypeElem == 1:
            return k3.distance(self.GeoInfo[:6])[0]
        elif self.TypeElem == 2:
            return self.length

class BandInfoElems:
    '''информация по кромке на элементе контура'''

    def __init__(self):
        self.Material = None
        self.Thickness = None
        self.Color = None
        self.BMask = None
        self.Length = None
        self.Width = None
        self.znak = 0
        self.znakduble = 0
        self.znakindex = 0

class FixInfo:
    '''информация по крепеже на линии'''

    def __init__(self):
        self.Type = None # типа  крепежа из таблицы крепежа
        self.NumLine = None # Номер линии крепежа на элементе контура
        self.SgvigLine = None #Сдвиг линии крепежа от начала элемента контура
        self.Orders = None  # Номер правила установки крепежа
        self.BMask = None #
        self.Length = None #  Длина линии крепежа.  Если  значение  равно  нулю,крепеж ставится на весь элемент контура
        
class FixInfoElems:
    '''информация по крепеже на элементе контура'''

    def __init__(self):   
        self.count=None
        self.fixinfo=[]
#-------------------------------------------------------------------------------
class Singleton:
    """
    http://www.mindviewinc.com/Books/Python3Patterns/Index.php
    """
    def __init__(self, klass):
        self.klass = klass
        self.instance = None
    def __call__(self, *args, **kwds):
        if self.instance == None:
            self.instance = self.klass(*args, **kwds)
        return self.instance
    
    

class PanelRectangle(mMatrix.Matrix, Drill_SP):
    '''
    Класс для работы с прямоугольной мебельной панелью К3
    '''

    def __init__(self, material=0, length=2000, width=600, TypePan=12, holder=None):
        self.iscuts = True
        self.material = material
        self.panelThickness = k3.priceinfo(self.material,'Thickness',16,1)
        self.length = length
        self.width = width
        self.typepan = TypePan
        self.slots = []
        self.pSlots = []
        self.bands = []
        self.fixs =  []
        self.butts = []
        self.paths = []
        self.cover_count = 0 #Число отделок панели
        self.cover_info = {}# Информация по отделкам
        self.pandir = -1.
        self.__setFixDef()
        self.__setBandDef()
        self.mix = [] # Массинерционные характеристики
        self.amass_locale = [] # Центр масс в ЛСК 
        self.amass_locale_ph = [] # Центр масс результирующего полилайна с учетом поворота текстуры и габарита результирующего полилайна
        self.ucsDir = "P_UCSDIR"
        self.ucsDirR = "PR_UCSDIR"
        self.matr = self._array(16)
        self.Ohcunit()
        self.is_matr = True
        self.rectangle_forma = None # Характеристика внешнего контура прямоугольный ДА/Нет
        self.dict_pathinfo = {} # Информация по результирующему полилайну
        self.mask = 0
        self.e_hashcode = None
        self.holder = holder
        self.cutsconturs = []
        if self.holder is not None:
            self.getPanelProperty()
            self.getPanelPathInfo()
            self.getPanelPathInfo(PathIn=1)

    def __getstate__(self):
        """Return state values to be pickled.
        Возвращает значение состояния для консервации (pickled)."""
        return(self.material,self.length,self.width,self.typepan,
        self.slots,self.bands,self.fixs)

    def __setstate__(self,state):
        """Restore state from the unpickled state values.
        Восстаналивает консервированные значения."""
        # далее пишем перечень атрибутов в скобках или все в одну строку
        (self.material,self.length,self.width,self.typepan,
        self.slots,self.bands,self.fixs) = state
    #----------------------------------------------------------------------
    def get_lrs_holes(self, sides=['A', 'B', 'C', 'D', 'E', 'F', 'X']):
        """"""
        if 'holes' in self.__dict__.keys():
            hls = []
            for d in self.holes:
                if d.Side in sides:
                    hls.append(d)
            return [a.__hash__() for a in sorted(hls)]
        else:
            return None
                   
    #----------------------------------------------------------------------
    def get_lrs(self):
        """
            * Габариты заготовки 1
            * Толщина панели 2
            * Материал панели 3
            * Форма внешнего контура заготовки 4
            * Основное расположение панели (полка, стойка, стенка) 5
            * Форма внешнего контура заготовки 6
            * Форма гнутья панели 7
            * Пропилы 8
            * Торцевые пазы 9
            * Линии крепежа 10
            * Отделки 11
            * К3-файл с заготовкой панели 12
            * Реальные вырезы 13
            * Линии маркировки 14
            * Кромки прямолинейные 15
            * Кромки криволинейные 16
            * Фрезеровки 17
            * Отверстия торцев 18
            * Отверстия пласти 19
            * Отверстия под углом 20
            * Группа материала кромки 21
            * Материал кромки 22
            * Толщина кромки 23
            * Группа материала отделки 24
            * Материал отделки 25
            * Толщина отделки 26
            * Группа материала панели 27
        """
        bitmask=bm.mb_bitmask()
        bitmask.ud_get()        
        self.mask = bitmask.mask
        kmask = bm.k3bitmask()
        lrs = []
        def _addlrs(lrs, i, vr):
            if kmask.nbittest(self.mask, i) == 1:
                if isinstance(vr, list):
                    lrs.append(vr)
                else:
                    lrs.append(vr)
            else:
                lrs.append(None)
            return lrs
        lrs = _addlrs(lrs, 1, [round(self.plength, 1), round(self.pwidth, 1)]) # Габариты заготовки 1
        lrs = _addlrs(lrs, 2, k3.priceinfo(self.materialPanel,'Thickness',self.panelThickness,1)) # Толщина панели 2
        lrs = _addlrs(lrs, 3, self.materialPanel) # Материал панели 3
        lrs = _addlrs(lrs, 4, self.forma) # Форма внешнего контура заготовки 4
        lrs = _addlrs(lrs, 5, self.pTypePan) # Основное расположение панели (полка, стойка, стенка) 5
        lrs = _addlrs(lrs, 6, self.dict_pathinfo[(0, False)].__hash__(0)) # Форма внешнего контура заготовки 6
        lrs = _addlrs(lrs, 7, None) # Форма гнутья панели 7
        lrs = _addlrs(lrs, 8, None) # Пропилы 8
        lrs = _addlrs(lrs, 9, None) # Торцевые пазы 9
        lrs = _addlrs(lrs, 10, None) # Линии крепежа 10
        lrs = _addlrs(lrs, 11, None) # Отделки 11
        lrs = _addlrs(lrs, 12, None) # К3-файл с заготовкой панели 12
        lrs = _addlrs(lrs, 13, [self.dict_pathinfo[(0, False)].__hash__(list(range(1, self.dict_pathinfo[(0, False)].n_paths))), self.dict_pathinfo[(0, True)].__hash__()]) # Реальные вырезы 13 включая сквозные и глухие
        lrs = _addlrs(lrs, 14, None) # Линии маркировки 14
        lrs = _addlrs(lrs, 15, None) # Кромки прямолинейные 15
        lrs = _addlrs(lrs, 16, None) # Кромки криволинейные 16
        lrs = _addlrs(lrs, 17, None) # Фрезеровки 17
        lrs = _addlrs(lrs, 18, self.get_lrs_holes(sides=['B', 'C', 'D', 'E'])) # Отверстия торцев 18sides=['A', 'B', 'C', 'D', 'E', 'F', 'X']
        lrs = _addlrs(lrs, 19, self.get_lrs_holes(sides=['A', 'F'])) # Отверстия пласти 19
        lrs = _addlrs(lrs, 20, self.get_lrs_holes(sides=['X'])) # Отверстия под углом 20
        lrs = _addlrs(lrs, 21, None) # Группа материала кромки 21
        lrs = _addlrs(lrs, 22, None) # Материал кромки 22
        lrs = _addlrs(lrs, 23, None) # Толщина кромки 23
        lrs = _addlrs(lrs, 24, None) # Группа материала отделки 24
        lrs = _addlrs(lrs, 25, None) # Материал отделки 25
        lrs = _addlrs(lrs, 26, None) # Толщина отделки 26
        lrs = _addlrs(lrs, 27, None) # Группа материала панели 27        
        return lrs

    #----------------------------------------------------------------------    
    def __hash__(self):
        m = hashlib.new('md5')
        dhj = str(self.get_lrs())
        m.update(bytes(dhj.encode()))
        hhh = m.hexdigest()
        return hhh

    def __cmp__(self,other):
        return cmp(self.get_lrs(), other.get_lrs())
    
    def __eq__(self,other):
        return self.get_lrs() == other.get_lrs()
    
    def __gt__(self, other):
        return self.get_lrs() > other.get_lrs()
    
    def __lt__(self, other):
        return self.get_lrs() < other.get_lrs()
#-------------------------------------------------------------------------------
    def make(self, x=0, y=0, z=0):
        '''Создает прямоугольную панель'''
        nullout=k3.setvarinst(1,"PanMater",  self.material) # назначаем материал
        nullout=k3.setarrinst(1,"g_BandPan", self.__setBand()) # назначаем кромки

        nullout=k3.setarrinst(1,"g_fixmask", self.__setFixMask(self)) # назначаем маски на крепеж
        nullout=k3.setarrinst(1,"FixtPan",   self.__setFix()) # назначаем крепеж
        self.addSlotsInPanel()                             # делаем пропилы
        self.addButtsInPanel()                             # торцевые обработки
        s=k3.mbmakepan(k3.k_rectangle, x, y, z, self.typepan, self.length, self.width)
        self.holder=s[0]
        return self.holder

#-------------------------------------------------------------------------------
    def getKontursID(self, Panel=None, TypeCuts = 1):
        '''
            Возвращает число врезок(вырезов, наростов, линий маркирвки) в панель.
            Panel - <k3.Var()> указатель на панель
            TypeCuts = 1
            o 1 - вырез;
            o 8 - нарост;
            o 0 - линия маркировки;
        '''
        tValueTypeCuts = [0,1,8]
        if TypeCuts not in tValueTypeCuts:
            raise BaseException('\nОшибка вызова функции. Значение аргумента за пределами допустимых значений ' + str(
                tValueTypeCuts) + ' задано ' + str(TypeCuts))
        if Panel is None:
            Panel = self.holder        
        aPan = self.panelInit(Panel) # -- Инициализируем панель
        NULLOUT=k3.initarray(aPan, 0) # работает для версий 7,1 от 7,11,2012
        nCutsInPan = k3.getpan6par(7, aPan)
        aPanD = k3.VarArray(int(nCutsInPan)+1)
        nCutsInPan = k3.getpan6par(7, aPanD)
        self.cutsconturs = []
        for i in range(1,int(nCutsInPan)+1):
            aPan[0].value = aPanD[i].value
            NULLOUT = k3.getpan6par(7,aPan)
            if int(aPan[1].value) == TypeCuts:
                self.cutsconturs.append(aPan[i])
        return len(self.cutsconturs)

#-------------------------------------------------------------------------------

    def panelInit(self,Panel=None):
        '''
            Инициализирует панель. Возвращает aPan <k3.VarArray(10)>
        '''

        def panel_typ_analise(Panel):
            if isinstance(Panel, k3.K3Obj): 
                panel=Panel
            else:
                panel = Panel.value
            return panel

        if Panel==None:
            Panel=self.holder
        else:
            self.holder = panel_typ_analise(Panel)
        aPan = k3.VarArray(300)
        NULLOUT=k3.initarray(aPan,0) # работает для версий 7,1 от 7,11,2012
        #-- Проверяем, не панель ли это?
        panel = self.holder
            
        ft=k3.getattr(panel,"FurnType","")

        if (k3.left(ft,2)!="01") : #-- Это не панель
            print(( k3.left(ft,2),'Это не панель!'))
            return False
        else:
            #print 'Это панель'
            pass
        self.udMaskBandDef() #-- читаем маску кромки в пользовательских умолчаниях
        #-- Инициализируем панель
        aPan[0]=panel
        NULLOUT= k3.getpan6par(1,aPan)
        return aPan
    #----------------------------------------------------------------------
    def set_polotno(self):
        """Определяет свойство polotno, соответствующее полотну панели"""
        arr = k3.VarArray(int(k3.getcntobjga(self.holder)))
        k3.scang(self.holder, arr)
        for a in arr:
            try:
                if a.value.get_attr('FurnType') == '010000':
                    self.polotno = a.value
                    break
            except:
                pass
    #----------------------------------------------------------------------
    def set_holes(self):
        """Заполняет свойство holes"""
        n_drill = int(k3.getholes(self.polotno))
        n = k3.Var()
        n.value = n_drill
        if n_drill > 0:
            a_drill = k3.VarArray(n_drill* 15, 'a_drill')
            k3.getholes(self.polotno, 'a_drill')
            self.drill_finder([a_drill, n], self)
            
    #-------------------------------------------------------------------------------
    def getmix(self):
        """Определение масс-инерционных характеристик панели
        """

        def _invisible(isvis, self):
            if isvis == 0:
                k3.invisible(self.holder)
        #---------------------------------
        isvis = 1
        try:
            isvis = k3.getobjvisual(self.holder)
            if isvis == 0:
                k3.visible(self.holder)
            self.mix = k3.mix(k3.k_nodc, self.holder)
            amass_locale = UK.ptransGcsToPsc(list(self.mix[-3:]))
            _invisible(isvis, self)
            return amass_locale
        except:
            _invisible(isvis, self)
            return None
    #----------------------------------------------------------------------    
    def getPanelPathInfo(self,
                         Panel=None,
                         PathIn=0,
                         IsCuts=False):
        '''Собирает и возвращает информацию по результирующему полилайну панели
        PathIn - вариант  с учетом кромки или без 1-с учетом кромки 0-без учета кромки
        IsCuts - True/False вырезы / результирующий полилайн'''
        #-------------------------------------------------------------------------------
        def _resultPoly(aPan, vGetPan, poly, IsCuts, self):
            #print '--------------------------------------'
            #print '_resultPoly  vGetPan=', vGetPan
            # Определяем число контуров в результирующем полилайне
            aPan[0].value=0
            NULLOUT=k3.getpan6par(vGetPan,aPan)
            poly.n_paths = int(aPan[1].value) # число контуров

            for i in range(poly.n_paths):
                aPan[0].value=i+1
                aPan[1].value=0
                NULLOUT=k3.getpan6par(vGetPan,aPan)
                n_elements=aPan[2].value
                path = PathInfo()
                path.n_elems = int(n_elements)

                path.index = i+1
                poly.paths.append(path)

                for j in range(int(n_elements)):
                    aPan[0].value=i+1
                    aPan[1].value=j+1
                    NULLOUT=k3.getpan6par(vGetPan,aPan)
                    element = ElemsInfo()
                    element.IdPoly = int(aPan[2].value)
                    element.IdLine = int(aPan[3].value)
                    element.TypeElem = int(aPan[4].value)
                    # - c 2015-02-20-------------
                    baseGeoinfo= [aPan[i_p].value for i_p in range(5, 14)]
                    try:
                        if self.dirNotOrto:
                            ls = self.matrGeoInfo(baseGeoinfo)
                            element.GeoInfo = ls
                        else:
                            element.GeoInfo = baseGeoinfo
                    except:
                        element.GeoInfo = baseGeoinfo
                    #element.GeoInfo = [aPan[i_p].value for i_p in range(5, 14)] # до 2015-02-20

                    path.elems.append(element)
                    #--
                    aPan[0].value = element.IdPoly
                    aPan[1].value = element.IdLine
                    aPan[2].value = 0
                    err=k3.getpan6par(26,aPan) # Инфа по крепежу
                    if err>0:
                        element.Fixs.count= int(aPan[3].value)
                        for ifix in range(element.Fixs.count):
                            aPan[2].value = ifix+1
                            err=k3.getpan6par(26,aPan) # Инфа по крепежу
                            tFix=FixInfo()
                            tFix.Type=int(aPan[3].value)
                            tFix.BMask=int(aPan[4].value)
                            tFix.SgvigLine=aPan[5].value
                            tFix.Length=aPan[6].value
                            tFix.Orders=aPan[6].value
                            element.Fixs.fixinfo.append(tFix)
                            
                    #--
                    aPan[0].value = element.IdPoly
                    aPan[1].value = element.IdLine

                    err=k3.getpan6par(10,aPan) # Инфа по кромке
                    if err==1:
                        element.Band.Material = int(aPan[2].value)
                        # Комент для проверки обновления
                        element.Band.Thickness = k3.priceinfo(element.Band.Material ,'Dept',k3.priceinfo(element.Band.Material ,'Thickness',0,1),1)
                        element.Band.znak = k3.priceinfo(element.Band.Material ,'znakKrom',0,1)
                        element.Band.znakduble = int(k3.priceinfo(element.Band.Material ,'znakKromDuble',0,1))
                        element.Band.znakindex = int(k3.priceinfo(element.Band.Material ,'znakKromIndex',0,1))
                        element.Band.Color = int(aPan[3].value) if int(aPan[3].value)>0 else 256
                        element.Band.BMask = aPan[4].value
                        element.Band.Length = aPan[5].value

                        if element.IdPoly == 1 and self.forma in [2,3]:
                            flag = []
                            Flag = 10 if abs(element.Band.Thickness - 2)<0.1 and element.Band.Thickness<2.5 else 8
                            flag.append(Flag)
                            #Flag = 36 if abs(element.Band.Thickness - 2)<0.1 and element.Band.Thickness<2.5 else 34
                           # flag.append(Flag)
                            if    element.IdLine        == 1:        # D
                                poly.FlagYmin = flag
                            elif  element.IdLine        == 3:        # C
                                poly.FlagXmax = flag
                            elif  element.IdLine        == 5:        # E
                                poly.FlagYmax = flag
                            elif  element.IdLine        == 7:        # B
                                poly.FlagXmin = flag
                        elif element.IdPoly == 1 and self.forma==1: # свободный контур
                            poly.FlagYmin =  [8.0,10.0]
                            poly.FlagXmax = [8.0,10.0]
                            poly.FlagYmax = [8.0,10.0]
                            poly.FlagXmin =  [8.0,10.0]


            #-- Очищаем структуру панели
            #print "Очищаем структуру панели"
            NULLOUT=k3.getpan6par(999,aPan)

        #---------------------------------------------------------------------------------
        def _cutsPoly(aPan, vGetPan, poly, IsCuts, self):
            #print '--------------------------------------'
            #print '_cutsPoly  vGetPan=', vGetPan
            #  1. Запрос количества несквозных вырезов
            aPan[0].value=0
            N_Cuts=k3.getpan6par(vGetPan,aPan)
            if N_Cuts < 0:
                return None
            N_Cuts = int(aPan[1].value)  #  количество несквозных вырезов, элементы контуров которых попадают внутрь результирующего полилайна
            l_cuts_id = [int(aPan[2+i].value) for i in range(N_Cuts)] #  ID контуров несквозных вырезов
            poly.n_paths = 0
            for cut in l_cuts_id:
                # 2. Запрос количества непрерывных кусков из элементов в контуре несквозного выреза
                aPan[0].value=cut
                aPan[1].value=0
                N_Cuts=k3.getpan6par(vGetPan,aPan)
                if N_Cuts > 0:
                    N_Cuts = int(aPan[2].value) # число непрерывных кусков
                    if N_Cuts > 0:
                        # 3. Запрос количества элементов в одном непрерывном куске из элементов контура несквозного выреза
                        poly.n_paths = poly.n_paths + N_Cuts
                        for sub_cut in range(1, N_Cuts+1):
                            aPan[0].value = cut
                            aPan[1].value = sub_cut
                            aPan[2].value = 0
                            rt=k3.getpan6par(vGetPan,aPan)
                            n_elements = int(aPan[3].value) #  количество элементов в контуре cut, которых попадают внутрь результирующего полилайна
                            path = PathInfo()
                            path.n_elems = n_elements
                            path.index = cut
                            # для глухих вырезов заполняем признак стороны и глубину
                            if IsCuts:
                                aPan[0].value=cut
                                aPan[1].value=0
                                err = k3.getpan6par(8,aPan)
                                path.depth = aPan[5].value
                                if path.depth < 0.0:
                                    path.cutSide = 'F'
                                elif path.depth > 0.0:
                                    path.cutSide = 'A'
                                else:
                                    path.cutSide = None

                            poly.paths.append(path)
                            aInfoCuts = k3.VarArray(n_elements+3)
                            #4. Запрос элемента контура
                                #на входе
                                  #array[0] - ID контура несквозного выреза
                                  #array[1] - номер непрерывного куска (с 1)
                                  #array[2] - номер элемента (больше 0)
                                #на выходе
                                  #array[3] - тип элемента: 1 - отрезок; 2 - дуга; 3 - сплайн
                                  #если тип элемента отрезок, то
                                    #array[4...6] - координаты начала и
                                    #array[7...9] - конца отрезка в ЛСК панели
                                  #если тип элемента дуга, то
                                    #array[4...6] - координаты начала,
                                    #array[7...9] - середины и
                                    #array[10...12] - конца дуги в ЛСК панели
                                  #если тип элемента сплайн, то
                                    #никакой информации больше не выдаем
                            for j in range(n_elements):
                                aPan[0].value = cut
                                aPan[1].value = sub_cut
                                aPan[2].value = j+1
                                NULLOUT=k3.getpan6par(vGetPan,aPan)
                                element = ElemsInfo()
                                element.IdPoly = cut
                                element.IdLine = int(j+1)
                                element.TypeElem = int(aPan[3].value)

                                # - c 2015-02-20-------------
                                baseGeoinfo= [aPan[i_p].value for i_p in range(4, 13)]
                                ls = self.matrGeoInfo(baseGeoinfo)
                                element.GeoInfo = ls
                                #GeoInfo = [aPan[i_p].value for i_p in range(4, 13)] # до 2015-02-20
                                path.elems.append(element)
            #-- Очищаем структуру панели
            NULLOUT=k3.getpan6par(999,aPan)

        #---------------------------------------------------------------------------------
        def _isRectangle(InfoPoly):
            '''Анализирует результирующий полилайн панели и возвращает True если он является прямоугольником'''
            listmerge = lambda s: reduce(lambda d, el: d.extend(el) or d, s, [])  # слияния списка списков
            if [1, 1, 1, 1] == [a.TypeElem for a in InfoPoly.paths[0].elems]:
                xl = list(
                    set(listmerge([(round(a.GeoInfo[0], 1), round(a.GeoInfo[3], 1)) for a in InfoPoly.paths[0].elems])))
                yl = list(
                    set(listmerge([(round(a.GeoInfo[1], 1), round(a.GeoInfo[4], 1)) for a in InfoPoly.paths[0].elems])))
                res = len(xl) == len(yl) == 2;  # значит это прямоугольник или нет
            else:
                res = False
            return res

        #-----------------------------------------------------------------------------------------------------------
        if Panel==None:
            Panel=self.holder
        
        if type(Panel) == k3.Var:
            Panel = Panel.value

        self.holder=Panel
        k3.getsnap()
        if self.getPanelProperty(Panel):
            if (PathIn, IsCuts) in self.dict_pathinfo.keys():
                poly = self.dict_pathinfo[(PathIn, IsCuts)]
            else:
                aPan = self.panelInit(Panel)
                poly = PolyInfo()
                self.paths.append(poly)
                if IsCuts:
                    if PathIn == 0:
                        vGetPan = 33
                    else:
                        vGetPan = 34
                    _cutsPoly(aPan, vGetPan, poly, IsCuts, self)
                else:
                    if PathIn == 0:
                        vGetPan = 32
                    else:
                        vGetPan = 31
                    _resultPoly(aPan, vGetPan, poly, IsCuts, self)
                if not IsCuts and (self.rectangle_forma is None):
                    self.rectangle_forma = _isRectangle(poly)
                self.dict_pathinfo[(PathIn, IsCuts)] = poly
            k3.resnap()
            return poly
        else:
            k3.resnap()
            return None

    def matrGeoInfo(self, baseGeoinfo):
        tt=(baseGeoinfo[i:i+3] for i in range(0, len(baseGeoinfo), 3))
        ls = []
        ss=list(tt)
        for s in ss:
            en = self.matrixPoint(s)
            ls.extend(en)
        return ls


#-------------------------------------------------------------------------------
    def getKontur(self, Panel=None,IDKontur = 1, IN = 0):
        '''Извлекает контур или группу контуров из панели
        Panel - <k3.Var()> указатель на панель
        IDKontur - ID контура 1-внешний контур
        IN - 0 или 1 0-с учетом кромки 1-без учета кромки(полотно панели)
        Теперь в случае запроса контура главного полилайна (arr[1]==1)

на выходе
arr[4] -  указатель на результирующую плоскую область полотна панели с учетом кромок (всегда больший)
arr[5] – количество контуров в arr[4]
arr[6] -  указатель на результирующую плоскую область полотна панели БЕЗ учета кромок (полотно панели)
arr[7] – количество контуров в arr[6]
            '''
        tValueIN = [0,1,False,True]
        dValueIN = {0:5,1:3,False:5,True:3}
        if IN not in tValueIN:
            raise BaseException('\nОшибка вызова функции. Значение аргумента за пределами допустимых значений ' + str(
                tValueIN) + ' задано ' + str(IN))
        if Panel is None:
            Panel = self.holder
        aPan = self.panelInit(Panel)
        aPan[0].value=IDKontur
        nobjs = k3.sysvar(60)
        NULLOUT=k3.getpan6par(27,aPan)
        pk = k3.Var()
        if IDKontur == 1:
            pk  = aPan[dValueIN[IN]]
        else:
            pk  = aPan[1]
        nobjs = k3.sysvar(60) - nobjs
        if nobjs>1:
            k3.delete(k3.k_last,nobjs,k3.k_remove,pk.value,k3.k_done)
        #-- Очищаем структуру панели
        NULLOUT=k3.getpan6par(999,aPan)
        return pk

    
    def setMatrixPanTexture(self):
        self.matr = self._array(16)
        self.Ohcunit()
        self.is_matr = True        
        if self.dirNotOrto and self.is_matr:
            k3.getsnap()
            try:
                vs = k3.getobjvisual(self.holder)
                if  vs< 1:
                    k3.visible(self.holder)
                k3.setucs(k3.k_lcs, self.holder)
                k3.setucs(k3.k_rotate, k3.k_2points, (0 , 0 , 0), (0 , 0 , 1), 180.0-self.pandir)
                gab = obj_k3_gab3(self.holder)
                self.Otdrotxyz((0, 0, 0), (0, 0, 1), -1*k3.radian(180.0-self.pandir))
                self.Otdtran((-1*gab[0], -1*gab[1], 0))
                if  vs< 1:
                    k3.invisible(self.holder)                
                self.is_matr = False
            finally:
                k3.resnap()    
#-------------------------------------------------------------------------------
    def _objgab(self, Panel, aXm):
        #isPanelVisible = True  if k3.getobjvisual(Panel) == 1 else False # Исправлено 10/04/2014
        NULLOUT= k3.objgab3(Panel,aXm)
        laXm = [ta.value for ta in aXm]
        isPanelVisible = True  if laXm[3] > laXm[0] or laXm[4] > laXm[2] or laXm[5] > laXm[2] else False        
        if not isPanelVisible:
            rs = k3.visible(k3.k_partly,Panel, k3.k_done)
            NULLOUT= k3.objgab3(Panel,aXm)
        if not isPanelVisible:
            rs = k3.invisible(k3.k_partly,Panel, k3.k_done)
            
    def getPanelProperty(self, Panel=None):
        ''''Читает свойства панели'''

        def _getGabPointPan(Panel, aXm, self, ucs=None):
            '''заполняет self.gabpoint свойство габаритами панели Panel
            в случае успешного выполнения возвращает True'''
            try:
                
                self._objgab(Panel, aXm)
                self.gabpoint = [aXm[0].value,aXm[1].value,aXm[2].value,aXm[3].value,aXm[4].value,aXm[5].value]
                #self._objgab(Panel, aXm)
                return True
            except:
                k3.putmsg(
                    'Ошибка анализа панели! Вероятно анализируемая панель находится на погашенном или замороженном слое.')
                return False

        if Panel==None:
            Panel=self.holder
        
        if type(Panel) == k3.Var:
            Panel = Panel.value
        k3.getsnap()

        self.holder=Panel
        self.amass_locale = self.getmix()
        try:
            self.e_hashcode = k3.gethashcode(self.holder)
        except:
            pass # для версий старше 2 ноября 2015
        aXm =  k3.VarArray(6)
        NULLOUT=k3.initarray(aXm,0) # работает для версий 7,1 от 7,11,2012
        aPan = self.panelInit(Panel)

        #-- Читаем материал панели
        aPan[0].value=0
        NULLOUT=k3.getpan6par(2,aPan)
        self.materialPanel = aPan[0].value
        self.material = self.materialPanel

        self.panelThickness = k3.priceinfo(self.materialPanel,'Thickness',0,1)
        #-- Читаем размеры панели
        aPan[0].value=0
        NULLOUT=k3.getpan6par(11,aPan)
        #print aPan[0].value
        self.forma = aPan[0].value
        #o 1 - пане ль по замкнутому контур у
        #o 2 - пр ямоугольная пане ль
        #o 3 - че тырехугольная панель
        #o 4 - пане ль, гнутая по хор де
        

        if _getGabPointPan(Panel, aXm, self):
            self.get_midpoint()
            if (aPan[0].value!=2):  #-- Если панель не прямоугольная, читаем ее габариты
                k3.getsnap()
                
                if not bool(k3.getobjvisual(Panel)):
                    k3.visible(Panel)

                k3.setucs(k3.k_lcs, k3.k_partly, Panel)
                self._objgab(Panel, aXm)
                k3.resnap()                
                self.plength= round(aXm[3].value-aXm[0].value, 1)
                self.pwidth= round(aXm[4].value-aXm[1].value, 1)
            else:  #-- Иначе берем все параметры
                self.plength = aPan[2].value
                self.pwidth  = aPan[1].value
            self.length = self.plength 
            self.width = self.pwidth  

            #-- Читаем тип панели
            aPan[0].value=0
            NULLOUT=k3.getpan6par(22,aPan)
            self.pTypePan = aPan[0].value
            self.typepan = self.pTypePan
            #-- 11 - стойка
            #-- 12 - полка
            #-- 13 - стенка накладна
            #-- 14 - стенка врезная
            self.pTypeInCut = aPan[1].value
     #-- Направление текстуры
            nullout=k3.getpan6par(19,aPan)
            self.pandir=aPan[0].value
            self.dirNotOrto = ((abs(self.pandir) > 1 and abs(self.pandir) < 89)
                               or (abs(self.pandir) > 91 and abs(self.pandir) < 179)
                               or (abs(self.pandir) > 181 and abs(self.pandir) < 269)
                               or (abs(self.pandir) > 271 and abs(self.pandir) < 359))
            #-- Читаем отделки панели
            aPan[0].value=0
            self.cover_count = k3.getpan6par(28,aPan) #Число отделок панели
            if self.cover_count>0:
                for i in range(-2, 13, 1):
                    if i!=0:
                        aPan[0].value=i
                    else: continue
                    count_cover = k3.getpan6par(28,aPan)
                    laPan = [a.value for a in aPan]
                    if count_cover>0:
                        self.cover_info[i] = laPan[1:int(count_cover*3+1)]

            #-- читаем пропилы
            aPan[0].value=0
            SlotCount = int(k3.getpan6par(17,aPan)) # число пропилов у панели
            if SlotCount>0:
                setattr(self,'pSlots',[])
                for i in range(SlotCount):
                    vSlot = mS.Slot()
                    self.pSlots.append(vSlot)

                for i in range(SlotCount):
                    aPan[0].value = i+1
                    nullout =  k3.getpan6par(17,aPan) # число пропилов у панели
                    self.pSlots[i].Plane  = aPan[1].value
                    self.pSlots[i].Side   = aPan[2].value
                    self.pSlots[i].Shift  = aPan[3].value
                    self.pSlots[i].Width  = aPan[4].value
                    self.pSlots[i].Depth  = aPan[5].value
                    self.pSlots[i].Beg    = aPan[6].value
                    self.pSlots[i].Length = aPan[7].value
                    self.pSlots[i].Angle  = aPan[8].value
                    self.pSlots[i].Map    = aPan[9].value

            #-- Читаем кромки панели
            #-- Узнаем количество контуров в результирующем полилайне
            aPan[0].value = 0
            err = k3.getpan6par(31,aPan)
            self.nRezPath = aPan[1].value
            for ph in range(1,int(self.nRezPath)):
                aPan[0].value = ph
                aPan[1].value = 0
                err = k3.getpan6par(31,aPan)
                nElem = aPan[2].value #-- Число контуров результирующего полилайна

                pass
            #-- Очищаем структуру панели
            NULLOUT=k3.getpan6par(999,aPan)
            self.CurvePath = k3.getattr(Panel,'CurvePath','')
            self.CommonPos = k3.getattr(Panel,'CommonPos',0)
            self.Name = k3.getattr(Panel,'ElemName','')
            self.setMatrixPanTexture()
            self.set_polotno() # Полотно панели
            self.set_holes() # Сверловка панели
            k3.resnap()
            return True
        else:
            k3.resnap()
            return False

    def get_midpoint(self):
        f_mid_coord=lambda v1,v2:(v1+v2)/2
        self.midpoint = list(map(f_mid_coord,self.gabpoint[3:],self.gabpoint[:3]))



#-------------------------------------------------------------------------------
#********** SLOT ***************************************************************
#-------------------------------------------------------------------------------

    def addSlotsInPanel(self):
        aSlot = k3.VarArray(56)
        asstt = [0] * 56
        for i in range(len(asstt)): aSlot[i]=asstt[i]
        NULLOUT=k3.setarrinst(1,"g_Slots",aSlot)
        NumP=0
        k=0
        #nSlotProp = len(gU.vDefProperty.slot_property)
        for k  in range(len(self.slots)):
            cs = self.slots[k]
##            print cs._Slot__slot_property
            if cs is not None:
                nSlotProp = len(cs._Slot__slot_property)
                NumP=k
                for i in range(nSlotProp):
                    j = i + 2

                    nullout = k3.setvarinst(1, "g_Slots", getattr(cs, cs._Slot__slot_property[i]),
                                            (NumP) * nSlotProp + j)
        k=NumP+1
        nullout=k3.setvarinst(1,"g_Slots",k,1)

#-------------------------------------------------------------------------------
    def getCountSlot(self):
        '''-- Читаем число пропилов из g_Slots'''
        NumP=k3.Var()
        NULLOUT=k3.getvarinst(1,"g_Slots",NumP,1,1)
        return NumP.value


#-------------------------------------------------------------------------------
    def setSlotNull(self):
        '''-- Удалить все пропилы из панели'''
        aSlot = k3.VarArray(56)
        asstt = [0] * 56
        #for i in range(len(asstt)): aSlot[i]=asstt[i]
        nullout=k3.initarray(aSlot,0) # работает для версий 7,1 от 7,11,2012
        nullout=k3.setarrinst(1,"g_Slots",aSlot)
        self.slot = []

#-------------------------------------------------------------------------------
#********** BAND****************************************************************
#-------------------------------------------------------------------------------
    def __setBand(self):
        '''Создает массив k3.VarArray(8) из списка self.bands'''
        bandArray = k3.VarArray(8)
        for i in self.bands:
            bandArray[i.Side-1]=i.Material
        return bandArray

#-------------------------------------------------------------------------------
    def setBand(self, Change_Default=False,lBand=[], **tBand):
        '''Назначает кромки на сторону и углы прямоугольной панели.
            -- Входные параметры:

            -- Change_Default по умолчанию False управляет сменой глобальных
            умолчаний при создании нового экземпляра класса Band

            -- tBand  може иметь значения
            --          D - сторона D;
            --          C - сторона C;
            --          E - сторона E;
            --          B - сторона B;
            --          Ang_1 - угол 1
            --          Ang_2 - угол 2
            --          Ang_3 - угол 3
            --          Ang_4 - угол 4
        Пример:
                pan1=PanelRectangle(material=502)
                pan1.setBand(True,B=1500,C=1500,D=0,E=400,Ang_1=0,Ang_2=0,Ang_3=0,Ang_4=0)

                Или lBand может быть списком из экземпляров класса Band
        Пример:
                vband_B = mB.Band()
                vband_C = mB.Band()
                vband_E = mB.Band()
                vband_B.setBand(True,Side='B',  Material=400)
                vband_C.setBand(Side='C',  Material=400)
                vband_E.setBand(Material=400,  Side='E')

                pan1.setBand(lBand=[vband_B,vband_C,vband_E])
                pan2.setBand(lBand=[vband_B,vband_C,vband_E])
                pan3.setBand(lBand=[vband_E])
                pan4.setBand(lBand=[vband_E])
        '''
        #print '******** ',tBand
        if type(tBand)==dict:
            for i in list(tBand.items()):
                tobj = mB.Band()
                # Надо проверить есть ли кромка на эту сторону
                for j in self.bands: # перебираем кромки
                    try:
                        if type(i[0])==str: # Если это буква
                            valSide = gU.vDefProperty.band_permissible[i[0]] # меняем на цифру
                        else:
                            valSide = i[0]
                        if valSide==j.Side:
                            self.bands.remove(j)
                    except:
                        print(( i[0],' недопустимое. Отсутствует в списке band_permissible'))
                tobj.setBand(False,Side=str(i[0]), Material=i[1])
                self.bands.append(tobj)
                if Change_Default:
                    gU.vDefProperty.band_defvalue_rectangle[i[0]]=i[1]
        if type(lBand)==list: # если аргумент это список кромок
            for k in lBand:
                if k.__class__.__name__=='Band':
                    for j in self.bands: # перебираем кромки
                        if k.Side==j.Side: self.bands.remove(j)
                    self.bands.append(k)
#-------------------------------------------------------------------------------

    def setBandNull(self, Change_Default=False):
        '''Обнуляет кромку по сторонам панели.
         Change_Default=False не изменяет умолчаний.
         Change_Default=True изменяет умолчания'''
        self.bands =[]
        #tbands = [0] * 8
        tbands = k3.VarArray(8)
        nullout=k3.setarrinst(1,"g_BandPan",tbands) # назначаем кромки

        if Change_Default:
            for key in gU.vDefProperty.band_defvalue_rectangle:
                gU.vDefProperty.band_defvalue_rectangle[key] = 0

#-------------------------------------------------------------------------------

    def up_band_defvalue(self):
        '''Восстанавливает умолчания по кромке из пользовательских умолчаний'''
        try:
            vType=k3.Var()
            sval=k3.Var()
            bFase_def=k3.Var()
            bRough_def=k3.Var()
            err  = k3.udgetentity("Typ_Kro",vType,bFase_def,sval)
            err1 = k3.udgetentity("RoughBandMater",vType,bRough_def,sval)
            Ang_1 = bRough_def.value
            Ang_2 = bRough_def.value
            band_D = bRough_def.value
            band_C = bRough_def.value
            band_B = bRough_def.value
            Ang_3 = bFase_def.value
            Ang_4 = bFase_def.value
            band_E = bFase_def.value
            gU.vDefProperty.newAttr('band_defvalue_rectangle', #{})
                {'B':band_B,'C':band_C,'D':band_D,'E':band_E,
                'Ang_1':Ang_1,'Ang_2':Ang_2,'Ang_3':Ang_3,'Ang_4':Ang_4})
            return True
        except:
            return False
#-------------------------------------------------------------------------------

    def __setBandDef(self):
        '''Расставляет кромки на панель из умолчаний'''
        if ('band_defvalue_rectangle' in gU.vDefProperty.__dict__)==False:
            self.up_band_defvalue()
        self.bands = []
        try:
            for i in list(gU.vDefProperty.band_defvalue_rectangle.items()):
                tobj = mB.Band()
                tobj.setBand(Side=i[0], Material=i[1])
                self.bands.append(tobj)
        except:
            pass
            
    def udMaskBandDef(self):
        vType=k3.Var()
        sval=k3.Var()
        IsBandInside=k3.Var()
        IsBandCut=k3.Var()
        err  = k3.udgetentity("IsBandInside",vType,IsBandInside,sval)
        err1 = k3.udgetentity("IsBandCut",vType,IsBandCut,sval)
        rs=0
        #o 0x00000001 - кромка включена в размер панели;
        #o 0x00000002 - кромка строится с предварительной фрезеровкой;
        #o 0x00000004 - кромка (фрезеровка) строится с переворотом по оси Z (по вертикали);
        #o 0x00000008 - кромку можно резать;
        #o 0x80000000 - лицевая кромка;
        #o 0x40000000 - текстуру кромки повернуть на 90 градусов
        rs=1*IsBandInside.value+8*IsBandCut.value
        self.bandmaskdef=int(rs)
        return int(rs)
    
    def changeBandFree(self, Arg):
        '''
        Arg список аргументов
        первый элемент указатель на ID Polyline второй ID Line  это набор аргументов для назначения кромки на линию
        возвращает указатель на панель с назначеныой кромкой'''
        if self.holder is None:
            return None
        Panel = self.holder
        aPan = self.panelInit(Panel)

        aPan[0].value = Arg[0]
        aPan[1].value = Arg[1]
        
        n = k3.getpan6par(10,aPan)
        if aPan[2].value==0: aPan[4].value = self.bandmaskdef
        aPan[2].value =  Arg[2]
        
        res = k3.setpan6par(10,aPan)
        self.holder = k3.mbpanel(k3.k_execute, Panel)[0]
        res = self.holder
        #-- Очищаем структуру панели
        #print "Очищаем структуру панели"
        NULLOUT=k3.getpan6par(999,aPan)
        return res    

#-------------------------------------------------------------------------------
#********** FIX ****************************************************************
#-------------------------------------------------------------------------------
    def __setFix(self):
        '''Создает массив k3.VarArray(8) из списка self.fixs'''
        fixArray = k3.VarArray(8)
        #print self.fixs
        for i in self.fixs:
            fixArray[i.Side-1]=i.fixID
            #print i.Side,'---', i.fixID
        return fixArray

#-------------------------------------------------------------------------------

    def setFix(self, Change_Default=False, lFix=[], **tFix):
        '''Назначает крепеж на сторону и углы прямоугольной панели.
            -- Входные параметры:

            -- Change_Default по умолчанию False управляет сменой глобальных
            умолчаний при создании нового экземпляра класса Fix

            -- tFix  може иметь значения
            --          D - сторона D;
            --          C - сторона C;
            --          E - сторона E;
            --          B - сторона B;
            --          Ang_1 - угол 1
            --          Ang_2 - угол 2
            --          Ang_3 - угол 3
            --          Ang_4 - угол 4
        Пример:
                pan1=PanelRectangle(material=502)
                pan1.setFix(True,B=1500,C=1500,D=0,E=400,Ang_1=0,Ang_2=0,Ang_3=0,Ang_4=0)

                Или lFix может быть списком из экземпляров класса Fix
        Пример:
                vfix_B = mF.Fix()
                vfix_C = mF.Fix()
                vfix_E = mF.Fix()
                vfix_B.setFix(True,Side='B',  fixID=45)
                vfix_C.setFix(Side='C',  fixID=45)
                vfix_E.setFix(fixID=75,  Side='E')

                pan1.setFix(lFix=[vfix_B,vfix_C,vfix_E])
                pan2.setFix(lFix=[vfix_B,vfix_C,vfix_E])
                pan3.setFix(lFix=[vfix_E])
                pan4.setFix(lFix=[vfix_E])
        '''
        if type(tFix)==dict:
            for i in list(tFix.items()):
                currFix = None
                # Надо проверить есть ли крепеж на эту сторону
                for j in self.fixs: # перебираем крепеж
                    try:
                        if type(i[0])==str: # Если это буква
                            valSide = gU.vDefProperty.fix_permissible[i[0]] # меняем на цифру
                        else:
                            valSide = i[0]
                        if valSide==j.Side:
                            #self.fixs.remove(j)
                            currFix = j
                    except:
                        print(( i[0],' недопустимое. Отсутствует в списке fix_permissible'))
                tobj = currFix if currFix is not None else mF.Fix()

                if currFix is  None:
                    tobj = mF.Fix()
                    self.fixs.append(tobj)
                else:
                    tobj = currFix
                tobj.setFix(False,Side=str(i[0]), fixID=i[1])
                if Change_Default:
                    gU.vDefProperty.fix_defvalue_rectangle[i[0]]=i[1]
        if type(lFix)==list: # если аргумент это список крепежа
            for k in lFix:
                if k.__class__.__name__=='Fix':
                    for j in self.fixs: # перебираем крепеж
                        if k.Side==j.Side: self.fixs.remove(j)
                    self.fixs.append(k)
#-------------------------------------------------------------------------------

    def setFixNull(self, Change_Default=False):
        '''Обнуляет крепеж по сторонам панели. Но не изменяет умолчаний.'''
        self.fixs =[]
        #tfixs = [0] * 8
        tfixs = k3.VarArray(8)
        nullout=k3.setarrinst(1,"FixtPan",tfixs) # назначаем крепеж
        if Change_Default:
            for key in gU.vDefProperty.fix_defvalue_rectangle:
                gU.vDefProperty.fix_defvalue_rectangle[key] = 0
        return tfixs

#-------------------------------------------------------------------------------
    def up_fix_defvalue(self):
        '''Восстанавливает умолчания по крепежу из пользовательских умолчаний'''
        try:
            gU.vDefProperty.newAttr('fix_defvalue_rectangle',{})
            return True
        except:
            return False
#-------------------------------------------------------------------------------

    def __setFixDef(self):
        '''Расставляет крепеж на панель из умолчаний'''
        if ('fix_defvalue_rectangle' in gU.vDefProperty.__dict__)==False:
            self.up_fix_defvalue()
        self.fixs = []
        for i in list(gU.vDefProperty.fix_defvalue_rectangle.items()):
            tobj = mF.Fix()
            tobj.setFix(Side=i[0], fixID=i[1])
            self.fixs.append(tobj)
#-------------------------------------------------------------------------------
    def get_fix_info(self, Arg):
        '''
        Arg список аргументов
        если список меньше двух функция возвращает None
        если список равен двум, первый элемент указатель на ID Polyline второй ID Line возвращает список параметров крепежей по линии
        если список 8 элементов, то это набор аргументов для назначения кркпежа на линию
        возвращает указатель на панель с назначеным крепежом'''
        if self.holder is None:
            return None
        Panel = self.holder
        aPan = self.panelInit(Panel)

        if len(Arg) == 2:
            aPan[0].value = Arg[0]
            aPan[1].value = Arg[1]
            aPan[2].value = 0
            n = k3.getpan6par(26,aPan)
            n = aPan[3].value
            #print 'n', n
            res = []
            for j in range(1, int(n)+1):

                aPan[0].value = Arg[0]
                aPan[1].value = Arg[1]
                aPan[2].value = j
                r = k3.getpan6par(26,aPan)
                #print r
                if r < 0:
                    res = None
                    break

                r = [a.value for a in aPan]
                r = r[:8]
                #print r
                res.append(r)
        elif len(Arg) < 2:
            res = None
        #-- Очищаем структуру панели
        #print "Очищаем структуру панели"
        NULLOUT=k3.getpan6par(999,aPan)
        return res
    
    def changeFixFree(self, Arg):
        '''
        Arg список аргументов
        если список меньше двух функция возвращает None
        если список равен двум, первый элемент указатель на ID Polyline второй ID Line возвращает список параметров крепежей по линии
        если список 8 элементов, то это набор аргументов для назначения кркпежа на линию
        возвращает указатель на панель с назначеным крепежом'''
        if self.holder is None:
            return None
        Panel = self.holder
        aPan = self.panelInit(Panel)

        if len(Arg) == 2:
            aPan[0].value = Arg[0]
            aPan[1].value = Arg[1]
            aPan[2].value = 0
            n = k3.getpan6par(26,aPan)
            n = aPan[3].value
            #print 'n', n
            res = []
            for j in range(1, int(n)+1):

                aPan[0].value = Arg[0]
                aPan[1].value = Arg[1]
                aPan[2].value = j
                r = k3.getpan6par(26,aPan)
                #print r
                if r < 0:
                    res = None
                    break

                r = [a.value for a in aPan]
                r = r[:8]
                #print r
                res.append(r)
        elif len(Arg) < 2:
            res = None
        else:
            for i in range(len(Arg)):
                aPan[i].value = Arg[i]
            res = k3.setpan6par(21,aPan)
            self.holder = k3.mbpanel(k3.k_execute, Panel)[0]
            res = self.holder
        #-- Очищаем структуру панели
        #print "Очищаем структуру панели"
        NULLOUT=k3.getpan6par(999,aPan)
        return res

#-----------------------------------FixMask--------------------------------------------
    def __setFixMask(self, pan):
        '''Создает массив k3.VarArray(8) из списка self.fixMask'''
        fixMaskArray = k3.VarArray(8)
        #print self.fixs
        for i in pan.fixs:
            fixMaskArray[i.Side-1]=i.fixMask
        return fixMaskArray

    #-------------------------------------------------------------------------------

    def setFixMask(self, Change_Default=False, lFix=[], **tFix):
        '''Назначает крепеж на сторону и углы прямоугольной панели.
            -- Входные параметры:

            -- Change_Default по умолчанию False управляет сменой глобальных
            умолчаний при создании нового экземпляра класса Fix

            -- tFix  може иметь значения
            --          D - сторона D;
            --          C - сторона C;
            --          E - сторона E;
            --          B - сторона B;
            --          Ang_1 - угол 1
            --          Ang_2 - угол 2
            --          Ang_3 - угол 3
            --          Ang_4 - угол 4
        Пример:
                pan1=PanelRectangle(material=502)
                pan1.setFixMask(True,B=1,C=11,D=0,E=5,Ang_1=0,Ang_2=0,Ang_3=0,Ang_4=0)

                Или lFix может быть списком из экземпляров класса Fix
        Пример:
                mfix_B = mF.Fix()
                mfix_C = mF.Fix()
                mfix_E = mF.Fix()
                mfix_B.setFix(True,Side='B',  fixMask=1)
                mfix_C.setFix(Side='C',  fixMask=4)
                mfix_E.setFix(fixMask=4,  Side='E')

                pan1.setFixMask(lFix=[mfix_B,mfix_C,mfix_E])
                pan2.setFixMask(lFix=[mfix_B,mfix_C,mfix_E])
                pan3.setFixMask(lFix=[mfix_E])
                pan4.setFixMask(lFix=[mfix_E])
        '''
        if type(tFix)==dict:
            for i in list(tFix.items()):
                currFix = None
                # Надо проверить есть ли крепеж на эту сторону
                for j in self.fixs: # перебираем крепеж
                    try:
                        if type(i[0])==str: # Если это буква
                            valSide = gU.vDefProperty.fix_permissible[i[0]] # меняем на цифру
                        else:
                            valSide = i[0]
                        if valSide==j.Side:
                            #self.fixs.remove(j)
                            currFix = j
                    except:
                        print(( i[0],' недопустимое. Отсутствует в списке fix_permissible'))
                tobj = currFix if currFix is not None else mF.Fix()

                if currFix is  None:
                    tobj = mF.Fix()
                    self.fixs.append(tobj)
                else:
                    tobj = currFix
                tobj.setFix(False,Side=str(i[0]), fixMask=i[1])
                if Change_Default:
                    gU.vDefProperty.fix_defvalue_rectangle[i[0]]=i[1]
        if type(lFix)==list: # если аргумент это список крепежа
            for k in lFix:
                if k.__class__.__name__=='Fix':
                    for j in self.fixs: # перебираем крепеж
                        if k.Side==j.Side: self.fixs.remove(j)
                    self.fixs.append(k)
#-------------------------------------------------------------------------------
#********** Butts ****************************************************************
#-------------------------------------------------------------------------------

    def buttsNull(self):
        '''-- Обнулить торцевые обработки'''
        TorcPaz = k3.VarAray(32)
        NULLOUT=k3.initarray(TorcPaz,0);
        NULLOUT=k3.setarrinst(1,"g_Butt",TorcPaz);

#-------------------------------------------------------------------------------
    def addButtsInPanel(self):
        aButt = k3.VarArray(56)
        asstt = [0] * 56
        for i in range(len(asstt)):
            aButt[i]=asstt[i]
        NULLOUT=k3.setarrinst(1,"g_Butt",aButt)
        NumP=0
        k=0
        for k  in range(len(self.butts)):
            cs = self.butts[k]
            nButtProp = len(cs._Butt__butt_property)
            NumP=k
            Side = getattr(cs,cs._Butt__butt_property[0])
            for i in range(1,nButtProp):
                nullout = k3.setvarinst(1, "g_Butt", getattr(cs, cs._Butt__butt_property[i]),
                                        (Side - 1) * (nButtProp - 1) + i)



#-------------------------------------------------------------------------------
def main():
    pass

def obj_k3_gab3(obj_k3):
    '''Возвращает список из 6-ти координат'''
    arr=k3.VarArray(6)
    gr=None
    if type(obj_k3)== list:
        if  False not in [isinstance(a, k3.K3Obj) for a in obj_k3]: # если в списке только объекты к3
            tmpLnObj = k3.line(0, 0, 0, 1, 0, 0)
            k3.delete(k3.k_wholly, tmpLnObj, k3.k_done)
            gr=k3.group(obj_k3)
            k3.objgab3(gr[0], arr)
            k3.explode(gr[0])
    elif type(obj_k3)==k3.Var:
            gr=obj_k3.value
            k3.objgab3(gr, arr)
    elif isinstance(obj_k3, k3.K3Obj):
        k3.objgab3(obj_k3, arr)
    
    return [round(a.value,1) for a in arr]

def drawRectanglePanNotOrto(panel):
    if panel.dirNotOrto:
        k3.getsnap()
        try:
            panel.getPanelProperty()
            panel.setMatrixPanTexture()
            mpp = panel.getPanelPathInfo(panel.holder)
            mpp.paths[0].draw()
        finally:
            k3.resnap()


if __name__ == '__main__':
    main()