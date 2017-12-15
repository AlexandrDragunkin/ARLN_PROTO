# -*- coding: utf-8 -*-
# A3.30 ARLINE

import sys


# commonappdata=k3.mpathexpand("<commonappdata>")+'\\'

dvsyspath=['f:\\Python33\\DLLs',
'f:\\Python33\\Lib',
'f:\\Python33\\Lib\\site-packages',
#'c:\\PKM73\\Bin\\python33.zip'
#'d:\\Python26\\Lib\\site-packages\\openpyxl',
#'d:\\Python26\\Lib\\site-packages\\win32',
#'d:\\Python26\\Lib\\site-packages\\win32\\lib',
#'d:\\Python26\\Lib\\site-packages\\win32com'
]
#for tpath in dvsyspath:
    #if tpath not in sys.path:
        #sys.path.insert(0, tpath)
sys.path.insert(0, 'c:\\PKM73\\Bin\\Lib\\site-packages\\')
# sys.path.insert(0, 'c:\ARL7\Data\PKM\Proto\\')

# try:
    # import wingdbstub
# except:
    # pass

import machine
import A330AR as CurM # импортируем модуль конкретного станка
from nameProg_s import (NameForProg) # класс формирования имени файла
import UtilesN as Utiles
import math
import os
import pyodbc

from UtilesD import iif, degrees
VARIANTPATH = 1 # 0-без кромки 1-с кромкой правильнее это решать только для прямоугольника заготовки
BASEPOINT = None # Номер базы стартовый(0,1,2,3 <-для стороны A 4,5,6,7 -для стороны F )
'''Классы и функции, определенные в модуле machine'''
'''
machine.Arc
  machine.Arc.bounding_box
  machine.Arc.center
  machine.Arc.Divide()
  machine.Arc.end
  machine.Arc.end_pt
  machine.Arc.eval()
  machine.Arc.middle_pt
  machine.Arc.orientation
  machine.Arc.perpendicular()
  machine.Arc.radius
  machine.Arc.start
  machine.Arc.start_pt
  machine.Arc.tangent()
  machine.Arc.Transform()
machine.Attribute
  machine.Attribute.name
  machine.Attribute.name
machine.BoundingBox2d
  machine.BoundingBox2d.max
  machine.BoundingBox2d.min
  machine.BoundingBox2d.size_x
  machine.BoundingBox2d.size_y
machine.Circle
  machine.Circle.bounding_box
  machine.Circle.center
  machine.Circle.Divide()
  machine.Circle.eval()
  machine.Circle.orientation
  machine.Circle.perpendicular()
  machine.Circle.radius
  machine.Circle.tangent()
  machine.Circle.Transform()
machine.Curve
  machine.Curve.bounding_box
  machine.Curve.eval()
  machine.Curve.path
  machine.Curve.path_id
  machine.Curve.perpendicular()
  machine.Curve.tangent()
  machine.Curve.Transform()
  machine.Curve.work_id
machine.Drilling
  machine.Drilling.alfa
  machine.Drilling.beta
  machine.Drilling.depth
  machine.Drilling.diameter
  machine.Drilling.id
  machine.Drilling.panel
  machine.Drilling.panel_id
  machine.Drilling.position
machine.error()
machine.Filletting
machine.Line
machine.Machine
machine.makedirs()
machine.Matrix2d
machine.Matrix3d
machine.message()
machine.Milling
machine.Model
machine.Operation
machine.OrderInfo
machine.Panel
machine.Path
machine.Point2d
machine.Point3d
machine.Settings
machine.Slot
  machine.Slot.depth
  machine.Slot.end
  machine.Slot.id
  machine.Slot.is_plane
  machine.Slot.panel
  machine.Slot.panel_id
  machine.Slot.start
  machine.Slot.width
machine.Vector2d
machine.Vector3d
machine.warning()

'''
vpi=3.1415926535897932384626433832795     # число Pi
eps_d = 0.001 # допустимое отклонение
# Допустимые габариты панелей
#xmax=1000
#xmin=85
#ymax=5000
#ymin=285
#zmax=50
#zmin=8

class Writer:
    '''Класс, осуществляющий вывод информации из класса Boa. Ссылка на этот класс есть в классе Boa
       В этом класск находятся функции, отвечающие за вывод информации о конкретных элементах в выходной файл'''
    def __init__(self):
# Здесь мы создаем текстовый форматные константы для вывода
        self.isFrontF = False
        self.header='''[HEADER]
TYPE=BPP
VER=120
'''
        self.description='''[DESCRIPTION]
|
'''
        self.variables='''[VARIABLES]
PAN=LPX|%f||4|
PAN=LPY|%f||4|
PAN=LPZ|%f||4|
PAN=ORLST|""||0|
PAN=SIMMETRY|1||0|
PAN=TLCHK|0||0|
PAN=TOOLING|""||0|
PAN=CUSTSTR|""||0|
PAN=FCN|1.000000||0|
PAN=XCUT|0||4|
PAN=YCUT|0||4|
PAN=JIGTH|0||4|
PAN=CKOP|0||0|
PAN=UNIQUE|0||0|
PAN=MATERIAL|"wood"||0|
PAN=PUTLST|""||0|
PAN=OPPWKRS|0||0|
PAN=UNICLAMP|0||0|
PAN=CHKCOLL|0||0|
PAN=WTPIANI|0||0|

'''
        self.num_tdcode=int(0) # счетчик номеров обработок TDCODE1 TDCODE2 .... TDCODE99
        self.program="[PROGRAM]"
        self.vbscript="[VBSCRIPT]"
        self.macrodata="[MACRODATA]"
        self.tdcodes='''[TDCODES]
VER=1'''
        self.pcf="[PCF]"
        
        self.tooling="[TOOLING]"
        
        self.subprogs="[SUBPROGS]"
        
        #                          SIDE CRN   X   Y   Z  DP  DIA THR RTY  DX  DY  R   A   DA  NPR ISO  OPT  AZ  AR  AP CKA XRC YRC ARP LRP  ER  MD COW A21 TOS VTR S21  ID   AZS  MAC   TNM  TTP TCL RSP IOS WSP  SPI  DDS DSP BFC SHP EA21 CEN   AGG        PRS
        self.drill= '''@ %s, "TDCODE%i", "" : %i, "%i", %f, %f, %f, %f, %f, %i, %s, %f, %f, %f, %f, %f, %i, "%s", %i, %f, %f, %i, %i, %f, %f, %f, %f, %i, %i, %i, %f, %i, %i, %i, "%s", %f, "%s", "%s", %i, %i, %i, %i, %i, "%s", %f, %i, %i, %i, %i, "%s", "%s", "%s", %i'''
 
         # Это обозначение сквозного отверстия. Косой крестик.
        self.drill_th_geo = '''@ GEO, "TDCODE%i", "": "P1002", 0, "%i", 0, -1, 0, 0, 32, 32, 50, 0, 45, 1, 0, 0, 0, 1, 0, 0
  @ START_POINT, "", "" : %i-10, %i-10, 0
  @ LINC_EP, "", "" : 20, 20, 0, 0, 0, 0, 0, 0
  @ START_POINT, "", "" : %i+10, %i-10, 0
  @ LINC_EP, "", "" : -20, 20, 0, 0, 0, 0, 0, 0
  @ ENDPATH, "", "" :'''
        
        # Вариант для автоматического выбора сверла по диаметру и типу
        self.drill_tdcodes = '''(MST)<LN=1,NJ=TDCODE%i,TYW=1,NT=1,>
(GEN)<WT=1,DL=1,>
(TOO)<DI=%f,SP=%f,CL=0,COD=----------,RO=-1,TY=%i,>'''
        # Вариант для  выбора сверла по конкретному коду COD и типу 
        self.drill_tdcodes_cod = '''(MST)<LN=1,NJ=TDCODE%i,TYW=1,NT=1,>
(GEN)<WT=1,DL=1,>
(TOO)<DI=%f,SP=%f,CL=0,COD=%s,RO=-1,TY=%i,>'''        
        
        self.mill='''@ ROUT, "TDCODE%i", "" : "%s", %i, "%i", %f, %s, "%s", %s, %f, %s, %f, %f, %f, %f, %f, %f, %f, %s, %i, %f, %f, %f, %f, %s, %i, %s, %s, %f, %f, %s, %i, %f, %f, %i, %i'''

        self.mill_tdcodes = '''(MST)<LN=1,NJ=TDCODE%i,TYW=2,NT=1,>
(GEN)<WT=2,DL=0,>
(TOO)<DI=%f,SP=%f,CL=1,COD=FO-20-R,RO=-1,TY=102,>
(IO)<AI=45.000,AO=45.000,DA=20,DT=20,DD=0,IFD=0.00,OFD=0.00,IN=1,OUT=1,PR=0,ETCI=0,ITI=0,TLI=0.00,THI=0.00,ETCO=0,ITO=0,TLO=0.00,THO=0.00,PDI=0.00,PDO=0.00,>
(WRK)<OP=1,CO=1,HH=0.000,DR=1,PV=0,PT=0,TC=%i,DP=,SM=0,TT=0,RC=0,BD=0,SW=0,IC="",IM="",IA="",PC=0,BL=0,PU=0,EA=0,EEA=0,SP=0,AP=0,>'''


        self.startsegment = '''  START_POINT, "", "" : %f, %f, %s '''
        #                                        XE  YE  ZS  ZE  SC  FD  SP  MTV
        self.linesegment =  '''  LINE_EP, "", "" : %f, %f, %f, %f, %s, %f, %f, %i'''
        #                                         X2  Y2  XE  YE  ZS  ZE  SC
        self.arcsegment =   '''  ARC_IPEP, "", "" : %f, %f, %f, %f, %f, %f, %i, %i, 0, 0, %s'''
        #
        self.millend =      '''  ENDPATH, "", "" :'''
        #
        self.slot = '''@ CUT_X, "TDCODE%i", "" : %i, "1", %f, %f, 0, %f, %s, 0, 100, "", 1, 4, 0, 0, 0, %f, 0, 0, 0, 1'''
        #                                                XS  YS     DP  L        дистанция повторов
        self.slot_tdcodes = '''(MST)<LN=1,NJ=TDCODE%i,TYW=3,NT=1,>
(GEN)<WT=3,DL=1,>
(TOO)<DI=4.0000,SP=4.0000,CL=2,COD=----------,RO=-1,TY=200,ACT=0,NCT=,DCT=5.000000,TCT=0.000000,DICT=20.000000,DFCT=80.000000,PCT=60.000000,>
(IO)<AI=0.000,AO=0.000,DA=%f,DT=%f,DD=0.000,IFD=0.00,OFD=0.00,IN=0,OUT=0,PR=0,ETCI=0,ITI=0,TLI=0.00,THI=0.00,ETCO=0,ITO=0,TLO=0.00,THO=0.00,PDI=0.00,PDO=0.00,>
(WRK)<OP=1,CO=0,HH=%f,DR=1,PV=0,PT=0,TC=0,DP=%f,SM=0,TT=0,RC=0,BD=0,SW=0,IC="",IM="",IA="",PC=0,BL=0,PU=0,EA=0.000,EEA=0,SP=0,AP=0,>
(SPD)<AF=0.00,CF=0.000,DS=0.00,FE=0.00,RT=0.00,OF=0.00,>
(MOR)<PE=0.000000,TG=0.000000,TL=0.000000,WH=0.000000,>'''
        #Для каждой обработки требуется заполнять несколько секций в файле. [PROGRAM] и [TDCODES] обязательно. Поэтому вывод делаем в словарь
        self.dict_section = {'[PROGRAM]':[],'[TDCODES]':[]}

        # Подписи на выводе для АРЛАЙН
        #@ GEOTEXT, "TDCODE0", "", 849 : "POTPIS", 0, "2", "(F)", LPX/2, LPY+70-70+200, 0, 0, 0, 0, 0, 0, 0, 0, "Century Gothic", 70, 0, 0, 0, 0, 1, 0, -1, 32, 32, 50, 0, 45, 0, 0, 0, 0, 0, 1, 1

        self.PlastName = '''@ GEOTEXT, "TDCODE%i", "" : "POTPIS", 0, "2", "(%s)", LPX/2, LPY+70-70+200, 0, 0, 0, 0, 0, 0, 0, 0, "Century Gothic", 70, 0, 0, 0, 0, 1, 0, -1, 32, 32, 50, 0, 45, 0, 0, 0, 0, 0, 1, 1'''

        #@ GEO, "TDCODE1", "", 697 : "TEXTURA", 0, "1", 0, -1, 0, 0, 32, 32, 50, 0, 45, 1, 0, 0, 0, 1, 0, 0
          #@ START_POINT, "", "", 698 : -100, -200, 0
          #@ LINE_EP, "", "", 699 : -200, -200, 0, 0, 0, 0, 0, 0, 0
          #@ LINE_EP, "", "", 700 : -200+30, -200+10, 0, 0, 0, 0, 0, 0, 0
          #@ LINE_EP, "", "", 701 : -200, -200, 0, 0, 0, 0, 0, 0, 0
          #@ LINE_EP, "", "", 702 : -200+30, -200-10, 0, 0, 0, 0, 0, 0, 0
          #@ ENDPATH, "", "", 703 :
        self.TextureDir_0 = '''@ GEO, "TDCODE%i", "" : "TEXTURA", 0, "1", 0, -1, 0, 0, 32, 32, 50, 0, 45, 1, 0, 0, 0, 1, 0, 0
            @ START_POINT, "", "": -100, -200, 0
            @ LINE_EP, "", "" : -200, -200, 0, 0, 0, 0, 0, 0, 0
            @ LINE_EP, "", "" : -200+30, -200+10, 0, 0, 0, 0, 0, 0, 0
            @ LINE_EP, "", "" : -200, -200, 0, 0, 0, 0, 0, 0, 0
            @ LINE_EP, "", "" : -200+30, -200-10, 0, 0, 0, 0, 0, 0, 0
            @ ENDPATH, "", "" :        '''
        self.TextureDir_90 = '''@ GEO, "TDCODE%i", "" : "TEXTURA", 0, "1", 0, -1, 0, 0, 32, 32, 50, 0, 45, 1, 0, 0, 0, 1, 0, 0
            @ START_POINT, "", "": -100, -200, 0
            @ LINE_EP, "", "" : -100, -100, 0, 0, 0, 0, 0, 0, 0
            @ LINE_EP, "", "" : -100-10, -100-30, 0, 0, 0, 0, 0, 0, 0
            @ LINE_EP, "", "" : -100, -100, 0, 0, 0, 0, 0, 0, 0
            @ LINE_EP, "", "" : -100+10, -100-30, 0, 0, 0, 0, 0, 0, 0
            @ ENDPATH, "", "" :        '''

        # Выводим указатель для кромки для
        self.BandSide = '''@ GEO, "TDCODE%i", "" : "KROMKA", 0, "%i", 0, -1, 0, 0, 32, 32, 50, 0, 45, 1, 0, 0, 0, 1, 0, 0
  @ START_POINT, "", "" : %s, %s, 0
  @ LINE_EP, "", "" : %s, %s, 0, 0, 0, 0, 0, 0, 0
  @ LINE_EP, "", "" : %s, %s, 0, 0, 0, 0, 0, 0, 0
  @ RECTANGLE, "", "" : %s, %s, %s, %s, 1, 0, 0, 1, HALF, 0, 0, 0, 0, 0, 0, 1, 1
  @ ENDPATH, "", "" :
  '''

        self.BandSidesSimbol = '''@ GEOTEXT, "TDCODE%i", "" : "KROMKA", 0, "%i", "G%i", %s, %s, 0, 0, 0, 0, 0, 0, 0, 0, "Century Gothic", 70, 0, 0, 0, 0, 1, 0, -1, 32, 32, 50, 0, 45, 0, 0, 0, 0, 0, 1, 1
        '''

# Здесь мы задаем методы для вывода
    def DrillingCommand(self, num, drill):
        '''Вывод информации об отверстии в файл

        num - порядковый номер отверстия
        drill - отверстие
        '''
        result_DrillingCommand = False
        self.num_tdcode +=1 # Увеличиваем значение счетчика на 1
        # x,y,z - координаты отверстия в системе координат панели
        x=drill.position.x
        y=drill.position.y
        z=drill.position.z
        # d, h - диаметр и глубина отверстия, соответственно
        d=drill.diameter
        h=drill.depth
        # alpha - угол между Ox и проекцией направляющей на Oxy (угол отверстия в проекции пласти панели)
        alpha=drill.alfa
        # beta - угол между Oz и направляющей (угол оси отверстия к пласти панели)
        beta=drill.beta
        thicknessPanel=drill.panel.thickness
        ## Здесь задаем координаты в зависимости от стороны панели
        side=Utiles.GetDrillPlane(drill)
        isTrough = Utiles.GetDrillTrough(drill)
        # b=Boa() # для каждого отверстия инициализировать класс, чтобы воспользоваться функцией - убрал
        siden=Boa.GetBiesseSideNum(self, side)
        bb = drill.panel.bounding_box
        Xpanel=bb.max.x-bb.min.x
        Ypanel=bb.max.y-bb.min.y
        crn=4
        if machine.constraints.d_trueposits[BASEPOINT] in drill.list_true_posits:
            # Проверяем возможно ли выполнить это отверстие
            # (список доступных установов drill.list_true_posits) в текущей позиции BASEPOINT
            if (siden==0):
                crn=4
            if (siden==5):  # Типа, низовой сверловки нет
                crn=1
            if (siden==1):
                crn=2
                x=y
                y=z
            if (siden==2):
                crn=4
                y=z
            if (siden==3):
                crn=3
                x=y
                y=z
            if (siden==4):
                crn=1
                y=z
            z=0
            typeinstr = {'TH':1,'BL':0,'':1,'SV':2, }
            
            if 'typ_cod_tool' in drill.__dict__.keys():
                pass
            #if d.typ_cod_tool = mc.typ_cod_tool
            #d.cod_tool
                self._Drill(0, self.num_tdcode, x,y,z,siden,h,d, isTrough, crn, typeinstr=drill.typ_cod_tool, COD=drill.cod_tool)
            else:
                self._Drill(1, self.num_tdcode, x,y,z,siden,h,d, isTrough, crn, typeinstr=typeinstr[drill.typetool])
            drill.cnc_key = True # признак вывода отверстия в файл
            result_DrillingCommand=True
        # if not result_DrillingCommand:
            # print(machine.constraints.d_trueposits[BASEPOINT])
            # print(drill.list_true_posits)
            # print(drill.typetool)
            # print(drill.diameter)
            
            # print(dir(drill))
            # print([arg for arg in dir(drill) if not arg.startswith('_')])
        # if drill.typetool=='BL' and drill.diameter==8.:
            # print(machine.constraints.d_trueposits[BASEPOINT])
            # print(drill.list_true_posits)
        return result_DrillingCommand

    def _Drill(self, v_comand, num_tdcode, x,y,z,side,h,diam,isTrough,crn=4, typeinstr=0 ,thr=0,rty="rpNO",dx=32,dy=32,
               r=50,a=0,da=45,npr=0,iso="",opt=1,az=0,ar=0, ap=0,cka=0,xrc=0,yrc=0,arp=0,lrp=0,er=1,md=0,cow=0,
               a21=0,tos=0,vtr=0,s21=-1,id="",azs=0,mac="",tnm="",ttp=0,tcl=0, rsp=0,ios=0,wsp=0,spi="",dds=0,dsp=0,
               bfc=0,shp=0,ea21=0,cen="",agg="",rps=0, COD="----------"):
        
        if (side==0 or side==5):
            dCRN = {1: 4, 4: 1, 2: 3, 3: 2}
            b="BV"  # Сверление вертикальное
            if isTrough:
                h = 5
                thr = 1
                if side == 5:
                    side = 0
                    crn = dCRN[crn]
            else:
                if h > 3 and side == 0:
                    
                    if diam == 35:
                        if h<10:
                            pass
                        else:
                            h = 13
                    # else:
                        # h = 12.5 # Для всех глухих пластевых отверстий . сделал по согласованию со Стасом 2014/12/17
                    if diam==10. :
                        typeinstr = 2 # SVASTA  есть только комбинированная 
                        h = 14
                if h<=3 and diam==5:
                    typeinstr = 1 # сквозное для наколки
        else:
            b="BH"  # Сверление горизонтальное

        ty = typeinstr
        if thr == 1:
            pass
        
        print(self.drill % (b,num_tdcode,side,crn,x,y,z,h,diam,thr,rty,dx,dy,r,a,da,npr,iso,opt,az,ar,ap,cka,xrc,yrc,arp,lrp,er,md,cow,a21,tos,vtr,s21,id,azs,mac,tnm,ttp,tcl,rsp,ios,wsp,spi,dds,dsp,bfc,shp,ea21,cen,agg,b,rps), file=self.OutputFile)
        self.dict_section['[PROGRAM]'].append((self.drill,(b,num_tdcode,side,crn,x,y,z,h,diam,thr,rty,dx,dy,r,a,da,npr,iso,opt,az,ar,ap,cka,xrc,yrc,arp,lrp,er,md,cow,a21,tos,vtr,s21,id,azs,mac,tnm,ttp,tcl,rsp,ios,wsp,spi,dds,dsp,bfc,shp,ea21,cen,agg,b,rps)))
        if COD=="----------":
            self.dict_section['[TDCODES]'].append((self.drill_tdcodes,(num_tdcode,diam, diam,ty)))
        else:
            self.dict_section['[TDCODES]'].append((self.drill_tdcodes_cod,(num_tdcode,diam, diam, COD, ty)))

        # Для случая сквозного отверстия рисуем крестик.
        if thr == 1:
            self.num_tdcode +=1 # Увеличиваем значение счетчика на 1
            print(self.drill_th_geo % (self.num_tdcode, crn, x, y, x, y), file=self.OutputFile)
            pass

        return

    def SlotCommand(self, num, slot):
        ''' Вывод информации о пропилах в панели
        num - порядковый номер пропила
        slot - пропил'''
        self.num_tdcode +=1 # Увеличиваем значение счетчика на 1
        #bb = slot.panel.bounding_box
        bb = slot.panel.paths[0].bounding_box
        Xpanel =  bb.max.x - bb.min.x
        Ypanel =  bb.max.y - bb.min.y
        ss = slot.start.x if slot.start.x > eps_d else 0
        ss = ss if ss<Xpanel else Xpanel
        se = slot.end.x if slot.end.x > eps_d else 0
        se = se if se<Xpanel else Xpanel
        w_tool = 4.0

        #print 'ss se xpanel', ss, se ,  Xpanel
        slot_num_width = slot.width/w_tool # Число ширин инструмента в заданном пропиле
        width = slot.width if slot_num_width > (1 + eps_d) else 0
        y_st = slot.start.y
        x_ss=Xpanel-min(Xpanel,max(ss,se))
        x_se=abs(ss-se)

        if abs(x_ss)<3:
            x_ss=3
        if abs(x_se-Xpanel)<3:
            x_se='lpx-3'        
        else:
            x_se=str(x_se)
        dt = 45 if (x_ss < 3)  else 0
        da = 0 if x_se.count('lpx-3')==1 or (se<Xpanel-3.1 and se>3) else 0 
        if slot_num_width >= 1 - eps_d:
            self._SlotByCoords(self.num_tdcode, x_ss,  y_st, slot.depth, x_se, width, da, dt)

        return

    def _SlotByCoords(self, num_tdcode, xbeg, y, depth, xend, width, da, dt):
        print(self.slot % (num_tdcode, 0, xbeg, y, depth, xend, width), file=self.OutputFile)
        self.dict_section['[TDCODES]'].append((self.slot_tdcodes,(num_tdcode, da, dt, width, depth)))
        return

    def geoBandCommand(self, *kwards):
        '''
        Создает указатель на кромку по стороне панели
        '''
        self.num_tdcode +=1 # Увеличиваем значение счетчика на 1
        print(self.BandSide % (self.num_tdcode , kwards[0], kwards[1], kwards[2], kwards[3], kwards[4], kwards[5], kwards[6], kwards[7], kwards[8], kwards[9], kwards[10] ), file=self.OutputFile)
        return
    def geoBandSimbolCommand(self, *kwards):
        '''
        Создает указатель на кромку по стороне панели
        '''
        self.num_tdcode +=1 # Увеличиваем значение счетчика на 1
        print(self.BandSidesSimbol % (self.num_tdcode , kwards[0], kwards[1], kwards[2], kwards[3]), file=self.OutputFile)
        return
    def geoDirTextureCommand(self):
        '''
        Создает указатель вектора направления текстуры
        '''
        self.num_tdcode +=1 # Увеличиваем значение счетчика на 1
        if self.texture_dir_value == 0:
            print(self.TextureDir_0 % (self.num_tdcode ), file=self.OutputFile)
        else:
            print(self.TextureDir_90 % (self.num_tdcode ), file=self.OutputFile)
        #self.dict_section['[PROGRAM]'].append((self.PlastName, (self.num_tdcode, SideName)))
        return


    def geoPlastNameCommand(self):
        '''
        Создает символ обрабатываемой пласти
        '''
        self.num_tdcode +=1 # Увеличиваем значение счетчика на 1
        nameS = 'Лицо'+self.NameSide
        # print(self.isFrontF)
        # print(self.NameSide[0])
        result = (self.isFrontF, self.NameSide[0]=='A')
        # print(result)
        if result==(True,True) or result==(False,False):
            nameS = 'Тыл'+self.NameSide
        # print(self.PlastName % (self.num_tdcode, self.NameSide), file=self.OutputFile)
        print(self.PlastName % (self.num_tdcode, nameS), file=self.OutputFile)
        return

    def MillingCommand(self, num, segment, panel, isouter=True, last=False,startp = True, depth=0,corr=1):
        '''Вывод информации о фрезеровке панели
        num - порядковый номер сегмента
        segment - сегмент фрезеровки
        isouter - признак внешнего контура
        startp - стартовая точка
        last - последний сегмент контура
        '''
        self.num_tdcode +=1 # Увеличиваем значение счетчика на 1

        Xpath,Ypath= self.panelLength, self.panelWidth
        xbeg=Xpath-segment.r.start_pt.x # для версии 6,5 добавил r. необходимо для реверса сегментов
        ybeg=Ypath-segment.r.start_pt.y
        xend=Xpath-segment.r.end_pt.x
        yend=Ypath-segment.r.end_pt.y
        if depth>0:
            thr = 1  
            if self.NameSide.count('$')==0:
                self.NameSide = self.NameSide+'$'
        else: 
            thr = 0
            
        z = 'LPZ+FL' if thr==1 else str(abs(depth)) #abs(depth)
        if (num==1):
            self._MillOperation(self.num_tdcode,corr,"P_"+str(self.num_tdcode),0,2,0,z, thr = 0)
        if startp:
            self._MillStartSeg(xbeg,ybeg,z)
        if (type(segment)==machine.Line):
            self._MillLineSeg(xend,yend)
        if (type(segment)==machine.Arc):
            x3 = Xpath-segment.middle_pt.x
            y3 = Ypath-segment.middle_pt.y
            self._MillArcSeg(x3,y3,xend,yend)
        if (last==True):
            self._MillEnd()
        return
    #@ ROUT, "TDCODE17", "", 53516480 : "P_9", 0, "2", 0, 0, "", 1, 18, -1, 0, 0, 5, 5, 50, 0, 45, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, -1

    def _MillOperation(self,num_tdcode,corr,id,side,crn,z,dp,dia=20,iso="",opt="YES",rty="rpNO",xrc=0,yrc=0,dx=5,dy=5,r=50,a=0,da=45, rdl="YES",nrp=0,az=0,ar=0,zs=0,ze=0,cka="azrNO",thr=1,rv="NO",ckt="NO",arp=0,lpr=0,er="NO",cow=0,ovm=0,
                       a21=0,tos=0,vtr=0):
        print(self.mill % (num_tdcode,id,side,crn,z,dp,iso,opt,dia,rty,xrc,yrc,dx,dy,r,a,da,rdl,nrp,az,ar,zs,ze,cka,thr,rv,ckt,arp,lpr,er,cow,ovm,a21,tos,vtr), file=self.OutputFile)
        self.dict_section['[TDCODES]'].append((self.mill_tdcodes,(num_tdcode,20, 20,corr)))
        return

    def _MillStartSeg(self,x,y,z):
        print(self.startsegment % (x,y,z), file=self.OutputFile)
        return

    def _MillLineSeg(self,x,y,zs=0,ze=0,sc="scOFF",fd=0,sp=0,mtv=0):
        print(self.linesegment % (x,y,zs,ze,sc,fd,sp,mtv), file=self.OutputFile)
        return

    def _MillArcSeg(self,x2,y2,xe,ye,zs=0,ze=0,fd=0,sp=0,sc="scOFF"):
        print(self.arcsegment % (x2,y2,xe,ye,zs,ze,fd,sp,sc), file=self.OutputFile)
        return

    def _MillEnd(self):
        print(self.millend, file=self.OutputFile)
        return

    def DataHeadCommand(self, x, y, z):
        '''Вывод информации в заголовок файл'''
        print(self.header, file=self.OutputFile)
        print(self.variables % (x,y,z), file=self.OutputFile)
        return

    def BeginProgram(self):
        print(self.program, file=self.OutputFile)

    def BeginVBScript(self):
        print(self.vbscript, file=self.OutputFile)

    def BeginMacroData(self):
        print(self.macrodata, file=self.OutputFile)

    def BeginTDCodes(self):
        print(self.tdcodes, file=self.OutputFile)

    def writerTDCodesCommand(self):
        for tdc in self.dict_section['[TDCODES]']:
            print(tdc[0] % tdc[1], file=self.OutputFile)

    def BeginPCF(self):
        print(self.pcf, file=self.OutputFile)

    def BeginTooling(self):
        print(self.tooling, file=self.OutputFile)

    def BeginSubProgs(self):
        print(self.subprogs, file=self.OutputFile)

    def CreateOutputFile(self,FileName):
        '''Открываем на запись файл с именем FileName'''
        self.fname=FileName
        self.OutputFile = open(FileName, 'w')
        return

class Boa(machine.Machine, NameForProg):
    '''
    Это самый главный класс. Именно его методы запускаются при вызове генератора
    Имя этого класс указано в модуле настроек станка (*_settings)
    Этот класс является наследником класса Machine, который реализован в Machine.pyd

    Методы запускаются в следующей последовательности:
      StartProcessing(model) - для всей модели (базы)
      StartPanel(panel)      - для каждой из панелей
        Drilling(drill)      - для каждого из отверстий панели
        Slot(slot)           - для каждого из пропилов панели
        Milling(mill,curve)  - для каждой обработки-фрезеровки панели
        Filletting(fillet,curve) - для каждой обработки-кромковки панели
      EndPanel()             - для каждой из панелей
      EndProcessing()        - для всей модели (базы)
    '''
    def __init__(self):
        ''' Конструктор класса'''
        machine.Machine.__init__(self)            # Вызываем конструктор базового класса. Здесь это обязательно
        '''
        Machine - Класс, генерирующий командные файла для станка
        Метода класса:
                      StartProcessing(model) - Метод вызывается один раз перед началом генерации командных файлов
                      EndProcessing() - Метод вызывается после генерации командных файлов
                      StartPanel(panel) - Начало обработки панели
                      EndPanel() - Конец обработки панели
                      Drilling(drill) - Сверловка панели
                      Slot(slot) - Пропил панели
                      Milling(mill,curve) - Фрезеровка панели
                      Filletting(fillet,curve) - Кромковка
        '''
        self.settings = machine.Settings()        # Собственно, получаем ссылку на класс Settings
        
        '''
              Settings - Класс предоставляет доступ к настройкам приложения, например размер рабочей области станка.
        Свойства класса:
                  machine_name - Имя класса, который будет генерировать команды для станка.
                  machine_module_name - Имя файла в котором находится реализация станка.
                  database_name - Путь к базе данных выгрузки.
                  cmdfile_path - Имя генерируемого командного файла.
                  working_area - BoundingBox2d определяющий рабочую область станка.
        '''
        machine.constraints = CurM.addSettingsToMachine(self.settings)
        # print(machine.constraints.xmax_constr)
        # self.writer = Writer()                    # Класс для вывода информации в файл

        # Стартовая инициализация атрибутов
        self.panelThickness = 16     # Толщина панели
        self.panelWidth = 0         # Ширина панели
        self.panelLength = 0        # Длина панели
        self.panelNum = -1          # Номер панели (Значение атрибута CommonPos)
        self.fname = "" # имя файла управляющей программы
        self.panelName = "" #Имя панели
        self.isProcessing =  False  # Наличие обработок сверловка, фрезеровка, пазы если они есть , то True в противном случае нет смысла выводить файл

        self.millingTech = []       # Список контуров для обработки
        self.bandPunktion = {} #Список сегментов с кромкой принадлежащих габариту панели
        self.isBlindHoleF = False # глухие отверстия по F
        self.isBlindHoleA = False # глухие отверстия по A
        self.isCutsA = False # Глухие вырезы по А
        self.isCutsF = False # Глухие вырезы по F
        self._overt_basepoint = {0: 5, 1: 4, 2: 7, 3: 6, 4: 1, 5: 0, 6: 3, 7: 2} # Номер базы после перворота  0<->7 1<->6
        self.structureOK = True
        
        self.writer = Writer()                    # Класс для вывода информации в файл
        self.writer.isFrontF = False
        
    def CreateCmdfile(self,post):
        '''Создаем файл с управляющей программой

        post - имя файла'''
        fname=post+".bpp"
        self.cmdfileName = self.GetCmdfilePath()
        self.cmdfileName +=fname
        self.writer.CreateOutputFile(self.cmdfileName)
        return

    def GetCmdfilePath(self):
        '''Читаем имя файла'''
        path = self.settings.cmdfile_path

        try:
            machine.makedirs(path)
        except OSError:
            pass
        return path

    def GetBiesseSideNum(self,sideName):
        '''Вернуть номер стороны в формате BiesseWorks'''
        if (sideName=="A"):
            return 0
        if (sideName=="F"):
            return 5
        if (sideName=="E"):
            return 2
        if (sideName=="B"):
            return 3
        if (sideName=="D"):
            return 4
        if (sideName=="C"):
            return 1
        return -1


    def CreateCmdfileHeading(self):
        '''Записываем общий заголовок в командный файл'''
        self.writer.DataHeadCommand(self.panelLength,self.panelWidth,self.panelThickness)
        return

    def CreateCmdfileProgram(self):
        '''Записываем текст программы в командный файл
        возвращает True если создана хотя бы одна секция обработок Сверловки фрезеровки или пропил'''
        self.revis_trueposits_brosers_drill()
        self.writer.BeginProgram()

        result_conturs_1 = self.writerContours(self.millingTech) # Требуется обработать только внешний контур и глухие вырезы
        result_slots = self.writerSlotsCommand(self.slots)
        result_drilling = self.writerDrillingCommand(self.drills)

        result_conturs_2 = self.writerContours(self.millingTech) # Обработку сквозных вырезов следует выполнять только после выполнения всех пазов и сверловок
        self.writer.geoPlastNameCommand()
        self.writer.geoDirTextureCommand()        
        return result_conturs_1 or result_conturs_2 or result_slots or result_drilling

    def CreateCmdfileVBScript(self):
        '''Записываем скриптовые данные в командный файл'''
        self.writer.BeginVBScript()
        return

    def CreateCmdfileMacroData(self):
        '''Записываем макроданные в командный файл'''
        self.writer.BeginMacroData()
        return

    def CreateCmdfileTDCodes(self):
        '''Записываем TD коды в командный файл'''
        self.writer.BeginTDCodes()
        self.writer.writerTDCodesCommand()
        return

    def CreateCmdfilePCF(self):
        '''Записываем PCF в командный файл'''
        self.writer.BeginPCF()
        return

    def CreateCmdfileTooling(self):
        '''Записываем инструменты в командный файл'''
        self.writer.BeginTooling()
        return

    def CreateCmdfileSubProgs(self):
        '''Записываем подпрограммы в командный файл'''
        self.writer.BeginSubProgs()
        return

    def StartProcessing(self,model):
        '''Метод запускается автоматически перед началом обработки панелей'''
        #      ptvsd.enable_attach(None)
        #      ptvsd.wait_for_attach(60)

        pass

    def EndProcessing(self):
        '''Метод запускается автоматически после окончания обработки панелей'''
        print(" ")
        print('Модуль CNC завершил работу')
        print('Программы ЧПУ находятся в папке:')
        print('   ',self.settings.cmdfile_path)
        return

    def writeOutputFile(self, postfix,hashsimbol=''):
        '''Записывает накопленную информацию в  файл'''
        # print("writeOutputFile")
        # Получаем имя файла
        #toInt = lambda x: str(int(x) if  abs(x-int(x)) < 0.2 else round(x, 1))

        #count_common_pos = self.getCountPanels(toInt)
        ##---------------------
        #nmPan = 'Неопределенный материал' if self.panel.nomenclature is None else self.panel.nomenclature.name
        #dnmth=(toInt(self.panel.thickness))+'-'
        #if nmPan.count(toInt(self.panel.thickness))>0:
            #if nmPan.index(toInt(self.panel.thickness))==0:
                #dnmth=''
        #index = dnmth + nmPan + '_' + toInt(self.panel.size.size_x) + 'x' + toInt(self.panel.size.size_y) + 'x' + toInt(self.panel.thickness) + '_' + str(self.panelNum if self.twins is None else self.twins)+postfix+'_'+hashsimbol + '_(' + toInt(count_common_pos) + ')'+'-NEW_VAR'
        ##'('+self.NumOrder+')_' + str(self.panelNum if self.twins is None else self.twins)+postfix+'_'+hashsimbol
        #index = index.replace(' ', '_')
        #index = index.replace('/', '_')
        #index = index.replace('\\', '_')
        
        
        # for m in self.millingTech:
            # if not m.cnc_key:
                # print("m=",m.cnc_key)
            
        # for d in self.drills:
            # if not d.cnc_key:
                # print("d=",d.cnc_key)
            
        # Каждый проход проверяем все ли элементы были обработаны
        # isSlots=True if (False, True) in [(s.cnc_key,s.is_plane) for s in self.slots] else False
        # isMills=True if True in [m.cnc_key for m in self.millingTech] else False
        # isDrills=True if True in [d.cnc_key for d in self.drills] else False
        # print("isSlots=",isSlots,";isMills=",isMills,";isDrills=",isDrills,)
        index = self.name_prog_calc( machine,eps_d,postfix, hashsimbol)
        if (self.panelNum==-1 or
            not ((False in [m.cnc_key for m in self.millingTech]) or
             ((False, True) in [(s.cnc_key,s.is_plane) for s in self.slots]) or
             (False in [d.cnc_key for d in self.drills]))):
        # if self.panelNum==-1 or (isSlots or isMills or isDrills):
            resOutput = False
        else:
            # Создаем файл
            self.CreateCmdfile(index)
            # Пишем в файл шапку
            self.CreateCmdfileHeading()
            # Пишем в файл по очереди все секции
            result = self.CreateCmdfileProgram()
            self.CreateCmdfileVBScript()
            self.CreateCmdfileMacroData()
            self.CreateCmdfileTDCodes()
            self.CreateCmdfilePCF()
            self.CreateCmdfileTooling()
            self.CreateCmdfileSubProgs()
            self.writer.panelName=self.panelName
            if result:
                print("Панель № ",self.panelNum, " Запись в файл",index,".bpp")
                self.writer.OutputFile.close()
                resOutput = True
            else:
                resOutput = self.closeCmdfile()
        return resOutput

    def getCountPanels(self, toInt):
        '''Возвращает число одинаковых commonpos'''
        SQL_STR='''SELECT Count(TElems.CommonPos) AS [Count-CommonPos] FROM TPanels INNER JOIN TElems ON TPanels.UnitPos = TElems.UnitPos GROUP BY TElems.CommonPos HAVING TElems.CommonPos=''' + toInt(self.panel.common_pos)
        cnxn, cursor, recordset = self.odbc_conn(SQL_STR)
        count_common_pos = recordset[0][0]
        return count_common_pos

    def closeCmdfile(self):
        fn = self.writer.OutputFile.name
        self.writer.OutputFile.close()
        os.unlink(fn)
        resOutput = False
        return resOutput

    def rotatePanel(self):
        '''поворачивает панель на 90 градусов против часовой стрелки и сдвигает правильным образом
        в точку базы изменяет имя положения базовой точки'''
        
        def _aposition(self):
            if self.aposition < 360:
                self.aposition += 90
            else:
                self.aposition = 0
        
        self.bandPunktion = {}
        dChtextureDir = {0: 90, 90: 0, -90: 0, 270: 0, 180: 90, -180: 90, 360: 90, -360: 90,}
        b = self.findPathSize(VARIANTPATH) #self.panel.bounding_box
        self.panel.Translate(machine.Vector2d(-b.min.x,-b.min.y))
        if (self.Selobj != 0):  # Если это выбр
            pass
        self.panel.Rotate(vpi/2,machine.Point2d(0,0))
        _aposition(self)
        b = self.findPathSize(VARIANTPATH)
        Xpanel,Ypanel= self.getXY_bounding_box(b)
        self.panel.Translate(machine.Vector2d(Xpanel,0))
        b = self.findPathSize(VARIANTPATH)
        Xpanel,Ypanel= self.getXY_bounding_box(b)
        self.panel.Translate(machine.Vector2d(-b.min.x,-b.min.y))
        self.panelWidth = Ypanel #self.panel.panel_width
        self.panelLength = Xpanel #self.panel.panel_length
        self.writer.panelWidth = self.panelWidth
        self.writer.panelLength = self.panelLength
        self.panel.textureDir = dChtextureDir[round(self.panel.textureDir , 1)]
        self.writer.texture_dir_value = self.panel.textureDir
        global BASEPOINT
        BASEPOINT = BASEPOINT + 1 if BASEPOINT not in [3, 7] else BASEPOINT - 3
        mc = machine.constraints
        for d in self.drills:
            self.drill_revisia(d, mc)

    def drill_revisia(self, d, mc):
        # Side=Utiles.GetDrillPlane(d)
        CurM.change_MinMaxXY_Space(mc, d)
        d.typetool=mc.typetool
        list_property_mc = list(mc.__dict__.keys())
        if 'typ_cod_tool' in list_property_mc:
            d.typ_cod_tool = mc.typ_cod_tool
            d.cod_tool = mc.cod_tool


    def StartPanel(self, panel):
        # print("StartPanel")
        '''Метод вызывается автоматически перед началом обработки каждой панели'''
        self.aposition = 0
        # Контролер числа установов при стартовой базовой точке
        self.start_optimist = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []}
        self.millingTech = []
        self.bandPunktion = {}
        self.drills=[]
        self.slots = [] # Пропилы
        self.workingsides=[]        # Список сторон панели, которые нужно будет обработать
        self.writer=Writer()
        self.isSlotsF = False
        self.isSlotsA = False
        self.isSlotsY = False
        self.isBlindHoleF = False
        self.isBlindHoleA = False
        self.isCutsA = False
        self.isCutsF = False
        self.gnumdet = 0
        self.fname="" # Имя файла управляющей программы
        self.panelName=panel.name
        self.panel = panel
        self.NumOrder = ''
        self.Selobj = 0
        self.twins  = None # строка панелей близнецов
        self.hashsimbol=0
        self.panel.textureDir = self.panel.texture_dir
        # self.writer.isFrontF = False
        
        for a in self.panel.attributes:
            if a.name=='Selobj':
                self.Selobj = int(a.value)
            if a.name=='NumOrder':
                self.NumOrder = str(a.value)
            if a.name=='ListTwins':
                self.twins = str(a.value)
            if a.name == 'GDetNumber':
                self.gnumdet = str(a.value)
            if a.name=='FrontF':
                self.writer.isFrontF = True if int(a.value) == 1 else False
                # print('startpanel_isFrontF=',self.writer.isFrontF)
        
        # self.writer=Writer()
        
        global BASEPOINT
        BASEPOINT = 0 # Номер базы стартовый(0,1,2,3 <-для стороны A 4,5,6,7 -для стороны F )
        if (self.Selobj == 0):  # Если это не выбранная панель, то не фиг ее обрабатывать
            return False
        # (Анализируем габарит панели и поворачиваем ее длинной стороной вдоль X) так делать нельзя.
        # Здесь нельзя только после того как считали все обработки, вот тогда можно. Крутить надо в EndPanel
        # По итогам тестов надо подбирать вариант с минимальным числом установов
        b = self.findPathSize(VARIANTPATH)
        if isinstance(b, list):
            if len(b) == 0:
                self.structureOK = False
                print( '\n !!!!ОШИБКА в структуре панели!!!!!')
                print(('См. панель UnitPos= '+ str(self.panel.id.handle)))
                print('--------------------------------------------')
                return False
        Xpanel,Ypanel= self.getXY_bounding_box(b)
        self.panel.Translate(machine.Vector2d(-b.min.x, -b.min.y))
        self.panelWidth = Ypanel  #self.panel.panel_width
        self.panelLength = Xpanel #self.panel.panel_length
        
        self.writer.panelWidth = self.panelWidth
        self.writer.panelLength = self.panelLength
        self.panel.panelThickness = panel.thickness + 6 if panel.thickness<5 else panel.thickness
        self.panelThickness = panel.thickness + 6 if panel.thickness<5 else panel.thickness

        self.panelNum = panel.common_pos if self.gnumdet == 0 else self.gnumdet
        # Собираем контура
        self.Contour()
        return True

    def writerContours(self, pathsTuple):
        '''Функция подготавливает к выводу контура
        pathsTuple - список контуров, которые нужно обработать
        Требуется обработать только внешний контур и глухие вырезы которые можно сделать.
        Сквозные вырезы только если больше нет пазов и сверловки.
        '''
        result = False
        outer = True
        lFun = lambda v1, v2: abs(v1-v2)
        for p in pathsTuple:
            pCuts = 'cuts' in list(p.__dict__.keys())
            if (not outer) and (not pCuts) and ([a.cnc_key for a in self.drills].count(False)>0):
                continue
            for segment in p.segments:
                for sw in segment.works:
                    if type(sw) == machine.Filletting:
                        segment.band = sw.nomenclature.values['Dept']
                        if segment.path.id.handle == 1:
                            maxPathX = segment.path.bounding_box.max.x
                            maxPathY = segment.path.bounding_box.max.y
                            minPathX = segment.path.bounding_box.min.x
                            minPathY = segment.path.bounding_box.min.y
                            if (abs(segment.start_pt.x-segment.end_pt.x ) < 0.1 and abs(segment.start_pt.x - maxPathX) < 0.1): # Этот сегмент соответствует  С"
                                if 'C' not in list(self.bandPunktion.keys()):
                                    self.bandPunktion['C'] = segment
                                    self.writer.geoBandCommand(1, '0', 'LPY/2', '-50', 'LPY/2+40', '-50-140', 'LPY/2+40', '-1', 'LPY/2', '2', 'LPY')
                                    self.writer.geoBandSimbolCommand(2, segment.band, '-(140/2+50)', 'LPY/2-20')

                            if (abs(segment.start_pt.x-segment.end_pt.x ) < 0.1 and abs(segment.start_pt.x - minPathX) < 0.1): # Этот сегмент соответствует  B"
                                if 'B' not in list(self.bandPunktion.keys()):
                                    self.bandPunktion['B'] = segment
                                    self.writer.geoBandCommand(4, '0', 'LPY/2', '-50', 'LPY/2+40', '-50-140', 'LPY/2+40', '-1', 'LPY/2', '2', 'LPY' )
                                    self.writer.geoBandSimbolCommand(2, segment.band, 'LPX+140/2+50', 'LPY/2-20')

                            if (abs(segment.start_pt.y-segment.end_pt.y ) < 0.1 and abs(segment.start_pt.y - minPathY) < 0.1): # Этот сегмент соответствует  D"
                                if 'D' not in list(self.bandPunktion.keys()):
                                    self.bandPunktion['D'] = segment
                                    self.writer.geoBandCommand(2, 'LPX/2', 'LPY', 'LPX/2-140/2', 'LPY+50', 'LPX/2-140/2+140', 'LPY+50', 'LPX/2', 'LPY+1', 'LPX', '2' )
                                    self.writer.geoBandSimbolCommand(2, segment.band, 'LPX/2', 'LPY+70')

                            if (abs(segment.start_pt.y-segment.end_pt.y ) < 0.1 and abs(segment.start_pt.y - maxPathY) < 0.1): # Этот сегмент соответствует  E"
                                if 'E' not in list(self.bandPunktion.keys()):
                                    self.bandPunktion['E'] = segment
                                    self.writer.geoBandCommand(1, 'LPX/2', 'LPY', 'LPX/2-140/2', 'LPY+50', 'LPX/2-140/2+140', 'LPY+50', 'LPX/2', 'LPY+1', 'LPX', '2' )
                                    self.writer.geoBandSimbolCommand(2, segment.band, 'LPX/2', '-70-70')
                        #print('----Кромка толщиной ',segment.band, ' мм по сегменту----')

            if not p.cnc_key: # Признак вывода в файл ЧПУ отсутствует
                #segments=p.Segments() # специально для версии 6,5
                segments = p.segments
                for s in segments:
                    s.path.overt = p.overt
                    #print(s.band if 'band' in list(s.__dict__.keys()) else '---')
                #----------
                # Изменяет последовательность прохода по сегментам начиная с минимальной точки по XY для внешних и разорванных внутренних
                # и Ищет точку входа у вырезов. Середина самой длинной стороны
                #pCuts = 'cuts' in p.__dict__.keys()
                closed_path = True
                if pCuts:
                    if type(segments[0]) == machine.Circle:
                        r=segments[0].path
                        segments = segments[0].Divide(0.5)
                        for s in segments:
                            s.path_H=r
                        for sg in segments:
                            Utiles.SegmentReverse(sg,0)
                    #segments = Utiles.checkSegments(segments,False)
                    if ((p.overt and p.cuts[0][0] < 0) or
                        (not p.overt and p.cuts[0][0] > 0)):
                        if (abs(segments[0].start_pt.x - segments[-1:][0].end_pt.x) > 0.1 or
                            abs(segments[0].start_pt.y - segments[-1:][0].end_pt.y) > 0.1):
                            closed_path=False
                        else:
                            closed_path=True
                    else:
                        continue
                if (not pCuts) or (pCuts and closed_path):
                    segments = Utiles.checkSegments(segments,outer)
                #----------
                a=0
                ai=0
                last=False

                if p.overt: # признак того что панель перевернута и проходы фрезы должны происходить в обратном порядке
                    segments.reverse()

                conW, singleSetup = self.RevisiaSegmentsToPath(segments, p.overt)

                if False not in singleSetup:
                    p.cnc_key = True # Признак вывода в файл ЧПУ изменяем
                startp = True

                for s in zip(segments,conW[0]):
                    ai += 1
                    conWL=conW[0][ai:]
                    if True not in conWL:
                        last=True
                    # специально для версии 6,5
                    Utiles.SegmentReverse(s[0], p.overt)
                    #depth = p.panel.thickness if not pCuts else abs(p.cuts[0][0])*(-1)
                    depth = 5 if not pCuts else abs(p.cuts[0][0])*(-1)
                    #---
                    if s[1]: # Сегмент есть в списке обрабатываемых
                        a=a+1
                        #-------------------
                        fun_segment_path_is_tcuts=lambda f: f.path_H.is_tcuts if f.path is None else f.path.is_tcuts
                        if (outer==True):
                            corr=2  # Правая коррекция
                        else:
                            s_path_id=segments[0].path_H.id if segments[0].path is None else segments[0].path.id
                            if (((len(segments) == 2)
                                and (False not in conW[0])  # специальное условие для круглого сквозного выреза
                                and (s_path_id.handle>1))
                                or (fun_segment_path_is_tcuts(s[0]))):
                                corr= 2 if p.overt else 1 # Левая коррекция
                            else:
                                corr=2  # Правая коррекция
                        #--------------------
                        self.writer.MillingCommand(a,s[0], self.panel, outer,last,startp, depth,corr)
                        result = True
                        startp = False
                    else:
                        startp = True
            outer=False
        return result

    def writerSlotsCommand(self, slotsTuple):
        '''Подоготавливает к выводу пропилы
        side - сторона пропила
        slotsTuple - список пропилов в данной панели'''
        result = False
        a=0
        for s in slotsTuple:
            #logplane = iif(self.panel.overt, not s.is_plane, s.is_plane)
            if (Utiles.GetSlotDirection(s)=="X" and s.is_plane):
                a=a+1
                if s.cnc_key == False: # Признак вывода отверстия в файл ЧПУ
                    self.writer.SlotCommand(a,s)
                    result = True
                    s.cnc_key = True # Признак вывода отверстия в файл ЧПУ
        return result

    def writerDrillingCommand(self, drillTuple):
        '''Подоготавливает к выводу отверстия
        drillTuple - список отверстий в данной панели'''
        result = []
        #self.writer.geoPlastNameCommand()
        #self.writer.geoDirTextureCommand()
        for d in drillTuple:
            SideS=Utiles.GetDrillPlane(d)
            SideNum=self.GetBiesseSideNum(SideS)
            # print(SideS,' ',' ',SideNum,[a.cnc_key for a in drillTuple])
            if d.diameter == 5.0:
                pass
            # Если сторона не определена,или это стороны F, отверстие не выводим, если сквозное , то выводим
            if (SideNum<0 or SideNum==5) and  not Utiles.GetDrillTrough(d):
                continue
            #if
            # Изменил эту часть кода 2013-06-25
            if d.cnc_key == False: # Признак вывода отверстия в файл ЧПУ (т.е если отверстие не выведено его надо выводить)
                result.append(self.writer.DrillingCommand(drillTuple.index(d),d))
                pass
            #-----------
        return result.count(True)>0

    def revis_trueposits_brosers_drill(self):
        '''корректирует списки допустимых вариантов расположения панели с учетом "братьев"'''
        for dd in self.drills:
            for ddd in self.drills:
                if (ddd.id.handle in dd.brothers):
                    new_true_posits = Utiles.intersect(ddd.list_true_posits, dd.list_true_posits)
                    ddd.list_true_posits = new_true_posits
                    dd.list_true_posits = new_true_posits

    def tech_cicle(self, hashsimbol, p_overt, NameSide):
        self.writer.NameSide = NameSide
        for p in self.millingTech:
            p.overt = p_overt # Добавляем новое свойство у контура overt
            p.segments_cnc_key = [] # Необходимость вывода сегмента на ЧПУ
            [p.segments_cnc_key.append(True) for i in range(len(p.segments))]
        # print(BASEPOINT)
        # print(machine.constraints.d_trueposits[BASEPOINT])
        resultOutput = self.writeOutputFile(self.settings.machine_base_name[BASEPOINT],hashsimbol)
        if resultOutput:
            hashsimbol +=1        
        self.app_start_optimist(resultOutput)
        for i in range(3): # Крутим панель три раза и пытаемся обработать
            # print("tech_cicle_i")
            self.rotatePanel()
            # print(BASEPOINT)
            # print(machine.constraints.d_trueposits[BASEPOINT])
            resultOutput = self.writeOutputFile(self.settings.machine_base_name[BASEPOINT],hashsimbol)
            if resultOutput:
                hashsimbol +=1            
            self.app_start_optimist(resultOutput)
        # print("tech_cicle_fin")
        self.rotatePanel() # Возвращаем в исходное состояние
        return hashsimbol

    def EndPanel(self):
        '''Функция вызывается в конце обработки каждой панели'''
        if (self.Selobj == 0):  # Если это не выбранная панель
            return
        if not self.structureOK:  # Если какие то проблемы в структуре панели
            return
        b = self.findPathSize(VARIANTPATH)
        Ypanel=b.max.y-b.min.y
        Xpanel=b.max.x-b.min.x
        self.panel.textureDir = self.panel.texture_dir
        self.writer.texture_dir_value = self.panel.textureDir
        # print(Xpanel)
        # print(Ypanel)
        if (Xpanel<Ypanel):
            rangeBase = [ 3, 0, 1, 2]
            # print("EndPanel_3")
            self.rotatePanel()
            self.rotatePanel()
            self.rotatePanel()
        else:
            rangeBase = [0, 1, 2, 3]
        #and (Xpanel<250 and Ypanel>1200):
            ##self.rotatePanel()
        print('-------------------------------------')
        print('\nПоиск оптимальной установки детали.')
        print('Деталь :'+ str(self.panelNum if self.twins is None else self.twins))
        _hashsimbol = '#'
        print('\n------- старт расчета с позиции ', int(rangeBase[0]))
        for bp in rangeBase:
        
            # b = self.findPathSize(VARIANTPATH)
            # Ypanel=b.max.y-b.min.y
            # print(Ypanel)
            # print(machine.constraints.ymax_constr)
            # print(self.panelLength)
            if (machine.constraints.ymax_constr < self.panelWidth):
                print("\n--- Габарит Y={} больше ограничения {}. Смотрим следующий вариант".format(
                self.panelWidth, machine.constraints.ymax_constr))
                # print("EndPanel_rotate")
                self.rotatePanel()
                continue
            
            print('\n------- Позиция ', int(bp))
            if bp != rangeBase[0]:
                for fNmeForRename in self.start_optimist[previndexbp]:
                    #try:
                        os.rename(fNmeForRename,fNmeForRename[:-3]+'~bpp') # переименовать
                    #except:
                        #pass
            self.hashsimbol = 1
            self.startBP = bp
            for a in self.slots:
                a.cnc_key = False
            for a in self.millingTech:
                a.cnc_key = False
            for a in self.drills:
                a.cnc_key = False

            self.panel.overt = False # Признак перевернутости Для версии к3 6,5  надо проверить в 7,1
            #print 'self.panel.overt ', self.panel.overt
            # Если необходимо, проверка на габариты
            #Utiles.CheckGabs(self,panel,xmin,xmax,ymin,ymax,zmin,zmax)
            # Запоминаем пропилы и отверстия. Они нам потребуются
            # Выясняем какие пласти панели требуют обязательной обработки
            isPlaneA = (self.isBlindHoleA==True or self.isSlotsA==True or self.isCutsA) # Если по А есть пропил или глухое отверстие его выводить обязательно
            isPlaneF = (self.isBlindHoleF==True or self.isSlotsF==True or self.isCutsF) # Если по F есть пропил или глухое отверстие его выводить обязательно
            # print("isPlaneA",isPlaneA)
            # print("isPlaneF",isPlaneF)
            #hashsimbol='#' if isPlaneA and isPlaneF else '' # Знак # указываем для того, чтобы оператор видел, что обработка за несколько проходов
            if isPlaneA or (not isPlaneF): # Выводим сторону А  если есть условие обязательной обработки или по стороне F все пусто
                # Определяем возможность обработки за один установ и порождаем необходимое число установов для выполнения всех обработок пласти A
                
                self.hashsimbol = self.tech_cicle(self.hashsimbol, False, 'A')
                
            # Выключаем перевороты все делаем на станке. Братусь 12-10-2015 3) Переворотами деталей!!! 
            # Если есть глухие отверстия или пропилы с обратной стороны, надо еще перевернуть панель
            if isPlaneF: #(self.isBlindHoleF==True or self.isSlotsF==True):
                self.panelOverturn()
                # Переворачиваем относительно оси X
                self.hashsimbol = self.tech_cicle(self.hashsimbol, True, 'F')
            falsedrills = [a.cnc_key for a in self.drills].count(False)
            if falsedrills > 0:
                print('!!!!!!!!!!!!ОШИБКА!!!!!!!!!!!!!!!')
                print('Остались необработанными ', falsedrills , ' отверстия.')
                for t in  [(a.diameter, a.depth) if not a.cnc_key else None for a in self.drills]:
                    if t is  not None:
                        print(t[0], 'x', t[1])
                print('-------------------------------')
            # Если в текущем варианте были созданы файлы и их меньше , чем в прошлый раз.
            # Значит этот вариант оптимальнее предыдущего и предыдущие файлы следует удалить если их имена отличаются от новых
            
            if bp != rangeBase[0]:
                if ((len(self.start_optimist[bp]) < len(self.start_optimist[previndexbp]))
                    and len(self.start_optimist[bp])>0):
                    print('Новый вариант лучше старый удаляем.')
                    for fNmeForRemove in self.start_optimist[previndexbp]:
                            #try:
                                os.remove(fNmeForRemove[:-3]+'~bpp')
                            #except:
                                #pass
                    self.start_optimist[previndexbp] = []
                elif len(self.start_optimist[previndexbp])>0:
                    print('Старый вариант лучше новый удаляем.')
                    for fNmeForRemove in self.start_optimist[bp]:
                            try:
                                os.remove(fNmeForRemove)
                            except:
                                pass
                    for fNmeForRename in self.start_optimist[previndexbp]:
                        #try:
                            os.rename(fNmeForRename[:-3]+'~bpp', fNmeForRename) # переименовать
                        #except:
                            #pass
                    self.start_optimist[bp] = self.start_optimist[previndexbp]
            if len(self.start_optimist[bp]) == 1:
                print("Лучший вариант! Стартовая точка " + self.settings.machine_base_name[BASEPOINT])
                break
            if self.panel.overt: self.panelOverturn()
            # print("EndPanel_rotate_fin")
            self.rotatePanel()
            previndexbp = bp
        return

    def app_start_optimist(self, resultOutput):
        if resultOutput:
            self.start_optimist[self.startBP].append(self.cmdfileName)

    def panelOverturn(self):
        # Переворачиваем относительно оси X
        self.panel.Overturn(0)
        b =self.findPathSize(VARIANTPATH)
        #print b.max.x, b.min.x
        self.panel.Translate(machine.Vector2d(-b.min.x, -b.min.y))
        #b =self.findPathSize(VARIANTPATH)
        #print b.max.x, b.min.x
        self.panel.overt = True # Признак перевернутости Для версии к3 6,5  надо проверить в 7,1
        global BASEPOINT
        BASEPOINT = self._overt_basepoint[BASEPOINT]
        paths = self.panel.paths
        for path in paths:
            path.overt = True # Изменяется при перевороте панели
        mc = machine.constraints
        for d in self.drills:
            self.drill_revisia(d, mc)

    def Drilling(self, d):
        '''Сверловка. Пласти и торцы. Заполняем списки структурами для пластей и торцев'''
        if (self.Selobj == 0):  # Если это не выбранная панель
            return

        d.cnc_key = False # Признак вывода отверстия в файл ЧПУ
        d.panel.thiknessPanel = self.panel.thickness # Для версии к3 6,5
        mc = machine.constraints
        isTrough = Utiles.GetDrillTrough(d)
        Side=Utiles.GetDrillPlane(d)
        lDDM = self.get_list_torec_drillMachine(d, mc)  # для торцевых отверстий требуется уточнение по допустимым осям
        # print(lDDM)
        self.drill_revisia(d, mc)
#не заморачиваемся c 11-11-2015 см письма Братуся        # 
        # проверка на выполнимость по допустимым экстримальным координатам
        ps = machine.constraints.CheckConstraints(d, listDrillDimMashine=lDDM)
        # print(ps)
        #ps=('AE', 'AC', 'AB', 'AD','FE', 'FC', 'FB', 'FD')
        self.get_drill_brosers(d)
        if len(ps) > 0:
            d.list_true_posits = ps
            #self.drill_revisia(d, mc)
            if isTrough:
                self.isTrough=True
            elif (Side=="F"):
                self.isBlindHoleF=True
            elif (Side=="A"):
                self.isBlindHoleA=True
            self.drills.append(d)
        else:
            print('''---!!!!!!!!!---''')
            print('''Отверстие не может быть выполнено по допустимым экстримальным координатам''')
            print('     d x h =' + str(d.diameter) + ' x ' + str(d.depth))
            print('     координаты центра  X Y Z = ' + str(d.position.x) + '  ' + str(d.position.y)  + str(d.position.z))
            print('''---!!!!!!!!!---''')
        return

    def get_list_torec_drillMachine(self, d, mc):
        '''список допустимых торцев и пластей сверловки на станке mc для отверстия d'''
        tt = []
        for dr in  mc.tools_dims['drilling']:
            if  d.diameter in  dr['DIA'] :
                axl = dr['AXE']
                tt.extend(list(axl))
        return tt

    def get_drill_brosers(self, d):
        '''Заполняет список индексов "братьев отверстий". Тех которые принадлежат тому же крепежу и той же панели. Например эксцентриковая стяжка.
        Возвращает список кортежеей вида
        d.brothers
        [2]
        для штока вернет id отверстия эксентрика
        а для эксцентрика вернет id отверстия штока.
        Есть мнение, что сверлить их нужно вместе, за один установ
        '''
        SQL_STR='''SELECT THoles.HolePos
        FROM THoles INNER JOIN TElems ON THoles.HolderPos = TElems.UnitPos
        WHERE ((Not (THoles.HolePos)='''+str(d.id.handle)+''') AND ((TElems.UnitPos) In (SELECT TElems.UnitPos
        FROM THoles INNER JOIN TElems ON THoles.HolderPos = TElems.UnitPos
        WHERE (((THoles.UnitPos)='''+str(self.panel.id.handle)+''') AND ((THoles.HolePos)='''+str(d.id.handle)+'''))
        ORDER BY THoles.UnitPos, THoles.HolePos)) AND ((THoles.UnitPos)='''+str(self.panel.id.handle)+'''))
        ORDER BY THoles.HolePos, THoles.UnitPos;'''
        cnxn, cursor, recordset = self.odbc_conn(SQL_STR)
        d.brothers = [a[0] for a in recordset]
        self.odbc_close(cursor, cnxn)


    def Slot(self, s):
        '''Пропилы. Заполняем списки структурами пропилов'''
        self.slots.append(s)
        s.cnc_key = False # Признак вывода пропила в файл ЧПУ
        # Если пропил по стороне F
        if (s.is_plane==False):
            self.isSlotsF=True
        else:
            self.isSlotsA=True
        if (Utiles.GetSlotDirection(s)!="X"):
            self.isSlotsY=True
        return

    def Contour(self):
        '''Контура. Заполняем списки контурами для фрезеровки'''
        # Получаем список контуров панели.
        paths = self.panel.paths
        # Проверяем. Если контур один и состоит из 4 отрезков, то фрезеровать не надо
        for path in paths:
            path.cnc_key = False # Признак вывода в файл ЧПУ
            path.overt = False # Изменяется при перевороте панели

            for s in path.segments:
                s.path.overt = False

            segments=path.segments

            if path.is_plane_path:
                if path.is_tcuts:

                    # Это место надо менять теперь это может быть вырез в панели, который надо обрабатывать
                    # path.is_plane_path Признак, что контур относится к полотну панели, а не к панели
                    # path.is_tcuts Контур из TCuts
                    # path.cutpos CutPos выреза из TCuts, по которому получен контур

                    cnxn, cursor, recordset = self.odbc_conn(SQL_STR='''SELECT TCuts.Depth, TCuts.ExtrZ FROM TPaths
                    INNER JOIN TCuts ON (TPaths.CutPos = TCuts.CutPos) AND (TPaths.PanelPos = TCuts.UnitPos)
                    WHERE (((TCuts.UnitPos)='''+str(self.panel.id.handle)+''') AND ((TPaths.PathID)='''+str(path.id.handle)+'''));''')
                    path.cuts = recordset
                    if (path.cuts[0][0] < 0):
                        self.isCutsF = True
                    elif (path.cuts[0][0] > 0):
                        self.isCutsA = True
                    self.odbc_close(cursor, cnxn)
                    self.millingTech.append(path)
                    continue
                else:
                    bbox=path.bounding_box
                    if (len(segments)!=4):    # Если контур состоит не из 4-х отрезков, то он заведомо кривой. Его добавляем
                        self.millingTech.append(path)
                        continue
                    for segment in segments:
                        if (type(segment)!=machine.Line):
                            self.millingTech.append(path)
                            break
                        else:
                            # Если линия не горизонтальная и не вертикальная - добавляем контур
                            Xst = segment.start_pt.x
                            Yst = segment.start_pt.y
                            Xen = segment.end_pt.x
                            Yen = segment.end_pt.y
                            if (abs(Xst-Xen)>eps_d and abs(Yst-Yen)>eps_d):
                                self.millingTech.append(path)
                                break
                            # Cравниваем с элементами BoundingBox Если хотя бы один конец не на bbox - добавляем контур
                            if ((abs(Xst-bbox.min.x)>eps_d or abs(Xst-bbox.max.x)>eps_d) or
                                (abs(Xen-bbox.min.x)>eps_d or abs(Xen-bbox.max.x)>eps_d) or
                                (abs(Yst-bbox.min.y)>eps_d or abs(Yst-bbox.max.y)>eps_d) or
                                (abs(Yen-bbox.min.y)>eps_d or abs(Yen-bbox.max.y)>eps_d)):
                                self.millingTechApp(path)
                                break
        return

    def odbc_close(self, cursor, cnxn):
        '''Закрывает соединение с базой'''
        cursor.close()
        cnxn.commit()
        cnxn.close()

    def odbc_conn(self, SQL_STR):
        '''Создает соединение с базой self.settings.database_name
        Выполняет запрос к базе'''
        cnxn = pyodbc.connect('Driver={Microsoft Access Driver (*.mdb)};Dbq='+self.settings.database_name+';Uid=;Pwd=;')
        cursor = cnxn.cursor()
        cursor.execute(SQL_STR )
        recordset = cursor.fetchall()
        return cnxn, cursor, recordset

    def millingTechApp(self, path):
        self.millingTech.append(path)

    def Milling(self, m, s):
        '''Фрезеровки. Заполняем списки фрезеровок'''
        return

    def Filletting(self, f, s):
        #print('----Кромка толщиной ', ' мм по сегменту----')
        pass

#--------------------------------------------------------------------------------------------------


#--------------------------------------------------------------------
    def RevisiaSegmentsToPath(self, conl, overt):
        '''Упорядочивание элементов контуров'''

        def _getIndexMT(self, con, iP, iS):
            t = 0
            for j, ii in  enumerate(self.millingTech):
                if  ii.id.handle == con[iP][iS].path_H.id.handle:
                    t = j
                    break
            return t

        def _getExtrPoint(iP, iS, con):
            Xst = round(con[iP][iS].start_pt.x,3)
            Yst = round(con[iP][iS].start_pt.y,3)
            Xen = round(con[iP][iS].end_pt.x,3)
            Yen = round(con[iP][iS].end_pt.y,3)
            return Xst, Yst, Xen, Yen

        Inf = False  # Вывод отладочной информации в окно
        singleSetup = [True] # Обработка за один установ
        if type(conl[0])==list :
            con = conl
        else:
            con = []
            con.append(conl)
        # dictG = {}
        dictw = {}

        mc = machine.constraints.tools_dims['milling'][0]
        thkns =2.5  #  Толщина кромки
        b =self.findPathSize(VARIANTPATH) #self.panel.paths[VARIANTPATH].bounding_box  #  Без учета кромок и подрезов
        maxX = min(round(b.max.x,3), mc['MAX_X_VAL'])
        minX = max(round(b.min.x,3), mc['MIN_X_VAL'])
        maxY = min(round(b.max.y,3), mc['MAX_Y_VAL'])
        minY = max(round(b.min.y,3), mc['MIN_Y_VAL'])
        if Inf:
            print("b.max.x= ",maxX)
            print("b.min.x= ",minX)
            print("b.max.y= ",maxY)
            print("b.min.y= ",minY)
        conW = list(range(len(con)))  # Список индексов контуров для обработок
        indexMillingTech = 0

        for iP in conW:
            if Inf: print(iP)
            segW = [False for a in con[iP]]  # Создаем список обработок на сегменты

            segmentsOutGab = []
            for iS in range(len(con[iP])):
                Xst, Yst, Xen, Yen = _getExtrPoint(iP, iS, con)
                log = (True in [(v>maxX) for v in [Xst, Xen]]) or (True in [(v>maxY) for v in [Yst, Yen]])
                segmentsOutGab.append(log)

            for iS in range(len(con[iP])):
                try:
                    if Inf: print("iS= ",iS+1)
                    Xst, Yst, Xen, Yen = _getExtrPoint(iP, iS, con)
                    indexMillingTech = _getIndexMT(self, con,iP, iS )
                    if Inf:
                        print("Xst= ",Xst)
                        print("Xen= ",Xen)
                        print("Yst= ",Yst)
                        print("Yen= ",Yen)
                    while len(self.millingTech[indexMillingTech].segments_cnc_key) < len(segW):
                        self.millingTech[indexMillingTech].segments_cnc_key.append(True)
    # '''Находим угол между касательными двух соседних элементов контура'''
                    if segmentsOutGab[iS]:
                        print('--Сегмент за пределами зоны обработки--')
                        continue
                    else:
                        self.millingTech[indexMillingTech].segments_cnc_key[iS] = segW[iS]
                        pass
                    if con[iP][iS].path_H.id.handle > 1:
                        segW[iS] = True # Если это вырез сквозной или нет неважно- метим на обработку
                    else:
                        v1 =con[iP][iS-1].tangent(0 if overt else 1)
                        v2 =con[iP][iS].tangent(1 if overt else 0)
                        cs =self.angleGet(v1,v2)
                        if Inf: print("угол между ", iS , " и ", iS+1, "= " , cs)
                        if type(con[iP][iS]) == machine.Line:
                            if not segW[iS]:  # При уже наложенной обработке пропускаем
                                PlaneX =Xst-Xen
                                PlaneY =Yst-Yen
                                if PlaneX == 0: # В плоскости Y
                                    if Inf: print("В плоскости Y")
                                    if abs(Xst-minX) > thkns < abs(Xst-maxX):
                                        segW[iS] = True
                                        if Inf: print("Добавляем обработку")

                                if PlaneY == 0: # В плоскости X
                                    if Inf:
                                        print("В плоскости X")
                                        print("Yst-maxY=",abs(Yst-maxY))
                                        print("Yst-minY=",abs(Yst-minY))
                                    if abs(Yst-minY) > thkns < abs(Yst-maxY):
                                    #if abs(Yst-minY) > thkns and abs(Yst-maxY) > thkns:
                                        segW[iS] = True
                                        if Inf: print("Добавляем обработку")

                                if PlaneY != 0 and PlaneX != 0 :
                                    if Inf: print("Ни горизонтальна, ни вертикальна")
                                    segW[iS] = True
                                    if Inf: print("Добавляем обработку")

                                if type(con[iP][iS-1]) == machine.Arc:  #  Смотрим скругление ли предыдущий контур
                                    if Inf: print("Анализ предыдущего - Скругление")
                                    AngDir =con[iP][iS-1].orientation
                                    # if self.Ovtrn:
                                        # cs =180-cs
                                        # print "Ovrtn.cs=", cs
                                    if (AngDir == 0 or AngDir == 1) and (cs <= 45 or cs == 180) :
                                        segW[iS] =True #  Метим в списке на обработку
                                        if Inf: print("Добавляем обработку на линию")

                        if type(con[iP][iS]) == machine.Arc:
                            segW[iS] =True #  Метим в списке на обработку
                            if Inf:
                                print("Xen=", Xen)
                                print("Yen=", Yen)
                                print("start=", degrees(con[iP][iS].start))
                                print("end=", degrees(con[iP][iS].end))

                            # Ищем направление дуги AngDir если
                            AngDir =con[iP][iS].orientation
                            if type(con[iP][iS-1]) == machine.Line:  #  Смотрим линия ли предыдущий контур
                                if Inf: print("Анализ предыдущего контура - Линия")
                                # if self.Ovtrn:
                                    # cs =180-cs
                                    # print "Ovrtn.cs=", cs
                                if (AngDir == 0 or AngDir == 1) and (cs <= 45 or cs == 180):
                                    segW[iS-1] = True if not segmentsOutGab[iS-1] else False #  Метим в списке на обработку
                                    if Inf: print("Добавляем обработку")

                    segment = con[iP][iS]
                    isWorkIds = 'work_ids' in list(segment.__dict__.keys())
                    if isWorkIds:
                        lenm = len(segment.work_ids)
                        
                        for i in range(lenm):
                            numW = segment.work_ids[i].handle # ID обработки
                            if numW not in dictw and type(segment.works[i]) == machine.Milling:
                                dictw.update({numW : []})
                except:
                    pass
            conW[iP] = segW
            singleSetup.append(not (True in  [log for log in self.millingTech[indexMillingTech].segments_cnc_key]))
        return conW, singleSetup

    def angleGet(self, v1, v2):
        cc = round((v1%v2)/(v1.length()*v2.length()),3)
        cs = round(degrees(math.acos(cc)),2)
        return cs

    # def readerContours(self, panel):
        # "Чтение внешнего контура и сквозных вырезов. Подготовка."
        # #print "readerContours"
        # p= panel.paths # Список контуров панели
        # con = []  #  Список для контуров
        # #i=0
        # for a in p:
            # #print i
            # #print a.is_tcuts
            # #print a.is_plane_path
            # if (not(a.is_tcuts) and a.is_plane_path) or (a.is_tcuts and not(a.is_plane_path)):
                # segments = a.segments
                # ttt=len(segments)
                # if ttt!=0:
                    # if type(segments[0]) == machine.Circle:
                        # r=segments[0].path
                        # segments = segments[0].Divide(0.5)
                        # for s in segments:
                            # s.path_H=r
                        # for sg in segments:
                            # Utiles.SegmentReverse(sg)
                    # elif ttt==2:
                        # s0=segments[0]
                        # s1=segments[1]
                        # if  s0== machine.Arc and  s1== machine.Arc and s0.start_pt==s1.end_pt:
                            # for sg in segments:
                                # Utiles.SegmentReverse(sg)
                # segm = []  #  Инициализация списка сегментов
                # for seg1 in segments:
                    # segm.append(seg1)
                    # #print seg1.params
                    # #print seg1.work_ids
                    # #print seg1.works
                # con.append(segm)
            # #i+=1

    # # На выходе список контуров con со списками составляющих сегментов seg
    # # Доступ по индексу con [i] [j], где i - номер контура, j - номер сегмента

        # #if not self.keyFrez: #  Обработка должна накладываться на одну сторону
            # #self.keyFrez = True
            # #con =self.FilterBetweenCNC(con) # Достаточно один раз, так как меняется только направление)
        # return con

    def findPathSize(self, VARIANTPATH):
        '''находит контур с кромкой или без кромки
        VARIANTPATH   0-без кромки 1-с кромкой
        bounding_box нужного контура
        '''
        lSizePath = []
        dSizePath = {}
        lBand = True if VARIANTPATH ==0 else False
        for ph in self.panel.paths:
            if not ph.is_tcuts and ph.is_plane_path == lBand: #
                b=ph.bounding_box
                X, Y = self.getXY_bounding_box(b)
                S = X * Y
                dSizePath[S]=b
        lSizePath =  list(dSizePath.keys())
        lSizePath.sort(reverse=True)
        result = []
        if len(lSizePath) > 0:
            result = dSizePath[lSizePath[0]]
        return result

    def getXY_bounding_box(self, b):
        '''возвращает габаритные размеры объекта b bounding_box2D'''
        X=b.max.x-b.min.x
        Y=b.max.y-b.min.y
        return X, Y

# global boa
# boa=Boa()
