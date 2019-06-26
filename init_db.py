# coding=utf-8

import openfoodfacts as opf

from tables_opf import *
from wrap_api_opf import WrapAPI
from dbmysql import *

class DB_opf(DBMysql):
    def __init__(self, name, user, pwd=None):
        self.db = None
        try:
            self.db = DBMysql(user, dbpwd=pwd, dbname=name)
        except DBException as err:
            if err.errcode == DBException.ERR_USER:
                self.db = create_user(user, dbpwd=pwd)
                if self.db is None:
                    raise Exception("Impossible de créer l'utilsateur.")
            self.db.create_database(name)
            self.db.create_table(TABLES)
            self.save_datas_to_db()

    def save_datas_to_db(self):
        api_opf = WrapAPI(page_size=100)
        for datas_product in api_opf.get_all_products():
            name_table = 'category'
            datas = datas_product[name_table]
            req = "SELECT cat_id FROM category WHERE cname={};" \
                  .format(datas['cname'])
            cat_id = -1
            try:
                cat_id = self.db.get_result_to_request(req)
            except StopIteration:
                self.insert_into_table(name_table, datas)
                cat_id = self.db.cursor.lastrowid
            name_table = 'product'
            datas = datas_product[name_table]
            datas['cat_id'] = cat_id
            self.db.insert_into_table(name_table, datas)
