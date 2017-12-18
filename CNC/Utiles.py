# -*- coding: utf-8 -*-

''' Здесь собраны полезные функции для всех (или не всех) станков
'''
import machine
import math

vpi=3.1415926535897932384626433832795     # число Pi
eps_d = 0.001 # допустимое отклонение

def GetDrillPlane(d):
  '''Вернуть сторону панели, в котрой сверлится отверстие
        
  d - отверстие
  Функция возвращает сторону отверстия: A,B,C,D,E,F Если отверстие сквозное, то сторона А

  Если отверстие расположено под углом к торцу или пласти, функция возвращает X
  '''
  z=d.position.z
  h=d.depth
  alpha=d.alfa

  if alpha < 0:
    alpha = vpi + alpha
  beta=d.beta
  t=d.panel.thickness
  if (abs(beta)<eps_d or abs(beta-vpi)<eps_d):  # отверстие в пласти
    if (z<=0 and h+z>=t or z>=t):
      return "A"
    else:
      return "F"
  if (abs(alpha)<eps_d):
    return "B"
  if (abs(alpha-vpi)<eps_d):
    return "C"
  if (abs(alpha+vpi/2)<eps_d):
    return "D"
  if (abs(alpha-vpi/2)<eps_d):
    return "E"
  return "X"

def GetDrillTrough(d):
  '''Вернуть признак характеристики СКВОЗНОЕ для отверстия
  
  d - отверстие
  
  Возвращает True если сквозное
  или False если глухое
  '''
  if (d.panel.thickness - d.depth)<eps_d and (GetDrillPlane(d) in ['A','F']):
    return True
  else:
    return False
    
def GetSlotDirection(slot):
  '''Определяем направление пропила
  Возвращает:
  "X" - если пропил вдоль оси X
  "Y" - если пропил вдоль оси Y
  Иначе, если пропил под углом, то "A"
  '''
  if (abs(slot.start.x-slot.end.x)<eps_d):
    return "Y"
  if (abs(slot.start.y-slot.end.y)<eps_d):
    return "X"
  return "A"

def CheckGabs(panel,xmin,xmax,ymin,ymax,zmin,zmax):
  '''Проверка панели на прохождение теста по габаритам.
  
  panel - панель
  xmin, xmax; ymin,ymax; zmin,zmax - минимальные и максимально-допустимые
  габариты по соответствующим осям
  
  Функция возвращает True, если она проходит по габаритам и False, если не проходит.
  Если габаритный тест не пройден, то выводится соответствующее сообщение
  '''  
  b = panel.bounding_box
  if (b.max.x-b.min.x>xmax or b.max.x-b.min.x<xmin):
    print ("Панель #",panel.common_pos," (",panel.name,") не проходит по габаритам X(",b.max.x-b.min.x,")")
    print ("Габариты панели: ", b.max.x,b.max.y)
    return False
  if (b.max.y-b.min.y>ymax or b.max.y-b.min.y<ymin):
    print ("Панель #",panel.common_pos," (",panel.name,") не проходит по габаритам Y(",b.max.y-b.min.y,")")
    print ("Габариты панели: ", b.max.x,b.max.y)
    return False
  if (panel.thickness>zmax or panel.thickness<zmin):
    print ("Панель #",panel.common_pos," (",panel.name,") не проходит по габаритам Z(",panel.thickness,")")
    return False
  return True

class Constraints():
  '''Класс, задающий ограничения на те или иные операции'''
  trueposits=("AE","AC","AB","AD","FE","FC","FB","FD")  # Кореж допустимых позиций

  def __init__(self):
    # Допустимые габариты панелей
    self.xmax_constr=1000
    self.xmin_constr=85
    self.ymax_constr=5000
    self.ymin_constr=285
    self.zmax_constr=50
    self.zmin_constr=8

    self.drillf_constr=False		# Нет низовой сверловки
    self.slotf_constr=False		# Нет низовых пропилов
    self.slotx_constr=True			# Пропилы по стороне X
    self.sloty_constr=False		# Нет пропилов по стороне Y

    # Количества использованных положений
    self.sideAE=0
    self.sideAC=0
    self.sideAB=0
    self.sideAD=0
    self.sideFE=0
    self.sideFC=0
    self.sideFB=0
    self.sideFD=0

    return

  def SetConstraints(self,xmin,xmax,ymin,ymax,zmin,zmax,**kwords):
    '''Передача ограничений в класс'''
    self.xmax_constr=xmax
    self.xmin_constr=xmin
    self.ymax_constr=ymax
    self.ymin_constr=ymin
    self.zmax_constr=zmax
    self.zmin_constr=zmin

  def AppendPosition(self,poslist,posname):
    '''Метод добавляет позицию posname в список poslist и увеличивает счетчик данной позиции
    
    poslist - список позиций для данной операции
    posname - имя позиции (AE,AC,AB,AD,FE,FC,FB,FD)
    
    Функция возвращает количество в списке добавленных позиций'''

    if posname not in Constraints.trueposits:
      return 0
    poslist.append(posname)
    if posname=="AE":
      self.sideAE+=1
      return self.sideAE
    if posname=="AC":
      self.sideAC+=1
      return self.sideAC
    if posname=="AB":
      self.sideAB+=1
      return self.sideAB
    if posname=="AD":
      self.sideAD+=1
      return self.sideAD
    if posname=="FE":
      self.sideFE+=1
      return self.sideFE
    if posname=="FC":
      self.sideFC+=1
      return self.sideFC
    if posname=="FB":
      self.sideFB+=1
      return self.sideFB
    if posname=="AD":
      self.sideFD+=1
      return self.sideFD
    return 0

  def _CheckDrilling(self,operation):
    '''Проверка операции Сверловка
    operation - операция Сверловка
    self - ограничения станка
  
    Функция возвращает кортеж положений панели вида <Plane><Side>,
    где <Plane> - пласть панели, расположенная вверху (А или F)
    <Side> - сторона панели, расположенная вперед (B, C, D, E)
    '''

    # Проверяем отверстия
    poslist=[]	# Список положений
    panel=operation.panel	# Панель операции
    bbox=panel.bounding_box
    ypanel=bbox.max.y-bbox.min.y
    xpanel=bbox.max.x-bbox.min.x
    xmin=self.xmin_constr
    xmax=self.xmax_constr
    ymin=self.ymin_constr
    ymax=self.ymax_constr
    if isinstance(operation,machine.Drilling):
      position=operation.position
      matr3d=machine.Matrix3d()
      matr3d.translate(machine.Vector2d(-bbox.min.x,-bbox.min.y))
      position.transform(matr3d)
      x=position.x
      y=position.y
      side=GetDrillPlane(operation)
      if side=="X":
        return tuple(poslist)

      # Проверяем пласти панели
      if (side=="A"): # Проверяем сторону А
        if _CheckPositGabs(xmin,xmax,ymin,ymax,x,y):
          self.AppendPosition(poslist,"AE")
        if _CheckPositGabs(xmin,xmax,ymin,ymax,ypanel-y,x):
          self.AppendPosition(poslist,"AC")
        if _CheckPositGabs(xmin,xmax,ymin,ymax,y,xpanel-x):
          self.AppendPosition(poslist,"AB")
        if _CheckPositGabs(xmin,xmax,ymin,ymax,xpanel-x,ypanel-y):
          self.AppendPosition(poslist,"AD")

      if ((operation.depth>=panel.thickness and side=="A") or side=="F"):  # Если отверстие сквозное или сторона F
        if _CheckPositGabs(xmin,xmax,ymin,ymax,xpanel-x,y):
          self.AppendPosition(poslist,"FE")
        if _CheckPositGabs(xmin,xmax,ymin,ymax,y,x):
          self.AppendPosition(poslist,"FC")
        if _CheckPositGabs(xmin,xmax,ymin,ymax,ypanel-y,xpanel-x):
          self.AppendPosition(poslist,"FB")
        if _CheckPositGabs(xmin,xmax,ymin,ymax,x,ypanel-y):
          self.AppendPosition(poslist,"FD")

      if (side=="B"): # Проверяем сторону B
        if (y<ymax and y>ymin):
          self.AppendPosition(poslist,"AE")
        if (ypanel-y<xmax and ypanel-y>xmin):
          self.AppendPosition(poslist,"AC")
        if (y<xmax and y>xmin and xpanel<ymax):
          self.AppendPosition(poslist,"AB")
        if (ypanel-y<ymax and ypanel-y>ymin and xpanel<xmax):
          self.AppendPosition(poslist,"AD")
        if (y<ymax and y>ymin and xpanel<xmax):
          self.AppendPosition(poslist,"FE")
        if (y<xmax and y>xmin):
          self.AppendPosition(poslist,"FC")
        if (ypanel-y<xmax and ypanel-y>xmin and xpanel<ymax):
          self.AppendPosition(poslist,"FB")
        if (ypanel-y<ymax and ypanel-y>ymin):
          self.AppendPosition(poslist,"FD")

      if (side=="C"): # Проверяем сторону C
        if (y<ymax and y>ymin and xpanel<xmax):
          self.AppendPosition(poslist,"AE")
        if (ypanel-y<xmax and ypanel-y>xmin and xpanel<ymax):
          self.AppendPosition(poslist,"AC")
        if (y<xmax and y>xmin):
          self.AppendPosition(poslist,"AB")
        if (ypanel-y<ymax and ypanel-y>ymin):
          self.AppendPosition(poslist,"AD")
        if (y<ymax and y>ymin):
          self.AppendPosition(poslist,"FE")
        if (y<xmax and y>xmin and xpanel<ymax):
          self.AppendPosition(poslist,"FC")
        if (ypanel-y<xmax and ypanel-y>xmin):
          self.AppendPosition(poslist,"FB")
        if (ypanel-y<ymax and ypanel-y>ymin and xpanel<xmax):
          self.AppendPosition(poslist,"FD")

      if (side=="D"): # Проверяем сторону D
        if (x<xmax and x>xmin):
          self.AppendPosition(poslist,"AE")
        if (x<ymax and x>ymin and ypanel<xmax):
          self.AppendPosition(poslist,"AC")
        if (xpanel-x<ymax and xpanel-x>ymin):
          self.AppendPosition(poslist,"AB")
        if (xpanel-x<xmax and xpanel-x>xmin and ypanel<ymax):
          self.AppendPosition(poslist,"AD")
        if (xpanel-x<ymax and xpanel-x>xmin):
          self.AppendPosition(poslist,"FE")
        if (x<ymax and x>ymin):
          self.AppendPosition(poslist,"FC")
        if (xpanel-x<ymax and xpanel-x>ymin and ypanel<xmax):
          self.AppendPosition(poslist,"FB")
        if (x<xmax and x>xmin and ypanel<ymax):
          self.AppendPosition(poslist,"FD")

      if (side=="E"): # Проверяем сторону E
        if (x<xmax and x>xmin and ypanel<ymax):
          self.AppendPosition(poslist,"AE")
        if (x<ymax and x>ymin):
          self.AppendPosition(poslist,"AC")
        if (xpanel-x<ymax and xpanel-x>ymin and ypanel<xmax):
          self.AppendPosition(poslist,"AB")
        if (xpanel-x<xmax and xpanel-x>xmin):
          self.AppendPosition(poslist,"AD")
        if (xpanel-x<ymax and xpanel-x>xmin and ypanel<ymax):
          self.AppendPosition(poslist,"FE")
        if (x<ymax and x>ymin and ypanel<xmax):
          self.AppendPosition(poslist,"FC")
        if (xpanel-x<ymax and xpanel-x>ymin):
          self.AppendPosition(poslist,"FB")
        if (x<xmax and x>xmin):
          self.AppendPosition(poslist,"FD")
    return tuple(poslist)
  
  def CheckConstraints(self,operation):
    '''Определение положения панели, при котором данная операция может быть выполнена
  
    operation - операция
    self - ограничения станка
  
    Функция возвращает кортеж положений панели вида <Plane><Side>,
    где <Plane> - пласть панели, расположенная вверху (А или F)
    <Side> - сторона панели, расположенная вперед (B, C, D, E)
    '''
    poslist=[]	# Список положений
    if not isinstance(operation,machine.Operation):
      return tuple(poslist)

    # Проверяем габариты по Z. Если не проходит, то ничего не поможет
    panel=operation.panel	# Панель операции
    bbox=panel.bounding_box
    ypanel=bbox.max.y-bbox.min.y
    xpanel=bbox.max.x-bbox.min.x
    if (panel.thickness>self.zmax_constr or panel.thickness<self.zmin_constr):
      return tuple(poslist)
    posit=self._CheckDrilling(operation)
    return posit

  def _CheckPositGabs(self,xmin,xmax,ymin,ymax,x,y):
    '''Проверка на попадание координат (x,y) в прямоугольник (xmin,ymin) - (xmax,ymax)'''
    if x<xmin or x>xmax:
      return False
    if y<ymin or y>ymax:
      return False
    return True

  def GetFirst(self):
    '''Функция возвращает масимальное положение панели (из оставшихся)'''

    # Если ни одна обработка недоступна
    if (max(self.sideAE,self.sideAC,self.sideAB,self.sideAD,self.sideFE,self.sideFC,self.sideFB,self.sideFD)==0):
      return "XX"
    if (max(self.sideAE,self.sideAC,self.sideAB,self.sideAD,self.sideFE,self.sideFC,self.sideFB,self.sideFD)==self.sideAE):
      self.sideAE=0
      return "AE"
    if (max(self.sideAE,self.sideAC,self.sideAB,self.sideAD,self.sideFE,self.sideFC,self.sideFB,self.sideFD)==self.sideAC):
      self.sideAC=0
      return "AC"
    if (max(self.sideAE,self.sideAC,self.sideAB,self.sideAD,self.sideFE,self.sideFC,self.sideFB,self.sideFD)==self.sideAB):
      self.sideAB=0
      return "AB"
    if (max(self.sideAE,self.sideAC,self.sideAB,self.sideAD,self.sideFE,self.sideFC,self.sideFB,self.sideFD)==self.sideAD):
      self.sideAD=0
      return "AD"
    if (max(self.sideAE,self.sideAC,self.sideAB,self.sideAD,self.sideFE,self.sideFC,self.sideFB,self.sideFD)==self.sideFE):
      self.sideFE=0
      return "FE"
    if (max(self.sideAE,self.sideAC,self.sideAB,self.sideAD,self.sideFE,self.sideFC,self.sideFB,self.sideFD)==self.sideFC):
      self.sideFC=0
      return "FC"
    if (max(self.sideAE,self.sideAC,self.sideAB,self.sideAD,self.sideFE,self.sideFC,self.sideFB,self.sideFD)==self.sideFB):
      self.sideFB=0
      return "FB"
    if (max(self.sideAE,self.sideAC,self.sideAB,self.sideAD,self.sideFE,self.sideFC,self.sideFB,self.sideFD)==self.sideFD):
      self.sideAE=0
      return "FD"
    return "XX"

  def TransformToSide(self,panel,posit,toback=False):
    '''Функция устанавливает положение панели panel в соответствие с заданной сторонй posit.
    Если toback = True, то положение возвращается из posit в стандартное (АЕ)

    Если передено корректное положение, то функция возвращает True. Иначе - False
    '''
    b = panel.bounding_box
    ypanel=b.max.x-b.min.x
    ypanel=b.max.y-b.min.y
    matr=machine.Matrix3d()
    # Добавляем в матрицу преобразования в зависимости от положенияя
    if posit=="AE":
      pass  # Это нормальное положение панели
    elif posit=="AC":
      matr = machine.Matrix3d.rotate(vpi/2)
      matr *= machine.Matrix3d.translate(machine.Vector2d(-ypanel,0))
    elif posit=="AD":
      matr = machine.Matrix3d.rotate(vpi)
      matr *= machine.Matrix3d.translate(machine.Vector2d(-xpanel,-ypanel))
    elif posit=="AB":
      matr = machine.Matrix3d.rotate(-vpi/2)
      matr *= machine.Matrix3d.translate(machine.Vector2d(0,-xpanel))
    elif posit=="FE":
      matr = machine.Matrix3d.overturn_y(0,panel.thickness/2)
      matr *= machine.Matrix3d.translate(machine.Vector2d(-xpanel,0))
    elif posit=="FC":
      matr = machine.Matrix3d.overturn_y(0,panel.thickness/2)
      matr *= machine.Matrix3d.rotate(vpi/2)
    elif posit=="FD":
      matr = machine.Matrix3d.overturn_y(0,panel.thickness/2)
      matr *= machine.Matrix3d.rotate(vpi)
      matr *= machine.Matrix3d.translate(machine.Vector2d(0,-ypanel))
    elif posit=="FB":
      matr = machine.Matrix3d.overturn_y(0,panel.thickness/2)
      matr *= machine.Matrix3d.rotate(-vpi/2)
      matr *= machine.Matrix3d.translate(machine.Vector2d(-ypanel,-xpanel))
    else:
      return False
    # Если нужно восстановить положение, то инвертируем матрицу
    if toback:
      matr.inverse()
    panel.Transform(matr)
    return True



 
  # Написать функцию поворота панели в соответствии с положением.

  # Написать фуункции проверки положения для пропилов
  
def createSPath(segments, d):
  # создать огибающую по списоку сегментов и расстоянию до огибающей
  segm = []
  def length(start_pt, end_pt): 
    l = start_pt.x-end_pt.x
    m = start_pt.y-end_pt.y
    return math.sqrt(l*l+m*m)
  for s in segments:
    crv = buildSeg(s, d)
    for w in s.work_ids:
      handle = w.handle
      crv.AddWorkId(handle)
    if len(segm) > 0:
      if not intersect_1(segm[-1], crv):
        if length(segm[-1].end_pt, crv.start_pt) > eps_d:
          m = getMArc(segm[-1].end_pt, crv.start_pt, s.start_pt, d)
          crv1 = machine.Arc(segm[-1].end_pt, m, crv.start_pt)
          crv1.AddWorkId(handle)
          segm.append(crv1)
          segm.append(crv)
      else:
        segm.append(crv)
        addLineLine(segm, -2, handle)
    else:
      segm.append(crv)
  if (length(segments[0].start_pt, segments[-1].end_pt) < eps_d) and (len(segments) > 1):
    if (not intersect_1(segm[0], segm[-1])) and (length(segm[0].start_pt, segm[-1].end_pt) > eps_d):
      m = getMArc(segm[-1].end_pt, segm[0].start_pt, segments[0].start_pt, d)
      crv1 = machine.Arc(segm[-1].end_pt, m, segm[0].start_pt)
      crv1.AddWorkId(handle)
      segm.append(crv1)
    else:
      addLineLine(segm, 0, handle)
    
  return segm

def addLineLine(segm, id1, handle):
  # проверяет на пересечение id1 и последний элемент списка segm и при необходимости редактирует список
#  lis = intersectLineLine(segm[id1], segm[-1])
  lis = segm[-1].Intersect(segm[id1])
  if len(lis) == 1:
    crv = segm.pop(id1)
    crv1= segm.pop()
    if id1 == 0:
      crv = machine.Line(lis[0], crv.end_pt)
    else:
      crv = machine.Line(crv.start_pt, lis[0])
    crv.AddWorkId(handle)
    if id1 == 0:
      crv1 = machine.Line(crv1.start_pt, lis[0])
      crv1.AddWorkId(handle)
      segm.insert(0, crv)
    else:
      crv1 = machine.Line(lis[0], crv1.end_pt)
      crv1.AddWorkId(handle)
      segm.append(crv)
    segm.append(crv1)
'''
def intersectLineLine(line1, line2):
  lis = []
  a1 = line1.start_pt.y-line1.end_pt.y
  a2 = line2.start_pt.y-line2.end_pt.y
  b1 = line1.end_pt.x-line1.start_pt.x
  b2 = line2.end_pt.x-line2.start_pt.x
  c1 = -a1*line1.start_pt.x - b1*line1.start_pt.y
  c2 = -a2*line2.start_pt.x - b2*line2.start_pt.y
  def det(a, b, c, d): return a*d - b*c
  zn = det(a1, b1, a2, b2)
  if abs(zn) > eps_d:
    x = -det(c1, b1, c2, b2)/zn
    y = -det(a1, c1, a2, c2)/zn
    lis.append(machine.Point2d(x, y))
  return lis
'''
def getMArc(s, e, c, r):
  # стартовая, конечная, центр радиус арки
  x = (e.x-s.x)/2+s.x   # точка на  хорде/2 от стартовой точки к конечной
  y = (e.y-s.y)/2+s.y
  x = x-c.x             # вектор от центра арки к центру хорды
  y = y-c.y
  l = math.sqrt(x*x +y*y)
  x = x/l*abs(r) + c.x
  y = y/l*abs(r) + c.y
  return machine.Point2d(x, y)

def intersect_1(line1, line2):
  def intersect_1d(a, b, c, d):
    if a > b:
      a,b = b,a
    if c > d:
      c,d = d,c
    return max(a,c) <= min(b,d) + eps_d
  return (intersect_1d(line1.start_pt.x, line1.end_pt.x, line2.start_pt.x, line2.end_pt.x))\
    or ( intersect_1d(line1.start_pt.y, line1.end_pt.y, line2.start_pt.y, line2.end_pt.y))
    
def buildSeg(segment, d):
  if type(segment)==machine.Line:
    crv = buildLine(segment, d)
  elif type(segment)== machine.Arc:
    s = segment.start_pt
    e = segment.end_pt
    m = segment.middle_pt
    c = segment.center
    r = segment.radius
    if (d < 0) and (2*r < d+eps_d):
      crv = buildLine(segment, d)
    else:
      def buildPoint(c, p, r, d):
        x = p.x-c.x
        y = p.y-c.y
        l = math.sqrt(x*x+y*y)
        x = x/l*(r+d)
        y = y/l*(r+d)
        return machine.Point2d(x, y)
      s = buildPoint(c, s, r, d)
      e = buildPoint(c, e, r, d)
      m = buildPoint(c, m, r, d)
      crv = machine.Arc(s, m, e)
  return crv
  
def buildLine(segment, d):
  l = segment.end_pt.x - segment.start_pt.x
  m = segment.end_pt.y - segment.start_pt.y
  length = math.sqrt(l*l + m*m)
  l /= length
  m /= length
  start_pt = machine.Point2d(segment.start_pt.x + m*d, segment.start_pt.y - l*d)
  end_pt = machine.Point2d(segment.end_pt.x + m*d, segment.end_pt.y - l*d)
  return machine.Line(start_pt, end_pt)
