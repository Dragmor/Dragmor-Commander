import tkinter
import os
import os.path
from tkinter import messagebox
import tkinter.filedialog


class App():
    """просмотрщик png/gif/ppm/pgm"""
    def __init__(self, path=None):
        self.path = path
        self.image = None
        self.create_window()
        self.create_user_elements()
        if self.path != None:
            temp = ""
            for p in self.path:
                temp += ("%s/" %(p,))
            self.path = os.path.normpath(temp)
            self.load_file()
        self.window.mainloop()


    def create_window(self):
        self.window = tkinter.Tk()
        self.window.title("ImageViewer")
        # self.window.geometry('800x480')
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
        # self.cascade_files.add_command(label='Сохранить',
        #          command=self.save_file)
        # self.cascade_files.add_command(label='Сохранить как...',
        #          command=self.save_as)
        # self.cascade_files.add_separator()
        # self.codecs = tkinter.Menu(self.cascade_files, tearoff=0)
        # self.cascade_files.insert_cascade(5, menu=self.codecs, label='Кодировка...')
        # self.codecs.add_command(label='UTF-8', command=(lambda self=self, codec="utf-8": self.change_codec(codec)))
        # self.codecs.add_command(label='mbcs', command=(lambda self=self, codec="mbcs": self.change_codec(codec)))
        # self.codecs.add_command(label='ascii', command=(lambda self=self, codec="ascii": self.change_codec(codec)))
        # self.codecs.add_command(label='cp1252', command=(lambda self=self, codec="cp1252": self.change_codec(codec)))
        # self.codecs.add_command(label='UTF-16', command=(lambda self=self, codec="utf-16": self.change_codec(codec)))
        # self.codecs.add_command(label='Latin-1', command=(lambda self=self, codec="latin-1": self.change_codec(codec)))

        self.cascade_files.add_separator()
        self.cascade_files.add_command(label='Выйти',
                 command=exit)

        #канвас
        self.canvas = tkinter.Canvas(self.main_frame)
        self.canvas.grid(sticky='swen', row=0, column=0)
        #нижняя инфо-панель
        self.info_panel = tkinter.Label(self.window, font='Terminal', width=1, anchor='w')
        self.info_panel.grid(row=1, column=0, sticky="w, e")
        #захват для изменения размера окна
        self.sizegrip = tkinter.ttk.Sizegrip(self.window)
        self.sizegrip.grid(row=1, column=0, sticky='e, s')
        self.print_to_info_panel()
        #
        self.window.bind_all("<Control-Shift-KeyPress>", self.check_event)
        self.window.bind_all("<Control-KeyPress>", self.check_event)

    def print_to_info_panel(self):
        text = ""
        # if self.path != None:
        #     text += "файл:[%s]  " %self.path
        # if self.codec != None:
        #     text += "кодировка:[%s]  " %self.codec
        # if self.font.configure()['family'] != "":
        #     text += "шрифт:[%s]  " %self.font.configure()['family']
        # self.info_panel.configure(text=text)

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
            self.path = filename
            self.load_file()


    def load_file(self):
        self.image = None
        if os.path.isfile(self.path):
            self.image = tkinter.PhotoImage(file=self.path)
        self.draw_image()

    def draw_image(self):
        self.canvas.create_image(self.image.width()//2, self.image.height()//2, image=self.image)
        self.window.geometry("%sx%s" %(self.image.width(), self.image.height()+25))
    

if __name__ == "__main__":
    app = App()

'''
HotKeys:

'''