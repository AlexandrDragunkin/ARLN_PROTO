# -*- coding: utf-8 -*-
import os, fnmatch, k3
# import wingdbstub
mask = '*.k3'
pattern = ''
filesT = []

def walk(dir,files):
   for file in files:
      if fnmatch.fnmatch(file,mask):
         name = os.path.join(dir,file)
         try:
            if len(pattern)>0:
               data = open(name,'rb').read()
               if data.find(pattern) != -1:
                     print(name)
                     filesT.append(name)
            else:
               filesT.append(name)
         except:
            pass
tree = os.walk('d:\\tmp\\caddata_DAE\\')
for t in tree:
   walk(t[0], t[2])


i=0
for nfile in filesT[2090:]:
   k3.new()
   k3.open(nfile)
   k3.setucs(k3.k_gcs)
   k3.setucs(0, 0, 0,
             -1, 0, 0,
             0, 0, 1)
   tg = k3.group(k3.k_all, k3.k_done)
   k3.setucs(k3.k_gcs)
   k3.place(tg[0])
   k3.explode(tg[0])
   
   k3.vport(4)
   k3.rendmode(4, 2)
   k3.picture(4,k3.k_yes)
   k3.save(k3.k_all,nfile,k3.k_overwrite)
   print('Сохранили: ', i, nfile)
   i = i + 1
