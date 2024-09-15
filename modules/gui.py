import tkinter
from tkinter import ttk
from tkinter import messagebox
import tkinter.filedialog
import os
import sys
import multiprocessing

import modules.files_field
import modules.config_parser

"""
метод создания главного окна приложения
"""
attached_instruments = []
if os.path.isdir("instruments"):
    for m in os.listdir("instruments"):
        if os.path.splitext(m)[1] == '.py':
            try:
                exec("import  instruments.%s\nname = instruments.%s.App.__doc__" %(os.path.splitext(m)[0], os.path.splitext(m)[0]))
                attached_instruments.append([os.path.splitext(m)[0], name])
            except:
                pass

class GUI():
    def __init__(self, panels=2):
        """panels-количество файловых окон по дефолту"""
        self.instruments = attached_instruments #список подключенных модулей-инструментов
        self.panels = [] #окна файлов
        self.tabs = [] #вкладки
        self.cut = None #переменная для вырезания/вставки файла или каталога
        self.copy = None #для хранения копируемого файла
        #парсер, считывающий и сохраняющий значения опций в файл
        self.config = modules.config_parser.Parser("options.ini")
        #если файл конфигураций не найден
        if self.config.exist() == False:
            #создаю дефолтные настройки
            self.config.create_default()
        self.create_window()
        self.create_user_elements()
        self.create_window_menu()
        self.create_files_windows(panels)
        self.window.mainloop()

    def create_window(self):
        '''создаёт окно приложения'''
        self.window = tkinter.Tk()
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        self.window.title('DragmorCommander')
        try:
            self.window.wm_iconbitmap("images/icon.ico")
        except:
            pass

    def load_config(self): #-=----------------------------------------------------------------------------------------------------------------------
        pass


    def create_user_elements(self):
        '''метод расстановки пользовательских элементов'''
        #главный фрейм и разделитель окон
        self.main_frame = tkinter.Frame(self.window, padx=3, pady=3)
        self.delimiter = tkinter.PanedWindow(self.main_frame,
            opaqueresize=True, sashwidth=0, sashpad=2)
        self.delimiter.grid(sticky="w, n, e, s")
        self.main_frame.grid(sticky="w, n, e, s")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

    def create_files_windows(self, count=2):
        #метод создаёт файловые окна в количестве count
        for panel_id in range(count):
            self.tabs.append(ttk.Notebook())
            self.tabs[-1].enable_traversal()
            self.panels.append([modules.files_field.FilesField(self, tkinter.Frame(), panel_id)])
            self.tabs[-1].add(self.panels[-1][-1].frame)
            self.tabs[-1].grid()
            #разделитель
            self.delimiter.add(self.tabs[-1]) 
            self.panels[-1][0].show_dir()
            self.panels[-1][0].hide_selections()
        self.panels[0][0].unhide_selections()
        self.panels[0][0].field.focus_set()

    def add_tab(self, index=0, path=None):
        '''метод добавляет новую вкладку'''
        if path == None:
            path = self.panels[index][self.tabs[index].index("current")].file_manager.path
        self.panels[index].append(modules.files_field.FilesField(self, frame=tkinter.Frame(), index=index, path=path))
        self.tabs[index].add(self.panels[index][-1].frame)
        self.tabs[index].select(len(self.tabs[index].tabs())-1)
        self.panels[index][-1].show_dir()
        #ставлю фокус на открытую вкладку
        self.panels[index][self.tabs[index].index("current")].field.focus_set()
        self.panels[index][self.tabs[index].index("current")].field.event_generate("<KeyPress-space>") 

    def close_tab(self, index=0, x=0, y=0):
        '''метод вызывается при щелчке СКМ по вкладке.
        закрывает вкладку, высвобождает ресурсы'''
        
        #генерирую клик мыши по панели, что-бы установить фокус на вкладке
        self.tabs[index].event_generate("<Button-1>", x=x, y=y)
        #если вкладка всего одна, не закрываю её
        if len(self.tabs[index].tabs()) <= 1:
            return
        #удаляю вкладку (и некоторые объекты)
        temp = self.panels[index][self.tabs[index].index("current")] #ссылка на объект
        del self.panels[index][self.tabs[index].index("current")] #удаляю из списка вкладок
        self.tabs[index].forget(self.tabs[index].index("current")) #удаляю вкладку
        temp.frame.destroy()
        del temp.file_manager
        del temp

    def update_panels(self):
        '''метод обновляет содержимое всех файловых
        окон во всех вкладках'''
        #прохожусь по списку списков панелей
        for panel in self.panels:
            #прохожусь по конкретным панелям
            for current in panel:
                #обновляю содержимое
                current.show_dir()

    def create_window_menu(self):
        '''метод задаёт верхнее меню программы'''
        #само меню
        self.menu = tkinter.Menu(self.main_frame)

        #выпадающие кнопки меню
        self.cascade_files = tkinter.Menu(self.menu, tearoff=0)
        self.cascade_view = tkinter.Menu(self.menu, tearoff=0)
        self.cascade_tools = tkinter.Menu(self.menu, tearoff=0)
        self.cascade_help = tkinter.Menu(self.menu, tearoff=0)
        #добавляю кнопки

        #меню ФАЙЛ
        self.menu.add_cascade(label='Файлы', menu=self.cascade_files)
        self.cascade_files.add_command(label='Создать файл',
                 command=sys.exit)
        self.cascade_files.add_separator()
        self.cascade_files.add_command(label='Выйти',
                 command=sys.exit)

        #Инструменты
        #если были заимпортированы инструменты, добавляю в меню соответствующий выпадающий список
        if self.instruments != []:
            self.menu.add_cascade(label='Инструменты', menu=self.cascade_tools) 
            for inst in self.instruments:
                self.cascade_tools.add_command(label=inst[1],
                         command=(lambda self=self, instrument=inst[0]: self.run_instrumente(instrument)))

        #Вид
        self.menu.add_cascade(label='Вид', menu=self.cascade_view)
        self.cascade_view.add_command(label='Настройки цветов',
                 command=sys.exit)
        #Помощь
        self.menu.add_cascade(label='Помощь', menu=self.cascade_help)
        self.cascade_help.add_command(label='Горячие клавиши',
                 command=sys.exit)
        self.cascade_help.add_command(label='Авторы',
                 command=sys.exit)
        self.window.config(menu=self.menu)

    def switch_focus_left(self, index, mode=0):
        '''метод переводит фокус на левое окно, либо на правое,
        если левое и так уже крайнее. Если mode=0, то переключается файловое окно.
        Если-же mode!=0 то переключается вкладка на панели. Через ctrl+стрелки переключаются вкладки'''
        #переключение файловых окон
        if mode == 0:
            if index == 0:
                self.panels[0][self.tabs[0].index("current")].hide_selections()
                self.panels[-1][self.tabs[-1].index("current")].unhide_selections()
                self.panels[-1][self.tabs[-1].index("current")].field.focus_set()
                self.panels[-1][self.tabs[-1].index("current")].field.event_generate("<KeyPress-space>")  
            else:
                self.panels[index][self.tabs[index].index("current")].hide_selections()
                self.panels[index-1][self.tabs[index-1].index("current")].unhide_selections()
                self.panels[index-1][self.tabs[index-1].index("current")].field.focus_set()
                self.panels[index-1][self.tabs[index-1].index("current")].field.event_generate("<KeyPress-space>")
        #переключение вкладок
        else:
            if self.tabs[index].index("current") != 0:
                self.tabs[index].select(self.tabs[index].index("current")-1)
                #ставлю фокус на открытую вкладку
                self.panels[index][self.tabs[index].index("current")].field.focus_set()
                self.panels[index][self.tabs[index].index("current")].field.event_generate("<KeyPress-space>") 
            else:
                self.tabs[index].select(len(self.tabs[index].tabs())-1)
                #ставлю фокус на открытую вкладку
                self.panels[index][self.tabs[index].index("current")].field.focus_set()
                self.panels[index][self.tabs[index].index("current")].field.event_generate("<KeyPress-space>") 


    def switch_focus_right(self, index, mode=0):
        '''метод переводит фокус на правое окно. Аналогично методу switch_focus_left,
        но переключение идёт в противоположную сторону'''
        #переключение файловых окон
        if mode == 0:
            if index+1 == len(self.panels):
                self.panels[0][self.tabs[0].index("current")].field.focus_set()
                self.panels[0][self.tabs[0].index("current")].field.event_generate("<KeyPress-space>")  
                self.panels[-1][self.tabs[-1].index("current")].hide_selections()
                self.panels[0][self.tabs[0].index("current")].unhide_selections()

            else:
                self.panels[index+1][self.tabs[index+1].index("current")].field.focus_set()
                self.panels[index+1][self.tabs[index+1].index("current")].field.event_generate("<KeyPress-space>")
                self.panels[index][self.tabs[index].index("current")].hide_selections()
                self.panels[index+1][self.tabs[index+1].index("current")].unhide_selections()

        #переключение вкладок
        else:
            if self.tabs[index].index("current") == len(self.tabs[index].tabs())-1:
                self.tabs[index].select(0)
                #ставлю фокус на открытую вкладку
                self.panels[index][self.tabs[index].index(0)].field.focus_set()
                self.panels[index][self.tabs[index].index(0)].field.event_generate("<KeyPress-space>") 
            else:
                self.tabs[index].select(self.tabs[index].index("current")+1)
                #ставлю фокус на открытую вкладку
                self.panels[index][self.tabs[index].index("current")].field.focus_set()
                self.panels[index][self.tabs[index].index("current")].field.event_generate("<KeyPress-space>") 

    def run_instrumente(self, instrument, args=''):
        '''метод запускает модуль в отдельном процессе'''
        try:
            if args=='':
                args=None
            else:
                args = args.split(os.sep) #разбиваю путь, что бы символы обратного слэша не искажались
            process = multiprocessing.Process(target=exec, args=('import  instruments.%s\napp=instruments.%s.App(%s)' %(instrument, instrument, args),))
            process.daemon = False
            process.start()
        except:
            tkinter.messagebox.showerror(title='Ошибка запуска', message='Не удалось запустить инструмент "%s"!' %(instrument))
