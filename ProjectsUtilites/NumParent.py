# -*- coding: utf-8 -*-

import k3
import Utilites_K3 as Ut
# import wingdbstub
# protopath = k3.GlobalVar('protopath').value

if __name__ == '__main__':
    
    def IncludePan(dict, chDict):
        "Исключаем отдельно нумеруемые панели из глобального общего списка панелей сцены"
        for rb in dict:
            for panr in dict[rb]:
                for pkey in chDict:
                    plist = chDict[pkey]
                    if panr in plist:
                        chDict[pkey].remove(panr)
    
    def GetChildPans(AforD):
        "Заполняем из массива словарь всеми дочерними панелями групп"
        Dict = {}
        for Arr in AforD:
            for elem in Arr:
                obj = elem.value
                if isinstance(obj, k3.K3Obj):
                    # Заполнение дочерних панелей
                    for pl in Pans.values():
                        for p in pl:
                            if k3.findobjholdg(obj, p) > 0:
                                if obj in Dict:
                                    Dict[obj].append(p)
                                else:
                                    Dict[obj] = [p]
        return Dict
    
    def GetData(ScrMod, ParGroup):
        # Чтение скрэйтча
        # print(ParGroup.value)
        Data='';
        CurIDM=k3.Var('CurIDM');
        numpar=k3.cntvarscr(ScrMod,ParGroup)
        if numpar>0:
            
            DSArr = k3.VarArray(int(numpar))
            numP = k3.namevarscr(ScrMod,ParGroup,DSArr)
            
            for ScrPar in DSArr:
                # print(ScrPar.value)
                nullout=k3.getscratch(ScrMod,ParGroup,ScrPar,CurIDM,psc);
                Data += "#"+str(CurIDM.value)
        
        return Data
    
    NameAtrPos="CommonPos"
    
    Pans = {}
    # Boxs = {}
    Dsys = {}
    # Rubb = {}
    ArrPans = Ut.getListArrayAllObjectsScene(AttrFilter='left(furntype,2)==\"01\"')
    ArrBoxs = Ut.getListArrayAllObjectsScene(AttrFilter='left(furntype,4)==\"3101\"')
    ArrDsys = Ut.getListArrayAllObjectsScene(AttrFilter='furntype==\"210000\"')
    ArrRubb = Ut.getListArrayAllObjectsScene(AttrFilter='left(furntype,5)==\"10001\"')
    
    psc=k3.Var('psc')
    
    # Панели
    for elem in [elem for Arr in ArrPans for elem in Arr]:
        obj = elem.value
        if isinstance(obj, k3.K3Obj):
            if k3.isassign("FurnType", obj):
                tt = k3.getattr(obj, "FurnType", "")
            else:
                tt = 'xxxxxx'
            # находим панели, но не полотна панелей
            if tt[:2] == '01' and tt[2:] in ['0000', '1000']:
                continue
            Number = k3.getattr(obj, "Number", "")
            # Pans[obj] = Number
            if Number in Pans:
                Pans[Number].append(obj)
            else:
                Pans[Number] = [obj]
    
    # Ящики
    Boxs = GetChildPans(ArrBoxs)
    
    BxUn = {}
    for elem in [elem for Arr in ArrBoxs for elem in Arr if isinstance(elem.value, k3.K3Obj)]:
        Name = k3.getattr(elem, "FurnType", "")
        print(Name)
    
    DSUn = {}
    # Двери-купе
    for elem in [elem for Arr in ArrDsys for elem in Arr]:
        aFlap = elem.value
        if isinstance(aFlap, k3.K3Obj):
            # Нахождение одинаковых дверей
            Name = k3.getattr(aFlap, "ElemName", "")
            PriceID = k3.getattr(aFlap, "PriceID", 0)
            # NameScr = 'ScrFlat'
            Data1 = k3.Var('Data1')
            ScrMod=0;
            # NVst=0
            ParGroup=k3.Var('ParGroup')
            
            if k3.isassign('ScrFlat',aFlap):
                ScrMod=k3.readscratch('ScrFlat',aFlap)
            
            if ScrMod>0:
                
                ParGroup.value="ВставкаМ";
                Data1.value = GetData(ScrMod, ParGroup)
                
                ParGroup.value="Текстура";
                Data1.value += GetData(ScrMod, ParGroup)
                
                ParGroup.value="Профиль";
                Data1.value += GetData(ScrMod, ParGroup)
                
                ParGroup.value="ID профиля";
                Data1.value += GetData(ScrMod, ParGroup)
                
                ParGroup.value="X начала";
                Data1.value += GetData(ScrMod, ParGroup)
                
                ParGroup.value="Z начала";
                Data1.value += GetData(ScrMod, ParGroup)
                
                ParGroup.value="X конца";
                Data1.value += GetData(ScrMod, ParGroup)
                
                ParGroup.value="Z конца";
                Data1.value += GetData(ScrMod, ParGroup)
                
                ParGroup.value="ОтделкаВс";
                Data1.value += GetData(ScrMod, ParGroup)
                
                ParGroup.value="ОтделкаМЛ";
                Data1.value += GetData(ScrMod, ParGroup)
                
                # ParGroup="Вставка";
                # NVst=k3.Var('NVst')
                # nullout=k3.getscratch(ScrMod,ParGroup,"Колво",NVst,psc);
                
                if Data1.value in DSUn:
                    DSUn[Data1.value].append(aFlap)
                else:
                    DSUn[Data1.value] = [aFlap]
            
            # Заполнение дочерних панелей
            for pl in Pans.values():
                for p in pl:
                    if k3.findobjholdg(aFlap, p) > 0:
                        if aFlap in Dsys:
                            Dsys[aFlap].append(p)
                        else:
                            Dsys[aFlap] = [p]
    
    
    Rubb = GetChildPans(ArrRubb)
    
    # Исключим из словаря панелей, дочек ящиков и дверей-купе
    IncludePan(Boxs, Pans)
    IncludePan(Dsys, Pans)
    # Исключим панели резинового шкафа
    # В резиновом шкафе присутствуют двери-купе и могут ящики
    IncludePan(Rubb, Pans)
    # IncludePan(Rubb, Boxs)
    # IncludePan(Rubb, Dsys)

    # Список всех панелей резинового шкафа
    lstrubbpan = [b for a in Rubb.values() for b in a if isinstance(a, list)]

    num = 0
    
    nDr=101;           
    for UnD in DSUn:
        num += 1
        for door in DSUn[UnD]:
            # print("door",door,"=",Dsys[door])
            pnum = 0
            pnDr = 0
            KeyRubb = False
            for pand in Dsys[door]:
                if isinstance(pand, k3.K3Obj):
                    # Проверим является ли панель частью РезШк
                    # print(Rubb.items())
                    if pand in lstrubbpan:
                        # print("+")
                        pnDr += 1
                        KeyRubb = True
                        k3.attrobj(k3.k_attach, NameAtrPos, k3.k_done,
                                   k3.k_partly, pand, float('{}.{}'.format(nDr,pnDr)))
                    else:
                        pnum += 1
                        k3.attrobj(k3.k_attach, NameAtrPos, k3.k_done,
                                   k3.k_partly, pand, float('{}.{}'.format(num,pnum)))
            if KeyRubb:
                nDr += 1
    
    # print(Pans)
    for ps in Pans:
        if len(Pans[ps])>0:
            num += 1
            for pan in Pans[ps]:
                k3.attrobj(k3.k_attach, NameAtrPos, k3.k_done, k3.k_partly, pan, num)
    
    for box in Boxs:
        # print("box",box,"=",Boxs[box])
        num += 1
        pnum = 0
        for pbox in Boxs[box]:
            if isinstance(pbox, k3.K3Obj):
                pnum += 1
                k3.attrobj(k3.k_attach, NameAtrPos, k3.k_done,
                           k3.k_partly, pbox, float('{}.{}'.format(num,pnum)))
                # print("k_attach_up=",k3.getattr(pbox, "UnitPos", ""))
