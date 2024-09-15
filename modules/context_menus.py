"""
реализует контекстное меню для мыши с разным содержимым
"""
import tkinter
import os
import subprocess

class Menu():
    def __init__(self, parent):
        self.parent = parent



    def show_menu(self, x, y):
        #контекстное меню по нажатию ПКМ

        selected = self.parent.get_selected_field()

        context_menu = tkinter.Menu(self.parent.frame, tearoff=0)
        #если ПКМ была по пункту перехода вверх
        if selected == [0]:
            context_menu.add_command(label='открыть', command=self.parent._open)
            context_menu.add_command(label='открыть в новой вкладке', command=self.parent.add_tab_with_path)

        #если ПКМ была нажата, но не был выбран ни один пункт (по пустому пространству)
        elif selected == []:
            if os.name == 'nt' or os.name == 'rt':
                context_menu.add_command(label='открыть в проводнике', command=(lambda self=self, path=self.parent.file_manager.path: subprocess.getoutput('explorer "%s"' %path)))
            if self.parent.parent.cut != None or self.parent.parent.copy != None:
                context_menu.add_command(label='вставить', command=self.parent._paste)
            context_menu.add_command(label='создать каталог', command=self.parent._make_dir)
            context_menu.add_command(label='обновить', command=self.parent.show_dir)
        #
        else:
            context_menu.add_command(label='открыть', command=self.parent._open)
            #если был выбран 1 пункт, и это каталог
            if len(selected) == 1:
                if self.parent.file_manager.objects[selected[0]-1][0] == "d":
                    if os.name == 'nt' or os.name == 'rt':
                        context_menu.add_command(label='открыть в проводнике', command=(lambda self=self, path=os.path.join(self.parent.file_manager.path, self.parent.file_manager.objects[selected[0]-1][1]): subprocess.getoutput('explorer "%s"' %path)))
                    context_menu.add_command(label='открыть в новой вкладке', command=self.parent.add_tab_with_path)
                #если отмечен 1 пункт, и это файл
                elif self.parent.file_manager.objects[selected[0]-1][0] == "f":
                    #если инструменты были заимпортированы
                    if self.parent.parent.instruments != []:
                        #выпадающее доп. меню "открыть через..."
                        open_as_cascade = tkinter.Menu(context_menu, tearoff=0)
                        for inst in self.parent.parent.instruments:
                            open_as_cascade.add_command(label=inst[1], command=(lambda self=self,
                             parent=self.parent, instrument=inst[0]: parent.parent.run_instrumente(instrument=instrument, args=parent.get_args())))
                        context_menu.insert_cascade(2, menu=open_as_cascade, label='открыть через...')



            context_menu.add_command(label='открыть с помощью...', command=self.parent._open_as)
            context_menu.add_command(label='копировать', command=self.parent._copy)
            context_menu.add_command(label='вырезать', command=self.parent._cut)

            #если не выбран файл/каталог для вставки, не вывожу этот пункт меню
            if self.parent.parent.cut != None or self.parent.parent.copy != None:
                context_menu.add_command(label='вставить', command=self.parent._paste)

            context_menu.add_command(label='переименовать', command=self.parent._rename)
            context_menu.add_command(label='создать каталог', command=self.parent._make_dir)
            context_menu.add_command(label='удалить', command=self.parent._delete)

        context_menu.post(x, y)
