# -*- coding: cp1251 -*-
import k3
# import wingdbstub
params = k3.getpar()
nZFt= params[0]
sZFt= params[1]
ZFt = params[2]  #k3.GlobalVarArray('gs_ZFt')

lZFt=[a.value for a in ZFt]
defnull=lambda val: val if val>0 else 0
nZFt.value= len(lZFt) - lZFt.count(0)
sZFt.value=sum(map(defnull,lZFt))