# -*- coding: utf-8 -*-
#import wingdbstub
# Generated  by generateDS.py.
# macro protopath+"blum_sub7.py" ;
#-------------------------------------------------------------------------------
# Name:        Blum_sub7
# Purpose:     Модуль интеграции BlumDynalog&K3_Mebel
#
# Author:      Aleksandr Dragunkin
#
# Created:     10.12.2012
# Copyright:   (c) GEOS 2012 http://k3info.ru/
# Licence:     FREE
#-------------------------------------------------------------------------------
import mKarcas
import mPanel as mP
import gUtilitesK3 as gU
import mSlot as mS
import mBand as mB
import mfix  as mF
import DynaplanSupport as mDy
import k3
import sys
import time


import Blum_api7 as supermod

gTypeQuader = None # Передает тип панели в Quader
gTypepanel = None # Значения атрибута ID например LinkeSeitenwand.Seitenwand.ID
dynalog = mDy.Dynalog()

gExportPath = dynalog.projectFolder #.USERPROFILE+'\Documents\Blum\Dynaplan\Export\\' # путь к папке для экспорта из Dynaplan




etree_ = None
Verbose_import_ = False
(   XMLParser_import_none, XMLParser_import_lxml,
    XMLParser_import_elementtree
    ) = list(range(3))
XMLParser_import_library = None
try:
    # lxml
    from lxml import etree as etree_
    XMLParser_import_library = XMLParser_import_lxml
    if Verbose_import_:
        print("running with lxml.etree")
except ImportError:
    try:
        # cElementTree from Python 2.5+
        import xml.etree.cElementTree as etree_
        XMLParser_import_library = XMLParser_import_elementtree
        if Verbose_import_:
            print("running with cElementTree on Python 2.5+")
    except ImportError:
        try:
            # ElementTree from Python 2.5+
            import xml.etree.ElementTree as etree_
            XMLParser_import_library = XMLParser_import_elementtree
            if Verbose_import_:
                print("running with ElementTree on Python 2.5+")
        except ImportError:
            try:
                # normal cElementTree install
                import cElementTree as etree_
                XMLParser_import_library = XMLParser_import_elementtree
                if Verbose_import_:
                    print("running with cElementTree")
            except ImportError:
                try:
                    # normal ElementTree install
                    import elementtree.ElementTree as etree_
                    XMLParser_import_library = XMLParser_import_elementtree
                    if Verbose_import_:
                        print("running with ElementTree")
                except ImportError:
                    raise ImportError("Failed to import ElementTree from any known place")



def parsexml_(*args, **kwargs):
    if (XMLParser_import_library == XMLParser_import_lxml and
        'parser' not in kwargs):
        # Use the lxml ElementTree compatible parser so that, e.g.,
        #   we ignore comments.
        kwargs['parser'] = etree_.ETCompatXMLParser()
    doc = etree_.parse(*args, **kwargs)
    return doc

#
# Globals
#

ExternalEncoding = 'cp1251'

#
# Data representation classes
#
class OutBlockPoints:
    def __init__(self):
        self.pDict = {}

dictBP = OutBlockPoints() # Координаты базовых точек внешних блоков в ГСК

class gZilinder:
    def __init__(self):
        self.obj = None
        self.status = True
gListZilinder = []

class VarInst():
    def __init__(self):
        tmp = k3.Var()
        k3.getvarinst(1,"DySeiteMat",tmp,k3.dbvar("SeiteMat",495))
        self.seitematerial = tmp.value
        k3.getvarinst(1,"DyBaseMat",tmp, k3.dbvar("BaseMat",495))
        self.basematerial = tmp.value
        k3.getvarinst(1,"DyBackMat",tmp, k3.dbvar("BackMat",314))
        self.backmaterial= tmp.value
        k3.getvarinst(1,"DyInnenFMat",tmp, k3.dbvar("InnenFMat",495))
        self.InnenFachmaterial = tmp.value
        k3.getvarinst(1,"DyFrontMat",tmp, k3.dbvar("FrontMat",495))
        self.FrontTypematerial = tmp.value
        k3.getvarinst(1,"Dy_H",tmp, k3.dbvar("H",720))
        self.H = tmp.value
        k3.getvarinst(1,"Dy_D",tmp, k3.dbvar("W",560))
        self.D = tmp.value
        k3.getvarinst(1,"Dy_W",tmp, k3.dbvar("T",600))
        self.W = tmp.value
        k3.getvarinst(1,"Dy_FixCorp",tmp, k3.dbvar("FixCorp",0))
        self.FixCorp = tmp.value
        k3.getvarinst(1,"Dy_FixBp",tmp, k3.dbvar("FixBp",0))
        self.FixBp = tmp.value
        k3.getvarinst(1,"Dy_BandType",tmp, k3.dbvar("BandType",0))
        self.BandType = tmp.value
        k3.getvarinst(1,"Dy_KorpusPan",tmp,int(k3.dbvar("KorpusPan",1)))
        self.lV = tmp.value
        k3.getvarinst(1,"Dy_KorpBlumType",tmp,int(k3.dbvar("KorpBlumType",1)))
        l_KorpBlumType = {1:'Standardkorpus1',2:'Standardkorpus2',3:'Standardkorpus3'}
        self.KorpBlumType = l_KorpBlumType[tmp.value]
        k3.getvarinst(1,"Dy_BackBlumType",tmp,int(k3.dbvar("BackBlumType",1)))
            #Наложение встык    1
            #С фальцем    2
            #С пазом    3
            #С пазом - наложение сверху    4
            #С фальцем - наложение сверху    5
            #Вкладная    6
            #Вкладная - наложение сверху    7
        l_BackBlumType = {1:1,2:2,3:3,4:4,5:5,6:6,7:7}
        self.BackBlumType = l_BackBlumType[tmp.value]
        k3.getvarinst(1,"Dy_CoverBlumTyp",tmp,int(k3.dbvar("CoverBlumTyp",1)))
        l_CoverBlumTyp = {1:1,2:2,3:3}
        self.CoverBlumTyp = l_CoverBlumTyp[tmp.value]

varinst = VarInst()


class DefaultMaterial:
    '''Служит для задания и хранения ID материалов панелей и прочих умолчаний'''
    def __init__(self):
        self.seitematerial=None
        self.basematerial=None
        self.backmaterial=None
        self.panel_K3=None
        self.object_K3=k3.Var()
        self.InnenFachmaterial = None
        self.backmaterial = None
        self.FrontTypematerial =None
        self.HoldPosition = None
        self.karNumb = None
        self.FurnType = None
        self.macro = None
        self.slots = []

    def getThickness(self,material):
        return k3.priceinfo(material,'Thickness',0,1)
# end class DefaultMaterial

defmaterial=DefaultMaterial()
defmaterial.seitematerial       = varinst.seitematerial
defmaterial.basematerial        = varinst.basematerial
defmaterial.InnenFachmaterial   = varinst.InnenFachmaterial
defmaterial.backmaterial        = varinst.backmaterial
defmaterial.FrontTypematerial   = varinst.FrontTypematerial
defmaterial.FixCorp             = varinst.FixCorp
defmaterial.FixBp               = varinst.FixBp
defmaterial.BandType            = varinst.BandType
lV                              = varinst.lV

variantKarkas = False

intToLog = lambda tt: True if tt==1  else False
gVarKorpus = intToLog(lV)  # Создавать панели корпуса или нет True - создавать



#--------------------------------------
class CarcasK3:
    def __init__(self):
        self.object_k = None
        self.numkar = None
carcasK3 = CarcasK3()
#--------------------------------------
class HolderArt:
    def __init__(self):
        self.object = None
        self.art = None
holderart = HolderArt()


#--------------------------------------
class Isdebug:
    def __init__(self):
        self.debug = True
        self.logfile = None
        dynalog = mDy.Dynalog()
        self.createLog ()

    def Print(self,*arg):
      pass
#        if self.debug:
#            print(arg)

    def createLog(self,logfile=dynalog.projectFolder+'K3.log'):
        try:
            self.logfile = open(logfile, "wb")
        except FileNotFoundError :
            print('Данные по DYNALOG устарели или неверны. Будет произведен новый поиск данных')
            dynalog.deletePicle()
            dynalog.set_files_and_pathes()
            try:
                self.logfile = open(logfile, "wb")
            except FileNotFoundError :
                raise FileNotFoundError
            
            

    def addLog(self,addStr=None):
        self.logfile.write(bytes(addStr, "cp1251"))

    def closeLog(self):
        self.logfile.close()

ISDEBUG = Isdebug()


#--------------------------------------

class KorpusSub(supermod.Korpus):
    '''Класс Корпус существует в единственном экземпляре'''
    def __init__(self, Name=None, Header=None, Parameterliste=None, Korpusdaten=None, Oberboden=None, Unterboden=None, LinkeSeitenwand=None, RechteSeitenwand=None, KorpusRueckwand=None, Platten=None, KorpusAnbindung=None, Tuer=None, Doppeltuer=None, Blindfront=None, Aussenschubkasten=None, Innenschubkasten=None, Traverse=None, Klappensystem=None, InnenFach=None, OffenesFach=None, Vorratsauszug=None, SERVODRIVE=None):
        super(KorpusSub, self).__init__(Name, Header, Parameterliste, Korpusdaten, Oberboden, Unterboden, LinkeSeitenwand, RechteSeitenwand, KorpusRueckwand, Platten, KorpusAnbindung, Tuer, Doppeltuer, Blindfront, Aussenschubkasten, Innenschubkasten, Traverse, Klappensystem, InnenFach, OffenesFach, Vorratsauszug, SERVODRIVE, )
        self.objects = None

    def DrawTT(self):
        if variantKarkas == True:
            k3.mbcarcase(k3.k_groupall)
        self.objects = k3.sysvar(60)

    def GroupChildObjectK3(self):
        if self.objects  is not None:
            #print 'self.objects = ',self.objects
            self.objects=k3.sysvar(60)-self.objects
            #print 'self.objects = ',self.objects
            if self.objects>0:
                #k3.setucs(k3.k_move,self.PosIsZero(self.PositionX),self.PosIsZero(self.PositionY),self.PosIsZero(self.PositionZ))
                #k3.group(k3.k_last,self.objects,k3.k_done)
                # Все отверстия принадлежащие панелям корпуса требуется собрать в общуюю группу
                holegrkey = False # ключик былали создана группа
                holegr = k3.Var() # объект та самая группа
                h_hole = k3.Var() # для
                nObj = k3.getcntobjs()
                arrObj = k3.VarArray(int(nObj))
                err = k3.getarrobjs(arrObj)
##                for holeZ in gListZilinder: # цикл по отверстиям выбираем безхозные и создаем из них группу
##                    hole = holeZ.obj
##                    holeZ.status = False
##                    for iobj in range(int(nObj)):
##                        if hole.value==arrObj[iobj].value:
##                            print "****"
##                        if k3.compareobj(hole.value,arrObj[iobj].value)==True:
##                            holeZ.status = True

                for holeZ in gListZilinder: # цикл по отверстиям выбираем безхозные и создаем из них группу
                    hole = holeZ.obj
                    if k3.getobjhold(hole,h_hole) == False:
##                    if holeZ.status == True:
                        if holegrkey == False:
                            k3.group(hole.value,k3.k_done)
                            k3.objident(k3.k_last,1,holegr)
                            holegrkey = True
                        else:
                            k3.add(holegr.value,hole.value,k3.k_done)

                if holegrkey == True:
                    k3.attrobj(k3.k_attach,"ElemName",k3.k_done,holegr.value,str('Блок сверловки'))
                    k3.attrobj(k3.k_attach,"FurnType",k3.k_done,holegr.value,str(('800000')))
                    k3.attrobj(k3.k_attach,'Assembly','ObjType','PlaceType',k3.k_done,holegr.value,1,0,0)
                    if variantKarkas == True:
                        k3.attrobj(k3.k_attach,'Karkasnumb',k3.k_done,holegr.value,carcasK3.numkar)


                ISDEBUG.closeLog()
                GRP=k3.Var()
                if variantKarkas == True:
                    k3.setucs(k3.k_lcs,carcasK3.object_k)
                    k3.mbcarcase(k3.k_group,carcasK3.object_k)
                    k3.group(k3.k_last,1,k3.k_done)
                else:
                    k3.setucs(k3.k_restore,"KarkasUcs")
                    k3.group(k3.k_all,k3.k_done)
                k3.objident(k3.k_last,1,GRP)
                PRJ_listInfo = mDy.impProjectFilesToStr(dynalog.projectFolder,dynalog.rootNameFile,dynalog.listExtensionRoot)
                if len(PRJ_listInfo)>0:
                    for name_ext in dynalog.listExtensionRoot:
                        if k3.isattrdef("Blum"+name_ext)==False:
                            k3.attribute(k3.k_create, "Blum"+name_ext, str(("Файл проекта "+ name_ext)), k3.k_text, 40, 255)
                    for i in range(len(PRJ_listInfo)):
                        arr = k3.VarArray(len(PRJ_listInfo[i]))
                        for j in range(len(PRJ_listInfo[i])):
                            sTemp = ''
                            for a in PRJ_listInfo[i][j]:
                                sTemp += chr(a)
                            arr[j].value = sTemp
                            #print arr[j].value
                        if len(PRJ_listInfo[i])>0:
                            res = k3.textbystr(GRP,str("Blum"+dynalog.listExtensionRoot[i]),len(PRJ_listInfo[i]),arr)
                            #print dynalog.listExtensionRoot[i],"   ",res

                #k3.setucs(k3.k_previous)
                #k3.attrobj(k3.k_attach,"ElemName",'Article',k3.k_done,GRP.value,str(self.Schubkastenart)+' '+str(self.Auszugslaenge),str(self.Name))

supermod.Korpus.subclass = KorpusSub
# end class KorpusSub


class HeaderTypeSub(supermod.HeaderType):
    '''Шапка проекта'''
    def __init__(self, BXFVersion=None, Datum=None, Ersteller=None, Attribut=None):
        super(HeaderTypeSub, self).__init__(BXFVersion, Datum, Ersteller, Attribut, )
supermod.HeaderType.subclass = HeaderTypeSub
# end class HeaderTypeSub


class ParameterlisteTypeSub(supermod.ParameterlisteType):
    def __init__(self, DSKorpus=None, Korpusinformationen=None, Anwendungsinformationen=None, Sonderregeln=None):
        super(ParameterlisteTypeSub, self).__init__(DSKorpus, Korpusinformationen, Anwendungsinformationen, Sonderregeln, )
supermod.ParameterlisteType.subclass = ParameterlisteTypeSub
# end class ParameterlisteTypeSub


class KorpusinformationenTypeSub(supermod.KorpusinformationenType):
    def __init__(self, Attribut=None, Oberbodenkonstruktion=None, Rueckwandkonstruktion=None):
        super(KorpusinformationenTypeSub, self).__init__(Attribut, Oberbodenkonstruktion, Rueckwandkonstruktion, )
supermod.KorpusinformationenType.subclass = KorpusinformationenTypeSub
# end class KorpusinformationenTypeSub


class AnwendungsinformationenTypeSub(supermod.AnwendungsinformationenType):
    def __init__(self, Allgemein=None, Anwendung=None):
        super(AnwendungsinformationenTypeSub, self).__init__(Allgemein, Anwendung, )
supermod.AnwendungsinformationenType.subclass = AnwendungsinformationenTypeSub
# end class AnwendungsinformationenTypeSub


class AttributeListTypeSub(supermod.AttributeListType):
    def __init__(self, Art=None, Name=None, Attribut=None):
        super(AttributeListTypeSub, self).__init__(Art, Name, Attribut, )
supermod.AttributeListType.subclass = AttributeListTypeSub
# end class AttributeListTypeSub


class KorpusdatenTypeSub(supermod.KorpusdatenType):
    def __init__(self, Fugendaten=None, Korpusdaten=None, Plattendicken=None):
        super(KorpusdatenTypeSub, self).__init__(Fugendaten, Korpusdaten, Plattendicken, )
supermod.KorpusdatenType.subclass = KorpusdatenTypeSub
# end class KorpusdatenTypeSub


class FugendatenTypeSub(supermod.FugendatenType):
    def __init__(self, Oben=None, Unten=None, Zwischen=None, Links=None, Rechts=None, valueOf_=None):
        super(FugendatenTypeSub, self).__init__(Oben, Unten, Zwischen, Links, Rechts, valueOf_, )
supermod.FugendatenType.subclass = FugendatenTypeSub
# end class FugendatenTypeSub


class KorpusdatenValuesTypeSub(supermod.KorpusdatenValuesType):
    def __init__(self, Kab=None, Kwi=None, Kh=None, Ekb=None, Ktr=None, Ktl=None, Lw=None, Lt=None, Pta=None, Fb=None, Kt=None, Ekt=None, Pm=None, valueOf_=None):
        super(KorpusdatenValuesTypeSub, self).__init__(Kab, Kwi, Kh, Ekb, Ktr, Ktl, Lw, Lt, Pta, Fb, Kt, Ekt, Pm, valueOf_, )

    def DrawTT(self):
        '''Рисует каркас в сцене К3'''
        ##ISDEBUG.Print( '---------------------------------------------KorpusdatenValuesTypeSub-----------------',self.Kab, self.Kwi, self.Kh, self.Ekb, self.Ktr, self.Ktl, self.Lw, self.Lt, self.Pta, self.Fb, self.Kt, self.Ekt, self.Pm )
        self.objects = k3.sysvar(60)
        Kdat = self
        Kab = Kdat.Kab
        Kh = Kdat.Kh
        Kt = Kdat.Kt
        Lw =  Kdat.Lw
        Kwi = Kdat.Kwi
        Ktr = Kdat.Ktr
        Ktl = Kdat.Ktl
        Fb =  Kdat.Fb
        Pta = Kdat.Pta
        Pm =  Kdat.Pm
        Ekt = Kdat.Ekt
        Ekb = Kdat.Ekb
        Standard_cabinet = None not in [Kh,Kt,Kab,Lw]
##        <Kh>                     (= 1…Cabinet height)
##        <Kt>                        (= 2…Cabinet depth)
##        <Kab>                 (= 3…Outside cabinet width)
##        <Lw>                     (= 4…Inner cabinet width)
        Angled_cabinet = None not in [Kh,Ktr,Ktl,Kab,Kwi]
##        <Kh>                     (= 1…Cabinet height)
##        <Ktr>                     (= 2…Right cabinet depth)
##        <Ktl>                    (= 3…Left cabinet depth)
##        <Kab>                 (= 4…Outside cabinet width)
##        <Kwi>                 (= 5…Cabinet angle)
##        <Fb>                     (= 6…Front width)
        SPACE_CORNER_1 = None not in [Kh,Pm,Pta]
##        <Kh>                     (= 1…Cabinet height)
##        <Pm>                 (= 2…Installation dimension)
##        <Pta>                 (= 3…Installation depth adjacent cabinet)
        SPACE_CORNER_2 = None not in [Kh,Ekt,Ekb]
##        <Kh>                     (= 1…Cabinet height)
##        <Ekt>                 (= 2…Corner cabinet depth)
##        <Ekb>                 (= 3…Corner cabinet width)
        SPACE_CORNER_SYNCROMOTION_1 = None not in [Kh,Pm,Pta]
##        <Kh>                     (= 1…Cabinet height)
##        <Pm>                 (= 2…Installation dimension)
##        <Pta>                 (= 3…Installation depth adjacent cabinet)
        SPACE_CORNER_SYNCROMOTION_2 = None not in [Kh,Ekt,Ekb]
##        <Kh>                     (= 1…Cabinet height)
##        <Ekt>                 (= 2…Corner cabinet depth)
##        <Ekb>                 (= 3…Corner cabinet width)
        # По состоянию на 12.12.2012 16:16 предложено(Ермаковым) делать все в прямых каркасах
        if Standard_cabinet:
            TypKar = 0; Orient = 0; W = Kab; T = Kt; H = Kh;  Wmins = 0; Tmins = 0; MaskContact=0
        if Angled_cabinet:
            TypKar = 0; Orient = 0; W = Kab; T = max(Ktr,Ktl); H = Kh;  Wmins = 0; Tmins = 0; MaskContact=0
        if SPACE_CORNER_1:
            TypKar = 0; Orient = 0; W = Ekb; T = Ekb; H = Kh;  Wmins = 0; Tmins = 0; MaskContact=0
        if SPACE_CORNER_2:
            TypKar = 0; Orient = 0; W = Kab; T = Kt; H = Kh;  Wmins = 0; Tmins = 0; MaskContact=0
        if SPACE_CORNER_SYNCROMOTION_1:
            TypKar = 0; Orient = 0; W = Pm;  T = Pm; H = Kh;  Wmins = 0; Tmins = 0; MaskContact=0
        if SPACE_CORNER_SYNCROMOTION_2:
            TypKar = 0; Orient = 0; W = Ekb; T = Ekb; H = Kh;  Wmins = 0; Tmins = 0; MaskContact=0
        #ISDEBUG.Print(Standard_cabinet)
        # Этот код для случая работы с каркасом
        if variantKarkas == True:
            Kr = mKarcas.Karkas(TypKar, Orient, W, T, H, Wmins, Tmins, MaskContact)
            Kr.make(0,0,0)
            k3.setucs(k3.k_save,"KarkasUcs")
            k3.setucs(W,0,0,W,T,0,0,0,0)
            k3.setucs(k3.k_save,"DynaplanUcs")
            Kar=k3.Var()
            k3.objident(k3.k_last,1,Kar)
            carcasK3.numkar = k3.getattr(Kar,'KarkasNumb',-1)
            carcasK3.object_k = Kar.value
        else:
            k3.setucs(k3.k_save,"KarkasUcs")
            k3.setucs(W,0,0,W,T,0,0,0,0)
        # end DrawTT
supermod.KorpusdatenValuesType.subclass = KorpusdatenValuesTypeSub
# end class KorpusdatenValuesTypeSub


class PlattendickenTypeSub(supermod.PlattendickenType):
    def __init__(self, Distd=None, Oben=None, Unten=None, Links=None, Rechts=None, valueOf_=None):
        super(PlattendickenTypeSub, self).__init__(Distd, Oben, Unten, Links, Rechts, valueOf_, )
supermod.PlattendickenType.subclass = PlattendickenTypeSub
# end class PlattendickenTypeSub


class BodenTypeSub(supermod.BodenType):
    def __init__(self, Boden=None):
        super(BodenTypeSub, self).__init__(Boden, )
    def DrawTT(self):
        global gTypeQuader, gTypepanel
        gTypeQuader = 12
        if 'ID' in self.__dict__:
            gTypepanel = self.ID
            #ISDEBUG.Print( gTypepanel )
        defmaterial.panel_K3 = mP.PanelRectangle(material = defmaterial.basematerial)
        defmaterial.panel_K3.setBand(B = 0,C = 0,D = 0,E = defmaterial.BandType,
                                     Ang_1 = 0,Ang_2 = 0,Ang_3 = 0,Ang_4 = 0)
        #Наложение встык    1
            #С фальцем    2
            #С пазом    3
            #С пазом - наложение сверху    4
            #С фальцем - наложение сверху    5
            #Вкладная    6
            #Вкладная - наложение сверху    7
        defmaterial.panel_K3.setFix(B = defmaterial.FixCorp,C = defmaterial.FixCorp,
                                    D = (defmaterial.FixBp if varinst.BackBlumType in [1,2,4,5] else 0) ,
                                    E = 0,
                                     Ang_1 = 0,Ang_2 = 0,Ang_3 = 0,Ang_4 = 0)
supermod.BodenType.subclass = BodenTypeSub
# end class BodenTypeSub


class SeitenwandTypeSub(supermod.SeitenwandType):
    def __init__(self, Seitenwand=None, Eckkorpusseite=None):
        super(SeitenwandTypeSub, self).__init__(Seitenwand, Eckkorpusseite, )
    def DrawTT(self):
        global gTypeQuader, gTypepanel
        gTypeQuader = 11
        if 'ID' in self.__dict__:
            gTypepanel = self.ID
            #ISDEBUG.Print( gTypepanel )
        defmaterial.panel_K3=mP.PanelRectangle(material=defmaterial.seitematerial)
        #defmaterial.panel_K3.setBandNull()
        defmaterial.panel_K3.setBand(B = defmaterial.BandType,C = defmaterial.BandType,D = 0,E = defmaterial.BandType,
                                     Ang_1 = 0,Ang_2 = 0,Ang_3 = 0,Ang_4 = 0)
        defmaterial.panel_K3.setFix(B = 0,C = 0,D = (defmaterial.FixBp if varinst.BackBlumType in [1,2] else 0),E = 0,
                                     Ang_1 = 0,Ang_2 = 0,Ang_3 = 0,Ang_4 = 0)

supermod.SeitenwandType.subclass = SeitenwandTypeSub
# end class SeitenwandTypeSub


class RueckwandListTypeSub(supermod.RueckwandListType):
    def __init__(self, Rueckwand=None, RueckwandVerbinder=None):
        super(RueckwandListTypeSub, self).__init__(Rueckwand, RueckwandVerbinder, )
    def DrawTT(self):
        global gTypeQuader, gTypepanel
        gTypeQuader = 14
        if 'ID' in self.__dict__:
            gTypepanel = self.ID
            #ISDEBUG.Print( gTypepanel )
        defmaterial.panel_K3=mP.PanelRectangle(material=defmaterial.backmaterial)
supermod.RueckwandListType.subclass = RueckwandListTypeSub
# end class RueckwandListTypeSub


class PlattenTypeSub(supermod.PlattenType):
    def __init__(self, Platte=None):
        super(PlattenTypeSub, self).__init__(Platte, )
supermod.PlattenType.subclass = PlattenTypeSub
# end class PlattenTypeSub


class KorpusAnbindungTypeSub(supermod.KorpusAnbindungType):
    def __init__(self, Distanz=None, Keil=None):
        super(KorpusAnbindungTypeSub, self).__init__(Distanz, Keil, )
supermod.KorpusAnbindungType.subclass = KorpusAnbindungTypeSub
# end class KorpusAnbindungTypeSub


class TuerTypeSub(supermod.TuerType):
    def __init__(self, ScharnierSeite=None, Name=None, Beschlaege=None, Front=None, Innenschubkasten=None, Traverse=None):
        super(TuerTypeSub, self).__init__(ScharnierSeite, Name, Beschlaege, Front, Innenschubkasten, Traverse, )
supermod.TuerType.subclass = TuerTypeSub
# end class TuerTypeSub


class DoppeltuerTypeSub(supermod.DoppeltuerType):
    def __init__(self, Name=None, Beschlaege=None, Front=None, Innenschubkasten=None, Mittelwand=None, Steher=None, Traverse=None):
        super(DoppeltuerTypeSub, self).__init__(Name, Beschlaege, Front, Innenschubkasten, Mittelwand, Steher, Traverse, )
supermod.DoppeltuerType.subclass = DoppeltuerTypeSub
# end class DoppeltuerTypeSub


class BlindfrontTypeSub(supermod.BlindfrontType):
    def __init__(self, Name=None, Front=None):
        super(BlindfrontTypeSub, self).__init__(Name, Front, )
supermod.BlindfrontType.subclass = BlindfrontTypeSub
# end class BlindfrontTypeSub


class AussenschubkastenTypeSub(supermod.AussenschubkastenType):
    def __init__(self, Schubkastenart=None, Auszugslaenge=None, Name=None, Beschlaege=None, Front=None, Holzschubkasten=None, GlasBoxside=None, Eckblende=None, Verbindungsstueck=None, Boden=None, Rueckwand=None, EINSCHUBELEMENT_BCO=None, EINSCHUBELEMENT_antaro=None, Innenschubkasten=None, Zwischenstueck=None):
        super(AussenschubkastenTypeSub, self).__init__(Schubkastenart, Auszugslaenge, Name, Beschlaege, Front, Holzschubkasten, GlasBoxside, Eckblende, Verbindungsstueck, Boden, Rueckwand, EINSCHUBELEMENT_BCO, EINSCHUBELEMENT_antaro, Innenschubkasten, Zwischenstueck, )
        self.objects=None
    def DrawTT(self):
        self.objects=k3.sysvar(60)
        #ISDEBUG.Print( '---------------------------------Aussenschubkasten----',self.__class__,'-------------------------------------' )
    def GroupChildObjectK3(self):
        if self.objects  is not None:
            self.objects=k3.sysvar(60)-self.objects
            if self.objects>0:
                #k3.setucs(k3.k_move,self.PosIsZero(self.PositionX),self.PosIsZero(self.PositionY),self.PosIsZero(self.PositionZ))
                k3.group(k3.k_last,self.objects,k3.k_done)
                GRP=k3.Var()
                k3.objident(k3.k_last,1,GRP)
                #k3.setucs(k3.k_previous)
                k3.attrobj(k3.k_attach,"ElemName",k3.k_done,GRP.value,str(self.Name)+" "+str(self.Schubkastenart)+' '+str(self.Auszugslaenge))
                k3.attrobj(k3.k_attach,"FurnType",k3.k_done,GRP.value,str(('310300')))
                k3.attrobj(k3.k_attach,'Assembly','ObjType','PlaceType',k3.k_done,GRP.value,1,0,0)
                if variantKarkas == True:
                    k3.attrobj(k3.k_attach,'Karkasnumb',k3.k_done,GRP.value,carcasK3.numkar)


supermod.AussenschubkastenType.subclass = AussenschubkastenTypeSub
# end class AussenschubkastenTypeSub


class InnenschubkastenTypeSub(supermod.InnenschubkastenType):
    def __init__(self, Schubkastenart=None, Auszugslaenge=None, Name=None, Beschlaege=None, Front=None, Holzschubkasten=None, Boden=None, Rueckwand=None, EINSCHUBELEMENT_BCO=None, EINSCHUBELEMENT_FRONT=None, EINSCHUBELEMENT_antaro=None, SeitlicheDistanz=None):
        super(InnenschubkastenTypeSub, self).__init__(Schubkastenart, Auszugslaenge, Name, Beschlaege, Front, Holzschubkasten, Boden, Rueckwand, EINSCHUBELEMENT_BCO, EINSCHUBELEMENT_FRONT, EINSCHUBELEMENT_antaro, SeitlicheDistanz, )
supermod.InnenschubkastenType.subclass = InnenschubkastenTypeSub
# end class InnenschubkastenTypeSub


class TraverseTypeSub(supermod.TraverseType):
    def __init__(self, Name=None, Boden=None):
        super(TraverseTypeSub, self).__init__(Name, Boden, )
supermod.TraverseType.subclass = TraverseTypeSub
# end class TraverseTypeSub


class KlappensystemTypeSub(supermod.KlappensystemType):
    def __init__(self, Typ=None, Name=None, Beschlaege=None, Front=None, Mittelwand=None, Steher=None):
        super(KlappensystemTypeSub, self).__init__(Typ, Name, Beschlaege, Front, Mittelwand, Steher, )
supermod.KlappensystemType.subclass = KlappensystemTypeSub
# end class KlappensystemTypeSub


class VorratsauszugTypeSub(supermod.VorratsauszugType):
    def __init__(self, Name=None, Beschlaege=None, Front=None, Aussenschubkasten=None):
        super(VorratsauszugTypeSub, self).__init__(Name, Beschlaege, Front, Aussenschubkasten, )
supermod.VorratsauszugType.subclass = VorratsauszugTypeSub
# end class VorratsauszugTypeSub


class noWrite:
    def write(self,a):
        pass
class BeschlaegeTypeSub(supermod.BeschlaegeType):
    def __init__(self, PositionZ=None, PositionX=None, PositionY=None, Name=None,
        Bezug=None, WinkelY=None, WinkelX=None, WinkelZ=None, Artikel=None):
        super(BeschlaegeTypeSub, self).__init__(PositionZ, PositionX, PositionY,
        Name, Bezug, WinkelY, WinkelX, WinkelZ, Artikel, )
        #self.objects=k3.sysvar(60)
    def DrawTT(self):
        self.objects=k3.sysvar(60)
        defmaterial.HoldPosition.PositionX=self.PositionX
        defmaterial.HoldPosition.PositionY=self.PositionY
        defmaterial.HoldPosition.PositionZ=self.PositionZ
        defmaterial.HoldPosition.Bezug=self.Bezug
        #ISDEBUG.Print( '---------------------------------BeschlaegeType----',self.__class__,'-------------------------------------' )
    def GroupChildObjectK3(self):
        #ISDEBUG.Print( '---------------GroupChildObjectK3------------------BeschlaegeType----',self.__class__,'-------------------------------------' )
        try:
            self.objects=k3.sysvar(60)-self.objects
            if self.objects>0:
                k3.setucs(k3.k_move,self.PositionX,self.PositionY,self.PositionZ)

                k3.group(k3.k_last,self.objects,k3.k_done)
                GRP=k3.Var()
                k3.objident(k3.k_last,1,GRP)
                k3.setucs(k3.k_previous)
                k3.attrobj(k3.k_attach,"ElemName",k3.k_done,GRP.value,str(('Комплект фурнитуры '+self.Name)))
                #k3.attrobj(k3.k_attach,"FurnType",k3.k_done,GRP.value,str(('040300')))

                if variantKarkas == True:
                    k3.attrobj(k3.k_attach,'Karkasnumb',k3.k_done,GRP.value,carcasK3.numkar)
        except BaseException:
            print("Error!:", sys.exc_info()[0])
supermod.BeschlaegeType.subclass = BeschlaegeTypeSub
# end class BeschlaegeTypeSub


class HolzschubkastenTypeSub(supermod.HolzschubkastenType):
    def __init__(self, Name=None, Quader=None, Zargendicke=None, Bodendicke=None, Nischentiefe=None, Holzschubkastenhoehe=None, Rueckwandhoehe=None):
        super(HolzschubkastenTypeSub, self).__init__(Name, Quader, Zargendicke, Bodendicke, Nischentiefe, Holzschubkastenhoehe, Rueckwandhoehe, )
    def DrawTT(self):
        #ISDEBUG.Print( '---------------------------------HolzschubkastenType-----------------------------------------' )
        pass
supermod.HolzschubkastenType.subclass = HolzschubkastenTypeSub
# end class HolzschubkastenTypeSub


class InnenFachTypeSub(supermod.InnenFachType):
    def __init__(self, Name=None, Boden=None):
        super(InnenFachTypeSub, self).__init__(Name, Boden, )
    def DrawTT(self):
        global gTypeQuader, gTypepanel
        gTypeQuader = 12
        defmaterial.panel_K3=mP.PanelRectangle(material=defmaterial.InnenFachmaterial)
        if 'ID' in self.__dict__:
            gTypepanel = self.ID
            #ISDEBUG.Print( gTypepanel )
        #ISDEBUG.Print( '---------------------------------InnenFachType-----------------------------------------' )
supermod.InnenFachType.subclass = InnenFachTypeSub
# end class InnenFachTypeSub


class FachTypeSub(supermod.FachType):
    def __init__(self, Hoehe=None, Tiefe=None, Breite=None):
        super(FachTypeSub, self).__init__(Hoehe, Tiefe, Breite, )
supermod.FachType.subclass = FachTypeSub
# end class FachTypeSub


class SERVODRIVETypeSub(supermod.SERVODRIVEType):
    def __init__(self, Beschlaege=None):
        super(SERVODRIVETypeSub, self).__init__(Beschlaege, )
supermod.SERVODRIVEType.subclass = SERVODRIVETypeSub
# end class SERVODRIVETypeSub


class QuaderTypeSub(supermod.QuaderType):
    def __init__(self, aufd=None, mode=None, dir=None, Position=None, Orientierung=None, Hoehe=None, PunktC=None, Handle=None, Linien=None, View=None, Punkte=None, Fasen=None, Verrundung=None, Nut=None, Falz=None, Bohrungen=None):
        super(QuaderTypeSub, self).__init__(aufd, mode, dir, Position, Orientierung, Hoehe, PunktC, Handle, Linien, View, Punkte, Fasen, Verrundung, Nut, Falz, Bohrungen, )
    def DrawTT(self):
        '''Создает прямоугольную панель в среде к3'''
        global gTypeQuader
        # это стартовая точка"
        px,py,pz = k3.Var(),k3.Var(),k3.Var()
        px1,py1,pz1= k3.Var(),k3.Var(),k3.Var()
        pxh1,pyh1,pzh1 = k3.Var(),k3.Var(),k3.Var()
        pos_X = self.Position.X
        pos_Y = self.Position.Y
        pos_Z = self.Position.Z
        pos_ABSUCS = self.Position.Bezug
        # Вторая точка прямоугольника
        sec_X = self.PunktC.X
        sec_Y = self.PunktC.Y
        sec_Z = self.PunktC.Z
        sec_ABSUCS = self.PunktC.Bezug
        # параметр для определения габарита панели
        Height = self.Hoehe
        k3.ptranscs(0,3,pos_X,pos_Y,pos_Z,px,py,pz)
        k3.ptranscs(0,3,sec_X,sec_Y,sec_Z,px1,py1,pz1)
        k3.ptranscs(0,3,sec_X,sec_Y,pz1.value+Height,pxh1,pyh1,pzh1)
        k3.setucs(k3.k_restore,"KarkasUcs")
        k3.ptranscs(3,0,px,py,pz,px,py,pz)
        k3.ptranscs(3,0,px1,py1,pz1,px1,py1,pz1)
        k3.ptranscs(0,3,pxh1,pyh1,pzh1,pxh1,pyh1,pzh1)
        pos_X,pos_Y,pos_Z=px.value,py.value,pz.value
        sec_X,sec_Y,sec_Z=px1.value,py1.value,pz1.value
        sech_X,sech_Y,sech_Z=pxh1.value,pyh1.value,pzh1.value
        # <Orientierung X="0.0" Y="0.0" Z="1.0" Bezug="A" />
        # В зависимости от типа панели определяем ее характеристики

        # Требуются эксперименты с системой координат

        par_mbpanel_3points = []
        if gTypeQuader==12:
            par_mbpanel_3points = [ sec_X,pos_Y,pos_Z,
                                    pos_X,pos_Y,pos_Z,
                                    sec_X,sec_Y,pos_Z
                                    ]
            length=abs(sec_Y-pos_Y)
            width=abs(sec_X-pos_X)
        if gTypeQuader==11:
            par_mbpanel_3points = [ pos_X,pos_Y,pos_Z,
                                    pos_X,pos_Y,sech_Z,
                                    pos_X,sec_Y,pos_Z
                                    ]
            length=abs(sec_Y-pos_Y)
            width=abs(sech_Z-pos_Z)
        if gTypeQuader==14:
##            ISDEBUG.Print( "pos_X= ",pos_X," pos_Y= ",pos_Y,"pos_Z= ",pos_Z )
##            ISDEBUG.Print( "sec_X= ",sec_X," sec_Y= ",sec_Y," sec_Z= ",sec_Z )
##            ISDEBUG.Print( "sech_X= ",sech_X," sech_Y= ",sech_Y," sech_Z= ",sech_Z )
            par_mbpanel_3points = [ sec_X,pos_Y,pos_Z,
                                    sec_X,pos_Y,sech_Z,
                                    pos_X,pos_Y,pos_Z
                                    ]

            length=abs(sec_X-pos_X)
            width=abs(sech_Z-pos_Z)
        #k3.mbpanel(k3.k_3points, par_mbpanel_3points) # Это вариант работы всем хорош , но не годится не понятно как задавать материал кромку крепеж и прочее
        #ISDEBUG.Print( gTypeQuader )
        defmaterial.HoldPosition = self.Position
        if gTypeQuader is not None:
            gU.change_attrs([defmaterial.panel_K3],['length','width','typepan'],[length,width,gTypeQuader])
        if variantKarkas == True:
            k3.setucs(k3.k_restore,"DynaplanUcs")
        else:
            k3.setucs(k3.k_previous)
        return gTypeQuader,sec_X,pos_Y,pos_Z

    def makeDraw(self,gTypeQuader,sec_X,pos_Y,pos_Z):
        k3.setucs(k3.k_restore,"KarkasUcs")
        if gTypeQuader is not None:
            gU.change_attrs([defmaterial.panel_K3],['slots'],[defmaterial.slots])
            #defmaterial.slots = []
            # Эксперримент с фасадом. Требуется вызвать макрос построения фасада. Пока не получается. Ждем Малова 17,01,2013
            if defmaterial.macro == None:
                defmaterial.panel_K3.make(sec_X,pos_Y,pos_Z)
            else:
                if defmaterial.macro == 'Fasad':
                    defmaterial.panel_K3.make(sec_X,pos_Y,pos_Z)

            PNT=k3.Var()
            k3.objident(k3.k_last,1,PNT)
            defmaterial.object_K3=PNT
            k3.attrobj(k3.k_attach,"ElemName",k3.k_done,defmaterial.object_K3.value,gTypepanel)

            if defmaterial.FurnType is not None:
                k3.attrobj(k3.k_attach,'FurnType',k3.k_done,defmaterial.object_K3.value,str((defmaterial.FurnType)))
                defmaterial.FurnType = None

        #defmaterial.HoldPosition = self.Position
        if variantKarkas == True:
            k3.setucs(k3.k_restore,"DynaplanUcs")
        else:
            k3.setucs(k3.k_previous)
        defmaterial.slots = []
supermod.QuaderType.subclass = QuaderTypeSub
# end class QuaderTypeSub


class PolygonTypeSub(supermod.PolygonType):
    def __init__(self, Eckpunkte=None, Position=None, Orientierung=None, Hoehe=None, PunktB=None, PunktC=None, PunktD=None, PunktE=None, PunktF=None, PunktG=None, PunktH=None, Handle=None, Verrundung=None, Falz=None, Bohrungen=None):
        super(PolygonTypeSub, self).__init__(Eckpunkte, Position, Orientierung, Hoehe, PunktB, PunktC, PunktD, PunktE, PunktF, PunktG, PunktH, Handle, Verrundung, Falz, Bohrungen, )
supermod.PolygonType.subclass = PolygonTypeSub
# end class PolygonTypeSub


class NutFalzTypeSub(supermod.NutFalzType):
    def __init__(self, Position=None, Orientierung=None, PunktB=None, Tiefe=None, Radius=None):
        super(NutFalzTypeSub, self).__init__(Position, Orientierung, PunktB, Tiefe, Radius, )
    def DrawTT(self):
        plane = ('A' if self.Position.Y >0.1 else 'F')
        vSlot = mS.Slot()
        if defmaterial.panel_K3.typepan==11:
            plane = ('A' if self.Position.Y >0.1 else 'F')
        elif defmaterial.panel_K3.typepan==12:
            plane = ('A' if self.Position.Z >0.1 else 'F')
        vSlot.setSlot(False,Plane=plane,
                               Side='D',
                               Shift = self.Position.X - self.Radius, # Отступ от стороны
                                Width = 2*self.Radius, # Ширина
                                Depth = self.Tiefe # Глубина
                                )
        defmaterial.slots.append(vSlot)
        pass
supermod.NutFalzType.subclass = NutFalzTypeSub
# end class NutFalzTypeSub


class BohrbildTypeSub(supermod.BohrbildType):
    def __init__(self, HauptBohrbild=None, Name=None, Blockname=None, Position=None, Drehung=None, LayerZuordnung=None, Bohrtiefe=None, Bohrradius=None):
        super(BohrbildTypeSub, self).__init__(HauptBohrbild, Name, Blockname, Position, Drehung, LayerZuordnung, Bohrtiefe, Bohrradius, )
supermod.BohrbildType.subclass = BohrbildTypeSub
# end class BohrbildTypeSub


class BohrungenTypeSub(supermod.BohrungenType):
    def __init__(self, Zylinder=None):
        super(BohrungenTypeSub, self).__init__(Zylinder, )
supermod.BohrungenType.subclass = BohrungenTypeSub
# end class BohrungenTypeSub


class BohrtiefeTypeSub(supermod.BohrtiefeType):
    def __init__(self, BT=None):
        super(BohrtiefeTypeSub, self).__init__(BT, )
supermod.BohrtiefeType.subclass = BohrtiefeTypeSub
# end class BohrtiefeTypeSub


class BohrradiusTypeSub(supermod.BohrradiusType):
    def __init__(self, BR=None):
        super(BohrradiusTypeSub, self).__init__(BR, )
supermod.BohrradiusType.subclass = BohrradiusTypeSub
# end class BohrradiusTypeSub


class ArtikelTypeSub(supermod.ArtikelType):
    def __init__(self, PositionZ=None, PositionX=None, PositionY=None, Name=None, Bezug=None,
        Identnummer=None, Anzahl=None, Oberflaeche=None, Bezeichnung=None, WinkelY=None, WinkelX=None, WinkelZ=None,
        Artikelnummer=None, Artikel=None, Ablaengen=None, Skalierung=None):
        super(ArtikelTypeSub, self).__init__(PositionZ, PositionX, PositionY, Name, Bezug, Identnummer,
        Anzahl, Oberflaeche, Bezeichnung, WinkelY, WinkelX, WinkelZ, Artikelnummer, Artikel, Ablaengen, Skalierung, )
        self.objects=None
        self.box = False
    isStringFloat = lambda self,  v: float(v) if isinstance(v, str) else v
    isNoneFloat = lambda self, v: 0. if v is None else self.isStringFloat(v)
    funSort = lambda self, t:abs(t)
    PosIsZero = lambda self,val:float(sorted([0., self.isNoneFloat(val)], key=self.funSort, reverse=True)[0])

    def placeObjectPozition(self,PNT):
        '''PNT -объект К3 группа
        Функция помещает его в текущую ПСК затем откатывает и пересобирает
        Встречается в трех местах. Поэтому написана просто дабы избежать дублирования кода'''
        k3.place(PNT.value)
        k3.setucs(k3.k_restore,'tArtUcs551')
        k3.explode(k3.k_last,1)
        k3.group(k3.k_last,1,k3.k_done)
        k3.objident(k3.k_last,1,PNT)

        return PNT

    def addArtToK3(self,nameart):

##        try:
            Res = False
            k3.setucs(k3.k_save,'tArtUcs551')
            listModels = []
            if type(nameart) == k3.Var:
                PNT = nameart
                Res = True
            else:
                PNT = k3.Var()
                fMask = nameart + '.k3'
                ozMask = 'A_' + nameart +'*.k3'
                stlMask = nameart + '.stl'
    ##            koefX,koefY,koefZ = 1,1,1
    ##            if self.Skalierung is not None:
    ##
    ##                if self.Skalierung.X is not None: koefX= float(self.Skalierung.X)
    ##
    ##                if self.Skalierung.Y is not None: koefY= float(self.Skalierung.Y)
    ##
    ##                if self.Skalierung.Z is not None: koefZ= float(self.Skalierung.Z)
    ##
    ##                ISDEBUG.Print( koefX,koefY,koefZ)

                #ISDEBUG.Print( dynalog.caddata[0]+'----',fMask )
                listModels = dynalog.FindFileMaskInZip(dynalog.caddata[0],fMask)

                if len(listModels)>0 :
                    fAppName = dynalog.caddata[0]+'|'+listModels[0]
                    k3.setucs(k3.k_gcs)

                    if self.Ablaengen is None :
                        #k3.append(k3.k_block,fAppName,(0,0,0)) # добавляем внешний блок
                        vres = k3.append(fAppName,(0,0,0))
                        Res = True
                    if self.Ablaengen is not None :
                        vres = k3.append(fAppName,(0,0,0)) # добавляем файл
                        Res = True

                else:
                    listModels = dynalog.FindFileMaskInZip(dynalog.caddata[0],ozMask)
##                    print 'ozMask = ',ozMask,'----',listModels

                    if len(listModels)>0:
                        fAppName = dynalog.caddata[0]+'|'+listModels[0]
                        k3.setucs(k3.k_gcs)
                        if self.Ablaengen is None :
                            #k3.append(k3.k_block,fAppName,(0,0,0)) # добавляем внешний блок
                            vres = k3.append(fAppName,(0,0,0))
                            Res = True
                        if self.Ablaengen is not None :
                            vres = k3.append(fAppName,(0,0,0)) # добавляем файл
                            Res = True

                    else:
                        stlModels = []
                        if len(dynalog.stldata) == 0:
                            #print('Отсутствует архив STL моделей')
                            pass
                        else:
                            stlModels = dynalog.FindFileMaskInZip(dynalog.stldata[0],stlMask)
                        if len(stlModels)>0:
                            fImpName = dynalog.stldata[0]+'|'+stlModels[0]
                            k3.k3_import(k3.k_stl,k3.k_x,1,k3.k_y,1,k3.k_z,1,fImpName,0,0,0)
                            Res = True
                            k3.chprop(k3.k_mapbypars,k3.k_last,1,k3.k_done,
                                    0,  -1,          # Для всех секций
                                    1,  'Lb.pkm7_1_iml.#204', # Меняем код материала на “Lb.pkm7_1_iml.#204”
                                    # – имя материала в таблице материалов
                                    0,   3,          # А для 3й секции
                                    1,   'Lb.pkm7_1_iml.#205',         # Меняем код материала на 26-й
                                    # в текущей библиотеке материалов
                                    14, 1,           # и режим вычисления масштабов и
                                    # сдвигов – по габаритам текстурной секции
                                    15, 1,
                                    9,   1,          # И, кроме того,  режим наложения – только текстура
                                    k3.k_done)           # Больше ничего не меняем, команда закончилась

                self.box = False
                if Res:
                    k3.group(k3.k_last,1,k3.k_done)
                    k3.objident(k3.k_last,1,PNT)
                    k3.setucs(k3.k_restore,'tArtUcs551')

                    k3.place(PNT.value)
                    k3.setucs(0,0,0,0,1,0,0,0,1)

                    PNT = self.placeObjectPozition(PNT)

                    if self.WinkelX!=None:
                        k3.setucs(k3.k_rotate,k3.k_2points,(0.,0.,0.),(1.,0.,0.),float(self.WinkelX))
                        PNT = self.placeObjectPozition(PNT)

                    if self.WinkelY!=None:
                        k3.setucs(k3.k_rotate,k3.k_2points,(0.,0.,0.),(0.,1.,0.),float(self.WinkelY))
                        PNT = self.placeObjectPozition(PNT)

                    if self.WinkelZ!=None:
                        k3.setucs(k3.k_rotate,k3.k_2points,(0.,0.,0.),(0.,0.,1.),float(self.WinkelZ))
                        PNT = self.placeObjectPozition(PNT)

                    if self.Ablaengen is not None:
                        aGab = k3.VarArray(6)
                        k3.objgab3(PNT,aGab)

                        if self.Ablaengen.LaengeY is not None:
                            k3.box(aGab[0].value,aGab[1].value,aGab[2].value,
                                aGab[3].value,aGab[4].value-float(self.Ablaengen.LaengeY ),aGab[5].value)
                            Box = k3.Var()
                            k3.objident(k3.k_last,1,Box)
                            objs = k3.sysvar(60)
                            k3.boolean(k3.k_sub,PNT.value,Box.value)
                            k3.objident(k3.k_last,1,PNT)
                else:
                    k3.box((0,0,0),(1,1,1))
                    k3.objident(k3.k_last,1,PNT)
                    self.box = True
            k3.setucs(k3.k_restore,'tArtUcs551')

            #ISDEBUG.Print( self.PosIsZero(self.PositionX),self.PosIsZero(self.PositionY),self.PosIsZero(self.PositionZ) )
            #k3.move(k3.k_nocopy,PNT.value,k3.k_done,self.PosIsZero(self.PositionX),self.PosIsZero(self.PositionY),self.PosIsZero(self.PositionZ))
            tlt =[self.PosIsZero(self.PositionX),self.PosIsZero(self.PositionY),self.PosIsZero(self.PositionZ)]
            k3.move(k3.k_nocopy,PNT.value,k3.k_done,tlt)
            if str(self.Bezug) in ['R']:
                tlt = [self.PosIsZero(defmaterial.HoldPosition.PositionX),
                        self.PosIsZero(defmaterial.HoldPosition.PositionY),
                        self.PosIsZero(defmaterial.HoldPosition.PositionZ)]
                k3.move(k3.k_nocopy,PNT.value,k3.k_done,tlt)
##        except BaseException:
##            print '----addArtToK3------',self.__class__,'--------'
##            print 'listModels=',listModels,'  nameart = ',nameart
##            print "Error!:", sys.exc_info()[0]
##            k3.box((0,0,0),(1,1,1))
##            k3.objident(k3.k_last,1,PNT)
            return PNT


    def DrawTT(self):
        #ISDEBUG.Print('----DrawTT------',self.__class__,'--------')
##        try:
        PNT = None
        if self.Artikelnummer is not None:
            self.objects=k3.sysvar(60)
            defmaterial.HoldArtikel = str(self.Artikelnummer)
            defmaterial.HoldName = str(self.Oberflaeche)
            holderart.object = self.addArtToK3(self.Artikelnummer+'_temp') # нельзя+'_temp' добавлять артикул у которого нет информации по позиционированию
            holderart.art = self.Artikelnummer
            PNT = holderart.object
            #print self.Artikelnummer

        if self.Name is not None:
            tObgj = self.Name
            if self.Name.find('xx')>-1:
                tObgj = holderart.object
            #elif self.Name == holderart.art:
                #k3.delete(holderart.object.value,k3.k_done)

            PNT = self.addArtToK3(tObgj)
            #holderart.art = None
            #holderart.object = None
        if PNT is not None :
            if self.Name is not None:
                k3.attrobj(k3.k_attach,'ElemName',k3.k_done,PNT.value,str(self.Name))
                toLog=str(self.Name)+" no 3DModel\n"
            else:
                k3.attrobj(k3.k_attach,'ElemName',k3.k_done,PNT.value,str(self.Artikelnummer)+' '+str(self.Bezeichnung)+' '+str(self.Oberflaeche))
                toLog=str(str(self.Bezeichnung)+' '+str(self.Oberflaeche)+str(self.Artikelnummer))+" no 3DModel\n"
            #k3.attrobj(k3.k_attach,'FurnType',k3.k_done,PNT.value,str(('040000')))
        if self.box == True:
            ISDEBUG.addLog(toLog)


    def GroupChildObjectK3(self):
        if self.objects  is not None:
            self.objects=k3.sysvar(60)-self.objects
            if self.objects>0:
                k3.setucs(k3.k_move,self.PosIsZero(self.PositionX),self.PosIsZero(self.PositionY),self.PosIsZero(self.PositionZ))
                k3.group(k3.k_last,self.objects,k3.k_done)
                if self.objects>1:
                    k3.delete(k3.k_partly,holderart.object.value,k3.k_done)
                GRP=k3.Var()
                k3.objident(k3.k_last,1,GRP)
                k3.setucs(k3.k_previous)
                k3.attrobj(k3.k_attach,'ElemName',k3.k_done,GRP.value,str(self.Artikelnummer)+' '+str(self.Bezeichnung)+' '+str(self.Oberflaeche))
                #k3.attrobj(k3.k_attach,"FurnType",k3.k_done,GRP.value,str(('040000')))
                # Создаем скрейч атрибут ExtElem
##                if k3.isattrdef("ExtElem")==False:
##                    k3.attribute(k3.k_create, "ExtElem", str("Импортированное комплектующее"), k3.k_text, 10, 20)
##                ScrMod=k3.initscratch()
##                err=k3.addscratch(ScrMod,"WasteCoeff",1.)
##                err=k3.addscratch(ScrMod,"PriceCoeff",1.)
##                NULLOUT=k3.writescratch(ScrMod,"ExtElem",GRP.value)
##                ScrMod=k3.termscratch(ScrMod)




            #print self.gds_format_string(quote_attrib(self.Oberflaeche).encode(ExternalEncoding), input_name='Oberflaeche')

##        except BaseException:
##            print( "Error!:", sys.exc_info()[0] )
##            pass

            #ISDEBUG.Print( '---------------------------------ArtikelType----',self.__class__,'-------------------------------------' )
supermod.ArtikelType.subclass = ArtikelTypeSub
# end class ArtikelTypeSub


class AblaengenTypeSub(supermod.AblaengenType):
    def __init__(self, ReferenzX=None, ReferenzY=None, ReferenzZ=None, LaengeZ=None, LaengeY=None, LaengeX=None):
        super(AblaengenTypeSub, self).__init__(ReferenzX, ReferenzY, ReferenzZ, LaengeZ, LaengeY, LaengeX, )
supermod.AblaengenType.subclass = AblaengenTypeSub
# end class AblaengenTypeSub


class LayerZuordnungTypeSub(supermod.LayerZuordnungType):
    def __init__(self, Von=None, Nach=None):
        super(LayerZuordnungTypeSub, self).__init__(Von, Nach, )
supermod.LayerZuordnungType.subclass = LayerZuordnungTypeSub
# end class LayerZuordnungTypeSub


class VerrundungTypeSub(supermod.VerrundungType):
    def __init__(self, Kante=None, Radius=None):
        super(VerrundungTypeSub, self).__init__(Kante, Radius, )
supermod.VerrundungType.subclass = VerrundungTypeSub
# end class VerrundungTypeSub


class AttributTypeSub(supermod.AttributType):
    def __init__(self, Name=None, Wert=None, MIN=None, MAX=None, Front=None, Griff=None, Sperren=None, Typ=None, valueOf_=None):
        super(AttributTypeSub, self).__init__(Name, Wert, MIN, MAX, Front, Griff, Sperren, Typ, valueOf_, )
supermod.AttributType.subclass = AttributTypeSub
# end class AttributTypeSub


class GeometryTypeSub(supermod.GeometryType):
    def __init__(self, Name=None, ID=None, Quader=None, Polygon=None, Bohrbild=None, extensiontype_=None):
        super(GeometryTypeSub, self).__init__(Name, ID, Quader, Polygon, Bohrbild, extensiontype_, )

    def DrawTT(self):
        global  gTypepanel, gTypeQuader
        if 'ID' in self.__dict__:
            gTypepanel = self.ID
            # getposInList - находит позицию вхождения элемента списка в gTypepanel. Если хотябы один из элементов списка
            # встречается в строке, то возвращает значение больше -1
            getposInList = lambda x:sorted([gTypepanel.find(velement) for velement in x],reverse=True)[0]
            gTypeQuader = None
            #print 'gVarKorpus = ',gVarKorpus
            if gVarKorpus == True: # Если панели корпуса надо создавать
                if getposInList(['LWAND','EWAND','KSR','KSL'])>=0:
                    gTypeQuader = 11
                elif getposInList(['BODEN','TRAV','OB','UB'])>=0:
                    gTypeQuader = 12
                elif getposInList(['KWAND','KRW','FRONT'])>=0:
                    gTypeQuader = 14
            else: # Если нужна только начинка
                if getposInList(['LWAND','EWAND'])>=0:
                    gTypeQuader = 11
                elif getposInList(['BODEN'])>=0:
                    gTypeQuader = 12
                elif getposInList(['KWAND','FRONT'])>=0:
                    gTypeQuader = 14
            #ISDEBUG.Print( '****************************************',gTypepanel,'**',gTypeQuader )

        #ISDEBUG.Print( '---------------------------------GeometryType-----------------------------------------' )
supermod.GeometryType.subclass = GeometryTypeSub
# end class GeometryTypeSub


class LinienTypeSub(supermod.LinienType):
    def __init__(self, L=None):
        super(LinienTypeSub, self).__init__(L, )
supermod.LinienType.subclass = LinienTypeSub
# end class LinienTypeSub


class ViewTypeSub(supermod.ViewType):
    def __init__(self, L=None, Dim=None):
        super(ViewTypeSub, self).__init__(L, Dim, )
supermod.ViewType.subclass = ViewTypeSub
# end class ViewTypeSub


class PunkteTypeSub(supermod.PunkteType):
    def __init__(self, Bezug=None, p=None):
        super(PunkteTypeSub, self).__init__(Bezug, p, )
supermod.PunkteType.subclass = PunkteTypeSub
# end class PunkteTypeSub


class FasenTypeSub(supermod.FasenType):
    def __init__(self, Fase=None):
        super(FasenTypeSub, self).__init__(Fase, )
supermod.FasenType.subclass = FasenTypeSub
# end class FasenTypeSub


class DimTypeSub(supermod.DimType):
    def __init__(self, typ=None, o=None, v=None, valueOf_=None):
        super(DimTypeSub, self).__init__(typ, o, v, valueOf_, )
supermod.DimType.subclass = DimTypeSub
# end class DimTypeSub


class LineTypeSub(supermod.LineType):
    def __init__(self, v=None, valueOf_=None):
        super(LineTypeSub, self).__init__(v, valueOf_, )
supermod.LineType.subclass = LineTypeSub
# end class LineTypeSub


class FaseTypeSub(supermod.FaseType):
    def __init__(self, Abstand=None, Kante=None, Winkel=None):
        super(FaseTypeSub, self).__init__(Abstand, Kante, Winkel, )
supermod.FaseType.subclass = FaseTypeSub
# end class FaseTypeSub


class ZylinderTypeSub(supermod.ZylinderType):
    def __init__(self, von_Bohrbild=None, Position=None, Orientierung=None, Hoehe=None, Radius=None):
        super(ZylinderTypeSub, self).__init__(von_Bohrbild, Position, Orientierung, Hoehe, Radius, )
    def DrawTT(self):
        pos_X = self.Position.X
        pos_Y = self.Position.Y
        pos_Z = self.Position.Z
        poe_X = self.Position.X+self.Hoehe*self.Orientierung.X
        poe_Y = self.Position.Y+self.Hoehe*self.Orientierung.Y
        poe_Z = self.Position.Z+self.Hoehe*self.Orientierung.Z
        #ISDEBUG.Print( pos_X,"  ",pos_Y,"  ",pos_Z,"  ",poe_X,"  ",poe_Y,"  ",poe_Z,"  ",self.Radius," ",self.Position.Bezug )
        #k3.cylinder(pos_X,pos_Y,pos_Z,poe_X,poe_Y,poe_Z,self.Radius)
        k3.line(pos_X,pos_Y,pos_Z,poe_X,poe_Y,poe_Z)
        tdef=str(self.Hoehe)+","+str(self.Radius*2)+",0,0,0"
        k3.attrobj(k3.k_attach,"FixHole",k3.k_done,k3.k_last,1,tdef)
        if self.Position.Bezug == 'R':
            k3.move(k3.k_nocopy,k3.k_last,1,k3.k_done,defmaterial.HoldPosition.X,defmaterial.HoldPosition.Y,defmaterial.HoldPosition.Z)
        #k3.add(defmaterial.object_K3.value,k3.k_last,1,k3.k_done)
        hole = k3.Var()
        k3.objident(k3.k_last,1,hole)
        global gListZilinder
        hh = gZilinder()
        hh.obj = hole
        hh.status = False
        gListZilinder.append(hh)
supermod.ZylinderType.subclass = ZylinderTypeSub
# end class ZylinderTypeSub


class VectorTypeSub(supermod.VectorType):
    def __init__(self, Y=None, X=None, Z=None, extensiontype_=None):
        super(VectorTypeSub, self).__init__(Y, X, Z, extensiontype_, )
supermod.VectorType.subclass = VectorTypeSub
# end class VectorTypeSub


class DoubleWithIdSub(supermod.DoubleWithId):
    def __init__(self, ID=None, valueOf_=None):
        super(DoubleWithIdSub, self).__init__(ID, valueOf_, )
    def DrawTT(self):
        #ISDEBUG.Print( '---------------------------------',self.__class__,'-----------------------------------------' )
        pass
supermod.DoubleWithId.subclass = DoubleWithIdSub
# end class DoubleWithIdSub


class pTypeSub(supermod.pType):
    def __init__(self, Y=None, X=None, Z=None, id=None, idx=None):
        super(pTypeSub, self).__init__(Y, X, Z, id, idx, )
    def DrawTT(self):
        #ISDEBUG.Print( '---------------------------------',self.__class__,'-----------------------------------------' )
        pass
supermod.pType.subclass = pTypeSub
# end class pTypeSub


class PunktTypeSub(supermod.PunktType):
    def __init__(self, Y=None, X=None, Z=None, Bezug=None):
        super(PunktTypeSub, self).__init__(Y, X, Z, Bezug, )
supermod.PunktType.subclass = PunktTypeSub
# end class PunktTypeSub


class FrontTypeSub(supermod.FrontType):
    '''Это панель которая дверка'''
    def __init__(self, Name=None, ID=None, Quader=None, Polygon=None, Bohrbild=None, Rahmen=None):
        super(FrontTypeSub, self).__init__(Name, ID, Quader, Polygon, Bohrbild, Rahmen, )
    def DrawTT(self):
        '''Надо приедшую панель превратить в фасад'''
        global gTypeQuader, gTypepanel
        gTypeQuader = 14
        if 'ID' in self.__dict__:
            gTypepanel = self.ID
            #ISDEBUG.Print( gTypepanel )
        defmaterial.panel_K3=mP.PanelRectangle(material=defmaterial.FrontTypematerial)

        defmaterial.FurnType = '500001'
        protopath = k3.GlobalVar('protopath').value

##        k3.setucs(k3.k_save,"tempFas")
##        k3.setucs(k3.k_lcs,defmaterial.object_K3.value)
##        k3.macro(protopath+'makefas.mac',(0,0,0),defmaterial.panel_K3.length,defmaterial.panel_K3.width,k3.k_done)


        #defmaterial.macro = 'Fasad'

##        k3.delete(defmaterial.object_K3,k3.k_done)
        #ISDEBUG.Print( '---------------------------------',self.__class__,'-----------------------------------------' )
supermod.FrontType.subclass = FrontTypeSub
# end class FrontTypeSub



def get_root_tag(node):
    tag = supermod.Tag_pattern_.match(node.tag).groups()[-1]
    rootClass = None
    if hasattr(supermod, tag):
        rootClass = getattr(supermod, tag)
    return tag, rootClass


def parse(inFilename):
    doc = parsexml_(inFilename)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'Korpus'
        rootClass = supermod.Korpus
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    sys.stdout.write('<?xml version="1.0" encoding="ISO-8859-1" standalone="yes"?>\n')
    if ISDEBUG.debug == False: tt=noWrite()
    else: tt = sys.stdout
    rootObj.export(tt, 0, name_=rootTag, #
        namespacedef_='',
        pretty_print=True)
    doc = None
    return rootObj


def parseString(inString):
    from io import StringIO
    doc = parsexml_(StringIO(inString))
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'Korpus'
        rootClass = supermod.Korpus
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    sys.stdout.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
    rootObj.export(sys.stdout, 0, name_=rootTag,
        namespacedef_='')
    return rootObj


def parseLiteral(inFilename):
    doc = parsexml_(inFilename)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'Korpus'
        rootClass = supermod.Korpus
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    sys.stdout.write('#from Blum_api7 import *\n\n')
    sys.stdout.write('import Blum_api7 as model_\n\n')
    sys.stdout.write('rootObj = model_.Korpus(\n')
    rootObj.exportLiteral(sys.stdout, 0, name_="Korpus")
    sys.stdout.write(')\n')
    return rootObj


USAGE_TEXT = """
Usage: python ???.py <infilename>
"""

def usage():
    ISDEBUG.Print( USAGE_TEXT )
    sys.exit(1)
#-------------------------------------------------------------------------------
#----------------------------------Это пускачи----------------------------------
class Writer:
    def __init__(self,indexRK):
        self.indexRK = indexRK
        self.l_Rueckwandkonstruktion ={1:'''
    <Rueckwandkonstruktion Art="1">
        <Attribut Name="KRwd" Wert="%.3f" MIN="3" MAX="100" Sperren="0"/>
        <Attribut Name="NuT" Wert="11" MIN="0" MAX="15" Sperren="0"/>
        <Attribut Name="Fzb" Wert="0" MIN="0" MAX="15" Sperren="0"/>
        <Attribut Name="F_KRw" Wert="1" MIN="0" MAX="15" Sperren="0"/>
        <Attribut Name="Einrueck" Wert="0" MIN="0" MAX="100" Sperren="0"/>
    </Rueckwandkonstruktion>
    ''',2:'''
    <Rueckwandkonstruktion Art="2">
        <Attribut Name="KRwd" Wert="%.3f" MIN="3.0" MAX="10.0" Sperren="0" />
        <Attribut Name="Fzb" Wert="13.0" MIN="5.0" MAX="13.0" Sperren="0" />
        <Attribut Name="Einrueck" Wert="10.0" MIN="10.0" MAX="20.0" Sperren="0" />
        <Attribut Name="F_KRw" Wert="0.0" MIN="0.0" MAX="10.0" Sperren="0" />
    </Rueckwandkonstruktion>
    ''',3:'''
    <Rueckwandkonstruktion Art="3">
        <Attribut Name="KRwd" Wert="%.3f" MIN="3.0" MAX="10.0" Sperren="0" />
        <Attribut Name="NuT" Wert="8.0" MIN="5.0" MAX="13.0" Sperren="0" />
        <Attribut Name="Einrueck" Wert="20.0" MIN="10.0" MAX="20.0" Sperren="0" />
        <Attribut Name="F_KRw" Wert="0.0" MIN="0.0" MAX="10.0" Sperren="0" />
    </Rueckwandkonstruktion>
    ''',4:'''
    <Rueckwandkonstruktion Art="4">
        <Attribut Name="KRwd" Wert="%.3f" MIN="3.0" MAX="10.0" Sperren="0" />
        <Attribut Name="NuT" Wert="8.0" MIN="5.0" MAX="13.0" Sperren="0" />
        <Attribut Name="Einrueck" Wert="20.0" MIN="10.0" MAX="20.0" Sperren="0" />
        <Attribut Name="F_KRw" Wert="0.0" MIN="0.0" MAX="10.0" Sperren="0" />
    </Rueckwandkonstruktion>
    ''',5:'''
    <Rueckwandkonstruktion Art="5">
        <Attribut Name="KRwd" Wert="%.3f" MIN="3.0" MAX="10.0" Sperren="0" />
        <Attribut Name="Fzb" Wert="13.0" MIN="5.0" MAX="13.0" Sperren="0" />
        <Attribut Name="Einrueck" Wert="10.0" MIN="10.0" MAX="20.0" Sperren="0" />
        <Attribut Name="F_KRw" Wert="0.0" MIN="0.0" MAX="10.0" Sperren="0" />
    </Rueckwandkonstruktion>
    ''',6:'''
    <Rueckwandkonstruktion Art="6">
        <Attribut Name="KRwd" Wert="%.3f" MIN="3.0" MAX="10.0" Sperren="0" />
        <Attribut Name="Einrueck" Wert="10.0" MIN="10.0" MAX="20.0" Sperren="0" />
        <Attribut Name="F_KRw" Wert="0.0" MIN="0.0" MAX="10.0" Sperren="0" />
    </Rueckwandkonstruktion>
    ''',7:'''
    <Rueckwandkonstruktion Art="7">
        <Attribut Name="KRwd" Wert="%.3f" MIN="3.0" MAX="10.0" Sperren="0" />
        <Attribut Name="Einrueck" Wert="10.0" MIN="10.0" MAX="20.0" Sperren="0" />
        <Attribut Name="F_KRw" Wert="0.0" MIN="0.0" MAX="10.0" Sperren="0" />
    </Rueckwandkonstruktion>
    '''
    }
        self.BXFOUTFORMAT ='''
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Korpus Name="shkaf">
    <Header BXFVersion="2.9.0153"  Ersteller="">
        <Attribut Name="DYNAPLAN_Version" Typ="String">2.9.43 DYA</Attribut>
        <Attribut Name="Kommission" Typ="String">K3MEBEL</Attribut>
        <Attribut Name="FrontenInliegend" Typ="Boolean">Falsch</Attribut>
        <Attribut Name="Korpusart" Typ="String">%s</Attribut>
    </Header>
    <Parameterliste>
        <Korpusinformationen>
            <Attribut Name="Po" Wert="%.3f" MIN="14" MAX="100" Sperren="0"/>
            <Attribut Name="Pu" Wert="%.3f" MIN="14" MAX="100" Sperren="0"/>
            <Attribut Name="Pr" Wert="%.3f" MIN="14" MAX="100" Sperren="0"/>
            <Attribut Name="Pl" Wert="%.3f" MIN="14" MAX="100" Sperren="0"/>
            <Attribut Name="KH" Wert="%.3f" MIN="50" MAX="3000" Sperren="0"/>
            <Attribut Name="KT" Wert="%.3f" MIN="100" MAX="1000" Sperren="0"/>
            <Attribut Name="KAB" Wert="%.3f" MIN="50" MAX="1200" Sperren="0"/>
            <Attribut Name="LW" Wert="%.3f" MIN="5" MAX="1200" Sperren="0"/>
            <Attribut Name="So" Wert="1.5" MIN="0" MAX="3" Sperren="0"/>
            <Attribut Name="FzF" Wert="1.5" MIN="0" MAX="3" Sperren="0"/>
            <Attribut Name="Su" Wert="1.5" MIN="0" MAX="3" Sperren="0"/>
            <Attribut Name="Sr" Wert="1.5" MIN="0" MAX="3" Sperren="0"/>
            <Attribut Name="Sl" Wert="1.5" MIN="0" MAX="3" Sperren="0"/>
            <Oberbodenkonstruktion Art="%d">
                <Attribut Name="OTravThin" Wert="80" MIN="30" MAX="100" Sperren="0"/>
                <Attribut Name="OTravDhin" Wert="%.3f" MIN="14" MAX="100" Sperren="0"/>
                <Attribut Name="OTravTvor" Wert="80" MIN="30" MAX="100" Sperren="0"/>
                <Attribut Name="OTravDvor" Wert="%.3f" MIN="14" MAX="100" Sperren="0"/>
            </Oberbodenkonstruktion>
            '''+self.l_Rueckwandkonstruktion[self.indexRK]+'''
        </Korpusinformationen>
    </Parameterliste>
</Korpus>
'''
    def CreateBxfFile(self,post):
        fname=post+".bxf"
        fullName = dynalog.projectFolder+fname
        self.BXFfile = open(fullName, 'w')    # открываем файл на запись
        self.OutputFile=self.BXFfile
        return fullName

    def bxfOutCommand(self,Sk='Standardkorpus1', Po=16, Pu=16,Pr=16,Pl=16,KH=720,KT=560,KAB=600,LW=568,TypOB=1,OTravDhin=16,OTravDvor=16,TypRK=1,KRwd=4):
        self.indexRK = TypRK
        print(self.BXFOUTFORMAT % (Sk, Po,Pu,Pr,Pl,KH,KT,KAB,LW,TypOB,OTravDhin,OTravDvor,KRwd), file=self.OutputFile)
        self.OutputFile.close()


#-------------------------------------------------------------------------------
def nishe_edit():
    '''Редактирует нишу К3'''
    global gVarKorpus
    gVarKorpus = False
    ISDEBUG.debug = False
    k3.getsnap()
    root, res = objK3_Update(varNiche=False)
    OBJA=k3.Var()
    k3.objident(k3.k_last,1,OBJA)
    k3.setucs(k3.k_restore,"KarkasUcs")
    k3.setucs(k3.k_delete,"KarkasUcs")
    k3.group(OBJA.value,k3.k_done)
    k3.objident(k3.k_last,1,OBJA)
    k3.setucs(k3.k_restore,'tnSaveNiche')
    k3.place(OBJA.value)
    print(-root.Korpusdaten.Plattendicken.Rechts,0.,-root.Korpusdaten.Plattendicken.Unten)
    tr1=root.Korpusdaten.Plattendicken.Rechts
    tr2=root.Korpusdaten.Plattendicken.Unten
    #k3.move(k3.k_nocopy,OBJA.value,k3.k_done,(-tr1,0.,-tr2))
    k3.explode(OBJA.value,k3.k_done)
    k3.setucs(k3.k_delete,"tnSaveNiche")
    k3.resnap()
    if variantKarkas == True:
        k3.mbcarcase(k3.k_ungroupall)
    return
#-------------------------------------------------------------------------------
def nishe():
    '''Заполняет нишу к3'''
    k3.getsnap()
    aNiche = k3.VarArray(15)
    k3.mbget(str("Укажите нишу:"),k3.k_niche,aNiche,k3.k_interact)
    k3.setucs(k3.k_save,'tnSaveNiche')


    ##k3.putmsg(aNiche)
    ##for i in range(15):
    ##    print aNiche[i].value
    widthP = []
    kArr = k3.VarArray(5)
    for i in [3,4,7,8]:
        if aNiche[i].value > 0:
            kArr[0].value=aNiche[i+6].value
            k3.getpan6par(1.,kArr)
            t = k3.getpan6par(2.,kArr)
            k3.getpan6par(999)
            widthP.append(t)
    KH=aNiche[2].value+widthP[0]+widthP[1]
    KT=aNiche[1].value
    KAB=aNiche[0].value+widthP[2]+widthP[3]
    LW=aNiche[0].value
    writer = Writer(KH=KH, KT=KT, KAB=KAB,  LW=LW, widthP=widthP)
    OutputFile = open(dynalog.projectFolder+'shkaf.bxf', "wb")
    print(writer.Skorpus % (KH,KT,KAB,LW,widthP[0],widthP[1],widthP[2],widthP[3]), file=OutputFile)
    OutputFile.close()
    mDy.DynaplanStartBXF(dynalog.projectFolder+'shkaf.bxf')
    global gVarKorpus
    gVarKorpus = False
    ISDEBUG.debug = False

    k3.setucs(k3.k_save,"KarkasUcs")
    listFiles = mDy.getsubs(dynalog.projectFolder)
    listBXF=mDy.getfilemask(listFiles[1],'*.bxf')
    infilename = mDy.getungfiles(listBXF)
    #ISDEBUG.Print( infilename )
    root = parse(infilename)
    #k3.chprop(k3.k_mapbypars,k3.k_partly,k3.k_attribute,'left(Furntype,2)==\"01\"',k3.k_done,11,70,k3.k_done)
    OBJA=k3.Var()
    k3.objident(k3.k_last,1,OBJA)
    k3.setucs(k3.k_restore,"KarkasUcs")
    k3.setucs(k3.k_delete,"KarkasUcs")
    k3.group(OBJA.value,k3.k_done)
    k3.objident(k3.k_last,1,OBJA)
    k3.setucs(k3.k_restore,'tnSaveNiche')
    k3.place(OBJA.value)
    k3.move(k3.k_nocopy,OBJA.value,k3.k_done,(-widthP[2],0.,-widthP[0]))
    k3.explode(OBJA.value,k3.k_done)
    k3.setucs(k3.k_delete,"tnSaveNiche")
    k3.resnap()
    if variantKarkas == True:
        k3.mbcarcase(k3.k_ungroupall)
    #k3.mbcarcase(k3.k_current,carcasK3.object_k)
    return
#-------------------------------------------------------------------------------
#----DynaplanEdit
def sel_ObjectK3_to_Dy():
    '''Выбирает в сцене К3 объект для передачи в Dynaplan
            Изделие полученное ранее Dynaplan
            Ниша для заполнения в Dynaplan'''

    obj_k3 = k3.Var()
    k3.switch(k3.k_autosingle,k3.k_on)
    k3.selbyattr('IsAssign("Blumbpf")',k3.k_prompt,str('Укажите объект для передачи в Dynaplan:'),k3.k_interact)
    k3.switch(k3.k_autosingle,k3.k_off)
    objs = k3.sysvar(61)
    if objs>0.:
        obj_k3.value = k3.getselnum(1)
    return obj_k3

def read_BlumAtrr():
    '''Читает атрибуты Blum из объекта'''
    if variantKarkas == True:
        obj_k3 = sel_ObjectK3_to_Dy()

    lstF = []
    for i in dynalog.listExtensionRoot:
        aK3 = k3.VarArray(300)
        #print obj_k3.value,'  Blum'+i
        if variantKarkas == True:
            s_e = k3.getattrtext(obj_k3.value,str('Blum'+i),aK3)
        else:
            s_e = k3.getattrtext(0,str('Blum'+i),aK3)
            obj_k3 = None
        #print s_e
        lstt = []
        i_count=0
        for j in range(int(s_e)):
            lstt.append(aK3[j].value)
            i_count = +1
        lstF.append(lstt)
        #print i,'   ',i_count
    return lstF,obj_k3

def objK3_Update(varNiche=True):
    '''Редактирует объект типа Blumotyp'''
    lstFF=read_BlumAtrr()
    lstF,obj_k3 = lstFF
    res = mDy.expProjectFilesToStr(dynalog.projectFolder,'shkaf',lstF,dynalog.listExtensionRoot)
    #print res
    root = None
    if res:
        # если были  внесены изменения в проект
        if varNiche == False:
            k3.setucs(k3.k_lcs,obj_k3.value)
        k3.setucs(k3.k_save,'tnSaveNiche')
        if type(obj_k3)==k3.Var: k3.delete(obj_k3.value,k3.k_done)
        k3.setucs(k3.k_save,"KarkasUcs")
        listFiles = mDy.getsubs(dynalog.projectFolder)
        listBXF=mDy.getfilemask(listFiles[1],'*.bxf')
        infilename = mDy.getungfiles(listBXF)
        #ISDEBUG.Print( infilename )
        root = parse(infilename)
        k3.setucs(k3.k_restore,"KarkasUcs")
        #k3.chprop(k3.k_mapbypars,k3.k_partly,k3.k_attribute,'left(Furntype,2)==\"01\"',k3.k_done,11,70,k3.k_done)
    return root, res
#-------------------------------------------------------------------------------
def newobject():
    '''Создает новый объект'''
    # создаем файл старта
    writer = Writer(varinst.BackBlumType)
    fname = "shkaf"
    fullName = writer.CreateBxfFile(fname)
    Po=defmaterial.getThickness(defmaterial.basematerial) # Толщина верхних панелей
    KRwd=defmaterial.getThickness(defmaterial.backmaterial) # Толщина задней стенки
    Pr=defmaterial.getThickness(defmaterial.seitematerial) #боковые стенки

    writer.bxfOutCommand(Sk=varinst.KorpBlumType,Po=Po, Pu=Po, Pr=Pr, Pl=Pr,  OTravDhin=Po ,OTravDvor=Po, # толщины
                    KH=varinst.H,KT=varinst.D,KAB=varinst.W,LW=varinst.W-2*Pr,TypOB=varinst.CoverBlumTyp,TypRK=varinst.BackBlumType)
    #print(fullName)
    res=mDy.DynaplanStartBXF(fullName)
    if res:
        gVarKorpus = True
        ISDEBUG.debug = False
        k3.setucs(k3.k_save,"KarkasUcs")
        listFiles = mDy.getsubs(dynalog.projectFolder)
        listBXF=mDy.getfilemask(listFiles[1],'*.bxf')
        infilename = mDy.getungfiles(listBXF)
        #ISDEBUG.Print( infilename )
        root = parse(infilename)
        k3.setucs(k3.k_restore,"KarkasUcs")
        k3.setucs(k3.k_delete,"KarkasUcs")
        #k3.chprop(k3.k_mapbypars,k3.k_partly,k3.k_attribute,'left(Furntype,2)==\"01\"',k3.k_done,11,70,k3.k_done)
    else:
        pass
    return
#-------------------------------------------------------------------------------
def editobject():
    '''Редактирует объект'''
    global gVarKorpus
##    gVarKorpus = True
    ISDEBUG.debug = False
    root,res = objK3_Update()
    if res:
        OBJA=k3.Var()
        k3.objident(k3.k_last,1,OBJA)
        k3.setucs(k3.k_restore,"KarkasUcs")
        k3.setucs(k3.k_delete,"KarkasUcs")
        k3.group(OBJA.value,k3.k_done)
        k3.objident(k3.k_last,1,OBJA)
        k3.setucs(k3.k_restore,'tnSaveNiche')
        k3.place(OBJA.value)
        #k3.move(k3.k_nocopy,OBJA.value,k3.k_done,(-root.Korpusdaten.Plattendicken.Rechts,0.,-root.Korpusdaten.Plattendicken.Unten))
        k3.explode(OBJA.value,k3.k_done)
        k3.setucs(k3.k_delete,"tnSaveNiche")
    else:
        pass
    return
#-------------------------------------------------------------------------------
def ErrMsg(key=1):
    dict_msg = {
        1:'''aaa= k3.alternative(
    str("Ошибка!!!"),
    k3.k_msgbox, k3.k_picture, 3, k3.k_beep, 3, k3.k_default, 2,
    k3.k_text, k3.k_left,
    str("На Вашем компьютере не найден установленный Dynalog!"),
    str("Создание объекта невозможно."),
    k3.k_done,
    str("Ок"),
    k3.k_done)'''
    }
    code_object = compile(dict_msg[key],'<string>', 'exec')
    exec(code_object)
    return aaa[0]

#-------------------------------------------------------------------------------
def __init__():
    #print(dynalog.RegPathDynalog)
    if not dynalog.RegPathDynalog:
        ErrMsg(1)
        return
    params  = k3.getpar()
    #print params[0]
    if k3.isattrdef("FixHole")==False:
            k3.attribute(k3.k_create, "FixHole", str("Крепеж комплектующих"), k3.k_string, 15, 80)
    if len(params)==0:
        print(('\nТребуется указать имя вызываемой функции в модуле ' + __file__))
    else:
        namedef = params[0].lower()
        #print(namedef)
        f = globals().get(namedef, None)
        if f is None or not hasattr(f, '__call__'):
            print(('\nНе найдена вызываемая функция с именем ' + namedef + ' в модуле ' + __file__))
        else:
            if len(params)==1:
                f()
                return
            elif len(params)>1: f(params[1:])
    return



def main():
##    args = sys.argv[1:]
##    if len(args) != 1:
##        usage()
##    infilename = args[0]
##    root = parse(infilename)
    global gVarKorpus
    gVarKorpus = True
    ISDEBUG.debug = False
    if k3.isattrdef("FixHole")==False:
        k3.attribute(k3.k_create, "FixHole", str("Крепеж комплектующих"), k3.k_string, 15, 80)
    k3.setucs(k3.k_save,"KarkasUcs")
    listFiles = mDy.getsubs(gExportPath)
    listBXF=mDy.getfilemask(listFiles[1],'*.bxf')
    infilename = mDy.getungfiles(listBXF)
    #ISDEBUG.Print( infilename )
    #infilename = 'c:\Users\USER\Documents\Blum\Dynaplan\Export\PlKorpus.bxf'
    #global root, stt
    root = parse(infilename)
    k3.setucs(k3.k_restore,"KarkasUcs")
    k3.setucs(k3.k_delete,"KarkasUcs")
    #k3.chprop(k3.k_mapbypars,k3.k_partly,k3.k_attribute,'left(Furntype,2)==\"01\"',k3.k_done,11,70,k3.k_done)
    #k3.holes(k3.k_create,k3.k_all)
    return



if __name__ == '__main__':
    #import pdb; pdb.set_trace()
    #main()
    #macro protopath+"blum_sub7.py" "main";
    #nishe()
    __init__()


