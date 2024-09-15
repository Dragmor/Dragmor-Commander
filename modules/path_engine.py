"""модуль для управления координацией по ФС. Большая часть методов
возвращает список элементов каталога.
"""
import os

class FileManager():
    '''класс реализует управление по ФС'''
    def __init__(self, path=None):
        self.objects = []
        self.files_in_dir = 0
        self.dirs_in_dir = 0
        if path == None:
            self.path = os.getcwd()
        else:
            self.path = path

    def set_dir(self, path):
        '''метод для смены текущего каталога.
        Возвращает True, если каталог успешно выбран, или
        False в противном случае'''
        try:
            os.scandir(path)
        except:
            return False
        else:
            self.path = path
            return True

    def refresh(self):
        '''метод возвращает список элементов текущего каталога'''
        dirs = []
        files = [] 
        for obj in os.scandir(self.path):
            if obj.is_dir():
                stat = obj.stat()
                #тип, имя каталога, размер (-1 для сортировки), дата изменения
                dirs.append(["d", obj.name, -1, stat.st_mtime])
            elif obj.is_file():
                stat = obj.stat()
                #имя, размер, дата изменения
                files.append(["f", obj.name, stat.st_size, stat.st_mtime])
        #
        self.files_in_dir = len(files)
        self.dirs_in_dir = len(dirs)
        #
        self.objects = []
        for obj in dirs:
            self.objects.append(obj)
        for obj in files:
            self.objects.append(obj)
        return self.objects

    def get_drives(self):
        '''метод возвращает список букв доступных дисков'''
        drives = [os.path.sep]
        for drive in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            if os.path.lexists("%s:%s" %(drive, os.path.sep)):
                drives.append("%s:%s" %(drive, os.path.sep))
        return drives
