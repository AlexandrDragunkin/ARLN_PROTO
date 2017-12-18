# -*- coding: utf-8 -*-
import k3
from mPanel import (PanelRectangle)
# from DrawingSupp import (drill_finder)
from drill_sp import Drill_SP
drs = Drill_SP()
import isFront
global Panel    
if 'Panel' in globals().keys():
    del(Panel)
Panel = PanelRectangle()

pars = k3.getpar()
pan = pars[0] # Объект к3 - панель
isEskis = pars[1] # Определяет наличие примечания См.Эскиз
mask = pars[2] # Маска поворота панели
# Front = pars[3].value # По какой пласти Лицо(по умолчанию 0 - по A)
slt = pars[4].value # Само примечание
length = pars[5].value
width = pars[6].value

nullout = k3.setvarinst(1,"IsUpil",0)

Panel.panelInit(pan)
Panel.getPanelProperty(pan)
Panel.getPanelPathInfo(pan)
FrontF, NeedEskisA, NeedEskisF = isFront.isfront(Panel) # Является ли пласть F лицом

if NeedEskisA:
    k3.setvarinst(1, "NeedEskisA", 1)
if NeedEskisF:
    k3.setvarinst(1, "NeedEskisF", 1)
    
k3.selbyattr('furntype==\"010000\"',k3.k_child,Panel.holder)
p=k3.getselnum(1)
nH=k3.getholes(p)
if nH>0:
    k3.VarArray(int(nH*15),'aHoles')
    nHH=k3.getholes(p,'aHoles')
    aHoles=k3.VarArray(int(nHH),'aHoles')
    nh=k3.Var()
    nh.value=int(nH)
    drs.drill_finder([aHoles,nh],Panel)

result = (Panel.rectangle_forma,
          max(len(Panel.slots), len(Panel.pSlots)),
          'holes' in Panel.__dict__.keys()
          )    

isEskis.value = 1
if result == (True, 0, False):
    isEskis.value = 0
    
dictSlot={1 : 'D',
          3 : 'C',
          5 : 'E',
          7 : 'B',
          9 : 'X',
          0 : 'X'
          }

# FrontF = False # True - Лицо по пласти F
# if Panel.cover_count > 0:
    # for dec in Panel.cover_info.keys():
        # if 334. in Panel.cover_info[dec]:
            # # front.value = 1
            # FrontF = True
pazcom = ""
for s in Panel.pSlots:
    # Если передаем еще маску для поворота 
    # if len(pars) >= 4:
    # slt.value=slt.value+'Паз '+dictSlot[int(k3.findinarray(mask,int(s.Side)))]+str(int(round((s.Shift),0)))+'['+str(int(s.Width))+'x'+str(int(s.Depth)) +'] '+' '
    # s.Plane = 1 - пласть A;
    # s.Plane = 0 - пласть F;
    res = (s.Plane==1, FrontF==True)
    # print(res)
    pazcom += 'Паз по {} {}{}[{}x{}]'.format(
    'Т' if res==(True, True) or res==(False, False) else 'Л', 
    dictSlot[int(k3.findinarray(mask,int(s.Side)))],
    int(round(s.Shift,0)),
    int(s.Width),
    int(s.Depth)
    )
    if len(pazcom)>0: pazcom += ';'

pars[3].value = 1 if FrontF==True else 0

lUnitCodeOut = ['3102', # Боковые стенки ящиков
                '3101',
                '2101', # Фасад ящика
               ]
               
# Нужно убирать см.эскиз и примечание паза для исключаемых
if k3.getattr(pan,"UnitCode",'') in lUnitCodeOut and \
   k3.getattr(pan,"ParentPos",0) and \
   k3.getattr(pan,"TopParentPos",0):
    isEskis.value = 0
else:
    slt += pazcom 

PathIn = 0
InfoPoly = Panel.getPanelPathInfo(pan,
                                  PathIn,
                                  IsCuts=False)  # Получаем информацию по результирующему полилайну

dBand = { 'D': 0, 'C': 0, 'E': 0, 'B': 0 }
for i, pp in enumerate(InfoPoly.paths):  # пошли по контурам
    dictT = { 'D':'', 'C':'', 'E':'', 'B':'', }
    dCoord = { 1:'D', 3:'C', 5:'E', 7:'B', }
    for el in pp.elems:
        if el.Band.Material > 0:
            if dCoord.get(el.IdLine,0):
            
                ind = dCoord[int(k3.findinarray(mask,int(el.IdLine)))]
                dBand[ind] = el.Band.Material
                # dBand[dCoord[el.IdLine]] = el.Band.Material
                
                Bndtp = k3.priceinfo(el.Band.Material, 'bandtype', 0, 1)
                if Bndtp in [1,2,3]:
                    v_article = k3.priceinfo(el.Band.Material, 'article', '***', 1)
                    alias = k3.priceinfo(el.Band.Material, 'Alias', v_article, 1)
                    if el.IdLine in dCoord and dCoord[el.IdLine] in dictT:
                        # dictT[dCoord[el.IdLine]] = alias
                        dictT[ind] = alias
    # Для еврокромки, шлифовки, фацета нужно примечание
    if (dictT['D'] == dictT['C'] == dictT['E'] == dictT['B']) and len(dictT['D'])>0:
        slt += "{} по периметру".format(dictT['D'])
    else:
        slt += ", ".join(["{} ({})".format(trz, dictT[trz]) for trz in dictT if len(dictT[trz])>0])

# Примечание УПИЛ
DSPmin = 75 # Габарит для упила
DSPupil = 120 # До скольки упиливать
if width < DSPmin or length < DSPmin:
    
    E = k3.priceinfo(dBand['E'], 'Dept', 0, 1)
    D = k3.priceinfo(dBand['D'], 'Dept', 0, 1)
    C = k3.priceinfo(dBand['C'], 'Dept', 0, 1)
    B = k3.priceinfo(dBand['B'], 'Dept', 0, 1)
    cutLen = round(max(C,B),0) if C and B else 0
    cutWdh = round(max(D,E),0) if D and E else 0
    
    if width < DSPmin:
        upil = width-cutWdh
        width = DSPupil
        
    if length < DSPmin:
        upil = length-cutLen
        length = DSPupil
        
    slt += "Упил с {} до {}".format(DSPupil, str(int(upil)))
    nullout = k3.setvarinst(1,"IsUpil",1)
    pars[5].value = length
    pars[6].value = width

pars[4].value = slt





