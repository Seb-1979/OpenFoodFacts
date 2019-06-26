# coding : utf-8

from tkinter import *


class ListSelect(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.columnconfigure(1, weight=1)
        lab = Label(self, text="Choix :", padx=10)
        lab.grid(row=0, column=0)
        self.__entry = Entry(self, width=8)
        self.__entry.grid(row=0, column=1, sticky="we")
        self.event_add("<<Enter>>", "<Key-KP_Enter>", "<Key-Return>")
        self.__entry.bind("<<Enter>>", self.__entry_valid)
        self.__listbox_init().grid(row=1, column=0, columnspan=2, sticky="we")

    def __listbox_init(self):
        f = Frame(self)
        f.columnconfigure(0, weight=1)
        self.__listbox = Listbox(f, selectmode='single')
        self.__listbox.grid(row=0, column=0, stick="we")
        self.__listbox.bind("<<ListboxSelect>>", self.__select_item)

        xscrollbar = Scrollbar(f, orient='horizontal',
                               command=self.__listbox.xview)
        yscrollbar = Scrollbar(f, orient='vertical',
                               command=self.__listbox.yview)
        yscrollbar.grid(row=0, column=1, sticky="ns")
        xscrollbar.grid(row=1, column=0, sticky="we")
        self.__listbox["yscrollcommand"] = yscrollbar.set
        self.__listbox["xscrollcommand"] = xscrollbar.set
        return f

    @property
    def item_value(self):
        try:
            e = int(self.__entry.get())
            if e and 1 <= e <= self.list_size:
                return self.__listbox.get(e-1)
            else:
                return None
        except (TypeError, ValueError):
            return None

    @property
    def list_size(self):
        return self.__listbox.size()

    def list_insert(self, item):
        if isinstance(item, list):
            for i in item:
                self.__listbox.insert(END, i)
        else:
            self.__listbox.insert(END, item)

    def __select_item(self, evt):
        if self.__listbox.curselection():
            self.__entry.delete(0, END)
            self.__entry.insert(0, self.__listbox.curselection()[0]+1)

    def __entry_valid(self, evt):
        if self.__entry.get():
            self.event_generate("<<Valid>>")


if __name__ == '__main__':
    def print_value(evt):
        w = evt.widget
        print(w.item_value)

    root = Tk()
    root.geometry("400x600")
    ls = ListSelect(root)
    ls.list_insert([str(pow(hash(str(x)), 2)) for x in range(10, 100)])
    ls.bind("<<Valid>>", print_value)
    ls.pack(fill=X)
    root.mainloop()
