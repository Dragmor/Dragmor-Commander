import tkinter
from tkinter import ttk
import threading
import os
import shutil
from tkinter import messagebox

class Deleter():
    def __init__(self, parent, obj_list=[]):
        """принимает список файлов/каталогов, которые подлежат удалению"""
        self.parent = parent
        self.obj_list = obj_list #список путей удаляемых файлов
        self.files_to_delete = [] #список путей ко всем удаляемым файлам
        self.dirs_to_delete = [] #список удаляемых каталогов
        self.count = 0 #кол-во файлов
        self.size = 0 #общий размер
        self.deleted_size = 0 #размер удалённых файлов
        self.files_error = 0 #кол-во файлов, которые не удалось удалить
        self.is_exit = False #флаг, нажал-ли юзер кнопку отмены 

        self.create_window()
        self.make_counting_frame()
        #поток подсчёта файлов для удаления
        self.counting_thr = threading.Thread(target=self.counting_objects)
        self.counting_thr.daemon = True
        self.counting_thr.start()
        #поток удаления
        self.paste_thr = threading.Thread(target=self._delete)
        self.paste_thr.daemon = True
        self.paste_thr.start()
    
    def create_window(self):
        self.window = tkinter.Toplevel()
        self.window.grid_rowconfigure(0, weight=2)
        self.window.grid_columnconfigure(0, weight=2)
        self.window.resizable(width=False, height=False)
        try:
            window_x = self.parent.parent.window.winfo_screenwidth()//2-180
            window_y = self.parent.parent.window.winfo_screenheight()//2-60
            self.window.geometry("360x120+%s+%s" %(window_x, window_y))
        except:
            pass
        self.window.title("удаление объектов")

    def make_counting_frame(self):

        #ПОДСЧЁТ КОЛ-ВА УДАЛЯЕМЫХ ОБЪЕКТОВ
        self.counting_files_frame = tkinter.Frame(self.window)
        self.counting_files_frame.grid_rowconfigure(0, weight=2)
        self.counting_files_frame.grid_rowconfigure(1, weight=2)
        self.counting_files_frame.grid_rowconfigure(2, weight=2)
        self.counting_files_frame.grid_rowconfigure(3, weight=2)
        self.counting_files_frame.grid_columnconfigure(0, weight=2)
        self.counting_files_frame.grid(sticky="wnes", row=0, column=0)
        self.label_text = tkinter.Label(self.counting_files_frame, text="Подсчёт удаляемых файлов", font=('Arial', 10, "bold"))
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
        удаляется"""
        for obj in self.obj_list:
            if self.is_exit:
                self.window.destroy()
                return
            if os.path.isfile(obj):
                self.count+=1
                self.size+=os.stat(obj).st_size
                self.files_to_delete.append(obj)
                self.update_files_count_info()
            elif os.path.isdir(obj):
                self.dirs_to_delete.append(obj)
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
                    self.files_to_delete.append(obj.path)
                    self.update_files_count_info()
                elif obj.is_dir():
                    self.dirs_to_delete.append(obj)
                    self.fractal_counting(obj.path)
        except:
            pass


    def update_files_count_info(self):
        '''обновляет инфо о кол-ве файлов и их общем размере'''
        self.counting_files.configure(text="Файлов: %s" %self.count)
        self.counting_size.configure(text="Общий размер: %s" %self.parent.convert_bytes(self.size))
        self.window.update_idletasks()

    def progress_window(self):      
        '''создаю элементы управления (прогрессбары, кнопки и т.д.)'''
        #создаю элементы управления
        self.window.grid_rowconfigure(1, weight=2)
        self.window.grid_rowconfigure(2, weight=2)
        #текст:
        self.label_text = tkinter.Label(self.window, text="удалено: 0 из %s" %(self.parent.convert_bytes(self.size)), font=('Arial', 10, "bold"))
        
        #прогрессбар
        self.file_persents = tkinter.IntVar()
        self.file_persents.set(0)
        self.all_obj_progressbar = tkinter.ttk.Progressbar(self.window, mode="determinate", variable=self.file_persents, maximum=self.count)

        #кнопка отмены
        self.cancel_button = tkinter.Button(self.window, text='отмена', command=self._stop, relief="groove")

        self.label_text.grid(sticky="wse", row=0, column=0)
        self.all_obj_progressbar.grid(sticky="wse", row=1, column=0, padx=10, pady=10)
        self.cancel_button.grid(sticky="wse", row=2, column=0)

    def _delete(self):
        '''метод удаляет файлы и каталоги'''
        #жду завершения подсчёта файлов
        self.counting_thr.join()
        if self.is_exit == True:
            self.window.destroy()
            return
        #удаляю фрейм с инфой подсчёта
        self.counting_files_frame.destroy()
        #создаю пользовательские элементы
        self.progress_window()
        for obj in self.files_to_delete:
            if self.is_exit:
                break
            try:
                self.deleted_size += os.stat(obj).st_size
                os.remove(obj)
            except:
                self.files_error += 1
            self.label_text.configure(text="удалено: %s из %s" %(self.parent.convert_bytes(self.deleted_size), self.parent.convert_bytes(self.size)))
        for obj in self.dirs_to_delete:
            if self.is_exit:
                break
            try:
                shutil.rmtree(obj)
            except:
                pass
        #если при удалении возникли ошибки
        if self.files_error != 0:
            if self.is_exit == False:
                tkinter.messagebox.showwarning(title='Внимание!', message='Не удалось удалить %s файлов!' %self.files_error)
        self.parent.parent.update_panels()
        self.window.destroy()

        

    def _stop(self):
        self.is_exit = True
