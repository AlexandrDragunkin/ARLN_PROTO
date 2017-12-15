# -*- coding: utf-8 -*-

"""Создаем набор пользовательских умолчаний для различных типов чертежей"""

import wingdbstub
 
import k3

def _udgetentity(*args):
    return k3.udgetentity(args)

def _udgetpos(*args):
    return k3.udgetpos(args)

def _udnavigate(*args):
    return k3.udnavigate(args)

def _udremove(*args):
    return k3.udremove(args)

def _udaddcat(*args):
    return k3.udaddcat(args)

def _udaddentity(*args):
    return k3.udaddentity(args)

def _udloadsave(*args):
    return k3.udloadsave(args)

def _udgetinfo(*args):
    return k3.udgetinfo(args)

def _udsetname(*args):
    return k3.udsetname(args)

def _udbranch(*args):
    return k3.udbranch(args)

def _udsetentity(*args):
    return k3.udsetentity(args)

def _udcombototal(*args):
    return k3.udcombototal(args)

def _udcombonext(*args):
    return k3.udcombonext(args)

class Storage(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as key:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError as k:
            raise AttributeError(k)

    def __repr__(self):
        return '<Storage ' + dict.__repr__(self) + '>'


#---------------------------------------------------------------------------------------------
class bUdEntity:
    """
    Базовый класс пользовательских умолчаний.
    """
    @classmethod
    def udgetpos(self, nm):
        ''''''
        return _udgetpos([nm])
    @classmethod
    def udremove(self, ls):
        """
        Удалить категорию или свойство, или список категорий и свойств по наименованиям.
        """
        if isinstance(ls, (tuple, list, dict)):
            for nm in ls:
                if isinstance(nm, str):
                    pos=_udgetpos([nm])
                if pos>0:
                    return _udremove([pos])
        elif isinstance(ls, (int, float, str)):
            return _udremove([ls])

    @classmethod
    def udgetinfo(self, pos):
        '''Получить информацию о категории или свойствею
        Возвращает: Имя, Идентификатор, Тип'''
        Name,Variable,ValType = k3.Var(),k3.Var(),k3.Var()
        Name.value,Variable.value,ValType.value='','',0
        result = _udgetinfo(pos,Name,Variable,ValType)
        return Name.value,Variable.value,ValType.value
    
    @classmethod
    def udgetentity(self, pos):
        '''Получить значение свойства по переменной или по позиции'''
        def _isint(val):
            if isinstance(val, float):
                if abs(val - int(val)) < 0.0001:
                    return int(val)
            return val
        ValType,dVal,sVal = k3.Var(),k3.Var(),k3.Var()
        ValType.value,sVal.value,dVal.value='','',0
        if pos>0:
            _udgetentity(pos,ValType,dVal,sVal)
        return sVal.value if ValType.value in (4, 11) else _isint(dVal.value)

#---------------------------------------------------------------------------------------------
class UdCategory(bUdEntity):
    """Класс категория пользовательских умолчаний"""
        
    def __init__(self, pos = None, name = None, variable = None, collapsed = None, sort = None, funtree=None, node=None):
        self.funtree = funtree
        self.node = node
        if name is None:
            self.pos = pos
            self.name, self.variable, self.vartype = self.udgetinfo(pos)
            
        else:
            self.pos = pos
            self.name = name
            self.variable = variable
            self.collapsed = collapsed
            self.sort=sort
            self.pos = self.udaddcat(pos, name, variable, collapsed, sort)
        if not funtree is None :
            if not self.pos in funtree.parents.keys():
                funtree.add(self)
                tc = self.childs
            
        
    def udaddcat(self, pos , name, variable, collapsed = 0, sort=1):
        
        """Добавить категорию.
        * Pos– позиция в дереве пользовательских параметров
        * Name– имя категории в диалоге редактирования 
        * Variable– Переменная для доступа к категории
        * Collapsed– первоначально показывать  категорию в диалоге в свёрнутом виде (1) 
        или развёрнутом виде (0)
        * Sort– задаёт порядок сортировки с соседними категориями и свойствами
        """
        self.pos = pos
        self.name = name
        self.variable = variable
        self.collapsed
        self.sort=sort        
        return k3.udaddcat(pos, name, variable, collapsed, sort=1)
    
    @property
    def childs(self):
        '''Список потомков текущей категории'''
        funtree = self.funtree
        def _add_child(i, el, childs=[]):
            childs.insert(i, el)
        
        childs = []
        am = self.node
        fch = am.first_child
        lch = am.last_child
        el = Node(fch, funtree)
        _add_child(0, el, childs) 
        el = Node(lch, funtree)
        while el.pos != fch and el.pos > 0:
            _add_child(1, el, childs)
            el = Node(el.previous_neighbor, funtree)
        
        return childs

#---------------------------------------------------------------------------------------------
class UdEntity(bUdEntity):
    """Класс пользовательских умолчаний (свойство)"""
    
    def __init__(self, pos = None, name = None, variable = None, vartype = None,dvar = None,data = None,sort = None, funtree=None, node=None):
        self.node = node
        if name is None:
            self.pos = pos
            self.name, self.variable, self.vartype = self.udgetinfo(pos)
        else:
            self.name = name
            self.variable = variable
            self.vartype = vartype
            self.dvar = dvar
            self.data = data
            self.Sort=sort
            self.pos = self.udaddentity(pos, name, variable, vartype, dvar, data, sort)
        if not funtree is None:
            funtree.add(self)        


    def udaddentity(pos, name, variable, vartype, dvar, data, sort=1):
        """Добавить свойство
        POSITION Pos, STRING name, STRING Variable, DOUBLE VarType, 
        DOUBLE dVar, DOUBLE data2, DOUBLE Sort
        """
        self.pos = pos
        self.name = name
        self.variable = variable
        self.vartype = vartype
        self.dvar = dvar
        self.data = data
        self.Sort=Sort        
        return _udaddentity([pos, name, variable, vartype, dvar, data, sort])

#---------------------------------------------------------------------------------------------
class UdNavigate:
    '''Навигатор по дереву умолчаний
    '''
    def __init__(self, ud):
        '''ud - экземпляр класса свойства или категории'''
        self._setud(ud)
        pass
    
    def _setud(self, ud):
        if ud is None:
            self.ud = bUdEntity()
        else:
            self.ud = ud

    def branch(self, nm):
        '''Возвращает словарь свойств '''
        br = Branch(nm)
        return  br #[self.ud.udgetinfo(e.pos) for e in childs]

#---------------------------------------------------------------------------------------------
#class Branch(Storage):
    #'''Ветвь дерева'''
    #def __init__(self, parent=None):
        #'''parent - Индекс корня'''
        #self.parent = parent
        
        #self.__setattr__(nm, self._br(nm)) # Список прямых потомков
    
    #def _br(self, nm):
        #def _add_branch(el):
            #if bUdEntity.udgetinfo(el.pos)[2] == 0:
                ## Это категория
                #br = Branch(el.pos)
                #el['branches'] = el.get('branches', [])
                #el['branches'].append(br)

        #def _add_child(i, el, childs=[], _add_branch=_add_branch):
            #childs.insert(i, el)
            #_add_branch(el)

        ## am- корень по сути, родитель ветки. Это может быть ствол или предыдущая ветка или ничего
        #am = Node(nm)
        #fch = am.first_child
        #lch = am.last_child
        #el = Node(fch)
        #_add_child(0, el) , childs
        #el = Node(lch)
        #while el.pos != fch and el.pos > 0:
            #_add_child(1, el, childs)
            #el = Node(el.previous_neighbor)
        #return childs

#---------------------------------------------------------------------------------------------
class Pos:
    @property
    def pos(self):
        return self._pos
    
    @pos.deleter
    def pos(self):
        del self._pos
        
    @pos.setter
    def pos(self, nm):
        def _getpos(nm):
            if isinstance(nm, (int, float)):
                return nm
            if nm is None:
                nm = ''
            if nm == ' ':
                nm = ''
            return bUdEntity.udgetpos(nm)
        self._pos = _getpos(nm)
        
# -----------------------------------------------------------------------------------------------
class Node(Pos):
    '''Узел дерева пользовательских умолчаний.
    '''
    def __init__(self, nm=' ', funtree=None):
        '''nm - имя или позиция или пустая строка или None в дереве пользовательских умолчаний.'''
        self.pos = nm
        self.funtree = funtree
        self.holder = self.setholder()
        
        
    @property
    def info(self):
        return self.holder.udgetinfo(self.pos)
    
    @property
    def values(self):
        return self.holder.udgetentity(self.pos)
    
    def setholder(self ):
        info = bUdEntity.udgetinfo(self.pos)
        
        if info[2] == 0 or self.parent == 0:
            # Это категория если тип 0 или отсутствует родитель (значит корень)
            nd = UdCategory(self.pos, funtree=self.funtree, node=self)
            return nd

        else:
            # Это свойство
            nd = UdEntity(self.pos, funtree=self.funtree, node=self)
            return nd

    
    @property
    def parent(self):
        '''Предок
        Значение позиции предка в дереве пользовательских умолчаний.
        Возвращаемое значение, равное 0, означает, что такой позиции не существует. 
        '''
        return _udnavigate(self.pos, -10)
    
    @property
    def first_child(self):
        '''Первый потомок'''
        return _udnavigate(self.pos, 10)
    
    @property
    def last_child(self):
        '''Последний потомок'''
        return _udnavigate(self.pos, 20)
    
    @property
    def first_neighbor(self):
        '''Первый сосед'''
        return _udnavigate(self.pos, -2)
    
    @property
    def previous_neighbor(self):
        '''Предыдущий сосед'''
        return _udnavigate(self.pos, -1)
    
    @property
    def next_neighbor(self):
        '''Следующий сосед'''
        return _udnavigate(self.pos, 1)
    
    @property
    def last_neighbor(self):
        '''Последний сосед'''
        return _udnavigate(self.pos, 2)        
        

#---------------------------------------------------------------------------------------------
def test():
    #tree = UdNavigate(ud=None)
    #print(tree.branch('Drawings')['Drawings'])
    nd = Node('')
    for el in nd.holder:
        if isinstance(el, UdCategory):
            el.childs
    #br = Branch('')
    
def gui():
    from SingletonMetaClass import Singleton
    
    import wx
    try:
        from agw import hypertreelist as HTL
        #bitmapDir = "bitmaps/"
    except ImportError: # if it's not there locally, try the wxPython lib.
        import wx.lib.agw.hypertreelist as HTL
        #bitmapDir = "bitmaps/"    
    
    #import ListCtrl
    #import images
    try:
        from mMpathexpand import Mpathexpand as mpex
        TESTSPATH = mpex().TESTSPATH + 'python\\'
    except:
        TESTSPATH = ''
    
    #import wx.lib.agw.supertooltip as supertooltip
    #class SuperToolTipTestPanel(wx.Panel):
        #def __init__(self, parent):
            #super(SuperToolTipTestPanel, self).__init__(parent)
            #self.locale = wx.Locale(wx.LANGUAGE_RUSSIAN)
            ## Attributes
            ##self.button = wx.Button(self, label="Go")
            #msg = "Запуск отсчета"
            #self.stip = supertooltip.SuperToolTip(msg)
            ## Setup SuperToolTip
            #bodybmp = wx.Bitmap(TESTSPATH+"16-homer-simpson.png", wx.BITMAP_TYPE_PNG)
            #self.stip.SetBodyImage(bodybmp)
            #self.stip.SetHeader("Пускач отсчета")
            #footbmp = wx.Bitmap(TESTSPATH+"warning.png", wx.BITMAP_TYPE_PNG)
            #self.stip.SetFooterBitmap(footbmp)
            #self.footer_def = "Внимание: Ща, щитать начну"
            #self.stip.SetFooter(self.footer_def) 
            #self.stip.ApplyStyle("XP Blue")
        ##self.stip.SetTarget(self.button)
        
        
        
    # Показывать идентификаторы групп
    KEY_IDENTIFER_GROUP = True    
    
    penstyle = ["wx.PENSTYLE_SOLID", "wx.PENSTYLE_TRANSPARENT", "wx.PENSTYLE_DOT",
                "wx.PENSTYLE_LONG_DASH", "wx.PENSTYLE_DOT_DASH", "wx.PENSTYLE_USER_DASH",
                "wx.PENSTYLE_BDIAGONAL_HATCH", "wx.PENSTYLE_CROSSDIAG_HATCH",
                "wx.PENSTYLE_FDIAGONAL_HATCH", "wx.PENSTYLE_CROSS_HATCH",
                "wx.PENSTYLE_HORIZONTAL_HATCH", "wx.PENSTYLE_VERTICAL_HATCH"]    
    ArtIDs = [ "None",
               "wx.ART_ADD_BOOKMARK",
               "wx.ART_DEL_BOOKMARK",
               "wx.ART_HELP_SIDE_PANEL",
               "wx.ART_HELP_SETTINGS",
               "wx.ART_HELP_BOOK",
               "wx.ART_HELP_FOLDER",
               "wx.ART_HELP_PAGE",
               "wx.ART_GO_BACK",
               "wx.ART_GO_FORWARD",
               "wx.ART_GO_UP",
               "wx.ART_GO_DOWN",
               "wx.ART_GO_TO_PARENT",
               "wx.ART_GO_HOME",
               "wx.ART_FILE_OPEN",
               "wx.ART_PRINT",
               "wx.ART_HELP",
               "wx.ART_TIP",
               "wx.ART_REPORT_VIEW",
               "wx.ART_LIST_VIEW",
               "wx.ART_NEW_DIR",
               "wx.ART_HARDDISK",
               "wx.ART_FLOPPY",
               "wx.ART_CDROM",
               "wx.ART_REMOVABLE",
               "wx.ART_FOLDER",
               "wx.ART_FOLDER_OPEN",
               "wx.ART_GO_DIR_UP",
               "wx.ART_EXECUTABLE_FILE",
               "wx.ART_NORMAL_FILE",
               "wx.ART_TICK_MARK",
               "wx.ART_CROSS_MARK",
               "wx.ART_ERROR",
               "wx.ART_QUESTION",
               "wx.ART_WARNING",
               "wx.ART_INFORMATION",
               "wx.ART_MISSING_IMAGE",
               "SmileBitmap"
               ]
    keyMap = {
        wx.WXK_BACK : "WXK_BACK",
        wx.WXK_TAB : "WXK_TAB",
        wx.WXK_RETURN : "WXK_RETURN",
        wx.WXK_ESCAPE : "WXK_ESCAPE",
        wx.WXK_SPACE : "WXK_SPACE",
        wx.WXK_DELETE : "WXK_DELETE",
        wx.WXK_START : "WXK_START",
        wx.WXK_LBUTTON : "WXK_LBUTTON",
        wx.WXK_RBUTTON : "WXK_RBUTTON",
        wx.WXK_CANCEL : "WXK_CANCEL",
        wx.WXK_MBUTTON : "WXK_MBUTTON",
        wx.WXK_CLEAR : "WXK_CLEAR",
        wx.WXK_SHIFT : "WXK_SHIFT",
        wx.WXK_ALT : "WXK_ALT",
        wx.WXK_CONTROL : "WXK_CONTROL",
        wx.WXK_MENU : "WXK_MENU",
        wx.WXK_PAUSE : "WXK_PAUSE",
        wx.WXK_CAPITAL : "WXK_CAPITAL",
        wx.WXK_END : "WXK_END",
        wx.WXK_HOME : "WXK_HOME",
        wx.WXK_LEFT : "WXK_LEFT",
        wx.WXK_UP : "WXK_UP",
        wx.WXK_RIGHT : "WXK_RIGHT",
        wx.WXK_DOWN : "WXK_DOWN",
        wx.WXK_SELECT : "WXK_SELECT",
        wx.WXK_PRINT : "WXK_PRINT",
        wx.WXK_EXECUTE : "WXK_EXECUTE",
        wx.WXK_SNAPSHOT : "WXK_SNAPSHOT",
        wx.WXK_INSERT : "WXK_INSERT",
        wx.WXK_HELP : "WXK_HELP",
        wx.WXK_NUMPAD0 : "WXK_NUMPAD0",
        wx.WXK_NUMPAD1 : "WXK_NUMPAD1",
        wx.WXK_NUMPAD2 : "WXK_NUMPAD2",
        wx.WXK_NUMPAD3 : "WXK_NUMPAD3",
        wx.WXK_NUMPAD4 : "WXK_NUMPAD4",
        wx.WXK_NUMPAD5 : "WXK_NUMPAD5",
        wx.WXK_NUMPAD6 : "WXK_NUMPAD6",
        wx.WXK_NUMPAD7 : "WXK_NUMPAD7",
        wx.WXK_NUMPAD8 : "WXK_NUMPAD8",
        wx.WXK_NUMPAD9 : "WXK_NUMPAD9",
        wx.WXK_MULTIPLY : "WXK_MULTIPLY",
        wx.WXK_ADD : "WXK_ADD",
        wx.WXK_SEPARATOR : "WXK_SEPARATOR",
        wx.WXK_SUBTRACT : "WXK_SUBTRACT",
        wx.WXK_DECIMAL : "WXK_DECIMAL",
        wx.WXK_DIVIDE : "WXK_DIVIDE",
        wx.WXK_F1 : "WXK_F1",
        wx.WXK_F2 : "WXK_F2",
        wx.WXK_F3 : "WXK_F3",
        wx.WXK_F4 : "WXK_F4",
        wx.WXK_F5 : "WXK_F5",
        wx.WXK_F6 : "WXK_F6",
        wx.WXK_F7 : "WXK_F7",
        wx.WXK_F8 : "WXK_F8",
        wx.WXK_F9 : "WXK_F9",
        wx.WXK_F10 : "WXK_F10",
        wx.WXK_F11 : "WXK_F11",
        wx.WXK_F12 : "WXK_F12",
        wx.WXK_F13 : "WXK_F13",
        wx.WXK_F14 : "WXK_F14",
        wx.WXK_F15 : "WXK_F15",
        wx.WXK_F16 : "WXK_F16",
        wx.WXK_F17 : "WXK_F17",
        wx.WXK_F18 : "WXK_F18",
        wx.WXK_F19 : "WXK_F19",
        wx.WXK_F20 : "WXK_F20",
        wx.WXK_F21 : "WXK_F21",
        wx.WXK_F22 : "WXK_F22",
        wx.WXK_F23 : "WXK_F23",
        wx.WXK_F24 : "WXK_F24",
        wx.WXK_NUMLOCK : "WXK_NUMLOCK",
        wx.WXK_SCROLL : "WXK_SCROLL",
        wx.WXK_PAGEUP : "WXK_PAGEUP",
        wx.WXK_PAGEDOWN : "WXK_PAGEDOWN",
        wx.WXK_NUMPAD_SPACE : "WXK_NUMPAD_SPACE",
        wx.WXK_NUMPAD_TAB : "WXK_NUMPAD_TAB",
        wx.WXK_NUMPAD_ENTER : "WXK_NUMPAD_ENTER",
        wx.WXK_NUMPAD_F1 : "WXK_NUMPAD_F1",
        wx.WXK_NUMPAD_F2 : "WXK_NUMPAD_F2",
        wx.WXK_NUMPAD_F3 : "WXK_NUMPAD_F3",
        wx.WXK_NUMPAD_F4 : "WXK_NUMPAD_F4",
        wx.WXK_NUMPAD_HOME : "WXK_NUMPAD_HOME",
        wx.WXK_NUMPAD_LEFT : "WXK_NUMPAD_LEFT",
        wx.WXK_NUMPAD_UP : "WXK_NUMPAD_UP",
        wx.WXK_NUMPAD_RIGHT : "WXK_NUMPAD_RIGHT",
        wx.WXK_NUMPAD_DOWN : "WXK_NUMPAD_DOWN",
        wx.WXK_NUMPAD_PAGEUP : "WXK_NUMPAD_PAGEUP",
        wx.WXK_NUMPAD_PAGEDOWN : "WXK_NUMPAD_PAGEDOWN",
        wx.WXK_NUMPAD_END : "WXK_NUMPAD_END",
        wx.WXK_NUMPAD_BEGIN : "WXK_NUMPAD_BEGIN",
        wx.WXK_NUMPAD_INSERT : "WXK_NUMPAD_INSERT",
        wx.WXK_NUMPAD_DELETE : "WXK_NUMPAD_DELETE",
        wx.WXK_NUMPAD_EQUAL : "WXK_NUMPAD_EQUAL",
        wx.WXK_NUMPAD_MULTIPLY : "WXK_NUMPAD_MULTIPLY",
        wx.WXK_NUMPAD_ADD : "WXK_NUMPAD_ADD",
        wx.WXK_NUMPAD_SEPARATOR : "WXK_NUMPAD_SEPARATOR",
        wx.WXK_NUMPAD_SUBTRACT : "WXK_NUMPAD_SUBTRACT",
        wx.WXK_NUMPAD_DECIMAL : "WXK_NUMPAD_DECIMAL",
        wx.WXK_NUMPAD_DIVIDE : "WXK_NUMPAD_DIVIDE"
        }
    
    class Log:
        def WriteText(self, text):
            if text[-1:] == '\n':
                text = text[:-1]
            wx.LogMessage(text)
        write = WriteText    
    
    class Branch(Singleton):
        def __init__(self,  tree_list, parent_name):
            self.tree_list = tree_list
            self.root = None
            self.parents = {}
            self.KEY_IDENTIFER_GROUP = False                    # Показывать идентификаторы групп
                     

        def add(self,el):
            parent = Node(el.pos).parent
            info = Node(el.pos).info
            if self.tree_list.GetRootItem() is None:
                self.root = self.tree_list.AddRoot(info[0]+'['+info[1]+']' if len(info[1])>0 else 'Пользовательские умолчания', ct_type=0)
                self.parents[el.pos]=self.root
            elif not el.pos in self.parents.keys():
                lst_ch = info[0].split('~')
                child = self.tree_list.AppendItem(self.parents[parent], lst_ch[0], ct_type=0)
                vls = self.values(child, el)
                if vls is None:
                    
                    # Выделяем группы 
                    # жирным текстом
                    self.tree_list.SetItemBold(child, True)
                    
                    # цветом шрифта
                    col1 = (0, 64, 128, 255)
                    self.tree_list.SetItemTextColour(child, col1)
                    
                    # Показывать идентификаторы групп
                    self.set_identifer(KEY_IDENTIFER_GROUP, info, child)                    
                self.parents[el.pos]=child
                if len(lst_ch) > 1:
                    for e in range(0, len(lst_ch[1:]), 2):
                        t_child = self.tree_list.AppendItem(child, lst_ch[1:][e+1], ct_type=2)
                        self.set_t_child(el, child, e, lst_ch, t_child)

        def set_identifer(self, KEY_IDENT, info, child):
            if KEY_IDENT:
                self.tree_list.SetItemText(child, '['+info[1]+']', 1)

        def set_t_child(self, el, child, e, lst_ch, t_child):
            if self.values(child, el) == int(lst_ch[1:][e]):
                t_child.Set3StateValue(True)
            else:
                t_child.Set3StateValue(False)
            self.tree_list.SetItemText(t_child, str(t_child.GetValue()), 2)
                        

                        
        def values(self, child, el):
            vls = None
            if isinstance(Node(el.pos).holder, UdEntity):
                vls = Node(el.pos).values
                if not vls is None:
                    # значит это UdEntity заполняем столбец значение
                    self.tree_list.SetItemText(child, str(vls), 2)
            return vls

                
    class HyperTreeList(HTL.HyperTreeList):
        
        def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                     size=wx.DefaultSize,
                     style=wx.SUNKEN_BORDER,
                     agwStyle=wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT,
                     log=None):
    
            HTL.HyperTreeList.__init__(self, parent, id, pos, size, style, agwStyle)
    
            alldata = dir(HTL)
    
            treestyles = []
            events = []
            for data in alldata:
                if data.startswith("TR_"):
                    treestyles.append(data)
                elif data.startswith("EVT_"):
                    events.append(data)
    
            events = events + [i for i in dir(wx) if i.startswith("EVT_TREE_")]
            for evt in ["EVT_TREE_GET_INFO", "EVT_TREE_SET_INFO", "EVT_TREE_ITEM_MIDDLE_CLICK",
                        "EVT_TREE_STATE_IMAGE_CLICK"]:
                events.remove(evt)
    
            treestyles = treestyles + [i for i in dir(wx) if i.startswith("TR_")]
            treeset = {}
            treestyles = [treeset.setdefault(e,e) for e in treestyles if e not in treeset]
    
            treestyles.sort()
    
            self.events = events
            self.styles = treestyles
            self.item = None
    
            #il = wx.ImageList(16, 16)
    
            #for items in ArtIDs[1:-1]:
                #bmp = wx.ArtProvider.GetBitmap(eval(items), wx.ART_TOOLBAR, (16, 16))
                #il.Add(bmp)
    
            #smileidx = il.Add(images.Smiles.GetBitmap())
            #numicons = il.GetImageCount()
    
            #self.AssignImageList(il)
            self.count = 0
            self.log = log
    
            # NOTE:  For some reason tree items have to have a data object in
            #        order to be sorted.  Since our compare just uses the labels
            #        we don't need any real data, so we'll just use None below for
            #        the item data.
    
            # create some columns        

            self.AddColumn("Наименование")
            
            self.AddColumn("Переменная")
            
            self.AddColumn("Значение")
            
            # Авторазмер столбца
            self.choices = [wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE_USEHEADER, wx.LIST_AUTOSIZE_USEHEADER]  # LIST_AUTOSIZE_USEHEADER | LIST_AUTOSIZE 
            
            # Скрыть корневой столбец
            self.SetAGWWindowStyleFlag(self.GetAGWWindowStyleFlag() | wx.TR_HIDE_ROOT)
            
            # Имя корня
            self.tree_name = ''
            
            self.branch = Branch(self, self.tree_name)
                    
            self.ud_tree()


            # Initialize the cursor position
            
            self.cursor= (-1, -1) 
    
            # Bind the Motion event 
            wx.EVT_MOTION(self, self.OnMotion)
            
            self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged)
            self.Bind(wx.EVT_TREE_SEL_CHANGING, self.OnSelChanging)

            #self.Bind(wx.EVT_MOTION, self.OnMotion)

        # Motion event handler to update the ToolTip 
        def OnMotion(self, event):
            self.locale = wx.Locale(wx.LANGUAGE_RUSSIAN)
            # Get cursor position 
            cursor= (event.GetX(), event.GetY()) 
            if cursor != self.cursor: 
                # True cursor displacement 
                (item, flags, column)= self.HitTest(cursor) 
                if flags == wx.TREE_HITTEST_ONITEMLABEL: 
                    # Over an item 
                    #self.SetToolTipString(self.GetItemText(item))
                    self.SetToolTip(self.GetItemText(item))
                elif flags == wx.TREE_HITTEST_NOWHERE : 
                    # Elsewhere 
                    #self.SetToolTipString('Подсказка о районе')
                    self.SetToolTip('Подсказка о районе') 
    
                # Update the cursor position 
                self.cursor= cursor
                
        def ud_tree(self):
            return Node(self.tree_name , self.branch)
        


        def OnSelChanging(self, event):
            self.item = event.GetItem()
            if self.item:
                if self.item.GetType() == 0 and self.item.GetChildrenCount() > 0:
                    #self.item.Collapse()
                    #self.item.Expand()
                    pass
                    
            #self.SetColumnWidth(0,  wx.LIST_AUTOSIZE)
            #self.SetColumnWidth(1,  wx.LIST_AUTOSIZE)
            #self.SetColumnWidth(2,  wx.LIST_AUTOSIZE)
            event.Skip()  
        
        def OnSelChanged(self, event):
    
            self.item = event.GetItem()
            #self.STT.stip.SetTarget(self.item)  # Подсказка
            if self.item:
                ##self.log.write("OnSelChanged: %s" % self.GetItemText(self.item))
                ##if self.GetItemText(self.item, 1) == '':
                    ##self.log.write("Ge1: %s" % self.GetItemText(self.GetItemParent(self.item), 1))
                ##else:
                    ##self.log.write("Ge2: %s" % self.GetItemText(self.item, 1))
                ##if wx.Platform == '__WXMSW__':
                    ##self.log.write(", BoundingRect: %s\n" % self.GetBoundingRect(self.item, True))

                ##else:
                    ##self.log.write("\n")
                if self.item.GetType() == 2:
                    # Чекбокс
                    parent = self.item.GetParent()
                    parent.SetText(2, str(self.item.GetText()+' ('+str(parent.GetChildren().index(self.item))+')'))
                
                    parent.Collapse()
                    for t_item in parent.GetChildren():
                        if t_item == self.item:
                            t_item.Set3StateValue(True)
                            t_item.SetText(2, 'TRUE')
                        else:
                            t_item.Set3StateValue(False)
                            t_item.SetText(2, 'FALSE')
                    
    
            event.Skip()        



    class MyFrame(wx.Frame):    
        def __init__(self, parent):
    
            wx.Frame.__init__(self, parent, -1)

            self.SetMinSize((840, 680))
            #self.SetIcon(images.Mondrian.GetIcon())
            self.SetTitle("Пользовательские умолчания")
    
            self.CenterOnParent()
    
            statusbar = self.CreateStatusBar(2)
            statusbar.SetStatusWidths([-2, -1])
            # statusbar fields
            statusbar_fields = [("Дерево пользовательских умолчаний, Александр Драгункин @ 22 Июля 2016"),
                                ("Добро пожаловать в wxPython!")]
    
            for i in range(len(statusbar_fields)):
                statusbar.SetStatusText(statusbar_fields[i], i)
    
            self.CreateMenuBar()
    
            #self.oldicons = 0
            
    
            sizer = wx.BoxSizer(wx.VERTICAL)            

            sizer.Layout()               


            sizer = wx.BoxSizer(wx.VERTICAL)
            self.tree = HyperTreeList(self, -1, log=Log())
            sizer.Add(self.tree, 1, wx.EXPAND)
            self.SetSizer(sizer)            
            
        def CreateMenuBar(self):
    
            file_menu = wx.Menu()
    
            AS_EXIT = wx.NewId()
            file_menu.Append(AS_EXIT, "&Выход")
            self.Bind(wx.EVT_MENU, self.OnClose, id=AS_EXIT)
    
            help_menu = wx.Menu()
    
            AS_ABOUT = wx.NewId()
            help_menu.Append(AS_ABOUT, "&About...")
            self.Bind(wx.EVT_MENU, self.OnAbout, id=AS_ABOUT)
    
            menu_bar = wx.MenuBar()
    
            menu_bar.Append(file_menu, "&Файл")
            menu_bar.Append(help_menu, "&Помощь")
    
            self.SetMenuBar(menu_bar)

        def OnClose(self, event):
    
            self.Destroy()
    
    
        def OnAbout(self, event):
    
            msg = "Диалог управления пользовательскими умлчаниями.\n\n" + \
                  "Автор: Александр Драгункин @ 22 Июля 2016\n\n" + \
                  "Пожалуйста направляйте Ваши замечания и предложения\n" + \
                  "На мой почтовый адрес:\n\n" + \
                  "            \n" + "dr69@bk.ru\n\n" + \
                  "Разработано с использованием wxPython " + wx.VERSION_STRING + "!!"
    
            dlg = wx.MessageDialog(self, msg, "Пользовательские умолчания",
                                   wx.OK | wx.ICON_INFORMATION)
    
            if wx.Platform != '__WXMAC__':
                dlg.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False))
    
            dlg.ShowModal()
            dlg.Destroy()


            
    # our normal wxApp-derived class, as usual
    
    app = wx.App(0)
    
    frame = MyFrame(None)
    
    app.SetTopWindow(frame)

    frame.Show()

    frame.tree.ExpandAll()
    
    for i in range(frame.tree.GetMainWindow().GetColumnCount()):
        frame.tree.SetColumnWidth(i, frame.tree.choices[i])
    #frame.tree.Collapse()
    app.MainLoop()

    
    app.Destroy()
    
    del(app)
    
if __name__ == '__main__':
    #test()
    gui()
    pass
    