#coding: utf-8

from listselect import *
from tkinter.messagebox import showinfo
import webbrowser as wb
import tkinter.font as font


class UI:
    BACKGROUND = 'lightgrey'

    def __init__(self, dbaccess):
        self._root = Tk()
        self._root.configure(bg=UI.BACKGROUND)
        self._root.title("Changer son alimentation")
        self._root.geometry("800x600")
        self.frame = None
        self.dbaccess = dbaccess

    def __init_frame(self):
        if self.frame:
            self.frame.destroy()
        self.frame = Frame(self._root, bg=UI.BACKGROUND)
        self.frame.pack(fill=X)

    def main_menu(self):
        self.__init_frame()
        lb1 = Label(self.frame,
                    text="Choisissez parmi les options 1 ou 2 :\n" +
                         "1 - Quel aliment souhaitez-vous remplacer ?\n" +
                         "2 - Retrouver mes aliments substitués.")
        lb1.pack()
        lb2 = Label(self.frame, text="Votre choix :")
        lb2.pack()
        choice = Entry(self.frame)
        choice.pack()
        bt_valid = Button(self.frame, text="Valider", bd=3, relief=RAISED)
        bt_valid.bind("<Button-1>",
                      lambda evt: self.menu_event(choice))
        bt_valid.pack(side=RIGHT)

    def menu_event(self, choice):
        if choice.get() == "1":
            self.print_categories()
        elif choice.get() == "2":
            self.print_favorite_substitute()

    def print_favorite_substitute(self):
        pass
		
    def print_categories(self):
        self.__init_frame()
        self.slist = ListSelect(self.frame, bd=3, relief=RIDGE)
        for v in self.dbaccess.select_from_table("category"):
            self.slist.list_insert("{:d}: {}".format(v["cat_id"], v["cname"]))
        self.__print_list("Sélectionnez une catégorie :")
        bt_valid = Button(self.frame, text="valider", bd=3, relief=RAISED)
        bt_valid.bind("<Button-1>",
                      lambda evt: self.verify_entry(self.print_food))
        bt_valid.pack(side=RIGHT)

    def print_food(self, cat):
        self.__init_frame()
        self.slist = ListSelect(self.frame, bd=3, relief=RIDGE)
        cat_id = cat[:cat.index(":")]
        req = "SELECT prod_id, pname FROM product WHERE cat_id=%s" % cat_id
        for v in self.dbaccess.get_values(req):
            self.slist.list_insert("{:d}: {}".format(v["prod_id"], v["pname"]))
        self.__print_list("Sélectionnez un aliment :")
        bt_substitute = Button(self.frame, text="Afficher un substitut",
                               bd=3, relief=RAISED)
        bt_substitute.bind("<Button-1>",
                      lambda evt: self.verify_entry(self.print_substitute))
        bt_substitute.pack(side=RIGHT)

    def __print_list(self, title):
        self.slist.bind("<<Valid>>", self.verify_entry)
        lb = Label(self.frame, text=title, padx=10)
        lb.pack()
        self.slist.pack(fill=X)

    def print_substitute(self, prod):
        self.__init_frame()
        prod_id = prod[:prod.index(":")]
        req = "SELECT cat_id, energy FROM product WHERE prod_id=%s" % prod_id
        res = self.dbaccess.get_values(req)[0]
        req = "SELECT * FROM product \
               WHERE cat_id = {0} and \
               energy = ( \
                    select min(energy) from product \
                    where cat_id = {0} and energy <= {1} \
                )".format(res["cat_id"], res["energy"])
        res = self.dbaccess.get_values(req)[0]
        if res["prod_id"] == int(prod_id):
            showinfo("Information", "Il n'existe pas de produits connus mieux \
                     que celui selectionné.")
        del res["prod_id"]
        del res["cat_id"]
        row = 0
        url = None
        for k, v in res.items():
            Label(self.frame, text=k+": ", anchor="w"). \
                grid(row=row, column=0, sticky="nw")
            if k == "url":
                url = v
                lb = Label(self.frame, text=url, cursor="hand2", anchor="nw")
                lb.grid(row=row, column=1, sticky="we")
                lb.bind("<Enter>",
                        lambda ev: lb.configure(font=font.Font(underline=1)))
                lb.bind("<Leave>",
                        lambda ev: lb.configure(font=font.Font(underline=0)))
                lb.bind("<Button-1>", lambda ev: wb.open_new(url))
            else:
                Label(self.frame, text=v, justify="left", anchor="w",
                      wraplength=300).grid(row=row, column=1, sticky="we")
            row += 1
            
        bt_save = Button(self.frame, text="Enregistrer ce produit",
                               bd=3, relief=RAISED, command=self.main_menu)
        bt_save.grid(row=row, column=1, sticky="e")

    def verify_entry(self, func, *args):
        fname = func.__name__
        error = False
        if fname == 'print_categories':
            self.print_categories()
        elif fname == 'print_food':
            val = self.slist.item_value
            if val:
                self.print_food(val)
            else:
                error = True
        elif fname == 'print_substitute':
            val = self.slist.item_value
            if val:
                self.print_substitute(val)
            else:
                error = True
        else:
            error = True

        if error:
            showinfo("Erreur de saisie",
                       "Veuillez entrer une valeur numérique entière.")

    def loop(self):
        self._root.mainloop()
