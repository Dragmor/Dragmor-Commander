import tkinter
from tkinter import ttk
from tkinter import messagebox
import multiprocessing
import subprocess
import os
import shutil
import time


import modules.path_engine
import modules.paste
import modules.delete
import modules.context_menus
import modules.modal_windows

class FilesField():
    def __init__(self, parent=None, frame=None, index=0, path=None):
        self.index = index #идентификатор файлового окна
        self.frame = frame
        self.frame.grid_rowconfigure(2, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.parent = parent
        self.value = "" #хранит значение из модальных окон
        self.file_manager = modules.path_engine.FileManager(path=path)
        self.context_menus = modules.context_menus.Menu(self)
        self.create_user_elements() #отрисовка и компоновка элементов управления
        self.bind_events() #бинд событий
        self.coloring_fields() #устанавливаю цвета ячеек и т.д
        # self.set_icons() #назначаю иконки файлам/папкам №№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№
        self.current_selected = [] #переменная для сохранения выделенных пунктов

    def create_user_elements(self):
        #создаю элементы управления

        #фрейм для верхней панели выбора диска и информации о свободном месте на нём
        self.top_frame = tkinter.Frame(self.frame)
        self.top_frame.grid(sticky="swen")

        #СПИСОК ВЫБОРА ДИСКА
        self.drives = self.file_manager.get_drives()
        self.drive_selector = tkinter.ttk.Combobox(self.top_frame, values=self.drives, postcommand=self.refresh_drives)
        self.drive_selector.current(0)
        self.drive_selector.grid(sticky="w", row=0, pady=2)

        #СТРОКА ПОИСКА ФАЙЛОВ
        self.disk_space = tkinter.Label(self.top_frame, text="")
        self.disk_space.grid(sticky="swen", row=0, column=1)

        #СТРОКИ ВВОДА ПУТИ
        self.path_entry = tkinter.Entry(self.frame)
        self.path_entry.grid(sticky="w, e", row=1)
        
        #ФАЙЛОВОЕ ОКНО
        self.field = tkinter.ttk.Treeview(self.frame, selectmode="extended", columns=("name", "type", "size", "mdate"),
            displaycolumns="#all", show="tree headings", height=34)
        self.field.column("#0", width=40, minwidth=40) #задаю дефолтную ширину указанного столбца СТОЛБЕЦ С ИКОНКАМИ
        self.field.column("name", stretch=True) #задаю дефолтную ширину указанного столбца
        self.field.column("type", width=90) #задаю дефолтную ширину указанного столбца
        self.field.column("size", width=100) #задаю дефолтную ширину указанного столбца
        self.field.column("mdate", width=120) #задаю дефолтную ширину указанного столбца

        self.field.heading("name", text="имя")
        self.field.heading("type", text="тип")
        self.field.heading("size", text="размер")
        self.field.heading("mdate", text="изменён")

        #ПОЛЕ ПЕРЕХОДА В ВЕРХНИЙ КАТАЛОГ
        self.field.insert("", "end", tags=["field","odd"], values=("[%s]"%os.pardir, "", "", ""))
        self.field.grid(sticky="w, n, e, s", row=2)

        #НИЖНЕЕ ПОЛЕ ОТОБРАЖЕНИЯ СВЕДЕНИЙ О ФАЙЛЕ/КАТАЛОГЕ
        self.bottom_info_panel = tkinter.Label(self.frame, text='', relief='groove', anchor="w")
        self.bottom_info_panel.grid(sticky='swne', column=0) 

    def bind_events(self):
        """метод биндит события"""
        #бинд на выбор диска
        self.drive_selector.bind("<<ComboboxSelected>>", self.goto_drive)
        #закрытие вкладки по СКМ
        self.parent.tabs[self.index].bind("<Button-2>", self.close_tab)
        self.path_entry.bind("<KeyPress-Return>", self.goto_path)
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
        self.field.bind("<KeyRelease-Left>", (lambda self=self, parent=self.parent, index=self.index : parent.switch_focus_left(index)))
        self.field.bind("<KeyRelease-Right>", (lambda self=self, parent=self.parent, index=self.index : parent.switch_focus_right(index)))
        self.field.bind("<Control-KeyPress-Left>", (lambda self=self, parent=self.parent, index=self.index : parent.switch_focus_left(index, 1)))
        self.field.bind("<Control-KeyPress-Right>", (lambda self=self, parent=self.parent, index=self.index : parent.switch_focus_right(index, 1)))
        self.field.bind("<Control-Return>", self.add_tab_with_path)

    def refresh_drives(self):
        '''метод обновляет список доступных дисков'''
        self.drives = self.file_manager.get_drives()
        self.drive_selector.configure(values=self.drives)

    def hide_selections(self):
        '''метод скрывает выделенные пункты (нужно для
        переключения по разным окнам/вкладкам)'''
        self.current_selected = self.field.selection()
        self.field.selection_remove(self.field.get_children(""))

    def unhide_selections(self):
        '''метод восстанавливает выделения пунктов,
        скрытых методом hide_selections'''
        self.field.selection_set(self.current_selected)
        if self.current_selected == ():
            self.field.selection_set(self.field.get_children("")[0])

    def show_menu(self, event):
        """метод для вывода контекстного меню по ПКМ"""
        selected = self.get_selected_field()
        if len(selected) <= 1:
            self.field.selection_remove(self.field.get_children(""))
            self.field.event_generate("<Button-1>", x=event.x, y=event.y)
            selected = self.get_selected_field()
        self.context_menus.show_menu(event.x_root, event.y_root)

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
            self._paste()
        #ctrl+x
        elif event.keycode == 88:
            self._cut()

    def select_all(self, *args):
        '''метод выбирает все пункты'''
        if len(self.file_manager.objects) > 1:
            self.field.selection_set(self.field.get_children("")[1])
            self.field.focus(self.field.get_children("")[1])
        self.field.selection_add(self.field.get_children("")[1:])
        self.print_info()

    def show_dir(self, *args):
        '''заполняет файлами и папками окна'''
        
        #меняю путь в строке ввода пути
        self.path_entry.delete(0, len(self.path_entry.get()))
        self.path_entry.insert(0, self.file_manager.path) 
        #стираю все поля перед перерисовкой
        for obj in self.field.get_children("")[1:]:
            self.field.delete(obj)
        #заполняю поля обновлёнными данными
        count = 0 #переменная для определения чётных/нечётных строк
        for obj in self.file_manager.refresh():
            #определяю, чёт или нечёт
            if count%2 == 0:
                temp = "even"
            else:
                temp = "odd"
            count+=1
            obj_name, obj_type, obj_size, obj_mtime = self.get_stats(obj)
            if obj[0] == "d":
                self.field.insert("", "end", tags=["field","dir", temp], values=(obj_name, obj_type, obj_size, obj_mtime))
            elif obj[0] == "f":
                self.field.insert("", "end", tags=["field","file","%s" %obj_type, temp], values=(obj_name, obj_type, obj_size, obj_mtime))
        #меняю название вкладки
        self.parent.tabs[self.index].tab(self.parent.tabs[self.index].index("current"), text="%s%s" %(os.path.splitdrive(self.file_manager.path)[0], os.path.split(self.file_manager.path)[1]))
        #вывожу инфо о каталоге в нижнюю панель
        self.print_info()
        #вывожу инфо о памяти на диске в верхнюю панель
        self.get_disk_info()
        #ставлю фокус на [..]
        self.field.selection_set(self.field.get_children("")[0])
        self.field.focus(self.field.get_children("")[0])

    def print_info(self, *args):
        '''метод выводит инфо о файле/каталоге в нижнюю панель'''
        selected = self.get_selected_field()
        #если выбран 1 или 0 элементов
        if len(selected) <= 1:
            self.bottom_info_panel.configure(text="папок: %s, файлов: %s" %(self.file_manager.dirs_in_dir, self.file_manager.files_in_dir))
            return
        #если выбрано несколько элементов
        elif len(selected) > 1:
            #если был выбран пункт перехода наверх, не учитывать это выделение
            if len(selected) == 2 and selected[0] == 0:
                return
            file_size = 0
            for num in selected:
                if num == 0:
                    continue
                if self.file_manager.objects[num-1][0] == "f":
                    file_size += self.file_manager.objects[num-1][2]
            #высчитываю общий размер
            file_size = self.convert_bytes(file_size)
            if 0 in selected:
                selected_obj = len(selected)-1
            else:
                selected_obj = len(selected)
            selected_obj = "%s из %s" %(selected_obj, len(self.field.get_children("")[1:]))
            self.bottom_info_panel.configure(text="выделено: %s, размер: %s" %(selected_obj, file_size))


    def get_stats(self, obj):
        '''метод принимает объект из self.file_manager.get(),
        и возвращает данные о нём, для внесения в список show_dir'''
        #если передана инфа каталога
        if obj[0] == "d":
            obj_name = obj[1]
            obj_type = ""
            obj_size = "<каталог>"
            obj_mtime = time.strftime("%d.%m.%Y - %H:%M", time.localtime(obj[3]))
            return obj_name, obj_type, obj_size, obj_mtime
        elif obj[0] == "f":
            obj_name = os.path.splitext(obj[1])[0]
            obj_type = os.path.splitext(obj[1])[1]
            obj_size = self.convert_bytes(obj[2])
            obj_mtime = time.strftime("%d.%m.%Y - %H:%M", time.localtime(obj[3]))
            return obj_name, obj_type, obj_size, obj_mtime

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

    def coloring_fields(self):
        '''метод назначения цветов'''
        #меняю цвет чётных строк
        self.field.tag_configure("odd", background='lightgray')
        #меняю шрифты всех строк
        self.field.tag_configure("field", font=('Arial', 10, "bold"))
        #меняю цвет текста в строке каталога
        self.field.tag_configure("dir", foreground='blue')

    def goto_drive(self, event):
        '''метод для перехода к указанному диску'''
        path = self.drive_selector.get()
        if os.path.lexists(path):
            self.file_manager.set_dir(path)  
            self.show_dir()

    def goto_path(self, event):
        '''метод перехода по введённому пути в строку ввода'''
        path = self.path_entry.get()
        if os.path.lexists(path):
            self.file_manager.set_dir(path)
            self.show_dir()

    def goto_last_element(self, *args):
        '''переход к последнему элементу списка файлов'''
        self.field.focus(self.field.get_children("")[-1])
        self.field.selection_set(self.field.get_children("")[-1])
        self.field.event_generate("<KeyPress-space>")
        self.field.see(self.field.get_children("")[-1])

    def goto_first_element(self, *args):
        '''переход к первому элементу списка файлов'''
        self.field.focus(self.field.get_children("")[0])
        self.field.selection_set(self.field.get_children("")[0])
        self.field.event_generate("<KeyPress-space>")
        self.field.see(self.field.get_children("")[0])

    def get_selected_field(self):
        '''возвращает список индексов выбранных ячеек'''
        selected = [] #сюда попадают индексы выделенных ячеек
        for obj in self.field.selection():
            selected.append(self.field.index(obj))
        return selected

    def close_tab(self, event):
        '''метод закрывает вкладку по нажатии СКМ, или
        открывает новую вкладку, если клик СКМ был по пустому месту'''
        try:
            self.parent.tabs[self.index].index("@%s,%s" %(event.x, event.y))
        except:
            self.parent.add_tab(index=self.index)
        else:
            self.parent.close_tab(index=self.index, x=event.x, y=event.y)

    def add_tab(self, event):
        '''добавляет новую вкладку'''
        self.parent.add_tab(index=self.index)

    def add_tab_with_path(self, *event):
        '''добавляет новую вкладку с определённым путём'''
        selected = self.get_selected_field()
        if selected == []:
            self.parent.add_tab(index=self.index, path=self.file_manager.path)
        #если выбран пункт перехода на уровень вверх
        elif selected == [0]:
            self.parent.add_tab(index=self.index, path=os.path.split(self.file_manager.path)[0])
        #если был отмечен пункт
        else:
            for tab_id in selected:
                #если был отмечен пункт перехода наверх, игнорирую его
                if tab_id == 0:
                    continue
                path = os.path.join(self.file_manager.path, self.file_manager.objects[tab_id-1][1])
                if os.path.lexists(path) == False or os.path.isdir(path) == False:
                    continue
                self.parent.add_tab(index=self.index, path=path)

    def get_args(self, *args):
        '''метод задаёт аргументы для вызова инструмента'''
        selected = self.get_selected_field()
        if selected == [] or selected == [0]:
            return None
        else:
            for num in selected:
                if num == 0:
                    continue
                else:
                    arg = os.path.join(self.file_manager.path, self.file_manager.objects[num-1][1])
                    return arg
        return None

    def goto_up_catalog(self, *args):
        '''метод перехода в верхний каталог'''
        self.file_manager.path = os.path.split(self.file_manager.path)[0]
        self.show_dir()

    def _open(self, *args):
        #генерирую событие, что-бы сбить дабл-клик (что-бы трипл-клик не открывал объект 2 раза)
        self.field.event_generate("<Shift-slash>")
        selected = self.get_selected_field()
        #если не выбран ни один элемент
        if selected == []:
            return
        #если выбран элемент перехода в верхний каталог
        elif selected == [0]:
            self.goto_up_catalog()
            return
        #если выбран каталог или файл
        for obj in selected:
            if obj == 0:
                continue
            try_open = os.path.join(self.file_manager.path, self.file_manager.objects[obj-1][1])
            if os.path.isdir(try_open):
                self.file_manager.set_dir(try_open)
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
        selected = self.get_selected_field()
        #собираю строку аргументов
        for obj in selected:
            if obj == 0:
                continue
            else:
                arguments += '"%s" ' %(os.path.join(self.file_manager.path, self.file_manager.objects[obj-1][1]))
        #запускаю процесс
        process = multiprocessing.Process(target=subprocess.call, args=('"%s" %s' %(filename, arguments),))
        process.daemon = False
        process.start()

    def _delete(self, *args):
        '''метод вызывается при выборе удаления файла или каталога'''
        selected = self.get_selected_field()
        if selected == [] or selected == [0]:
            return
        if len(selected) == 1:
            user_choose = messagebox.askyesno(title='Подтверждение удаления', message='Вы действительно хотите удалить "%s"?' %(self.file_manager.objects[selected[0]-1][1]))
        elif len(selected) > 1:
            user_choose = messagebox.askyesno(title='Подтверждение удаления', message='Вы действительно хотите удалить выбранные элементы?')
        if user_choose == False or user_choose == None:
            return
        try_delete = [] #список файлов и папок на удаление
        #реализация удаления файлов/каталогов
        for obj in selected:
            if obj == 0:
                continue
            try_delete.append(os.path.join(self.file_manager.path, self.file_manager.objects[obj-1][1]))
        deleter = modules.delete.Deleter(self, obj_list=try_delete)


    def _cut(self, *args):
        '''метод вырезает файл/каталог'''
        selected = self.get_selected_field()
        if len(selected) == 0 or selected == [0]:
            return
        else:
            self.parent.cut = []
            for obj in selected:
                if obj == 0:
                    continue
                else:
                    self.parent.cut.append(os.path.join(self.file_manager.path, self.file_manager.objects[obj-1][1]))
        self.parent.copy = None

    def _copy(self, *args):
        '''копирование файла/папки'''
        selected = self.get_selected_field()
        if len(selected) == 0 or selected == [0]:
            return
        else:
            self.parent.copy =  []
            for obj in selected:
                if obj == 0:
                    continue
                else:
                    self.parent.copy.append(os.path.join(self.file_manager.path, self.file_manager.objects[obj-1][1]))
        self.parent.cut = None

    def _paste(self):
        '''метод запускает вставку вырезанного или
        скопированного файла/папки'''
        if self.parent.cut != None:
            mode = "move"
            obj_list = self.parent.cut
        elif self.parent.copy != None:
            mode = "copy"
            obj_list = self.parent.copy
        else:
            return
        #объект для вставки файлов/каталогов
        paste = modules.paste.Paste(self, path=self.file_manager.path, obj_list=obj_list, mode=mode)

    def _make_dir(self):
        '''метод создаёт каталог'''
        self.value = ""
        window = modules.modal_windows.GetName(parent=self, title='Создать каталог', text='Введите название')
        self.parent.window.wait_window(window.window) #ожидаю закрытия окна
        if self.value != "" and self.value != None:
            os.mkdir(os.path.join(self.file_manager.path, self.value))
            #обновляю содержимое всех файловых окон
            self.parent.update_panels()

    def _rename(self):
        '''метод переименовывет файл/каталог'''
        selected = self.get_selected_field()
        if selected == [] or selected == [0]:
            return
        if len(selected) == 1:
            old_name = self.file_manager.objects[selected[0]-1][1]
            if old_name == '' or old_name == None:
                return
            self.value = ""
            window = modules.modal_windows.GetName(parent=self, title='Переименовать', text='Введите новое имя', entry_text=old_name)
            self.parent.window.wait_window(window.window) #ожидаю закрытия окна
            if self.value != "" and self.value != None:
                os.rename(os.path.join(self.file_manager.path, old_name), os.path.join(self.file_manager.path, self.value))
        else:
            self.value = ""
            window = modules.modal_windows.GetName(parent=self, title='Групповое переименование', text='Введите шаблонное имя для выделенных объектов')
            self.parent.window.wait_window(window.window) #ожидаю закрытия окна
            if self.value != "" and self.value != None:
                file_num = 1
                dir_num = 1
                for obj in selected:
                    if obj == 0:
                        continue
                    #если переименовываю файлы
                    if os.path.isfile(os.path.join(self.file_manager.path, self.file_manager.objects[obj-1][1])):
                        #если файла с таким же именем в системе нет
                        if os.path.exists(os.path.join(self.file_manager.path, self.value)) == False:
                            try:
                                os.rename(os.path.join(self.file_manager.path, self.file_manager.objects[obj-1][1]), os.path.join(self.file_manager.path, self.value))
                            except:
                                pass
                        #если файл с таким же именем уже существует, добавляю _num
                        else:
                            while os.path.exists(os.path.join(self.file_manager.path, "%s_%s%s" %(os.path.splitext(self.value)[0], file_num, os.path.splitext(self.value)[1]))) == True:
                                file_num += 1
                            try:
                                os.rename(os.path.join(self.file_manager.path, self.file_manager.objects[obj-1][1]), os.path.join(self.file_manager.path, 
                                    "%s_%s%s" %(os.path.splitext(self.value)[0],
                                    file_num, os.path.splitext(self.value)[1])))
                                file_num += 1
                            except:
                                pass
                    #если переименовываю каталоги
                    elif os.path.isdir(os.path.join(self.file_manager.path, self.file_manager.objects[obj-1][1])):
                        if os.path.exists(os.path.join(self.file_manager.path, self.value)) == False:
                            try:
                                os.rename(os.path.join(self.file_manager.path, self.file_manager.objects[obj-1][1]), os.path.join(self.file_manager.path, self.value))
                            except:
                                pass
                        #если такой каталог уже существует
                        else:
                            while os.path.exists(os.path.join(self.file_manager.path, "%s_%s" %(self.value, dir_num))) == True:
                                dir_num += 1
                            try:
                                os.rename(os.path.join(self.file_manager.path, self.file_manager.objects[obj-1][1]), os.path.join(self.file_manager.path, "%s_%s" %(self.value, dir_num)))
                                dir_num += 1
                            except:
                                pass
        #обновляю содержимое всех файловых окон
        self.parent.update_panels()

    def get_disk_info(self):
        """выводит информацию и свободной памяти на текущем диске"""
        disk_free = self.convert_bytes(shutil.disk_usage(self.file_manager.path).free)
        disk_total =  self.convert_bytes(shutil.disk_usage(self.file_manager.path).total)
        self.disk_space.configure(text="[свободно %s из %s]" %(disk_free, disk_total))

