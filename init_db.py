# coding=utf-8

import openfoodfacts as opf

from tables_opf import *
from wrap_api_opf import WrapAPI
from dbmysql import *

class DB_opf(DBMysql):
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
    def __init__(self, name, user, pwd=None):
        self.db = None
        try:
            self.db = DBMysql(user, dbpwd=pwd)
            self.db.use_db(name)
        except DBException as err:
            if err.errcode == DBException.ERR_USER:
                self.db = create_user(user, dbpwd=pwd)
                if self.db is None:
                    raise Exception("Impossible de créer l'utilsateur.")
                self.db = DBMysql(user, dbpwd=pwd)
            elif err.errcode == DBException.ERR_UNKNOWN:
                raise DBException(err.errcode, msg=err.__repr__())
            self.db.create_database(name)
            self.db.create_table(TABLES)
            self.save_datas_to_db()

    def save_datas_to_db(self):
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
            try:
                # Retrieving the product category identifier if it exist.
                # Otherwise we add it to the category table.
                result = self.db.get_values(req)
                if result:
                    cat_id = result[0]['cat_id']
                else:
                    self.db.insert_into_table(name_table, datas)
                    cat_id = self.db.lastrowid
            except DBException as err:
                print("save_datas_to_db: ", repr(err))
                print("result: ", result)
                print("datas: ", datas)
                exit()

            name_table = 'product'
            datas = datas_product[name_table]
            datas['cat_id'] = cat_id
            try:
                self.db.insert_into_table(name_table, datas)
            except DBException as err:
                print("save_datas_to_db: ", repr(err))
                print("datas: ", datas)
                exit()
