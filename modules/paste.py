"""
вставляет вырезанный/скопированный файл/каталог с ведением
прогрессбара в отдельном модальном окне
"""
import tkinter
from tkinter import ttk
import threading
import os
import shutil
from tkinter import messagebox

import modules.modal_windows

class Paste():
    def __init__(self, parent, path="", obj_list=[], mode="copy"):
        """принимает список файлов/каталогов, откуда вставлять,
        и путь, куда вставлять"""
        self.parent = parent
        self.path = path #путь, куда вставляю
        self.obj_list = obj_list #список путей к вставляемым файлам
        self.count = 0 #кол-во файлов
        self.size = 0 #общий размер
        self.value = None
        self.mode = mode #режим copy/move
        self.files_error = 0 #кол-во файлов, которые не удалось вставить
        self.dirs_error = 0 #сколько каталогов не удалось вставить
        self.is_exit = False #флаг, нажал-ли юзер кнопку отмены 

        self.create_window()
        self.make_counting_frame()
        #поток подсчёта файлов для вставки
        self.counting_thr = threading.Thread(target=self.counting_objects)
        self.counting_thr.daemon = True
        self.counting_thr.start()
        #поток вставки
        self.paste_thr = threading.Thread(target=self.paste)
        self.paste_thr.daemon = True
        self.paste_thr.start()
    
    def create_window(self):
        self.window = tkinter.Toplevel()
        self.window.grid_rowconfigure(0, weight=2)
        self.window.grid_columnconfigure(0, weight=2)
        self.window.resizable(width=False, height=False)
        try:
            window_x = self.parent.parent.window.winfo_screenwidth()//2-210
            window_y = self.parent.parent.window.winfo_screenheight()//2-90
            self.window.geometry("420x180+%s+%s" %(window_x, window_y))
        except:
            pass
        self.window.title("вставка объектов")

    def make_counting_frame(self):

        #ПОДСЧЁТ КОЛ-ВА ВСТАВЛЯЕМЫХ ОБЪЕКТОВ
        self.counting_files_frame = tkinter.Frame(self.window)
        self.counting_files_frame.grid_rowconfigure(0, weight=2)
        self.counting_files_frame.grid_rowconfigure(1, weight=2)
        self.counting_files_frame.grid_rowconfigure(2, weight=2)
        self.counting_files_frame.grid_rowconfigure(3, weight=2)
        self.counting_files_frame.grid_columnconfigure(0, weight=2)
        self.counting_files_frame.grid(sticky="wnes", row=0, column=0)
        self.label_text = tkinter.Label(self.counting_files_frame, text="Подсчёт вставляемых файлов", font=('Arial', 10, "bold"))
        self.label_text.grid(sticky="we", row=0, column=0)
        self.counting_files = tkinter.Label(self.counting_files_frame, text="Файлов: %s" %self.count, font=('Calibri', 10, "bold"))
        self.counting_size = tkinter.Label(self.counting_files_frame, text="Общий размер: %s" %self.parent.convert_bytes(self.size), font=('Calibri', 10, "bold"))
        self.cancel_button = tkinter.Button(self.counting_files_frame, text='отмена', command=self._stop, relief="groove")
        #
        self.counting_files.grid(sticky="we", row=1, column=0)
        self.counting_size.grid(sticky="we", row=2, column=0)
        self.cancel_button.grid(sticky="wse", row=3, column=0)


    def counting_objects(self):
        """метод подсчитывает, сколько элементов всего
        вставляется"""
        for obj in self.obj_list:
            if self.is_exit == True:
                self.window.destroy()
                return
            if os.path.isfile(obj):
                self.count+=1
                self.size+=os.stat(obj).st_size
                self.update_files_count_info()
            elif os.path.isdir(obj):
                self.fractal_counting(obj)

    def fractal_counting(self, path):
        '''рекурсивно обходит каталоги, подсчитывая файлы
        и их размеры'''
        try:
            for obj in os.scandir(path):
                if self.is_exit == True:
                    return
                if obj.is_file():
                    self.count+=1
                    self.size+=obj.stat().st_size
                    self.update_files_count_info()
                elif obj.is_dir():
                    self.fractal_counting(obj.path)
        except:
            pass


    def update_files_count_info(self):
        '''обновляет инфо о кол-ве файлов и их общем размере'''
        self.counting_files.configure(text="Файлов: %s" %self.count)
        self.counting_size.configure(text="Общий размер: %s" %self.parent.convert_bytes(self.size))
        self.window.update_idletasks()

    def progress_window(self):      
        '''элементы вставки файлов (прогрессбары, кнопки и т.д.)'''
        #создаю элементы управления
        self.window.grid_rowconfigure(1, weight=2)
        self.window.grid_rowconfigure(2, weight=2)
        self.window.grid_rowconfigure(3, weight=2)
        #текст:
        self.label_text = tkinter.Label(self.window, text="прогресс: 0 из %s" %(self.parent.convert_bytes(self.size)), font=('Arial', 10, "bold"))
        #
        self.label_text_mid = tkinter.Label(self.window, text='"%s"' %(os.path.split(self.obj_list[0])[1]), font=('Arial', 10, "bold"))
        #
        self.label_text_bot = tkinter.Label(self.window, text="0 из %s" %(self.count), font=('Arial', 10, "bold"))
        #
        #прогрессбар одного файла
        self.file_persents = tkinter.IntVar()
        self.file_persents.set(0)
        self.singe_obj_progressbar = tkinter.ttk.Progressbar(self.window, mode="determinate", variable=self.file_persents)

        #прогрессбар всех файлов
        self.pasted_files = tkinter.IntVar()
        self.pasted_files.set(0)
        self.all_obj_progressbar = tkinter.ttk.Progressbar(self.window, mode="determinate", variable=self.pasted_files, maximum=self.count)

        #кнопка отмены
        self.cancel_button = tkinter.Button(self.window, text='отмена', command=self._stop, relief="groove")

        self.label_text.grid(sticky="wse", row=0, column=0)
        self.label_text_mid.grid(sticky="wse", row=1, column=0)
        self.label_text_bot.grid(sticky="wse", row=3, column=0)

        self.singe_obj_progressbar.grid(sticky="wse", row=2, column=0, padx=10, pady=10)
        self.all_obj_progressbar.grid(sticky="wse", row=4, column=0, padx=10, pady=10)
        self.cancel_button.grid(sticky="wse", row=5, column=0)




    def paste(self):
        #жду завершения потока подсчёта
        self.counting_thr.join()
        if self.is_exit == True:
            self.window.destroy()
            return
        #если на диске недостаточно места для вставки
        if shutil.disk_usage(self.path).free < self.size:
            user_answer = tkinter.messagebox.askyesno(title='Внимание!', message='На диске не хватает места для вставки [%s]! Хотите вставить всё, что сможет поместиться?' %self.parent.convert_bytes(self.size-shutil.disk_usage(self.path).free))
            if user_answer == False:
                self.window.destroy()
                return

        #удаляю фрейм с инфой подсчёта
        self.counting_files_frame.destroy()
        #создаю пользовательские элементы вставки
        self.progress_window()

        self.pasted_size = 0 #какой объём данных уже вставлен

        #если был вырезан объект ФС
        if self.mode == "move":
            for obj in self.obj_list:
                if self.is_exit == True:
                    self.window.destroy()
                    return
                #если имена файлов совпадают с именами файлов в конечном каталоге
                if os.path.exists(os.path.join(self.path, os.path.split(obj)[1])):
                    if self.value == 'overwriteall' or self.value == 'renameall':
                        pass
                    else:
                        window = modules.modal_windows.OverwriteOrRename(parent=self, title='Внимание', text='В данном каталоге уже есть "%s"' %(os.path.split(obj)[1]))
                        self.window.wait_window(window.window) #ожидаю закрытия окна
                        self.window.focus_force()
                    if self.value == None:
                        continue
                    elif self.value == 'rename' or self.value == 'renameall':
                        num = 1
                        name = os.path.split(obj)[1]
                        while os.path.exists(os.path.join(self.path, "%s_%s%s" %(os.path.splitext(name)[0], num, os.path.splitext(name)[1]))):
                            num+=1
                        if os.path.isfile(obj):
                            self._file(filename=obj, path=os.path.join(self.path, "%s_%s%s" %(os.path.splitext(name)[0], num, os.path.splitext(name)[1])))
                            os.remove(obj) #удаляю исходный файл после вставки
                        elif os.path.isdir(obj):
                            self._fractal(dirname=obj, path=os.path.join(self.path, "%s_%s%s" %(os.path.splitext(name)[0], num, os.path.splitext(name)[1])))
                            shutil.rmtree(obj, True) #удаляю исходный каталог после вставки
                    elif self.value == 'overwrite' or self.value == 'overwriteall':
                        #если пытается перезаписать один и тот-же файл
                        if os.path.join(self.path, os.path.split(obj)[1]) == obj:
                            break
                        if os.path.isfile(obj):
                            self._file(filename=obj, path=os.path.join(self.path, os.path.split(obj)[1]))
                            os.remove(obj) #удаляю исходный файл после вставки
                        #если такой каталог уже есть в исходной папке
                        elif os.path.isdir(obj):
                            #рекурсивных обход каталога
                            self._fractal(dirname=obj, path=os.path.join(self.path, os.path.split(obj)[1]))
                            shutil.rmtree(obj, True) #удаляю исходный каталог после вставки
                #если-же не обнаружено совпадений имён
                else:
                    #если пытается перезаписать один и тот-же файл
                    if os.path.join(self.path, os.path.split(obj)[1]) == obj:
                        break
                    if os.path.isfile(obj):
                        self._file(filename=obj, path=os.path.join(self.path, os.path.split(obj)[1]))
                        os.remove(obj) #удаляю исходный файл после вставки
                    #если такой каталог уже есть в исходной папке, удаляю его
                    elif os.path.isdir(obj):
                        #рекурсивных обход каталога
                        self._fractal(dirname=obj, path=os.path.join(self.path, os.path.split(obj)[1]))
                        shutil.rmtree(obj, True)
                    
        #если был скопирован объект ФС
        elif self.mode == "copy":
            for obj in self.obj_list:
                if os.path.exists(os.path.join(self.path, os.path.split(obj)[1])):
                    if self.value == 'overwriteall' or self.value == 'renameall':
                        pass
                    else:
                        window = modules.modal_windows.OverwriteOrRename(parent=self, title='Внимание', text='В данном каталоге уже есть "%s"' %(os.path.split(obj)[1]))
                        self.window.wait_window(window.window) #ожидаю закрытия окна
                        self.window.focus_force()
                    if self.value == None:
                        continue
                    elif self.value == 'rename' or self.value == 'renameall':
                        num = 1
                        name = os.path.split(obj)[1]
                        while os.path.exists(os.path.join(self.path, "%s_%s%s" %(os.path.splitext(name)[0], num, os.path.splitext(name)[1]))):
                            num+=1
                        if os.path.isfile(obj):
                            self._file(filename=obj, path=os.path.join(self.path, "%s_%s%s" %(os.path.splitext(name)[0], num, os.path.splitext(name)[1])))
                        elif os.path.isdir(obj):
                            self._fractal(dirname=obj, path=os.path.join(self.path, "%s_%s%s" %(os.path.splitext(name)[0], num, os.path.splitext(name)[1])))

                    elif self.value == 'overwrite' or self.value == 'overwriteall':
                        #если пытается перезаписать один и тот-же файл
                        if os.path.join(self.path, os.path.split(obj)[1]) == obj:
                            break
                        if os.path.isfile(obj):
                            self._file(filename=obj, path=os.path.join(self.path, os.path.split(obj)[1]))
                        #если такой каталог уже есть в исходной папке, удаляю его
                        elif os.path.isdir(obj):
                            #рекурсивных обход каталога
                            self._fractal(dirname=obj, path=os.path.join(self.path, os.path.split(obj)[1]))

                #если-же совпадений имён обнаружено не было
                else:
                    #если пытается перезаписать один и тот-же файл
                    if os.path.join(self.path, os.path.split(obj)[1]) == obj:
                        break
                    if os.path.isfile(obj):
                        self._file(filename=obj, path=os.path.join(self.path, os.path.split(obj)[1]))
                    elif os.path.isdir(obj):
                        self._fractal(dirname=obj, path=os.path.join(self.path, os.path.split(obj)[1]))

        #если при вставке возникли ошибки
        if self.dirs_error != 0 and self.files_error != 0:
            tkinter.messagebox.showwarning(title='Внимание!', message='Не удалось вставить %s файлов, %s каталогов!' %(self.files_error, self.dirs_error))
        elif self.files_error != 0:
            tkinter.messagebox.showwarning(title='Внимание!', message='Не удалось вставить %s файлов!' %self.files_error)
        elif self.dirs_error != 0:
            tkinter.messagebox.showwarning(title='Внимание!', message='Не удалось вставить %s каталогов!' %self.dirs_error)

        #Обновляю файловые окна. Закрываю окно вставки
        self.parent.parent.cut = None
        self.parent.parent.update_panels()
        self.window.destroy()

    def _fractal(self, dirname="", path=""):
        '''рекурсивно обходит каталог dirname, выполняя
        определённые действия в нём'''
        try:
            if self.is_exit == True:
                return
            #если каталога нет
            if not os.path.exists(path):
                #создаю его
                os.makedirs(path)
            for obj in os.scandir(dirname):
                if obj.is_file():
                    # if 
                    self._file(filename=obj.path, path=os.path.join(path, obj.name))
                elif obj.is_dir():
                    self._fractal(dirname=obj.path, path=os.path.join(path, obj.name))
        except:
            self.dirs_error += 1

    def _file(self, filename="", path=""):
        '''метод для вставки файла
        filename-исходный файл
        path-путь для вставки файла'''
        try:
            file_size = os.stat(filename).st_size #сколько байт в файле
            pasted_bytes = 0 #кол-во вставленных байтов одного файла
            persents = 0
            #какой файл вставляется в данный момент        
            self.label_text_mid.configure(text='"%s", %s' %(os.path.split(filename)[1], self.parent.convert_bytes(file_size)))
            self.label_text_bot.configure(text="%s из %s" %(self.pasted_files.get(), self.count))
            file = open(filename, 'rb') #файл, который нужно скопировать
            pasting_file = open(path, 'wb') #вставляемый файл

            while True:
                if self.is_exit == True:
                    return
                self.label_text.configure(text="Вставлено: %s из %s" %(self.parent.convert_bytes(self.pasted_size), self.parent.convert_bytes(self.size)))
                if file_size >  0:
                    persents = int(pasted_bytes/file_size*100) #сколько это в процентах
                    self.file_persents.set(persents)

                #чем выше число, тем быстрее вставляются файлы, но тем больше грузит ОЗУ и диск
                b = file.read(1000000)
                if not b:
                    file.close()
                    pasting_file.close()
                    break
                pasting_file.write(b)
                pasted_bytes+=len(b)
                self.pasted_size += len(b)
                self.window.update_idletasks()
            self.pasted_files.set(self.pasted_files.get()+1)
        except:
            self.files_error += 1

    def _stop(self):
        self.is_exit = True
