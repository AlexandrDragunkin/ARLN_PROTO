# -*- coding: cp1251 -*-

# ��� ������� ����������:
# 1. ���������� � ����� �� ��������� ��gre � ������ ptvsd
# 2. � ������ ������ ��������
# import ptvsd
# 3. ���������� ������� k3cncw.exe � ���������. 
# ��� ����� � StartProcessing (��������) �������� ������:
# ptvsd.enable_attach(None)
# ptvsd.wait_for_attach(60)
# ������ ������ ��������� ����������� �������, � ������ ���� 60 ������ �� �����������
# 4. � ������, ��� ���������� ����� �������� ��������:
# ptvsd.break_into_debugger()
# 5. ����� ����� ��������� ���������� k3cncw.exe. ����� ����, ��� ������� �����������
# �� 60 ������ � ��������� ����������� � ���������, � Visual Studio �������
# Debug\Attach to process. ��� � ������� ���������� ������ ������� Python remote debuging (unsecure),
# � � ������ ������ 127.0.0.1:5678. ��� ��� � ������ ��������� �������� k3cncw.exe. ��� ������ �������.

#import ptvsd

import machine
import Utiles
from math import sqrt
#import wingdbstub # ������ ������� �������� WING IDE

'''������ � �������, ������������ � ������ machine'''
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
vpi=3.1415926535897932384626433832795     # ����� Pi
eps_d = 0.001 # ���������� ����������
# ���������� �������� �������
xmax=1000
xmin=85
ymax=5000
ymin=285
zmax=50
zmin=8

class Writer:
    '''�����, �������������� ����� ���������� �� ������ Boa. ������ �� ���� ����� ���� � ������ Boa
       � ���� ������ ��������� �������, ���������� �� ����� ���������� � ���������� ��������� � �������� ����'''
    def __init__(self):
# ����� �� ������� ��������� ��������� ��������� ��� ������
        self.header='''[HEADER]
TYPE=BPP
VER=150
'''
        self.description='''[DESCRIPTION]
|
'''
        self.variables='''[VARIABLES]
PAN=LPX|%f||4|
PAN=LPY|%f||4|
PAN=LPZ|%f||4|
PAN=ORLST|"1"||3|
PAN=SIMMETRY|1||1|
PAN=TLCHK|0||1|
PAN=TOOLING|""||3|
PAN=CUSTSTR|$B$KBsSkipperProcessor1.PreProc$V""||3|
PAN=FCN|1.000000||2|
PAN=XCUT|0||4|
PAN=YCUT|0||4|
PAN=JIGTH|0||4|
PAN=CKOP|0||1|
PAN=UNIQUE|0||1|
PAN=MATERIAL|"wood"||3|
PAN=PUTLST|"2"||3|
PAN=OPPWKRS|0||1|
PAN=UNICLAMP|0||1|
PAN=CHKCOLL|0||1|
PAN=WTPIANI|0||1|
PAN=COLLTOOL|0||1|
PAN=CALCEDTH|0||1|
PAN=ENABLELABEL|0||1|
PAN=LOCKWASTE|0||1|
PAN=LOADEDGEOPT|0||1|
PAN=ITLTYPE|0||1|
PAN=RUNPAV|0||1|
PAN=FLIPEND|0||1|
'''
        self.program="[PROGRAM]"
        self.vbscript="[VBSCRIPT]"
        self.macrodata="[MACRODATA]"
        self.tdcodes="[TDCODES]"
        self.pcf="[PCF]"
        self.tooling="[TOOLING]"
        self.subprogs="[SUBPROGS]"
        #                          SIDE CRN   X   Y   Z  DP  DIA THR RTY  DX  DY  R   A   DA  NPR ISO  OPT  AZ  AR  AP CKA XRC YRC ARP LRP  ER  MD COW A21 TOS VTR S21  ID   AZS  MAC   TNM  TTP TCL RSP IOS WSP  SPI  DDS DSP BFC SHP EA21 CEN   AGG        PRS
        self.drill= '''%s, "", "" : %i, "%i", %f, %f, %f, %f, %f, %i, %s, %f, %f, %f, %f, %f, %i, "%s", %i, %f, %f, %i, %i, %f, %f, %f, %f, %i, %i, %i, %f, %i, %i, %i, "%s", %f, "%s", "%s", %i, %i, %i, %i, %i, "%s", %f, %i, %i, %i, %i, "%s", "%s", "%s", %i'''
        #                           ID  SIDE  CRN   Z   DP  ISO   OPT DIA RTY XRC YRC DX  DY  R   A   DA  RDL NRP AZ  AR  ZS  ZE CKA THR  RV CKT ARP LPR  ER COW OVM A21 TOS VTR
        self.mill='''ROUT, "", "" : "%s", %i, "%i", %f, %f, "%s", %s, %f, %s, %f, %f, %f, %f, %f, %f, %f, %s, %i, %f, %f, %f, %f, %s, %i, %s, %s, %f, %f, %s, %i, %f, %f, %i, %i'''
        #     ROUT, "TDCODE1", "" : "P1", 0,   "1",  0,  5, "",   YES, 10, rpNO, 0, 0, 5, 5,  50, 0,  45, YES, 0, 0, 0, 0, 0,    azrNO, 1, NO, NO, 0, 0, NO, 0, 0, 0, 0, 0
        #                                            X   Y   Z  
        self.slot1='''CUT_X, "", "": %i, "%i", %f, %f, 0, %f, %f, 0, %f, "", 1, %f'''
        #                          SIDE CRN   X    Y  Z depth length
        self.slot2='''CUT_G, "", "": %i, "%i", %f, %f, 0, %f, cutXY, 0, 0, %f, %f, 0, 0, "", 1, %f'''
        #                          SIDE CRN   X    Y  Z depth type length angle                 width
        #             CUT_G, "", "": 0, "1", 354.000000, 12.000000, 0, 8.000000, cutLA, -350.000000, 45, 0, 0, 0, 0, "", 1, 7
        #             CUT_G, "", "": 0, "1", 54.000000, 12.000000, 0, 8.000000, cutXY, 0, 0, 100, 80, 0, 0, "", 1, 7
        self.startsegment='''  START_POINT, "", "" : %f, %f, %f '''
        #                                        XE  YE  ZS  ZE  SC  FD  SP  MTV
        self.linesegment= '''  LINE_EP, "", "" : %f, %f, %f, %f, %s, %f, %f, %i'''
        #                                         X2  Y2  XE  YE  ZS  ZE  SC        
        self.arcsegment=  '''  ARC_IPEP, "", "" : %f, %f, %f, %f, %f, %f, %i, %i, 0, 0, %s'''
        #
        self.millend=     '''  ENDPATH, "", "" :'''
        self.DTool = 12       # ������� �����
# ����� �� ������ ������ ��� ������
    def DrillingCommand(self, num, drill):
      '''����� ���������� �� ��������� � ����
      
      num - ���������� ����� ���������
      drill - ���������
      '''
      # x,y,z - ���������� ��������� � ������� ��������� ������
      x=drill.position.x  
      y=drill.position.y
      z=drill.position.z
      # d, h - ������� � ������� ���������, ��������������
      d=drill.diameter
      h=drill.depth
      # alpha - ���� ����� Ox � ��������� ������������ �� Oxy (���� ��������� � �������� ������ ������)
      alpha=drill.alfa
      # beta - ���� ����� Oz � ������������ (���� ��� ��������� � ������ ������)
      beta=drill.beta
      thicknessPanel=drill.panel.thickness
      ## ����� ������ ���������� � ����������� �� ������� ������
      b=Boa()
      side=Utiles.GetDrillPlane(drill)
      siden=b.GetBiesseSideNum(side)
      bb = drill.panel.bounding_box
      Xpanel=bb.max.x-bb.min.x
      Ypanel=bb.max.y-bb.min.y
      crn=4
      thr=0
      if (siden==0):
        crn=4
        if (h>=thicknessPanel):
          thr=1
      if (siden==5):  # ����, ������� ��������� ���
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
      self._Drill(x,y,z,siden,h,d,crn,thr)
      return

    def _Drill(self,x,y,z,side,h,diam,crn=4,thr=0,rty="rpNO",dx=32,dy=32,r=50,a=0,da=45,npr=0,iso="",opt=1,az=0,ar=0,ap=0,cka=0,xrc=0,yrc=0,arp=0,lrp=0,er=1,md=0,cow=0,a21=0,tos=0,vtr=0,s21=-1,id="",azs=0,mac="",tnm="",ttp=0,tcl=0,rsp=0,ios=0,wsp=0,spi="",dds=0,dsp=0,bfc=0,shp=0,ea21=0,cen="",agg="",rps=0):
      if (side==0 or side==5):
        b="BV"  # ��������� ������������
      else:
        b="BH"  # ��������� ��������������
      print (self.drill % (b,side,crn,x,y,z,h,diam,thr,rty,dx,dy,r,a,da,npr,iso,opt,az,ar,ap,cka,xrc,yrc,arp,lrp,er,md,cow,a21,tos,vtr,s21,id,azs,mac,tnm,ttp,tcl,rsp,ios,wsp,spi,dds,dsp,bfc,shp,ea21,cen,agg,b,rps), file = self.OutputFile)
      return

    def SlotCommand(self, num, side, slot):
      ''' ����� ���������� � �������� � ������
      CUT_G, "", "": 0, "1", 354.000000, 12.000000, 0, 8.000000, cutLA, -350.000000, 45, 0, 0, 0, 0, "", 1, 7
      CUT_G, "", "": 0, "1", 54.000000, 12.000000, 0, 8.000000, cutXY, 0, 0, 100, 80, 0, 0, "", 1, 7
      num - ���������� ����� �������
      slot - ������'''
      bb=slot.panel.bounding_box
      Xpanel=bb.max.x-bb.min.x
      Ypanel=bb.max.y-bb.min.y
#      side = 0
#      if slot.is_plane==False:
#	side = 5

      xstart = bb.min.x
      xend = bb.max.x
      ystart = slot.start.y
      yend = slot.end.y
      xstart = Xpanel-xstart
      xend   = Xpanel-xend
      '''
      if side == 0:
	xstart = Xpanel-xstart
	xend   = Xpanel-xend
      else:
	xstart = Xpanel-xstart
	xend   = Xpanel-xend
#	ystart = Ypanel-ystart
#	yend = Ypanel-yend
      '''
      D = 100    # ���������� �� ������ ����� ����
      cutType = 1
      if (Utiles.GetSlotDirection(slot)=="X"):
        self._SlotByCoords(side, xstart, ystart, xend, yend, slot.depth, D, slot.width, cutType )
      return

    def _SlotByCoords(self,side,xbeg,ybeg,xend,yend,depth,D, width,cutType=1,crn=1):
      if cutType == 1:
        print (self.slot1 % (side,crn, xbeg,ybeg,depth,xend-xbeg, D, width), file = self.OutputFile)
#      else:
#	print >> self.OutputFile, self.slot2 % (side,crn, xbeg,ybeg,depth,xend, yend, width)
      return
  
    def MillingSlot(self, num, slot):
      bb = slot.panel.bounding_box
      Xpanel=bb.max.x-bb.min.x
      Ypanel=bb.max.y-bb.min.y
      z = slot.depth
      if self.DTool < slot.width:
        self._MillOperation("P"+str(num+1),0,2,0,z)
        dx = slot.end.x-slot.start.x
        dy = slot.end.y-slot.start.y
        l = sqrt(dx*dx + dy*dy)
        x = dy/l*slot.width*0.5
        y = dx/l*slot.width*0.5
        xstart = Xpanel-slot.start.x
        ystart = Ypanel-slot.start.y
        xend = Xpanel-slot.end.x
        yend = Ypanel-slot.end.y
        x1 = xstart+x
        y1 = ystart-y
        x2 = xend+x
        y2 = yend-y
        x3 = xend-x
        y3 = yend+y
        x4 = xstart-x
        y4 = ystart+y
        self._MillStartSeg(x1,y1,z)
        self._MillLineSeg(x2,y2)
        self._MillLineSeg(x3,y3)
        self._MillLineSeg(x4,y4)
        self._MillLineSeg(x1,y1)
        self._MillEnd()
      return

    def MillingCommand(self, num, segment, isouter=True, last=False):
      '''����� ���������� � ���������� ������
      
      num - ���������� ����� ��������
      segment - ������� ����������
      isouter - ������� �������� �������'''
      Xpath=segment.path.panel.panel_length
      Ypath=segment.path.panel.panel_width
      if (type(segment)==machine.Line) or (type(segment)==machine.Arc):
        xbeg=Xpath-segment.start_pt.x
        ybeg=Ypath-segment.start_pt.y
        xend=Xpath-segment.end_pt.x
        yend=Ypath-segment.end_pt.y
      elif type(segment)==machine.Circle:
        xbeg=(Xpath-segment.center.x) + segment.radius
        yend = ybeg=Ypath-segment.center.y
        xend = (Xpath-segment.center.x) - segment.radius
      else:
        print (" ��������� ��� ��������")
        return
      z=segment.path.panel.thickness
      #if (isouter==True):
      #  corr=2  # ������ ���������
      #else:
      #  corr=1  # ����� ���������
      if (num==1):
        self._MillOperation("P1",0,2,0,z)
        self._MillStartSeg(xbeg,ybeg,z)
      if (type(segment)==machine.Line):
        self._MillLineSeg(xend,yend)
      elif (type(segment)==machine.Arc):
        x3 = Xpath-segment.middle_pt.x
        y3 = Ypath-segment.middle_pt.y
        self._MillArcSeg(x3,y3,xend,yend)
      elif (type(segment) ==machine.Circle):
        x3 = Xpath-segment.center.x
        y3 = Ypath-segment.center.y + segment.radius
        self._MillArcSeg(x3,y3,xend,yend)
        y3 = Ypath-segment.center.y - segment.radius
        self._MillArcSeg(x3,y3,xbeg,ybeg)
      if (last==True):
        self._MillEnd()
      return

    def _MillOperation(self,id,side,crn,z,dp,dia=10,iso="",opt="YES",rty="rpNO",xrc=0,yrc=0,dx=5,dy=5,r=50,a=0,da=45,rdl="YES",nrp=0,az=0,ar=0,zs=0,ze=0,cka="azrNO",thr=1,rv="NO",ckt="NO",arp=0,lpr=0,er="NO",cow=0,ovm=0,a21=0,tos=0,vtr=0):
      print (self.mill % (id,side,crn,z,dp,iso,opt,dia,rty,xrc,yrc,dx,dy,r,a,da,rdl,nrp,az,ar,zs,ze,cka,thr,rv,ckt,arp,lpr,er,cow,ovm,a21,tos,vtr), file = self.OutputFile)
      return

    def _MillStartSeg(self,x,y,z):
      print (self.startsegment % (x,y,z), file = self.OutputFile)
      return

    def _MillLineSeg(self,x,y,zs=0,ze=0,sc="scOFF",fd=0,sp=0,mtv=0):
      print (self.linesegment % (x,y,zs,ze,sc,fd,sp,mtv), file = self.OutputFile)
      return

    def _MillArcSeg(self,x2,y2,xe,ye,zs=0,ze=0,fd=0,sp=0,sc="scOFF"):
      print (self.arcsegment % (x2,y2,xe,ye,zs,ze,fd,sp,sc), file = self.OutputFile)
      return

    def _MillEnd(self):
      print ( self.millend, file = self.OutputFile)
      return

    def DataHeadCommand(self, x, y, z):
      '''����� ���������� � ��������� ����'''
      print (self.header, file = self.OutputFile)
      print (self.variables % (x,y,z), file = self.OutputFile)
      return

    def BeginProgram(self):
      print (self.program, file = self.OutputFile)

    def BeginVBScript(self):
      print (self.vbscript, file = self.OutputFile)

    def BeginMacroData(self):
      print (self.macrodata, file = self.OutputFile)

    def BeginTDCodes(self):
      print (self.tdcodes, file = self.OutputFile)

    def BeginPCF(self):
      print (self.pcf, file = self.OutputFile)

    def BeginTooling(self):
      print (self.tooling, file = self.OutputFile)

    def BeginSubProgs(self):
      print (self.subprogs, file = self.OutputFile)

    def CreateOutputFile(self,FileName):
      '''��������� �� ������ ���� � ������ FileName'''
      self.fname=FileName
      self.OutputFile = open(FileName, 'w') 
      return        

    def CloseOFile(self):
      '''��������� ���� ��������� '''
      self.OutputFile.close()
      return

class Boa(machine.Machine):
    '''
    ��� ����� ������� �����. ������ ��� ������ ����������� ��� ������ ����������
    ��� ����� ����� ������� � ������ �������� ������ (*_settings)
    ���� ����� �������� ����������� ������ Machine, ������� ���������� � Machine.pyd

    ������ ����������� � ��������� ������������������:
      StartProcessing(model) - ��� ���� ������ (����)
      StartPanel(panel)      - ��� ������ �� �������
        Drilling(drill)      - ��� ������� �� ��������� ������
        Slot(slot)           - ��� ������� �� �������� ������
        Milling(mill,curve)  - ��� ������ ���������-���������� ������
        Filletting(fillet,curve) - ��� ������ ���������-��������� ������
      EndPanel()             - ��� ������ �� �������
      EndProcessing()        - ��� ���� ������ (����)
    '''
    def __init__(self):
      ''' ������������ ������'''
      machine.Machine.__init__(self)            # �������� ����������� �������� ������. ����� ��� �����������
      '''
      Machine - �����, ������������ ��������� ����� ��� ������
      ������ ������:
		    StartProcessing(model) - ����� ���������� ���� ��� ����� ������� ��������� ��������� ������
		    EndProcessing() - ����� ���������� ����� ��������� ��������� ������
		    StartPanel(panel) - ������ ��������� ������
		    EndPanel() - ����� ��������� ������
		    Drilling(drill) - ��������� ������
		    Slot(slot) - ������ ������
		    Milling(mill,curve) - ���������� ������
		    Filletting(fillet,curve) - ���������
      '''
      self.settings = machine.Settings()        # ����������, �������� ������ �� ����� Settings
      '''
	    Settings - ����� ������������� ������ � ���������� ����������, �������� ������ ������� ������� ������.
      �������� ������:
		    machine_name - ��� ������, ������� ����� ������������ ������� ��� ������.
		    machine_module_name - ��� ����� � ������� ��������� ���������� ������.
		    database_name - ���� � ���� ������ ��������.
		    cmdfile_path - ��� ������������� ���������� �����.
		    working_area - BoundingBox2d ������������ ������� ������� ������.
      '''
      self.writer = Writer()                    # ����� ��� ������ ���������� � ����

      # ��������� ������������� ���������
      self.panelThickness = 16     # ������� ������
      self.panelWidth = 0         # ������ ������
      self.panelLength = 0        # ����� ������
      self.panelNum = -1          # ����� ������ (�������� �������� CommonPos)
      self.millingTech = []       # ������ �������� ��� ���������

      self.isBlindHoleF = False # ������ ��������� �� F
      self.fname="" # ��� ����� ����������� ���������
      self.panelName="" #��� ������

    def CreateCmdfile(self,post):
      '''������� ���� � ����������� ����������
      
      post - ��� �����'''    
      fname=post+".bpp"
      self.cmdfileName = self.GetCmdfilePath()
      self.cmdfileName +=fname
      self.writer.CreateOutputFile(self.cmdfileName)
      return

    def GetCmdfilePath(self):
        '''������ ��� �����'''
        path = self.settings.cmdfile_path
        try:
            machine.makedirs(path)
        except OSError:
            pass
        return path

    def GetBiesseSideNum(self,sideName):
      '''������� ����� ������� � ������� BiesseWorks'''
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
      '''���������� ����� ��������� � ��������� ����'''
      self.writer.DataHeadCommand(self.panelLength,self.panelWidth,self.panelThickness)
      return

    def CreateCmdfileProgram(self, postfix):
      '''���������� ����� ��������� � ��������� ����'''
      self.writer.BeginProgram()
      self.writerDrillingCommand(self.drills)
      self.writerContours(self.millingTech)
      side = 0
      if postfix == "_AE" or postfix == "_AC":
        side = 0
      elif postfix == "_FD" or postfix == "_FC":
        side = 5
      self.writerSlotsCommand(side, self.slots) #NSH
      if side == 0:
        self.writerMillingSlots(self.millingSlots)
      return

    def CreateCmdfileVBScript(self):
      '''���������� ���������� ������ � ��������� ����'''
      self.writer.BeginVBScript()
      return

    def CreateCmdfileMacroData(self):
      '''���������� ����������� � ��������� ����'''
      self.writer.BeginMacroData()
      return

    def CreateCmdfileTDCodes(self):
      '''���������� TD ���� � ��������� ����'''
      self.writer.BeginTDCodes()
      return

    def CreateCmdfilePCF(self):
      '''���������� PCF � ��������� ����'''
      self.writer.BeginPCF()
      return

    def CreateCmdfileTooling(self):
      '''���������� ����������� � ��������� ����'''
      self.writer.BeginTooling()
      return

    def CreateCmdfileSubProgs(self):
      '''���������� ������������ � ��������� ����'''
      self.writer.BeginSubProgs()
      return

    def StartProcessing(self,model):
      '''����� ����������� ������������� ����� ������� ��������� �������'''
#      ptvsd.enable_attach(None)
#      ptvsd.wait_for_attach(60)
      pass

    def EndProcessing(self):
      '''����� ����������� ������������� ����� ��������� ��������� �������'''
      print (" ")
      print ('������ CNC �������� ������')
      print ('��������� ��� ��������� � �����:')
      print ('   '+self.settings.cmdfile_path)
      return

    def writeOutputFile(self, postfix):
        '''���������� ����������� ���������� �  ����'''
        # �������� ��� �����
        index = self.NumOrder+str(self.panelNum) + postfix
        # ������� ����
        self.CreateCmdfile(index)
        # ����� � ���� �����
#        ptvsd.break_into_debugger()
        self.CreateCmdfileHeading()
        # ����� � ���� �� ������� ��� ������
        self.CreateCmdfileProgram(postfix)
        self.CreateCmdfileVBScript()
        self.CreateCmdfileMacroData()
        self.CreateCmdfileTDCodes()
        self.CreateCmdfilePCF()
        self.CreateCmdfileTooling()
        self.CreateCmdfileSubProgs()
        self.writer.panelName=self.panelName
        self.writer.CloseOFile()
        print ("������ � "+str(self.panelNum), " ������ � ����", index,".bpp")

    def StartPanel(self, panel):
      '''����� ���������� ������������� ����� ������� ��������� ������ ������'''
      self.millingTech = []
      self.drills=[]
      self.slots = [] # �������
      self.millingSlots = []
      self.workingsides=[]        # ������ ������ ������, ������� ����� ����� ����������
      self.writer=Writer()
      self.isSlotsFX = False
      self.isSlotsFY = False
      self.isSlotsAY = False
      self.isBlindHoleF = False

      self.fname="" # ��� ����� ����������� ���������
      self.panelName=panel.name
      self.panel = panel
      b = self.panel.bounding_box
      self.NumOrder = ''
      self.Selobj = 0
      for a in self.panel.attributes:
        if a.name=='Selobj':
          self.Selobj = int(a.value)
        if a.name=='NumOrder':
          self.NumOrder = str(a.value)+"_"
      # ����������� ������� ������ � ������������ �� ������� �������� ����� X
      #Xpanel=b.max.x-b.min.x
      #Ypanel=b.max.y-b.min.y
      self.panel.Translate(machine.Vector2d(-b.min.x,-b.min.y))
      self.panelThickness = panel.thickness
      self.panelWidth = self.panel.panel_width
      self.panelLength = self.panel.panel_length
      self.panelNum = panel.common_pos
      # �������� �������
      self.Contour()
      return True

    def writerContours(self, pathsTuple):
      '''������� �������������� � ������ �������
      pathsTuple - ������ ��������, ������� ����� ����������'''
      outer=True
      for p in pathsTuple:
        segments=p.segments
        a=0
        last=False
        for s in segments:
          a=a+1
          if (a==len(segments)):
            last=True
          self.writer.MillingCommand(a,s,outer,last)
        outer=False
      return

    def writerSlotsCommand(self, side, slotsTuple):
      '''��������������� � ������ �������
      side - ������� �������
      slotsTuple - ������ �������� � ������ ������'''
      if (side!=0 and side != 5): # ������� � ��� ������ �� ������ �������
        return
      a=0
      for s in slotsTuple:
        if (s.is_plane==True):       # Utiles.GetSlotDirection(s)=="X" and 
          a=a+1
          self.writer.SlotCommand(a, side, s)
      return
  
    def writerMillingSlots(self, millingSlots):
      ''' ����� ������������ � ����� �������� ������ '''
      a = 0
      for s in millingSlots:
        a = a+1
        self.writer.MillingSlot(a, s)
      return

    def writerDrillingCommand(self, drillTuple):
      '''��������������� � ������ ���������
      drillTuple - ������ ��������� � ������ ������'''
      for d in drillTuple:
        SideS=Utiles.GetDrillPlane(d)
        SideNum=self.GetBiesseSideNum(SideS)
        if (SideNum<0 or SideNum==5): # ���� ������� �� ����������,��� ��� ������� F, ��������� �� �������
          continue
        self.writer.DrillingCommand(drillTuple.index(d),d)
      return

    def EndPanel(self):
      '''������� ���������� � ����� ��������� ������ ������'''
      if (self.Selobj == 0):  # ���� ��� �� ��������� ������, �� �� ��� �� ������������
        return
      b = self.panel.bounding_box
      Ypanel=b.max.y-b.min.y
      Xpanel=b.max.x-b.min.x
      # ���� ����������, �������� �� ��������
      # Utiles.CheckGabs(self,panel,xmin,xmax,ymin,ymax,zmin,zmax)
      # ���������� ������� � ���������. ��� ��� �����������
      #slotsave=self.slots
      drillsave=self.drills
      self.writeOutputFile('_AE') # ������� ���� ������ � ����� � ���� ����������� ����������.
      ## ���� ���� ������� ����� Y �� ������� A, ������������ ������
      if (self.isSlotsAY==True):
        # ������������ ������������ ������� �������� ����
        self.panel.Rotate(vpi/2,machine.Point2d(0,Ypanel))
        b = self.panel.bounding_box
        Xpanel,Ypanel=Ypanel,Xpanel
        self.panel.Translate(machine.Vector2d(-b.min.x,-b.min.y))
        self.panelWidth = self.panel.panel_length
        self.panelLength = self.panel.panel_width
        self.workingsides=[]
        self.workingsides.append(1)
        # ������� ����������
        self.millingTech=[]
        self.writeOutputFile("_AC")
        # ���������� ������� ����
        self.panel.Translate(machine.Vector2d(b.min.x,b.min.y))
        self.panel.Rotate(-vpi/2,machine.Point2d(0,Xpanel))
        Xpanel,Ypanel=Ypanel,Xpanel
        self.panelWidth = self.panel.panel_width
        self.panelLength = self.panel.panel_length

      # ���� ���� ������ ��������� ��� ������� � �������� �������, ���� ��� ����������� ������
      if (self.isBlindHoleF==True or self.isSlotsFX==True or self.isSlotsFY== True):
        drlist=[]
        # ������� ��� ���������, ����� ������ �� F
        for d in self.drills:
          if (Utiles.GetDrillPlane(d)=="F"):
            drlist.append(d)
        self.drills=drlist
        # ������� ����������
        self.millingTech=[]
        # �������������� ������������ ��� X
        b = self.panel.bounding_box
        self.panel.Overturn(0)
        self.panel.Rotate(-vpi,machine.Point2d(0,Xpanel))
        self.panel.Translate(machine.Vector2d(Xpanel-b.min.x,0))
        if (self.isBlindHoleF==True or self.isSlotsFX==True):
          self.writeOutputFile("_FD") 

      ## B ��������� - ������� �� F ����� Y
        if (self.isSlotsFY==True):
        # ������������ ������������ ������� �������� ����
          self.panel.Rotate(vpi/2,machine.Point2d(0,Ypanel))
          Xpanel,Ypanel=Ypanel,Xpanel
          b = self.panel.bounding_box
          self.panel.Translate(machine.Vector2d(-b.min.x,-b.min.y))
          self.panelWidth = self.panel.panel_length
          self.panelLength = self.panel.panel_width
          self.writeOutputFile("_FC")
      return

    def Drilling(self, d):
      '''���������. ������ � �����. ��������� ������ ����������� ��� ������� � ������'''
      if (self.Selobj == 0):  # ���� ��� �� ��������� ������, �� �� ��� �� ������������
        return
      self.drills.append(d)
      Side=Utiles.GetDrillPlane(d)
      if (Side=="F"):
        self.isBlindHoleF=True
      return

    def Slot(self, s):
      '''�������. ��������� ������ ����������� ��������'''
      if (self.Selobj == 0):  # ���� ��� �� ��������� ������, �� �� ��� �� ������������
        return
      if (s.params["SlotType"][0] == 1):
        self.slots.append(s)
        slotDir = Utiles.GetSlotDirection(s)
        if (s.is_plane==True and  slotDir=="Y"): # ���� ������ �� ������� A ����� Y
          self.isSlotsAY = True
        elif (s.is_plane==False and slotDir == "X"): # ���� ������ �� ������� F ����� X
          self.isSlotsFX=True
        elif (s.is_plane==False and slotDir == "Y"): # ���� ������ �� ������� F ����� Y
          self.isSlotsFY=True
      else:
        self.millingSlots.append(s)
      return

    def Contour(self):
      '''�������. ��������� ������ ��������� ��� ����������'''
      if (self.Selobj == 0):  # ���� ��� �� ��������� ������, �� �� ��� �� ������������
        return
      # �������� ������ �������� ������.
      paths=self.panel.paths
      # ���������. ���� ������ ���� � ������� �� 4 ��������, �� ����������� �� ����
      for path in paths:
        if (path.is_tcuts==True or path.is_plane_path==False):
          continue
        else:
          bbox=path.bounding_box
          segments=path.segments
          if (len(segments)!=4):    # ���� ������ ������� �� �� 4-� ��������, �� �� �������� ������. ��� ���������
            self.millingTech.append(path)
            continue
          for segment in segments:
            if (type(segment)!=machine.Line):
              self.millingTech.append(path)
              break
            else:
              # ���� ����� �� �������������� � �� ������������ - ��������� ������
              Xst = segment.start_pt.x
              Yst = segment.start_pt.y
              Xen = segment.end_pt.x
              Yen = segment.end_pt.y
              if (abs(Xst-Xen)>eps_d and abs(Yst-Yen)>eps_d):
                self.millingTech.append(path)
                break
              # C��������� � ���������� BoundingBox ���� ���� �� ���� ����� �� �� bbox - ��������� ������
              if ((abs(Xst-bbox.min.x)>eps_d and abs(Xst-bbox.max.x)>eps_d) or  
                  (abs(Xen-bbox.min.x)>eps_d and abs(Xen-bbox.max.x)>eps_d) or  
                  (abs(Yst-bbox.min.y)>eps_d and abs(Yst-bbox.max.y)>eps_d) or 
                  (abs(Yen-bbox.min.y)>eps_d and abs(Yen-bbox.max.y)>eps_d)):
                self.millingTech.append(path)
                break
      return

    def Milling(self, m, s):
      '''����������. ��������� ������ ����������'''
      return

    def Filletting(self, f, s):
      pass
