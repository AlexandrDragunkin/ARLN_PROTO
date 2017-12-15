# -*- coding: utf-8 -*-

if __name__ == '__main__':
    
    import k3
    
    # Прифуговка
    
    # | 2 | - | => -2
    # | 2 | 2 | => -3
    # |.4 | - | => 0
    # |.4 |.4 | => 0
    # | 2 |.4 | => -2
    # | 1 | - | => 0
    # | 1 | 1 | => -1
    # | 1 | 2 | => -2
    # | 1 |.4 | => 0
    
    pars2 = k3.getpar()
    # print(pars)
    KE = pars2[0].value
    KD = pars2[1].value
    KC = pars2[2].value
    KB = pars2[3].value
    cutLen = pars2[4].value
    cutWdh = pars2[5].value
    kromLen = (KC>0, KB>0)
    kromWdh = (KE>0, KD>0)
    # print(KB+KC)
    # print(KE+KD)
    if (kromLen == (True,False) or kromLen == (False,True)) and (KB+KC)>=2:
        cutLen = 2
        
    if (kromWdh == (True,False) or kromWdh == (False,True)) and (KE+KD)>=2:
        cutWdh = 2

    if kromLen == (True,True):
        if (KB+KC)==2.:
            cutLen = 1
        if (KB+KC) in (2.4, 3.):
            cutLen = 2
        if (KB+KC)==4:
            cutLen = 3
            
    if kromWdh == (True,True):
        if (KE+KD)==2.:
            cutWdh = 1
        if (KE+KD) in (2.4, 3.):
            cutWdh = 2
        if (KE+KD)==4.:
            cutWdh = 3
                        
    pars2[4].value = cutLen
    pars2[5].value = cutWdh