# -*- coding: utf-8 -*-
# import wingdbstub
import k3
from SingletonMetaClass import Singleton

class k3bitmask:
    """Работа с битовыми масками
    BitClear,  BitSet,  BitTest,  NBitClear,  NBitSet,  NBitTest"""
    ivalue = 0
    imask = 0
    
    def bitclear(self, ivalue=0, imask=0):        """INTEGER BitClear(INTEGER <iValue>, INTEGER <iMask >)
        Функция сбрасывает (обнуляет) биты в <iValue>, для которых в <iMask > стоит значение
        1. Остальные биты в <iValue> не изменяются. Функция возвращает результирующее значение."""
        return k3.bitclear(ivalue, imask)
    
    def bitset(self, ivalue=0, imask=0):
        """INTEGER BitSet(INTEGER <iValue>, INTEGER <iMask >)
        Функция установить в единицу биты в <iValue>, для которых в <iMask > стоит значение
        1. Остальные биты в <iValue> не изменяются. Функция возвращает результирующее значение.
        """
        return k3.bitset(ivalue, imask)
    
    def bittest(self, ivalue=0, imask=0):
        """INTEGER BitTest(INTEGER <iValue>, INTEGER <iMask >)
        Если хотя бы один бит в <iValue>, для которых в <iMask > стоит значение 1, равен
        единице, то функция возвращает 1, иначе - возвращает 0.
        """
        return k3.bittest(ivalue, imask)
    
    def nbitclear(self, ivalue=0, nBit=0):
        """INTEGER NBitClear(INTEGER <iValue>, INTEGER <nBit>)
        Функция сбрасывает (обнуляет) один бит с номером <nBit> в <iValue>. Значения <nBit>
        могут быть от 1 (крайний правый) до 32 (крайний левый). Функция возвращает результирующее
        значение.
        """
        return k3.nbitclear(ivalue, nBit)
    
    def nbitset(self,  ivalue=0, nBit=0):
        """INTEGER NBitSet(INTEGER <iValue>, INTEGER <nBit>)
        Функция устанавливает в единицу один бит с номером <nBit> в <iValue>. Значения
        <nBit> могут быть от 1 (крайний правый) до 32 (крайний левый). Функция возвращает
        результирующее значение.
        """
        return k3.nbitset(ivalue, nBit)
    
    def nbittest(self,  ivalue=0, nBit=0):
        """INTEGER NBitTest(INTEGER <iValue>, INTEGER <nBit>)
        Если один бит с номером <nBit> в <iValue> равен 1, функция возвращает 1. В противном
        случае, функция возвращает 0. Значения <nBit> могут быть от 1 (крайний правый) до 32
        (крайний левый)"""
        return k3.nbittest(ivalue, nBit)
    
class mb_bitmask(Singleton):
    """
    Битовая маска учета парметров мебельной панели
    * Габариты заготовки 1
    * Толщина панели 2
    * Материал панели 3
    * Форма внешнего контура заготовки 4
    * Основное расположение панели (полка, стойка, стенка) 5
    * Форма внешнего контура заготовки 6
    * Форма гнутья панели 7
    * Пропилы 8
    * Торцевые пазы 9
    * Линии крепежа 10
    * Отделки 11
    * К3-файл с заготовкой панели 12
    * Реальные вырезы 13
    * Линии маркировки 14
    * Кромки прямолинейные 15
    * Кромки криволинейные 16
    * Фрезеровки 17
    * Отверстия торцев 18
    * Отверстия пласти 19
    * Отверстия под углом 20
    * Группа материала кромки 21
    * Материал кромки 22
    * Толщина кромки 23
    * Группа материала отделки 24
    * Материал отделки 25
    * Толщина отделки 26
    * Группа материала панели 27
    """
    mask = None
    idpropgroup = 163


    def dialog(self):
        k3.udbranch('u69_CRTPan')

                       
    def __init__(self):
        self.ud_create()
        self.ud_get()


    def ud_create(self):
        try:
            pos3=k3.udgetpos("u69_CRTPan")
            if pos3==0 : #Различные критерии
                pos=k3.udgetpos("Numerator")
                pos3= k3.udaddcat(pos,"Различные критерии сравнения","u69_CRTPan",0,1)
            if k3.udgetpos("u69_CRTPan_1")==0 :
                pos3 = k3.udgetpos("u69_CRTPan")
                self.mask = 111148523
                pos4 = k3.udaddentity(pos3,"Критерии графической документации панели","u69_CRTPan_1",13,self.mask, self.idpropgroup,0)
        except Exception as inst:
            print(type(inst))    # the exception instance
            print(inst.args)     # arguments stored in .args
            print(inst)        
            
    def ud_get(self):
        try:
            vType=k3.Var()
            sVal=k3.Var()
            rVal=k3.Var()
            res = k3.udgetentity("u69_CRTPan_1",vType,rVal,sVal)
            self.mask = int(rVal.value)
        except Exception as inst:
            print(type(inst))    # the exception instance
            print(inst.args)     # arguments stored in .args
            print(inst)
        #return [self.nbittest(self.mask, i) for i in range(27)]



