# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        drill_sp
# Purpose:     Назначить имя слоя при экспорте DXF
#
# Author:      Aleksandr Dragunkin
#
# Created:     31.10.2012-2015
# изменения для версии 7.3 поддержка Python3
# Copyright:   (c) GEOS 2012-13
# Licence:     FREE
#-------------------------------------------------------------------------------
#import wingdbstub
import k3
import hashlib
from BIESSE_layerToDXF import layerToDXF
from mCounter import (Counter,Userproperty, Central,)

#----------------------------------------------
delZero = lambda X: int(X) if X - int(X) < 0.099 else X  # убирает нули первращает вещественное в целое если можно

class Drill(layerToDXF):
    '''Отверстие в К3
     [1] - диаметр отверстия
     [2] - глубина отверстия
     [3] - hOBJ элемента, породившего отверстие.
     [4] - [15] - матрица отверстия вида A11, A12, A13, A14, A21, A22, A23, A24,'''

    def __init__(self, Name=None, Hold=None, Diameter=None, Hohe=None,
                 MX=[], MY=[], MZ=[], Side='X', Panel=None):
        self.Name = Name
        self.Hold = Hold
        self.Diameter = delZero(Diameter)
        self.counter = Counter()

        self.MX = MX
        self.MY = MY
        self.MZ = MZ
        self.XV = MX[2]
        self.YV = MY[2]
        self.ZV = MZ[2]
        self.Xc = MX[3]
        self.Yc = MY[3]
        self.Zc = MZ[3]

        self.objs = []
        self.list_of_entries = []
        self.DrawDim = True
        self.DrawNote = True
        if 0 <= abs(MX[2] - 1.0) < 0.001:
            self.Side = 'B'
        elif 0 <= abs(MX[2] + 1.0) < 0.001:
            self.Side = 'C'
        elif 0 <= abs(MY[2] - 1.0) < 0.001:
            self.Side = 'D'
        elif 0 <= abs(MY[2] + 1.0) < 0.001:
            self.Side = 'E'
        elif 0 <= abs(MZ[2] - 1.0) < 0.001:
            self.Side = 'F'
        elif 0 <= abs(MZ[2] + 1.0) < 0.001:
            self.Side = 'A'
        else:
            self.Side = 'X'
        # Если отверстие висит в воздухе над панелью
        # Требуется посчиать реальную глубину сверловки
        if self.Side in ['A', 'F']:
            if self.Zc < 0.1:
                Hohe = round(Hohe + self.Zc + 0.1)
            elif self.Zc > Panel.panelThickness + 0.1:
                th_cover = 0
                if Panel.cover_count > 0:
                    for th_c in Panel.cover_info.keys():
                        th_cover = th_cover + Panel.cover_info[th_c][2]
                Hohe = round(Panel.panelThickness + th_cover - (self.Zc - Hohe) + 0.1)

        self.Hohe = delZero(Hohe)

        if (Panel.panelThickness - Hohe) < 0.01 and (self.Side in ['A', 'F']):
            self.Through = True
        else:
            self.Through = False
            if self.Side == 'F':
                self.counter.drill_F = True
            elif self.Side == 'A':
                self.counter.drill_A = True

        self.HolTypes = k3.getattr(Hold, 'priceid', 0)
        sVal = k3.priceinfo(self.HolTypes, 'MatName', '', 1)
        self.Name = str(sVal)
        sVal = k3.priceinfo(self.HolTypes, 'Alias', '', 1)
        self.Alias = str(sVal)

    #----------------------------------------------------------------------
    def get_lrs(self):
        return [self.Side, self.Diameter, self.Hohe, self.MX, self.MY, self.MZ, self.XV, self.YV, self.ZV, self.Xc, self.Yc, self.Zc]        

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

    def getPointForDrawing(self):
        '''Возвращает координату точки для размерной цепи'''
        result = (self.Xc, self.Yc, 0)
        return result

    def Draw(self, Side="F", PathIn=1, IsOBJDXF=True, LAYERTODXF=False, OBJ_DXF=None):
        '''Изображение отверстия'''
        userproperty = Userproperty()
        cir = k3.Var()
        list_objs = []
        g_upr = k3.GlobalVar('g_upr')
        gupr = g_upr.value
        #-- Нормируем вектор направления
        #self.getNormal()
        result = False
        issign = lambda S: 1 if S == 'A' else -1

        if self.Side == Side or self.Through == True:
            holesPath = k3.mpathexpand("<k3files>") + '\Holes\\'
            nm = holesPath + str(self.Diameter) + ('_' + str(self.Hohe) if not self.Through else '') + '.k3'
            cir = k3.circle(self.Xc, self.Yc, 0., k3.k_normal, (0., 0., 1.), self.Diameter / 2.0)[0]
            ct = cir
            # ставим особый символ для идентификации отверстий
            try:
                if IsOBJDXF:
                    if LAYERTODXF:
                        self.Change(cir, self.set_name_layer_drill())
                    OBJ_DXF.addCounterHandle(cir)
                    if gupr != 1.0:
                        print(gupr)
                        ct = k3.scale(k3.k_copy, cir, k3.k_done, self.Xc, self.Yc, 0., gupr)
                else:
                    if gupr != 1.0:
                        print(gupr)
                        k3.scale(k3.k_nocopy, cir, k3.k_done, self.Xc, self.Yc, 0., gupr)
            

                if k3.fileexist(nm) > 0:
                    tt = k3.append(nm, self.Xc, self.Yc, 0.)
                    if len(tt) > 0:
                        tt = k3.group(tt)
                        if gupr != 1.0:
                            k3.scale(k3.k_nocopy, tt[0], k3.k_done, self.Xc, self.Yc, 0., gupr)
                        self.objs.append(tt[0])
            except:
                pass
            result = True
            self.objs.append(cir)
            #k3.objident(k3.k_last,1,cir)
            k3.chprop(k3.k_lwidth, cir, k3.k_done, userproperty.DrawLineS)
            if self.Through:
                dss = ''
            else:
                dss = "x" + str(self.Hohe)
        elif self.Side in ['B', 'C', 'D', 'E', 'X']:  # Торцевые отверстия
            #-- Внутренняя линия отверстия
            chkn = 0;
            xc1 = self.Xc
            yc1 = self.Yc
            xc2, yc2 = self.getEndPointTHole()
            colcen = 60
            lineCen = Central(xc1, yc1, 0, xc2, yc2, 0)
            #k3.chprop(k3.k_grfcoeff,k3.k_last,1,k3.k_done,1)
            k3.setucs(xc1, yc1, 0, xc2, yc2, 0, xc2 * 1.5, yc2 * 1.5, 0)
            recObj = k3.rectangle(k3.k_3points, 0, self.Diameter / 2.0, 0, self.Hohe, self.Diameter / 2.0, 0, 0,
                                  -self.Diameter / 2.0)[0]
            k3.setucs(k3.k_previous)
            self.objs.extend([lineCen, recObj])
            if IsOBJDXF:
                if LAYERTODXF:
                    self.Change(recObj, self.set_name_layer_drill())
                OBJ_DXF.addCounterHandle(recObj)
                OBJ_DXF.addCounterHandle(lineCen)
            result = True

        return result

    def getEndPointTHole(self):
        self.getNormal()
        xc2 = self.Xc + self.holxv * self.Hohe
        yc2 = self.Yc + self.holyv * self.Hohe
        return xc2, yc2

    def moveStartPointTHole(self, delta):
        self.getNormal()
        xc2 = self.Xc - self.holxv * delta
        yc2 = self.Yc - self.holyv * delta
        return xc2, yc2


    def getNormal(self):
        '''Нормируем вектор направления'''
        nor = k3.sqrt(self.XV * self.XV + self.YV * self.YV + self.ZV * self.ZV)
        self.holxv = self.XV / nor
        self.holyv = self.YV / nor
        self.holzv = self.ZV / nor
        
class Drill_SP:
    #----------------------------------------------------------------------
    def drill_finder(self, params=[],Panel=None):
        '''Возвращает список объектов типа Drill принадлежащих панели'''

        def _drill_holder(self, _drill_fabrick, Panel):
            '''Определяем отверстия принадлежащие панели'''
            keyvisible = True
            pan_holes = []
            if not bool(k3.getobjvisual(self.holder)):
                k3.visible(self.holder)
                keyvisible = False
                nPanHole = int(k3.getholes(self.holder))
                aPanHoles = k3.VarArray(nPanHole*15, 'aPanHoles')
                k3.getholes(self.holder, 'aPanHoles')
                pan_holes = []
                gs = 0
                for i in range(int(nPanHole)):
                    tmp = _drill_fabrick(gs, aPanHoles, Panel)
                    pan_holes.append(tmp)
                    gs = gs + 15                
            if not keyvisible:
                k3.invisible(self.holder)
            return pan_holes

        def _drill_fabrick(gs, params, Panel):
            '''Создаем объект отверстие на основе переданных параметров'''
            Diameter = params[gs].value
            Hohe = params[gs + 1].value
            Hold = params[gs + 2].value
            MX, MY, MZ, sM = [], [], [], []
            for j in range(4):
                MX.append(params[gs + 3 + j].value)
            for j in range(4):
                MY.append(params[gs + 7 + j].value)
            for j in range(4):
                MZ.append(params[gs + 11 + j].value)
            if Panel.dirNotOrto:
                sM.extend(MX)
                sM.extend(MY)
                sM.extend(MZ)
                sM.extend([0, 0, 0, 1])
                rM = Panel.Ohcmult(sM, Panel.matr)
                rDM = []
                for i in range(0, len(rM), 4):
                    rDM.append(rM[i:i + 4])
                MX, MY, MZ = rDM[0], rDM[1], rDM[2]
        
            tmp = Drill(Hold=Hold, Diameter=Diameter, Hohe=Hohe,
                        MX=MX, MY=MY, MZ=MZ, Panel=Panel)
            return tmp
        
        #---------------------------
        if 'holes' in Panel.__dict__.keys():
            holes = Panel.holes
        else:
            #pan_holes = _drill_holder(self, _drill_fabrick, Panel)
            holes = []
            gs = 0
            for i in range(int(params[1].value)):
                tmp = _drill_fabrick(gs, params[0], Panel)
                #if tmp in pan_holes :
                    #holes.append(tmp)
                holes.append(tmp)
                gs = gs + 15
                #print tmp.__dict__
            Panel.holes = sorted(holes)
        return holes

