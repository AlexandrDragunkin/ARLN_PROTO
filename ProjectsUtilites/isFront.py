# -*- coding: utf-8 -*-
import k3
from mPanel import (PanelRectangle)
    
def isfront(Panel):
    "Определяет пласть являющуюся лицом"
    
    FrontF = False      # True - Лицо по пласти F
    NeedEskisA= False    # Нельзя однозначно разобраться без эскиза где лицо
    NeedEskisF= False
    KeyDecA = False     # Наличие отделки по A
    KeyDecF = False     # Наличие отделки по F
    KeyPropF = False    # Наличие свойства определяющего лицо по F
    if Panel.cover_count > 0:
        for dec in Panel.cover_info.keys():
            if dec==5.:
                KeyDecA=True
            if dec==6.:
                KeyDecF=True
            if dec==-1:
                KeyDecA=True
                KeyDecF=True        
            if 334. in Panel.cover_info[dec]:
                # Ключ наличия свойства явного указания лица
                KeyPropF = True
                # FrontF = True

        drill_A = False
        drill_F = False
        drill_X = False
        if 'holes' in Panel.__dict__.keys():
            # Panel.counter.drill_A
            for hole in Panel.holes:
                if hole.Side in 'A':
                    drill_A = True
                if hole.Side in 'F':
                    drill_F = True
                if hole.Side in ['B', 'C', 'D', 'E', 'X']:
                    drill_X = True
                # print(hole.counter.drill_A)
                
        # Сверка сверловок по пластям и отделок по пластям
        # при наличии свойства
        if KeyPropF==True:
            FrontF = True
        
        # Присадка кроме пластей A,F - эскиз
        if drill_X:
            if KeyDecA:
                NeedEskisA = True
            if KeyDecF:
                NeedEskisF = True
        else:
            # print('drill_A,drill_F,KeyDecA,KeyDecF = ',drill_A,drill_F,KeyDecA,KeyDecF)
            # Сверловка только по F и свойство лицо по F противоречат друг другу
            if (drill_A,drill_F,KeyPropF)==(False,True,True):
                print('Найдено несоответствие: Сверловка только по F и задано лицо по F')
                FrontF = False
                
            # Если сверловка по обоим пластям
            if (drill_A,drill_F)==(True,True):
                if KeyDecA:
                    NeedEskisA = True
                if KeyDecF:
                    NeedEskisF = True
            
            # Сверловка только по A, отделка только по F - всегда лицо по F
            if (drill_A,drill_F,KeyDecA,KeyDecF)==(True,False,False,True):
                FrontF = True
            
            # Сверловка по F, отделка по A - всегда лицо по A
            if (drill_A,drill_F,KeyDecA,KeyDecF)==(False,True,True,False):
                FrontF = False
        
        # print('KeyPropF=',KeyPropF)    
        # print('FrontF=',FrontF)
        # print('NeedEskisA=',NeedEskisA)
        # print('NeedEskisF=',NeedEskisF)
    # Одна отделка, являющаяся свойством лица по F для глянцевых материалов
    elif Panel.cover_count==1 and KeyPropF:
        FrontF = True
    
    return FrontF, NeedEskisA, NeedEskisF

if __name__ == '__main__':
    
    # print("main")
    pars=k3.getpar()
    # print(pars)
    # global Panel    
    # if 'Panel' in globals().keys():
        # del(Panel)
    Panel = PanelRectangle()
    
    pan=pars[0] # Объект к3 - панель
    # print(pan)
    Panel.panelInit(pan)
    Panel.getPanelProperty(pan)
    Panel.getPanelPathInfo(pan)
    FrontF = isfront(Panel) # Является ли пласть F лицом
    
    pars[1].value = 1 if FrontF==True else 0