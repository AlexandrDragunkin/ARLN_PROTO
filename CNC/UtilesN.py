# -*- coding: cp1251 -*-

''' Здесь собраны полезные функции для станков
'''
import machine
import math
vpi=3.1415926535897932384626433832795         # число Pi
eps_d = 0.001 # допустимое отклонение

degrees = lambda f: f*180/vpi # вместо math преобразует радианы в градусы
iif = lambda cond,if_true,if_false : if_true if cond else if_false

def GetDrillPlane(d):
    '''Вернуть сторону панели, в которой сверлится отверстие

    d - отверстие
    Функция возвращает сторону отверстия: A,B,C,D,E,F Если отверстие сквозное, то сторона А

    Если отверстие расположено под углом к торцу или пласти, функция возвращает X
    '''
    z=d.position.z
    h=d.depth
    alpha=d.alfa
    if abs(alpha - vpi*2/3)<eps_d:
        pass
    if alpha < 0:
        alpha = 2*vpi + alpha
    beta=d.beta
    t=d.panel.thickness
    if (abs(beta)<eps_d or abs(beta-vpi)<eps_d):    # отверстие в пласти
        if (z<=0 and h+abs(z)>=t or z>=t):
            return "A"
        else:
            return "F"
    if (abs(alpha)<eps_d):
        return "B"
    if (abs(alpha-vpi)<eps_d):
        return "C"
    if (abs(alpha-vpi/2)<eps_d):
        return "D"
    if (abs(alpha-vpi*3/2)<eps_d):
        return "E"
    return "X"

def GetGab_bounding_box(obj):
    '''Возвращает габариты по X Y '''
    b = obj.bounding_box
    Xpanel=b.max.x-b.min.x
    Ypanel=b.max.y-b.min.y
    return Xpanel, Ypanel

def GetDrillTrough(d):
    '''Вернуть признак характеристики СКВОЗНОЕ для отверстия

    d - отверстие

    Возвращает True если сквозное
    или False если глухое
    '''
    if (d.depth-d.panel.thickness)>-eps_d and (GetDrillPlane(d) in ['A','F']):
        return True
    else:
        return False

def GetSlotDirection(slot):
    '''Определяем направление пропила
    Возвращает:
    "X" - если пропил вдоль оси X
    "Y" - если пропил вдоль оси Y
    Иначе, если пропил под углом, то "A"
    '''
    if (abs(slot.start.x-slot.end.x)<eps_d):
        return "Y"
    if (abs(slot.start.y-slot.end.y)<eps_d):
        return "X"
    return "A"

def CheckGabs(panel,xmin,xmax,ymin,ymax,zmin,zmax):
    '''Проверка панели на прохождение теста по габаритам.

    panel - панель
    xmin, xmax; ymin,ymax; zmin,zmax - минимальные и максимально-допустимые
    габариты по соответствующим осям

    Функция возвращает True, если она проходит по габаритам и False, если не проходит.
    Если габаритный тест не пройден, то выводится соответствующее сообщение
    '''
    b = panel.bounding_box
    if (b.max.x-b.min.x>xmax or b.max.x-b.min.x<xmin):
        print("Панель #",panel.common_pos," (",panel.name,") не проходит по габаритам X(",b.max.x-b.min.x,")")
        print("Габариты панели: ", b.max.x,b.max.y)
        return False
    if (b.max.y-b.min.y>ymax or b.max.y-b.min.y<ymin):
        print("Панель #",panel.common_pos," (",panel.name,") не проходит по габаритам Y(",b.max.y-b.min.y,")")
        print("Габариты панели: ", b.max.x,b.max.y)
        return False
    if (panel.thickness>zmax or panel.thickness<zmin):
        print("Панель #",panel.common_pos," (",panel.name,") не проходит по габаритам Z(",panel.thickness,")")
        return False
    return True

class Constraints():
    '''Класс, задающий ограничения на те или иные операции'''
    trueposits=("AE","AC","AB","AD","FE","FC","FB","FD")  # Кореж допустимых позиций

    def __init__(self, xmax=3540, xmin=0, ymax=1600, ymin=0, zmax=50, zmin=0.1, drillf=False, slotf=False, slotx=True, sloty=False):

        # Допустимые габариты панелей
        self.xmax_constr=xmax
        self.xmin_constr=xmin
        self.ymax_constr=ymax
        self.ymin_constr=ymin
        self.zmax_constr=zmax
        self.zmin_constr=zmin

        self.drillf_constr=drillf	# Нет низовой сверловки
        self.slotf_constr=slotf		# Нет низовых пропилов
        self.slotx_constr=slotx		# Пропилы по стороне X
        self.sloty_constr=sloty		# Нет пропилов по стороне Y

        # Количества использованных положений
        self.sideAE=0
        self.sideAC=0
        self.sideAB=0
        self.sideAD=0
        self.sideFE=0
        self.sideFC=0
        self.sideFB=0
        self.sideFD=0
        return

    def SetConstraints(self, **kwargs_):
        '''Передача ограничений в класс'''
        keys_kwargs_ = list(kwargs_.keys())
        if  len(keys_kwargs_)> 0:
            for key in list(kwargs_.items()):
                setattr(self, key[0], key[1])


    def AppendPosition(self,poslist,posname):
        '''Метод добавляет позицию posname в список poslist и увеличивает счетчик данной позиции

        poslist - список позиций для данной операции
        posname - имя позиции (AE,AC,AB,AD,FE,FC,FB,FD)

        Функция возвращает количество в списке добавленных позиций'''

        if posname not in Constraints.trueposits:
            return 0
        poslist.append(posname)
        if posname=="AE":
            self.sideAE+=1
            return self.sideAE
        if posname=="AC":
            self.sideAC+=1
            return self.sideAC
        if posname=="AB":
            self.sideAB+=1
            return self.sideAB
        if posname=="AD":
            self.sideAD+=1
            return self.sideAD
        if posname=="FE":
            self.sideFE+=1
            return self.sideFE
        if posname=="FC":
            self.sideFC+=1
            return self.sideFC
        if posname=="FB":
            self.sideFB+=1
            return self.sideFB
        if posname=="AD":
            self.sideFD+=1
            return self.sideFD
        return 0

    def CheckConstraints(self,operation, listDrillDimMashine=['B', 'C', 'D', 'E', 'A', 'F']):
        '''Определение положения панели, при котором данная операция может быть выполнена

        operation - операция
        self - ограничения станка

        Функция возвращает кортеж положений панели вида <Plane><Side>,
        где <Plane> - пласть панели, расположенная вверху (А или F)
        <Side> - сторона панели, расположенная вперед (B, C, D, E)
        '''
        poslist=[]	# Список положений
        if not isinstance(operation,machine.Operation):
            return tuple(poslist)

        # Проверяем габариты по Z. Если не проходит, то ничего не поможет
        panel=operation.panel	# Панель операции
        b=panel.bounding_box
        #ypanel=bbox.max.y-bbox.min.y
        #xpanel=bbox.max.x-bbox.min.x
        xpanel, ypanel = GetGab_bounding_box(panel)
        if (panel.thickness>=self.zmax_constr or panel.thickness<=self.zmin_constr):
            return tuple(poslist)

        # Проверяем отверстия
        xmin=self.xmin_constr
        xmax=self.xmax_constr
        ymin=self.ymin_constr
        ymax=self.ymax_constr
        if isinstance(operation,machine.Drilling):
            position=operation.position
            matr3d=machine.Matrix3d()
            matr3d.translate(machine.Vector2d(-b.min.x,-b.min.y))
            position.transform(matr3d)
            x=operation.position.x
            y=operation.position.y
            side=GetDrillPlane(operation)
            if side=="X":
                return tuple(poslist)
            # print('side=',side)
            # Проверяем пласти панели
            if ((operation.depth>=panel.thickness and side=="F") or side=="A"): # Проверяем сторону А
                if self._CheckPositGabs(xmin,xmax,ymin,ymax,x,y):
                    self.AppendPosition(poslist,"AE")
                if self._CheckPositGabs(xmin,xmax,ymin,ymax,ypanel-y,x):
                    self.AppendPosition(poslist,"AC")
                if self._CheckPositGabs(xmin,xmax,ymin,ymax,y,xpanel-x):
                    self.AppendPosition(poslist,"AB")
                if self._CheckPositGabs(xmin,xmax,ymin,ymax,xpanel-x,ypanel-y):
                    self.AppendPosition(poslist,"AD")

            if ((operation.depth>=panel.thickness and side=="A") or side=="F"):  # Если отверстие сквозное или сторона F
                if self._CheckPositGabs(xmin,xmax,ymin,ymax,xpanel-x,y):
                    self.AppendPosition(poslist,"FE")
                if self._CheckPositGabs(xmin,xmax,ymin,ymax,y,x):
                    self.AppendPosition(poslist,"FC")
                if self._CheckPositGabs(xmin,xmax,ymin,ymax,ypanel-y,xpanel-x):
                    self.AppendPosition(poslist,"FB")
                if self._CheckPositGabs(xmin,xmax,ymin,ymax,x,ypanel-y):
                    self.AppendPosition(poslist,"FD")

            if (side=="B"): # Проверяем сторону B
                if ((y <= (eps_d + ymax)) and
                    ((y +eps_d) >= ymin) and
                    ('B' in listDrillDimMashine)):
                    self.AppendPosition(poslist,"AE")
                if (((ypanel-y)<= (eps_d + xmax)) and
                    ((ypanel-y) +eps_d >= xmin) and
                    ('D' in listDrillDimMashine)):
                    self.AppendPosition(poslist,"AC")
                if ((y <= (eps_d + xmax)) and
                    ((y +eps_d) >= xmin) and
                    (xpanel <= (eps_d + ymax)) and
                    ('E' in listDrillDimMashine)):
                    self.AppendPosition(poslist,"AB")
                if (((ypanel-y) <= (eps_d + ymax)) and
                    (((ypanel-y) +eps_d) >= ymin) and
                    (xpanel <= (eps_d + xmax)) and
                    ('C' in listDrillDimMashine)):
                    self.AppendPosition(poslist,"AD")
                if ((y <= (eps_d + ymax)) and
                    ((y +eps_d) >= ymin) and
                    (xpanel <= (eps_d + xmax)) and
                    ('C' in listDrillDimMashine)):
                    self.AppendPosition(poslist,"FE")
                if ((y <= eps_d + xmax) and
                    (y+eps_d >= xmin) and
                    ('C' in listDrillDimMashine)):
                    self.AppendPosition(poslist,"FD")
                if (((ypanel-y) <= (eps_d + xmax)) and
                    (((ypanel-y) +eps_d) >= xmin) and
                    ((xpanel) <= (eps_d + ymax)) and
                    ('D' in listDrillDimMashine)):
                    self.AppendPosition(poslist,"FB")
                if (((ypanel-y) <= (eps_d + ymax)) and
                    (((ypanel-y) +eps_d) >= ymin) and
                    ('E' in listDrillDimMashine)):
                    self.AppendPosition(poslist,"FC")

            if (side=="C"): # Проверяем сторону C
                if (y<= eps_d + ymax and
                    y+eps_d >= ymin and
                    xpanel<= xmax and
                    ('C' in listDrillDimMashine)):
                    self.AppendPosition(poslist,"AE")
                if (((ypanel-y)<= (eps_d + xmax)) and
                    ((ypanel-y)+eps_d) >= xmin and
                    (xpanel<= (eps_d + ymax)) and
                    ('E' in listDrillDimMashine)):
                    self.AppendPosition(poslist,"AC")
                if ((y<= (eps_d + xmax)) and
                    ((y+eps_d) >= xmin) and
                    ('D' in listDrillDimMashine)):
                    self.AppendPosition(poslist,"AB")
                if (((ypanel-y)<= (eps_d + ymax)) and
                    (((ypanel-y)+eps_d) >= ymin) and
                    ('B' in listDrillDimMashine)):
                    self.AppendPosition(poslist,"AD")
                if ((y<= (eps_d + ymax)) and
                    ((y+eps_d) >= ymin) and
                    ('B' in listDrillDimMashine)):
                    self.AppendPosition(poslist,"FE")
                if ((y<= eps_d + xmax) and
                    (y+eps_d >= xmin) and
                    (xpanel<= eps_d + ymax) and
                    ('E' in listDrillDimMashine)):
                    self.AppendPosition(poslist,"FC")
                if ((ypanel-y<= eps_d + xmax) and
                    (ypanel-y+eps_d >= xmin) and
                    ('D' in listDrillDimMashine)):
                    self.AppendPosition(poslist,"FB")
                if ((ypanel-y<= eps_d + ymax) and
                    (ypanel-y+eps_d >= ymin) and
                    (xpanel<= eps_d + xmax) and
                    ('C' in listDrillDimMashine)):
                    self.AppendPosition(poslist,"FD")

            if (side=="D"): # Проверяем сторону D
                if ((x<= eps_d + xmax) and (x+eps_d >= xmin) and ('D' in listDrillDimMashine)):
                    self.AppendPosition(poslist,"AE")
                if ((x<= eps_d + ymax) and (x+eps_d >= ymin) and (ypanel<= eps_d + xmax) and ('C' in listDrillDimMashine)):
                    self.AppendPosition(poslist,"AC")
                if ((xpanel-x<= eps_d +ymax) and (xpanel-x+eps_d >=ymin) and ('B' in listDrillDimMashine)):
                    self.AppendPosition(poslist,"AB")
                if ((xpanel-x<= eps_d +xmax) and (xpanel-x+eps_d >=xmin) and (ypanel<= eps_d +ymax) and ('E' in listDrillDimMashine)):
                    self.AppendPosition(poslist,"AD")
                if ((xpanel-x<= eps_d +ymax) and (xpanel-x+eps_d >=xmin) and ('D' in listDrillDimMashine)):
                    self.AppendPosition(poslist,"FE")
                if ((x<= eps_d +ymax) and (x+eps_d >=ymin) and ('C' in listDrillDimMashine)):
                    self.AppendPosition(poslist,"FC")
                if ((xpanel-x<= eps_d +ymax) and (xpanel-x+eps_d >=ymin) and (ypanel<= eps_d +xmax) and ('B' in listDrillDimMashine)):
                    self.AppendPosition(poslist,"FB")
                if ((x<= eps_d +xmax) and (x+eps_d >=xmin) and (ypanel<= eps_d +ymax) and ('E' in listDrillDimMashine)):
                    self.AppendPosition(poslist,"FD")

            if (side=="E"): # Проверяем сторону E
                if ((x<= eps_d +xmax) and (x+eps_d >=xmin) and (ypanel<= eps_d +ymax) and ('E' in listDrillDimMashine)):
                    self.AppendPosition(poslist,"AE")
                if ((x<= eps_d +ymax) and (x+eps_d >=ymin) and ('B' in listDrillDimMashine)):
                    self.AppendPosition(poslist,"AC")
                if ((xpanel-x<= eps_d +ymax) and (xpanel-x+eps_d >=ymin) and (ypanel<= eps_d +xmax) and ('C' in listDrillDimMashine)):
                    self.AppendPosition(poslist,"AB")
                if ((xpanel-x<= eps_d +xmax) and (xpanel-x+eps_d >=xmin) and ('D' in listDrillDimMashine)):
                    self.AppendPosition(poslist,"AD")
                if ((xpanel-x<= eps_d +ymax) and (xpanel-x+eps_d >=xmin) and (ypanel<= eps_d +ymax) and ('E' in listDrillDimMashine)):
                    self.AppendPosition(poslist,"FE")
                if ((x<= eps_d +ymax) and (x+eps_d >=ymin) and (ypanel<= eps_d +xmax) and ('C' in listDrillDimMashine)):
                    self.AppendPosition(poslist,"FC")
                if ((xpanel-x<= eps_d +ymax) and (xpanel-x+eps_d >=ymin) and ('B' in listDrillDimMashine)):
                    self.AppendPosition(poslist,"FB")
                if ((x<= eps_d +xmax) and (x+eps_d >=xmin) and ('D' in listDrillDimMashine)):
                    self.AppendPosition(poslist,"FD")

        posit=tuple(poslist)
        return posit

    def _CheckPositGabs(self,xmin,xmax,ymin,ymax,x,y):
        '''Проверка на попадание координат (x,y) в прямоугольник (xmin,ymin) - (xmax,ymax)'''
        if x<xmin or x>xmax:
            return False
        if y<ymin or y>ymax:
            return False
        return True

    def GetFirst(self):
        '''Функция возвращает масимальное положение панели (из оставшихся)'''

        # Если ни одна обработка недоступна
        if (max(self.sideAE,self.sideAC,self.sideAB,self.sideAD,self.sideFE,self.sideFC,self.sideFB,self.sideFD)==0):
            return "XX"
        if (max(self.sideAE,self.sideAC,self.sideAB,self.sideAD,self.sideFE,self.sideFC,self.sideFB,self.sideFD)==self.sideAE):
            self.sideAE=0
            return "AE"
        if (max(self.sideAE,self.sideAC,self.sideAB,self.sideAD,self.sideFE,self.sideFC,self.sideFB,self.sideFD)==self.sideAC):
            self.sideAC=0
            return "AC"
        if (max(self.sideAE,self.sideAC,self.sideAB,self.sideAD,self.sideFE,self.sideFC,self.sideFB,self.sideFD)==self.sideAB):
            self.sideAB=0
            return "AB"
        if (max(self.sideAE,self.sideAC,self.sideAB,self.sideAD,self.sideFE,self.sideFC,self.sideFB,self.sideFD)==self.sideAD):
            self.sideAD=0
            return "AD"
        if (max(self.sideAE,self.sideAC,self.sideAB,self.sideAD,self.sideFE,self.sideFC,self.sideFB,self.sideFD)==self.sideFE):
            self.sideFE=0
            return "FE"
        if (max(self.sideAE,self.sideAC,self.sideAB,self.sideAD,self.sideFE,self.sideFC,self.sideFB,self.sideFD)==self.sideFC):
            self.sideFC=0
            return "FC"
        if (max(self.sideAE,self.sideAC,self.sideAB,self.sideAD,self.sideFE,self.sideFC,self.sideFB,self.sideFD)==self.sideFB):
            self.sideFB=0
            return "FB"
        if (max(self.sideAE,self.sideAC,self.sideAB,self.sideAD,self.sideFE,self.sideFC,self.sideFB,self.sideFD)==self.sideFD):
            self.sideAE=0
            return "FD"
        return "XX"

    def TransformToSide(self,panel,posit,toback=False):
        '''Функция устанавливает положение панели panel в соответствие с заданной сторонй posit.
        Если toback = True, то положение возвращается из posit в стандартное (АЕ)

        Если передено корректное положение, то функция возвращает True. Иначе - False
        '''
        b = panel.bounding_box
        ypanel=b.max.x-b.min.x
        ypanel=b.max.y-b.min.y
        matr=machine.Matrix3d()
        # Добавляем в матрицу преобразования в зависимости от положенияя
        if posit=="AE":
            pass  # Это нормальное положение панели
        elif posit=="AC":
            matr = machine.Matrix3d.rotate(vpi/2)
            matr *= machine.Matrix3d.translate(machine.Vector2d(-ypanel,0))
        elif posit=="AD":
            matr = machine.Matrix3d.rotate(vpi)
            matr *= machine.Matrix3d.translate(machine.Vector2d(-xpanel,-ypanel))
        elif posit=="AB":
            matr = machine.Matrix3d.rotate(-vpi/2)
            matr *= machine.Matrix3d.translate(machine.Vector2d(0,-xpanel))
        elif posit=="FE":
            matr = machine.Matrix3d.overturn_y(0,panel.thickness/2)
            matr *= machine.Matrix3d.translate(machine.Vector2d(-xpanel,0))
        elif posit=="FC":
            matr = machine.Matrix3d.overturn_y(0,panel.thickness/2)
            matr *= machine.Matrix3d.rotate(vpi/2)
        elif posit=="FD":
            matr = machine.Matrix3d.overturn_y(0,panel.thickness/2)
            matr *= machine.Matrix3d.rotate(vpi)
            matr *= machine.Matrix3d.translate(machine.Vector2d(0,-ypanel))
        elif posit=="FB":
            matr = machine.Matrix3d.overturn_y(0,panel.thickness/2)
            matr *= machine.Matrix3d.rotate(-vpi/2)
            matr *= machine.Matrix3d.translate(machine.Vector2d(-ypanel,-xpanel))
        else:
            return False
        # Если нужно восстановить положение, то инвертируем матрицу
        if toback:
            matr.inverse()
        panel.Transform(matr)
        return True




  # Написать функцию поворота панели в соответствии с положением.

  # Написать функции проверки положения для пропилов
#----------------------------------------------------------------------------------

# Хитрость для смены мест начальнй и конечной точек сегмента
# У сегмента контура появляется свойство r типа MirrSegment
# Координаты начальной и конечной точки типа machine.Point2d()
class MirrSegment():
    def __init__(self):
        self.start_pt = machine.Point2d()
        self.end_pt = machine.Point2d()

def addAtrOvertToPath(path):
    path.overt = False

def addSegmentMirrSegment(s):
    '''Cоздает новое свойство r    у сегмента контура, которое можно менять в отличии от свойств start_pt end_pt'''
    s.r = MirrSegment()
    s.r.start_pt.x, s.r.start_pt.y, s.r.end_pt.x, s.r.end_pt.y    =\
    s.start_pt.x , s.start_pt.y, s.end_pt.x ,    s.end_pt.y

def SegmentReverse(segment, overt):
    '''Меняет местами координаты конечной и начальной точки сегмента.
    segment - сегмент контура
    '''
    addSegmentMirrSegment(segment) # Cоздает новое свойство r    у сегмента контура
    if overt:    # Если контур подвергся обработке Overturn
        segment.r.start_pt.x, segment.r.start_pt.y, segment.r.end_pt.x,        segment.r.end_pt.y    = \
        segment.end_pt.x ,    segment.end_pt.y ,    segment.start_pt.x , segment.start_pt.y

def findMinPointInSegments(list_segments):
        '''Находит минимальную точку в списке сегментов
        list_segments = self.millingTech[index_path].segments
        '''
        i=0
        pos=[]
        dcx=99999999999

        for s in list_segments:
                #print round(s.start_pt.x,3)," ",round(s.start_pt.y,3)," ",round(s.end_pt.x,3)," ",round(s.end_pt.y,3)
                if s.start_pt.x<=dcx:
                        if s.start_pt.x==dcx:
                                pos=pos[len(pos)-1:]
                        pos.append(i)
                        #print i
                        dcx=s.start_pt.x
                i+=1
        #print pos
        if len(pos)>0:
                dcy=99999999999
                for i in pos:
                        s = list_segments[i]
                        if s.start_pt.y<dcy:
                                ps=i
        else:
                ps = pos[0]
        return ps

#--------------------------------------------------------

def findMaxPointInSegments(list_segments):
        '''Находит максимальную точку в списке сегментов
        index_path=0
        list_segments = self.millingTech[index_path].segments
        ps = findMinPointInSegments(list_segments)
        print ps
        print '------------------'
        ps = findMaxPointInSegments(list_segments)
        print ps
        print '------------------'
        '''
        i=0
        pos=[]
        dcx=-99999999999

        for s in list_segments:
            #print round(s.start_pt.x,3)," ",round(s.start_pt.y,3)," ",round(s.end_pt.x,3)," ",round(s.end_pt.y,3)
            if s.start_pt.x>=dcx:
                    if s.start_pt.x==dcx:
                            pos=pos[len(pos)-1:]
                    pos.append(i)
                    #print i
                    dcx=s.start_pt.x
            i+=1
        #print pos
        if len(pos)>0:
            dcy=-99999999999
            for i in pos:
                    s = list_segments[i]
                    if s.start_pt.y>dcy:
                            ps=i
        else:
            ps = pos[0]
        return ps
#---------------------------------------------------------

def findMaxLongSegment(list_segments):
    '''Возвращает индекс максимального по длинне сегмента'''
    i=0
    clg=0
    pos=[]
    lensg=0.0
    for s in list_segments:
        leng_s=lengSegment(s)
        if leng_s>lensg:
            clg=i
            lensg=leng_s
        i+=1
    return clg
#---------------------------------------------------------

def checkMaxLongSegments(segments):
    '''Изменяет последовательность прохода по сегментам
    для внутреннего ищем максимальный по длине делим его пополам и начинаем с этой точки'''
    if type(segments[0]) == machine.Circle:
        path_H = segments[0].path
        segments = segments[0].Divide(0.5)
        for s in segments:
            s.path_H = path_H
        ps=0
    else:
        ps=findMaxLongSegment(segments)
        path_H = segments[ps].path
        sg=segments[ps].Divide(0.5)
        for s in sg:
            s.path_H = path_H
        ts=segments[:ps]
        ts.extend(sg)
        ts.extend(segments[ps+1:])
        segments=ts
    return ps+1,segments
#--------------------------------------------------------

def angleGet( v1, v2):
    '''Возвращает угол между двумя векторами
        v1 =con.tangent(1)
        v2 =con.tangent(0)
        res=angleGet(v1, v2)
    '''
    cc = round((v1%v2)/(v1.length()*v2.length()),3)
    cs = round(degrees(math.acos(cc)),2)
    return cs
#--------------------------------------------------------

def lengSegment(con):
    '''Возвращает длину сегмента или None'''
    res=None
    if type(con)==machine.Arc:
        v1 =con.tangent(1)
        v2 =con.tangent(0)
        res=vpi*con.radius*(angleGet(v1, v2))/180
    elif type(con)==machine.Line:
        vx=con.end_pt.x-con.start_pt.x
        vy=con.end_pt.y-con.start_pt.y
        vt=machine.Vector2d(vx,vy)
        res=vt.length()

    return res
#--------------------------------------------------------

def checkSegments(segments,outer):
    '''Изменяет последовательность прохода по сегментам
    для внешнего контура начиная с минимальной точки по XY
    для внутреннего ищем максимальный по длинне делим его пополам и начинаем с этой точки'''
    list_segments = segments
    path_H = segments[0].path_H if segments[0].path is None else segments[0].path

    if outer:
        ps = findMinPointInSegments(list_segments)
    else:
        ps, list_segments = checkMaxLongSegments(list_segments)
    segments=list_segments[ps:]
    segments.extend(list_segments[:ps])
    for s in segments:
        s.path_H = path_H
    return segments
#-------------------------------------------------------------------------------
def is_permissible(val, t):
    '''Ищет val в списке или ключах словаря t
    возвращае True или False'''
    if type(t)==list:
        try:
            i_el=t.index(val)
        except:
            return False
        return True
    elif type(t)==dict:
        return val in t
#-------------------------------------------------------------------------------
def intersect(a, b):
    '''Возвращает результат пересечения двух списков'''
    return list(set(a) & set(b))

#-------------------------------------------------------------------------------
def flatten(x):
    """flatten(sequence) -> list

    Возвращает один, плоский список, который содержит все элементы,
    которые передаются из последовательности и рекурсивно содержит
    все  субпоследовательности
    (iterables).

    Examples:
    >>> [1, 2, [3,4], (5,6)]
    [1, 2, [3, 4], (5, 6)]
    >>> flatten([[[1,2,3], (42,None)], [4,5], [6], 7, MyVector(8,9,10)])
    [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]"""

    result = []
    for el in x:
        #if isinstance(el, (list, tuple)):
        if hasattr(el, "__iter__") and not isinstance(el, str):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result
#-------------------------------------------------------------------------------
