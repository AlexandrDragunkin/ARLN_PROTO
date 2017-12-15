# -*- coding: cp1251 -*-
#import wingdbstub
import k3 # Подключаем модуль k3

params=k3.getpar()
pl_pnt,nElStr,aNAtr = params[0],params[1],params[2]

S_val = ''

for i in range(int(nElStr)):
    elem = aNAtr[i]
    vv = elem.value if type(elem.value)==float else k3.getattr(0,elem.value,elem.value)
    if type(vv)==float:
        if abs(vv-int(vv))<0.1:
            vv = int(vv)
    else:         
        pos = k3.instr(1,vv,"{",1)
        if pos>0:
            l_vv=len(vv)
            cod = k3.right(vv,l_vv-pos)            
            v_result,v_error = k3.Var(), k3.Var()
            k3.expression(cod,v_result,v_error) 
            if len(v_error.value)>1:
                print v_error.value
            vv = v_result.value    
    S_val = S_val + str(vv)
if len(S_val)>0:
    pl_pnt.value = S_val