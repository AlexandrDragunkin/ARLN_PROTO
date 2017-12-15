# -*- coding: utf-8 -*-
# import wingdbstub
import k3
def g(nm):
    ValType=k3.Var()
    PrM=k3.Var()
    PrM.value = 0
    sVal=k3.Var()
    k3.udgetentity(nm[0],ValType,PrM,sVal)
    # print(PrM.value)
    nm[2]=PrM.value
lbs=[
["u69_FoilBMF","Эмаль",0],              # 335
["u69_FoilORF","Фрезеровка",0],         # 340
["u69_FoilBLF","Тонировка",0],          # 337
["u69_FoilEFF","Лак",0],                # 338
["u69_FoilPTF","Патина",0],             # 341
["u69_FoilFPF","Фотопечать",0],         # 336
["u69_FoilTPF","Трафаретная печать",0], # 339
["u69_FoilFMF","Пленка",0],             # 346
["u69_FoilSKF","Кожа",0],               # 347
["u69_FoilBMA","Эмаль",0],
["u69_FoilORA","Фрезеровка",0],
["u69_FoilBLA","Тонировка",0],
["u69_FoilEFA","Лак",0],
["u69_FoilPTA","Патина",0],
["u69_FoilFPA","Фотопечать",0],
["u69_FoilTPA","Трафаретная печать",0],
["u69_FoilFMA","Пленка",0],
["u69_FoilSKA","Кожа",0],
]
for a in lbs:
    g(a)
    k3.setvarinst(1,a[0],a[2])