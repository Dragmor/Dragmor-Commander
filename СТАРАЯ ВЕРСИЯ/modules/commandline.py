import tkinter
import subprocess
import threading
import os

class App():
    """командная консоль"""
    def __init__(self, path=None):
        self.path = path
        self.create_window()
        self.create_user_elements()
        if self.path != None:
            temp = ""
            for p in self.path:
                temp += ("%s/" %(p,))
            self.path = os.path.normpath(temp)
            self.command_entry.insert(0, '"%s"' %self.path)
            self.pre_execute()
        self.window.mainloop()


    def create_window(self):
        self.window = tkinter.Tk()
        self.window.title("CommandConsole")
        self.window.geometry('800x480')
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        self.main_frame = tkinter.Frame(self.window)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.main_frame.grid(sticky="w, n, e, s")

    def create_user_elements(self):
        self.command_entry = tkinter.Entry(self.main_frame, border=3)
        self.console_output = tkinter.Listbox(self.main_frame, relief="sunken", activestyle='none', bg='black', fg='green', height=15, border=5)
        self.console_output.bind("<Double-ButtonPress>", self.copy_text_to_entry)
        self.command_entry.bind("<Key-Return>", self.pre_execute)
        #
        self.console_output.grid(sticky="w, n, e, s")
        self.command_entry.grid(sticky="w, n, e, s", row=1)
        #
        self.command_entry.focus()

    def pre_execute(self, *args):
        command = self.command_entry.get()
        thread = threading.Thread(target=self.execute_command, args=(command,))
        thread.daemon = True
        thread.start()

    def execute_command(self, command):
        cmd = subprocess.getoutput(command)
        self.write_to_output(cmd)

    def write_to_output(self, data):
        #если командная строка виндовая, то меняю кодировку выходного текста
        if os.name == 'nt' or os.name == 'rt':
            data = data.encode('mbcs')
            data = data.decode('cp866')
        data = data.split('\n')
        for d in data:
            self.console_output.insert(self.console_output.size(), d)
        self.console_output.see(self.console_output.size())

    def copy_text_to_entry(self, event):
        self.command_entry.delete(0, len(self.command_entry.get()))
        self.command_entry.insert(0, self.console_output.get(self.console_output.curselection()))
        self.console_output.get(self.console_output.curselection()) #получаю текст выбранного пункта
        self.command_entry.focus()

if __name__ == "__main__":
    app = App()