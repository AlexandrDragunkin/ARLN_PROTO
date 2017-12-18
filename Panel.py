# -*- coding: cp1251 -*-
import k3
import os
import lister

@lister.printerable
class Slot():
  '''Пропил для панели'''
  __sides={"B": 7,"C": 3,"D": 1,"E": 5,"Free": 9}    # Привязки пропилов
  __maps=(1,2,3,4,5,6,7,8,9,10,11,12) # Секции раскрашивания
  __types=("Bounded","Halfthrough","Through") # Типы пропилов (ограниченный, полуограниченный, сквозной)

  def __init__(self):
    self.__num=0        # Номер пропила в панели. Присваивается при добавлении пропила в панель
    self.__planeA=False # Пласть пропила (False - F, True - A)
    self.__side="Free"  # Привязка пропила к стороне
    self.__cpr=0        # Отступ от стороны
    self.__cpw=0        # Ширина
    self.__cpd=0        # Глубина
    self.__cps=0        # Отступ от начала
    self.__cpl=0        # Длина
    self.__angle=0      # Угол
    self.__map=0        # Map-секция пропила
    self.__bIncise=False# Признак автопропила

  def SetSlot(self,planeA,side,stype,cpr,cps,cpd,cpw,cpl,angle,map):
    '''Установить параметры пропила
    planeA - сторона пропила (True - A, False - F)
    side - привязка пропила к стороне ("B", "C", "D", "E", "Free")
    stype - тип пропила ("Bounded" - ограниченный, "Halfthrough" - полуограниченный, "Through" - сквозной)
    cpr - отступ от стороны или координата X (для свободного пропила)
    cps - отступ от начала или координата Y (для свободного пропила)
    cpd - глубина пропила
    cpw - ширина пропила
    cpl - длина пропила (для ограниченного "Bounded" пропила)
    angle - угол пропила (в градусах)
    map - секция раскрашивания
          (E - 1, D - 2, C - 3, B - 4, A - 5, F - 6, 
          Угол 1 - 7, Угол 2 - 8, Угол 3 - 9, Угол 4 - 10,
          Дополнение 1 - 11, Дополнение 2 - 12)'''
    if (side not in Slot.__sides):
      return False
    if (map not in Slot.__maps):
      return False
    if (stype not in Slot.__types):
      return False
    self.__planeA=planeA
    if (stype=="Bounded"):
      self.__cpl=cpl
    if (stype=="Halfthrough"):
      self.__cpl=-1
    if (stype=="Through"):
      self.__cpl=0
    self.__side=side
    self.__cpr=cpr
    self.__cps=cps
    self.__cpd=cpd
    self.__cpw=cpw
    self.__angle=angle
    self.__map=map
    return True

  def GetType(self):
    '''Получить тип пропила 
    ("Bounded" - ограниченный, "Halfthrough" - полуограниченный, "Through" - сквозной)'''
    if (self.__cpl==-0):
      return Slot.__types[2]
    if (self.__cpl==-1):
      return Slot.__types[1]
    return Slot.__types[0]

  def IsPlaneA(self):
    '''Получить пласть пропила'''
    return self.__planeA

  def GetSide(self):
    '''Получить привязку пропила к стороне'''
    return self.__side

  def GetMap(self):
    '''Получить секцbю раскрашивателя'''
    return self.__map

  def GetAngle(self):
    '''Получить угол пропила (в градусах)'''
    return self.__angle

  def GetWidth(self):
    '''Вернуть ширину пропила'''
    return self.__cpw

  def GetDepth(self):
    '''Вернуть глубину пропила'''
    return self.__cpd

  def GetBegPoint(self):
    '''Вернуть отступ пропила от стороны и отсуп пропила от начала
    или координаты X и Y начала пропила (для свободного пропила)'''
    return (self.__cpr,self.__cps)

  def GetLength(self):
    '''Вернуть длину пропила'''
    return self.__cpl

  def _SetNum(self,num):
    '''Задать номер пропила в панели'''
    self.__num=num
    return self.__num

  def GetNum(self):
    '''Вернуть номер пропила'''
    return self.__num

class AngleTypes:
  '''Параметры углов панели'''
  __types=(0,1,2,3,4,5,6,7)

  def __init__(self):
    self.__typeang=0            # Тип подрезки угла
    self.__param=[0.,0.,0.,0.]  # Параметры подрезки углов

  def SetAngle(self,Type,*Params):
    '''Установить параметры подрезки угла'''
    if (Type not in AngleTypes.__types):
      return False
    self.__typeang=Type
    if (len(Params)>4):
      return False
    self.__param=Params
    return True

  def GetAngleType(self):
    '''Получить тип угла'''
    return self.__typeang

  def GetAngleParams(self):
    '''Получить параметры угла'''
    return self.__param

class Cutline:
  '''Линия врезки, нароста или линия маркировки
  '''
  __forms={"Free": 1, "Circle": 500, "Arc": 600, "Rectangle": 601, "Figure": 603}
  __types={"Cut": 1, "Bulge": 8, "Mark": 0}
  __maps=(1,2,3,4,5,6,7,8,9,10,11,12) # Секции раскрашивания
  __sides={"B": 7,"C": 3,"D": 1,"E": 5,"Free": 9}    # Привязки линий врезки
  __planes={"A": 1, "F": 2, "Through": 0} # Сторона врезки

  def __init__(self):
    self.__num=0    # Номер врезки в панели
    self.__type="Cut"
    self.__form="Circle"
    self.__params=[0.,0.,0.,0.] # Параметры линии врезки
    self.__map=0
    self.__plane="Through"
    self.__side="Free"
    self.__ismiddle=False # Применять ли вырез к середине панели
    self.__posx=0   # Сдвиг врезки вдоль стороны или координата X врезки в ЛСК панели
    self.__posy=0   # Сдвиг врезки внутрь панели или координата Y врезки в ЛСК панели
    self.__angle=0  # Угол поворота линни врезки в градусах
    self.__depth=0  # Глубина врезки
    self.__depthshift=0 # Сдвиг врезки внутрь панели по толщине
    self.__bands=[]     # Список кромок на врезке
    self.__fixlines=[]  # Список линий крепежа на врезке
    self.__butts=[]     # Список торцевых обработок на врезке
    self.__mills=[]     # Список фрезеровок на врезке

  def SetCutline(self,map,type,form,*params):
    '''Задать параметры линии врезки

    map - секция раскрашивания
          (E - 1, D - 2, C - 3, B - 4, A - 5, F - 6, 
          Угол 1 - 7, Угол 2 - 8, Угол 3 - 9, Угол 4 - 10,
          Дополнение 1 - 11, Дополнение 2 - 12)
    type - тип линии врезки:
      "Cut" - вырез,
      "Bulge" - нарост,
      "Mark" - линия маркировки
    form - форма врезки:
      "Free" - произвольная врезка:
        param[0] - ссылка на объект (полилинию) контура врезки 
      "Circle" - окружность:
        param[0] - радиус окружности
      "Arc" - дуга:
        param[0] - ширина дуги
        param[1] - прогиб дуги
        param[2] - радиус скругления
      "Rectangle" - прямоугольник со скругленными концами:
        param[0] - ширина прямоугольника
        param[1] - высота прямоугольника
        param[2] - радиус скругления
      "Figure" - фигурная врезка:
        param[0] - длина
        param[1] - ширина
        param[2] - верхний радиус
        param[3] - нижний радиус
      '''
    if (map not in Cutline.__maps):
      return False
    if (type not in Cutline.__types):
      return False
    if (form not in Cutline.__forms):
      return False
    if (len(params)>4):
      return False
    self.__map=map;
    self.__type=type
    self.__form=form
    if (form!="Free"):
      self.__params=params
    else:
      self.__params=params[0]
    return True

  def SetPosition(self,plane,side,ismiddle,posx,posy,angle,depth,depthshift):
    '''Задать параметры положения линии врезки
    
    plane - пласть врезки ("A", "F", "Through") - для несквозной врезки
    side - привязка врезки к стороне ("B", "C", "D", "E", "Free")
    ismiddle - применять ли врезку к середине панели (True - применять, False - не применять)
    posx - cдвиг врезки вдоль стороны или координата X врезки в ЛСК панели
    posy - cдвиг врезки внутрь панели или координата Y врезки в ЛСК панели
    angle - угол поворота линни врезки в градусах
    depth - глубина врезки (для несквозной врезки)
    depthshift - сдвиг врезки внутрь панели по толщине (для несквозной врезки)
    '''
    if (plane not in Cutline.__planes):
      return False
    if (side not in Cutline.__sides):
      return False
    self.__plane=plane
    self.__side=side
    self.__ismiddle=ismiddle
    self.__posx=posx
    self.__posy=posy
    self.__angle=angle
    if (self.__plane != "Through"):
      self.__depth=depth
      self.__depthshift=depthshift
    else:
      self.__depth=0
      self.__depthshift=0
    return True

  def GetMap(self):
    '''Вернуть секцию раскрашивания врезки'''
    return self.__map

  def GetType(self):
    '''Вернуть тип врезки врезки
    "Cut" - вырез, "Bulge" - нарост, "Mark" - линия маркировки'''
    return self.__type

  def GetPlane(self):
    '''Вернуть пласть врезки
    "A", "F", "Through" - сквозная врезка'''
    return self.__plane

  def GetSide(self):
    '''Вернуть сторону врезки
    "B", "C", "D", "E", "Free" - свободная врезка'''
    return self.__side

  def GetIsMiddle(self):
    '''Вернуть признак, применять ли врезку к середине панели
    (True - применять, False - не применять)'''
    return self.__ismiddle

  def GetPosition(self):
    '''Вернуть положение врезки
    posx - cдвиг врезки вдоль стороны или координата X врезки в ЛСК панели
    posy - cдвиг врезки внутрь панели или координата Y врезки в ЛСК панели    
    '''
    return (self.__posx,self.__posy)

  def GetNum(self):
    '''Вернуть номер врезки'''
    return self.__num
  
  def GetDepth(self):
    '''Вернуть глубину врезки (для сквозной врезки - 0)'''
    return self.__depth

  def GetAngle(self):
    '''Вернуть угол поворота врезки (в градусах)'''
    return self.__angle

  def GetDepthShift(self):
    '''Вернуть сдвиг врезки внутрь панели по толщине (для сквозной врезки - 0)'''
    return self.__depthshift

  def GetForm(self):
    '''Вернуть форму врезки:
      "Free" - произвольная врезка,
      "Circle" - окружность,
      "Arc" - дуга,
      "Rectangle" - прямоугольник со скругленными концами,
      "Figure" - фигурная врезка:
    '''
    return self.__form

  def GetParams(self):
    '''Вернуть параметры врезки

      "Free" - произвольная врезка:
        param[0] - ссылка на объект (полилинию) контура врезки 
      "Circle" - окружность:
        param[0] - радиус окружности
      "Arc" - дуга:
        param[0] - ширина дуги
        param[1] - прогиб дуги
        param[2] - радиус скругления
      "Rectangle" - прямоугольник со скругленными концами:
        param[0] - ширина прямоугольника
        param[1] - высота прямоугольника
        param[2] - радиус скругления
      "Figure" - фигурная врезка:
        param[0] - длина
        param[1] - ширина
        param[2] - верхний радиус
        param[3] - нижний радиус
    '''
    return self.__params

  def _SetNum(self,num):
    '''Задать номер врезки в панели'''
    self.__num=num
    return self.__num

  def AddBand(self,band):
    '''Добавить кромку в панель на врезку
    band - кромка
    
    Функция возвращает количество кромок в панели на врезке'''
    # Проверяем, а нет ли уже таакой кромки в панели
    segment=band.GetSegment()
    idpoly=0 # Контур, на котороый наложена кромка, определяется вырезом
    #idpoly=segment.GetSegment()[0]
    idline=segment.GetSegment()[1]
    i=0
    for ba in self.__bands:
      baseg=ba.GetSegment()
      baidpoly=baseg.GetSegment()[0]
      baidline=baseg.GetSegment()[1]
      if (idpoly==baidpoly and idline==baidline): # Нашли кромку
        del self.__bands[i]
        break
      i+=1
    # Добавляем кромку
    band.SetSegment2(idpoly,idline)
    self.__bands.append(band)
    return len(self.__bands)

  def GetBands(self):
    '''Вернуть список кромок на данной врезке'''
    return self.__bands

  def AddFixline(self,fixline):
    '''Добавить линию крепежа в панель на врезку
    fixline - линия крепежа
    
    Функция возвращает количество линий крепежа в панели на врезки'''
    # Проверяем, а нет ли уже такого крепежа в панели на том же сегмента
    segment=fixline.GetSegment()
    idpoly=0 # Контур, на котороый наложена линия крепежа, определяется вырезом
    #idpoly=segment.GetSegment()[0]
    idline=segment.GetSegment()[1]
    type=fixline.GetType()
    i=0
    for fi in self.__fixlines:
      fiseg=fi.GetSegment()
      fiidpoly=fiseg.GetSegment()[0]
      fiidline=fiseg.GetSegment()[1]
      fitype=fi.GetType()
      if (idpoly==fiidpoly and idline==fiidline and type==fitype): # Нашли линию крепежа
        del self.__fixlines[i]
        break
      i+=1
    # Добавляем линию крепежа
    fixline.SetSegment2(idpoly,idline)
    self.__fixlines.append(fixline)
    return len(self.__fixlines)

  def GetFixlines(self):
    '''Вернуть список линий крепежа на данной врезке'''
    return self.__fixlines

  def AddButt(self,butt):
    '''Добавить торцевую обработку на врезку
    butt - торцевая обработка
    
    Функция возвращает количество торцевых обработок на врезке'''
    # Проверяем, а нет ли уже такой же торцевой обработки в панели на том же сегмента
    segment=butt.GetSegment()
    idpoly=0 # Контур, на котороый наложена торцевая обработка, определяется вырезом
    #idpoly=segment.GetSegment()[0]
    idline=segment.GetSegment()[1]
    type,params=butt.GetType()
    i=0
    for bu in self.__butts:
      buseg=bu.GetSegment()
      buidpoly=buseg.GetSegment()[0]
      buidline=buseg.GetSegment()[1]
      butype,buparams=bu.GetType()
      if (idpoly==buidpoly and idline==buidline and type==butype and params==buparams): # Нашли торцевую обработку
        del self.__butts[i]
        break
      i+=1
    # Добавляем торцевую обработку
    butt.SetSegment2(idpoly,idline)
    self.__butts.append(butt)
    return len(self.__butts)

  def GetButts(self):
    '''Вернуть список торцевых обработок на данной врезке'''
    return self.__butts

  def AddMill(self,mill):
    '''Добавить фрезеровку на врезку
    mill - фрезеровка

    Функция возвращает количество фрезеровок на врезке'''
        # Проверяем, а нет ли уже такой же фрезеровки в панели на том же сегменте
    segment=mill.GetSegment()
    idpoly=0 # Контур, на котороый наложена фрезеровка, определяется вырезом
    #idpoly=segment.GetSegment()[0]
    idline=segment.GetSegment()[1]
    millid=mill.GetMillID()
    coeff,sdv=mill.GetPosition()
    issymmetry=mill.GetSymmetry()
    planea=mill.GetPlane()
    i=0
    for mi in self.__mills:
      miseg=mi.GetSegment()
      miidpoly=miseg.GetSegment()[0]
      miidline=miseg.GetSegment()[1]
      mimillid=mi.GetMillID()
      micoeff,misdv=mi.GetPosition()
      miissymmetry=mi.GetSymmetry()
      miplanea=mi.GetPlane()      
      if (idpoly==miidpoly and idline==miidline and millid==mimillid and coeff==micoeff 
          and sdv==misdv and issymmetry==miissymmetry and planea==miplanea): # Нашли фрезеровку
        del self.__mills[i]
        break
      i+=1
    # Добавляем фрезеровку
    mill.SetSegment2(idpoly,idline)
    self.__mills.append(mill)
    return len(self.__mills)

  def GetMills(self):
    '''Вернуть список фрезеровок на данной врезке'''
    return self.__mills

class Segment:
  '''Сегмент контура или выреза панели
  Применяется для кромок, крепежа, обработки и пр.'''
  def __init__(self,idp=0,idl=0):
    self.__idpoly=idp    # ID контура
    self.__idline=idl    # ID элемента контура (или -1, если весь контур)

  def SetSegment(self,idp,idl):
    '''Задать сегмент
    idp - ID контура
    idl - ID элемента контура (или -1, если весь контур)'''
    self.__idpoly=idp
    self.__idline=idl
    return True

  def GetSegment(self):
    '''Вернуть IDPoly и IDLine сегмента в иде кортежа (IDPoly,IDLine)'''
    return (self.__idpoly,self.__idline)

class Band:
  '''Кромка на стороне панели'''
  def __init__(self,type=0,idpoly=0,idline=0,mask=0x00000009):
    '''Наложить кромку на сторону панели
    
    type - тип кромки
    idpoly - ID контура сегмента
    idline - ID элемента сегмента
    mask - маска наложения кромки'''
    self.__type=type             # Тип кромки на стороне панели
    self.__segment=Segment(idpoly,idline)  # Сегмент контура панели, на который наложена кромка
    self.__mask=mask    # Маска наложения кромки на сторону
    '''
    0x00000001 - Кромка вклюяена в размер панели;
    0x00000002 - Кромка строится с предварительной фрезеровкой;
    0x00000004 - Кромка (фрезеровка) строится с поворотом по оси Z (по вертикали);
    0x00000008 - Кромку можно резать;
    0x80000000 - Лицевая кромка;
    0x40000000 - Текстуру кромки повернуть на 90 градусов
    '''

  def SetType(self,type):
    '''Задать тип кромки type'''
    self.__type=type
    return True

  def GetType(self):
    '''Вернуть тип кромки'''
    return self.__type

  def SetSegment2(self,idpoly,idline):
    '''Задать элементу кромки положение
    idpoly - ID контура, на который наложена кромка
    idline - ID элемента контура, на который наложена кромка.
      Если idline=-1, кромка наложена на весь контур
    '''
    self.__segment.SetSegment(idpoly,idline)
    return True

  def SetSegment(self,idline):
    '''Задать элементу кромки положение
    idline - сегмент, на который надо наложить кромку
    '''
    self.__segment=idline
    return True

  def GetSegment(self):
    '''Вернуть сегмент контура, на который наложена кромка'''
    return (self.__segment)

  def SetMask(self,mask):
    '''Задать маску наложения кромки
    mask - маска наложения кромки'''
    self.__mask=mask
    return True

  def GetMask(self):
    '''Вернуть маску наложения кромки'''
    return self.__mask

  def SetBandInPanel(self,bInpanel):
    '''Задать для кромки режим включения внутрь панели
    bInpanel=True - включать внутрь панели
    bInpanel=False - не включать внутрь панели
    '''
    if (bInpanel==True):
      self.__mask=self.__mask|0x00000001
    else:
      self.__mask=self.__mask&0xFFFFFFFE
    return True

  def GetBandInPanel(self):
    '''Вернуть режим включения кромки внутрь панели'''
    return bool(self.__mask&0x00000001)

  def SetBandMill(self,bMill):
    '''Задать для кромки режим построения с предварительной фрезеровкой
    bMill=True - включать режим
    bMill=False - выключить режим
    '''
    if (bMill==True):
      self.__mask=self.__mask|0x00000002
    else:
      self.__mask=self.__mask&0xFFFFFFFD
    return True

  def GetBandMill(self):
    '''Вернуть для кромки режим построения с предварительной фрезеровкой'''
    return bool(self.__mask&0x00000002)

  def SetBandRotate(self,bRotate):
    '''Задать для кромки режим поворота по оси Z
    bRotate=True - включать режим
    bRotate=False - выключить режим
    '''
    if (bRotate==True):
      self.__mask=self.__mask|0x00000004
    else:
      self.__mask=self.__mask&0xFFFFFFFB
    return True

  def GetBandRotate(self):
    '''Вернуть для кромки режим поворота по оси Z'''
    return bool(self.__mask&0x00000004)

  def SetBandCut(self,bCut):
    '''Задать режим "Кромку можно резать"
    bCut=True - включать режим
    bCut=False - выключить режим
    '''
    if (bCut==True):
      self.__mask=self.__mask|0x00000008
    else:
      self.__mask=self.__mask&0xFFFFFFF7
    return True

  def GetBandCut(self):
    '''Вернуть режим "Кромку можно резать"'''
    return bool(self.__mask&0x00000008)

  def SetBandFace(self,bFace):
    '''Задать признак "Лицевая кромка"
    bFace=True - включать признак
    bFace=False - выключить признак
    '''
    if (bFace==True):
      self.__mask=self.__mask|0x80000000
    else:
      self.__mask=self.__mask&0x7FFFFFFF
    return True

  def GetBandFace(self):
    '''Вернуть признак "Лицевая кромка"'''
    return bool(self.__mask&0x80000000)

  def SetBandTextureRotate(self,bTextureRotate):
    '''Задать режим поворота текстуры кромки на 90 градусов
    bTextureRotate=True - включать режим
    bTextureRotate=False - выключить режим
    '''
    if (bTextureRotate==True):
      self.__mask=self.__mask|0x40000000
    else:
      self.__mask=self.__mask&0xBFFFFFFF
    return True

  def GetBandTextureRotate(self):
    '''Вернуть режим поворота текстуры кромки на 90 градусов'''
    return bool(self.__mask&0x40000000)

class Fixline:
  '''Класс линий крепежа в панели'''

  def __init__(self,type=0,idpoly=0,idline=0,mask=0x00000000,shift=0,length=0,rule=0):
    ''' Создать линейку крепаж
    type - тип крепежа
    idpoly - ID контура сегмента
    idline - ID элемента сегмента
    mask - маска крепежа
    shift - сдвиг линии крепежа от начала сегмента
    length - длина линейки крепежа (0 - на всю длину семента)
    rule - номер правила крепежа (0 - правило по умолчанию0
    '''
    self.__type=type             # Тип крепежа на стороне панели
    self.__segment=Segment(idpoly,idline)  # Сегмент контура панели, на который назначен крепеж
    self.__mask=mask          # Маска крепежа на стороне
    self.__shift=shift        # Сдвиг линии крепежа от начала сегмента
    self.__length=length      # Длина линии крепежа (0 - на весь сегмент)
    self.__rule=rule          # Номер правила расстанвки крепержа (0 - правило из таблиц крепежа)
    '''
    0x00000001 - Крепеж ставится от конца сегмента (0 - от начала);
    0x00000002 - Ось Z направлена вниз (0 - вверх);
    0x00000004 - Использовать пятно контакта;
    0x00000040 - Если установлен, то не используется умолчание на пятно контакта,
                 задаваемое типом крепежа;
    0x00000400 - Если установлен, то крепеж ставится без сверловки;
    '''

  def SetType(self,type):
    '''Задать тип крепежа type'''
    self.__type=type
    return True

  def GetType(self):
    '''Вернуть тип крепежа'''
    return self.__type

  def SetSegment2(self,idpoly,idline):
    '''Задать линии крепежа положение
    idpoly - ID контура, на который назначен крепеж
    idline - ID элемента контура, на который назначен крепеж.
    '''
    self.__segment.SetSegment(idpoly,idline)
    return True

  def SetSegment(self,segm):
    '''Задать линии крепежа положение
    segm - сегмент, на который надо назначить крепеж
    '''
    self.__segment=segm
    return True

  def GetSegment(self):
    '''Вернуть сегмент контура, на который назначен крепеж'''
    return (self.__segment)

  def SetMask(self,mask):
    '''Задать маску крепежа
    mask - маска крепежа'''
    self.__mask=mask
    return True

  def GetMask(self):
    '''Вернуть маску крепежа'''
    return self.__mask

  def SetFixFromEnd(self,bFromEnd):
    '''Задать для крепежа режим установки с конца сегмента
    bFromEnd=True - ставить с конца сегмента
    bFromEnd=False - ставить с начала сегмента
    '''
    if (bFromEnd==True):
      self.__mask=self.__mask|0x00000001
    else:
      self.__mask=self.__mask&0xFFFFFFFE
    return True

  def GetFixFromEnd(self):
    '''Вернуть режим режим установки крепежа с конца сегмента'''
    return bool(self.__mask&0x00000001)

  def SetZDown(self,bZDown):
    '''Задать направление оси Z для крепежа
    bZDown=True - ось Z направлена вниз
    bZDown=False - ось Z направлена вверх
    '''
    if (bZDown==True):
      self.__mask=self.__mask|0x00000002
    else:
      self.__mask=self.__mask&0xFFFFFFFD
    return True

  def GetZDown(self):
    '''Вернуть направление оси Z для крепежа
    True - ось Z направлена вниз
    False - ось Z направлена вверх    
    '''
    return bool(self.__mask&0x00000002)

  def SetUseSpot(self,bUseSpot):
    '''Задать режим использования пятна контакта
    bUseSpot=True - включать режим
    bUseSpot=False - выключить режим
    '''
    if (bUseSpot==True):
      self.__mask=self.__mask|0x00000004
    else:
      self.__mask=self.__mask&0xFFFFFFFB
    return True

  def GetUseSpot(self):
    '''Вернуть режим использования пятна контакта'''
    return bool(self.__mask&0x00000004)

  def SetUseDefaultSpot(self,bUseDefaultSpot):
    '''Задать режим "Использовать умолчание на пятно контакта, заданное в правиле крепежа"
    bUseDefaultSpot=True - использовать умолчание
    bUseDefaultSpot=False - не использовать умолчание
    '''
    if (bUseDefaultSpot==False):
      self.__mask=self.__mask|0x00000040
    else:
      self.__mask=self.__mask&0xFFFFFFBF
    return True

  def GetUseDefaultSpot(self):
    '''Вернуть режим "Использовать умолчание на пятно контакта, заданное в правиле крепежа"'''
    return not(bool(self.__mask&0x00000040))

  def SetWithoutDrill(self,bWithoutDrill):
    '''Задать режим отключения сверловки
    bWithoutDrill=True - включать режим
    bWithoutDrill=False - выключить режим
    '''
    if (bWithoutDrill==True):
      self.__mask=self.__mask|0x00000400
    else:
      self.__mask=self.__mask&0xFFFFFBFF
    return True

  def GetWithoutDrill(self):
    '''Вернуть режим отключения сверловки'''
    return bool(self.__mask&0x00000400)

  def SetShift(self,shift):
    '''Задать сдвиг линейки крепежа от начала сегмента
    
    shift - величина сдвига линейки крепежа
    '''
    self.__shift=shift
    return True

  def GetShift(self):
    '''Вернуть сдвиг линейки крепежа от начала сегмента'''
    return self.__shift

  def SetLength(self,length):
    '''Задать длину линейки крепежа
    
    length - длина линейки крепежа
    '''
    self.__length=length
    return True

  def GetLength(self):
    '''Вернуть длину линейки крепежа'''
    return self.__length

  def SetRule(self,rule):
    '''Задать правило расстановки крепежа на линейке
    
    rule - номер правила расстановки крепежа
    '''
    self.__rule=rule
    return True

  def GetRule(self):
    '''Вернуть номер правила расстановки крепежа'''
    return self.__rule

class Decorate:
  '''Класс отделки панели'''
  __maps=(1,2,3,4,5,6,7,8,9,10,11,12) # Секции раскрашивания

  def __init__(self,map=5,variantID=0,matID=0,isvisible=False):
    '''Конструктор отделки'''
    self.__map=map
    self.__variantID=variantID
    self.__matID=matID
    self.__isvisible=isvisible

  def SetDecorate(self,map,variantID,matID,isvisible):
    '''Задать параметры отделки
      map - секция раскрашивания
          (E - 1, D - 2, C - 3, B - 4, A - 5, F - 6, 
          Угол 1 - 7, Угол 2 - 8, Угол 3 - 9, Угол 4 - 10,
          Дополнение 1 - 11, Дополнение 2 - 12)    
      variantID - ID варианта отделки. Если variantID=0, то происходит автоопределение
      варианта отделки. Предполагается, что matID есть хотя бы в одном варианте
      matID - ID материала отделки
      isvisible - признак видимости отделки
    '''
    if (map not in Decorate.__maps):
      return False
    self.__map=map
    self.__variantID=variantID
    self.__matID=matID
    self.__isvisible=isvisible
    return True

  def GetMap(self):
    '''Вернуть секцию раскрашивания отделки
          (E - 1, D - 2, C - 3, B - 4, A - 5, F - 6, 
          Угол 1 - 7, Угол 2 - 8, Угол 3 - 9, Угол 4 - 10,
          Дополнение 1 - 11, Дополнение 2 - 12)    
    '''
    return self.__map

  def GetVariantID(self):
    '''Вернуть вариант отделки'''
    return self.__variantID

  def GetMatID(self):
    '''Вернуть материал отделки'''
    return self.__matID

  def GetIsVisible(self):
    '''Вернуть признак видимости отделки:
    True - отделка видима
    False - отделка невидима
    '''
    return self.__isvisible

class Butt:
  '''Класс торцевой обработки'''
  __types={"None": 0, "Groove": 1, "Chamfer": 2, "Rounding": 3} # Типы торцевых пазов
  __maps=(1,2,3,4,5,6,7,8,9,10,11,12) # Секции раскрашивания

  def __init__(self,type='None',map=1,idpoly=0,idline=0,shift=0,length=0,frombeg=True,islength=True,*params):
    '''Конструктор торцевой обрабоотки
    
    type - тип торцевой обработки:
      None - без обработки
      Groove - паз
      Chamfer - скос
      Rounding - скругление
    map - номер секции раскрашивания
    idpoly - ID контура сегмента
    idline - ID элемента сегмента
    shift - сдвиг торцевой обработки от начала сегмента
    length - длина торцевой обработки (0 - на всю длину семента)
    frombeg - признак того, что торцевая обработки строится с начала сегмента
    islength - если True, то length - длина торцевой обработки. 
      Иначе - растояние от края сегмента, до которого должна идти обработка.
    params - параметры торцевой обработки:
      Для паза -  коэффициент сдвига от пласти А в долях толщины
                  глубина паза 
                  ширина паза
      Для скоса - коэффициент сдвига от пласти А в долях толщины
                  смещение от пласти А в мм
                  угол в градусах
      Для скругления - коэффициент сдвига от пласти А в долях толщины
                  верхний радиус в мм
                  нижний радиус в мм
    '''
    if (type not in Butt.__types):
      type="None"
    if (map not in Butt.__maps):
      map=1
    self.__map=map
    self.__type=type             # Тип торцевой обработкина стороне панели
    self.__segment=Segment(idpoly,idline)  # Сегмент контура панели, на который назначена торцевая обработки
    self.__shift=abs(shift)        # Сдвиг торцевой обработки от начала сегмента
    self.__length=abs(length)      # Длина торцевой обработки (0 - на весь сегмент)
    if (islength==False):
      self.__length=-self.__length
    if (frombeg==False):
      self.__shift=-self.__shift
    if (len(params)!=3):
      params=(0,0,0)
    self.__params=params
    return

  def SetButt(self,type,map,idpoly,idline,shift,length,frombeg,islength,*params):
    '''Создать торцевую обработку
    
    type - тип торцевой обработки:
      None - без обработки
      Groove - паз
      Chamfer - скос
      Rounding - скругление
    map - номер секции раскрашивания
    idpoly - ID контура сегмента
    idline - ID элемента сегмента
    shift - сдвиг торцевой обработки от начала сегмента
    length - длина торцевой обработки (0 - на всю длину семента)
    frombeg - признак того, что торцевая обработки строится с начала сегмента
    islength - если True, то length - длина торцевой обработки. 
      Иначе - растояние от края сегмента, ло которого должна идти обработка.
    params - параметры торцевой обработки:
      Для паза -  коэффициент сдвига от пласти А в долях толщины
                  глубина паза 
                  ширина паза
      Для скоса - коэффициент сдвига от пласти А в долях толщины
                  смещение от пласти А в мм
                  угол в градусах
      Для скругления - коэффициент сдвига от пласти А в долях толщины
                  верхний радиус в мм
                  нижний радиус в мм
    '''
    if (type not in Butt.__types):
      return False
    if (map not in Butt.__maps):
      return False
    self.__map=map
    self.__type=type             # Тип торцевой обработкина стороне панели
    self.__segment=Segment(idpoly,idline)  # Сегмент контура панели, на который назначена торцевая обработки
    self.__shift=abs(shift)        # Сдвиг торцевой обработки от начала сегмента
    self.__length=abs(length)      # Длина торцевой обработки (0 - на весь сегмент)
    if (islength==False):
      self.__length=-self.__length
    if (frombeg==False):
      self.__shift=-self.__shift
    if (len(params)!=3):
      return False
    self.__params=params
    return True

  def SetType(self,type,*params):
    '''Задать тип торцевой обработки type и параметры *params'''
    if (type not in Butt.__types):
      return False
    self.__type=type   
    if (len(params)!=3):
      return False
    self.__params=params 
    return True

  def GetType(self):
    '''Вернуть тип торцевой обработки type и параметры *params'''
    return (self.__type,self.__params)

  def SetSegment2(self,idpoly,idline):
    '''Задать положение тооцевой обработке
    idpoly - ID контура, на который назначена торцевая обработка
    idline - ID элемента контура, на который назначена торцевая обработка
    '''
    self.__segment.SetSegment(idpoly,idline)
    return True

  def SetSegment(self,segm):
    '''Задать положение тооцевой обработке
    segm - сегмент, на который надо назначить торцевую обработку
    '''
    self.__segment=segm
    return True

  def GetSegment(self):
    '''Вернуть сегмент контура, на который назначена торцеая обработка'''
    return (self.__segment)

  def SetPosition(self,shift,length,frombeg=True,islength=True):
    '''Назначить положение торцевой обработке на сегменте панели
    shift - сдвиг торцевой обработки от начала сегмента
    length - длина торцевой обработки (0 - на всю длину семента)
    frombeg - признак того, что торцевая обработки строится с начала сегмента
    islength - если True, то length - длина торцевой обработки. 
      Иначе - растояние от края сегмента, ло которого должна идти обработка.
    '''
    self.__shift=abs(shift)        # Сдвиг торцевой обработки от начала сегмента
    self.__length=abs(length)      # Длина торцевой обработки (0 - на весь сегмент)
    if (islength==False):
      self.__length=-self.__length
    if (frombeg==False):
      self.__shift=-self.__shift
    return True

  def GetPosition(self):
    '''Вернуть параметр положения торцевой обработки на сегменте панели
    shift - сдвиг торцевой обработки от начала сегмента
    length - длина торцевой обработки (0 - на всю длину семента)
    frombeg - признак того, что торцевая обработки строится с начала сегмента
    islength - если True, то length - длина торцевой обработки. 
      Иначе - растояние от края сегмента, ло которого должна идти обработка.
    '''
    shift=abs(self.__shift)
    length=abs(self.__length)
    frombeg=True
    islength=True
    if (self.__shift<0):
      frombeg=False
    if (self.__length<0):
      islength=False
    return (shift,length,frombeg,islength)

  def _GetShiftLength(self):
    '''Вернуть параметр положения торцевой обработки на сегменте панели во внутреннем представлении
    shift - сдвиг торцевой обработки от начала сегмента
    length - длина торцевой обработки (0 - на всю длину семента)
    '''
    shift=self.__shift
    length=self.__length
    return (shift,length)

  def SetMap(self,map):
    '''Установить номер секцию раскрашивания map'''
    if (map not in Butt.__maps):
      return False
    self.__map=map
    return True

  def GetMap(self):
    '''Вернуть секцию раскрашивания торцевой обработки map'''
    return self.__map

class Mill:
  '''Создание фрезеровки на панели'''
  __maps=(1,2,3,4,5,6,7,8,9,10,11,12) # Секции раскрашивания

  def  __init__(self,millid=0,coeff=0,sdv=0,idpoly=0,idline=0,map=5,issymmetry=False,isplaneA=True,name="",path=None):
    '''Инициализация фрезеровки

    millid - ID фрезы из Номенклатурного справочника
    coeff - Сдвиг фрезеровки внутри панели в долях единицы
    sdv - Сдвиг фрезеровки внутрь панели в мм
    idpoly - ID контура сегмента
    idline - ID элемента сегмента
    map - Номер секции раскрашивания 
    issymmetry - Признак симметрии образующей относительно оси OX
    isplaneA - Пласть фрезеровки (A или F)
    name - Имя фрезеровки
    path - Контур образующей фрезы
    '''
    self.__millid=millid            # ID фрезы из Номенклатурного справочника
    self.__coeff=coeff              # Сдвиг фрезеровки внутри панели в долях единицы
    self.__sdv=sdv                  # Сдвиг фрезеровки внутрь панели в мм
    self.__segment=Segment(idpoly,idline)  # Сегмент контура панели, на который назначена фрезеровка
    self.__map=map                  # Номер секции раскрашивания 
    self.__issymmetry=issymmetry    # Признак симметрии образующей относительно оси OX
    self.__isplaneA=isplaneA        # Пласть фрезеровки (A или F)
    self.__name=name                # Имя фрезеровки
    if (path!=None):
      if isinstance(path[0],k3.Pline):
        self.__path=path[0]         # Контур образующей фрезы
      else:
        Ply=k3.pline(k3.k_path,path[0])
        self.__path=Ply[0]
    else:
      self.__path=path
    return

  def SetMill(self,millid,coeff,sdv,idpoly,idline,map,issymmetry,isplaneA):
    '''
    millid - ID фрезы из Номенклатурного справочника
    coeff - Сдвиг фрезеровки внутри панели в долях единицы
    sdv - Сдвиг фрезеровки внутрь панели в мм
    idpoly - ID контура сегмента
    idline - ID элемента сегмента
    map - Номер секции раскрашивания 
    issymmetry - Признак симметрии образующей относительно оси OX
    isplaneA - Пласть фрезеровки (A или F)
    
    Данной функцией можно пользоваться только для фрез, которые есть в Номенклатурном справочнике'''
    # Проверяем наличие фрезы в номенклатурном справочнике
    if (k3.priceinfo(millid,"MATNAME","")==""): 
      return False                  # Такой фрезы в номенклатурном справоянике нет
    fname=k3.priceinfo(millid,"K3File","")
    if (fname==""):
      return False                  # Нет свойства K3File для фрезы
    if (os.path.dirname(fname)!="Профили\\Фрезы"):
      return False                  # Это не профиль фрезеровки
    self.__millid=millid            # ID фрезы из Номенклатурного справочника
    self.__coeff=coeff              # Сдвиг фрезеровки внутри панели в долях единицы
    self.__sdv=sdv                  # Сдвиг фрезеровки внутрь панели в мм
    self.__segment=Segment(idpoly,idline)  # Сегмент контура панели, на который назначена фрезеровка
    if (map not in Mill.__maps):
      return False
    self.__map=map                  # Номер секции раскрашивания 
    self.__issymmetry=issymmetry    # Признак симметрии образующей относительно оси OX
    self.__isplaneA=isplaneA        # Пласть фрезеровки (A или F)
    return True

  def SetMap(self,map):
    '''Установить номер секцию раскрашивания map'''
    if (map not in Mill.__maps):
      return False
    self.__map=map
    return True

  def GetMap(self):
    '''Вернуть секцию раскрашивания фрезеровки map'''
    return self.__map

  def SetSegment2(self,idpoly,idline):
    '''Задать сегмент контура панели, на который наложена фрезеровка
    idpoly - ID контура, на который наложена фрезеровка
    idline - ID элемента контура, на который наложена фрезеровка
    '''
    self.__segment.SetSegment(idpoly,idline)
    return True

  def SetSegment(self,segm):
    '''Задать сегмент контура панели, на который наложена фрезеровка
    segm - сегмент, на который наложена фрезеровка
    '''
    self.__segment=segm
    return True

  def GetSegment(self):
    '''Вернуть сегмент контура, на который наложена фрезеровка'''
    return (self.__segment)

  def SetMillID(self,millid):
    '''Задать ID фрезы для фрезеровки
    
    millid - ID фрезы из Номенклатурного справочника'''
    # Проверяем наличие фрезы в номенклатурном справочнике
    if (k3.priceinfo(millid,"MATNAME","")==""): 
      return False                  # Такой фрезы в номенклатурном справоянике нет
    fname=k3.priceinfo(millid,"K3File","")
    if (fname==""):
      return False                  # Нет свойства K3File для фрезы
    if (os.path.dirname(fname)!="Профили\\Фрезы"):
      return False                  # Это не профиль фрезеровки
    self.__millid=millid            # ID фрезы из Номенклатурного справочника
    return True

  def GetMillID(self):
    '''Вернуть ID фрезы из Номенклатурного справочника'''
    return self.__millid

  def SetPosition(self,coeff,sdv):
    '''Назначить положение фрезеровки на панели
    coeff - cдвиг фрезеровки внутри панели в долях единицы
    sdv - cдвиг фрезеровки внутрь панели в мм
    '''
    self.__coeff=coeff              # Сдвиг фрезеровки внутри панели в долях единицы
    self.__sdv=sdv                  # Сдвиг фрезеровки внутрь панели в мм
    return True

  def GetPosition(self):
    '''Вернуть положение фрезеровки на панели
    coeff - cдвиг фрезеровки внутри панели в долях единицы
    sdv - cдвиг фрезеровки внутрь панели в мм
    '''
    coeff=self.__coeff
    sdv=self.__sdv
    return (coeff,sdv)

  def SetSymmetry(self,issymmetry):
    '''Установить признак симметрии образующей относительно оси OX

    issymmetry - признак симметрии
    issymmetry=False - симметрия отсутствует
    issymmetry=True - признак симметрии установлен
    '''
    self.__issymmetry=issymmetry     # Признак симметрии образующей относительно оси OX
    return True

  def GetSymmetry(self):
    '''Вернуть признак симметрии образующей относительно оси OX

    False - симметрия отсутствует
    True - признак симметрии установлен
    '''
    return self.__issymmetry

  def SetPlane(self,isplaneA):
    '''Установить пласть фрезеровки (A или F)

    isplaneA - пласть фрезеровки A
    isplaneA=False - пласть фрезеровки A
    isplaneA=True - Пласть фрезеровки (A или F)
    '''
    self.__isplaneA=isplaneA  # Пласть фрезеровки (A или F)
    return True

  def GetPlane(self):
    '''Вернуть пласть фрезеровки (A или F)

    False - пласть фрезеровки A
    True - Пласть фрезеровки (A или F)
    '''
    return self.__isplaneA

  def SetPath(self,path,name):
    '''Задать контур образующей и имя для фрезеровки с произвольным контуром

    path - контур образующей фрезеровки
    name - имя фрезеровки для регистрации
    '''
    if (path!=None):
      if isinstance(path[0],k3.Pline):
        self.__path=path[0]         # Контур образующей фрезы
      else:
        Ply=k3.pline(k3.k_path,path[0])
        self.__path=Ply[0]
    else:
      self.__path=path
    self.__name=name    # Имя фрезеровки для регистрации
    return True

  def GetPath(self):
    '''Вернуть контур образующей фрезы и имя фрезеровки для регистрации

    path - контур образующей фрезеровки
    name - имя фрезеровки для регистрации
    '''
    path=self.__path
    name=self.__name
    return (path,name)

@lister.printerable
class Panel:
  '''Создание панели'''
  __majortypes=(11,12,13,14)
  __anglenums=(1,2,3,4)
  __sides={"B": 7,"C": 3,"D": 1,"E": 5,"Free": 9}
  __sidetuple=("B", "C", "D", "E")
  __cutlineforms={"Free": 1, "Circle": 502, "Arc": 600, "Rectangle": 601, "Figure": 603}
  __cutlinetypes={"Cut": 1, "Bulge": 8, "Mark": 0}
  __planes={"A": 1, "F": 2, "Through": 0} # Сторона врезки
  __butttypes={"None": 0, "Groove": 1, "Chamfer": 2, "Rounding": 3} # Типы торцевых пазов
  __panelforms={"Free": 1, "Rectangle": 2, "Quadrangle": 3, "Bychord": 4, "Bytwolines": 5}  # Формы панели

  def __init__(self):
    '''Конструктор панели'''
    self.__majorplace=12          # Тип панели (полка, стойка, стенка)
    self.__length=1000            # Длина панели
    self.__width=1000             # Ширина панели
    self.__panmater=0             # ID материала панели
    self.__texangle=0             # Направление текутруы
    self.__slots=[]               # Список пропилов в панели
    self.__butts=[]               # Список торцевых обработок панели
    self.__fixlines=[]            # Список линий крепежа в панели
    self.__decorates=[]           # Список отделок панели
    self.__bIncise=False          # Признак врезной панели - нужно делать пропилы в смежных
    self.__bands=[]               # Список кромок на панели
    self.__type=0                 # Тип формы панели (прямая, гнутая и пр.)
    at=AngleTypes()
    self.__angles=[at,at,at,at]   # Параметры подрезки углов
    self.__caves=[0,0,0,0]        # Список прогибов сторон
    self.__cuts=[0,0,0,0]         # Список подрезок сторон
    self.__maxcut=0               # Максимальный номер врезок
    self.__cutlines=[]            # Список врезок
    self.__mills=[]               # Список фрезеровок
    self.__panelform="Rectangle"  # Форма панели
    self.__formpath=None          # Контур панели по замкнутому контуру
    self.__coords=()              # Координаты 4-х углов панели в формате ((x1,y1),(x2,y2),(x3,y3),(x4,y4))
    self.__chordlength=0          # Длина хорды панели
    self.__chordarc=0             # Прогиб хорды панели
    self.__isaxeY=False           # Ось гиба панели (Y - True, X - False)
    self.__length1=0              # Длина первого отрезка панели
    self.__length2=0              # Длина второго отрезка панели
    self.__angle=90               # Угол гиба панели
    self.__radius=0               # Радиус гиба панели
    self.__issymmetry=False       # Признак симметрии панели

  def SetMater(self, mater):
    '''Задаем материал панели
    Mater - ID материала из номенклатурного справочника
    '''
    self.__panmater=mater
    return True

  def SetTextureAngle(self,texangle):
    '''Задаем улол текстуры
    texangle - Угол поворота текстуры по отношению к длине панели
    Если texangle=-1 - текстура игнорируется
    '''
    if (0<=texangle<=90 or texangle==-1):
      self.__texangle=texangle
      return True
    return False

  def SetMajorPlace(self,majorplace):
    '''Задаем положение панели (полка, стойка, стенка)
    majorplace - положение панели:
    12 - полка,
    11 - стойка,
    13 - накладная стенка,
    14 - врезная стенка.
    '''
    if (majorplace in Panel.__majortypes):
      self.__majorplace=majorplace
      return True
    return False

  def SetCutAngles(self,anglenum,angletype,*angleparams):
    '''Задаем подрезку угла с номером AngleNum
    anglenum - номер угла (1, 2, 3, 4),
    angletype - Тип угла,
    angleparams - Кортеж параметров панели. Он зависит от типа угла
      angletype=0 - угол без подрезки. Параметры отсутствуют
      angletype=1 - фаска.
        angleparams[0] - подрезка по X
        angleparams[1] - подрезка по Y
      angletype=2 - вырез прямоугольный.
        angleparams[0] - подрезка по X
        angleparams[1] - подрезка по Y
        angleparams[2] - радиус
      angletype=3 - дуга.
        angleparams[0] - подрезка по X
        angleparams[1] - подрезка по Y
        angleparams[2] - радиус (>0 - для выпуклой дуги, <0 - для вогнутой)
      angletype=4 - скругление.
        angleparams[0] - радиус
      angletype=5 - голубница.
        angleparams[0] - радиус
      angletype=6 - вырез произвольный.
        angleparams[0] - подрезка по X
        angleparams[1] - подрезка по Y
        angleparams[2] - смещение вершины по X
        angleparams[3] - смещение вершины по Y
    '''
    if (anglenum not in Panel.__anglenums):
      return False
    at=AngleTypes()
    if(at.SetAngle(angletype,*angleparams)==False):
      return False
    self.__angles[anglenum-1]=at
    return True

  def SetCave(self,sidenum,cave):
    '''Задаем прогиб стороны SideNum на величину Cave
    sidenum - номер стороны
    cave - величина прогиба
    '''
    if (sidenum in Panel.__sidetuple):
      ind=Panel.__sidetuple.index(sidenum)
      self.__caves[ind]=cave
      return True
    return False

  def SetCuts(self,sidenum,cut):
    '''Задаем подрез стороны SideNum на величину Cut
    sidenum - номер стороны
    cut - величина подрезки
    '''
    if (sidenum in Panel.__sidetuple):
      ind=Panel.__sidetuple.index(sidenum)
      self.__cuts[ind]=cut
      return True
    return False

  def SetGabs(self,length,width):
    '''Задаем габариты панели
    length - длина панели
    width - ширина панели

    Данная функция делает панель прямоугольной
    '''
    if (length>0 and width>0):
      self.__length=length
      self.__width=width
      self.__panelform="Rectangle"
      return True
    return False

  def  SetFreeForm(self, path):
    '''Задаем форму панели про произвольному замкнутому контуру
    path - контур панели по замкнутому контуру
    
    Данная функция делает панель по произвольному контуру'''
    if (path!=None):
      if isinstance(path[0],k3.Pline):
        self.__formpath=path[0]         
      else:
        Ply=k3.pline(k3.k_path,path[0])
        self.__formpath=Ply[0]
      self.__panelform="Free"
    else:
      return False
    return True

  def SetQuadrangle(self,*coords):
    '''Задаем форму четырехугольной панели
    *coords - координаты 4-х вершин четырехугольника в формате
    ((x1,y1),(x2,y2),(x3,y3),(x4,y4))
    
    Данная функция делает панель четырехугольной'''
    if (len(coords)!=4):
      return False
    for c in coords:
      if (len(c)!=2):
        return False
    self.__coords=coords
    self.__panelform="Quadrangle"
    return True

  def SetBychord(self,chordlength,chordarc,width,isaxeY):
    '''Установить форму панели в гнутую по хорде
    chordlength - длина хорды панели
    chordarc - прогиб хорды панели
    width - ширина панели
    isaxeY - ось гиба панели (Y - True, X - False)

    Функция делает панель гнутой по хорде
    '''
    self.__chordlength=chordlength
    self.__chordarc=chordarc
    self.__width=width
    self.__isaxeY=isaxeY
    self.__panelform="Bychord"
    return True

  def SetBytwolines(self,length1, length2, angle, radius, width, issymmetry, isaxeY):
    '''Установить форму панели в гнутую по двум отрезкам и дуге
    length1 - длина первого отрезка панели
    length2 - длина второго отрезка панели
    angle - угол гиба панели
    radius - радиус гиба панели
    width - ширина панели
    issymmetry - признак симметрии панели
    isaxeY - ось гиба панели (Y - True, X - False)

    Функция делает панель гнутой по двум отрезкам и дуге.
    '''
    self.__length1=length1
    self.__length2=length2
    self.__angle=angle
    self.__radius=radius
    self.__width=width
    self.__issymmetry=issymmetry
    self.__isaxeY=isaxeY
    self.__panelform="Bytwolines"
    return True

  def AddSlot(self,slot):
    '''Добавить пропил в панель
    slot - пропил.
    
    Функция возвращает количество пропилов в панели
    '''
    self.__maxcut=slot._SetNum(self.__maxcut+1)
    self.__slots.append(slot)
    return len(self.__slots)

  def AddCutline(self,cutline):
    '''Добавить врезку в панель
    cutline - врезка

    Функция возвращает количество врезок в панели
    '''
    self.__maxcut=cutline._SetNum(self.__maxcut+1)
    self.__cutlines.append(cutline)
    return len(self.__cutlines)

  def AddBand(self,band):
    '''Добавить кромку в панель
    band - кромка
    
    Функция возвращает количество кромок в панели'''
    # Проверяем, а нет ли уже такой кромки в панели
    segment=band.GetSegment()
    idpoly=1 # Кромка на внешний контур
    #idpoly=segment.GetSegment()[0]
    idline=segment.GetSegment()[1]
    i=0
    for ba in self.__bands:
      baseg=ba.GetSegment()
      baidpoly=baseg.GetSegment()[0]
      baidline=baseg.GetSegment()[1]
      if (idpoly==baidpoly and idline==baidline): # Нашли кромку
        del self.__bands[i]
        break
      i+=1
    # Добавляем кромку
    band.SetSegment2(idpoly,idline)
    self.__bands.append(band)
    return len(self.__bands)

  def AddFixline(self,fixline):
    '''Добавить линию крепежа в панель
    fixline - линия крепежа
    
    Функция возвращает количество линий крепежа в панели'''
    # Проверяем, а нет ли уже такого крепежа в панели на том же сегмента
    segment=fixline.GetSegment()
    idpoly=1 # Крепеж на внешний контур
    #idpoly=segment.GetSegment()[0]
    idline=segment.GetSegment()[1]
    type=fixline.GetType()
    i=0
    for fi in self.__fixlines:
      fiseg=fi.GetSegment()
      fiidpoly=fiseg.GetSegment()[0]
      fiidline=fiseg.GetSegment()[1]
      fitype=fi.GetType()
      if (idpoly==fiidpoly and idline==fiidline and type==fitype): # Нашли линию крепежа
        del self.__fixlines[i]
        break
      i+=1
    # Добавляем линию крепежа
    fixline.SetSegment2(idpoly,idline)
    self.__fixlines.append(fixline)
    return len(self.__fixlines)
  
  def SetIncise(self,bIncise):
    '''Установить признак врезной панели
    bIncise=True -панель врезная
    bIncise=False -панель не врезная
    '''
    self.__bIncise=bIncise
    return True

  def AddDecorate(self,decorate):
    '''Добавить отделку в панель
    decorate - отделка

    Функция аозвращает количество отделок в панели
    '''
    map=decorate.GetMap()
    variantID=decorate.GetVariantID()
    matID=decorate.GetMatID()
    isvisible=decorate.GetIsVisible()
    # Ищем, а нет ли уже таукой отделки
    i=0
    for de in self.__decorates:
      demap=de.GetMap()
      devariantID=de.GetVariantID()
      dematID=de.GetMatID()
      deisvisible=de.GetIsVisible()
      if (demap==map and devariantID==variantID and dematID==matID and deisvisible==isvisible):
        del self.__decorates[i]
        break
      i+=1
    # Добавляем отделку
    self.__decorates.append(decorate)
    return len(self.__decorates)

  def AddButt(self,butt):
    '''Добавить торцевую обработку в панель
    butt - торцевая обработка
    
    Функция возвращает количество торцевых обработок в панели'''
    # Проверяем, а нет ли уже такой же торцевой обработки в панели на том же сегменте
    segment=butt.GetSegment()
    idpoly=1 # Торцевая обработка на внешний контур
    #idpoly=segment.GetSegment()[0]
    idline=segment.GetSegment()[1]
    type,params=butt.GetType()
    i=0
    for bu in self.__butts:
      buseg=bu.GetSegment()
      buidpoly=buseg.GetSegment()[0]
      buidline=buseg.GetSegment()[1]
      butype,buparams=bu.GetType()
      if (idpoly==buidpoly and idline==buidline and type==butype and params==buparams): # Нашли торцевую обработку
        del self.__butts[i]
        break
      i+=1
    # Добавляем торцевую обработку
    butt.SetSegment2(idpoly,idline)
    self.__butts.append(butt)
    return len(self.__butts)

  def AddMill(self,mill):
    '''Добавить фрезеровку в панель
    mill - фрезеровка

    Функция возвращает количество фрезеровок в панели'''
        # Проверяем, а нет ли уже такой же фрезеровки в панели на том же сегменте
    segment=mill.GetSegment()
    idpoly=1 # Фрезеровка на внешний контур
    #idpoly=segment.GetSegment()[0]
    idline=segment.GetSegment()[1]
    millid=mill.GetMillID()
    coeff,sdv=mill.GetPosition()
    issymmetry=mill.GetSymmetry()
    planea=mill.GetPlane()
    i=0
    for mi in self.__mills:
      miseg=mi.GetSegment()
      miidpoly=miseg.GetSegment()[0]
      miidline=miseg.GetSegment()[1]
      mimillid=mi.GetMillID()
      micoeff,misdv=mi.GetPosition()
      miissymmetry=mi.GetSymmetry()
      miplanea=mi.GetPlane()      
      if (idpoly==miidpoly and idline==miidline and millid==mimillid and coeff==micoeff 
          and sdv==misdv and issymmetry==miissymmetry and planea==miplanea): # Нашли фрезеровку
        del self.__mills[i]
        break
      i+=1
    # Добавляем фрезеровку
    mill.SetSegment2(idpoly,idline)
    self.__mills.append(mill)
    return len(self.__mills)

  def Draw(self, x, y, z):
    '''Отрисовываем (добавляем в сцену) созданную панель
    x,y,z - координаты ЛСК панели
    
    Функция возвращает созданную панель'''
    a=k3.VarArray(10)
    # Инициализируем панель
    NULLOUT=k3.setpan6par(1,a)
    # Задаем материал панели
    a[0].value=self.__panmater
    NULLOUT=k3.setpan6par(2,a)
    # Задаем параметры подрезки углов панели
    ty=1
    for i in self.__angles:
      a[0].value=ty
      a[1].value=i.GetAngleType()
      Par=i.GetAngleParams()
      for j in range(len(Par)):
        a[j+2].value=Par[j]
      NULLOUT=k3.setpan6par(4,a)
      ty+=1
    # Задаем прогибы сторон
    a[0].value=self.__caves[2]
    a[1].value=self.__caves[1]
    a[2].value=self.__caves[3]
    a[3].value=self.__caves[0]
    NULLOUT=k3.setpan6par(5,a)
    # Задаем подрезки сторон
    a[0].value=self.__cuts[2]
    a[1].value=self.__cuts[1]
    a[2].value=self.__cuts[3]
    a[3].value=self.__cuts[0]
    NULLOUT=k3.setpan6par(6,a)
    # Добавляем врезки в панель
    for cutline in self.__cutlines:
      a[0].value=Panel.__cutlinetypes[cutline.GetType()]
      a[1].value=Panel.__cutlineforms[cutline.GetForm()]
      pars=cutline.GetParams()
      parnum=1
      for par in pars:
        if (type(par)==int or type(par)==float):
          a[parnum+2].value=par
        else:
          a[2].value=par
          break
        a[2].value=1
        parnum+=1
      NULLOUT=k3.setpan6par(7,a)
      a[0].value=Panel.__sides[cutline.GetSide()]
      pos=cutline.GetPosition()
      a[1].value=pos[0]
      a[2].value=pos[1]
      a[3].value=cutline.GetAngle()
      if (cutline.GetPlane()=="A"):
        a[4].value=cutline.GetDepth()
      elif (cutline.GetPlane()=="F"):
        a[4].value=-cutline.GetDepth()
      else:
        a[4].value=0
      a[5].value=cutline.GetDepthShift()
      a[6].value=cutline.GetIsMiddle()
      NULLOUT=k3.setpan6par(8,a)
      a[0].value=cutline.GetMap()
      NULLOUT=k3.setpan6par(9,a)
      cutline._SetNum(NULLOUT)
      # Дообавляем кромки на эту врезку
      for ba in cutline.GetBands():
        baseg=ba.GetSegment()
        idpoly=cutline.GetNum()
        idline=baseg.GetSegment()[1]
        ba.SetSegment2(idpoly,idline)
        a[0].value=idpoly
        a[1].value=idline
        a[2].value=ba.GetType()
        a[4].value=ba.GetMask()
        NULLOUT=k3.setpan6par(10,a)
      # Дообавляем линии крепежа на эту врезку
      for fi in cutline.GetFixlines():
        fiseg=fi.GetSegment()
        idpoly=cutline.GetNum()
        idline=fiseg.GetSegment()[1]
        fi.SetSegment2(idpoly,idline)
        a[0].value=idpoly
        a[1].value=idline
        a[2].value=fi.GetType()
        a[3].value=fi.GetMask()
        a[4].value=fi.GetShift()
        a[5].value=fi.GetLength()
        a[6].value=fi.GetRule()
        NULLOUT=k3.setpan6par(21,a)
      # Добавляем торцевые обработки на эту врезку
      for bu in cutline.GetButts():
        typeb,params=bu.GetType()
        shift,length=bu._GetShiftLength()
        buseg=bu.GetSegment()
        idpoly=cutline.GetNum()
        idline=buseg.GetSegment()[1]
        bu.SetSegment2(idpoly,idline)
        a[0].value=Panel.__butttypes[typeb]
        a[1].value=idpoly
        a[2].value=idline
        a[3].value=bu.GetMap()
        a[4].value=params[0]
        a[5].value=params[1]
        a[6].value=params[2]
        a[7].value=shift
        a[8].value=length
        NULLOUT=k3.setpan6par(25,a)
      # Добавляем фрезеровки на эту врезку
      for mi in cutline.GetMills():
        path,name=mi.GetPath()
        millid=mi.GetMillID()
        coeff,sdv=mi.GetPosition()
        miseg=mi.GetSegment()
        idpoly=cutline.GetNum()
        idline=miseg.GetSegment()[1]
        if (millid!=0):
          a[0].value=millid
          a[1].value=coeff
          a[2].value=sdv
          a[3].value=mi.GetMap()
          a[4].value=mi.GetSymmetry()
          a[5].value=mi.GetPlane()
          a[6].value=idpoly
          a[7].value=idline
          NULLOUT=k3.setpan6par(20,a)
        elif (path!=None):
          a[0].value=name
          a[1].value=path
          idmilla=k3.setpan6par(13,a)
          a[0].value=coeff
          a[1].value=sdv
          flwork=0
          if (mi.GetPlane()):
            flwork=flwork|4
            if (not mi.GetSymmetry()):
              flwork=flwork|16
          else:
            if (mi.GetSymmetry()):
              flwork=flwork|16
          a[2].value=flwork
          a[3].value=0
          a[4].value=0
          NULLOUT=k3.setpan6par(14,a)
          a[0].value=name+"_Path"
          a[1].value=idmilla
          a[2].value=mi.GetMap()
          idfreza=k3.setpan6par(15,a)
          a[0].value=idpoly
          a[1].value=idline
          a[2].value=idfreza
          idfreza=k3.setpan6par(16,a)
    # Задаем тип панели и размеры
    paneform=Panel.__panelforms[self.__panelform]
    a[0].value=paneform
    if (paneform==1):   # Панель по замкнутому контуру
      a[1].value=self.__formpath
    elif (paneform==2): # Прямоугольная панель
      a[1].value=self.__length
      a[2].value=self.__width
    elif (paneform==3): # Четырехугольная панель
      i=0
      for c in self.__coords:
        a[1+i].value=c[0]
        a[2+i].value=c[1]
        i+=2
    elif (paneform==4): # Гнутая по хорде панель
      a[1].value=self.__chordlength
      a[2].value=self.__chordarc
      a[3].value=self.__width
      a[4].value=self.__isaxeY
    else: # (paneform==5): # Гнутая по двум отрезкам и дуге панель
      a[1].value=self.__length1
      a[2].value=self.__length2
      a[3].value=self.__angle
      a[4].value=self.__radius
      a[5].value=self.__width
      a[6].value=self.__issymmetry
      a[7].value=self.__isaxeY
    NULLOUT=k3.setpan6par(11,a)
    # Добавляем пропилы в панель
    for slot in self.__slots:
      a[0].value=slot.IsPlaneA()
      side=slot.GetSide()
      siden=Panel.__sides[side]
      a[1].value=siden
      begp=slot.GetBegPoint()
      a[2].value=begp[1]
      a[3].value=slot.GetWidth()
      a[4].value=slot.GetDepth()
      a[5].value=begp[0]
      a[6].value=slot.GetLength()
      a[7].value=slot.GetAngle()
      a[8].value=slot.GetMap()
      NULLOUT=k3.setpan6par(17,a)
    # Задаем кромку
    for ba in self.__bands:
      baseg=ba.GetSegment()
      idpoly=baseg.GetSegment()[0]
      idline=baseg.GetSegment()[1]
      a[0].value=idline
      a[1].value=ba.GetType()
      a[3].value=ba.GetMask()
      NULLOUT=k3.setpan6par(3,a)
    # Задаем угол поворота текстуры
    a[0].value=self.__texangle
    NULLOUT=k3.setpan6par(19,a)
    # Задаем фрезеровки
    for mi in self.__mills:
      path,name=mi.GetPath()
      millid=mi.GetMillID()
      coeff,sdv=mi.GetPosition()
      miseg=mi.GetSegment()
      idpoly=miseg.GetSegment()[0]
      idline=miseg.GetSegment()[1]
      if (millid!=0):
        a[0].value=millid
        a[1].value=coeff
        a[2].value=sdv
        a[3].value=mi.GetMap()
        a[4].value=mi.GetSymmetry()
        a[5].value=mi.GetPlane()
        a[6].value=idpoly
        a[7].value=idline
        NULLOUT=k3.setpan6par(20,a)
      elif (path!=None):
        a[0].value=name
        a[1].value=path
        idmilla=k3.setpan6par(13,a)
        a[0].value=coeff
        a[1].value=sdv
        flwork=0
        if (mi.GetPlane()):
          flwork=flwork|4
          if (not mi.GetSymmetry()):
            flwork=flwork|16
        else:
          if (mi.GetSymmetry()):
            flwork=flwork|16
        a[2].value=flwork
        a[3].value=0
        a[4].value=0
        NULLOUT=k3.setpan6par(14,a)
        a[0].value=name+"_Path"
        a[1].value=idmilla
        a[2].value=mi.GetMap()
        idfreza=k3.setpan6par(15,a)
        a[0].value=idpoly
        a[1].value=idline
        a[2].value=idfreza
        idfreza=k3.setpan6par(16,a)
    # Задаем линейки крепежа
    for fi in self.__fixlines:
      fiseg=fi.GetSegment()
      idpoly=fiseg.GetSegment()[0]
      idline=fiseg.GetSegment()[1]
      a[0].value=idpoly
      a[1].value=idline
      a[2].value=0
      NULLOUT=k3.setpan6par(21,a)
      a[2].value=fi.GetType()
      a[3].value=fi.GetMask()
      a[4].value=fi.GetShift()
      a[5].value=fi.GetLength()
      a[6].value=fi.GetRule()
      NULLOUT=k3.setpan6par(21,a)
    # Задаем положение и параметра "С автопропилом"
    a[0].value=self.__majorplace
    a[1].value=self.__bIncise
    NULLOUT=k3.setpan6par(22,a)
    # Задаем торцевые обработки
    for bu in self.__butts:
      typeb,params=bu.GetType()
      shift,length=bu._GetShiftLength()
      buseg=bu.GetSegment()
      idpoly=buseg.GetSegment()[0]
      idline=buseg.GetSegment()[1]
      a[0].value=Panel.__butttypes[typeb]
      a[1].value=idpoly
      a[2].value=idline
      a[3].value=bu.GetMap()
      a[4].value=params[0]
      a[5].value=params[1]
      a[6].value=params[2]
      a[7].value=shift
      a[8].value=length
      NULLOUT=k3.setpan6par(25,a)
    # Задаем отделки
    for de in self.__decorates:
      a[0].value=de.GetMap()
      a[1].value=de.GetVariantID()
      a[2].value=de.GetMatID()
      a[3].value=de.GetIsVisible()
      NULLOUT=k3.setpan6par(28,a)
    # Собственно, создаем панель
    pan=k3.mbpanel(k3.k_create,(x,y,z),self.__majorplace)
    NULLOUT=k3.setpan6par(999,a)
    return pan[0]

#p=Panel()
#p.Draw(0,0,0)
#p.SetMajorPlace(11)
#p.Draw(0,0,0)
#p.SetMater(496)
#p.SetMajorPlace(13)
#p.SetGabs(100,500)
#p.SetCave("E",10)
#p.SetCave("B",50)
#p.SetTextureAngle(20)
#fixline=Fixline()
#fixline.SetType(1)
#fixline.SetSegment2(1,7)
#fixline.SetUseDefaultSpot(False)
#fixline.SetUseSpot(False)
#p.AddFixline(fixline)
#p.Draw(0,0,0)