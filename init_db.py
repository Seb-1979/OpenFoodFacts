# coding=utf-8

import mysql.connector
from mysql.connector import errorcode

import openfoodfacts as opf

from subprocess import run as process, PIPE
from getpass import getpass
from tempfile import NamedTemporaryFile

from tables_opf import *
from wrap_api_opf import WrapAPI


class Database:
    DB_NAME = "openfoodfacts"
    DB_USER = "opfusr"

    def __init__(self):
        try:
            print("Connexion à la base de données {} de l'utilisateur {} ..."
                  .format(Database.DB_NAME, Database.DB_USER))
            self.cnx = mysql.connector.connect(
                user=Database.DB_USER,
                database=Database.DB_NAME)
            self.cursor = self.cnx.cursor()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("--> L'utilisateur {} n'existe pas."
                      .format(Database.DB_USER))
                if not Database.__create_user():
                    raise Exception("--> Impossible de créer l'utilisateur {}")
                self.cnx = mysql.connector.connect(user=Database.DB_USER)
                self.cursor = self.cnx.cursor()
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                if not self.__create_database():
                    raise Exception(
                        "--> Impossible de créer la base de données.")
        except:
            print("--> Erreur indéterminée.")
        print("Vous êtes connecté.")

    def __del__(self):
        try:
            print("\n>>>Base de données fermée.")
            self.cnx.close()
        except TypeError:
            pass

    def save_datas_to_db(self):
        api_opf = WrapAPI(page_size=500)
        # fp = open("requests.sql", "w")
        # Parcours de tous les produits de la base
        for datas_product in api_opf.get_all_products():
            for name_table, datas in datas_product.items():
                req = "INSERT INTO `{}` (".format(name_table)
                names = []
                values = []
                for name, value in datas.items():
                    names.append("`"+name+"`")
                    values.append("`"+value+"`")
                req += ",".join(names)
                req += ") VALUES ("
                req += ",".join(values)
                req += ")"
                self.cursor.execute(req)
        #         fp.write(req+"\n")
        # fp.close()

    def __create_database(self):
        try:
            print("--> Création de la base de données en cours ...")
            self.cursor.execute(
                "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'"
                .format(Database.DB_NAME))
            self.cnx.database = Database.DB_NAME
            print("{:7}Création des tables.".format(''))
            for table in TABLES:
                print(table)
                self.cursor.execute(TABLES[table])
            print("{:7}Enregistrements des données dans la base.".format(''))
            self.__save_datas_to_db()
        except mysql.connector.Error as err:
            print(err.msg)
            return False
        print("{:5}La base de donnée a été créée avec succés.".format(''))
        return True

    @classmethod
    def __create_user(cls):
        ret = None
        try:
            print("--> Création d'un nouvel utilisateur en cours ...")
            print(
                "{:7}Un nouvel utilisateur doit-être créé pour pouvoir lui "
                "associer la base de données de Open Food Facts. Veuillez "
                "entrer le mot de passe de l'utilisateur root sous mysql"
                .format(''), end=' : '
            )
            pwd = getpass("")
            tmpf = NamedTemporaryFile(mode='w', encoding='utf8')
            tmpf.file.write(
                "[client]\n"
                "user=root\n"
                "password="+pwd
            )
            tmpf.file.flush()
            del pwd
            req = "CREATE USER IF NOT EXISTS '{}'@'localhost';" \
                  "GRANT ALL PRIVILEGES ON * . * TO '{}'@'localhost';" \
                  "FLUSH PRIVILEGES;" \
                  .format(cls.DB_USER, cls.DB_USER)
            print(req)
            ret = process(
                ["mysql", "--defaults-file={}".format(tmpf.name), "-e", req],
                stderr=PIPE
            )
            tmpf.close()
        except Exception:
            if tmpf:
                tmpf.close()
            print("Exception dans fonction :", __name__)
            return False
        if ret.returncode:
            print("Erreur process -> code de retour :", ret.returncode)
            print(ret.stderr)
            return False

        print("{:5}L'utilisateur a été créé correctement.".format(''))
        return True


if __name__ == '__main__':
    db = Database()
    db.save_datas_to_db()
