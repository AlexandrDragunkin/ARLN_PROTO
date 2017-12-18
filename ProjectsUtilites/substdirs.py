# -*- coding: utf-8 -*-
"""
Выполняет поиск дирректорий и файлов

root = 'D:\\МАШИНГЛЮК\\А_ГЛЮК\\28\\Reports\\K3_Drafts\\'
sb = Substdirs()
sb(cdir=root)
sb(mask="*.k3")
"""

import os, fnmatch


class Substdirs:
    def __init__(self, **kwards ):
        for t in kwards:
            setattr(self, t, kwards[t])
    
    def __call__(self, **kwards):
        for t in kwards:
            setattr(self, t, kwards[t])

        if 'cdir' in self.__dict__:
            self.listfiles = self.getsubs()
            if 'mask' in self.__dict__:
                self.list_mask_files = self.getfilemask(self.listfiles[1],self.mask)


    def getsubs(self):
        '''Возвращает списки дирректорий и файлов расположенных в дирректории cdir'''
        dirs = []
        files = []
        for dirname, dirnames, filenames in os.walk(self.cdir):
            dirs.append(dirname)
            for subdirname in dirnames:
                dirs.append(os.path.join(dirname, subdirname))
            for filename in filenames:
                files.append(os.path.join(dirname, filename))
        return dirs, files
    
    def getsubdirs(self):
        '''Возвращает списки дирректорий  расположенных в дирректории cdir'''
        dirs = []
        for dirname, dirnames, filenames in os.walk(self.cdir):
            dirs.append(dirname)
            for subdirname in dirnames:
                dirs.append(os.path.join(dirname, subdirname))
        return dirs
    
    def getfilemask(self,f,mask):
        '''Возвращает список файлов удовлетворяющих mask из списка файлов f'''
        tt=[]
        for i in f:
            if fnmatch.fnmatch(i,mask):
                tt.append(i)
        return tt
    
    def getungfiles(self,listfiles):
        '''Находит в списке listfiles самый свежий файл'''
        tdatapr = None
        filename = None
        for i in listfiles:
            tdata = os.stat(i).st_mtime
            if  tdatapr is None:
                tdatapr = tdata
                filename = i
            elif tdatapr < tdata:
                tdatapr = tdata
                filename = i
        return filename



