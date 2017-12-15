# -*- coding: utf-8 -*-
class NameForProg:
    
    def name_prog_calc(self,machine,eps_d, postfix='',hashsimbol=''):
        '''
        !!!В пути к файлу запрещено использовать пробелы!!!
        
        
        Конкретный пример

        19-МДФ_596x176x19_81_@FLU^(2).bpp
        19-МДФ_596x176x19_81_@ALD^(2).bpp
        
        Описание: Детали и наименования при виденного примера.
         Деталь выполнена из (19-МДФ)
        1 размер 176
        2 размер 596
        (596x176x19) указывает расположение детали по осям X, Y, Z.
        (81) артикул детали
        (@) признак переворота детали.
        (FLU) F - сторона обработки обратная.
                 LU - Левый верхний угол.
        (ALD) A - сторона обработки лицевая со стороны бирки.
                 LD - Левый нижний угол.
        (^) Текстура расположена по оси Y
        (-) Текстура расположена по оси X
        ((2)) - количество деталей
        
        
        Обозначение сторон:
        Лицевая со стороны бирки - A
        Обратная - F
        Обозначение углов:
        LU - левый верхний угол.
        LD - левый нижний угол.
        RU - правый верхний угол.
        RD - правый нижний угол.

        '''
        
        
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
        

        
        def _s(nm):
            if len(nm)>0:
                return nm[-1]
            else:
                return ''
            
        toInt = lambda x: str(int(x) if  abs(x-int(x)) < 0.2 else round(x, 1))
        count_common_pos = self.getCountPanels(toInt)

        pandir = {0: '-', 90: '^', 180: '-', 270: '^',}
        reverspostfix = {'A': 'F', 'F': 'A',}
        apoint = {'A':{0: 'RU', 90: 'RD', 180: 'LD', 270: 'LU', 360: 'RU'}, 'F':{0: 'LU', 90: 'LD', 180: 'RD', 270: 'RU', 360: 'LU'}}
        marker = '_@' if str(hashsimbol) > '1' else '_'
        marker += (reverspostfix[postfix] + apoint[postfix][self.aposition])
        index = (_get_matname(self) + '_' # имя материала или артикул
        + toInt(self.panelLength) + 'x' + toInt(self.panelWidth) + 'x' + toInt(self.panelThickness) + '_' # Размер детали
        + str(self.panelNum if self.twins is None else self.twins)
        + marker
        #+ '(' + reverspostfix[postfix]+ ')'
        + pandir[self.panel.textureDir]
        + '(' + toInt(count_common_pos) + ')')
        index = index.replace('*', 'x')
        index = index.replace(' ', '_')
        index = index.replace('/', '_')
        index = index.replace('\\', '_')
        return index

