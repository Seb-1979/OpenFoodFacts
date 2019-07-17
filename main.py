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

from ui import UI

if __name__ == '__main__':
    app = UI(dbaccess)
#    app.print_categories()
    app.main_menu()
    app.loop()
    del dbaccess
