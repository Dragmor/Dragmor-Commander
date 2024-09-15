import tkinter

"""
тут прописаны модальные окна для различных ситуаций
"""

class GetName():
    '''модальное окно для переименовывания и создания папок и файлов'''
    def __init__(self, parent=None, title='', text='', entry_text=''):
        self.title = title
        self.text = text
        self.entry_text = entry_text
        self.parent = parent
        self.create_window()

    def create_window(self):
        self.window = tkinter.Toplevel(self.parent.frame)
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

class OverwriteOrRename():
    '''модальное окно запроса при вставке файлов, если их имена совпадают'''
    def __init__(self, parent=None, title='', text=''):
        self.title = title
        self.text = text
        self.choose = None
        self.parent = parent
        self.parent.value = self.choose
        self.create_window()

    def create_window(self):
        self.window = tkinter.Toplevel(self.parent.window)
        self.window.focus()
        self.window.grid_columnconfigure(0, weight=2)
        self.window.grid_rowconfigure(0, weight=2)
        #задаю положение модального окна
        try:
            window_x = self.parent.parent.parent.window.winfo_screenwidth()//2-290
            window_y = self.parent.parent.parent.window.winfo_screenheight()//2-70
            self.window.geometry("580x140+%s+%s" %(window_x, window_y))
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
        self.button_rename_all = tkinter.Button(self.buttons_frame, text='Переименовать все', width=15, command=self.pressed_rename_all, relief="groove")
        self.button_overwrite = tkinter.Button(self.buttons_frame, text='Заменить', width=15, command=self.pressed_overwrite, relief="groove")
        self.button_overwrite_all = tkinter.Button(self.buttons_frame, text='Заменить все', width=15, command=self.pressed_overwrite_all, relief="groove")
        self.button_cancel = tkinter.Button(self.buttons_frame, text='Отмена', width=15, command=self.pressed_cancel, relief="groove")
        self.text_label.grid(row=0, sticky='swen')
        self.button_rename.grid(row=0, sticky='swen', column=0)
        self.button_rename_all.grid(row=0, sticky='swen', column=1)
        self.button_overwrite.grid(row=0, sticky='swen', column=2)
        self.button_overwrite_all.grid(row=0, sticky='swen', column=3)
        self.button_cancel.grid(row=0, sticky='swen', column=4)

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

    def pressed_rename_all(self, *args):
        self.choose = 'renameall'
        self.parent.value = self.choose
        self.window.destroy()

    def pressed_cancel(self, *args):
        self.choose = None
        self.parent.value = self.choose
        self.window.destroy()
