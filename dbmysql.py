# coding : utf-8

import mysql.connector
from mysql.connector import errorcode, connection

from subprocess import run as process, PIPE
from getpass import getpass
from tempfile import NamedTemporaryFile


class DBException(Exception):
    ERR_UNKNOWN = 0
    ERR_USER = 1
    ERR_USER_OR_PWD = 2
    ERR_DB_NAME = 3
    ERR_REQUEST = 4

    ERR_MSG = {
        ERR_UNKNOWN: "",
        ERR_USER: "L'utilisateur est incorrect.",
        ERR_USER_OR_PWD: "L'utilisateur et/ou le mot de passe sont "
                         "incorrects.",
        ERR_DB_NAME: "Impossible de se connecter à la base de données.",
        ERR_REQUEST: "Erreur dans la requête SQL."
    }

    def __init__(self, code, msg=None):
        self.errcode = code
        if code == 0:
            DBException.ERR_MSG[0] = msg

    def __repr__(self):
        return DBException.ERR_MSG[self.errcode]


class DBMysql:
    def __init__(self, dbuser, dbpwd=None, dbname=None):
        self.cnx = None
        self.cursor = None
        try:
            print("Connexion à l'utilisateur {} ...".format(dbuser))
            if dbpwd:
                self.cnx = connection.MySQLConnection(user=dbuser, password=dbpwd)
            else:
                self.cnx = connection.MySQLConnection(user=dbuser)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                raise DBException(
                    DBException.ERR_USER
                    if dbpwd else DBException.ERR_USER_OR_PWD)
            else:
                raise DBException(
                    DBException.ERR_UNKNOWN,
                    msg="Autre erreur MySQL:\n" + err.msg)
        else:
            self.cursor = self.cnx.cursor(dictionary=True)
            if dbname:
                self.use_db(dbname)
            print("Vous êtes connecté.")

    def use_db(self, dbname):
        try:
            self.cursor.execute("USE %s;" % dbname)
            print("database name : ", self.cnx.database)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                raise DBException(DBException.ERR_DB_NAME)

    def create_database(self, dbname):
        try:
            print("Création de la base de données en cours ...")
            self.cursor.execute(
                "CREATE DATABASE IF NOT EXISTS {}".format(dbname) +
                " DEFAULT CHARACTER SET 'utf8'")
            self.cnx.database = dbname
        except mysql.connector.Error as err:
            print(err.msg)
            return False
        print("La base de donnée a été créée avec succés.".format(''))
        return True

    def delete_database(self):
        if self.cnx.database:
            self.cursor.execute("DROP DATABASE IF EXISTS %s;" %
                                self.cnx.database)

    def create_table(self, tables):
        try:
            print("Création des tables en cours ...")
            for table in tables:
                print("Table ", table, " créée")
                self.cursor.execute(tables[table])
            print("La création des tables est effectuée.")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_PARSE_ERROR:
                raise DBException(DBException.ERR_REQUEST)
            else:
                raise DBException(DBException.ERR_UNKNOWN, msg=err.msg)

    def insert_into_table(self, name_table, datas):
        req = "INSERT INTO {}.{} ".format(self.cnx.database, name_table) + \
              "(" + ', '.join(datas.keys()) + ") "
        fields = []
        for f in datas.keys():
            fields.append("%({})s".format(f))
        req +=  "VALUES(" + ', '.join(fields) + ")"
        #############################
        # print("query : ", req)

        try:
            self.cursor.execute(req, datas)
            self.__lastrowid = self.cursor.lastrowid
            self.cnx.commit()
        except mysql.connector.Error as err:
            #####################################
            print("insert_into_table: ", err.msg)
            print("insert_into_table: ", req)
            if err.errno == errorcode.ER_PARSE_ERROR:
                raise DBException(DBException.ERR_REQUEST)
            else:
                raise DBException(DBException.ERR_UNKNOWN, msg=err.msg)
        # except Exception as err:
        #     ###################################
        #     print("insert_into_table: ", datas)
        #     # print(err)

    @property
    def lastrowid(self):
        return self.__lastrowid

    def select_from_table(self, name_table, fields=('*',)):
        ln = len(fields)
        if ln == 1:
            req = "SELECT " + fields[0] + "FROM " + name_table + ";"
        else:
            req = "SELECT " + ",".join(fields) + " FROM " + name_table + ";"
        try:
            self.cursor.execute(req)
            for values in self.cursor:
                yield values
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_PARSE_ERROR:
                raise DBException(DBException.ERR_REQUEST)
            else:
                raise DBException(DBException.ERR_UNKNOWN, msg=err.msg)

    def get_values(self, req):
        try:
            self.cursor.execute(req)
            if not self.cursor.rowcount:
                print("Aucun résultat")
                rows = []
            else:
                rows = self.cursor.fetchall()
        except mysql.connector.Error as err:
            print("get_values: ", repr(err))
            print("get_values: ", req)
            if err.errno == errorcode.ER_PARSE_ERROR:
                raise DBException(DBException.ERR_REQUEST)
            else:
                raise DBException(DBException.ERR_UNKNOWN, msg=err.msg)

        return rows

    # def close(self):
    #     if self.cnx and self.cnx.is_connected():
    #         self.cursor.close()
    #         self.cnx.close()
    #         self.cnx = None
    #         print("\n>>>Base de données fermée.")


def create_user(dbuser, dbpwd=None):
    try:
        print("Création d'un nouvel utilisateur en cours ...\n"
              "Un nouvel utilisateur doit-être créé pour pouvoir lui associer"
              " la base de données de Open Food Facts. Veuillez entrer le mot"
              " de passe de l'utilisateur root sous mysql : ", end='')
        pwd = getpass("")
        tmpf = NamedTemporaryFile(mode='w', encoding='utf8')
        tmpf.file.write(
            "[client]\n"
            "user=root\n"
            "password="+pwd
        )
        tmpf.file.flush()
        del pwd
        req = "CREATE USER IF NOT EXISTS '{}'@'localhost'{};".format(
            dbuser, "" if dbpwd is None else " IDENTIFY BY " + dbpwd)
        req += "GRANT ALL PRIVILEGES ON * . * TO '{}'@'localhost';" \
               .format(dbuser)
        req += "FLUSH PRIVILEGES;"
        ret = process(
            ["mysql", "--defaults-file={}".format(tmpf.name), "-e", req],
            stderr=PIPE)
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
