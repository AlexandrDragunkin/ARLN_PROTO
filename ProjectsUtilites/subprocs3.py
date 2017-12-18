# -*- coding: utf-8 -*-
#import os, sys
import threading
#import win32process
import win32file, win32con, win32api
#import pywintypes

from ctypes import windll, Structure, sizeof, byref
from ctypes import c_int, c_ulong, c_char
#from ctypes import POINTER, WINFUNCTYPE
#from time import sleep
#####################################################################################

TH32CS_SNAPHEAPLIST = 0x01
TH32CS_SNAPPROCESS  = 0x02
TH32CS_SNAPTHREAD   = 0x04
TH32CS_SNAPMODULE   = 0x08
TH32CS_SNAPMODULE32 = 0x10
TH32CS_SNAPALL      = (TH32CS_SNAPHEAPLIST|TH32CS_SNAPPROCESS|TH32CS_SNAPTHREAD|TH32CS_SNAPMODULE)
TH32CS_INHERIT      = 0x80000000

INVALID_HANDLE_VALUE = 0
ERROR_SUCCESS        = 0
#####################################################################################

thelp_sema = threading.Semaphore()
#####################################################################################

## декларируем используемые функции WinAPI
CreateToolhelp32Snapshot = windll.kernel32.CreateToolhelp32Snapshot
Process32First           = windll.kernel32.Process32First
Process32Next            = windll.kernel32.Process32Next
GetCurrentProcessId      = windll.kernel32.GetCurrentProcessId
OpenProcess              = windll.kernel32.OpenProcess
TerminateProcess         = windll.kernel32.TerminateProcess
WaitForSingleObject      = windll.kernel32.WaitForSingleObject
EnumWindows              = windll.user32.EnumWindows
IsWindowVisible          = windll.user32.IsWindowVisible
GetDesktopWindow         = windll.user32.GetDesktopWindow
PostMessage              = windll.user32.PostMessageA
SendMessageTimeout       = windll.user32.SendMessageTimeoutA
#####################################################################################

class PROCESSENTRY32 (Structure) :
    _fields_ = [("dwSize", c_ulong),
                ("cntUsage", c_ulong),
                ("th32ProcessID", c_ulong),
                ("th32DefaultHeapID", c_ulong),
                ("th32ModuleID", c_ulong),
                ("cntThreads", c_ulong),
                ("th32ParentProcessID", c_ulong),
                ("pcPriClassBase", c_ulong),
                ("dwFlags", c_ulong),
                ("szexeFile", c_char * 260)]

class CSEARCH (Structure) :
    _fields_ = [("pid", c_ulong),
                ("wnd", c_ulong)]

def GetProcessList() :
    """ Возвращает список кортежей (Имя exe'шника, ID процесса, число потоков) """
    pe32 = PROCESSENTRY32()
    pe32.dwSize = sizeof(PROCESSENTRY32)

    result   = []
    thelp_sema.acquire()
    try :
        snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        flag     = Process32First(snapshot, byref(pe32))
        while flag :
            result.append((pe32.szexeFile, pe32.th32ProcessID, pe32.cntThreads))
            flag = Process32Next(snapshot, byref(pe32))
        win32file.CloseHandle(snapshot)
    finally :
        thelp_sema.release()
    return result

#list_process = GetProcessList()
#for f in sorted(list_process):
    #print(f)
#sf = lambda x: x[0]
#print(b'Mebel.exe' in  map(sf, list_process))
