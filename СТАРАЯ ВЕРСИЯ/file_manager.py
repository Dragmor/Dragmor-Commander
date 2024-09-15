'''графический файловый менеджер'''
import tkinter
from tkinter import ttk
from tkinter import messagebox
import tkinter.filedialog
import os
import subprocess
import glob
import shutil
import multiprocessing
import time


instruments = []
if os.path.isdir("modules"):
    for m in os.listdir("modules"):
        if os.path.splitext(m)[1] == '.py':
            try:
                exec("import  modules.%s\nname = modules.%s.App.__doc__" %(os.path.splitext(m)[0], os.path.splitext(m)[0]))
                instruments.append([os.path.splitext(m)[0], name])
            except:
                pass
print(instruments)

class GUI():
    def __init__(self):
        #устанавливаю стандартные цвета
        self.dirs_color = 'green'
        #
        self.cut = None #переменная для вырезания/вставки файла или каталога
        self.copy = None #для хранения копируемого файла
        self.load_instruments()
        self.create_window()
        self.create_user_elements()
        self.window.mainloop()

    def load_instruments(self):
        '''загружаю доступные модули инструментов в список'''
        self.instruments = instruments    

    def run_instrumente(self, instrument, args=''):
        '''метод запускает модуль в отдельном процессе'''
        try:
            if args=='':
                args=None
            else:
                args = args.split(os.sep) #разбиваю путь, что бы символы обратного слэша не искажались
            process = multiprocessing.Process(target=exec, args=('import  modules.%s\napp=modules.%s.App(%s)' %(instrument, instrument, args),))
            process.daemon = False
            process.start()
        except:
            tkinter.messagebox.showerror(title='Ошибка запуска', message='Не удалось запустить инструмент "%s"!' %(instrument))

    def create_window(self):
        self.window = tkinter.Tk()
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        self.window.title('DragmorCommander')

    def create_user_elements(self):
        #главный фрейм и разделитель окон
        self.main_frame = tkinter.Frame(self.window, padx=3, pady=3)
        self.delimiter = tkinter.PanedWindow(self.main_frame,
            opaqueresize=True, sashwidth=0, sashpad=2)
        self.delimiter.grid(sticky="w, n, e, s")
        self.main_frame.grid(sticky="w, n, e, s")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        #меню
        self.menu = tkinter.Menu(self.main_frame)
        #выпадающие кнопки меню
        self.cascade_files = tkinter.Menu(self.menu, tearoff=0)
        self.cascade_view = tkinter.Menu(self.menu, tearoff=0)
        self.cascade_tools = tkinter.Menu(self.menu, tearoff=0)
        self.cascade_help = tkinter.Menu(self.menu, tearoff=0)
        #добавляю кнопки
        #
        self.menu.add_cascade(label='Файлы', menu=self.cascade_files)
        self.cascade_files.add_command(label='Создать файл',
                 command=exit)
        self.cascade_files.add_separator()
        self.cascade_files.add_command(label='Выйти',
                 command=exit)
        #заполняю каскад инструментов найденными модулями
        self.menu.add_cascade(label='Инструменты', menu=self.cascade_tools)
        for inst in self.instruments:
            self.cascade_tools.add_command(label=inst[1],
                     command=(lambda self=self, instrument=inst[0]: self.run_instrumente(instrument)))
        #Вид
        self.menu.add_cascade(label='Вид', menu=self.cascade_view)
        self.cascade_view.add_command(label='Настройки цветов',
                 command=exit)
        #
        self.menu.add_cascade(label='Помощь', menu=self.cascade_help)
        self.cascade_help.add_command(label='Горячие клавиши',
                 command=exit)
        self.cascade_help.add_command(label='Авторы',
                 command=exit)
        self.window.config(menu=self.menu)
        #
        #создаю панели файлов
        self.panels = []
        self.tabs = [] #вкладки
        for panels in range(2): # 2 - количество панелей
            self.tabs.append(ttk.Notebook())
            self.tabs[-1].enable_traversal()
            self.panels.append([FilesField(self, tkinter.Frame(), panels)])
            self.tabs[-1].add(self.panels[-1][-1].frame)
            self.tabs[-1].grid()
            #разделитель
            self.delimiter.add(self.tabs[-1]) 
            self.panels[-1][-1].show_dir()
        self.panels[0][0].field.focus_set()

    def switch_focus_left(self, index, mode=0):
        '''метод переводит фокус на левое окно, либо на правое,
        если левое и так уже крайнее. Если mode=0, то переключается файловое окно.
        Если-же mode!=0 то переключается вкладка на панели. Через ctrl+стрелки переключаются вкладки'''
        #переключение файловых окон
        if mode == 0:
            if index == 0:
                self.panels[-1][self.tabs[index-1].index("current")].field.focus_set()
                self.panels[-1][self.tabs[index-1].index("current")].field.event_generate("<KeyPress-space>")  
            else:
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
            else:
                self.panels[index+1][self.tabs[index+1].index("current")].field.focus_set()
                self.panels[index+1][self.tabs[index+1].index("current")].field.event_generate("<KeyPress-space>")
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

    def close_tab(self, index=0, x=0, y=0):
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
        del temp.files
        del temp

    def add_tab(self, index=0, path=None):
        '''метод добавляет новую вкладку'''
        if path == None:
            path = self.panels[index][self.tabs[index].index("current")].files.path.get()
        self.panels[index].append(FilesField(self, frame=tkinter.Frame(), index=index, path=path))
        self.tabs[index].add(self.panels[index][-1].frame)
        self.tabs[index].select(len(self.tabs[index].tabs())-1)
        self.panels[index][-1].show_dir()
        #ставлю фокус на открытую вкладку
        self.panels[index][self.tabs[index].index("current")].field.focus_set()
        self.panels[index][self.tabs[index].index("current")].field.event_generate("<KeyPress-space>") 


class FilesField():
    def __init__(self, parent=None, frame=None, index=0, path=None):
        self.index = index #идентификатор файлового окна
        self.frame = frame
        self.frame.grid_rowconfigure(2, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.parent = parent
        self.parent.tabs[self.index].bind("<Button-2>", self.close_tab)
        self.files = FileManager(path=path)
        self.create_user_elements()
        self.set_icons() #назначаю иконки файлам/папкам
        self.searched_files = [] #сюда попадают найденные файлы
        self.searched_dirs = [] #сюда попадают найденные каталоги
        self.value = "" #переменная используется для записи в неё значения, полученного из модального окна
        self.print_info()

    def create_user_elements(self):
        #создаю элементы управления

        #список выбора диска
        self.drives = [os.path.sep]
        self.drive_selector = tkinter.ttk.Combobox(self.frame, values=self.drives, postcommand=self.refresh_drives)
        self.drive_selector.current(0)
        self.drive_selector.grid(sticky="w", row=0)
        #бинд на выбор диска
        self.drive_selector.bind("<<ComboboxSelected>>", self.goto_drive)

        #строка поиска файлов
        self.searching_frame = tkinter.Frame(self.frame)
        self.search_entry = tkinter.Entry(self.searching_frame, relief="groove")
        self.search_button = tkinter.Button(self.searching_frame, text='найти', command=self._search, relief="groove")
        self.search_button.grid(sticky="swen", row=0, column=1)
        self.search_entry.grid(sticky="swen", row=0)
        self.searching_frame.grid(sticky="se", row=0)

        #строки ввода пути
        self.path_entry = tkinter.Entry(self.frame)
        self.path_entry.grid(sticky="w, e", row=1)
        self.path_entry.bind("<KeyPress-Return>", self.goto_path)
        self.search_entry.bind("<KeyPress-Return>", self._search)
        self.search_entry.bind("<KeyPress-Escape>", self.show_dir)

        #файловое окно
        self.field = tkinter.ttk.Treeview(self.frame, selectmode="extended", columns=("name", "type", "size", "mdate"),
            displaycolumns="#all", show="tree headings", height=34)
        self.field.column("#0", width=40) #задаю дефолтную ширину указанного столбца СТОЛБЕЦ С ИКОНКАМИ
        self.field.column("name", stretch=True) #задаю дефолтную ширину указанного столбца
        self.field.column("type", width=90) #задаю дефолтную ширину указанного столбца
        self.field.column("size", width=100) #задаю дефолтную ширину указанного столбца
        self.field.column("mdate", width=120) #задаю дефолтную ширину указанного столбца

        self.field.heading("name", text="имя")
        self.field.heading("type", text="тип")
        self.field.heading("size", text="размер")
        self.field.heading("mdate", text="изменён")
        self.field.insert("", "end", tags=["field","even"], values=("[%s]"%os.pardir, "", "", ""))
        self.field.grid(sticky="w, n, e, s", row=2)

        #нижнее поле отображения сведений о файле/каталоге
        self.bottom_info_panel = tkinter.Label(self.frame, text='', relief='groove', anchor="w")
        self.bottom_info_panel.grid(sticky='swne', column=0) 

        #контекстное меню по нажатию ПКМ
        self.files_context_menu = tkinter.Menu(self.frame, tearoff=0)
        self.files_context_menu.add_command(label='открыть', command=self._open)
        self.files_context_menu.add_command(label='открыть как...', command=self._open_as)
        self.files_context_menu.add_command(label='копировать', command=self._copy)
        self.files_context_menu.add_command(label='вырезать', command=self._cut)
        self.files_context_menu.add_command(label='вставить', command=self._move)
        self.files_context_menu.add_command(label='переименовать', command=self._rename)
        self.files_context_menu.add_command(label='создать каталог', command=self._make_dir)
        self.files_context_menu.add_command(label='удалить', command=self._delete)
        self.field.bind("<Button-3>", self.show_menu)
        self.field.bind("<Double-Button-1>", self._open)
        self.field.bind("<KeyPress-Return>", self._open)
        self.field.bind("<KeyPress-Delete>", self._delete)
        self.field.bind("<KeyPress-Escape>", self.show_dir)
        self.field.bind("<KeyPress-BackSpace>", self.goto_up_catalog)
        self.field.bind("<KeyPress-End>", self.goto_last_element)
        self.field.bind("<KeyPress-Home>", self.goto_first_element)
        self.field.bind("<Control-KeyPress>", self.check_ctrl_event)
        self.field.bind("<<TreeviewSelect>>", self.print_info)   
        self.field.bind("<KeyPress-Left>", (lambda self=self, parent=self.parent, index=self.index : parent.switch_focus_left(index)))
        self.field.bind("<KeyPress-Right>", (lambda self=self, parent=self.parent, index=self.index : parent.switch_focus_right(index)))
        self.field.bind("<Control-KeyPress-Left>", (lambda self=self, parent=self.parent, index=self.index : parent.switch_focus_left(index, 1)))
        self.field.bind("<Control-KeyPress-Right>", (lambda self=self, parent=self.parent, index=self.index : parent.switch_focus_right(index, 1)))
        self.field.bind("<Control-Return>", self.add_tab_with_path)

        #выпадающее доп. меню "открыть через..."
        self.open_as_cascade = tkinter.Menu(self.files_context_menu, tearoff=0)







        #ТУТ НУЖНО ПРОВЕРЯТЬ, КАКИЕ МОДУЛИ ПОДКЛЮЧЕНЫ, И ПРЕДЛАГАТЬ ВЫБОР ИЗ МОДУЛЕЙ
        #т.е. заполнять список контекстного меню из доступных модулей






        for inst in self.parent.instruments:
            self.open_as_cascade.add_command(label=inst[1], command=(lambda self=self,
             parent=self.parent, instrument=inst[0]: parent.run_instrumente(instrument=instrument, args=self.get_args())))
            # self.open_as_cascade.add_command(label='текстовый редактор', command=exit)
        self.files_context_menu.insert_cascade(2, menu=self.open_as_cascade, label='открыть через...')

    def set_icons(self):
        '''метод для задания иконок файлам'''
        self.icons = []
        for icon in os.listdir("img/icons"):
            self.icons.append(tkinter.PhotoImage(file=os.path.join("img/icons" ,icon)))
            if os.path.splitext(icon)[0] == 'unknown':
                self.field.tag_configure("file", image=self.icons[-1])
                continue
            if os.path.splitext(icon)[0] == 'dir':
                self.field.tag_configure("dir", image=self.icons[-1])
                continue
            # else:
            print(".%s" %os.path.splitext(icon)[0] == '.zip')
            self.field.tag_configure((".%s" %os.path.splitext(icon)[0]), image=self.icons[-1])
            self.field.tag_configure(".zip", image=self.icons[-1])

    def get_args(self, *args):
        '''метод задаёт аргументы для вызова инструмента'''
        if self.field.selection()[0] == self.field.get_children("")[0] or self.field.selection() == ():
            return None
        else:
            for num in self.field.selection():
                if num == 0:
                    continue
                else:
                    arg = os.path.join(self.files.path.get(), "%s%s" %(self.field.set(num)["name"], self.field.set(num)["type"]))
                    return arg
        return None

    def print_info(self, *args):
        '''метод выводит инфо о файле/каталоге в нижнюю панель'''
       
        disk_total =  self.convert_bytes(shutil.disk_usage(self.files.path.get()).total)
        disk_free = self.convert_bytes(shutil.disk_usage(self.files.path.get()).free)

        #если выбран 1 или 0 элементов
        if len(self.field.selection()) <= 1:
            self.bottom_info_panel.configure(text="папок: %s, файлов: %s, свободно на диске: %s / %s" %(len(self.files.dirs), len(self.files.files), disk_free, disk_total))
            return
        #если выбрано несколько элементов
        elif len(self.field.selection()) > 1:
            if len(self.field.selection()) == 2 and self.field.get_children("")[0] in self.field.selection():
                return
            file_size = 0
            for num in self.field.selection():
                if num == 0:
                    continue
                obj = "%s%s" %(self.field.set(num)["name"], self.field.set(num)["type"])
                if os.path.isfile(os.path.join(self.files.path.get(), obj)):
                    file_size += os.stat(os.path.join(self.files.path.get(), obj)).st_size
            #высчитываю общий размер
            file_size = self.convert_bytes(file_size)
            if self.field.get_children("")[0] in self.field.selection():
                selected_obj = len(self.field.selection())-1
            else:
                selected_obj = len(self.field.selection())
            if selected_obj > len(self.field.get_children(""))-1:
                selected_obj = len(self.field.get_children(""))-1
            selected_obj = "%s из %s" %(selected_obj, len(self.field.get_children(""))-1)
            self.bottom_info_panel.configure(text="выделено: %s, размер: %s, свободно на диске: %s / %s" %(selected_obj, file_size, disk_free, disk_total))

    def goto_last_element(self, *args):
        '''переход к последнему элементу списка файлов'''
        self.field.focus(self.field.get_children("")[-1])
        self.field.selection_set(self.field.get_children("")[-1])
        self.field.event_generate("<KeyPress-space>")
        self.field.see(self.field.get_children("")[-1])

    def goto_first_element(self, *args):
        '''переход к последнему элементу списка файлов'''
        self.field.focus(self.field.get_children("")[0])
        self.field.selection_set(self.field.get_children("")[0])
        self.field.event_generate("<KeyPress-space>")
        self.field.see(self.field.get_children("")[0])

    def add_tab(self, event):
        '''добавляет новую вкладку'''
        self.parent.add_tab(index=self.index)

    def add_tab_with_path(self, event):
        '''добавляет новую вкладку с определённым путём'''
        if  self.field.selection() == ():
            path = self.files.path.get()
            self.parent.add_tab(index=self.index, path=path)
        elif len(self.field.selection()) == 1 and self.field.selection()[0] == self.field.get_children("")[0]:
            path = os.path.split(self.files.path.get())[0]
            self.parent.add_tab(index=self.index, path=path)
        else:
            for tab in self.field.selection():
                if tab == self.field.get_children("")[0]:
                    continue
                path = os.path.join(self.files.path.get(), "%s%s" %(self.field.set(tab)["name"], self.field.set(tab)["type"]))
                if os.path.lexists(path) == False or os.path.isdir(path) == False:
                        continue
                self.parent.add_tab(index=self.index, path=path)

    def close_tab(self, event):
        '''метод закрывает вкладку по нажатии СКМ, или
        открывает новую вкладку, если клик СКМ был по пустому месту'''
        try:
            self.parent.tabs[self.index].index("@%s,%s" %(event.x, event.y))
        except:
            self.parent.add_tab(index=self.index)
        else:
            self.parent.close_tab(index=self.index, x=event.x, y=event.y)

    def show_menu(self, event):
        if len(self.field.selection()) <= 1:
            for selected in self.field.selection():
                self.field.selection_remove(selected)
            self.field.event_generate("<Button-1>", x=event.x, y=event.y)
        self.files_context_menu.post(event.x_root, event.y_root)

    def goto_path(self, event):
        path = self.path_entry.get()
        if os.path.lexists(path):
            self.files.set_dir(path)
            self.show_dir()

    def goto_drive(self, event):
        path = self.drive_selector.get()
        if os.path.lexists(path):
            self.files.set_dir(path)  
            self.show_dir()

    def select_all(self, *args):
        '''метод выбирает все пункты'''
        if len(self.field.get_children("")) > 1:
            self.field.selection_set(self.field.get_children("")[1])
        for selection in self.field.get_children("")[1:]:
            self.field.selection_add(selection)
        self.print_info()

    def convert_bytes(self, input_bytes=0, output=0):
            '''функция принимает кол-во байтов, и возвращает форматированную строку
            перевода байтов в Кб, Мб, или Гб'''
            if (input_bytes/1024/1024/1024) > 1:
                output = "%0.2f Гб" %(input_bytes/1024/1024/1024)
            elif (input_bytes/1024/1024) > 1:
                output = "%0.2f Мб" %(input_bytes/1024/1024)
            elif (input_bytes/1024) > 1:
                output = "%0.2f Кб" %(input_bytes/1024)
            else:
                output = "%s байт" %(input_bytes)
            return output

    def show_dir(self, *args):
        '''заполняет файлами и папками окна'''
        

        self.path_entry.delete(0, len(self.path_entry.get()))
        self.path_entry.insert(0, self.files.path.get()) 
        #стираю все поля перед перерисовкой
        for obj in self.field.get_children("")[1:]:
            self.field.delete(obj)
        self.files.refresh() #обновляю список файлов и каталогов
        #заполняю каталогами
        for i in range(len(self.files.dirs)):
            fname=os.path.split(self.files.dirs[i])[1]
            ftype=""
            fsize="<каталог>"
            fmdate=time.localtime(os.stat(os.path.join(self.files.path.get(), self.files.dirs[i])).st_mtime)
            fmdate = time.strftime("%d.%m.%Y - %H:%M", fmdate)
            self.field.insert("", "end", tags=["field","dir"], values=(fname, ftype, fsize, fmdate))
        #заполняю файлами
        for i in range(len(self.files.files)):
            fname=os.path.split(self.files.files[i])[1]
            ftype=os.path.splitext(fname)[1]
            fname=os.path.splitext(fname)[0]
            fsize=self.convert_bytes(os.stat(os.path.join(self.files.path.get(), self.files.files[i])).st_size)
            fmdate=time.localtime(os.stat(os.path.join(self.files.path.get(), self.files.files[i])).st_mtime)
            fmdate = time.strftime("%d.%m.%Y - %H:%M", fmdate)
            self.field.insert("", "end", tags=["field","file", "%s" %ftype], values=(fname, ftype, fsize, fmdate))
        #раскрашиваю чётные строки
        self.coloring_even() #раскрашиваю четные пункты
        #меняю название вкладки
        self.parent.tabs[self.index].tab(self.parent.tabs[self.index].index("current"), text="%s%s" %(os.path.splitdrive(self.files.path.get())[0], os.path.split(self.files.path.get())[1]))
        #заношу информацию в нижнюю панель
        self.print_info()
        #ставлю фокус на [..]
        self.field.selection_set(self.field.get_children("")[0])
        self.field.focus(self.field.get_children("")[0])

    def check_ctrl_event(self, event):
        '''метод для проверки, какая комбинация клавиш с контролом была нажата,
        что-бы работало на любой раскладке'''
        #ctrl+a
        if event.keycode == 65:
            self.select_all()
        #ctrl+c
        elif event.keycode == 67:
            self._copy()
        #ctrl+v
        elif event.keycode == 86:
            self._move()
        #ctrl+x
        elif event.keycode == 88:
            self._cut()

    def _search(self, *args):
        #метод для поиска файлов
        self.searched_files = []
        self.searched_dirs = []
        filename = self.search_entry.get()
        if filename != '':
            self.fractal_search(self.files.path.get(), filename)
        else:
            self.show_dir()
        if len(self.searched_files) > 0 or len(self.searched_dirs):
            for obj in self.field.get_children("")[1:]:
                self.field.delete(obj) #стираю все поля перед перерисовкой
            for catalog in range(len(self.searched_dirs)):
                ftype=""
                fsize="<каталог>"
                fmdate=time.localtime(os.stat(os.path.join(self.files.path.get(), self.searched_dirs[catalog])).st_mtime)
                fmdate = time.strftime("%d.%m.%Y - %H:%M", fmdate)
                self.field.insert("", "end", tags=["field","dir"], values=(os.path.relpath(self.searched_dirs[catalog], self.files.path.get()), ftype,fsize,fmdate))
            for file in range(len(self.searched_files)):
                fname=os.path.splitext(self.searched_files[file])[0]
                ftype=os.path.splitext(self.searched_files[file])[1]
                fsize=self.convert_bytes(os.stat("%s%s" %(fname, ftype)).st_size)
                fmdate=time.localtime(os.stat(os.path.join(self.files.path.get(), "%s%s" %(fname, ftype))).st_mtime)
                fmdate = time.strftime("%d.%m.%Y - %H:%M", fmdate)
                self.field.insert("", "end", tags=["field","file", "%s" %ftype], values=(os.path.splitext(os.path.relpath(self.searched_files[file], self.files.path.get()))[0], ftype,fsize,fmdate))
            self.coloring_even() #раскрашиваю четные пункты

    def coloring_even(self):
        #раскрашиваю чётные строки
        for i in range(1, len(self.field.get_children(""))):
            if i%2 == 0:
                tags=[]
                tags+=(self.field.item(self.field.get_children("")[i])["tags"])
                tags+=["even"]
                self.field.item(self.field.get_children("")[i], tags=tags)
        self.field.tag_configure("even", background='lightgray')
        self.field.tag_configure("field", font=('Arial', 10, "bold"))
        self.field.tag_configure("dir", foreground='blue')

    def fractal_search(self, path, filename):
        #метод рекурсивно обходит каталоги, ища файл
        try:
            for file in os.scandir(path):
                if os.path.isdir(file):
                    if filename.lower() in file.name.lower():
                        self.searched_dirs.append(os.path.join(path, file.name))
                    self.fractal_search(os.path.join(path, file), filename)
                elif os.path.isfile(file):
                    if filename.lower() in file.name.lower():
                        self.searched_files.append(os.path.join(path, file))
        except:
            return

    def refresh_drives(self, *args):
        '''метод обновляет список доступных дисков'''
        self.drives = [os.path.sep]
        for drive in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            if os.path.lexists("%s:%s" %(drive, os.path.sep)):
                self.drives.append("%s:%s" %(drive, os.path.sep))
        self.drive_selector.configure(values=self.drives)

    def goto_up_catalog(self, *args):
        '''метод перехода в верхний каталог'''
        self.files.path.set(os.path.split(self.files.path.get())[0])
        self.show_dir()

    def _open(self, *args):
        #генерирую событие, что-бы сбить дабл-клик (что-бы трипл-клик не открывал объект 2 раза)
        self.field.event_generate("<Shift-slash>")
        #если не выбран ни один элемент
        if self.field.selection() == ():
            return
        #если выбран элемент перехода в верхний каталог
        if self.field.selection()[0] == self.field.get_children("")[0]: 
            self.goto_up_catalog()
            return
        #если выбран каталог или файл
        for obj in self.field.selection():
            if obj == self.field.get_children("")[0]:
                continue
            try_open = os.path.join(self.files.path.get(), "%s%s" %(self.field.set(obj)["name"], self.field.set(obj)["type"]))
            if os.path.isdir(try_open):
                self.files.set_dir(try_open)
                self.show_dir()
                return
            elif os.path.isfile(try_open):
                os.startfile(try_open)

    def _open_as(self, *args):
        '''метод открывает выбранный пенкт через другое приложение ("открыть как...")
        Запуск происходит в отдельном процессе, что-бы избежать зависания'''
        filename = tkinter.filedialog.askopenfilename(title='Укажите, через что нужно открыть')
        if filename == '':
            return
        filename = os.path.normcase(filename)
        arguments = ''
        #собираю строку аргументов
        for obj in self.field.selection():
            if obj == self.field.get_children("")[0]:
                continue
            else:
                arguments += '"%s" ' %(os.path.join(self.files.path.get(), "%s%s" %(self.field.set(obj)["name"], self.field.set(obj)["type"])))
        #запускаю процесс
        process = multiprocessing.Process(target=subprocess.call, args=('"%s" %s' %(filename, arguments),))
        process.daemon = False
        process.start()

    def _delete(self, *args):
        '''метод вызывается при выборе удаления файла или каталога'''
        if self.field.selection() == (self.field.get_children("")[0],) or self.field.selection() == ():
            return
        if len(self.field.selection()) == 1:
            user_choose = messagebox.askyesno(title='Подтверждение удаления', message='Вы действительно хотите удалить "%s"?' %("%s%s" %(self.field.set(self.field.selection()[0])["name"], self.field.set(self.field.selection()[0])["type"])))
        elif len(self.field.selection()) > 1:
            user_choose = messagebox.askyesno(title='Подтверждение удаления', message='Вы действительно хотите удалить выбранные элементы?')
        if user_choose == False or user_choose == None:
            return
        #реализация удаления нескольких файлов
        for obj in self.field.selection():
            if obj == self.field.get_children("")[0]:
                continue
            try_delete = os.path.join(self.files.path.get(), "%s%s" %(self.field.set(obj)["name"], self.field.set(obj)["type"]))
            if os.path.isdir(try_delete):
                try:
                    shutil.rmtree(try_delete, True)
                except:
                    pass
            elif os.path.isfile(try_delete):
                try:
                    os.remove(try_delete)
                except:
                    pass
        for i in self.parent.panels:
            i[0].show_dir()
     
    def _make_dir(self):
        '''метод создаёт каталог'''
        self.value = ""
        window = ModalWindow(parent=self, title='Создать каталог', text='Введите название')
        window.window.wait_window(window.window) #ожидаю закрытия окна
        if self.value != "" and self.value != None:
            os.mkdir(os.path.join(self.files.path.get(), self.value))
        for i in self.parent.panels:
            i[0].show_dir()

    def _rename(self):
        '''метод переименовывет файл/каталог'''
        if self.field.selection() == (self.field.get_children("")[0],) or self.field.selection() == ():
            return
        if len(self.field.selection()) < 2:
            old_name = "%s%s" %(self.field.set(self.field.selection()[0])["name"], self.field.set(self.field.selection()[0])["type"])
            if old_name == '' or old_name == None:
                return
            self.value = ""
            window = ModalWindow(parent=self, title='Переименовать', text='Введите новое имя', entry_text=old_name)
            window.window.wait_window(window.window) #ожидаю закрытия окна
            if self.value != "" and self.value != None:
                os.rename(os.path.join(self.files.path.get(), old_name), os.path.join(self.files.path.get(), self.value))
        else:
            self.value = ""
            window = ModalWindow(parent=self, title='Групповое переименование', text='Введите шаблонное имя для выделенных объектов')
            window.window.wait_window(window.window) #ожидаю закрытия окна
            if self.value != "" and self.value != None:
                file_num = 1
                dir_num = 1
                for obj in self.field.selection():
                    if obj == self.field.get_children("")[0]:
                        continue
                    #если переименовываю файлы
                    if os.path.isfile(os.path.join(self.files.path.get(), "%s%s" %(self.field.set(obj)["name"], self.field.set(obj)["type"]))):
                        #если файла с таким же именем в системе нет
                        if os.path.exists(os.path.join(self.files.path.get(), self.value)) == False:
                            try:
                                os.rename(os.path.join(self.files.path.get(), "%s%s" %(self.field.set(obj)["name"], self.field.set(obj)["type"])), os.path.join(self.files.path.get(), self.value))
                            except:
                                pass
                        #если файл с таким же именем уже существует, добавляю _num
                        else:
                            while os.path.exists(os.path.join(self.files.path.get(), "%s_%s%s" %(os.path.splitext(self.value)[0], file_num, os.path.splitext(self.value)[1]))) == True:
                                file_num += 1
                            try:
                                os.rename(os.path.join(self.files.path.get(), "%s%s" %(self.field.set(obj)["name"], self.field.set(obj)["type"])), os.path.join(self.files.path.get(), 
                                    "%s_%s%s" %(os.path.splitext(self.value)[0],
                                    file_num, os.path.splitext(self.value)[1])))
                                file_num += 1
                            except:
                                pass
                    #если переименовываю каталоги
                    elif os.path.isdir(os.path.join(self.files.path.get(), "%s%s" %(self.field.set(obj)["name"], self.field.set(obj)["type"]))):
                        if os.path.exists(os.path.join(self.files.path.get(), self.value)) == False:
                            try:
                                os.rename(os.path.join(self.files.path.get(), "%s%s" %(self.field.set(obj)["name"], self.field.set(obj)["type"])), os.path.join(self.files.path.get(), self.value))
                            except:
                                pass
                        #если такой каталог уже существует
                        else:
                            while os.path.exists(os.path.join(self.files.path.get(), "%s_%s" %(self.value, dir_num))) == True:
                                dir_num += 1
                            try:
                                os.rename(os.path.join(self.files.path.get(), "%s%s" %(self.field.set(obj)["name"], self.field.set(obj)["type"])), os.path.join(self.files.path.get(), "%s_%s" %(self.value, dir_num)))
                                dir_num += 1
                            except:
                                pass
        for i in self.parent.panels:
            i[0].show_dir()

    def _cut(self, *args):
        '''метод вырезает файл/каталог'''
        if self.field.selection() == (self.field.get_children("")[0],) or self.field.selection() == ():
            return
        else:
            self.parent.cut = []
            for obj in self.field.selection():
                if obj == self.field.get_children("")[0]:
                    continue
                else:
                    self.parent.cut.append(os.path.join(self.files.path.get(), "%s%s" %(self.field.set(obj)["name"], self.field.set(obj)["type"])))
        self.parent.copy = None

    def _copy(self, *args):
        '''копирование файла/папки'''
        if self.field.selection() == (self.field.get_children("")[0],) or self.field.selection() == ():
            return
        else:
            self.parent.copy =  []
            for obj in self.field.selection():
                if obj == self.field.get_children("")[0]:
                    continue
                else:
                    self.parent.copy.append(os.path.join(self.files.path.get(), "%s%s" %(self.field.set(obj)["name"], self.field.set(obj)["type"])))
        self.parent.cut = None

    def _move(self, *args):
        '''метод вставляет вырезанный/скопированный объект'''
        """
        ТУТ НУЖНО:














        -создавать окно с прогрессом копирования/перемещения. Нужно смотреть размер исходного и всталвяемого файлов.
        -запуск производить в отдельном процессе.


















        """
        if self.parent.cut != None:
            for obj in self.parent.cut:
                if os.path.exists(os.path.join(self.files.path.get(), os.path.split(obj)[1])):
                    if self.value == 'overwriteall' or self.value == 'rename':
                        pass
                    else:
                        window = ModalWindow_overwrite_or_rename(parent=self, title='Внимание', text='В данном каталоге уже есть "%s"' %(os.path.split(obj)[1]))
                        window.window.wait_window(window.window) #ожидаю закрытия окна
                    if self.value == None:
                        continue
                    elif self.value == 'rename':
                        num = 1
                        name = os.path.split(obj)[1]
                        while os.path.exists(os.path.join(self.files.path.get(), "%s_%s%s" %(os.path.splitext(name)[0], num, os.path.splitext(name)[1]))):
                            num+=1
                        try:
                            shutil.move(obj, os.path.join(self.files.path.get(), "%s_%s%s" %(os.path.splitext(name)[0], num, os.path.splitext(name)[1])))
                        except:
                            pass
                    elif self.value == 'overwrite' or self.value == 'overwriteall':
                        if os.path.isfile(os.path.join(self.files.path.get(), os.path.split(obj)[1])):
                            os.remove(os.path.join(self.files.path.get(), os.path.split(obj)[1]))
                            try:
                                shutil.move(obj, os.path.join(self.files.path.get(), os.path.split(obj)[1]))
                            except:
                                pass
                        elif os.path.isdir(os.path.join(self.files.path.get(), os.path.split(obj)[1])):
                            shutil.rmtree(os.path.join(self.files.path.get(), os.path.split(obj)[1]), True)
                            try:
                                shutil.move(obj, os.path.join(self.files.path.get(), os.path.split(obj)[1]))
                            except:
                                pass
                else:
                    try:
                        shutil.move(obj, self.files.path.get())
                    except:
                        pass
        elif self.parent.copy != None:
            for obj in self.parent.copy:
                if os.path.exists(os.path.join(self.files.path.get(), os.path.split(obj)[1])):
                    if self.value == 'overwriteall' or self.value == 'rename':
                        pass
                    else:
                        window = ModalWindow_overwrite_or_rename(parent=self, title='Внимание', text='В данном каталоге уже есть "%s"' %(os.path.split(obj)[1]))
                        window.window.wait_window(window.window) #ожидаю закрытия окна
                    if self.value == None:
                        continue
                    elif self.value == 'rename':
                        num = 1
                        name = os.path.split(obj)[1]
                        while os.path.exists(os.path.join(self.files.path.get(), "%s_%s%s" %(os.path.splitext(name)[0], num, os.path.splitext(name)[1]))):
                            num+=1
                        if os.path.isfile(obj):
                            try:
                                shutil.copy(obj, os.path.join(self.files.path.get(), "%s_%s%s" %(os.path.splitext(name)[0], num, os.path.splitext(name)[1])))
                            except:
                                pass
                        elif os.path.isdir(obj):
                            try:
                                shutil.copytree(obj, os.path.join(self.files.path.get(), "%s_%s%s" %(os.path.splitext(name)[0], num, os.path.splitext(name)[1])))
                            except:
                                pass
                    elif self.value == 'overwrite' or self.value == 'overwriteall':
                        if os.path.isfile(os.path.join(self.files.path.get(), os.path.split(obj)[1])):
                            os.remove(os.path.join(self.files.path.get(), os.path.split(obj)[1]))
                            try:
                                shutil.copy(obj, os.path.join(self.files.path.get(), os.path.split(obj)[1]))
                            except:
                                pass
                        elif os.path.isdir(os.path.join(self.files.path.get(), os.path.split(obj)[1])):
                            shutil.rmtree(os.path.join(self.files.path.get(), os.path.split(obj)[1]), True)
                            try:
                                shutil.copytree(obj, os.path.join(self.files.path.get(), os.path.basename(obj)))
                            except:
                                pass

                else:
                    if os.path.isfile(obj):
                        try:
                            shutil.copy(obj, self.files.path.get())
                        except:
                            pass
                    elif os.path.isdir(obj):
                        try:
                            shutil.copytree(obj, os.path.join(self.files.path.get(), os.path.basename(obj)))
                        except:
                            pass
        for i in self.parent.panels:
            i[0].show_dir()
        self.parent.cut = None
        self.value = ""

class ModalWindow_overwrite_or_rename():
    def __init__(self, parent=None, title='', text=''):
        self.title = title
        self.text = text
        self.choose = None
        self.parent = parent
        self.parent.value = self.choose
        self.create_window()

    def create_window(self):
        self.window = tkinter.Toplevel()
        self.window.focus()
        self.window.grid_columnconfigure(0, weight=2)
        self.window.grid_rowconfigure(0, weight=2)
        #задаю положение модального окна
        try:
            window_x = self.parent.parent.window.winfo_screenwidth()//2-250
            window_y = self.parent.parent.window.winfo_screenheight()//2-60
            self.window.geometry("500x120+%s+%s" %(window_x, window_y))
        except:
            pass
        self.window.grab_set() #фокус только на этом окне
        self.window.title(self.title)
        self.window.wm_attributes("-toolwindow", True)
        self.window.resizable(width=False, height=False)
        self.text_label = tkinter.Label(self.window, text=self.text, relief="groove")
        self.buttons_frame = tkinter.Frame(self.window)
        self.buttons_frame.grid_columnconfigure(0, weight=2)
        self.buttons_frame.grid_columnconfigure(1, weight=2)
        self.buttons_frame.grid_columnconfigure(2, weight=2)
        self.buttons_frame.grid_columnconfigure(3, weight=2)
        self.buttons_frame.grid(row=2, sticky='swen')
        self.button_rename = tkinter.Button(self.buttons_frame, text='Переименовать', width=15, command=self.pressed_rename, relief="groove")
        self.button_overwrite = tkinter.Button(self.buttons_frame, text='Заменить', width=15, command=self.pressed_overwrite, relief="groove")
        self.button_overwrite_all = tkinter.Button(self.buttons_frame, text='Заменить все', width=15, command=self.pressed_overwrite_all, relief="groove")
        self.button_cancel = tkinter.Button(self.buttons_frame, text='Отмена', width=15, command=self.pressed_cancel, relief="groove")
        self.text_label.grid(row=0, sticky='swen')
        self.button_rename.grid(row=0, sticky='swen', column=0)
        self.button_overwrite.grid(row=0, sticky='swen', column=1)
        self.button_overwrite_all.grid(row=0, sticky='swen', column=2)
        self.button_cancel.grid(row=0, sticky='swen', column=3)

    def pressed_overwrite_all(self, *args):
        self.choose = 'overwriteall'
        self.parent.value = self.choose
        self.window.destroy()

    def pressed_overwrite(self, *args):
        self.choose = 'overwrite'
        self.parent.value = self.choose
        self.window.destroy()

    def pressed_rename(self, *args):
        self.choose = 'rename'
        self.parent.value = self.choose
        self.window.destroy()

    def pressed_cancel(self, *args):
        self.choose = None
        self.parent.value = self.choose
        self.window.destroy()

class ModalWindow():
    '''модальное окно для переименовывания папок и файлов'''
    def __init__(self, parent=None, title='', text='', entry_text=''):
        self.title = title
        self.text = text
        self.entry_text = entry_text
        self.parent = parent
        self.create_window()

    def create_window(self):
        self.window = tkinter.Toplevel()
        self.window.grid_rowconfigure(0, weight=2)
        self.window.grid_columnconfigure(0, weight=2)
        #задаю положение модального окна
        try:
            window_x = self.parent.parent.window.winfo_screenwidth()//2-160
            window_y = self.parent.parent.window.winfo_screenheight()//2-60
            self.window.geometry("320x120+%s+%s" %(window_x, window_y))
        except:
            pass
        self.window.grab_set() #фокус только на этом окне
        self.window.title(self.title)
        self.window.wm_attributes("-toolwindow", True)
        self.window.resizable(width=False, height=False)
        self.text_label = tkinter.Label(self.window, text=self.text, relief="groove")
        self.text_in_entry = tkinter.StringVar()
        self.text_in_entry.set(self.entry_text)
        self.text_entry = tkinter.Entry(self.window, relief='sunken', border=4, textvariable=self.text_in_entry)
        self.text_entry.select_range(0, len(self.text_in_entry.get()))
        self.text_entry.bind("<KeyPress-Return>", self.pressed_ok)
        self.text_entry.focus()
        self.buttons_frame = tkinter.Frame(self.window)
        self.buttons_frame.grid_columnconfigure(0, weight=2)
        self.buttons_frame.grid_columnconfigure(1, weight=2)
        self.buttons_frame.grid_rowconfigure(0, weight=2)
        self.buttons_frame.grid(row=2, sticky='swen')
        self.button_ok = tkinter.Button(self.buttons_frame, text='ОК', command=self.pressed_ok, width=10, relief="groove")
        self.button_cancel = tkinter.Button(self.buttons_frame, text='Отмена', command=self.window.destroy, width=10, relief="groove")
        self.text_label.grid(row=0, sticky='swen')
        self.text_entry.grid(row=1, sticky='swen')
        self.button_ok.grid(row=0, sticky='swen', column=1)
        self.button_cancel.grid(row=0, sticky='swen')

    def pressed_ok(self, *args):
        self.parent.value = self.text_entry.get()
        self.window.destroy()

class ColorsChooseWindow():
    """класс для выбора цветов приложения"""
    def __init__(self, parent=None):
        self.parent = parent

class FontChooseWindow():
    """класс выбора шрифтов"""
    def __init__(self, parent=None):
        self.parent = parent


class FileManager():
    '''класс реализует управление по ФС'''
    def __init__(self, path=None):
        self.path = tkinter.StringVar()
        if path == None:
            self.path.set(os.getcwd())
        else:
            self.path.set(path)
        self.refresh()

    def set_dir(self, path):
        '''метод для смены текущего каталога'''
        try:
            os.listdir(path)
        except:
            tkinter.messagebox.showwarning(title='Ошибка доступа', message='Недостаточно прав для просмотра!') 
            return
        else:
            self.path.set(path)

    def refresh(self):
        '''метод обновляет список файлов'''
        self.dir = os.listdir(self.path.get())    
        self.files = []
        self.dirs = []
        for f in self.dir:
            if os.path.isfile(os.path.join(self.path.get(), f)):
                self.files.append(f)
            elif os.path.isdir(os.path.join(self.path.get(), f)):
                self.dirs.append(f)


if __name__ == "__main__":
    app = GUI()


'''
НУЖНО:
-подумать над сохранением состояния и над ассоциацией файлов
-в "открыть как..." подумать, как сделать своё меню выбора программы
-реализовать выбор шрифтов/цветов
-сделать по зажатому шифту выделение стрелками
-убирать синюю полосу при фокусировке на другом окне
-сделать выбор, использовать встроенные иконки, или системные
'''

'''
УПРАВЛЕНИЕ:
-клик средней кнопкой мыши по пустому месту в панели вкладок добавляет вкладку. Клмк СКМ по вкладке закроет её
-ctrl+c/v/x -копировать, вставить, вырезать
-del - удалить выбранные объекты
-стрелки влево/вправо - переключение между файловыми окнами
-контрол+стрелки влево/вправо - переключение по вкладкам в активном файловом окне
-ctrl+a - выбрать все элементы в файловом окне
-backspace - переход в верхний каталог
-ctrl+return - открывает выделенную(е) папки в новых вкладках. Если не выбран никакой элемент, то открывает новую вкладку
    с таким-же каталогом, что и текущая. Если выбран первый элеент (..), то открывает новую вкладку на уровне вверх 
'''


'''

        # "%s%s" %(self.field.set(self.field.selection()[0])["name"], self.field.set(self.field.selection()[0])["type"])
'''