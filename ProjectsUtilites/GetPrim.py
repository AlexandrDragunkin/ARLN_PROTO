import k3

def main():
    dct = {}
    if On_B==2:
        dct['{} по {}-{} шт'.format(NmFix_B ,CalcVar(Fz_B), int(NKB))] = ['B']
    elif On_B==1:
        dct['{} {} шт'.format(NmFix_B , int(NKB))] = ['B']
    
    if On_C==2:
        obj = '{} по {}-{} шт'.format(NmFix_C, CalcVar(Fz_C), int(NKC))
        if obj not in dct:
            dct[obj] = ['C']
        else:
            dct[obj].append('C')
    elif On_C==1:
        obj = '{} {} шт'.format(NmFix_C, int(NKC))
        if obj not in dct:
            dct[obj] = ['C']
        else:
            dct[obj].append('C')
    
    if On_D==2:
        obj = '{} по {}-{} шт'.format(NmFix_D, CalcVar(Fz_D), int(NKD))
        if obj not in dct:
            dct[obj] = ['D']
        else:
            dct[obj].append('D')
    elif On_D==1:
        obj = '{} {} шт'.format(NmFix_D, int(NKD))
        if obj not in dct:
            dct[obj] = ['D']
        else:
            dct[obj].append('D')
    
    if On_E==2:
        obj = '{} по {}-{} шт'.format(NmFix_E, CalcVar(Fz_E), int(NKE))
        if obj not in dct:
            dct[obj] = ['E']
        else:
            dct[obj].append('E')
    elif On_E==1:   
        obj = '{} {} шт'.format(NmFix_E, int(NKE))
        if obj not in dct:
            dct[obj] = ['E']
        else:
            dct[obj].append('E')
    
    # print(dct)
    
    strVar = ", ".join(["{} ({})".format(i, ",".join(j)) for i, j in dct.items()])

    params[17].value = strVar
    
def CalcVar(FZ):
    # FZ = 0 - пласть A
    # FZ = 1 - пласть F
    # Front = 0 - лицо по A
    
    res = (FZ > 0, Front == 0)
    Side = 'Т' if res==(True, True) or res==(False, False) else 'Л'
    
    return Side
    
if __name__ == '__main__':
    
    params = k3.getpar()

    Fz_B = params[0] # Пласть крепежа 0 - пласть A, 1 - F
    NKB = params[1] # Количество крепежа на торце
    Fz_C = params[2]
    NKC = params[3]
    Fz_D = params[4]
    NKD = params[5]
    Fz_E = params[6]
    NKE = params[7]
    On_B = params[8] # Наличие крепежа на торце
    On_C = params[9]
    On_D = params[10]
    On_E = params[11]
    NmFix_B = params[12] # Сокращение для крепежа из массива аббревиатур
    NmFix_C = params[13]
    NmFix_D = params[14]
    NmFix_E = params[15]
    Front = params[16]  # Лицо по пласти A = 0, F = 1
    # NameFix = params[17].value

    main()
