# -*- coding: utf-8 -*-

import k3
import Utilites_K3 as Ut
# import wingdbstub
# protopath = k3.GlobalVar('protopath').value

if __name__ == '__main__':
    
    def IncludePan(dict, chDict):
        "Исключаем отдельно нумеруемые панели из глобального общего списка панелей сцены"
        for panr in [panr for rb in dict for panr in dict[rb]]:
            for pkey in [pkey for pkey in chDict if panr in chDict[pkey]]:
                chDict[pkey].remove(panr)
    
    def GetChildPans(AforD):
        "Заполняем из массива словарь всеми дочерними панелями групп  на любом уровне"
        Dict = {}
        for obj in [elem.value for Arr in AforD for elem in Arr if isinstance(elem.value, k3.K3Obj)]:
            for p in [p for pl in Pans.values() for p in pl if k3.findobjholdg(obj, p) > 0]:
                if obj in Dict:
                    Dict[obj].append(p)
                else:
                    Dict[obj] = [p]

        return Dict
    
    def GetData(ScrMod, ParGroup):
        # Чтение скрэйтча
        Data='';
        CurIDM=k3.Var('CurIDM');
        numpar=k3.cntvarscr(ScrMod,ParGroup)
        if numpar>0:
            DSArr = k3.VarArray(int(numpar))
            numP = k3.namevarscr(ScrMod,ParGroup,DSArr)
            for ScrPar in DSArr:
                nullout=k3.getscratch(ScrMod,ParGroup,ScrPar,CurIDM,psc);
                Data += "#"+str(CurIDM.value)
        
        return Data
    
    NameAtrPos="CommonPos"
    
    Pans = {}
    Dsys = {}
    ArrPans = Ut.getListArrayAllObjectsScene(AttrFilter='left(furntype,2)==\"01\"')
    ArrBoxs = Ut.getListArrayAllObjectsScene(AttrFilter='left(furntype,4)==\"3101\"')
    ArrDsys = Ut.getListArrayAllObjectsScene(AttrFilter='furntype==\"210000\"')
    ArrRubb = Ut.getListArrayAllObjectsScene(AttrFilter='left(furntype,5)==\"10001\"')
    
    psc=k3.Var('psc')
    num = 0
    
    # Панели
    for obj in [elem.value for Arr in ArrPans for elem in Arr if isinstance(elem.value, k3.K3Obj)]:
        if k3.isassign("FurnType", obj):
            tt = k3.getattr(obj, "FurnType", "")
        else:
            tt = 'xxxxxx'
        # находим панели, но не полотна панелей
        if tt[:2] == '01' and tt[2:] in ['0000', '1000']:
            continue
        Number = k3.getattr(obj, "Number", "")
        if Number in Pans:
            Pans[Number].append(obj)
        else:
            Pans[Number] = [obj]
    
    # Ящики
    BxUn = {}
    # Находим одинаковые по составу панелей ящики
    Boxs = GetChildPans(ArrBoxs)
    for listpinbox in Boxs.values():
        lpan = []
        dpan = {}
        for pan in listpinbox:
            tn = k3.getattr(pan,"Number",0)
            if tn not in dpan:
                dpan[tn] = [pan]
            else:
                dpan[tn].append(pan)
            lpan.append(tn)
        lpan.sort()
        if tuple(lpan) not in BxUn:
            num += 1
            BxUn[tuple(lpan)] = num
            numf = num
        else:
            numf = BxUn[tuple(lpan)]
        pnum = 0
        for np in lpan:
            pnum += 1 
            for pn in dpan[np]:
                k3.attrobj(k3.k_attach, NameAtrPos, k3.k_done,
                           k3.k_partly, pn, float('{}.{}'.format(numf,pnum)))
                           
    Rubb = GetChildPans(ArrRubb)
    # Список всех панелей резинового шкафа
    lstrubbpan = [b for a in Rubb.values() for b in a if isinstance(a, list)]
    
    # Новый сопсобо по составляющим Number дверей-купе
    # В создании базы способ чтения скрейтчей
    DSUn = {}
    # Двери-купе
    nDr = 101
    pnDr = 0
    Dsys = GetChildPans(ArrDsys)
    for listpindoor in Dsys.values():
        lpan = []
        dpan = {}
        for pan in listpindoor:
            tn = k3.getattr(pan,"Number",0)
            if tn not in dpan:
                dpan[tn] = [pan]
            else:
                dpan[tn].append(pan)
            lpan.append(tn)
        lpan.sort()    
        pnDr += 1
        if tuple(lpan) not in DSUn:
            num += 1
            DSUn[tuple(lpan)] = num
            numf = num
        else:
            numf = DSUn[tuple(lpan)]
        pnum = 0
        KeyRubb = False
        for np in lpan:
            pnum += 1
            for pn in dpan[np]:
                if pn in lstrubbpan:
                    KeyRubb = True
                    k3.attrobj(k3.k_attach, NameAtrPos, k3.k_done,
                               k3.k_partly, pn, float('{}.{}'.format(nDr,pnDr)))
                else:
                    k3.attrobj(k3.k_attach, NameAtrPos, k3.k_done,
                               k3.k_partly, pn, float('{}.{}'.format(numf,pnum)))
        if KeyRubb:
            nDr += 1
        
    # Исключим из словаря панелей, дочек ящиков и дверей-купе
    IncludePan(Boxs, Pans)
    IncludePan(Dsys, Pans)
    # Исключим панели резинового шкафа
    # В резиновом шкафе присутствуют двери-купе и могут ящики
    IncludePan(Rubb, Pans)
    # IncludePan(Rubb, Boxs)
    # IncludePan(Rubb, Dsys)
    
    for ps in Pans:
        if len(Pans[ps])>0:
            num += 1
            for pan in Pans[ps]:
                k3.attrobj(k3.k_attach, NameAtrPos, k3.k_done, k3.k_partly, pan, num)
    
    
    
