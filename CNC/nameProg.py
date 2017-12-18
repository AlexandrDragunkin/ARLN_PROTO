# -*- coding: utf-8 -*-
class NameForProg:
    
    def name_prog_calc(self,machine,eps_d, postfix='',hashsimbol=''):
        '''
                !!!В пути к файлу запрещено использовать пробелы!!!
        
        
        W908_ 848x535x16_15.1F_((@-X))_(G___)-(A)(1)
        
        W908_ 848x535x16_15.2A_((@-X))_(G___)-(F)(1)
        
        1) Материал
        
        2) Размер по X
        
        3) Размер по Y
        
        Размер X и Y зависит о расположения детали в станке
        
        4) Размер по Z
        
        5) Артикул детали
        
        6) Выполнение
        
        (1F) – В первую очередь по стороне F
        
        (2A) – Во вторую очередь по стороне A
        
        7) Примечание о перевороте в оси
        
        8) Кромка
        «L» - Кромка толщиной 0.4 мм.
        
        «S» - Кромка толщиной 0.6 мм.
        
        «G» - Кромка толщиной 1 мм.
        
        «V» - Кромка толщиной 2 мм.
        
        «P» - Обозначает паз.
        
        «!» - Паз снизу со стороны присадки
        
        «^» - Паз сверху с обратной стороны от присадки
        
        «-» - Текстура по размеру X
        
        «^» - Текстура по размеру Y
        
        «A» - Присадка выполняется по стороне (F)
        
        «F» - Присадка выполняется по стороне (A)
        
        9) Текстура
        
        Если текстура по X то «-»
        
        Если текстура по Y то «^»
        
        10) Присадка по стороне
        
        Если присадка по A то указываем (F)
        
        Если присадка по F то указываем (A)
        
        11) Количество деталей
        '''

        def _getlistslot(self):

            def _setslotside(i, _listSlot, e, znak='P'):
                _listSlot[i]=znak
                _listSlot[i] += '!' if e.is_plane else '^'
            
            _listSlot = ['']*4
            if len(self.slots) > 0:
                for e in self.slots:
                    if abs(e.start.x-e.end.x)<eps_d:
                        if e.start.x<self.panelLength/2:
                            _setslotside(3, _listSlot, e) # паз по В находится в правой четверти параллельно В (вертикальный)
                        else:
                            _setslotside(1, _listSlot, e) # паз по С находится в левой четверти параллельно С (вертикальный)
                    elif abs(e.start.y-e.end.y)<eps_d:
                        if e.start.y<self.panelWidth/2:
                            _setslotside(2, _listSlot, e) # паз по D находится в верхней четверти параллельно D (горизонтальный)
                        else:
                            _setslotside(0, _listSlot, e) # паз по E находится в нижней четверти параллельно E (горизонтальный)
                    else: #какойто кривой паз
                        _setslotside(0, _listSlot, e,'Pcr')
            return _listSlot

        def _get_matname(self):
            if self.panel.nomenclature is None:
                nmPan = 'Неопределенный материал'
            elif len(self.panel.nomenclature.article) > 0:
                nmPan = self.panel.nomenclature.article
            else:
                nmPan = self.panel.nomenclature.name
            return nmPan
        
        def _getdfnth(dfnkey, valuet):
            for  e in dfnkey:
                if e < valuet - 0.2:
                    next
                else:
                    break
            return e
        
        def _FilletingContours(self):
            '''Функция формирует обозначение кромок
            «L» - Кромка толщиной 0.4 мм.
            
            «S» - Кромка толщиной 0.6 мм.
            
            «G» - Кромка толщиной 1 мм.
            
            «V» - Кромка толщиной 2 мм.
            '''
            dFN = {0.4: 'L',0.6: 'S',1.: 'G',2.: 'V',}
            dfnkey = sorted(list( dFN.keys()))
            FN = ['_'] * 4
            result = False
            outer=True
            lFun = lambda v1, v2: abs(v1-v2)
            for p in self.millingTech:
                pCuts = 'cuts' in list(p.__dict__.keys())
                if (not outer) and (not pCuts) and ([a.cnc_key for a in self.drills].count(False)>0):
                    continue
                for segment in p.segments:
                    for sw in segment.works:
                        if type(sw) == machine.Filletting:
                            segment.band = sw.nomenclature.values['Thickness']
                            simband = dFN[_getdfnth(dfnkey, segment.band)]
                            if segment.path.id.handle == 1:
                                maxPathX = segment.path.bounding_box.max.x
                                maxPathY = segment.path.bounding_box.max.y
                                minPathX = segment.path.bounding_box.min.x
                                minPathY = segment.path.bounding_box.min.y
                                if (abs(segment.start_pt.x-segment.end_pt.x ) < 0.1 and abs(segment.start_pt.x - maxPathX) < 0.1): # Этот сегмент соответствует  С"
                                    if 'C' not in list(self.bandPunktion.keys()):
                                        #self.bandPunktion['C'] = segment
                                        FN[1] = simband
    
                                if (abs(segment.start_pt.x-segment.end_pt.x ) < 0.1 and abs(segment.start_pt.x - minPathX) < 0.1): # Этот сегмент соответствует  B"
                                    if 'B' not in list(self.bandPunktion.keys()):
                                        #self.bandPunktion['B'] = segment
                                        FN[3] = simband
    
                                if (abs(segment.start_pt.y-segment.end_pt.y ) < 0.1 and abs(segment.start_pt.y - minPathY) < 0.1): # Этот сегмент соответствует  D"
                                    if 'D' not in list(self.bandPunktion.keys()):
                                        #self.bandPunktion['D'] = segment
                                        FN[2] = simband
    
                                if (abs(segment.start_pt.y-segment.end_pt.y ) < 0.1 and abs(segment.start_pt.y - maxPathY) < 0.1): # Этот сегмент соответствует  E"
                                    if 'E' not in list(self.bandPunktion.keys()):
                                        #self.bandPunktion['E'] = segment
                                        FN[0] = simband
            return FN
        
        def _s(nm):
            if len(nm)>0:
                return nm[-1]
            else:
                return ''
            
        toInt = lambda x: str(int(x) if  abs(x-int(x)) < 0.2 else round(x, 1))
        count_common_pos = self.getCountPanels(toInt)
        self.bandPunktion = {}
        _listFill =_FilletingContours(self)
        listSlot = _getlistslot(self)
        pandir = {0: '-', 90: '^', 180: '-', 270: '^',}
        reverspostfix = {'A': 'F', 'F': 'A',}
        index = (_get_matname(self) + '_' # имя материала или артикул
        + toInt(self.panelLength) + 'x' + toInt(self.panelWidth) + 'x' + toInt(self.panelThickness) + '_' # Размер детали
        + str(self.panelNum if self.twins is None else self.twins)
        + '.'+ str(hashsimbol)+postfix+ '_'
        + '(' + self._gside(0, _s, listSlot, _listFill) 
              + self._gside(1, _s, listSlot, _listFill) 
              + self._gside(2, _s, listSlot, _listFill) 
              + self._gside(3, _s, listSlot, _listFill)
        + ')'
        + pandir[self.panel.textureDir]
        + '(' + reverspostfix[postfix]+ ')'
        + '(' + toInt(count_common_pos) + ')')
        
        #'('+self.NumOrder+')_' + str(self.panelNum if self.twins is None else self.twins)+postfix+'_'+hashsimbol
        index = index.replace('*', 'x')
        index = index.replace(' ', '_')
        index = index.replace('/', '_')
        index = index.replace('\\', '_')
        return index

    def _gside(self, i, _s, listSlot, _listFill):
        return _s(listSlot[i])+_listFill[i] +listSlot[i]