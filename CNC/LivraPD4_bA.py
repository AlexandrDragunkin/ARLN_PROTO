# -*- coding: utf-8 -*-
# A3.30 ARLINE
#import wingdbstub
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


import machine
import LIVRA_AR as CurM # импортируем модуль конкретного станка
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
        self.num_tdcode=int(1) # счетчик номеров обработок
        self.num_point = int(0)
        
        #---------------------        
        self.header='''BEGIN ID CID3
  '=   
  REL= 3.10
  AXIS= x+,y-,z-
END ID
'''

        self.variables='''BEGIN MAINDATA
  LX= %.2f
  LY= %.2f
  LZ= %.2f
  OX= 0.00
  OY= 0.00
  OZ= 0.00
END MAINDATA
BEGIN PARAMETRIC SECTION

[ 0. ]  LAVORAZIONE N0 ( 
          LPX = %.1f NOP "Width"
        , LPY = %.1f NOP "Height"
        , LPZ = %.1f NOP "Thickness"
         ) SIST_RIF EOS EOS 
'''

        self.profilo = '''[  %i.0 ] PROFILO ON START FUORI SINISTRA
[  %i.1 ] PROFILO  +$%i EOS'''
        
        self.s_layer = ''
        self.add_s_layer = lambda s: '$' + str(s) + ' '
        self.layer = '''       
[  1.0 ] LAYER ON START 1 "WRK" COLORE 3
[  1.1 ] LAYER %s EOS
[  2.0 ] LAYER ON START 2 "DOC" COLORE 2
[  2.1 ] LAYER  EOS
        '''
        
        self.punto = '''
[  0.0 ] PUNTO [ 0,0,0 ]
[  0.1 ] CREA_SPACE %.1f %.1f %.1f
[  1.0 ] CREA_LAB FRONTALE'''        
        
        self.crf = '''[  %i.0 ] ($P%i) CRF CENTRO [%.1f,%.1f,%.1f] RAGGIO %.1f'''
        self.l_crf = []
        
        self.crf_e = '''[  %i.0 ] CREA_LAB FRONTALE



[  999.  ] FINE_MACRO
'''
        
        self.l_cat = []        
        self.cat = '''$$$ [%i] #NUM_CAT=1,#ID_TOOLNAME=*,#PRIORITY=*,#WORKSIDE=*,#TYPEDRILL=*,#DWNSPEED=*,#RIFDRILL=*,#TYPE=%i,#AR=%s,#AZ=%s,#DIAM=%f,#ID_DEPTH=%f'''
        
        self.cat_e = '''

END PARAMETRIC SECTION
'''
        #---------------------
        
        self.program="[PROGRAM]"
        self.tdcodes='''[TDCODES]
VER=1'''
        self.pcf="[PCF]"
        
        self.tooling="[TOOLING]"
        
        self.subprogs="[SUBPROGS]"
        
        self.drill= '''
        '''
        
        
        #'''@ %s, "TDCODE%i", "" : %i, "%i", %f, %f, %f, %f, %f, %i, %s, %f, %f, %f, %f, %f, %i, "%s", %i, %f, %f, %i, %i, %f, %f, %f, %f, %i, %i, %i, %f, %i, %i, %i, "%s", %f, "%s", "%s", %i, %i, %i, %i, %i, "%s", %f, %i, %i, %i, %i, "%s", "%s", "%s", %i'''
 

        # Вариант для автоматического выбора сверла по диаметру и типу
        self.drill_tdcodes = '''(MST)<LN=1,NJ=TDCODE%i,TYW=1,NT=1,>
(GEN)<WT=1,DL=1,>
(TOO)<DI=%f,SP=%f,CL=0,COD=----------,RO=-1,TY=%i,>'''
        # Вариант для  выбора сверла по конкретному коду COD и типу 
        self.drill_tdcodes_cod = '''(MST)<LN=1,NJ=TDCODE%i,TYW=1,NT=1,>
(GEN)<WT=1,DL=1,>
(TOO)<DI=%f,SP=%f,CL=0,COD=%s,RO=-1,TY=%i,>'''        
        



# Здесь мы задаем методы для вывода
    def CRF_Command(self):
        for e in self.l_crf:
            print(self.crf % e, file=self.OutputFile)
        print(self.crf_e % (self.num_tdcode+1), file=self.OutputFile)
    
    def CAT_Command(self):
        for e in self.l_cat:
            print(self.cat % e, file=self.OutputFile)
        print(self.cat_e,  file=self.OutputFile)
            
    def LayerCommand(self):
        print(self.layer % (self.s_layer), file=self.OutputFile)
        return True
    
    def PuntoCommand(self):
        print(self.punto % (self.panelLength, self.panelWidth, self.panelThickness), file=self.OutputFile)
        return True

    def DrillingCommand(self, num, drill):
        '''Вывод информации об отверстии в файл

        num - порядковый номер отверстия
        drill - отверстие
        '''
        result_DrillingCommand=False
        self.num_tdcode +=1 # Увеличиваем значение счетчика на 1
        self.num_point += 1
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
        b=Boa()
        side=Utiles.GetDrillPlane(drill)
        isTrough = Utiles.GetDrillTrough(drill)
        siden=b.GetSideNum(side)
        bb = drill.panel.bounding_box
        Xpanel=bb.max.x-bb.min.x
        Ypanel=bb.max.y-bb.min.y
        crn=4
        if isTrough:
            z = drill.panel.thickness
        
            
        if machine.constraints.d_trueposits[BASEPOINT] in drill.list_true_posits:
            # Проверяем возможно ли выполнить это отверстие (список доступных установов drill.list_true_posits) в текущей позиции BASEPOINT
            if (siden==0):
                crn=4
            if (siden==5):  # Типа, низовой сверловки нет
                crn=1
            if (siden==1): # C
                crn=2
                #x=y
                #y=z
            if (siden==2): #E
                crn=4
                #y=z
            if (siden==3): # B
                crn=3
                #x=y
                #y=z
            if (siden==4):  # D
                crn=1
                #y=z
            #z=0
            typeinstr = {'TH':2,'BL':1,'':1,'SV':3, }
            
            if 'typ_cod_tool' in drill.__dict__.keys():
                pass
            #if d.typ_cod_tool = mc.typ_cod_tool
            #d.cod_tool
                self._Drill(0, self.num_tdcode, x,y,z,siden,h,d, isTrough, crn, typeinstr=drill.typ_cod_tool, COD=drill.cod_tool)
            else:
                self._Drill(1, self.num_tdcode, x,y,z,siden,h,d, isTrough, crn, typeinstr=typeinstr[drill.typetool])
            drill.cnc_key = True # признак вывода отверстия в файл
            result_DrillingCommand=True

        return result_DrillingCommand

    def _Drill(self, v_comand, num_tdcode, x,y,z,side,h,diam,isTrough,crn=4, typeinstr=0, COD="----------"):
        thr = 0
        if (side==0 or side==5):
            dCRN = {1: 4, 4: 1, 2: 3, 3: 2}
            b="BV"  # Сверление вертикальное
            AZ = '270.000000'
            AR = '*'
            if isTrough:
                typeinstr = 2 
                h += 8
                if h > 40:
                    h = 40
                thr = 1
                if side == 5:
                    side = 0
                    crn = dCRN[crn]
            else:
                if h > 3 and side == 0:
                    h = 12.5 # Для всех глухих пластевых отверстий . сделал по согласованию со Стасом 2014/12/17
                    if diam==10. :
                        #typeinstr = 2 # SVASTA  есть только комбинированная 
                        h = 14
                    if h<=3 and diam==5:
                        typeinstr = 2 # сквозное для наколки
        else:
            b="BH"  # Сверление горизонтальное
            AZ = '*'
            dk = {1: '*', 2: '90.000000', 3: '180.000000', 4: '270.000000'}
            AR = dk[side]
        ty = typeinstr
        if thr == 1:
            pass
        ei = self.num_tdcode
        eei = self.num_point
        print(self.profilo % (eei, eei, ei), file=self.OutputFile)
        self.s_layer += self.add_s_layer(ei)
        self.l_crf.append((self.num_point+1, self.num_point, self.panelLength-x,self.panelWidth-y, z, diam/2 ))
        # '''$$$ [%i] #NUM_CAT=1,#AR=*,#ID_TOOLNAME=*,#PRIORITY=*,#WORKSIDE=*,#TYPEDRILL=*,#DWNSPEED=*,#TYPE=%i,#AZ=%f,#DIAM=%f,#ID_DEPTH=%f,#RIFDRILL=%i'''
        self.l_cat.append((self.num_point, ty, AR, AZ, diam, h))
        #self.dict_section['[PROGRAM]'].append((self.drill,(b,num_tdcode,side,crn,x,y,z,h,diam,thr,rty,dx,dy,r,a,da,npr,iso,opt,az,ar,ap,cka,xrc,yrc,arp,lrp,er,md,cow,a21,tos,vtr,s21,id,azs,mac,tnm,ttp,tcl,rsp,ios,wsp,spi,dds,dsp,bfc,shp,ea21,cen,agg,b,rps)))
        #if COD=="----------":
            #self.dict_section['[TDCODES]'].append((self.drill_tdcodes,(num_tdcode,diam, diam,ty)))
        #else:
            #self.dict_section['[TDCODES]'].append((self.drill_tdcodes_cod,(num_tdcode,diam, diam, COD, ty)))

        # Для случая сквозного отверстия рисуем крестик.
        #if thr == 1:
            #self.num_tdcode +=1 # Увеличиваем значение счетчика на 1
            ##print(self.drill_th_geo % (self.num_tdcode, crn, x, y, x, y), file=self.OutputFile)
            #pass

        return

    def DataHeadCommand(self, x, y, z):
        '''Вывод информации в заголовок файл'''
        print(self.header, file=self.OutputFile)
        print(self.variables % (x,y,z,x,y,z ), file=self.OutputFile)
        return


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
        ''' Конкструктор класса'''
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
        self.writer = Writer()                    # Класс для вывода информации в файл

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

    def CreateCmdfile(self,post):
        '''Создаем файл с управляющей программой
        4) Запись информации о кромке, направление текстуры и присадка по стороне A или F. «(GG!GP!G)-(A)» Обозначения
        
        «L» - Кромка толщиной 0.4 мм.
        
        «S» - Кромка толщиной 0.6 мм.
        
        «G» - Кромка толщиной 1 мм.
        
        «V» - Кромка толщиной 2 мм.
        
        «P» - Обозначает паз.
        
        «!» - Паз снизу со стороны присадки
        
        «^» - Паз сверху с обратной стороны от присадки
        
        «-» - Текстура по размеру X
        
        «^» - Текстура по размеру Y
        
        «A» - Присадка выполняется по стороне (F)
        
        «F» - Присадка выполняется по стороне (A)
        
        5) Артикул детали
        
        6) Количество
        
        7) Выполненное количество
        
        8) Размер по оси X
        
        9) Размер по оси Y
        
        10) Размер по оси Z
        
        11) Путь к исполнительному файлу без расширения.
        
        Например
        
        к детали 00 «Тест_K3\Livra-5\_960x315x16_00_(GG!GP!G)-(A)(1)»
        
        к детали 11 «Тест_K3\Livra-5\ W908_Белый_ST2_688x268x16_11_(____)-(A)(1)»
        
        к детали 15 «Тест_K3\Livra-5\ W908_Белый_ST2_848x535x16_15_((@-X))_(G___)-(A)(1)»
        

        
        post - имя файла'''
        
        fname=post+".pd4"
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

    def GetSideNum(self,sideName):
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
        #self.writer.BeginProgram()
        result_drilling = self.writerDrillingCommand(self.drills)
        self.writer.LayerCommand()
        self.writer.PuntoCommand()
        self.writer.CRF_Command()
        self.writer.CAT_Command()
        
        return  result_drilling



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

        # Получаем имя файла
        index = self.name_prog_calc( machine,eps_d,postfix, hashsimbol)

        if (self.panelNum==-1 or
            not ((False in [d.cnc_key for d in self.drills]))):
            resOutput = False
        else:
            # Создаем файл
            self.CreateCmdfile(index)
            # Пишем в файл шапку
            self.CreateCmdfileHeading()
            # Пишем в файл по очереди все секции
            result = self.CreateCmdfileProgram()
            #self.CreateCmdfileVBScript()
            #self.CreateCmdfileMacroData()
            #self.CreateCmdfileTDCodes()
            #self.CreateCmdfilePCF()
            #self.CreateCmdfileTooling()
            #self.CreateCmdfileSubProgs()
            self.writer.panelName=self.panelName
            if result:
                print("Панель № ",self.panelNum, " Запись в файл",index,".pd4")
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
        '''поворачивает панель на 90 градусов против часовой стрелки и сдвигает правильным образом в точку базы изменяет имя положения базовой точки'''

        def _aposition(self):
            if self.aposition < 360:
                self.aposition += 90
            else:
                self.aposition = 0
        
                
        dChtextureDir = {0: 90, 90: 0, -90: 0, 270: 0, 180: 90, -180: 90, 360: 90, -360: 90,}
        b = self.findPathSize(VARIANTPATH) #self.panel.bounding_box

        
        self.panel.Translate(machine.Vector2d(-b.min.x,-b.min.y))
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
        self.writer.num_tdcode=int(1) # счетчик номеров обработок
        self.writer.num_point = int(0)
        self.writer.l_crf = []
        self.writer.l_cat = []
        self.panel.textureDir = dChtextureDir[round(self.panel.textureDir , 1)]
        #self.writer.texture_dir_value = self.panel.textureDir
        global BASEPOINT
        BASEPOINT = BASEPOINT + 1 if BASEPOINT not in [3, 7] else BASEPOINT - 3
        mc = machine.constraints
        for d in self.drills:
            self.drill_revisia(d, mc)

    def drill_revisia(self, d, mc):
        Side=Utiles.GetDrillPlane(d)
        CurM.change_MinMaxXY_Space(mc, d)
        d.typetool=mc.typetool
        list_property_mc = list(mc.__dict__.keys())
        if 'typ_cod_tool' in list_property_mc:
            d.typ_cod_tool = mc.typ_cod_tool
            d.cod_tool = mc.cod_tool


    def StartPanel(self, panel):
        '''Метод вызывается автоматически перед началом обработки каждой панели'''
        self.aposition = 0
        self.start_optimist = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []} # Контролер числа установов при стартовой базовой точке
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
        for a in self.panel.attributes:
            if a.name=='Selobj':
                self.Selobj = int(a.value)
            if a.name=='NumOrder':
                self.NumOrder = str(a.value)
            if a.name=='ListTwins':
                self.twins = str(a.value)
            if a.name == 'GDetNumber':
                self.gnumdet = str(a.value)
        global BASEPOINT
        BASEPOINT = 0 # Номер базы стартовый(0,1,2,3 <-для стороны A 4,5,6,7 -для стороны F )
        if (self.Selobj == 0):  # Если это не выбранная панель, то не фиг ее обрабатывать
            return False
        # (Анализируем габарит панели и поворачиваем ее длинной стороной вдоль X) так делать нельзя. Здесь нельзя только после того как считали все обработки, вот тогда можно. Крутить надо в EndPanel
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
        self.writer.panelThickness = self.panelThickness

        self.panelNum = panel.common_pos if self.gnumdet == 0 else self.gnumdet
        # Собираем контура
        self.Contour()
        return True



    def writerDrillingCommand(self, drillTuple):
        '''Подоготавливает к выводу отверстия
        drillTuple - список отверстий в данной панели'''
        result = []
        #self.writer.geoPlastNameCommand()
        #self.writer.geoDirTextureCommand()
        for d in drillTuple:
            SideS=Utiles.GetDrillPlane(d)
            SideNum=self.GetSideNum(SideS)
            #print SideS,' ',' ',SideNum,[a.cnc_key for a in drillTuple]
            if d.diameter == 5.0:
                pass
            if (SideNum<0 or SideNum==5) and  not Utiles.GetDrillTrough(d): # Если сторона не определена,или это стороны F, отверстие не выводим, если сквозное , то выводим
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
        resultOutput = self.writeOutputFile(self.settings.machine_base_name[BASEPOINT],hashsimbol)
        if resultOutput:
            hashsimbol +=1
        self.app_start_optimist(resultOutput)
        for i in range(3): # Крутим панель три раза и пытаемся обработать
            self.rotatePanel()
            
            resultOutput = self.writeOutputFile(self.settings.machine_base_name[BASEPOINT],hashsimbol)
            if resultOutput:
                hashsimbol +=1            
            self.app_start_optimist(resultOutput)
        self.rotatePanel() # Возвращаем в исходное состояние
        return hashsimbol

    def EndPanel(self):
        '''Функция вызывается в конце обработки каждой панели'''
        if (self.Selobj == 0):  # Если это не выбранная панель
            return
        if not self.structureOK:  # Если какие то проблемы в структуре панели
            return
      
        if True in [s.width>4. for s in self.slots] or len(self.slots) > 1:
            print('Панель номер ', self.panelNum, ' обработана быть не может! Широкий паз или пазов больше 1')
            return
        if len(self.slots) == 1:
            if self.slots[0].width == 4:
                if (abs(self.slots[0].start.y-self.slots[0].end.y) < 0.5):
                    if self.panel.size.size_x - abs(self.slots[0].end.x-self.slots[0].start.x) < 1:
                        if abs(self.slots[0].start.y ) < 19 or  abs(self.slots[0].start.y - self.panel.size.size_y ) < 19:
                            pass
                        else:
                            print('Панель номер ', self.panelNum, ' обработана быть не может! Паз виноват. Положение центра дальше 18 от края')
                            return
                    else:
                        print('Панель номер ', self.panelNum, ' обработана быть не может! Паз виноват. Меньше панели')
                        return                    
                elif  (abs(self.slots[0].start.x-self.slots[0].end.x) < 0.5):
                    if self.panel.size.size_y - abs(self.slots[0].end.y-self.slots[0].start.y) < 1:
                        if abs(self.slots[0].start.x ) <19 or  abs(self.slots[0].start.x - self.panel.size.size_x) < 19:
                            pass
                        else:
                            print('Панель номер ', self.panelNum, ' обработана быть не может! Паз виноват. Положение центра дальше 18 от края')
                            return
                    else:
                        print('Панель номер ', self.panelNum, ' обработана быть не может! Паз виноват. Меньше панели ')
                        return                    
                else:
                    pass
                               
        if self.panel.curve_path:
            print('Панель номер ', self.panelNum, ' обработана быть не может! Криволинейная.')
            return            
        if self.panel.name.lower().count('фасад'):
            print('Панель номер ', self.panelNum, ' обработана быть не может! Фасад')
            return
        
        b = self.findPathSize(VARIANTPATH)
        Ypanel=b.max.y-b.min.y
        Xpanel=b.max.x-b.min.x

        if (Xpanel<Ypanel):
            rangeBase = [ 3, 0, 1, 2]
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
        for bp in rangeBase:
            print('\n------- старт расчета с позиции ' + str(int(bp)))
            if bp != rangeBase[0]:
                for fNmeForRename in self.start_optimist[previndexbp]:
                    #try:
                        os.rename(fNmeForRename,fNmeForRename[:-3]+'~pd4') # переименовать
                    #except:
                        #pass
            self.hashsimbol = 1 # Знак  указываем для того, чтобы оператор видел, что обработка за несколько проходов

            self.bandPunktion = {}
            self.startBP = bp
            #for a in self.slots:
                #a.cnc_key = False
            #for a in self.millingTech:
                #a.cnc_key = False
            for a in self.drills:
                a.cnc_key = False

            self.panel.overt = False # Признак перевернутости Для версии к3 6,5  надо проверить в 7,1
            #print 'self.panel.overt ', self.panel.overt
            # Если необходимо, проверка на габариты
            #Utiles.CheckGabs(self,panel,xmin,xmax,ymin,ymax,zmin,zmax)
            # Запоминаем пропилы и отверстия. Они нам потребуются
            # Выясняем какие пласти панели требуют обязательной обработки
            isPlaneA = (self.isBlindHoleA==True) # Если по А есть пропил или глухое отверстие его выводить обязательно
            isPlaneF = (self.isBlindHoleF==True) # Если по F есть пропил или глухое отверстие его выводить обязательно

            if isPlaneA or (not isPlaneF): # Выводим сторону А  если есть условие обязательной обработки или по стороне F все пусто
                # Определяем возможность обработки за один установ и поррождаем необходимое число установов для выполнения всех обработок пласти A

                self.hashsimbol = self.tech_cicle( self.hashsimbol, False, 'A')

            # Выключаем перевороты все делаем на станке. Братусь 12-10-2015 3) Переворотами деталей!!! 
            # Если есть глухие отверстия или пропилы с обратной стороны, надо еще перевернуть панель
            if isPlaneF: #(self.isBlindHoleF==True or self.isSlotsF==True):
                self.panelOverturn()
                # Переворачиваем относительно оси X
                self.hashsimbol = self.tech_cicle(self.hashsimbol,True, 'F')
            falsedrills = [a.cnc_key for a in self.drills].count(False)
            if falsedrills > 0:
                print('!!!!!!!!!!!!ОШИБКА!!!!!!!!!!!!!!!')
                print('Остались необработанными ', falsedrills , ' отверстия.')
                for t in  [(a.diameter, a.depth) if not a.cnc_key else None for a in self.drills]:
                    if t is  not None:
                        print(t[0], 'x', t[1])
                print('-------------------------------')
            # Если в текущем варианте были созданы файлы и их меньше , чем в прошлый раз. Значит этот вариант оптимальнее предыдущего и предыдущие файлы следует удалить если их имена отличаются от новых

            if bp != rangeBase[0]:
                if ((len(self.start_optimist[bp]) < len(self.start_optimist[previndexbp]))
                    and len(self.start_optimist[bp])>0):
                    print('Новый вариант лучше старый удаляем.')
                    for fNmeForRemove in self.start_optimist[previndexbp]:
                            #try:
                                os.remove(fNmeForRemove[:-3]+'~pd4')
                            #except:
                                #pass
                    self.start_optimist[previndexbp] = []
                elif len(self.start_optimist[previndexbp])>0:
                    print('Старый вариант лучше новый удаляем.')
                    for fNmeForRemove in self.start_optimist[bp]:
                            #try:
                                os.remove(fNmeForRemove)
                            #except:
                                #pass
                    for fNmeForRename in self.start_optimist[previndexbp]:
                        #try:
                            os.rename(fNmeForRename[:-3]+'~pd4', fNmeForRename) # переименовать
                        #except:
                            #pass
                    self.start_optimist[bp] = self.start_optimist[previndexbp]
            if len(self.start_optimist[bp]) == 1:
                print("Лучший вариант! Стартовая точка " + self.settings.machine_base_name[BASEPOINT])
                break
            if self.panel.overt: self.panelOverturn()
            self.rotatePanel()
            previndexbp = bp
        return

    def app_start_optimist(self, resultOutput):
        if resultOutput:
            self.start_optimist[self.startBP].append(self.cmdfileName)

    def panelOverturn(self):
        # Переворачиваем относительно оси X
        self.panel.Overturn(0)
        self.aposition = 0
        b =self.findPathSize(VARIANTPATH)
        self.panel.Translate(machine.Vector2d(-b.min.x, -b.min.y))
        self.panel.overt = True # Признак перевернутости Для версии к3 6,5  надо проверить в 7,1
        global BASEPOINT
        BASEPOINT = self._overt_basepoint[BASEPOINT]
        paths = self.panel.paths
        for path in paths:
            path.overt = True # Изменяется при перевороте панели
        mc = machine.constraints
        self.writer.num_tdcode=int(1) # счетчик номеров обработок
        self.writer.num_point = int(0)
        self.writer.l_crf = []
        self.writer.l_cat = []
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
        lDDM = self.get_list_torec_drillMachine(d, mc)        # для торцевых отверстий требуется уточнение по допустимым осям
        self.drill_revisia(d, mc)
#не заморачиваемся c 11-11-2015 см письма Братуся        # 
        ps = machine.constraints.CheckConstraints(d, listDrillDimMashine=lDDM) # проверка на выполнимость по допустимым экстримальным координатам
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

                    cnxn, cursor, recordset = self.odbc_conn(SQL_STR='''SELECT TCuts.Depth, TCuts.ExtrZ FROM TPaths INNER JOIN TCuts ON (TPaths.CutPos = TCuts.CutPos) AND (TPaths.PanelPos = TCuts.UnitPos) WHERE (((TCuts.UnitPos)='''+str(self.panel.id.handle)+''') AND ((TPaths.PathID)='''+str(path.id.handle)+'''));''')
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
        dictG = {}
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
        ##                            if self.Ovtrn:
        ##                                cs =180-cs
        ##                                print "Ovrtn.cs=", cs
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
        ##                        if self.Ovtrn:
        ##                            cs =180-cs
        ##                            print "Ovrtn.cs=", cs
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

    def readerContours(self, panel):
        "Чтение внешнего контура и сквозных вырезов. Подготовка."
        #print "readerContours"
        p= panel.paths # Список контуров панели
        con = []  #  Список для контуров
        #i=0
        for a in p:
            #print i
            #print a.is_tcuts
            #print a.is_plane_path
            if (not(a.is_tcuts) and a.is_plane_path) or (a.is_tcuts and not(a.is_plane_path)):
                segments = a.segments
                ttt=len(segments)
                if ttt!=0:
                    if type(segments[0]) == machine.Circle:
                        r=segments[0].path
                        segments = segments[0].Divide(0.5)
                        for s in segments:
                            s.path_H=r
                        for sg in segments:
                            Utiles.SegmentReverse(sg)
                    elif ttt==2:
                        s0=segments[0]
                        s1=segments[1]
                        if  s0== machine.Arc and  s1== machine.Arc and s0.start_pt==s1.end_pt:
                            for sg in segments:
                                Utiles.SegmentReverse(sg)
                segm = []  #  Инициализация списка сегментов
                for seg1 in segments:
                    segm.append(seg1)
                    #print seg1.params
                    #print seg1.work_ids
                    #print seg1.works
                con.append(segm)
            #i+=1

    # На выходе список контуров con со списками составляющих сегментов seg
    # Доступ по индексу con [i] [j], где i - номер контура, j - номер сегмента

        #if not self.keyFrez: #  Обработка должна накладываться на одну сторону
            #self.keyFrez = True
            #con =self.FilterBetweenCNC(con) # Достаточно один раз, так как меняется только направление)
        return con

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


