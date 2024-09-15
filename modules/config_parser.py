import os

"""парсит значения из конфигурационного файла"""
class Parser():
    def __init__(self, filename="options.ini"):
        self.file = filename

    def get_value(self, option_name=""):
        '''возвращает значение опции, чьё имя передано в параметре.
        Если не найдено, возвращает False'''
        pass

    def write_value(self, option_name="", value=""):
        '''записывает значение опции в файл'''
        pass

    def exist(self):
        """проверяет, существует-ли файл настроек. Если да,
        возвращает True. Иначе False"""
        if os.path.exists(self.file) and os.path.isfile(self.file):
            return True
        else:
            return False

    def create_default(self):
        '''метод создаёт файл с дефолтными настройками'''
        pass

    def read(self):
        '''считывает конфигурационный файл в ОЗУ в виде
        словаря КЛЮЧ-ЗНАЧЕНИЕ'''
        pass