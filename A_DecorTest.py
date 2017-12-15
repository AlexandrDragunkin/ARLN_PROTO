# -*- coding: utf-8 -*-
import k3
import Utilites_K3 as Ut
from mPanel import (PanelRectangle)
Panel = PanelRectangle()

def PropInfo(ID,Name,Typ,defVal=0):
    '''возвращает значение свойство Name изделия с ID из базы'''
    result=None
    #try:
    result=k3.Var()
    result=k3.priceinfo(ID,Name,defVal,Typ)
    #except KeyError, ID,Name:
        #raise AttributeError, ID
    return result

def menu_append(string):
    "Накапливаем сообщения для вывода"
    lMenu.append(string)
    return True
    
# def menu():
    # vFailColor = k3.Var()
    # k3.getvarinst(2,"FailColor", vFailColor,12)
    # FailColor = vFailColor.value
    # k3.select(k3.k_stayblink, k3.k_partly, obj, k3.k_done)
    # ok_flag = k3.alternative( "Найдено несоответствие", 
    # k3.k_msgbox, k3.k_picture, 1, k3.k_beep, 1, k3.k_text, k3.k_left,
    # "Панель выделена мерцанием",
    # "У выделенной панели на пласти <'{}'> назначены группы:".format(side),
    # ', '.join(map(lambda x:nGroups[x], dPans[side])),
    # "",
    # ', '.join(lMenu),
    # "",
    # "Отключить мерцание найденных объектов?", 
    # k3.k_done, 
    # "Да",  "Нет", "Изменить цвет", 
    # k3.k_done)
    # if (ok_flag[0]==1):
        # k3.select(k3.k_all, k3.k_done)
    # elif (ok_flag[0]==3):
        # k3.chprop( k3.k_color, k3.k_partly , k3.k_previous, k3.k_done, FailColor)

def checkDecor(side, idgroup):
    if side=='A':
        if idgroup not in lGDecA:
            lGDecA.append(idgroup)
        if IDDecor in lIDDecA:
            lIDDecA[idgroup].append(IDDecor)
        else:
            lIDDecA[idgroup]= [IDDecor]
    if side=='F':
        if idgroup not in lGDecF:
            lGDecF.append(idgroup)
        if IDDecor in lIDDecF:
            lIDDecF[idgroup].append(IDDecor)
        else:
            lIDDecF[idgroup]= [IDDecor]

nGroups = {}
dDecors={
335. : 'DecEnamel',
336. : 'DecFoto',
337. : 'DecEffect',
338. : 'DecShine', # Лак
339. : 'DecTPrint',
340. : 'DecWork',
341. : 'DecPatina',
}
# Было нужно для сверки наличия лака глянцевого
dCheck={
338 : 9302 # Глянцевый
}
ArrPans = Ut.getListArrayAllObjectsScene(AttrFilter='left(furntype,2)==\"01\"')
# Панели
for Arr in ArrPans:
    for elem in Arr:
        obj = elem.value
        if isinstance(obj, k3.K3Obj):
            if k3.isassign("FurnType", obj):
                tt = k3.getattr(obj, "FurnType", "")
            else:
                tt = 'xxxxxx'
            # находим панели, но не полотна панелей
            if tt[:2] == '01' and tt[2:] in ['0000', '1000']:
                continue
            
            Panel.panelInit(obj)
            Panel.getPanelProperty(obj)
            KeyMenu = False
            lMenu = []
            lGDecA = []
            lGDecF = []
            lIDDecA = {}
            lIDDecF = {}
            dPans = {}
            if Panel.cover_count > 0:
                for cover in Panel.cover_info.items():
                    i = 0
                    while i<len(cover[1]):
                        if i%3==0 or i==0:
                            side = cover[0]
                            IDGroup = int(cover[1][i])
                            IDDecor = cover[1][i+1]
                            # print(side,IDGroup,cover[1][i+1])
                            if IDGroup == 334.: # Убираем отделку определяющую лицо по F
                                i += 1
                                continue
                            
                            if side==5:
                                checkDecor('A', IDGroup)
                            if side==6:
                                checkDecor('F', IDGroup)
                            if side==-1:
                                checkDecor('A', IDGroup)
                                checkDecor('F', IDGroup)
                            
                            if IDGroup not in nGroups:
                                zp1="SELECT Name FROM TProtoParType WHERE ID={}".format(IDGroup)
                                indrs=k3.adbopen(k3.adbcon(2),zp1)
                                total_s1=k3.adbreccount(indrs)
                                if total_s1>0:
                                    err=k3.adbmovefirst(indrs)
                                    nGroups[IDGroup]=k3.adbgetvalue(indrs,"Name",0)
                                else: nGroups[IDGroup]=""
                        i += 1
                        
                dPans['A'] = lGDecA
                dPans['F'] = lGDecF
                
                Shpon = False
                isMDF = False
                isDSP = False
                priceid = k3.getattr(obj, 'priceid', 0)
                parentid = k3.priceinfo(priceid, 'ParentID', 0, 1)
                pid = parentid if parentid > 0 else priceid
                MATTYPENAM = k3.priceinfo(pid, 'MATTYPENAM', "", 1)
                if MATTYPENAM[:4] == 'Шпон':
                    Shpon = True
                if MATTYPENAM[:3] == 'МДФ':
                    isMDF = True
                if MATTYPENAM[:4] == 'ДСтП':
                    isDSP = True
                for side in dPans:
                    if len(dPans[side])>0:
                        print("Пласть {} найдены отделки".format(side))
                        
                        # Выяснилось, что лак матовый не нужен, только в случае исключительно одной отделки эмалью
                        # и в случае отсутствия лицевых элементов с такой же покраской и с дополнительным набором
                        # отделок, которые обязательно идут под лак
                        
                        # Можно проанализировать весь набор отделок в сцене
                        
                        if side=='A':
                            if (338 in lGDecA) and (335 in lGDecA) and len(lGDecA)==2:
                                if dCheck[338] not in lIDDecA[338]:
                                    # dPans['A'].remove(338)
                                    KeyMenu = menu_append('''Нужно использовать эмаль с 'лак матовый' только в случае
                                    наличия в изделиях вариаций отделок, где 'лак матовый' необходим''')
                        if side=='F':
                            if (338 in lGDecF) and (335 in lGDecF) and len(lGDecA)==2:
                                if dCheck[338] not in lIDDecF[338]:
                                    # dPans['F'].remove(338)
                                    KeyMenu = menu_append('''Нужно использовать эмаль с 'лак матовый' только в случае
                                    наличия в изделиях вариаций отделок, где 'лак матовый' необходим''')                        
                        tmpv = ""
                        lstr = []
                        for var in dDecors:
                            strv = ">0" if var in dPans[side] else " is null"
                            lstr.append("[{}]{}".format(dDecors[var], strv))
                        if Shpon: lstr.append("[Shpon]>0")
                        if isMDF: lstr.append("[MDF]>0")
                        if isDSP: lstr.append("[DSP]>0")
                        # print(lstr)
                        # print("Shpon=",Shpon,",isMDF=",isMDF,",isDSP=",isDSP)
                        tmpv = " and ".join(lstr)
                        nG=k3.npgetbywhere(2,tmpv,"ARR");
                        if nG>0:
                            if nG>1: print("ВНИМАНИЕ: {} -> Кол-во найденных доступных записей вариаций отделок".format(nG))
                            aK3 = k3.VarArray(int(nG),'ARR')
                            # Должна находиться одна, но на всякий
                            for i in aK3:
                                IDGood = int(i.value)
                                mName = PropInfo(IDGood, "NAME", 2, "")
                            # Для шпона сверка на соответствие материала
                            if Shpon:
                                # print("IDGood=",IDGood)
                                nG=k3.priceinfo(IDGood, 'ListMat', "", 2, "tA")
                                # print(nG)
                                tAK3 = k3.VarArray(2*int(nG),'tA')
                                # print(tAK3)
                                if k3.findinarray(tAK3,pid,1,nG)==0:
                                    KeyMenu = menu_append(PropInfo(priceid,"MATNAME",1,"")+" нельзя использовать для данной вариации отделок")
                        else:
                            KeyMenu = menu_append("Данная вариация отсутствует в списке допустимых")

                        if KeyMenu:
                            if Shpon: type ="ШПОН"
                            if isMDF: type ="МДФ"
                            if isDSP: type ="ДСП"
                            
                            vFailColor = k3.Var()
                            k3.getvarinst(2,"FailColor", vFailColor,12)
                            FailColor = vFailColor.value
                            k3.select(k3.k_stayblink, k3.k_partly, obj, k3.k_done)
                            ok_flag = k3.alternative( "Предупреждение", 
                            k3.k_msgbox, k3.k_picture, 1, k3.k_beep, 1, k3.k_text, k3.k_left,
                            "Панель выделена мерцанием",
                            "Тип проверки: "+type,
                            "У выделенной панели на пласти <'{}'> назначены группы:".format(side),
                            ', '.join(map(lambda x:nGroups[x], dPans[side])),
                            "",
                            ', '.join(lMenu),
                            "",
                            "Отключить мерцание найденных объектов?", 
                            k3.k_done, 
                            "Да",  "Нет", "Изменить цвет", 
                            k3.k_done)
                            if (ok_flag[0]==1):
                                k3.select(k3.k_all, k3.k_done)
                            elif (ok_flag[0]==3):
                                k3.chprop( k3.k_color, k3.k_partly , k3.k_previous, k3.k_done, FailColor)
