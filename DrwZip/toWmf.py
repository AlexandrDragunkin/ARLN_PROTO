# -*- coding: utf-8 -*-
# import wingdbstub
import k3

def getObj():
    k3.selbyattr('dsview',k3.k_partly,k3.k_all,k3.k_done)
    if k3.sysvar(61)>0:
        obj=k3.getselnum(1)
        return True, obj
    return False, None
    

Params = k3.getpar()
vnumWmf = Params[0] #k3.Var('vnumWmf')
k3.select(k3.k_all)
lobj=[]
for i in range(int(k3.sysvar(61))):
    lobj.append(k3.getselnum(i+1))
rs = getObj()
if rs[0]:
    hold=k3.Var()
    err=k3.getobjhold(rs[1],hold)
    holdo = hold.value
    k3.line(0., 0., 0., 100., 0., 0., k3.k_done)
    ls = k3.Var()
    k3.objident(k3.k_last, 1, ls)
    k3.add(k3.k_partly, holdo, ls.value)
    k3.extract(k3.k_partly, holdo, rs[1])
    k3.invisible(k3.k_wholly, lobj)
    k3.zoom(k3.k_oneview,k3.k_extents) 
    k3.exp2d(k3.k_wmf, k3.k_yes, k3.k_optimized, k3.k_yes, k3.k_fit, k3.k_yes, k3.k_height, 9500, k3.k_width,9500, k3.k_inscribe, k3.k_yes, vnumWmf.value, k3.k_overwrite ) 
    k3.visible(k3.k_wholly, lobj)
    rs = getObj()
    k3.add(k3.k_partly, holdo, rs[1])
    k3.delete(k3.k_partly, ls.value)