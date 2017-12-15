import winreg, os
from winreg import HKEY_LOCAL_MACHINE, HKEY_CURRENT_USER, HKEY_CLASSES_ROOT,\
    HKEY_CURRENT_CONFIG, HKEY_DYN_DATA, HKEY_PERFORMANCE_DATA, HKEY_USERS

hk2text = {
    HKEY_LOCAL_MACHINE: 'HKEY_LOCAL_MACHINE',
    HKEY_CURRENT_USER: 'HKEY_CURRENT_USER',
    HKEY_CLASSES_ROOT: 'HKEY_CLASSES_ROOT',
    HKEY_CURRENT_CONFIG: 'HKEY_CURRENT_CONFIG',
    HKEY_DYN_DATA: 'HKEY_DYN_DATA',
    HKEY_PERFORMANCE_DATA: 'HKEY_PERFORMANCE_DATA',
    HKEY_USERS: 'HKEY_USERS',
}

class Winreg:
    def __init__(self, root=None, location=''):
        self.__dict__['location'] = location
        self.__dict__['root'] = root
    def __getattr__(self, location):
        return Winreg(self.__dict__['root'], os.path.join(self.__dict__['location'], location))
    def __getitem__(self, location):
        return Winreg(self.__dict__['root'], os.path.join(self.__dict__['location'], location))
    def __setattr__(self, location, value):
        self.__setValue(location, value)
        return value
    def __setitem__(self, location, val):
        self.__setValue(location, value)
        return value
    def __str__(self):
        return str(self.__getValue())
    def __setValue(self, location, value):
        if isinstance(value, dict):
            winreg.CreateKey(self.__dict__['root'], os.path.join(self.__dict__['location'], location))
        elif isinstance(value, str):
            key = winreg.CreateKey(self.__dict__['root'], self.__dict__['location'])
            winreg.SetValueEx(key, location, 0, winreg.REG_SZ, value)
        elif isinstance(value, int):
            key = winreg.CreateKey(self.__dict__['root'], self.__dict__['location'])
            winreg.SetValueEx(key, location, 0, winreg.REG_DWORD, value)
        else:
            raise TypeError("valid types: dict, unicode, int")
    def __getValue(self):
        try:
            a,b = os.path.split(self.__dict__['location'])
            key = winreg.OpenKey(self.__dict__['root'], a)
            v = winreg.QueryValueEx(key, b)
            return v[0]
        except WindowsError as e:
            if e.winerror == 2:
                raise WindowsError(e.winerror, 'Value not found: '+self.__repr__())
            else:
                raise WindowsError(e.winerror, self.__repr__())
    def __int__(self):
        return int(self.__getValue())
    def __coerce__(self, other):
        return self.__getValue(), other
    def __repr__(self):
        return 'Winreg(winreg.%s, r"%s")'%(hk2text[self.__dict__['root']], self.__dict__['location'])

def keys(reg):
    key = winreg.OpenKey(reg.__dict__['root'], reg.__dict__['location'])
    class RegKeysIterator:
        current = 0
        def __iter__(self):
            return self
        def __next__(self):
            try:
                v = reg[winreg.EnumKey(key, self.current)]
                self.current += 1
            except WindowsError as e:
                if e.winerror == 259:
                    raise StopIteration
                else:
                    raise
            return v
    return RegKeysIterator()

def values(reg):
    key = winreg.OpenKey(reg.__dict__['root'], reg.__dict__['location'])
    class RegValuesIterator:
        current = 0
        def __iter__(self):
            return self
        def __next__(self):
            try:
                v = winreg.EnumValue(key, self.current)[:2]
                self.current += 1
                return v
            except WindowsError as e:
                if e.winerror == 259:
                    raise StopIteration
                else:
                    raise
    return RegValuesIterator()

def delete(reg):
    a,b = os.path.split(reg.__dict__['location'])
    try:
        key = winreg.OpenKey(reg.__dict__['root'], a, 0, winreg.KEY_WRITE)
        try:
            winreg.DeleteValue(key, b)
        except:
            winreg.DeleteKey(key, b)
    except WindowsError as e:
        raise WindowsError(e.winerror, 'Can not delete: ' + reg.__repr__())