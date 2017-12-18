# -*- coding: utf-8 -*-
import k3

n_scrFas = k3.Var() # Количество групп отделок
nullout=k3.getvarinst(2,"n_scrFas",n_scrFas,0)
n_scrFas = int(n_scrFas.value)
SrcFasGroup = k3.VarArray(n_scrFas) # ID группы отделки
nullout=k3.getarrinst(2,"SrcFasGroup",SrcFasGroup)
SrcFasName = k3.VarArray(n_scrFas)  # Название группы отделки
nullout=k3.getarrinst(2,"SrcFasName",SrcFasName)
SrcFasEntF = k3.VarArray(n_scrFas)  # Названия переменных для Тыла
nullout=k3.getarrinst(2,"SrcFasEntF",SrcFasEntF)
SrcFasEntA = k3.VarArray(n_scrFas)  # Названия переменных для Лица
nullout=k3.getarrinst(2,"SrcFasEntA",SrcFasEntA)

def CheckVar(NameVar, ir):

    return (str(int(k3.GlobalVar(NameVar+str(ir)).value)) if k3.isvardef(NameVar+str(ir)) > 0 else "0")
    
Namescr="FasadPar";
g_Scratch=k3.GlobalVar('g_Scratch')
params = k3.getpar()
pnt, FasCode = params

res=k3.calcvarscr(g_Scratch.value,  FasCode.value) # Читаем из скретча

nulldf, nulldf1 = k3.Var(), k3.Var()
gs_Nfasad=int(k3.GlobalVar('Nfas').value)
lNfasad=list(range(gs_Nfasad))
lNfasad.reverse()
aDecor = k3.VarArray(n_scrFas*gs_Nfasad)
fDecor = k3.VarArray(n_scrFas*gs_Nfasad)
listtst = []
for ir in lNfasad:
    listtst.append((k3.k_logical, k3.k_default, 1,  "-- Фасад N "+str(ir+1)+"---------------------------------", nulldf,))
    listtst.append((k3.k_logical, k3.k_default, 1,  "-- Сторона лицо(A) ----------", nulldf1,))
    
    for a in range(n_scrFas):
        listtst.append((k3.k_string, k3.k_button, 6, k3.k_auto, k3.k_default,
                        # CheckVar("АГрпОтд{}".format(a+1), ir+1)+'#'+CheckVar("АМатОтд{}".format(a+1), ir+1),
                        str(SrcFasGroup[a].value)+'#'+CheckVar("АМатОтд{}".format(a+1), ir+1),
                        str(SrcFasName[a].value), aDecor[ir*n_scrFas+a],))
                        
    listtst.append((k3.k_logical, k3.k_default, 1,  "-- Сторона тыл(F) ----------", nulldf1,))
    
    for f in range(n_scrFas):
        listtst.append((k3.k_string, k3.k_button, 6, k3.k_auto, k3.k_default,
                        # CheckVar("FГрпОтд{}".format(f+1), ir+1)+'#'+CheckVar("FМатОтд{}".format(f+1), ir+1),
                        str(SrcFasGroup[f].value)+'#'+CheckVar("FМатОтд{}".format(f+1), ir+1),
                        str(SrcFasName[f].value), fDecor[ir*n_scrFas+f],))

ok_flag=k3.setvar(
    "Фасад сплошной",
    "",
    k3.k_left,
    "Выберите параметры фасада",
    k3.k_done,
    listtst
    ,k3.k_done)

k3.addscratch(g_Scratch.value, FasCode.value,"Nfas",int(gs_Nfasad))
for ir in lNfasad:
    for a in range(n_scrFas):
        DecorA = aDecor[ir*n_scrFas+a].value
        dec = DecorA.split('#')[1] if len(DecorA.split('#')) > 1 else 0
        k3.addscratch(g_Scratch.value, FasCode.value,"АМатОтд{}{}".format(a+1,ir+1),dec)
        
        DecorF = fDecor[ir*n_scrFas+a].value
        dec = DecorF.split('#')[1] if len(DecorF.split('#')) > 1 else 0
        k3.addscratch(g_Scratch.value, FasCode.value,"FМатОтд"+str(a+1)+str(ir+1),dec)
        
k3.writescratch(g_Scratch.value,Namescr,pnt.value)

