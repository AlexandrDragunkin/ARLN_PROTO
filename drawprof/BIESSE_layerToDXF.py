# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        BIESSE_layerToDXF
# Purpose:     Назначить имя слоя при экспорте DXF
#
# Author:      Aleksandr Dragunkin
#
# Created:     31.10.2012-2015
# изменения для версии 7.3 поддержка Python3
# Copyright:   (c) GEOS 2012-13
# Licence:     FREE
#-------------------------------------------------------------------------------
#import wingdbstub
from Utilites_K3 import Layer
#-----------------------------
class layerToDXF(Layer):
    '''CNC BIESSE'''

    def layerPars(self, Zp):
        replPoint = lambda s: s.replace('.', 'K')
        if Zp != int(Zp):
            s_Zp = str(Zp)
            s_Zp = replPoint(s_Zp)
        else:
            s_Zp = str(int(Zp))
        return s_Zp

    def set_name_layer_drill(self):
        name_layers = {'AF': 'VERTICA', 'T': 'LATO', 'A': 'VERTICA', 'F': 'VERTICA', 'B': 'LATO3', 'C': 'LATO1',
                       'D': 'LATO4', 'E': 'LATO2'}
        if self.Side in ['B', 'C', 'D', 'E']:
            Zp = Panel.panelThickness - self.Zc
            s_Zp = self.layerPars(Zp)
            nm = name_layers[self.Side] + s_Zp
        elif self.Side in ['A', 'F']:
            Zp = self.Hohe
            s_Zp = self.layerPars(Zp)
            nm = name_layers[self.Side] + s_Zp
        elif self.Side in ['AF']:
            nm = ''
        else:
            nm = ''
        return nm

    def set_name_layer_panel(self):
        nm = 'PANNELLO' + self.layerPars(Panel.panelThickness)
        return nm