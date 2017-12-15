# -*- coding: cp1251 -*-
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import k3
#import wingdbstub

from tkinter import *
from tkinter.ttk import *
import Utilites_K3 as Ut

NULL=k3.renumerate()
sy = k3.sysvar(62)

obj_k3 = k3.Var()
k3.switch(k3.k_autosingle,k3.k_on)
#k3.selbyattr('left(FurnType,2)==\"10\"&&Posit!=10',k3.k_prompt,str('Выберите изделие'),k3.k_interact)
#3.selbyattr('Posit!=10',k3.k_prompt,str('Выберите изделие'),k3.k_interact)
k3.selbyattr('IsAssign(\"FurnType\")',k3.k_prompt,str('Выберите изделие'),k3.k_stayblink,k3.k_interact,k3.k_done)
sel = k3.sysvar(61)
if sel==0:
    Arr = Ut.getListArrayAllObjectsScene(AttrFilter='IsAssign(\"FurnType\")')
    # k3.cancel

listUP = []
listUN = [] 
for i in range(int(sel)):
    obj_k3.value = k3.getselnum(i+1)
    # UnitPosObj = k3.getattr(obj_k3,'UnitPos',0)
    listUP.append(int(k3.getattr(obj_k3,'UnitPos',0)))
    UnitName = k3.getattr(obj_k3,'UnitName','')
    # listUN.append(k3.getattr(obj_k3,'UnitPos',0))
    if len(UnitName) == 0:
        UnitName = k3.getattr(obj_k3,'ElemName','')
    listUN.append(UnitName)
# if sel>0.:
    # obj_k3.value = k3.getselnum(1)
    # # UnitPosObj = k3.getattr(obj_k3,'UnitPos',0)
    # # listUP.append(k3.getattr(obj_k3,'UnitPos',0))
    # UnitName = k3.getattr(obj_k3,'UnitName','')
    # listUN.append(k3.getattr(obj_k3,'UnitPos',''))
    # if len(UnitName) == 0:
        # UnitName = k3.getattr(obj_k3,'ElemName','')

listArrAllObjects=Ut.getListArrayAllObjectsScene() # Заполнение всеми элементами сцены

lArr1 = []
unique_data = []
i = 0
k = 0
SCMat = 0
CostRep = 0
Cline = 0
SizeF = 0

#ListGroup = ['Square', 'Length', 'Decorate']

Cost=k3.Var('Cost')
Size=k3.Var('Size')
SumCostMat=k3.Var('SumCostMat')
Curline=k3.Var('Curline')
#NomID=k3.Var('NomID')
MatName=k3.Var('MatName')
TypeElem = '--'
ParG = {}
ParGF = {}
NameElem = {}
NameElemTmp = {}

psc=k3.Var('psc')

for Arr in listArrAllObjects:
    for elem in Arr:
        #elem = arr.array[ind]
        if k3.isassign("FurnType",elem.value):
            TopParentPos = k3.getattr(elem.value,'TopParentPos',-1)
            UPObj = k3.getattr(elem.value,'UnitPos',-1)
            # if TopParentPos==UnitPosObj or UnitPosObj==UPObj:
            # if TopParentPos in listUP: print(TopParentPos)
            # if UPObj in listUP: print(UPObj)
            if TopParentPos in listUP or UPObj in listUP:
                UnitPos = k3.getattr(elem.value,'UnitPos',0)
                ParentPos = k3.getattr(elem.value,'ParentPos',0)

                # tt=k3.getattr(elem.value,"FurnType","")
                if k3.isassign("SumCostInfo",elem.value):
                    ScrNum=k3.readscratch("SumCostInfo",elem.value)
                    if ScrNum>0:
                        i += 1
                        PriceID = k3.getattr(elem.value,'PriceID',0)
                        NameElemTmp[i] = k3.getattr(elem.value,'ElemName',"")
                        #lArr1.append(PriceID) # добавляем в массив
                        Name = k3.getattr(elem.value,'ElemName','не удалось прочитать')
                        # k3.putmsg(Name)
                        
                        # print "i=",i
                        ParG[i] = []
                        
                        num=k3.cntgroupscr(ScrNum)
                        # print('num=',num)
                        j = 0
                        if num>0:
                            Arr = k3.VarArray(int(num))
                            k3.namegroupscr(ScrNum,Arr);

                            for ParGroup in Arr:
                                j += 1
                                # print "j=",j
                                
                                Cost.value = 0
                                Size.value = 0
                                SumCostMat.value = 0
                                Curline.value = '-'
                                #NomID.value = 0
                                MatName.value = Name

                                numpar=k3.cntvarscr(ScrNum,ParGroup)
                                
                                # Элементы с фиксируемой ценой для поиска одинаковых
                                KeyPiece = True if ParGroup.value in ['Elem', 'ElemFurn'] else False
                                
                                if numpar>0:
                                    
                                    ArrScrPar = k3.VarArray(int(numpar))
                                    
                                    k3.namevarscr(ScrNum,ParGroup,ArrScrPar)
                                    listD = []
                                    Cline = '-'
                                    TypeElem = u'шт.'
                                    SCMat = 0
                                    CostRep = 0
                                    for ScrPar in ArrScrPar:
                                        # print ScrPar.value
                                        if ScrPar.value=='Cost':
                                            NULLOUT=k3.getscratch(ScrNum,ParGroup,ScrPar,Cost,psc);
                                            if Cost.value == 0: break
                                            CostRep = round(Cost.value,2) if Cost.value%1 > 0 else int(Cost.value)
                                            if KeyPiece:
                                                lst = [int(PriceID),CostRep]
                                                lArr1.append(lst)
                                                if lst not in unique_data:
                                                    unique_data.append(lst)

                                        if ScrPar.value=='Square' or ScrPar.value=='Length' or\
                                        ScrPar.value=='Number' or ScrPar.value[7:]=='Decorate':
                                            NULLOUT=k3.getscratch(ScrNum,ParGroup,ScrPar,Size,psc);
                                            TypeElem = u'п.метр' if ScrPar.value=='Length' else u'кв.метр'
                                            if ScrPar.value=='Number': TypeElem = u'шт.'
                                            SizeF = round(Size.value,3) if Size.value%1 > 0 else int(Size.value)

                                        if ScrPar.value=='SumCostMat' or ScrPar.value=='SumCostWork' or ScrPar.value=='SumCostElem':
                                            NULLOUT=k3.getscratch(ScrNum,ParGroup,ScrPar,SumCostMat,psc);
                                            SCMat = round(SumCostMat.value,2) if SumCostMat.value%1 > 0 else int(SumCostMat.value)
                                            # print SCMat
                                        if ScrPar.value=='Curline':
                                            NULLOUT=k3.getscratch(ScrNum,ParGroup,ScrPar,Curline,psc);
                                            Cline = round(Curline.value,2) if Curline.value > 0 else '-'

                                        # if ScrPar.value=='NomID':
                                            # NULLOUT=k3.getscratch(ScrNum,ParGroup,ScrPar,NomID,psc);
                                            
                                        if ScrPar.value=='MatName':
                                            NULLOUT=k3.getscratch(ScrNum,ParGroup,ScrPar,MatName,psc);

                                    listD = [MatName.value, SizeF, SCMat, Cline, CostRep, TypeElem]
                                    # print listD
                                #par
                                ParG[i].append({j:listD})
                            #gr
                        #obj  
                        if KeyPiece==False:
                            k += 1
                            ParGF[k] = ParG[i]
                            NameElem[k] = NameElemTmp[i]

# print ParGF
# print unique_data

# Найдем уникальные значения                                 
#unique_data = [list(x) for x in set(tuple(x) for x in lArr1)]

# for a in unique_data:
    # print int(a[0])
    # print k3.priceinfo(int(a[0]),"MATNAME","",1)
    # print lArr1.count(a)

class Window():

    def __init__(self):
        self.root = Tk()
        # self.root.title(u"Ценовой состав изделия - %s" % UnitName.decode('cp1251'))
        UName = 'Набор элементов' if len(listUN)>1 else UnitName
        self.root.title(u'{}'.format(UName))
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.exitform())
        
        container = Frame(self.root) # создать внешний фрейм
        container.pack(fill='both', expand=True)
        
        self.tree = Treeview(container)
        
        self.tree["columns"]=("amount","typeunit","unitcost","extra","price")
        self.tree.column("#0",width=300)
        self.tree.heading("#0",text=u"Название")
        
        self.tree.column("amount",width=50)
        self.tree.heading("amount",text=u"Кол-во")
        
        self.tree.column("typeunit",width=80)
        self.tree.heading("typeunit",text=u"Ед. измерения")
        
        self.tree.column("unitcost",width=80)
        self.tree.heading("unitcost",text=u"Цена за ед.изм.")
        
        self.tree.column("extra",width=50)
        self.tree.heading("extra",text=u"Доп.")
        
        self.tree.column("price",width=100)
        self.tree.heading("price",text=u"Цена")

        vsb = Scrollbar(container, orient="vertical", command=self.tree.yview)
        hsb = Scrollbar(container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        #self.tree.tag_configure("ttk")
        self.tree.grid(column=0, row=0, sticky='nsew')
        vsb.grid(column=1, row=0, sticky='ns')
        hsb.grid(column=0, row=1, sticky='ew')
        
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)

        for a in unique_data:
            # self.tree.insert("",0,"dir"+str(int(a[0])),text=k3.priceinfo(int(a[0]),"MATNAME","",1).decode('cp1251')\
            self.tree.insert("",0,"dir"+str(int(a[0])),text=k3.priceinfo(int(a[0]),"MATNAME","",1)\
            ,values=(lArr1.count(a), u'шт', a[1], '', round(lArr1.count(a) * a[1],2)))
            
        for key in ParGF:
            # self.tree.insert("",0,"dir"+str(key),text=NameElem[key].decode('cp1251'))
            keyGr = False
            if len(ParGF[key])>1:
                keyGr = True
                self.tree.insert("",0,"dir"+str(key),text=NameElem[key])
            CostFin = 0
            for gr in ParGF[key]:
                
                for elem in gr:
                    MatName, Size, SumCostMat, Curline, Cost, TypeElem = gr[elem]
                    
                    # Преобразуем число в наглядно понятные проценты
                    if isinstance(Curline, float):
                        znak='+' if int(Curline) >= 1 else '-'
                        perc = round((Curline%1)*100,0) if znak=='+' else round(100-(Curline%1)*100,0)
                        Curline = "{0}{1}%".format(znak, str(perc))
                    
                    # self.tree.insert("dir"+str(key),'end',text=MatName.decode('cp1251')\
                    if keyGr:
                        self.tree.insert("dir"+str(key),'end',text=MatName,values=(Size, TypeElem, SumCostMat, Curline, Cost))
                    else:
                        # self.tree.insert("",0,"dir"+str(key)',text=MatName,values=(Size, TypeElem, SumCostMat, Curline, Cost))
                        self.tree.insert("",0,"dir"+str(key),text=NameElem[key],values=(Size, TypeElem, SumCostMat, Curline, Cost))
                    
                    CostFin = CostFin + Cost
            
            if keyGr:
                self.tree.set("dir"+str(key),'price',round(CostFin,2))
            
    def exitform(self):
        #k3.layers(k3.k_off, LayName)
        k3.select(k3.k_done)
        self.root.destroy()
        

main_window = Window()
#main_window.root.wm_geometry("")
mainloop()
