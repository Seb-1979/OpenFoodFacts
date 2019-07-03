# coding=utf-8

import openfoodfacts as opf

from tables_opf import *
from wrap_api_opf import WrapAPI
from dbmysql import *

class DB_opf(DBMysql):
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
        api_opf = WrapAPI(page_size=20)
        for datas_product in api_opf.get_all_products():
            name_table = 'category'
            datas = datas_product[name_table]
            req = "SELECT cat_id FROM openfoodfacts.category WHERE cname={};" \
                  .format(datas['cname'])

            ##########################
            print(__name__, ": ", req)
            ##########################

            cat_id = -1
            try:
                result = self.db.get_values(req)
                if result:
                    cat_id = result['id']
                else:
                    self.insert_into_table(name_table, datas)
                    cat_id = self.db.lastrowid
            except DBException as err:
                print(err)
                exit()
            except Exception as err:
                print("erreur indéterminée: ", err)
                exit()

            name_table = 'product'
            datas = datas_product[name_table]
            datas['cat_id'] = cat_id

            ############################
            print(__name__, ": ", datas)
            ############################

            self.db.insert_into_table(name_table, datas)
