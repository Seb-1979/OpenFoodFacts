#coding: utf-8

DB_NAME = "openfoodfacts"
DB_USER = "opfusr"
DB_PWD = None

try:
    from init_db import *

    db = DB_opf(DB_NAME, DB_USER)
    del db
    exit()
except Exception as err:
    print(__name__, ": ", err)
    exit()

from dbmysql import *
from listselect import *
from tkinter.messagebox import showerror


# dbaccess = DBMysql("opfusr", dbname="openfoodfacts")

class UI:
    BACKGROUND = 'lightgrey'

    def __init__(self):
        self._root = Tk()
        self._root.configure(bg=UI.BACKGROUND)
        self._root.title("Changer son alimentation")
        self._root.geometry("800x600")
        self.frame = None

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
        lb2 = Label(self.frame, text="Votre choix :")
        choice = Entry(self.frame)
        bt_valid = Button(self.frame, text="Valider", bd=3, relief=RAISED)
        bt_valid.bind("<Button-1>",
                      lambda evt: self.verify_entry(self.print_categories))
        bt_valid.pack(side=RIGHT)

    def print_categories(self):
        # cat = []
        cat = [str(pow(hash(str(x)), 2)) for x in range(10, 100)]
        # for v in dbaccess.get_values_into_table("category"):
        #     cat.append(v[1])
        self.__print_list(cat, "Sélectionnez une catégorie :")
        bt_valid = Button(self.frame, text="valider", bd=3, relief=RAISED)
        bt_valid.bind("<Button-1>",
                      lambda evt: self.verify_entry(self.print_food))
        bt_valid.pack(side=RIGHT)

    def print_food(self, cat):
        food = cat if isinstance(cat, list) else [cat]
        self.__print_list(food, "Sélectionnez un aliment :")
        bt_valid = Button(self.frame, text="valider", bd=3, relief=RAISED)
        bt_valid.bind("<Button-1>",
                      lambda evt: self.verify_entry(self.print_substitute))
        bt_valid.pack(side=RIGHT)

    def __print_list(self, lst, title):
        self.__init_frame()
        self.slist = ListSelect(self.frame, bd=3, relief=RIDGE)
        i = 1
        for v in lst:
            self.slist.list_insert("{:d}: {}".format(i, v))
            i += 1
        self.slist.bind("<<Valid>>", self.verify_entry)
        lb = Label(self.frame, text=title, padx=10)
        lb.pack()
        self.slist.pack(fill=X)

    def verify_entry(self, choice, func, *args):
        fname = func.__name__
        if fname == 'print_categories':
            pass
        elif fname == 'print_food':
            val = self.slist.item_value
            if val:
                self.print_food(val)
                pass
        elif fname == 'print_substitute':
            pass
        else:
            showerror("Erreur de saisie",
                       "Veuillez entrer une valeur numérique entière.")

    def print_substitute(self):
        pass

    def loop(self):
        self._root.mainloop()

    def inverse_print(self):
        pass


if __name__ == '__main__':
    pass
    # app = UI()
    # app.print_categories()
    # app.loop()
