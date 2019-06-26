# coding : utf-8

import mysql.connector
from mysql.connector import errorcode

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
        ERR_USER_OR_PWD: "L'utilisateur et/ou le mot de passe sont incorrects.",
        ERR_DB_NAME: "Impossible de se connecter à la base de données.",
        ERR_REQUEST: "Erreur dans la requête SQL."
    }

    def __init__(self, code, msg=None):
        self.errcode = code
        if code == 0:
            ERR_MSG[0] = msg

    def __repr__(self):
        print(ERR_MSG[self.errcode])

class DBMysql:
    def __init__(self, dbuser, dbpwd=None, dbname=None):
        self.db_initialize = False
        self.__dbname = dbname

        try:
            print("Connexion à l'utilisateur {} ...".format(dbuser))
            if dbpwd:
                self.cnx = mysql.connector.connect(user=dbuse, password=dbpwd)
            else:
                self.cnx = mysql.connector.connect(user=dbuser)
            self.cursor = self.cnx.cursor()
            self.db_initialize = True
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                raise DBException(DBException.ERR_USER \
                    if dbpwd else DBException.ERR_USER_OR_PWD)
            else:
                raise DBException(DBException.ERR_UNKNOWN,
                    msg="Autre erreur MySQL:\n" + err.msg)
        except:
            raise DBException(DBException.ERR_UNKNOWN,
                msg="Erreur indéterminée.")
        print("Vous êtes connecté.")
        if dbname:
            self.use_db(dbname)

    def use_db(self, dbname):
        try:
            cursor = self.cnx.cursor()
            cursor.execute("USE %s;" % dbname)
            self.cursor = cursor
            self.__dbname = dbname
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                raise DBException(DBException.ERR_DB_NAME)

    def create_database(self, dbname):
        try:
            print("Création de la base de données en cours ...")
            self.cursor.execute(
                "CREATE DATABASE IF NOT EXISTS {}".format(dbname) +
                " DEFAULT CHARACTER SET 'utf8'")
        except mysql.connector.Error as err:
            print(err.msg)
            return False
        print("La base de donnée a été créée avec succés.".format(''))
        return True

    def create_table(self, tables):
        try:
            print("Création des tables en cours ...".format(''))
            for table in tables:
                print(table)
                self.cursor.execute(tables[table])
            print("La création des tables est effectuée.")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_PARSE_ERROR:
                raise DBException(DBException.ERR_REQUEST)
            else:
                raise DBException(DBException.ERR_UNKNOWN, msg=err.msg)

    def insert_into_table(self, name_table, datas):
        req = "INSERT INTO {} ".format(name_table)
        fields = []
        values = []
        for f, v in datas.items():
            fields.append("{}".format(f))
            values.append("{}".format(v))
        req += "(" + ', '.join(fields) + ") VALUES(" + ', '.join(values) +");"
        print(req)
        self.cursor.execute(req)
        self.cnx.commit()

    def get_values_into_table(self, name_table, fields=('*',)):
        ln = len(fields)
        if ln == 1:
            req = "SELECT " + fields[0] + "FROM " + name_table + ";"
        else:
            req = "SELECT " + ",".join(fields) + "FROM " + name_table + ";"
        curs = self.cnx.cursor()
        curs.execute(req)
        rows = curs.fetchall()
        for values in rows:
            yield values
        curs.close()

    def get_result_to_request(self, req):
        try:
            curs = self.cnx.cursor()
            curs.execute(req)
            for result in curs:
                yield result
            curs.close()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_PARSE_ERROR:
                raise DBException(DBException.ERR_REQUEST)

    def __del__(self):
        try:
            self.cnx.close()
            print("\n>>>Base de données fermée.")
        except:
            pass


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


if __name__ == '__main__':
    user = "Jack"
    if(not create_user(user)):
        exit()
    db = DBMysql(user)
    dbname = "db_jack"
    if db.create_database(dbname):
        db.use_db(dbname)
        table_jack = {}
        table_jack['jack'] = (
            "CREATE TABLE IF NOT EXISTS `jack` ("
            "  `id` int(5) UNSIGNED AUTO_INCREMENT,"
            "  `age` int(3) UNSIGNED NOT NULL,"
            "  PRIMARY KEY (`id`)"
            ") ENGINE=InnoDB"
        )
        db.create_table(table_jack)
        db.insert_into_table("jack", {'age':12})
        for v in db.get_values_into_table("jack"):
            print(v)
