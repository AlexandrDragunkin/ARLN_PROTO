# -*- coding: utf-8 -*-

import machine

s = machine.Settings()
'''
    Settings - Класс предоставляет доступ к настройкам приложения, например размер рабочей области станка.
  Свойства класса:
        machine_name - Имя класса, который будет генерировать команды для станка.
        machine_module_name - Имя файла в котором находится реализация станка.
        database_name - Путь к базе данных выгрузки.
        cmdfile_path - Имя генерируемого командного файла.
        working_area - BoundingBox2d определяющий рабочую область станка.

'''

s.machine_name = 'Boa'
s.machine_module_name = 'LivraPD4_bA'


class GuiOutput:
    def __init__(self):
        import sys
        self.stdout = sys.stdout
        sys.stdout = self

    def write(self, text):
        machine.message(text)

