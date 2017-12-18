# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:        test_PathInfo
# Purpose:     Модуль теста pathInfo
#
# Author:      Aleksandr Dragunkin
#
# Created:     14.04.2015
# Изменения для версии 7.3 поддержка Python3
# Copyright:   (c) GEOS 2012 http://k3info.ru/
# Licence:     FREE
# -------------------------------------------------------------------------------


#import wingdbstub
import k3
import time
import datetime
import cProfile
from mPanel import PanelRectangle

#----------------------------------------------
def profile(func):
    """Decorator for run function profile"""
    def wrapper(*args, **kwargs):
        profile_filename = func.__name__ + '.prof'
        profiler = cProfile.Profile()
        result = profiler.runcall(func, *args, **kwargs)
        profiler.dump_stats(profile_filename)
        return result
    return wrapper
#---------------------------



# запуск построителя графа gprof2dot -f pstats start_ppi.prof | dot -Tpng -o start_ppi.png
# Вот это вариант что сверху не работает по причине кодировки консоли cp1251
# я сделал иначе gprof2dot -o s.res -f pstats start_ppi.prof выгрузил в файл s.res
# затем dot -Tpng -Tps s.res -o start_ppi.png и получил картинку вызовов
#
# Кроме того можем получить статистику
#>>> import pstats
#>>> p = pstats.Stats('d:\PKM73_DV\Data\PKM\Proto\start_ppi.prof')
#>>> p.sort_stats('calls').print_stats()
@profile
def start_ppi():
    PANEL = PanelRectangle()
    
    k3.switch(k3.k_autosingle, k3.k_on)
    try:
        k3.selbyattr('FurnType=="010100"', k3.k_interact)
        k3.switch(k3.k_autosingle, k3.k_off)
        if k3.sysvar(61) > 0:
            el = k3.getselnum(1)
    
            start_time=time.time()
    
            pInfo = PANEL.getPanelPathInfo(el)
            
            end_time=time.time()-start_time
            
            print(str(datetime.timedelta(seconds = end_time)))
    except:
        k3.switch(k3.k_autosingle, k3.k_off)
    
if __name__ == '__main__':
    start_ppi()