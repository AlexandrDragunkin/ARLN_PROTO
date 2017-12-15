# -*- coding: utf-8 -*-
"""
Редактирует указатели деталей на чертеже.
========================================


"""
#import wingdbstub
import k3

from DrawingSupp import (Note, )

#----------------------------------------------------------------------
def revisor(note):
    lrev = sf(note)
    if ((note.info[12]%2 <= 0 and lrev[0] > 0)
        or
        (note.info[12]%2 > 0 and (lrev[0] < 0 or (lrev[0] == 0 and lrev[1] == -1.)))):
        result = True
    else:
        if (note.info[12] % 2 == 1. and lrev[2] == 1.
            or
            note.info[12] % 2 == 0. and lrev[2] == -1.):
            result = True
        else:
            result = False
    return result

def sf(note):
    ava = k3.VarArray(3)
    f = lambda a, b:a - b
    l = list(map(f, note.info[7:10], note.info[4:7]))
    for i, a in enumerate(l):
        ava[i].value = a
    k3.normalv(ava)
    lrev = [round(a.value, 1) for a in ava]
    return lrev
        
def allnoteed():
    """"""
    try:
        nl = k3.fltrtype('Note')
        k3.select(k3.k_partly, k3.k_all, k3.k_done)
        n = k3.sysvar(61)
        note = Note()
        lsobj = []
        info = k3.VarArray(54)
        if n > 0:
            for i in range(int(n)):
                lsobj.append(k3.getselnum(i+1))
            for i in lsobj:
                note.holder = i
                note.getinfo()
                #lr = sf(note)
                #note.info[19] = '(' + str(lr) + ') ' + str(note.info[12])
                #for j in range(len(note.info)):
                    #info[j].value = note.info[j]                
                #k3.putnoteinfo(note.holder, info)
                gi = 0
                while revisor(note) and gi < 3:
                    note.info[12] = abs(note.info[12]-1.0)
                    for j in range(len(note.info)):
                        info[j].value = note.info[j]
                    k3.putnoteinfo(note.holder, info)
                    note.getinfo()
                    gi += 1
    except:
        nl = k3.fltrtype(0)
    finally:
        nl = k3.fltrtype(0)

if __name__ == '__main__':
    allnoteed()