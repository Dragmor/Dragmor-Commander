import tkinter
import os
from tkinter import ttk
from tkinter import messagebox
import tkinter.filedialog
from PIL import Image, ImageTk


class App():
    """просмотрщик изображений"""
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
        self.window.minsize(320, 320)
        self.window.title("ImageViewer")
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

        self.menu.add_cascade(label='Файл', menu=self.cascade_files)

        self.cascade_files.add_command(label='Открыть',
                 command=self.open_file)
        self.cascade_files.add_separator()
        self.cascade_files.add_command(label='Выйти',
                 command=exit)

        #канвас
        self.canvas = tkinter.Canvas(self.main_frame)
        self.canvas.grid(sticky='swen', row=0, column=0)
        #нижняя инфо-панель
        self.info_panel = tkinter.Label(self.window, font=('Calibri', 8, 'bold'), width=1, anchor='w')
        self.info_panel.grid(row=1, column=0, sticky="w, e")
        #захват для изменения размера окна
        self.sizegrip = tkinter.ttk.Sizegrip(self.window)
        self.sizegrip.grid(row=1, column=0, sticky='e, s')
        #
        self.window.bind_all("<Control-Shift-KeyPress>", self.check_event)
        self.window.bind_all("<Control-KeyPress>", self.check_event)
        self.window.bind_all("<MouseWheel>", self.zoom)

    def print_to_info_panel(self):
        if self.path != None:
            text = "[%s]  " %self.file_name
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

    def zoom(self, event):
        '''метод зумит изображение по колёсику мыши'''
        #уменьшаю размер
        if event.delta < 0:
            self.pillow_image.resize((100,100))
            self.image = ImageTk.PhotoImage(self.pillow_image)
        #увеличиваю
        else:
            self.pillow_image.resize((400,400))
            self.image = ImageTk.PhotoImage(self.pillow_image)
        self.canvas.create_image(self.image.width()//2, self.image.height()//2, image=self.image)

    def open_file(self):
        filename = tkinter.filedialog.askopenfilename()
        if filename != '':
            self.path = filename
            self.load_file()


    def load_file(self):
        self.image = None
        if os.path.isfile(self.path):
            self.pillow_image = Image.open(self.path)
            self.image = ImageTk.PhotoImage(self.pillow_image)
        self.file_name = os.path.split(self.path)[-1]
        self.print_to_info_panel()
        self.draw_image()

    def draw_image(self):
        #распологаю изображение в середине канваса
        center_x = 0
        center_y = 0
        #центрирую изображение, если оно меньше минимальных размеров окна
        if self.image.width() < 320:
            center_x = 320//2-self.image.width()//2
        if self.image.height() < 320:
            center_y = 320//2-self.image.height()//2

        self.canvas.create_image(center_x+self.image.width()//2, center_y+self.image.height()//2, image=self.image)
        self.window.geometry("%sx%s" %(self.image.width(), self.image.height()+25))
    

if __name__ == "__main__":
    app = App()

'''
HotKeys:

'''