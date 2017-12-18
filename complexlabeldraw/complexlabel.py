# -*- coding: utf-8 -*-
"""
Формирует указатели деталей на чертеже.
========================================


"""
# try:
#     import pydevd
#     pydevd.settrace('localhost', port=51764, stdoutToServer=True, stderrToServer=True)
# except:
#     pass
# import wingdbstub
import k3

from DrawingSupp import (Dimension,
                         GetListAllPanel,
                         Note,
                         obj_k3_gab3,
                         GetListAllPanel,
                         delZero)
import cProfile
import time
import datetime


class Raster:
    """
    Анализирует видимость твердого тела или пленки
    """

    def __init__(self, solidobj=None):
        self.handle = solidobj  # Указатель на объект К3
        self.raster_procent = None
        self.num_pixeles_in_zone_visible = None
        self.lpoint = []
        self.keyzoom = False
        self.zoom = False
        self.visible = False
        if solidobj is not None:
            self.get_raster_domain()

    def fo_zoom(self):
        if self.keyzoom:
            if not self.zoom:
                k3.zoom(k3.k_byobject, self.handle)
                self.zoom = True
            else:
                k3.zoom(k3.k_previous)
                self.zoom = False

    def get_raster_domain(self):
        try:
            a = k3.VarArray(10)
            n = k3.sysvar(60)
            delta_raster_k = 300
            result = False
            nnn = k3.getsnap()
            for i in range(2):
                a[0].value = (i + 1) * delta_raster_k  # Размер растра
                a[1].value = self.handle  # Объект
                a[2].value = 5  # глубина расчета

                k3.setucs(k3.k_vcs)
                self.raster_procent = k3.rasterdomain(1, a) # Процент видимости
                # print('Процент видимости =', self.raster_procent)
                if self.raster_procent > 0:
                    a[0].value = 2  #
                    self.num_pixeles_in_zone_visible = k3.rasterdomain(3, a)  # узнать число пикселей внутри зоны видимости с расстоянием от границы больше равному  a[0]
                    # print('число пикселей внутри зоны видимости =', self.num_pixeles_in_zone_visible)
                    if self.num_pixeles_in_zone_visible > 0:
                        for j in range(10):
                            a[0].value = 10-j  # расстояние от границы в пикселях
                            # print('расстояние от границы в пикселях  ',a[0].value)
                            a[1].value = 0  # 1-В гск 0-вск
                            a[2].value = 1  # 1 - только граница 0 - все
                            lpoint = []
                            while k3.rasterdomain(4, a) > 0:  # Получить очередную видимую точку
                                lpoint.append(Based_point_label(a[3].value, a[4].value, a[5].value))
                            if len(lpoint) > 3:
                                s = [i for i in range(0, len(lpoint), int(len(lpoint)/3))]
                                for i in s:
                                    self.lpoint.append(lpoint[i])
                            else:
                                self.lpoint = lpoint
                            if len(lpoint)>0:
                                self.visible = True
                                break
                        break
                    else:
                        pass
                    nv = k3.rasterdomain(2, a)
                    # print("---- Попытка ------- ", i)
                    self.keyzoom = True
                    self.fo_zoom()

                else:
                    if self.keyzoom:
                        print('Панель невидна, выходим.')
                        self.visible = False
                        break
                    else:
                        self.keyzoom = True
                        self.fo_zoom()
                nv = k3.rasterdomain(2, a)  #
            self.fo_zoom()
            nnn = k3.resnap()

        except:
            self.fo_zoom()
            nnn = k3.resnap()
            nv = k3.rasterdomain(2, a)  #


class Scene:
    """
    Класс сцена.
    """

    def __init__(self, fun=None):
        # Определяем список lstobj всех объектов сцены верхнего уровня
        self.get_obj_scene()
        # Определяем габарит сцены 
        self.get_gab_sene()
        # переопределяем список lstobj объектов по функци выбора
        if fun is not None:
            self.get_obj_scene(fun)

    def get_obj_scene(self, fun=None):
        """Заполняет список объектов сцены.
        Возврашает Истина если объекты есть и список составлен и Ложь если объектов сцены нет
        fun - функция возвращаеющая список нужных объектов
        """
        n = 0
        self.l_note=[]
        if fun is None:
            k3.select(k3.k_all)
            n = k3.sysvar(61)
            if n > 0:
                self.lstobj = []
                for i in range(int(n)):
                    self.lstobj.append(k3.getselnum(i + 1))
        else:
            self.lstobj = [a for a in fun()]
            self.nnote = len(self.lstobj)
            n = len(self.lstobj)
        if n > 0:
            return True
        else:
            return False

    def get_gab_sene(self):
        """
        Определяет габарит сцены в ВСК
        """
        if len(self.lstobj) > 0:
            nnn = k3.getsnap()
            k3.setucs(k3.k_vcs)
            self.gab_scene_vsc = obj_k3_gab3(self.lstobj)
            nnn = k3.resnap()

    def draw_rectangle_scene(self, k=0.2):
        """
        Область вокруг сцены
        """
        nnn = k3.getsnap()
        k3.setucs(k3.k_vcs)
        gabs = self.gab_scene_vsc
        t = min([abs(gabs[0]) * k, abs(gabs[1]) * k, abs(gabs[3]) * k, abs(gabs[4]) * k])
        # rect = k3.rectangle(k3.k_3points, gabs[0] - t, gabs[1] - t, max([gabs[2], gabs[5]]) + t,
        #                     gabs[3] + t, gabs[1] - t, max([gabs[2], gabs[5]]) + t,
        #                     gabs[0] - t, gabs[4] + t, max([gabs[2], gabs[5]]) + t
        #                     )
        length_x = 2 * (abs(gabs[0] - gabs[3]) + 2 * t)
        length_y = 2 * (abs(gabs[4] - gabs[1]) + 2 * t)

        tnote = Note()
        ht = tnote.getrealsizetext()
        wt = 2 * ht
        npoint_y = int(int(length_y / ht) / 2)
        npoint_x = int(int(length_x / wt) / 2)
        dy = length_y / 2 / npoint_y
        dx = length_x / 2 / npoint_x
        self.based_label=Based_label_rectangle()
        for i in range(npoint_y+1):
            self.based_label.childobjects.append(Based_point_label(gabs[0] - t, (gabs[1] - t) + i * dy, max([gabs[2], gabs[5]]) + t))
        for i in range(npoint_y+1):
            self.based_label.childobjects.append(Based_point_label(gabs[3] + t, (gabs[1] - t) + i * dy, max([gabs[2], gabs[5]]) + t))
        for i in range(1,npoint_x,):
            self.based_label.childobjects.append(Based_point_label(gabs[0] - t + i * dx, (gabs[1] - t), max([gabs[2], gabs[5]]) + t))
        for i in range(1,npoint_x,):
            self.based_label.childobjects.append(Based_point_label(gabs[0] - t + i * dx, (gabs[4] + t), max([gabs[2], gabs[5]]) + t))
        nnn = k3.resnap()


class Object_scene:
    """Объект сцены"""

    def __init__(self, obj=None, l_commonpos=[]):
        self.handle = obj
        self.l_commonpos=l_commonpos
        if obj is not None:
            self.commonpos = k3.getattr(obj, "UDetNumber", -1)
            self.unicid =  k3.getattr(obj, "UnitPos", 0)
            self.ft =  k3.getattr(obj, "FufrnType", '')
            self.karkasnumb = k3.getattr(obj,"KarkasNumb",-1)
            if self.commonpos > 0:
                if self.commonpos in l_commonpos:
                    # print("Панель уже указана ", self.commonpos)
                    self.raster = Raster()
                    self.raster.raster_procent = -10
                else:
                    
                    self.raster = Raster(self.handle)
                    print("Панель ", self.commonpos)
                    if self.raster.raster_procent == -1 or self.raster.num_pixeles_in_zone_visible < 1:
                        pass
                    else:
                        l_commonpos.append(self.commonpos)

def profile(func):
    """Decorator for run function profile"""

    def wrapper(*args, **kwargs):
        profile_filename = func.__name__ + '.prof'
        profiler = cProfile.Profile()
        result = profiler.runcall(func, *args, **kwargs)
        profiler.dump_stats(profile_filename)
        return result
    return wrapper


class Based_label_rectangle:
    def __init__(self):
        self.gabpoints = (0, 0, 0, 0, 0, 0)  # Габарит из 6 кооринат
        self.childobjects = []  # Список объектов внутри прямоугольника


class Based_point_label:
    def __init__(self, x, y, z):
        self.basedpoint = (x, y, z,)  # Точка положения полочки

    def draw(self):
        return k3.point(self.basedpoint)


# запуск построителя графа gprof2dot -f pstats start_scene_raster.prof | dot -Tpng -o start_ppi.png
# Вот это вариант что сверху не работает по причине кодировки консоли cp1251
# я сделал иначе gprof2dot -o s.res -f pstats start_scene_raster.prof выгрузил в файл s.res
# затем dot -Tpng -Tps s.res -o start_scene_raster.png и получил картинку вызовов
#
# Кроме того можем получить статистику
# >>> import pstats
# >>> p = pstats.Stats('d:\PKM73_DV\Bin\start_scene_raster.prof')
# >>> p.sort_stats('calls').print_stats()
# @profile
def start_scene_raster():
    start_time = time.time()
    s = Scene(fun=GetListAllPanel)
    s.draw_rectangle_scene()
    print('Число панелей = ', len(s.lstobj))
    l_commonpos=[]
    list_not_vis = []
    list_vis = []
    objects_scene = [Object_scene(obj,l_commonpos) for obj in s.lstobj]
    for obj in objects_scene:
        if ((not obj.raster.visible)
                and not (obj.commonpos in list_vis)
                and not (obj.commonpos in list_not_vis)):
            list_not_vis.append(obj.commonpos)
        elif obj.raster.visible:
            if not (obj.commonpos in list_vis):
                list_vis.append(obj.commonpos)
                if obj.commonpos in list_not_vis:
                    list_not_vis.remove(obj.commonpos)
    s.list_not_vis=list_not_vis
    s.list_vis=list_vis
    # Сначала надо взять те у которых меньше всего точек
    # Сортируем по возрастанию obj.raster_procent при условии , что в obj.lpoint есть хотя бы одна точка
    key_fun = lambda v: len(v.raster.lpoint) if v.raster.raster_procent>0 else -1
    sqr_fun = lambda v1, v2: (v1 - v2) ** 2
    sqrt_fun = lambda a, b: k3.sqrt(sum(map(sqr_fun, a, b)))
    objects_scene.sort(key=key_fun)

    while objects_scene[0].raster.raster_procent<0:
            objects_scene.pop(0)
    for obj in objects_scene:
        # Ищем положение точек
        # Найти ближайшую
        psn = None
        for iv, v in enumerate(obj.raster.lpoint):
            for ipb, pb in enumerate(s.based_label.childobjects):
                #ps=k3.distance(v.basedpoint, pb.basedpoint)
                ps = sqrt_fun(v.basedpoint, pb.basedpoint)
                if psn is None:
                    psn = ps
                elif ps < psn:
                    obj.ds = (ps, iv, ipb, s.based_label.childobjects[ipb])
                    psn = ps
        try:
            if len(obj.ds) > 0:
                s.based_label.childobjects.pop(obj.ds[2])
                # print(obj.ds, objects_scene.index(obj), len(objects_scene))
        except:
            pass
    end_time = time.time() - start_time
    print(str(datetime.timedelta(seconds=end_time)))
    k3.getsnap()
    ffun = lambda v1, v2: v2 - v1
    k3.setucs(k3.k_vcs)
    for obj in objects_scene:
        try:
            if obj.raster.visible:
                tp = [list(obj.raster.lpoint[obj.ds[1]].basedpoint), list(obj.ds[3].basedpoint)]
                tp[0][2] = max(tp[0][2], tp[1][2])
                tp[1][2] = tp[0][2]
                dd = list(map(ffun, tp[0], tp[1]))
                dx_2 = -1 if dd[0] < 0 else + 1
                #k3.line(tp)
                #n =  Note(Text1=str(obj.commonpos))
                note = Note(normal=(0, 0, 1), Text1= str(delZero(round(obj.commonpos, 1))), Text2="",
                                        point1=tp[0], relativ1=dd, relativ2=(dx_2, 0, 0))
                note.flip=False
                note.draw()
                nmac='\\complexlabeldraw\\complexlabel.py'
                CurrVi = int(k3.sysvar(51))
                CV = "VidDim_"+str(CurrVi)
                k3.attrobj( k3.k_attach,  "AutoPlace",  k3.k_done, note.holder, 1)
                k3.attrobj( k3.k_attach,  "VidDimPlace",  k3.k_done, note.holder, CurrVi)
                if obj.karkasnumb!=-1 :
                    k3.attrobj( k3.k_attach, "KarkasNumb", k3.k_done, note.holder, obj.karkasnumb)
                k3.chprop( k3.k_layer, note.holder,k3.k_done, CV)
                k3.attrobj( k3.k_attach, "NumType", "NumHolder", "NmMacNums", "FT_Holder", k3.k_done, note.holder, 1, obj.unicid, nmac, obj.ft)
                s.l_note.append(note)
        except:
            print("Ошибка данных:", sys.exc_info()[0])
    k3.resnap()
    return s

# @profile
def start_object_raster():
    obj = k3.Var()
    k3.objident(k3.k_interact, obj)
    start_time = time.time()
    p = Raster(obj.value)
    end_time = time.time() - start_time
    print(str(datetime.timedelta(seconds=end_time)))

def sDimLayer():
    if k3.isattrdef("AutoPlace")<1:
        k3.attribute( k3.k_create, "AutoPlace", "Номер вида на котором определен размер", k3.k_real, 5, 0  )
    if k3.isattrdef("VidDimPlace")<1:
        k3.attribute( k3.k_create, "VidDimPlace", "Номер вида на котором определен размер", k3.k_real, 5, 0 )
    if k3.isattrdef("NumType")<1:
        k3.attribute( k3.k_create, "NumType", "NumType", k3.k_real, 5, 0 )
    k3.layers(k3.k_new, "VidDim_1")
    k3.layers(k3.k_new, "VidDim_2")
    k3.layers(k3.k_new, "VidDim_3")
    k3.layers(k3.k_new, "VidDim_4")
    k3.selbyattr( "NumType!="+str(-999), k3.k_all, k3.k_done )
    if k3.sysvar(61):
        #--  Удаляем старые номера объектов
        k3.delete(k3.k_previous, k3.k_done)

if __name__ == '__main__':
    sDimLayer()
    k3.grfcoeff(9.6)
    s = start_scene_raster()
    if len(s.list_not_vis)>0 :
        print('Есть невидимые в данной схеме панели с номерами :', s.list_not_vis )


