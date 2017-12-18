# -*- coding: cp1251 -*-

def printerable(aClass):
  class Wrapper(aClass):
    """
    Этот декоратор нужен для того, чтобы по команде print (<Class>)
    выводился не просто адрес этого класса, а нормальная членораздельная
    информация. Будут выводиться список методов класса, значения полей и пр.
    """
    def __init__(self,*args,**kwargs):
      aClass.__init__(self,*args,**kwargs)
      self.wrapped=aClass(*args,**kwargs)
    def __getattr__(self,attrname):
      return getattr(self.wrapped,attrname)

    def __str__(self):
      self.__visited = {}
      #strin='\n<Экземпляр класса {0}, адрес {1}:\n""{2}""\n{3}{4}>'.format(
      #                    self.wrapped.__class__.__name__,
      #                    id(self.wrapped),   
      #                    self.wrapped.__class__.__doc__,                     
      #                    self.__attrnames(self.wrapped, 0),
      #                    self.__listclass(self.wrapped.__class__, 4))
      strin='\n<Экземпляр класса {0}, адрес {1}:\n\"{2}\"\n{3}{4}>'.format(
                          self.wrapped.__class__.__name__,
                          id(self.wrapped),   
                          self.wrapped.__class__.__doc__,                     
                          self.__attrnames(self, 0),
                          self.__listclass(self.__class__, 4))
      return strin

    def __listclass(self, aClass, indent):
      if (aClass.__name__=="object"):
        return ""
      if (aClass.__name__=="Wrapper"):
        genabove = (self.__listclass(c, indent+2) for c in aClass.__bases__)
        return ''.join(genabove)
      dots = '.' * indent
      if aClass in self.__visited:
        return '\n{0}<Класс {1}:, адрес {2}: (см. выше)>\n'.format(
                        dots,
                        aClass.__name__,
                        id(aClass))
      else:
        self.__visited[aClass] = True
        genabove = (self.__listclass(c, indent+2) for c in aClass.__bases__)
        return '\n{0}<Класс {1}, адрес {2}:\n{3}{4}{5}>\n'.format(
                        dots,
                        aClass.__name__,
                        id(aClass),
                        self.__attrnames(aClass, indent),
                        ''.join(genabove),
                        dots)

    def __attrnames(self, obj, indent):
      spaces = ' ' * (indent + 2)
      result = ''
      for attr in sorted(obj.__dict__):
        if (not(attr.startswith('__') and attr.endswith('__')) and attr!="wrapped" and attr!="_Wrapper__visited"):
          result += spaces + '{0}={1}\n'.format(attr, getattr(obj, attr))
      return result
  return Wrapper