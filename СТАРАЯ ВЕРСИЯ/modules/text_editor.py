import tkinter
import os.path
from tkinter import messagebox
import tkinter.filedialog
import tkinter.font
import tkinter.ttk
try:
    from tkinter import scrolledtext
except:
    pass

class App():
    """текстовый редактор"""
    def __init__(self, path=None):
        self.path = path
        self.codec = None
        self.text = None
        if self.path != None:
            temp = ""
            for p in self.path:
                temp += ("%s/" %(p,))
            self.path = os.path.normpath(temp)
            self.text = self.load_file()
        self.create_window()
        self.font = tkinter.font.Font(self.window)
        self.create_user_elements()
        self.load_text()
        self.window.mainloop()


    def create_window(self):
        self.window = tkinter.Tk()
        self.window.title("TextEditor")
        self.window.geometry('800x480')
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        self.main_frame = tkinter.Frame(self.window)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.main_frame.grid(sticky="w, n, e, s")

    def create_user_elements(self):
        self.menu = tkinter.Menu(self.main_frame)
        self.window.config(menu=self.menu)
        self.cascade_files = tkinter.Menu(self.menu, tearoff=0)
        self.view = tkinter.Menu(self.menu, tearoff=0)


        self.menu.add_cascade(label='Файл', menu=self.cascade_files)
        self.menu.add_cascade(label='Вид', menu=self.view)


        self.cascade_files.add_command(label='Открыть',
                 command=self.open_file)
        self.cascade_files.add_command(label='Сохранить',
                 command=self.save_file)
        self.cascade_files.add_command(label='Сохранить как...',
                 command=self.save_as)
        self.cascade_files.add_separator()
        self.codecs = tkinter.Menu(self.cascade_files, tearoff=0)
        self.cascade_files.insert_cascade(5, menu=self.codecs, label='Кодировка...')
        self.codecs.add_command(label='UTF-8', command=(lambda self=self, codec="utf-8": self.change_codec(codec)))
        self.codecs.add_command(label='mbcs', command=(lambda self=self, codec="mbcs": self.change_codec(codec)))
        self.codecs.add_command(label='ascii', command=(lambda self=self, codec="ascii": self.change_codec(codec)))
        self.codecs.add_command(label='cp1252', command=(lambda self=self, codec="cp1252": self.change_codec(codec)))
        self.codecs.add_command(label='UTF-16', command=(lambda self=self, codec="utf-16": self.change_codec(codec)))
        self.codecs.add_command(label='Latin-1', command=(lambda self=self, codec="latin-1": self.change_codec(codec)))

        self.cascade_files.add_separator()
        self.cascade_files.add_command(label='Выйти',
                 command=exit)
        #выбор шрифта
        self.fonts = tkinter.Menu(self.view, tearoff=0)
        self.view.insert_cascade(1, menu=self.fonts, label='Шрифт')
        self.fonts.add_command(label='Arial', command=(lambda self=self, font="Arial": self.change_font(font)))
        self.fonts.add_command(label='Courier New', command=(lambda self=self, font="Courier New": self.change_font(font)))
        self.fonts.add_command(label='Terminal', command=(lambda self=self, font="Terminal": self.change_font(font)))
        self.fonts.add_command(label='Modern', command=(lambda self=self, font="Modern": self.change_font(font)))
        self.fonts.add_command(label='System', command=(lambda self=self, font="System": self.change_font(font)))
        #размеры шрифта
        self.font_size = tkinter.Menu(self.view, tearoff=0)
        self.view.insert_cascade(1, menu=self.font_size, label='Размер шрифта')
        self.font_size.add_command(label='8', command=(lambda self=self, size=8: self.change_font_size(size)))
        self.font_size.add_command(label='10', command=(lambda self=self, size=10: self.change_font_size(size)))
        self.font_size.add_command(label='12', command=(lambda self=self, size=12: self.change_font_size(size)))
        self.font_size.add_command(label='14', command=(lambda self=self, size=14: self.change_font_size(size)))
        self.font_size.add_command(label='16', command=(lambda self=self, size=16: self.change_font_size(size)))
        self.font_size.add_command(label='18', command=(lambda self=self, size=18: self.change_font_size(size)))
        #
        try:
            self.text_field = tkinter.scrolledtext.ScrolledText(self.main_frame, font=("size:30"), undo=True)
        except:
            self.text_field = tkinter.Text(self.main_frame)
        self.text_field.grid(sticky="w, n, e, s", column=0, row=0)
        #нижняя инфо-панель
        self.info_panel = tkinter.Label(self.window, font='Terminal', width=1, anchor='w')
        self.info_panel.grid(row=1, column=0, sticky="w, e")
        #захват для изменения размера окна
        self.sizegrip = tkinter.ttk.Sizegrip(self.window)
        self.sizegrip.grid(row=1, column=0, sticky='e, s')
        self.print_to_info_panel()
        #
        self.text_field.focus()
        self.window.bind_all("<Control-Shift-KeyPress>", self.check_event)
        self.window.bind_all("<Control-KeyPress>", self.check_event)

    def print_to_info_panel(self):
        text = ""
        if self.path != None:
            text += "файл:[%s]  " %self.path
        if self.codec != None:
            text += "кодировка:[%s]  " %self.codec
        if self.font.configure()['family'] != "":
            text += "шрифт:[%s]  " %self.font.configure()['family']
        self.info_panel.configure(text=text)

    def check_event(self, event):
        #ctrl+shift+z
        if event.keycode == 90 and event.state == 13:
            try:
                self.text_field.edit_redo()
            except:
                pass
        #ctrl+z
        elif  event.keycode == 90:
            try:
                self.text_field.edit_undo()
            except:
                pass
        #ctrl-shift-s
        elif event.keycode == 83 and event.state == 13:
            self.save_as()
        #ctrl-s
        elif event.keycode == 83:
            self.save_file()


    def change_font(self, font=None):
        if font == None:
            return
        self.font.configure(family=font)
        self.text_field.configure(font=self.font)
        self.print_to_info_panel()

    def change_font_size(self, size=None):
        if size==None:
            return
        self.font.configure(size=size)
        self.text_field.configure(font=self.font)
        self.print_to_info_panel()


    def load_text(self):
        if self.text != None:
            self.text_field.replace('current', 'end', self.text)
            

    def change_codec(self, codec=None):
        if codec != None:
            try:
                self.text_field.replace('current', 'end', self.text.decode(codec))
                self.codec = codec
            except:
                tkinter.messagebox.showwarning(title='Не удалось изменить кодировку', message='Данная кодировка не подходит для этого файла! Попробуйте выбрать другую кодировку!') 
            self.print_to_info_panel()
    def open_file(self):
        filename = tkinter.filedialog.askopenfilename()
        if filename != '':
            file = open(filename, 'rb')
            self.text = file.read()
            file.close()
            self.path = filename
            self.text_field.replace('current', 'end', self.text)
        self.print_to_info_panel()

    def save_file(self):
        if self.path != None:
            try:
                file = open(self.path, "wb")
            except:
                tkinter.messagebox.showerror(title='Не удалось сохранить файл', message='Возможно, у Вас недостаточно прав для сохранения! Попробуйте выбрать другой каталог!') 
                self.save_as()
                return
            if self.codec == None:
                text = self.text_field.get(index1='current' ,index2='end').encode()
            else:
                text = self.text_field.get(index1='current' ,index2='end').encode(self.codec)
            try:
                file.write(text)
            except:
                tkinter.messagebox.showerror(title='Не удалось сохранить файл', message='Вероятно, проблема в кодировке файла! Попробуйте выбрать другую кодировку!') 
                return
            file.close()
            self.text = text
        else:
            self.save_as()
        self.print_to_info_panel()

    def save_as(self):
        name = ".txt"
        if self.path != None:
            name = "%s" %(os.path.split(self.path)[1])

        filename = tkinter.filedialog.asksaveasfilename(initialfile='%s' %name)
        if filename != '':
            try:
                file = open(filename, 'wb')
            except:
                tkinter.messagebox.showerror(title='Не удалось сохранить файл', message='Возможно, у Вас недостаточно прав для сохранения! Попробуйте выбрать другой каталог!') 
                return
            if self.codec == None:
                text = self.text_field.get(index1='current' ,index2='end').encode()
            else:
                text = self.text_field.get(index1='current' ,index2='end').encode(self.codec)
            try:
                file.write(text)
            except:
                tkinter.messagebox.showerror(title='Не удалось сохранить файл', message='Вероятно, проблема в кодировке файла! Попробуйте выбрать другую кодировку!') 
                return
            file.close()
            self.text = text
            self.path = filename
        self.print_to_info_panel()

    def load_file(self):
        if os.path.isfile(self.path):
            file = open(self.path, 'rb')
            text = file.read()
            file.close()
            return text
        return None
    

if __name__ == "__main__":
    app = App()

'''
HotKeys:
-ctrl+s (save file)
-ctrl+shift+s (save as)
-ctrl+z (undo)
-ctrl+shift+z (redo)
-ctrl+a (select all text (ENG only))
'''