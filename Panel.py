# -*- coding: cp1251 -*-
import k3
import os
import lister

@lister.printerable
class Slot():
  '''������ ��� ������'''
  __sides={"B": 7,"C": 3,"D": 1,"E": 5,"Free": 9}    # �������� ��������
  __maps=(1,2,3,4,5,6,7,8,9,10,11,12) # ������ �������������
  __types=("Bounded","Halfthrough","Through") # ���� �������� (������������, ����������������, ��������)

  def __init__(self):
    self.__num=0        # ����� ������� � ������. ������������� ��� ���������� ������� � ������
    self.__planeA=False # ������ ������� (False - F, True - A)
    self.__side="Free"  # �������� ������� � �������
    self.__cpr=0        # ������ �� �������
    self.__cpw=0        # ������
    self.__cpd=0        # �������
    self.__cps=0        # ������ �� ������
    self.__cpl=0        # �����
    self.__angle=0      # ����
    self.__map=0        # Map-������ �������
    self.__bIncise=False# ������� �����������

  def SetSlot(self,planeA,side,stype,cpr,cps,cpd,cpw,cpl,angle,map):
    '''���������� ��������� �������
    planeA - ������� ������� (True - A, False - F)
    side - �������� ������� � ������� ("B", "C", "D", "E", "Free")
    stype - ��� ������� ("Bounded" - ������������, "Halfthrough" - ����������������, "Through" - ��������)
    cpr - ������ �� ������� ��� ���������� X (��� ���������� �������)
    cps - ������ �� ������ ��� ���������� Y (��� ���������� �������)
    cpd - ������� �������
    cpw - ������ �������
    cpl - ����� ������� (��� ������������� "Bounded" �������)
    angle - ���� ������� (� ��������)
    map - ������ �������������
          (E - 1, D - 2, C - 3, B - 4, A - 5, F - 6, 
          ���� 1 - 7, ���� 2 - 8, ���� 3 - 9, ���� 4 - 10,
          ���������� 1 - 11, ���������� 2 - 12)'''
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
    '''�������� ��� ������� 
    ("Bounded" - ������������, "Halfthrough" - ����������������, "Through" - ��������)'''
    if (self.__cpl==-0):
      return Slot.__types[2]
    if (self.__cpl==-1):
      return Slot.__types[1]
    return Slot.__types[0]

  def IsPlaneA(self):
    '''�������� ������ �������'''
    return self.__planeA

  def GetSide(self):
    '''�������� �������� ������� � �������'''
    return self.__side

  def GetMap(self):
    '''�������� ����b� ��������������'''
    return self.__map

  def GetAngle(self):
    '''�������� ���� ������� (� ��������)'''
    return self.__angle

  def GetWidth(self):
    '''������� ������ �������'''
    return self.__cpw

  def GetDepth(self):
    '''������� ������� �������'''
    return self.__cpd

  def GetBegPoint(self):
    '''������� ������ ������� �� ������� � ����� ������� �� ������
    ��� ���������� X � Y ������ ������� (��� ���������� �������)'''
    return (self.__cpr,self.__cps)

  def GetLength(self):
    '''������� ����� �������'''
    return self.__cpl

  def _SetNum(self,num):
    '''������ ����� ������� � ������'''
    self.__num=num
    return self.__num

  def GetNum(self):
    '''������� ����� �������'''
    return self.__num

class AngleTypes:
  '''��������� ����� ������'''
  __types=(0,1,2,3,4,5,6,7)

  def __init__(self):
    self.__typeang=0            # ��� �������� ����
    self.__param=[0.,0.,0.,0.]  # ��������� �������� �����

  def SetAngle(self,Type,*Params):
    '''���������� ��������� �������� ����'''
    if (Type not in AngleTypes.__types):
      return False
    self.__typeang=Type
    if (len(Params)>4):
      return False
    self.__param=Params
    return True

  def GetAngleType(self):
    '''�������� ��� ����'''
    return self.__typeang

  def GetAngleParams(self):
    '''�������� ��������� ����'''
    return self.__param

class Cutline:
  '''����� ������, ������� ��� ����� ����������
  '''
  __forms={"Free": 1, "Circle": 500, "Arc": 600, "Rectangle": 601, "Figure": 603}
  __types={"Cut": 1, "Bulge": 8, "Mark": 0}
  __maps=(1,2,3,4,5,6,7,8,9,10,11,12) # ������ �������������
  __sides={"B": 7,"C": 3,"D": 1,"E": 5,"Free": 9}    # �������� ����� ������
  __planes={"A": 1, "F": 2, "Through": 0} # ������� ������

  def __init__(self):
    self.__num=0    # ����� ������ � ������
    self.__type="Cut"
    self.__form="Circle"
    self.__params=[0.,0.,0.,0.] # ��������� ����� ������
    self.__map=0
    self.__plane="Through"
    self.__side="Free"
    self.__ismiddle=False # ��������� �� ����� � �������� ������
    self.__posx=0   # ����� ������ ����� ������� ��� ���������� X ������ � ��� ������
    self.__posy=0   # ����� ������ ������ ������ ��� ���������� Y ������ � ��� ������
    self.__angle=0  # ���� �������� ����� ������ � ��������
    self.__depth=0  # ������� ������
    self.__depthshift=0 # ����� ������ ������ ������ �� �������
    self.__bands=[]     # ������ ������ �� ������
    self.__fixlines=[]  # ������ ����� ������� �� ������
    self.__butts=[]     # ������ �������� ��������� �� ������
    self.__mills=[]     # ������ ���������� �� ������

  def SetCutline(self,map,type,form,*params):
    '''������ ��������� ����� ������

    map - ������ �������������
          (E - 1, D - 2, C - 3, B - 4, A - 5, F - 6, 
          ���� 1 - 7, ���� 2 - 8, ���� 3 - 9, ���� 4 - 10,
          ���������� 1 - 11, ���������� 2 - 12)
    type - ��� ����� ������:
      "Cut" - �����,
      "Bulge" - ������,
      "Mark" - ����� ����������
    form - ����� ������:
      "Free" - ������������ ������:
        param[0] - ������ �� ������ (���������) ������� ������ 
      "Circle" - ����������:
        param[0] - ������ ����������
      "Arc" - ����:
        param[0] - ������ ����
        param[1] - ������ ����
        param[2] - ������ ����������
      "Rectangle" - ������������� �� ������������ �������:
        param[0] - ������ ��������������
        param[1] - ������ ��������������
        param[2] - ������ ����������
      "Figure" - �������� ������:
        param[0] - �����
        param[1] - ������
        param[2] - ������� ������
        param[3] - ������ ������
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
    '''������ ��������� ��������� ����� ������
    
    plane - ������ ������ ("A", "F", "Through") - ��� ���������� ������
    side - �������� ������ � ������� ("B", "C", "D", "E", "Free")
    ismiddle - ��������� �� ������ � �������� ������ (True - ���������, False - �� ���������)
    posx - c���� ������ ����� ������� ��� ���������� X ������ � ��� ������
    posy - c���� ������ ������ ������ ��� ���������� Y ������ � ��� ������
    angle - ���� �������� ����� ������ � ��������
    depth - ������� ������ (��� ���������� ������)
    depthshift - ����� ������ ������ ������ �� ������� (��� ���������� ������)
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
    '''������� ������ ������������� ������'''
    return self.__map

  def GetType(self):
    '''������� ��� ������ ������
    "Cut" - �����, "Bulge" - ������, "Mark" - ����� ����������'''
    return self.__type

  def GetPlane(self):
    '''������� ������ ������
    "A", "F", "Through" - �������� ������'''
    return self.__plane

  def GetSide(self):
    '''������� ������� ������
    "B", "C", "D", "E", "Free" - ��������� ������'''
    return self.__side

  def GetIsMiddle(self):
    '''������� �������, ��������� �� ������ � �������� ������
    (True - ���������, False - �� ���������)'''
    return self.__ismiddle

  def GetPosition(self):
    '''������� ��������� ������
    posx - c���� ������ ����� ������� ��� ���������� X ������ � ��� ������
    posy - c���� ������ ������ ������ ��� ���������� Y ������ � ��� ������    
    '''
    return (self.__posx,self.__posy)

  def GetNum(self):
    '''������� ����� ������'''
    return self.__num
  
  def GetDepth(self):
    '''������� ������� ������ (��� �������� ������ - 0)'''
    return self.__depth

  def GetAngle(self):
    '''������� ���� �������� ������ (� ��������)'''
    return self.__angle

  def GetDepthShift(self):
    '''������� ����� ������ ������ ������ �� ������� (��� �������� ������ - 0)'''
    return self.__depthshift

  def GetForm(self):
    '''������� ����� ������:
      "Free" - ������������ ������,
      "Circle" - ����������,
      "Arc" - ����,
      "Rectangle" - ������������� �� ������������ �������,
      "Figure" - �������� ������:
    '''
    return self.__form

  def GetParams(self):
    '''������� ��������� ������

      "Free" - ������������ ������:
        param[0] - ������ �� ������ (���������) ������� ������ 
      "Circle" - ����������:
        param[0] - ������ ����������
      "Arc" - ����:
        param[0] - ������ ����
        param[1] - ������ ����
        param[2] - ������ ����������
      "Rectangle" - ������������� �� ������������ �������:
        param[0] - ������ ��������������
        param[1] - ������ ��������������
        param[2] - ������ ����������
      "Figure" - �������� ������:
        param[0] - �����
        param[1] - ������
        param[2] - ������� ������
        param[3] - ������ ������
    '''
    return self.__params

  def _SetNum(self,num):
    '''������ ����� ������ � ������'''
    self.__num=num
    return self.__num

  def AddBand(self,band):
    '''�������� ������ � ������ �� ������
    band - ������
    
    ������� ���������� ���������� ������ � ������ �� ������'''
    # ���������, � ��� �� ��� ������ ������ � ������
    segment=band.GetSegment()
    idpoly=0 # ������, �� �������� �������� ������, ������������ �������
    #idpoly=segment.GetSegment()[0]
    idline=segment.GetSegment()[1]
    i=0
    for ba in self.__bands:
      baseg=ba.GetSegment()
      baidpoly=baseg.GetSegment()[0]
      baidline=baseg.GetSegment()[1]
      if (idpoly==baidpoly and idline==baidline): # ����� ������
        del self.__bands[i]
        break
      i+=1
    # ��������� ������
    band.SetSegment2(idpoly,idline)
    self.__bands.append(band)
    return len(self.__bands)

  def GetBands(self):
    '''������� ������ ������ �� ������ ������'''
    return self.__bands

  def AddFixline(self,fixline):
    '''�������� ����� ������� � ������ �� ������
    fixline - ����� �������
    
    ������� ���������� ���������� ����� ������� � ������ �� ������'''
    # ���������, � ��� �� ��� ������ ������� � ������ �� ��� �� ��������
    segment=fixline.GetSegment()
    idpoly=0 # ������, �� �������� �������� ����� �������, ������������ �������
    #idpoly=segment.GetSegment()[0]
    idline=segment.GetSegment()[1]
    type=fixline.GetType()
    i=0
    for fi in self.__fixlines:
      fiseg=fi.GetSegment()
      fiidpoly=fiseg.GetSegment()[0]
      fiidline=fiseg.GetSegment()[1]
      fitype=fi.GetType()
      if (idpoly==fiidpoly and idline==fiidline and type==fitype): # ����� ����� �������
        del self.__fixlines[i]
        break
      i+=1
    # ��������� ����� �������
    fixline.SetSegment2(idpoly,idline)
    self.__fixlines.append(fixline)
    return len(self.__fixlines)

  def GetFixlines(self):
    '''������� ������ ����� ������� �� ������ ������'''
    return self.__fixlines

  def AddButt(self,butt):
    '''�������� �������� ��������� �� ������
    butt - �������� ���������
    
    ������� ���������� ���������� �������� ��������� �� ������'''
    # ���������, � ��� �� ��� ����� �� �������� ��������� � ������ �� ��� �� ��������
    segment=butt.GetSegment()
    idpoly=0 # ������, �� �������� �������� �������� ���������, ������������ �������
    #idpoly=segment.GetSegment()[0]
    idline=segment.GetSegment()[1]
    type,params=butt.GetType()
    i=0
    for bu in self.__butts:
      buseg=bu.GetSegment()
      buidpoly=buseg.GetSegment()[0]
      buidline=buseg.GetSegment()[1]
      butype,buparams=bu.GetType()
      if (idpoly==buidpoly and idline==buidline and type==butype and params==buparams): # ����� �������� ���������
        del self.__butts[i]
        break
      i+=1
    # ��������� �������� ���������
    butt.SetSegment2(idpoly,idline)
    self.__butts.append(butt)
    return len(self.__butts)

  def GetButts(self):
    '''������� ������ �������� ��������� �� ������ ������'''
    return self.__butts

  def AddMill(self,mill):
    '''�������� ���������� �� ������
    mill - ����������

    ������� ���������� ���������� ���������� �� ������'''
        # ���������, � ��� �� ��� ����� �� ���������� � ������ �� ��� �� ��������
    segment=mill.GetSegment()
    idpoly=0 # ������, �� �������� �������� ����������, ������������ �������
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
          and sdv==misdv and issymmetry==miissymmetry and planea==miplanea): # ����� ����������
        del self.__mills[i]
        break
      i+=1
    # ��������� ����������
    mill.SetSegment2(idpoly,idline)
    self.__mills.append(mill)
    return len(self.__mills)

  def GetMills(self):
    '''������� ������ ���������� �� ������ ������'''
    return self.__mills

class Segment:
  '''������� ������� ��� ������ ������
  ����������� ��� ������, �������, ��������� � ��.'''
  def __init__(self,idp=0,idl=0):
    self.__idpoly=idp    # ID �������
    self.__idline=idl    # ID �������� ������� (��� -1, ���� ���� ������)

  def SetSegment(self,idp,idl):
    '''������ �������
    idp - ID �������
    idl - ID �������� ������� (��� -1, ���� ���� ������)'''
    self.__idpoly=idp
    self.__idline=idl
    return True

  def GetSegment(self):
    '''������� IDPoly � IDLine �������� � ��� ������� (IDPoly,IDLine)'''
    return (self.__idpoly,self.__idline)

class Band:
  '''������ �� ������� ������'''
  def __init__(self,type=0,idpoly=0,idline=0,mask=0x00000009):
    '''�������� ������ �� ������� ������
    
    type - ��� ������
    idpoly - ID ������� ��������
    idline - ID �������� ��������
    mask - ����� ��������� ������'''
    self.__type=type             # ��� ������ �� ������� ������
    self.__segment=Segment(idpoly,idline)  # ������� ������� ������, �� ������� �������� ������
    self.__mask=mask    # ����� ��������� ������ �� �������
    '''
    0x00000001 - ������ �������� � ������ ������;
    0x00000002 - ������ �������� � ��������������� �����������;
    0x00000004 - ������ (����������) �������� � ��������� �� ��� Z (�� ���������);
    0x00000008 - ������ ����� ������;
    0x80000000 - ������� ������;
    0x40000000 - �������� ������ ��������� �� 90 ��������
    '''

  def SetType(self,type):
    '''������ ��� ������ type'''
    self.__type=type
    return True

  def GetType(self):
    '''������� ��� ������'''
    return self.__type

  def SetSegment2(self,idpoly,idline):
    '''������ �������� ������ ���������
    idpoly - ID �������, �� ������� �������� ������
    idline - ID �������� �������, �� ������� �������� ������.
      ���� idline=-1, ������ �������� �� ���� ������
    '''
    self.__segment.SetSegment(idpoly,idline)
    return True

  def SetSegment(self,idline):
    '''������ �������� ������ ���������
    idline - �������, �� ������� ���� �������� ������
    '''
    self.__segment=idline
    return True

  def GetSegment(self):
    '''������� ������� �������, �� ������� �������� ������'''
    return (self.__segment)

  def SetMask(self,mask):
    '''������ ����� ��������� ������
    mask - ����� ��������� ������'''
    self.__mask=mask
    return True

  def GetMask(self):
    '''������� ����� ��������� ������'''
    return self.__mask

  def SetBandInPanel(self,bInpanel):
    '''������ ��� ������ ����� ��������� ������ ������
    bInpanel=True - �������� ������ ������
    bInpanel=False - �� �������� ������ ������
    '''
    if (bInpanel==True):
      self.__mask=self.__mask|0x00000001
    else:
      self.__mask=self.__mask&0xFFFFFFFE
    return True

  def GetBandInPanel(self):
    '''������� ����� ��������� ������ ������ ������'''
    return bool(self.__mask&0x00000001)

  def SetBandMill(self,bMill):
    '''������ ��� ������ ����� ���������� � ��������������� �����������
    bMill=True - �������� �����
    bMill=False - ��������� �����
    '''
    if (bMill==True):
      self.__mask=self.__mask|0x00000002
    else:
      self.__mask=self.__mask&0xFFFFFFFD
    return True

  def GetBandMill(self):
    '''������� ��� ������ ����� ���������� � ��������������� �����������'''
    return bool(self.__mask&0x00000002)

  def SetBandRotate(self,bRotate):
    '''������ ��� ������ ����� �������� �� ��� Z
    bRotate=True - �������� �����
    bRotate=False - ��������� �����
    '''
    if (bRotate==True):
      self.__mask=self.__mask|0x00000004
    else:
      self.__mask=self.__mask&0xFFFFFFFB
    return True

  def GetBandRotate(self):
    '''������� ��� ������ ����� �������� �� ��� Z'''
    return bool(self.__mask&0x00000004)

  def SetBandCut(self,bCut):
    '''������ ����� "������ ����� ������"
    bCut=True - �������� �����
    bCut=False - ��������� �����
    '''
    if (bCut==True):
      self.__mask=self.__mask|0x00000008
    else:
      self.__mask=self.__mask&0xFFFFFFF7
    return True

  def GetBandCut(self):
    '''������� ����� "������ ����� ������"'''
    return bool(self.__mask&0x00000008)

  def SetBandFace(self,bFace):
    '''������ ������� "������� ������"
    bFace=True - �������� �������
    bFace=False - ��������� �������
    '''
    if (bFace==True):
      self.__mask=self.__mask|0x80000000
    else:
      self.__mask=self.__mask&0x7FFFFFFF
    return True

  def GetBandFace(self):
    '''������� ������� "������� ������"'''
    return bool(self.__mask&0x80000000)

  def SetBandTextureRotate(self,bTextureRotate):
    '''������ ����� �������� �������� ������ �� 90 ��������
    bTextureRotate=True - �������� �����
    bTextureRotate=False - ��������� �����
    '''
    if (bTextureRotate==True):
      self.__mask=self.__mask|0x40000000
    else:
      self.__mask=self.__mask&0xBFFFFFFF
    return True

  def GetBandTextureRotate(self):
    '''������� ����� �������� �������� ������ �� 90 ��������'''
    return bool(self.__mask&0x40000000)

class Fixline:
  '''����� ����� ������� � ������'''

  def __init__(self,type=0,idpoly=0,idline=0,mask=0x00000000,shift=0,length=0,rule=0):
    ''' ������� ������� ������
    type - ��� �������
    idpoly - ID ������� ��������
    idline - ID �������� ��������
    mask - ����� �������
    shift - ����� ����� ������� �� ������ ��������
    length - ����� ������� ������� (0 - �� ��� ����� �������)
    rule - ����� ������� ������� (0 - ������� �� ���������0
    '''
    self.__type=type             # ��� ������� �� ������� ������
    self.__segment=Segment(idpoly,idline)  # ������� ������� ������, �� ������� �������� ������
    self.__mask=mask          # ����� ������� �� �������
    self.__shift=shift        # ����� ����� ������� �� ������ ��������
    self.__length=length      # ����� ����� ������� (0 - �� ���� �������)
    self.__rule=rule          # ����� ������� ���������� �������� (0 - ������� �� ������ �������)
    '''
    0x00000001 - ������ �������� �� ����� �������� (0 - �� ������);
    0x00000002 - ��� Z ���������� ���� (0 - �����);
    0x00000004 - ������������ ����� ��������;
    0x00000040 - ���� ����������, �� �� ������������ ��������� �� ����� ��������,
                 ���������� ����� �������;
    0x00000400 - ���� ����������, �� ������ �������� ��� ���������;
    '''

  def SetType(self,type):
    '''������ ��� ������� type'''
    self.__type=type
    return True

  def GetType(self):
    '''������� ��� �������'''
    return self.__type

  def SetSegment2(self,idpoly,idline):
    '''������ ����� ������� ���������
    idpoly - ID �������, �� ������� �������� ������
    idline - ID �������� �������, �� ������� �������� ������.
    '''
    self.__segment.SetSegment(idpoly,idline)
    return True

  def SetSegment(self,segm):
    '''������ ����� ������� ���������
    segm - �������, �� ������� ���� ��������� ������
    '''
    self.__segment=segm
    return True

  def GetSegment(self):
    '''������� ������� �������, �� ������� �������� ������'''
    return (self.__segment)

  def SetMask(self,mask):
    '''������ ����� �������
    mask - ����� �������'''
    self.__mask=mask
    return True

  def GetMask(self):
    '''������� ����� �������'''
    return self.__mask

  def SetFixFromEnd(self,bFromEnd):
    '''������ ��� ������� ����� ��������� � ����� ��������
    bFromEnd=True - ������� � ����� ��������
    bFromEnd=False - ������� � ������ ��������
    '''
    if (bFromEnd==True):
      self.__mask=self.__mask|0x00000001
    else:
      self.__mask=self.__mask&0xFFFFFFFE
    return True

  def GetFixFromEnd(self):
    '''������� ����� ����� ��������� ������� � ����� ��������'''
    return bool(self.__mask&0x00000001)

  def SetZDown(self,bZDown):
    '''������ ����������� ��� Z ��� �������
    bZDown=True - ��� Z ���������� ����
    bZDown=False - ��� Z ���������� �����
    '''
    if (bZDown==True):
      self.__mask=self.__mask|0x00000002
    else:
      self.__mask=self.__mask&0xFFFFFFFD
    return True

  def GetZDown(self):
    '''������� ����������� ��� Z ��� �������
    True - ��� Z ���������� ����
    False - ��� Z ���������� �����    
    '''
    return bool(self.__mask&0x00000002)

  def SetUseSpot(self,bUseSpot):
    '''������ ����� ������������� ����� ��������
    bUseSpot=True - �������� �����
    bUseSpot=False - ��������� �����
    '''
    if (bUseSpot==True):
      self.__mask=self.__mask|0x00000004
    else:
      self.__mask=self.__mask&0xFFFFFFFB
    return True

  def GetUseSpot(self):
    '''������� ����� ������������� ����� ��������'''
    return bool(self.__mask&0x00000004)

  def SetUseDefaultSpot(self,bUseDefaultSpot):
    '''������ ����� "������������ ��������� �� ����� ��������, �������� � ������� �������"
    bUseDefaultSpot=True - ������������ ���������
    bUseDefaultSpot=False - �� ������������ ���������
    '''
    if (bUseDefaultSpot==False):
      self.__mask=self.__mask|0x00000040
    else:
      self.__mask=self.__mask&0xFFFFFFBF
    return True

  def GetUseDefaultSpot(self):
    '''������� ����� "������������ ��������� �� ����� ��������, �������� � ������� �������"'''
    return not(bool(self.__mask&0x00000040))

  def SetWithoutDrill(self,bWithoutDrill):
    '''������ ����� ���������� ���������
    bWithoutDrill=True - �������� �����
    bWithoutDrill=False - ��������� �����
    '''
    if (bWithoutDrill==True):
      self.__mask=self.__mask|0x00000400
    else:
      self.__mask=self.__mask&0xFFFFFBFF
    return True

  def GetWithoutDrill(self):
    '''������� ����� ���������� ���������'''
    return bool(self.__mask&0x00000400)

  def SetShift(self,shift):
    '''������ ����� ������� ������� �� ������ ��������
    
    shift - �������� ������ ������� �������
    '''
    self.__shift=shift
    return True

  def GetShift(self):
    '''������� ����� ������� ������� �� ������ ��������'''
    return self.__shift

  def SetLength(self,length):
    '''������ ����� ������� �������
    
    length - ����� ������� �������
    '''
    self.__length=length
    return True

  def GetLength(self):
    '''������� ����� ������� �������'''
    return self.__length

  def SetRule(self,rule):
    '''������ ������� ����������� ������� �� �������
    
    rule - ����� ������� ����������� �������
    '''
    self.__rule=rule
    return True

  def GetRule(self):
    '''������� ����� ������� ����������� �������'''
    return self.__rule

class Decorate:
  '''����� ������� ������'''
  __maps=(1,2,3,4,5,6,7,8,9,10,11,12) # ������ �������������

  def __init__(self,map=5,variantID=0,matID=0,isvisible=False):
    '''����������� �������'''
    self.__map=map
    self.__variantID=variantID
    self.__matID=matID
    self.__isvisible=isvisible

  def SetDecorate(self,map,variantID,matID,isvisible):
    '''������ ��������� �������
      map - ������ �������������
          (E - 1, D - 2, C - 3, B - 4, A - 5, F - 6, 
          ���� 1 - 7, ���� 2 - 8, ���� 3 - 9, ���� 4 - 10,
          ���������� 1 - 11, ���������� 2 - 12)    
      variantID - ID �������� �������. ���� variantID=0, �� ���������� ���������������
      �������� �������. ��������������, ��� matID ���� ���� �� � ����� ��������
      matID - ID ��������� �������
      isvisible - ������� ��������� �������
    '''
    if (map not in Decorate.__maps):
      return False
    self.__map=map
    self.__variantID=variantID
    self.__matID=matID
    self.__isvisible=isvisible
    return True

  def GetMap(self):
    '''������� ������ ������������� �������
          (E - 1, D - 2, C - 3, B - 4, A - 5, F - 6, 
          ���� 1 - 7, ���� 2 - 8, ���� 3 - 9, ���� 4 - 10,
          ���������� 1 - 11, ���������� 2 - 12)    
    '''
    return self.__map

  def GetVariantID(self):
    '''������� ������� �������'''
    return self.__variantID

  def GetMatID(self):
    '''������� �������� �������'''
    return self.__matID

  def GetIsVisible(self):
    '''������� ������� ��������� �������:
    True - ������� ������
    False - ������� ��������
    '''
    return self.__isvisible

class Butt:
  '''����� �������� ���������'''
  __types={"None": 0, "Groove": 1, "Chamfer": 2, "Rounding": 3} # ���� �������� �����
  __maps=(1,2,3,4,5,6,7,8,9,10,11,12) # ������ �������������

  def __init__(self,type='None',map=1,idpoly=0,idline=0,shift=0,length=0,frombeg=True,islength=True,*params):
    '''����������� �������� ����������
    
    type - ��� �������� ���������:
      None - ��� ���������
      Groove - ���
      Chamfer - ����
      Rounding - ����������
    map - ����� ������ �������������
    idpoly - ID ������� ��������
    idline - ID �������� ��������
    shift - ����� �������� ��������� �� ������ ��������
    length - ����� �������� ��������� (0 - �� ��� ����� �������)
    frombeg - ������� ����, ��� �������� ��������� �������� � ������ ��������
    islength - ���� True, �� length - ����� �������� ���������. 
      ����� - ��������� �� ���� ��������, �� �������� ������ ���� ���������.
    params - ��������� �������� ���������:
      ��� ���� -  ����������� ������ �� ������ � � ����� �������
                  ������� ���� 
                  ������ ����
      ��� ����� - ����������� ������ �� ������ � � ����� �������
                  �������� �� ������ � � ��
                  ���� � ��������
      ��� ���������� - ����������� ������ �� ������ � � ����� �������
                  ������� ������ � ��
                  ������ ������ � ��
    '''
    if (type not in Butt.__types):
      type="None"
    if (map not in Butt.__maps):
      map=1
    self.__map=map
    self.__type=type             # ��� �������� ����������� ������� ������
    self.__segment=Segment(idpoly,idline)  # ������� ������� ������, �� ������� ��������� �������� ���������
    self.__shift=abs(shift)        # ����� �������� ��������� �� ������ ��������
    self.__length=abs(length)      # ����� �������� ��������� (0 - �� ���� �������)
    if (islength==False):
      self.__length=-self.__length
    if (frombeg==False):
      self.__shift=-self.__shift
    if (len(params)!=3):
      params=(0,0,0)
    self.__params=params
    return

  def SetButt(self,type,map,idpoly,idline,shift,length,frombeg,islength,*params):
    '''������� �������� ���������
    
    type - ��� �������� ���������:
      None - ��� ���������
      Groove - ���
      Chamfer - ����
      Rounding - ����������
    map - ����� ������ �������������
    idpoly - ID ������� ��������
    idline - ID �������� ��������
    shift - ����� �������� ��������� �� ������ ��������
    length - ����� �������� ��������� (0 - �� ��� ����� �������)
    frombeg - ������� ����, ��� �������� ��������� �������� � ������ ��������
    islength - ���� True, �� length - ����� �������� ���������. 
      ����� - ��������� �� ���� ��������, �� �������� ������ ���� ���������.
    params - ��������� �������� ���������:
      ��� ���� -  ����������� ������ �� ������ � � ����� �������
                  ������� ���� 
                  ������ ����
      ��� ����� - ����������� ������ �� ������ � � ����� �������
                  �������� �� ������ � � ��
                  ���� � ��������
      ��� ���������� - ����������� ������ �� ������ � � ����� �������
                  ������� ������ � ��
                  ������ ������ � ��
    '''
    if (type not in Butt.__types):
      return False
    if (map not in Butt.__maps):
      return False
    self.__map=map
    self.__type=type             # ��� �������� ����������� ������� ������
    self.__segment=Segment(idpoly,idline)  # ������� ������� ������, �� ������� ��������� �������� ���������
    self.__shift=abs(shift)        # ����� �������� ��������� �� ������ ��������
    self.__length=abs(length)      # ����� �������� ��������� (0 - �� ���� �������)
    if (islength==False):
      self.__length=-self.__length
    if (frombeg==False):
      self.__shift=-self.__shift
    if (len(params)!=3):
      return False
    self.__params=params
    return True

  def SetType(self,type,*params):
    '''������ ��� �������� ��������� type � ��������� *params'''
    if (type not in Butt.__types):
      return False
    self.__type=type   
    if (len(params)!=3):
      return False
    self.__params=params 
    return True

  def GetType(self):
    '''������� ��� �������� ��������� type � ��������� *params'''
    return (self.__type,self.__params)

  def SetSegment2(self,idpoly,idline):
    '''������ ��������� �������� ���������
    idpoly - ID �������, �� ������� ��������� �������� ���������
    idline - ID �������� �������, �� ������� ��������� �������� ���������
    '''
    self.__segment.SetSegment(idpoly,idline)
    return True

  def SetSegment(self,segm):
    '''������ ��������� �������� ���������
    segm - �������, �� ������� ���� ��������� �������� ���������
    '''
    self.__segment=segm
    return True

  def GetSegment(self):
    '''������� ������� �������, �� ������� ��������� ������� ���������'''
    return (self.__segment)

  def SetPosition(self,shift,length,frombeg=True,islength=True):
    '''��������� ��������� �������� ��������� �� �������� ������
    shift - ����� �������� ��������� �� ������ ��������
    length - ����� �������� ��������� (0 - �� ��� ����� �������)
    frombeg - ������� ����, ��� �������� ��������� �������� � ������ ��������
    islength - ���� True, �� length - ����� �������� ���������. 
      ����� - ��������� �� ���� ��������, �� �������� ������ ���� ���������.
    '''
    self.__shift=abs(shift)        # ����� �������� ��������� �� ������ ��������
    self.__length=abs(length)      # ����� �������� ��������� (0 - �� ���� �������)
    if (islength==False):
      self.__length=-self.__length
    if (frombeg==False):
      self.__shift=-self.__shift
    return True

  def GetPosition(self):
    '''������� �������� ��������� �������� ��������� �� �������� ������
    shift - ����� �������� ��������� �� ������ ��������
    length - ����� �������� ��������� (0 - �� ��� ����� �������)
    frombeg - ������� ����, ��� �������� ��������� �������� � ������ ��������
    islength - ���� True, �� length - ����� �������� ���������. 
      ����� - ��������� �� ���� ��������, �� �������� ������ ���� ���������.
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
    '''������� �������� ��������� �������� ��������� �� �������� ������ �� ���������� �������������
    shift - ����� �������� ��������� �� ������ ��������
    length - ����� �������� ��������� (0 - �� ��� ����� �������)
    '''
    shift=self.__shift
    length=self.__length
    return (shift,length)

  def SetMap(self,map):
    '''���������� ����� ������ ������������� map'''
    if (map not in Butt.__maps):
      return False
    self.__map=map
    return True

  def GetMap(self):
    '''������� ������ ������������� �������� ��������� map'''
    return self.__map

class Mill:
  '''�������� ���������� �� ������'''
  __maps=(1,2,3,4,5,6,7,8,9,10,11,12) # ������ �������������

  def  __init__(self,millid=0,coeff=0,sdv=0,idpoly=0,idline=0,map=5,issymmetry=False,isplaneA=True,name="",path=None):
    '''������������� ����������

    millid - ID ����� �� ��������������� �����������
    coeff - ����� ���������� ������ ������ � ����� �������
    sdv - ����� ���������� ������ ������ � ��
    idpoly - ID ������� ��������
    idline - ID �������� ��������
    map - ����� ������ ������������� 
    issymmetry - ������� ��������� ���������� ������������ ��� OX
    isplaneA - ������ ���������� (A ��� F)
    name - ��� ����������
    path - ������ ���������� �����
    '''
    self.__millid=millid            # ID ����� �� ��������������� �����������
    self.__coeff=coeff              # ����� ���������� ������ ������ � ����� �������
    self.__sdv=sdv                  # ����� ���������� ������ ������ � ��
    self.__segment=Segment(idpoly,idline)  # ������� ������� ������, �� ������� ��������� ����������
    self.__map=map                  # ����� ������ ������������� 
    self.__issymmetry=issymmetry    # ������� ��������� ���������� ������������ ��� OX
    self.__isplaneA=isplaneA        # ������ ���������� (A ��� F)
    self.__name=name                # ��� ����������
    if (path!=None):
      if isinstance(path[0],k3.Pline):
        self.__path=path[0]         # ������ ���������� �����
      else:
        Ply=k3.pline(k3.k_path,path[0])
        self.__path=Ply[0]
    else:
      self.__path=path
    return

  def SetMill(self,millid,coeff,sdv,idpoly,idline,map,issymmetry,isplaneA):
    '''
    millid - ID ����� �� ��������������� �����������
    coeff - ����� ���������� ������ ������ � ����� �������
    sdv - ����� ���������� ������ ������ � ��
    idpoly - ID ������� ��������
    idline - ID �������� ��������
    map - ����� ������ ������������� 
    issymmetry - ������� ��������� ���������� ������������ ��� OX
    isplaneA - ������ ���������� (A ��� F)
    
    ������ �������� ����� ������������ ������ ��� ����, ������� ���� � �������������� �����������'''
    # ��������� ������� ����� � �������������� �����������
    if (k3.priceinfo(millid,"MATNAME","")==""): 
      return False                  # ����� ����� � �������������� ����������� ���
    fname=k3.priceinfo(millid,"K3File","")
    if (fname==""):
      return False                  # ��� �������� K3File ��� �����
    if (os.path.dirname(fname)!="�������\\�����"):
      return False                  # ��� �� ������� ����������
    self.__millid=millid            # ID ����� �� ��������������� �����������
    self.__coeff=coeff              # ����� ���������� ������ ������ � ����� �������
    self.__sdv=sdv                  # ����� ���������� ������ ������ � ��
    self.__segment=Segment(idpoly,idline)  # ������� ������� ������, �� ������� ��������� ����������
    if (map not in Mill.__maps):
      return False
    self.__map=map                  # ����� ������ ������������� 
    self.__issymmetry=issymmetry    # ������� ��������� ���������� ������������ ��� OX
    self.__isplaneA=isplaneA        # ������ ���������� (A ��� F)
    return True

  def SetMap(self,map):
    '''���������� ����� ������ ������������� map'''
    if (map not in Mill.__maps):
      return False
    self.__map=map
    return True

  def GetMap(self):
    '''������� ������ ������������� ���������� map'''
    return self.__map

  def SetSegment2(self,idpoly,idline):
    '''������ ������� ������� ������, �� ������� �������� ����������
    idpoly - ID �������, �� ������� �������� ����������
    idline - ID �������� �������, �� ������� �������� ����������
    '''
    self.__segment.SetSegment(idpoly,idline)
    return True

  def SetSegment(self,segm):
    '''������ ������� ������� ������, �� ������� �������� ����������
    segm - �������, �� ������� �������� ����������
    '''
    self.__segment=segm
    return True

  def GetSegment(self):
    '''������� ������� �������, �� ������� �������� ����������'''
    return (self.__segment)

  def SetMillID(self,millid):
    '''������ ID ����� ��� ����������
    
    millid - ID ����� �� ��������������� �����������'''
    # ��������� ������� ����� � �������������� �����������
    if (k3.priceinfo(millid,"MATNAME","")==""): 
      return False                  # ����� ����� � �������������� ����������� ���
    fname=k3.priceinfo(millid,"K3File","")
    if (fname==""):
      return False                  # ��� �������� K3File ��� �����
    if (os.path.dirname(fname)!="�������\\�����"):
      return False                  # ��� �� ������� ����������
    self.__millid=millid            # ID ����� �� ��������������� �����������
    return True

  def GetMillID(self):
    '''������� ID ����� �� ��������������� �����������'''
    return self.__millid

  def SetPosition(self,coeff,sdv):
    '''��������� ��������� ���������� �� ������
    coeff - c���� ���������� ������ ������ � ����� �������
    sdv - c���� ���������� ������ ������ � ��
    '''
    self.__coeff=coeff              # ����� ���������� ������ ������ � ����� �������
    self.__sdv=sdv                  # ����� ���������� ������ ������ � ��
    return True

  def GetPosition(self):
    '''������� ��������� ���������� �� ������
    coeff - c���� ���������� ������ ������ � ����� �������
    sdv - c���� ���������� ������ ������ � ��
    '''
    coeff=self.__coeff
    sdv=self.__sdv
    return (coeff,sdv)

  def SetSymmetry(self,issymmetry):
    '''���������� ������� ��������� ���������� ������������ ��� OX

    issymmetry - ������� ���������
    issymmetry=False - ��������� �����������
    issymmetry=True - ������� ��������� ����������
    '''
    self.__issymmetry=issymmetry     # ������� ��������� ���������� ������������ ��� OX
    return True

  def GetSymmetry(self):
    '''������� ������� ��������� ���������� ������������ ��� OX

    False - ��������� �����������
    True - ������� ��������� ����������
    '''
    return self.__issymmetry

  def SetPlane(self,isplaneA):
    '''���������� ������ ���������� (A ��� F)

    isplaneA - ������ ���������� A
    isplaneA=False - ������ ���������� A
    isplaneA=True - ������ ���������� (A ��� F)
    '''
    self.__isplaneA=isplaneA  # ������ ���������� (A ��� F)
    return True

  def GetPlane(self):
    '''������� ������ ���������� (A ��� F)

    False - ������ ���������� A
    True - ������ ���������� (A ��� F)
    '''
    return self.__isplaneA

  def SetPath(self,path,name):
    '''������ ������ ���������� � ��� ��� ���������� � ������������ ��������

    path - ������ ���������� ����������
    name - ��� ���������� ��� �����������
    '''
    if (path!=None):
      if isinstance(path[0],k3.Pline):
        self.__path=path[0]         # ������ ���������� �����
      else:
        Ply=k3.pline(k3.k_path,path[0])
        self.__path=Ply[0]
    else:
      self.__path=path
    self.__name=name    # ��� ���������� ��� �����������
    return True

  def GetPath(self):
    '''������� ������ ���������� ����� � ��� ���������� ��� �����������

    path - ������ ���������� ����������
    name - ��� ���������� ��� �����������
    '''
    path=self.__path
    name=self.__name
    return (path,name)

@lister.printerable
class Panel:
  '''�������� ������'''
  __majortypes=(11,12,13,14)
  __anglenums=(1,2,3,4)
  __sides={"B": 7,"C": 3,"D": 1,"E": 5,"Free": 9}
  __sidetuple=("B", "C", "D", "E")
  __cutlineforms={"Free": 1, "Circle": 502, "Arc": 600, "Rectangle": 601, "Figure": 603}
  __cutlinetypes={"Cut": 1, "Bulge": 8, "Mark": 0}
  __planes={"A": 1, "F": 2, "Through": 0} # ������� ������
  __butttypes={"None": 0, "Groove": 1, "Chamfer": 2, "Rounding": 3} # ���� �������� �����
  __panelforms={"Free": 1, "Rectangle": 2, "Quadrangle": 3, "Bychord": 4, "Bytwolines": 5}  # ����� ������

  def __init__(self):
    '''����������� ������'''
    self.__majorplace=12          # ��� ������ (�����, ������, ������)
    self.__length=1000            # ����� ������
    self.__width=1000             # ������ ������
    self.__panmater=0             # ID ��������� ������
    self.__texangle=0             # ����������� ��������
    self.__slots=[]               # ������ �������� � ������
    self.__butts=[]               # ������ �������� ��������� ������
    self.__fixlines=[]            # ������ ����� ������� � ������
    self.__decorates=[]           # ������ ������� ������
    self.__bIncise=False          # ������� ������� ������ - ����� ������ ������� � �������
    self.__bands=[]               # ������ ������ �� ������
    self.__type=0                 # ��� ����� ������ (������, ������ � ��.)
    at=AngleTypes()
    self.__angles=[at,at,at,at]   # ��������� �������� �����
    self.__caves=[0,0,0,0]        # ������ �������� ������
    self.__cuts=[0,0,0,0]         # ������ �������� ������
    self.__maxcut=0               # ������������ ����� ������
    self.__cutlines=[]            # ������ ������
    self.__mills=[]               # ������ ����������
    self.__panelform="Rectangle"  # ����� ������
    self.__formpath=None          # ������ ������ �� ���������� �������
    self.__coords=()              # ���������� 4-� ����� ������ � ������� ((x1,y1),(x2,y2),(x3,y3),(x4,y4))
    self.__chordlength=0          # ����� ����� ������
    self.__chordarc=0             # ������ ����� ������
    self.__isaxeY=False           # ��� ���� ������ (Y - True, X - False)
    self.__length1=0              # ����� ������� ������� ������
    self.__length2=0              # ����� ������� ������� ������
    self.__angle=90               # ���� ���� ������
    self.__radius=0               # ������ ���� ������
    self.__issymmetry=False       # ������� ��������� ������

  def SetMater(self, mater):
    '''������ �������� ������
    Mater - ID ��������� �� ��������������� �����������
    '''
    self.__panmater=mater
    return True

  def SetTextureAngle(self,texangle):
    '''������ ���� ��������
    texangle - ���� �������� �������� �� ��������� � ����� ������
    ���� texangle=-1 - �������� ������������
    '''
    if (0<=texangle<=90 or texangle==-1):
      self.__texangle=texangle
      return True
    return False

  def SetMajorPlace(self,majorplace):
    '''������ ��������� ������ (�����, ������, ������)
    majorplace - ��������� ������:
    12 - �����,
    11 - ������,
    13 - ��������� ������,
    14 - ������� ������.
    '''
    if (majorplace in Panel.__majortypes):
      self.__majorplace=majorplace
      return True
    return False

  def SetCutAngles(self,anglenum,angletype,*angleparams):
    '''������ �������� ���� � ������� AngleNum
    anglenum - ����� ���� (1, 2, 3, 4),
    angletype - ��� ����,
    angleparams - ������ ���������� ������. �� ������� �� ���� ����
      angletype=0 - ���� ��� ��������. ��������� �����������
      angletype=1 - �����.
        angleparams[0] - �������� �� X
        angleparams[1] - �������� �� Y
      angletype=2 - ����� �������������.
        angleparams[0] - �������� �� X
        angleparams[1] - �������� �� Y
        angleparams[2] - ������
      angletype=3 - ����.
        angleparams[0] - �������� �� X
        angleparams[1] - �������� �� Y
        angleparams[2] - ������ (>0 - ��� �������� ����, <0 - ��� ��������)
      angletype=4 - ����������.
        angleparams[0] - ������
      angletype=5 - ���������.
        angleparams[0] - ������
      angletype=6 - ����� ������������.
        angleparams[0] - �������� �� X
        angleparams[1] - �������� �� Y
        angleparams[2] - �������� ������� �� X
        angleparams[3] - �������� ������� �� Y
    '''
    if (anglenum not in Panel.__anglenums):
      return False
    at=AngleTypes()
    if(at.SetAngle(angletype,*angleparams)==False):
      return False
    self.__angles[anglenum-1]=at
    return True

  def SetCave(self,sidenum,cave):
    '''������ ������ ������� SideNum �� �������� Cave
    sidenum - ����� �������
    cave - �������� �������
    '''
    if (sidenum in Panel.__sidetuple):
      ind=Panel.__sidetuple.index(sidenum)
      self.__caves[ind]=cave
      return True
    return False

  def SetCuts(self,sidenum,cut):
    '''������ ������ ������� SideNum �� �������� Cut
    sidenum - ����� �������
    cut - �������� ��������
    '''
    if (sidenum in Panel.__sidetuple):
      ind=Panel.__sidetuple.index(sidenum)
      self.__cuts[ind]=cut
      return True
    return False

  def SetGabs(self,length,width):
    '''������ �������� ������
    length - ����� ������
    width - ������ ������

    ������ ������� ������ ������ �������������
    '''
    if (length>0 and width>0):
      self.__length=length
      self.__width=width
      self.__panelform="Rectangle"
      return True
    return False

  def  SetFreeForm(self, path):
    '''������ ����� ������ ��� ������������� ���������� �������
    path - ������ ������ �� ���������� �������
    
    ������ ������� ������ ������ �� ������������� �������'''
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
    '''������ ����� ��������������� ������
    *coords - ���������� 4-� ������ ���������������� � �������
    ((x1,y1),(x2,y2),(x3,y3),(x4,y4))
    
    ������ ������� ������ ������ ���������������'''
    if (len(coords)!=4):
      return False
    for c in coords:
      if (len(c)!=2):
        return False
    self.__coords=coords
    self.__panelform="Quadrangle"
    return True

  def SetBychord(self,chordlength,chordarc,width,isaxeY):
    '''���������� ����� ������ � ������ �� �����
    chordlength - ����� ����� ������
    chordarc - ������ ����� ������
    width - ������ ������
    isaxeY - ��� ���� ������ (Y - True, X - False)

    ������� ������ ������ ������ �� �����
    '''
    self.__chordlength=chordlength
    self.__chordarc=chordarc
    self.__width=width
    self.__isaxeY=isaxeY
    self.__panelform="Bychord"
    return True

  def SetBytwolines(self,length1, length2, angle, radius, width, issymmetry, isaxeY):
    '''���������� ����� ������ � ������ �� ���� �������� � ����
    length1 - ����� ������� ������� ������
    length2 - ����� ������� ������� ������
    angle - ���� ���� ������
    radius - ������ ���� ������
    width - ������ ������
    issymmetry - ������� ��������� ������
    isaxeY - ��� ���� ������ (Y - True, X - False)

    ������� ������ ������ ������ �� ���� �������� � ����.
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
    '''�������� ������ � ������
    slot - ������.
    
    ������� ���������� ���������� �������� � ������
    '''
    self.__maxcut=slot._SetNum(self.__maxcut+1)
    self.__slots.append(slot)
    return len(self.__slots)

  def AddCutline(self,cutline):
    '''�������� ������ � ������
    cutline - ������

    ������� ���������� ���������� ������ � ������
    '''
    self.__maxcut=cutline._SetNum(self.__maxcut+1)
    self.__cutlines.append(cutline)
    return len(self.__cutlines)

  def AddBand(self,band):
    '''�������� ������ � ������
    band - ������
    
    ������� ���������� ���������� ������ � ������'''
    # ���������, � ��� �� ��� ����� ������ � ������
    segment=band.GetSegment()
    idpoly=1 # ������ �� ������� ������
    #idpoly=segment.GetSegment()[0]
    idline=segment.GetSegment()[1]
    i=0
    for ba in self.__bands:
      baseg=ba.GetSegment()
      baidpoly=baseg.GetSegment()[0]
      baidline=baseg.GetSegment()[1]
      if (idpoly==baidpoly and idline==baidline): # ����� ������
        del self.__bands[i]
        break
      i+=1
    # ��������� ������
    band.SetSegment2(idpoly,idline)
    self.__bands.append(band)
    return len(self.__bands)

  def AddFixline(self,fixline):
    '''�������� ����� ������� � ������
    fixline - ����� �������
    
    ������� ���������� ���������� ����� ������� � ������'''
    # ���������, � ��� �� ��� ������ ������� � ������ �� ��� �� ��������
    segment=fixline.GetSegment()
    idpoly=1 # ������ �� ������� ������
    #idpoly=segment.GetSegment()[0]
    idline=segment.GetSegment()[1]
    type=fixline.GetType()
    i=0
    for fi in self.__fixlines:
      fiseg=fi.GetSegment()
      fiidpoly=fiseg.GetSegment()[0]
      fiidline=fiseg.GetSegment()[1]
      fitype=fi.GetType()
      if (idpoly==fiidpoly and idline==fiidline and type==fitype): # ����� ����� �������
        del self.__fixlines[i]
        break
      i+=1
    # ��������� ����� �������
    fixline.SetSegment2(idpoly,idline)
    self.__fixlines.append(fixline)
    return len(self.__fixlines)
  
  def SetIncise(self,bIncise):
    '''���������� ������� ������� ������
    bIncise=True -������ �������
    bIncise=False -������ �� �������
    '''
    self.__bIncise=bIncise
    return True

  def AddDecorate(self,decorate):
    '''�������� ������� � ������
    decorate - �������

    ������� ���������� ���������� ������� � ������
    '''
    map=decorate.GetMap()
    variantID=decorate.GetVariantID()
    matID=decorate.GetMatID()
    isvisible=decorate.GetIsVisible()
    # ����, � ��� �� ��� ������ �������
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
    # ��������� �������
    self.__decorates.append(decorate)
    return len(self.__decorates)

  def AddButt(self,butt):
    '''�������� �������� ��������� � ������
    butt - �������� ���������
    
    ������� ���������� ���������� �������� ��������� � ������'''
    # ���������, � ��� �� ��� ����� �� �������� ��������� � ������ �� ��� �� ��������
    segment=butt.GetSegment()
    idpoly=1 # �������� ��������� �� ������� ������
    #idpoly=segment.GetSegment()[0]
    idline=segment.GetSegment()[1]
    type,params=butt.GetType()
    i=0
    for bu in self.__butts:
      buseg=bu.GetSegment()
      buidpoly=buseg.GetSegment()[0]
      buidline=buseg.GetSegment()[1]
      butype,buparams=bu.GetType()
      if (idpoly==buidpoly and idline==buidline and type==butype and params==buparams): # ����� �������� ���������
        del self.__butts[i]
        break
      i+=1
    # ��������� �������� ���������
    butt.SetSegment2(idpoly,idline)
    self.__butts.append(butt)
    return len(self.__butts)

  def AddMill(self,mill):
    '''�������� ���������� � ������
    mill - ����������

    ������� ���������� ���������� ���������� � ������'''
        # ���������, � ��� �� ��� ����� �� ���������� � ������ �� ��� �� ��������
    segment=mill.GetSegment()
    idpoly=1 # ���������� �� ������� ������
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
          and sdv==misdv and issymmetry==miissymmetry and planea==miplanea): # ����� ����������
        del self.__mills[i]
        break
      i+=1
    # ��������� ����������
    mill.SetSegment2(idpoly,idline)
    self.__mills.append(mill)
    return len(self.__mills)

  def Draw(self, x, y, z):
    '''������������ (��������� � �����) ��������� ������
    x,y,z - ���������� ��� ������
    
    ������� ���������� ��������� ������'''
    a=k3.VarArray(10)
    # �������������� ������
    NULLOUT=k3.setpan6par(1,a)
    # ������ �������� ������
    a[0].value=self.__panmater
    NULLOUT=k3.setpan6par(2,a)
    # ������ ��������� �������� ����� ������
    ty=1
    for i in self.__angles:
      a[0].value=ty
      a[1].value=i.GetAngleType()
      Par=i.GetAngleParams()
      for j in range(len(Par)):
        a[j+2].value=Par[j]
      NULLOUT=k3.setpan6par(4,a)
      ty+=1
    # ������ ������� ������
    a[0].value=self.__caves[2]
    a[1].value=self.__caves[1]
    a[2].value=self.__caves[3]
    a[3].value=self.__caves[0]
    NULLOUT=k3.setpan6par(5,a)
    # ������ �������� ������
    a[0].value=self.__cuts[2]
    a[1].value=self.__cuts[1]
    a[2].value=self.__cuts[3]
    a[3].value=self.__cuts[0]
    NULLOUT=k3.setpan6par(6,a)
    # ��������� ������ � ������
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
      # ���������� ������ �� ��� ������
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
      # ���������� ����� ������� �� ��� ������
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
      # ��������� �������� ��������� �� ��� ������
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
      # ��������� ���������� �� ��� ������
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
    # ������ ��� ������ � �������
    paneform=Panel.__panelforms[self.__panelform]
    a[0].value=paneform
    if (paneform==1):   # ������ �� ���������� �������
      a[1].value=self.__formpath
    elif (paneform==2): # ������������� ������
      a[1].value=self.__length
      a[2].value=self.__width
    elif (paneform==3): # ��������������� ������
      i=0
      for c in self.__coords:
        a[1+i].value=c[0]
        a[2+i].value=c[1]
        i+=2
    elif (paneform==4): # ������ �� ����� ������
      a[1].value=self.__chordlength
      a[2].value=self.__chordarc
      a[3].value=self.__width
      a[4].value=self.__isaxeY
    else: # (paneform==5): # ������ �� ���� �������� � ���� ������
      a[1].value=self.__length1
      a[2].value=self.__length2
      a[3].value=self.__angle
      a[4].value=self.__radius
      a[5].value=self.__width
      a[6].value=self.__issymmetry
      a[7].value=self.__isaxeY
    NULLOUT=k3.setpan6par(11,a)
    # ��������� ������� � ������
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
    # ������ ������
    for ba in self.__bands:
      baseg=ba.GetSegment()
      idpoly=baseg.GetSegment()[0]
      idline=baseg.GetSegment()[1]
      a[0].value=idline
      a[1].value=ba.GetType()
      a[3].value=ba.GetMask()
      NULLOUT=k3.setpan6par(3,a)
    # ������ ���� �������� ��������
    a[0].value=self.__texangle
    NULLOUT=k3.setpan6par(19,a)
    # ������ ����������
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
    # ������ ������� �������
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
    # ������ ��������� � ��������� "� ������������"
    a[0].value=self.__majorplace
    a[1].value=self.__bIncise
    NULLOUT=k3.setpan6par(22,a)
    # ������ �������� ���������
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
    # ������ �������
    for de in self.__decorates:
      a[0].value=de.GetMap()
      a[1].value=de.GetVariantID()
      a[2].value=de.GetMatID()
      a[3].value=de.GetIsVisible()
      NULLOUT=k3.setpan6par(28,a)
    # ����������, ������� ������
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