#coding: utf-8

from tables_opf import *
from wrap_api_opf import WrapAPI
from dbmysql import *

DB_NAME = "openfoodfacts"
DB_USER = "opfusr"
DB_PWD = None

def save_datas_to_db(db):
    """ Saves data from Open Food Facts in the Mysql database. """
    api_opf = WrapAPI(500)
    fp = None
    try:
        # We check the existence of the file 'data_products.bin'.
        fp = open("data_products.bin")
        fp.close()
    except IOError:
        # If the file 'data_products.bin' does not exist, we download
        # data from OpenFoodFacts and saves it to this file.
        api_opf.download_products()

    # Backup of each product registered in 'data_products.bin' in the
    # Mysql database.
    for datas_product in api_opf.get_all_products():
        name_table = 'category'
        datas = datas_product[name_table]
        req = 'SELECT cat_id FROM openfoodfacts.category WHERE cname="{}";' \
              .format(datas['cname'])

        cat_id = -1  # Identifier of the product category.
        # Retrieving the product category identifier if it exist.
        # Otherwise we add it to the category table.
        result = db.get_values(req)
        if result:
            cat_id = result[0]['cat_id']
        else:
            db.insert_into_table(name_table, datas)
            cat_id = db.lastrowid

        name_table = 'product'
        datas = datas_product[name_table]
        datas['cat_id'] = cat_id
        db.insert_into_table(name_table, datas)

def init_db(name, user, pwd=None):
    """
        Creation of the Mysql database storing part of data from Open Food
        Facts.

        Args:
            name (str): Name of the Mysql database.
            user (str): Username for the database 'name'.
            pwd (str): Password used to log in to the user 'user'.

        Raises:
            DBException: If any of the connection parameters at the base of
                data is incorrect.

    """
    db = None
    try:
        db = DBMysql(user, dbpwd=pwd)
        db.use_db(name)
    except DBException as err:
        if err.errcode == DBException.ERR_USER:
            db = DBMysql.create_user(user, dbpwd=pwd)
            if self.db is None:
                raise Exception("Impossible de créer l'utilsateur.")
            db = DBMysql(user, dbpwd=pwd)
        elif err.errcode == DBException.ERR_UNKNOWN:
            raise DBException(err.errcode, msg=err.__repr__())
        db.create_database(name)
        db.create_table(TABLES)
        save_datas_to_db(db)
    finally:
        return db

dbaccess = None
try:
    dbaccess = init_db(DB_NAME, DB_USER)
    # db.close()
except DBException as err:
    print("main: ", repr(err))

from listselect import *
from tkinter.messagebox import showinfo
import webbrowser as wb
import tkinter.font as font


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
        self.__init_frame()
        self.slist = ListSelect(self.frame, bd=3, relief=RIDGE)
        for v in dbaccess.select_from_table("category"):
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
        for v in dbaccess.get_values(req):
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
        res = dbaccess.get_values(req)[0]
        req = "SELECT * FROM product \
               WHERE cat_id = {0} and \
               energy = ( \
                    select min(energy) from product \
                    where cat_id = {0} and energy <= {1} \
                )".format(res["cat_id"], res["energy"])
        res = dbaccess.get_values(req)[0]
        if res["prod_id"] == int(prod_id):
            showinfo("Information", "Il n'existe pas de produits connus mieux \
                     que celui selectionné.")
        del res["prod_id"]
        del res["cat_id"]
        row = 0
        url = None
        for k, v in res.items():
            Label(self.frame, text=k+": ", anchor="w", bg="#ddd"). \
                grid(row=row, column=0, sticky="nw")
            if k == "url":
                url = v
                lb = Label(self.frame, text=url, cursor="hand2", anchor="nw",
                              bg="#afa")
                lb.grid(row=row, column=1, sticky="we")
                lb.bind("<Enter>",
                        lambda ev: lb.configure(font=font.Font(underline=1)))
                lb.bind("<Leave>",
                        lambda ev: lb.configure(font=font.Font(underline=0)))
                lb.bind("<Button-1>", lambda ev: wb.open_new(url))
            else:
                Label(self.frame, text=v, justify="left", anchor="w", bg="#afa",
                         wraplength=300).grid(row=row, column=1, sticky="we")
            row += 1

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

    def inverse_print(self):
        pass


if __name__ == '__main__':
    app = UI()
    app.print_categories()
    app.loop()
    del dbaccess
