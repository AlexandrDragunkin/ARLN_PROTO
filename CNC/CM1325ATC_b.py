# -*- coding: utf-8 -*-

#import ptvsd

import machine
import Utiles
import math
from math import sqrt
import os
import string

#import wingdbstub # строка запуска тладчика WING IDE

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
xmax=2000         # размеры рабочего поля станка
xmin=0     
ymax=2900
ymin=0
zmax=150
zmin=-150

class Writer:
    '''Класс, осуществляющий вывод информации из класса Boa. Ссылка на этот класс есть в классе Boa
       В этом классе находятся функции, отвечающие за вывод информации о конкретных элементах в выходной файл'''
    def __init__(self):
      # Здесь мы создаем текстовый форматные константы для вывода
      self.header='''%'''
      self.description='''( Program for CM132ATC )
( http://k3-mebel.ru/                                      )
( v.m 1.1                                                  )'''
      self.eps = 0.0005
      self.xt = -1          # текущее положение фрезы
      self.yt = -1
      self.zt = -1000
      self.zUp = 30         # верхнее и
      self.zDn = -30        # нижнее положение фрезы
      self.DTool = 12       # диаметр фрезы 1
      self.DTool2= 4        # диаметр фрезы 2
      self.FUp = 3000       # скорость передвижения вне полотна
      self.FWork = 1800     # скорость передвижения при резке
      self.Speed = 24000 # скорость вращения шпинделя
#      self.LR = 0
      self.panelName = ""
      self.oG1 = 0          # признак операции G1
      self.Diameter = -1    # текущий диаметр сверла
      self.nTool = 2        # первые 2 инструмента - фрезы, далее - сверла
      #
      self.isVrezka = True  # выполнять врезку
      self.VAngle = 10      # угол врезки
      self.VLength= 20      # длина врезки
      self.VDepth = 5       # минимальная глубина
#
      self.millend=     '''M30
%'''
      self.startsegment='''G0 X%.3f Y%.3f Z%.3f F%.0f'''
      self.arcsegment=  ''' X%.3f Y%.3f I%.3f J%.3f'''
      
# Здесь мы задаем методы для вывода
    def DrillingCommand(self, num, drill, isThrough):
      '''Вывод информации об отверстии в файл
      
      num - порядковый номер отверстия
      drill - отверстие
      '''
      if self.Diameter != drill.diameter:
        self.Diameter = drill.diameter
        self.nTool += 1
        print("(D = ", self.Diameter, " )", file = self.OutputFile)
        self._Operation("M6 T"+ str(self.nTool))
        self._Operation("G43 H"+ str(self.nTool))
        self._Operation("M03 S" + str(self.Speed))
        self._Operation("G0 Z" + str(self.zUp))
      print ("G0 X%.3f Y%.3f" %(drill.position.x, drill.position.y), file = self.OutputFile)
      self._Operation("G0 Z" + str(drill.panel.thickness))
      if isThrough:
        self._Operation("G1 Z" + str(self.zDn) + " F" +str(self.FUp))
      else:
        self._Operation("G1 Z" + str(drill.panel.thickness-drill.depth) + " F" +str(self.FUp))
      self._Operation("G0 Z" + str(self.zUp))
      return

    def SlotCommand(self, num, slot):
      ''' Вывод информации о пропилах в панели
      num - порядковый номер пропила
      slot - пропил'''
      dx = slot.end.x-slot.start.x
      dy = slot.end.y-slot.start.y
      l = sqrt(dx*dx + dy*dy)
      x = dy/l*slot.width*0.5
      y = dx/l*slot.width*0.5
      xstart = slot.start.x
      ystart = slot.start.y
      xend = slot.end.x
      yend = slot.end.y
      x1 = xstart+x
      y1 = ystart-y
      x2 = xend+x
      y2 = yend-y
      x3 = xend-x
      y3 = yend+y
      x4 = xstart-x
      y4 = ystart+y
      print ("G0 X%.3f Y%.3f" %(x1, y1), file = self.OutputFile)
#      self._Operation("G0 Z" + str(slot.panel.thickness-slot.depth))
      self.xt = x1
      self.yt = y1
      self.oG1 = 0
      self.vrezka(slot.panel.thickness-slot.depth, slot.panel.thickness, x2, y2)
      print ("G1 X%.3f Y%.3f" %(x2, y2), file = self.OutputFile)
      print ("G1 X%.3f Y%.3f" %(x3, y3), file = self.OutputFile)
      print ("G1 X%.3f Y%.3f" %(x4, y4), file = self.OutputFile)
      print ("G1 X%.3f Y%.3f" %(x1, y1), file = self.OutputFile)
      self._Operation("G0 Z" + str(self.zUp))
      return

    def getAngle(self, center_pt, pt):
      ''' Вычисляется угол от оси OX'''
      x = pt.x-center_pt.x
      y = pt.y-center_pt.y
      if abs(x) < 1e-7:
        if y > 0:
          angle = 0.5*vpi
        else:
          angle = 1.5*vpi
      else:
        angle = math.atan(abs(y/x))
        if y >= 0 and x < 0:
          angle = vpi-angle
        elif y < 0 and x <= 0:
          angle += vpi
        elif y <= 0 and x > 0:
          angle = 2*vpi-angle
      return angle
  
    def getGoOrder(self, segment):
      ''' Возвращает истину в случае если arc обходится против солнца '''
      a1 = self.getAngle(segment.center, segment.start_pt)
      a2 = self.getAngle(segment.center, segment.middle_pt)
      a3 = self.getAngle(segment.center, segment.end_pt)
      if a1 < a3:
        order = True
        if a2 < a1 or a2 > a3:
          order = not order
      else:
        order = False
        if a2 > a1 or a2 < a3:
          order = not order
      return order
        
    def MillingCommand(self, num, segment, isouter=True, last=False):
      '''Вывод информации о фрезеровки панели
      
      num - порядковый номер сегмента
      segment - сегмент фрезеровки
      isouter - признак внешнего контура'''
      Xpath=segment.path.panel.panel_length
      Ypath=segment.path.panel.panel_width
#      xbeg=Xpath-segment.start_pt.x
#      ybeg=Ypath-segment.start_pt.y
#      xend=Xpath-segment.end_pt.x
#      yend=Ypath-segment.end_pt.y
      xbeg=segment.start_pt.x
      ybeg=segment.start_pt.y
      xend=segment.end_pt.x
      yend=segment.end_pt.y
      if (type(segment)==machine.Line) or (type(segment)==machine.Arc):
        xbeg=segment.start_pt.x
        ybeg=segment.start_pt.y
        xend=segment.end_pt.x
        yend=segment.end_pt.y
      elif type(segment)==machine.Circle:
        xbeg=segment.center.x + segment.radius
        ybeg=segment.center.y
      else:
        print (" Ошибочный тип сегмента")
        return
      z=segment.path.panel.thickness
      #if (isouter==True):
      #  corr=2  # Правая коррекция
      #else:
      #  corr=1  # Левая коррекция
      #if isouter == False:
      #  return
      if (num==1):
        self._MillStartSeg(xbeg,ybeg,self.zUp,self.FUp)
        self.vrezka(self.zDn, segment.path.panel.thickness, segment.end_pt.x, segment.end_pt.y)
#        self._Operation("G1 F" + str(self.FWork) + " Z" + str(self.zDn))
      if (type(segment)==machine.Line):
        self._MillLineSeg(xend,yend)
      elif (type(segment)==machine.Arc):
        center = segment.center
        x3 = center.x-xbeg
        y3 = center.y-ybeg
        bynotsun = self.getGoOrder(segment)
        self._MillArcSeg(xend,yend, x3,y3, bynotsun)
      elif (type(segment) == machine.Circle) and segment.radius > 0.5*self.DTool:
        center = segment.center
        self._MillCircle(xbeg, ybeg, Xpath-center.x, Ypath-center.y, isouter)
      if (last==True):
        self._Operation("G0 Z" + str(self.zUp))
      return

    def _MillCircle(self, xbeg, ybeg, xCenter, yCenter, outer):
      frmt = "G3" if outer == True else "G2"
      if abs(xbeg - xCenter) < self.eps:
        print (frmt + " J%.3f" %(yCenter), file = self.OutputFile)
      elif abs(ybeg - yCenter) < self.eps:
        print (frmt + " I%.3f" %(xCenter), file = self.OutputFile)
      else:
        print (frmt + " I%.3f J%.3f" %(xCenter, yCenter), file = self.OutputFile)
      return

    def vrezka(self, zDn, thicknessPanel, xE, yE):
      if (zDn > thicknessPanel) or (self.isVrezka == False):
        self._Operation("G0 F" + str(self.FWork) + " Z" + str(zDn))
        return
      else:
        tz = thicknessPanel
        self._Operation("G0 Z" + str(tz))
        x0 = self.xt
        y0 = self.yt
        lSegment = sqrt((x0-xE)*(x0-xE) + (y0-yE)*(y0-yE))
        ks = self.VLength/lSegment
        xV = x0 + ks*(xE-x0)
        yV = y0 + ks*(yE-y0)
        while tz-self.VDepth > zDn:
          tz -= self.VDepth
          self._MillLineSeg(xV, yV, tz)
          if tz-self.VDepth > zDn:
            tz -= self.VDepth
            self._MillLineSeg(x0, y0, tz)
        if abs(self.xt-x0) > self.eps or abs(self.yt-y0) > self.eps:
          self._MillLineSeg(x0, y0, zDn)
      return
  
    def _Operation(self, op):
      print (op, file = self.OutputFile)
      return

    def _MillStartSeg(self,x,y,z,f):
      self.xt = x
      self.yt = y
      self.oG1 = 0
#      print ( self.startsegment % (x,y,z, f, self.panelName), file = self.OutputFile)
      print ( self.startsegment % (x,y,z, f), file = self.OutputFile)
      return

    def _MillLineSeg(self,x,y, z = -1000):
      frmt = ""
      if self.oG1 == 0:
        frmt = "G1"
      if abs(x-self.xt) > self.eps:
        frmt += " X%.3f"%(x)
        self.xt = x
#        print ( frmt % (y), file = self.OutputFile)
      if abs(y-self.yt) > self.eps:
        frmt += " Y%.3f"%(y)
        self.yt = y
#        print ( frmt % (x), file = self.OutputFile)
      if (z > -1000) and abs(z-self.zt) > self.eps:
        frmt += " Z%.3f"%(z)
        self.zt = z
      if self.oG1 == 0:
        frmt += " F"+str(self.FWork)
      print ( frmt, file = self.OutputFile)
      self.oG1 = 1
      return

    def _MillArcSeg(self,xe,ye,x2,y2, outer):
      self.oG1 = 0
      self.xt = xe
      self.yt = ye
      frmt = "G3" if outer == True else "G2"
      frmt = frmt +self.arcsegment
      print ( frmt % (xe,ye,x2,y2), file = self.OutputFile)
      return

    def _MillEnd(self):
      print (self.millend, file = self.OutputFile)
      return

    def DataHeadCommand(self):
      '''Вывод информации в заголовок файл'''
      print  (self.header, file=self.OutputFile)
      print  (self.description, file=self.OutputFile)
      return


    def CreateOutputFile(self,FileName):
      '''Открываем на запись файл с именем FileName'''
      self.fname=FileName
      self.OutputFile = open(FileName, 'w') 
      return    
  
    def CloseOFile(self):
      '''Закрываем файл программы '''
      self.OutputFile.close()
      return

class Boa(machine.Machine):
    '''
    Это самый главный класс. Именно его методы запускаются при вызове генератора
    Имя этого класс указано в модуле настроек станка (*_settings)
    Этот класс является наследником класса Machine, который реализован в Machine.pyd

    Методы запускаются в следующей последовательности:
      StartCutProcessing() - для всей всего раскроя (базы)
      StartSheet(Sheet)      - для каждого листа раскроя
        Milling(Panel)  - для каждой обработки-фрезеровки панели
      EndSheet()             - для каждой из панелей
      EndProcessing()        - для всей модели (базы)
    '''
    def __init__(self):
      ''' Конкструктор класса'''
      machine.Machine.__init__(self)            # Вызываем конструктор базового класса. Здесь это обязательно
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
      self.writer = Writer()                    # Класс для вывода информации в файл
      self.paths1=[]                            # Список контуров панелей
      self.paths2=[]                            # Список дырок в панелях, которые нужно будет обработать

      # Стартовая инициализация атрибутов
      self.panelThickness = 16     # Толщина панели
      self.panelWidth = 0          # Ширина панели
      self.panelLength = 0         # Длина панели
      self.fname=""                # имя файла управляющей программы
      self.panelName=""            # Имя панели
      self.numSheet = 0
      self.isBlindHoleA = False    # глухие отверстия по А
      self.isBlindHoleF = False    # глухие отверстия по F
      self.isThroughHole = False   # сквозные отверстия
      self.drillThrough= []
      self.drillPlaneA = []
      self.drillPlaneF = []
      self.drillHoriz  = []
      self.slots = []              # Пропилы

    def CreateCmdfile(self,post):
      '''Создаем файл с управляющей программой
      
      post - имя файла'''    
      fname=post+".u00"
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

    def CreateCmdfileHeading(self):
      '''Записываем общий заголовок в командный файл'''
      self.writer.DataHeadCommand()
      return

    def CreateCmdfileProgram(self, postfix):
      '''Записываем текст программы в командный файл'''
      return

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

    def StartCutProcessing(self):
      '''Метод запускается автоматически перед началом обработки панелей'''
#      ptvsd.enable_attach(None)
#      ptvsd.wait_for_attach(60)
      pass
  
    def StartSheet(self, Sheet):
      self.numSheet = self.numSheet + 1
      self.paths1 = []
      self.paths2 = []
      return
  
    def EndSheet(self):
#      if (len(self.paths2) > 0) or (len(self.paths1) > 0) or self.isThroughHole or self.isBlindHoleF:
      self.writeOutputFile(self.NumOrder+"_"+str(self.numSheet))
      self.writer._Operation("G90")
      self.writer._Operation("G17")
      self.writer._Operation("G49")
      self.writer._Operation("G40")
      self.writer._Operation("G80")
      if self.isThroughHole: # сверловка сквозных
        self.writerDrillingCommand(self.drillThrough, True)
        self.drillThrough.clear()
        self.isThroughHole = False
      if self.isBlindHoleF: # сверловка глухих по F
        self.writerDrillingCommand(self.drillPlaneF, False)
        self.drillPlaneF.clear()
        self.isBlindHoleF = False
#     пропилы фрезой 2 ( 4 мм)
      if len(self.slots) > 0:
        self.writer._Operation("M6 T2")
        self.writer._Operation("G43 H2")
        self.writer._Operation("M03 S" + str(self.writer.Speed))
        self.writer._Operation("G0 Z" + str(self.writer.zUp))
        self.writerSlotsCommand(self.slots)
        self.slots.clear()
#     раскрой основной фрезой (Tool 1)
      if len(self.paths1) > 0 or len(self.paths2) > 0:
        self.writer._Operation("M6 T1")
        self.writer._Operation("G43 H1")
        self.writer._Operation("G0 Z" + str(self.writer.zUp))
      if len(self.paths2) > 0:
        self.writer._Operation("M03 S" + str(self.writer.Speed))
        self.writerContours(self.paths2, False)
      if len(self.paths1) > 0:
#       self.writer._Operation("M05")
        self.writer._Operation("M03 S" + str(self.writer.Speed)) # было M04
        self.writerContours(self.paths1, True)
      self.writer._Operation("M05")
      self.writer._Operation("G0 X" + str(xmax) + " Y" + str(ymax))
      self.writer._MillEnd()
      self.writer.CloseOFile()
      return
  
    def EndProcessing(self):
      '''Метод запускается автоматически после окончания обработки панелей'''
      print('Модуль CNC завершил работу')
      print('Программы ЧПУ находятся в папке:')
      print ("   ",self.settings.cmdfile_path)
      return

    def writeOutputFile(self, postfix):
      '''Записывает накопленную информацию в  файл'''
      # Получаем имя файла
      index = "u"+postfix
      # Создаем файл
      self.CreateCmdfile(index)
      # Пишем в файл шапку
      self.CreateCmdfileHeading()
      # Пишем в файл по очереди все секции
      self.writer.panelName=self.panelName
      print (" Запись в файл ",index,".u00")

    def StartPanel(self, panel):
      '''Метод вызывается автоматически перед началом обработки каждой панели'''
#      self.millingTech = []
#      self.drills=[]
#      self.slots = [] # Пропилы
#      self.workingsides=[]        # Список сторон панели, которые нужно будет обработать

      self.fname="" # Имя файла управляющей программы
      #self.panelName=panel.name
      self.panel = panel
      b = self.panel.bounding_box
#      print (os.path.split(self.settings.database_name)[1])
      a=os.path.split(self.settings.database_name)[1]
#      b=a.split('.')
#      print (b)
      self.NumOrder = a.split('.')[0] #"" #self.settings.database_name
      self.Selobj = 0
      for a in self.panel.attributes:
        if a.name=='Selobj':
          self.Selobj = int(a.value)
        if a.name=='NumOrder':
          self.NumOrder = str(a.value)+"_"
      # Анализируем габарит панели и поворачиваем ее
      w = 0
      if abs(self.panel.bounding_box.size_x-self.panel.detail.bounding_box.size_x) +\
      abs(self.panel.bounding_box.size_y-self.panel.detail.bounding_box.size_y) >\
      abs(self.panel.bounding_box.size_x-self.panel.detail.bounding_box.size_y) +\
      abs(self.panel.bounding_box.size_y-self.panel.detail.bounding_box.size_x):
        self.panel.Rotate(0.5*vpi, self.panel.bounding_box.min)
        w = self.panel.bounding_box.max.x - self.panel.bounding_box.min.x
      self.panel.Translate(machine.Vector2d(w+self.panel.detail.bounding_box.min.x, self.panel.detail.bounding_box.min.y ))
      b = self.panel.bounding_box
      if b.min.x < xmin-eps_d or b.max.x > xmax+eps_d:
        print("Панель #",self.panel.common_pos," (",panel.name,") не проходит по габаритам X(",b.min.x,"-",b.max.x,")")
        print("Габариты панели: ", b.max.x-b.min.x,b.max.y-b.min.y)
        return
      if b.min.y < ymin-eps_d or b.max.y > ymax+eps_d:
        print("Панель #",self.panel.common_pos," (",panel.name,") не проходит по габаритам Y(",b.min.y,"-",b.max.y,")")
        print("Габариты панели: ", b.max.x-b.min.x,b.max.y-b.min.y)
        return 
#      p0 = self.panel.bounding_box.min
#      p0.x = 0
#      p0.y = 0
#      self.panel.Rotate(0.5*vpi, p0)
      self.panelThickness = panel.thickness
      self.panelWidth = self.panel.panel_width
      self.panelLength = self.panel.panel_length
      self.panelNum = panel.common_pos
      self.writer.panelName=panel.name
      # Собираем контура
      self.Contour()
      return True

    def writerContours(self, pathsTuple, outer):
      '''Функция подготавливает к выводу контура pathsTuple - список контуров, которые нужно обработать'''
#      outer=True
      for pp in pathsTuple:
        (p, name) = pp
        self.writer.panelName=name
        segments=p.segments
        a=0
        last=False
        for s in segments:
          a=a+1
          if (a==len(segments)):
            last=True
          self.writer.MillingCommand(a,s,outer,last)
#        outer=False
      return

    def writerSlotsCommand(self, slotsTuple):
      '''Подоготавливает к выводу пропилы
      side - сторона пропила
      slotsTuple - список пропилов в данной панели'''
      a=0
      for a in range(len(slotsTuple)):
        s = slotsTuple[a]
        self.writer.SlotCommand(a, s)
      return

    def writerDrillingCommand(self, drillTuple, isThrough):
      '''Подоготавливает к выводу отверстия
      drillTuple - список отверстий в данной панели'''
      drillTuple.sort(key = lambda d: d.diameter) 
      a=0
      for a in range(len(drillTuple)):
        d = drillTuple[a]
        self.writer.DrillingCommand(a, d, isThrough)
      return

    def EndPanel(self):
      '''Функция вызывается в конце обработки каждой панели'''
      return

    def Drilling(self, d):
      '''Сверловка. Пласти и торцы. Заполняем списки структурами для пластей и торцев'''
      if  abs(abs(d.beta)-vpi/2)<eps_d :
        # сверловка торца
        self.drillHoriz.append(d)
      elif  abs(abs(d.beta)-vpi)<eps_d:
        # сверловка пласти F
        if (d.depth-self.panelThickness)<-eps_d:
          # глубина меньше толщины значит глухое
          self.drillPlaneF.append(d)
          self.isBlindHoleF = True
        else:
          self.drillThrough.append(d)
          self.isThroughHole = True
      elif  abs(abs(d.beta))<eps_d:
        # сверловка пласти A
        if (d.depth-self.panelThickness)<-eps_d:
          # глубина меньше толщины значит глухое
          self.drillPlaneA.append(d)
          self.isBlindHoleA = True
        else:
          self.drillThrough.append(d)
          self.isThroughHole = True
#      print("0: scv=",len(self.drillThrough), " drF=",len(self.drillPlaneF))
      return

    def Slot(self, s):
      '''Пропилы. Заполняем списки структурами пропилов'''
      if s.is_plane==False and s.width >= self.writer.DTool2:
        self.slots.append(s)
      return

    def Contour(self):
      '''Контура. Заполняем списки контурами для фрезеровки'''
      paths=self.panel.paths
      a = 0
      for p in paths:
        if p.is_plane_path == True and p.is_tcuts == False:
          a = a+1
          if a == 1:
            segments=p.segments
            self.paths1.append((p, self.panel.name))
          else:
            self.paths2.append((p, self.panel.name))
      return
  
    def Milling(self, m, s):
      '''Фрезеровки. Заполняем списки фрезеровок'''
      return

    def Filletting(self, f, s):
      pass
