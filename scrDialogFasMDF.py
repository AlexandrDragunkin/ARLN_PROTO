# -*- coding: utf-8 -*-
# import wingdbstub
import k3


def getscrparam(s,m,i):
    si=str(int(i)) if i>0 else ''
    v=k3.GlobalVar(s+si).value
    vm=k3.GlobalVar(m+si).value
    return str(v)+"#"+ str(int(vm)) if vm>10 else ''

def CheckVar(NameVar, ir):
    # print(str(int(k3.GlobalVar(NameVar+str(ir+1)).value)))
    return (str(int(k3.GlobalVar(NameVar+str(ir)).value)) if k3.isvardef(NameVar+str(ir)) > 0 else '')
    
    
Namescr="FasadPar";
g_Scratch=k3.GlobalVar('g_Scratch')
params  = k3.getpar()
pnt=params[0]
FasCode=params[1]
res=k3.calcvarscr(g_Scratch.value,  FasCode.value) # Читаем из скретча
# print(res)
# print(FasCode.value)
n=7
nulldf, nulldf1=k3.Var(),k3.Var()
aDecor1,aDecor2,aDecor3,aDecor4,aDecor5=k3.VarArray(n),k3.VarArray(n),k3.VarArray(n),k3.VarArray(n),k3.VarArray(n)
fDecor1,fDecor2,fDecor3,fDecor4,fDecor5=k3.VarArray(n),k3.VarArray(n),k3.VarArray(n),k3.VarArray(n),k3.VarArray(n)
aDecor6,aDecor7,aDecor8,aDecor9=k3.VarArray(n),k3.VarArray(n),k3.VarArray(n),k3.VarArray(n)
fDecor6,fDecor7,fDecor8,fDecor9=k3.VarArray(n),k3.VarArray(n),k3.VarArray(n),k3.VarArray(n)
#KCur=0;

gs_Nfasad=int(k3.GlobalVar('Nfas').value)
# print('scrDialog.py',gs_Nfasad)
lNfasad=list(range(gs_Nfasad))
lNfasad.reverse()
ok_flag=k3.setvar(
    "Фасад сплошной",
    "",
    k3.k_left,
    "Выберите параметры фасада",
    k3.k_done,
        [((k3.k_logical, k3.k_default, 0,  "-- Фасад N "+str(ir+1)+"---------------------------------", nulldf,),

         (k3.k_logical, k3.k_default, 1,  "-- Сторона лицо ----------", nulldf1,),
         #(k3.k_logical, k3.k_default, 0,  "Удалить отделку по лицу", nulldf1,),
         (k3.k_string, k3.k_button, 6, k3.k_auto, k3.k_default, CheckVar("FГрпОтд1", ir+1)+'#'+CheckVar("FМатОтд1", ir+1), 
                            "Эмаль", fDecor1[ir],),
         (k3.k_string, k3.k_auto, k3.k_button, 6, k3.k_default, CheckVar("FГрпОтд2", ir+1)+'#'+CheckVar("FМатОтд2", ir+1), 
                            "Лак", fDecor2[ir],),
         (k3.k_string, k3.k_auto, k3.k_button, 6, k3.k_default, CheckVar("FГрпОтд3", ir+1)+'#'+CheckVar("FМатОтд3", ir+1), 
                            "Тонировка(Бейтс)", fDecor3[ir],),
         (k3.k_string, k3.k_auto, k3.k_button, 6, k3.k_default, CheckVar("FГрпОтд4", ir+1)+'#'+CheckVar("FМатОтд4", ir+1), 
                            "Фрезеровка", fDecor4[ir],),
         (k3.k_string, k3.k_auto, k3.k_button, 6, k3.k_default, CheckVar("FГрпОтд5", ir+1)+'#'+CheckVar("FМатОтд5", ir+1), 
                            "Патина", fDecor5[ir],),
         (k3.k_string, k3.k_auto, k3.k_button, 6, k3.k_default, CheckVar("FГрпОтд6", ir+1)+'#'+CheckVar("FМатОтд6", ir+1), 
                            "Фотопечать", fDecor6[ir],),
         (k3.k_string, k3.k_auto, k3.k_button, 6, k3.k_default, CheckVar("FГрпОтд7", ir+1)+'#'+CheckVar("FМатОтд7", ir+1), 
                            "Трафаретная печать", fDecor7[ir],),
         (k3.k_string, k3.k_auto, k3.k_button, 6, k3.k_default, CheckVar("FГрпОтд8", ir+1)+'#'+CheckVar("FМатОтд8", ir+1), 
                            "Пленка", fDecor8[ir],),
         (k3.k_string, k3.k_auto, k3.k_button, 6, k3.k_default, CheckVar("FГрпОтд9", ir+1)+'#'+CheckVar("FМатОтд9", ir+1), 
                            "Кожа", fDecor9[ir],),
         (k3.k_logical, k3.k_default, 0,  "-- Сторона тыл ----------", nulldf1,),
         #(k3.k_logical, k3.k_default, 0,  "Удалить отделку по тылу", nulldf1,),
         (k3.k_string, k3.k_auto, k3.k_button, 6, k3.k_default, CheckVar("АГрпОтд1", ir+1)+'#'+CheckVar("АМатОтд1", ir+1), 
                            "Эмаль", aDecor1[ir],),
         (k3.k_string, k3.k_auto, k3.k_button, 6, k3.k_default, CheckVar("АГрпОтд2", ir+1)+'#'+CheckVar("АМатОтд2", ir+1), 
                            "Лак", aDecor2[ir],),
         (k3.k_string, k3.k_auto, k3.k_button, 6, k3.k_default, CheckVar("АГрпОтд3", ir+1)+'#'+CheckVar("АМатОтд3", ir+1), 
                            "Тонировка(Бейтс)", aDecor3[ir],),
         (k3.k_string, k3.k_auto, k3.k_button, 6, k3.k_default, CheckVar("АГрпОтд4", ir+1)+'#'+CheckVar("АМатОтд4", ir+1), 
                            "Фрезеровка", aDecor4[ir],),
         (k3.k_string, k3.k_auto, k3.k_button, 6, k3.k_default, CheckVar("АГрпОтд5", ir+1)+'#'+CheckVar("АМатОтд5", ir+1), 
                            "Патина", aDecor5[ir],),
         (k3.k_string, k3.k_auto, k3.k_button, 6, k3.k_default, CheckVar("АГрпОтд6", ir+1)+'#'+CheckVar("АМатОтд6", ir+1), 
                            "Фотопечать", aDecor6[ir],),
         (k3.k_string, k3.k_auto, k3.k_button, 6, k3.k_default, CheckVar("АГрпОтд7", ir+1)+'#'+CheckVar("АМатОтд7", ir+1), 
                            "Трафаретная печать", aDecor7[ir],),
         (k3.k_string, k3.k_auto, k3.k_button, 6, k3.k_default, CheckVar("АГрпОтд8", ir+1)+'#'+CheckVar("АМатОтд8", ir+1), 
                            "Пленка", aDecor8[ir],),
         (k3.k_string, k3.k_auto, k3.k_button, 6, k3.k_default, CheckVar("АГрпОтд9", ir+1)+'#'+CheckVar("АМатОтд9", ir+1), 
                            "Кожа", aDecor9[ir],),
         ) for ir in lNfasad] 
,k3.k_done)

k3.addscratch(g_Scratch.value, FasCode.value,"Nfas",int(gs_Nfasad))
for ir in range(gs_Nfasad):
    Decor=aDecor1[ir].value
    k3.addscratch(g_Scratch.value, FasCode.value,"АМатОтд1"+str(ir+1),Decor.split('#')[1])
    Decor=aDecor2[ir].value
    k3.addscratch(g_Scratch.value, FasCode.value,"АМатОтд2"+str(ir+1),Decor.split('#')[1])
    Decor=aDecor3[ir].value
    k3.addscratch(g_Scratch.value, FasCode.value,"АМатОтд3"+str(ir+1),Decor.split('#')[1])
    Decor=aDecor4[ir].value
    k3.addscratch(g_Scratch.value, FasCode.value,"АМатОтд4"+str(ir+1),Decor.split('#')[1])
    Decor=aDecor5[ir].value
    k3.addscratch(g_Scratch.value, FasCode.value,"АМатОтд5"+str(ir+1),Decor.split('#')[1])
    Decor=aDecor6[ir].value
    k3.addscratch(g_Scratch.value, FasCode.value,"АМатОтд6"+str(ir+1),Decor.split('#')[1])
    Decor=aDecor7[ir].value
    k3.addscratch(g_Scratch.value, FasCode.value,"АМатОтд7"+str(ir+1),Decor.split('#')[1])
    Decor=aDecor8[ir].value
    k3.addscratch(g_Scratch.value, FasCode.value,"АМатОтд8"+str(ir+1),Decor.split('#')[1])
    Decor=aDecor9[ir].value
    k3.addscratch(g_Scratch.value, FasCode.value,"АМатОтд9"+str(ir+1),Decor.split('#')[1])
    Decor=fDecor1[ir].value
    k3.addscratch(g_Scratch.value, FasCode.value,"FМатОтд1"+str(ir+1),Decor.split('#')[1])
    Decor=fDecor2[ir].value
    k3.addscratch(g_Scratch.value, FasCode.value,"FМатОтд2"+str(ir+1),Decor.split('#')[1])
    Decor=fDecor3[ir].value
    k3.addscratch(g_Scratch.value, FasCode.value,"FМатОтд3"+str(ir+1),Decor.split('#')[1])
    Decor=fDecor4[ir].value
    k3.addscratch(g_Scratch.value, FasCode.value,"fМатОтд4"+str(ir+1),Decor.split('#')[1])
    Decor=fDecor5[ir].value
    k3.addscratch(g_Scratch.value, FasCode.value,"FМатОтд5"+str(ir+1),Decor.split('#')[1])
    Decor=fDecor6[ir].value
    k3.addscratch(g_Scratch.value, FasCode.value,"fМатОтд6"+str(ir+1),Decor.split('#')[1])
    Decor=fDecor7[ir].value
    k3.addscratch(g_Scratch.value, FasCode.value,"FМатОтд7"+str(ir+1),Decor.split('#')[1])
    Decor=fDecor8[ir].value
    k3.addscratch(g_Scratch.value, FasCode.value,"fМатОтд8"+str(ir+1),Decor.split('#')[1])
    Decor=fDecor9[ir].value
    k3.addscratch(g_Scratch.value, FasCode.value,"FМатОтд9"+str(ir+1),Decor.split('#')[1])
k3.writescratch(g_Scratch.value,Namescr,pnt.value);