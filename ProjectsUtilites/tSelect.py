# -*- coding: utf-8 -*-

#import wingdbstub
import k3
from Utilites_K3 import ptransGcsToPsc

def main():
    params=k3.getpar()
    cordt=params[0] # X Y
    pcrd=params[1] # Контрольное число по координате
    v=(params[2],params[3],params[4]) # Вектор сдвига
    
    objlst=[]

    for i in params[5]:
        objlst.append(i.value)
    n=len(objlst)
    moveadj(objlst, cordt, pcrd, v)
    
def moveadj(objlst, cordt, pcrd, v):
    objlstp=[]
    arr=k3.VarArray(15)
    for obj in objlst:
        k3.initarray(arr,0)
        k3.getobjgeo(obj,arr)
        geoinfo=[a.value for a in arr]
        typobj=k3.getobjtype(obj)
        if typobj==2. :
            # Линия
            if cordt=='X':
                r=(0,3)
            elif cordt=='Y':
                r=(1,4)
            geoinfo[0:6]=ptransGcsToPsc(geoinfo[0:6])
        elif typobj==4.:
            if cordt=='X':
                r=(7,10)
            elif cordt=='Y':
                r=(8,11)
            geoinfo[7:13]=ptransGcsToPsc(geoinfo[7:13])

        if not False in [(pcrd<a) for a in [geoinfo[r[0]],geoinfo[r[1]]]]:
            objlstp.append(obj)
    #print(len(objlstp))
    #print([(pcrd<a) for a in [geoinfo[r[0]],geoinfo[r[1]]]])
    #print([geoinfo[r[0]],geoinfo[r[1]]])
    if len(objlstp)>0:
        k3.moveadjacency(k3.k_partly,objlstp,k3.k_done,v)

if __name__ == '__main__':
    main()

        