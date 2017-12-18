# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:        DynaplanSupport
# Purpose:     Модуль интеграции BlumDynalog&K3_Mebel
#
# Author:      Aleksandr Dragunkin
#
# Created:     25.12.2012-07.05.2013
# Copyright:   (c) GEOS 2012-13 http://k3info.ru/
# Licence:     FREE
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import pickle
#import wingdbstub
import os, fnmatch, zipfile, base64, datetime, time, k3
from winreg_l import *
import subprocess as SubS
from SingletonMetaClass import Singleton
#   Dynalog
#------------------------------------------------------------------------------
#ProtoPath = k3.mpathexpand('<proto>')
CadDataPath = k3.mpathexpand('<K3Files>')
APPDATA = k3.mpathexpand('<appdata>')



class Dynalog(Singleton):
    '''Класс для работы с программами BLUM'''
    def __init__(self):
        self.path = None
        self.version = None
        self.caddata = []
        self.USERPROFILE = None
        self.rootNameFile = None
        self.set_files_and_pathes()
        
    def __call__(self):
        self.set_files_and_pathes()
        
    def set_files_and_pathes(self):
        self.RegPathDynalog = self.FindRegPathDynalog()
        #self.caddata_path = self.path + '\\PBilder\\CAD\\'
        self.caddata_path = CadDataPath + '\\Dynaplan\\'
        self.caddata = self.Find3DModelsZIP('*_K3_')
        self.stldata = self.Find3DModelsZIP('*_STL_')
        err = self.FindUserProfileWindows()
        self.FindProjectsFolder()
        self.listZipFile = {}
        #listFiles = getsubs(self.USERPROFILE+'\Documents\Blum\Dynaplan\Kommissionen\Pool\\')
        listFiles = getsubs(self.projectFolder)
        listBXF= getfilemask(listFiles[1],'*.bxf')
        self.infilename = getungfiles(listBXF)
        #self.projectFolder = self.USERPROFILE+'\Documents\Blum\Dynaplan\Kommissionen\Pool\\'
        #self.projectFolder = self.USERPROFILE+str('\Мои документы\Blum\Dynaplan\Kommissionen\Pool\\')
        lF = getsubs(self.projectFolder)
        lB =  getfilemask(lF[1],'*.bxf')
        self.listExtensionRoot = []
        if len(lB)>0:
            lRB = getungfiles(lB)
            tlRB = lRB.split('\\')
            tlRB.reverse()
            self.rootNameFile = tlRB[0][:-4]
            self.listRootFile = getfilemask(lF[1],'*\\'+self.rootNameFile+'.*')
            for i in self.listRootFile:
                self.listExtensionRoot.append(i.split('.')[1])
        else:
            print('None Files')

    #------------------------------------------------------------------------------
    def FindProjectsFolder(self):
        self.projectFolder = ''
        D = self.LoaderPickle()
        if len(D) > 0:
            if os.path.exists(D[0]):
                lf = getsubs(D[0])
                if len(lf[0]) > 0:                
                    self.projectFolder = D[0]

        if len(self.projectFolder) < 5:
            listdirs = getsubdirs(self.USERPROFILE)
            for l in listdirs:
                if '\Blum\Dynaplan\Kommissionen\Pool' in l :
                    index = l.find('\Blum\Dynaplan\Kommissionen\Pool')
                    self.projectFolder = l[:index] + '\Blum\Dynaplan\Kommissionen\Pool\\'
                    key = False
                    break
            if len(self.projectFolder) < 5:
                k3.putmsg(str('Отсутствует дирректория ..\Blum\Dynaplan\Kommissionen\Pool\\'), 0)
            else:
                self.DumperPickle([self.projectFolder])
    #------------------------------------------------------------------------------
    def FindFileMaskInZip(self,nameZipFile,mask=''):
        '''Возвращает список файлов из архива с именем nameZipFile удовлетворяющему
        маске mask '''
        tt = []
        if not nameZipFile in list(self.listZipFile.keys()):
            f = zipfile.ZipFile(nameZipFile)
            self.listZipFile[nameZipFile] = f.namelist()
        if mask in  self.listZipFile[nameZipFile]:
            tt.append(mask)
        return tt

#------------------------------------------------------------------------------
    def FindRegPathDynalog(self):
        '''Находит в реестре WINDOWS путь к установленной программе Dynalog
        и версию программы
        Если путь найден возвращает ИСТИНА
        Если путь не найден возвращает ЛОЖЬ'''
        dynalog_path = ''
        reg_Finder = Winreg(HKEY_CURRENT_USER, 'SOFTWARE\\BLUM\\Dynalog')
        try:
            self.path = str(reg_Finder.Maindir)
            self.version = str(reg_Finder.Version)
            return True
        except WindowsError as e:
            reg_Finder = Winreg(HKEY_LOCAL_MACHINE, 'SOFTWARE\\BLUM\\Dynalog')
            try:
                self.path = str(reg_Finder.Maindir)
                self.version = str(reg_Finder.Version)
                return True
            except WindowsError as e:
                print(e)
                return False

    #os.system(dynalog_path+"\\dynalog.exe")
#------------------------------------------------------------------------------
    def FindUserProfileWindows(self):
        '''Находит путь к папке текущего пользователя'''
        reg_Finder = Winreg(HKEY_CURRENT_USER, 'Volatile Environment')
##        self.USERPROFILE = str(reg_Finder.USERPROFILE)
        self.USERPROFILE = os.getenv('USERPROFILE')
        return True
#------------------------------------------------------------------------------
    def Find3DModelsZIP(self,inmask=''):
        '''Возвращает список файлов удовлетворяющих версии'''
        filesT = []
        pos = self.version.find(' ')
        mask = inmask+(self.version[:pos]).replace('.','-')+'.zip'
        #print mask
        files = os.listdir(self.caddata_path)
        for file in files:
            if fnmatch.fnmatch(file,mask):
                filesT.append(os.path.join(self.caddata_path,file))
        return filesT
#------------------------------------------------------------------------------
    def DumperPickle(self, pan):
        '''пишет объекты из списка pan в файл'''
        filer = open(APPDATA + '\DYNAPLAN.pcl', "wb")
        fil = pickle.dump(pan,filer)
        filer.close()

    def LoaderPickle(self):
        '''Читает объекты из файла'''

        def _loader_pcl(pkl_file):
            pn = pickle.load(pkl_file)
            pkl_file.close()
            return pn

        fname = APPDATA + '\DYNAPLAN.pcl'
        if k3.fileexist(fname)>0:
            pkl_file = open(fname, 'rb')
            try:
                return _loader_pcl(pkl_file)
            except:
                try:
                    pkl_file.close()
                except:
                    pass
                err = k3.removefile(fname)
                return []
        else:
            return []
    
    def deletePicle(self):
        """Удаляет файл"""
        fname = APPDATA + '\DYNAPLAN.pcl'
        if k3.fileexist(fname)>0:
            try:
                k3.removefile(fname)
            except:
                print('Не смог удалить файл ', fname)
                return False
        return True

#------------------------------------------------------------------------------
def findAttributIn(holder = None, Nm = ''):
    '''Ищет есть ли у объекта holder атрибуты.
    Если есть, то
        если задано имя искомого Nm и такое имя определено возвращает значение.
        или возвращает словарь атрибутов'''
    try:
        dh = holder.__dict__
        if 'Attribut' in dh:
            dc = {}
            for i in holder.Attribut:
                dc[i.Name] = i.valueOf_
            if Nm in dc:
                return dc[Nm]
            return dc
        else:
            print('Нет такого атрибута')

    except:
        print('Ошибка ')
#------------------------------------------------------------------------------
def getsubs(dir):
    '''Возвращает списки дирректорий и файлов расположенных в дирректории dir'''
    # get all
    dirs = []
    files = []
    for dirname, dirnames, filenames in os.walk(dir):
        dirs.append(dirname)
        for subdirname in dirnames:
            dirs.append(os.path.join(dirname, subdirname))
        for filename in filenames:
            files.append(os.path.join(dirname, filename))
    return dirs, files
#------------------------------------------------------------------------------
def getsubdirs(dir):
    '''Возвращает списки дирректорий  расположенных в дирректории dir'''
    # get all
    dirs = []
    files = []
    for dirname, dirnames, filenames in os.walk(dir):
        dirs.append(dirname)
        for subdirname in dirnames:
            dirs.append(os.path.join(dirname, subdirname))
    return dirs
#------------------------------------------------------------------------------
def getfilemask(f,mask):
    '''Возвращает список файлов удовлетворяющих mask из списка файлов f'''
    tt=[]
    for i in f:
        if fnmatch.fnmatch(i,mask):
            tt.append(i)
    return tt
#------------------------------------------------------------------------------
def getungfiles(listfiles):
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
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def impProjectFilesToStr(rootFolder = None,rootname=None, listext=[]):
    '''Возвращает списки строк из бинарных файлов с именем rootname и расширениями  listext'''
    listFiles = []
    for i in listext:
        tt = []
        filer = open(rootFolder + rootname + '.' + i, "rb")
        while True:
            buff = filer.read(176)
            if len(buff) > 0:
                string = base64.b64encode(buff) # base64 кодирование
                tt.append(string)
            else: break # EOF
        filer.close()
        listFiles.append(tt)
    return listFiles
#------------------------------------------------------------------------------
def expProjectFilesToStr(rootFolder = None,rootname=None, listobject = [],listext=[]):
    '''Преобразует текстовый атрибут в файл и запускает DYNAPLAN
    Возвращает '''
    listFiles = []
    for i,BaseV in zip(listext,listobject):
        tt = []
        filer = open(rootFolder + rootname + '.' + i, "wb")
        for buff in BaseV:
            if len(buff) > 0:
                string = base64.b64decode(buff) # base64 декодирование
                filer.write(string)

        filer.close()
    dt_st = datetime.datetime.now() # Фиксируем текущее время
    dt_start = time.mktime(dt_st.timetuple())
    DynaplanStart(dynalog.projectFolder+rootname+'.bpf')
    # После окончания работы внешней программы надо проверить были ли внесены изменения в проект
    #ggg=getsubs(dynalog.USERPROFILE+'\Documents\Blum\Dynaplan\Kommissionen\Pool\\')
    #ggg=getsubs(dynalog.USERPROFILE+str('\Мои документы\Blum\Dynaplan\Kommissionen\Pool\\'))
    ggg=getsubs(dynalog.projectFolder)
    ss=getfilemask(ggg[1],'*.bxf')
    tt = getungfiles(ss)
    dt_end = os.stat(tt).st_mtime
    #print dt_end,'   ',dt_start
    #print 'dt_end-dt_start ',dt_end-dt_start
    return dt_end-dt_start>2
#------------------------------------------------------------------------------
def DynaplanStart(startfile=''):
    '''Запускает Dynaplan'''
    #print(startfile)
    SubS.call([dynalog.path + '\\Dynaplan\\Dynaplan.exe',startfile,'-icon', 'DP_bbn_Main_K3'])

def DynaplanStartBXF(startfile=''):
    '''Запускает Dynaplan'''
    dt_start = os.stat(startfile).st_mtime
    SubS.call([dynalog.path + '\\Dynaplan\\Dynaplan.exe','-f',startfile])
    dt_end = os.stat(startfile).st_mtime
    return dt_end-dt_start>2

dynalog=Dynalog()
def main():
##    dynalog=Dynalog()
##    lstF = []
##    ggg=getsubs(dynalog.USERPROFILE+'\Documents\Blum\Dynaplan\Export\\')
##    ss=getfilemask(ggg[1],'*.bxf')
##    getungfiles(ss)
##    global lstF
##    lstF = impProjectFilesToStr(dynalog.projectFolder,dynalog.rootNameFile,dynalog.listExtensionRoot)
##    print lstF
##    expProjectFilesToStr(dynalog.projectFolder,'shkaf',lstF,dynalog.listExtensionRoot)
##    subprocess.call([dynalog.path + '\\Dynaplan\\Dynaplan.exe',dynalog.projectFolder+'shkaf.bpf'])
    print('ok')



if __name__ == '__main__':
    main()
