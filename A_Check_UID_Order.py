# -*- coding: cp1251 -*-
import k3
import uuid
# str(uuid.uuid4())
# import wingdbstub

params = k3.getpar()

LayName='OrderUUID'
countr=int(k3.countlayers())

arrname = k3.VarArray(countr,'Lay')
arrprop = k3.VarArray(countr,'OnOff')
result = k3.namelayers(arrname, arrprop)

KeyOnLay = False

for i in range(countr):
    if arrname[i].value == LayName:
        #print LayName
        KeyOnLay = True
        if arrprop[i].value==1:
            k3.layers(k3.k_on, LayName)
            break

if KeyOnLay == False:           
    k3.layers(k3.k_new, LayName)
    k3.layers(k3.k_on, LayName)

lObj = {}
k3.selbyattr('Posit==999',k3.k_partly,k3.k_all,k3.k_done)
n = int(k3.sysvar(61))
print(n)

if n == 0:
    bx = k3.box(0,0,0,10,10,10)
    GUID = str(uuid.uuid4())
    k3.attrobj(k3.k_attach, 'ElemName', k3.k_done, k3.k_partly, bx, GUID)
    k3.attrobj(k3.k_attach, 'Posit', k3.k_done, k3.k_partly, bx, 999)
    k3.chprop(k3.k_layer, k3.k_partly, bx, k3.k_done, LayName)
    bx = bx[0] # k3.box возвращает tuple
    
if n > 0:
    bx = k3.getselnum(1)
    GUID = k3.getattr(bx,"ElemName",'')

k3.layers(k3.k_off, LayName) 

params[0].value = GUID
params[1].value = bx