# -*- coding: utf-8 -*-
#import wingdbstub
from DrawingSupp import creator_kromznak

if 'KROMZNAK' in globals().keys():
    del(KROMZNAK)
    
KROMZNAK = creator_kromznak()