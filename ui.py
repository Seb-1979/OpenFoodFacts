# coding : utf-8

from tkinter import *
from tkinter.font import Font


class Chevron(Button):
    '''
    Cette classe définit un bouton qui permet de réduire ou d'afficher un
    widget quand l'utilisateur clique dessus.
    '''
    def __init__(self, widget, parent=None, **options):
        Button.__init__(self, parent, **options)
        self.widget = widget
        self.config(bd=5, text="Cacher", compound=LEFT)
        self.config(command=self.action_button)
        self._chevron = "down"
        self._down_chevron = PhotoImage(file="images/chevron_bas.gif")
        self._right_chevron = PhotoImage(file="images/chevron_droite.gif")
        self.config(image=self._down_chevron)

    def action_button(self):
        if self._chevron == "down":
            self.config(image=self._right_chevron, text="Montrer")
            self._chevron = "right"
            self.widget.grid_remove()
        elif self._chevron == "right":
            self.config(image=self._down_chevron, text="Cacher")
            self._chevron = "down"
            self.widget.grid()


class FilterList(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        lab = Label(self, text="Filtrer :", padx=10)
        lab.grid(row=0, column=0)
        self.entry = Entry(self, width=20)
        self.entry.grid(row=0, column=1)
        self.__listbox_init().grid(row=1, column=0, columnspan=2, sticky="we")


    def __listbox_init(self):
        f = Frame(self)
        scrollbar = Scrollbar(f)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.__listbox = Listbox(f, yscrollcommand=scrollbar.set)
        self.__listbox.pack(fill=X)
        scrollbar.config(command=self.__listbox.yview)
        return f

    def list_insert(self, item):
        for i in item:
            self.__listbox.insert(END, i)


class UI:
    def __init__(self):
        self._root = Tk()
        self._root.title("Changer son alimentation")
        self._root.geometry("800x600")

        f1 = FilterList(self._root, bd=3, relief=RIDGE)
        b1 = Chevron(f1)
        l1 = Label(self._root, text="Les catégories", padx=10)
        b1.grid(row=0, column=0, sticky="nw")
        l1.grid(row=0, column=1, sticky="we")
        f1.grid(row=1, column=0, columnspan=2, sticky="we")

        f2 = FilterList(self._root, bd=3, relief=RIDGE)
        b2 = Chevron(f2)
        l2 = Label(self._root, text="Les aliments", padx=10)
        b2.grid(row=2, column=0, sticky="nw")
        l2.grid(row=2, column=1, sticky="we")
        f2.grid(row=3, column=0, columnspan=2, sticky="we")

        f1.list_insert([i for i in range(21)])
        f2.list_insert([i for i in range(21)])

    def print_categories(self, parent):
        pass

    def print_food(self, parent):
        pass

    def print_substitute(self):
        pass

    def loop(self):
        self._root.mainloop()

    def inverse_print(self):
        pass

    def relief_button(self, evt, func=None, *args):
        '''
        Evênements à relier à un bouton pour que celui-ci change d'état
        quand on appuie dessus :

        >>> button.bind("<ButtonPress-1>", lambda ev: self.relief_button(ev))
        >>> button.bind("<ButtonRelease-1>", lambda ev: self.relief_button(ev))

        La fonction relief_button peut prendre en paramètre une fonction
        <<func>> avec ses paramètres <<args>>.
        '''
        if evt.type == EventType.ButtonPress:
            evt.widget.config(relief=SUNKEN, state=DISABLED)
        elif evt.type == EventType.ButtonRelease:
            evt.widget.config(relief=RAISED, state=ACTIVE)
            if func:
                func(args)


if __name__ == "__main__":
    ui = UI()
    ui.loop()
