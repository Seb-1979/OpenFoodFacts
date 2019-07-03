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
            DBException.ERR_MSG[0] = msg

    def __repr__(self):
        return ERR_MSG[self.errcode]

class DBMysql:
    def __init__(self, dbuser, dbpwd=None, dbname=None):
        self.cnx = None
        try:
            print("Connexion à l'utilisateur {} ...".format(dbuser))
            if dbpwd:
                self.cnx = mysql.connector.connect(user=dbuser, password=dbpwd)
            else:
                self.cnx = mysql.connector.connect(user=dbuser)
            self.cursor = self.cnx.cursor()
            if dbname:
                self.use_db(dbname)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                raise DBException(DBException.ERR_USER \
                    if dbpwd else DBException.ERR_USER_OR_PWD)
            else:
                raise DBException(DBException.ERR_UNKNOWN,
                    msg="Autre erreur MySQL:\n" + err.msg)
        except DBException as err:
            if err.errcode == DBException.ERR_DB_NAME:
                raise DBException(DBException.ERR_DB_NAME)
        except:
            raise DBException(DBException.ERR_UNKNOWN,
                msg="Erreur indéterminée.")
        print("Vous êtes connecté.")

    def use_db(self, dbname):
        try:
            self.cursor = self.cnx.cursor()
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

    def create_table(self, tables):
        try:
            print("Création des tables en cours ...")
            for table in tables:
                print(table)
                self.cursor.execute(tables[table])
            print("La création des tables est effectuée.")
        except mysql.connector.Error as err:
            print(self.cursor.statement)
            if err.errno == errorcode.ER_PARSE_ERROR:
                raise DBException(DBException.ERR_REQUEST)
            else:
                raise DBException(DBException.ERR_UNKNOWN, msg=err.msg)

    def insert_into_table(self, name_table, datas):
        print(datas)

        req = "INSERT INTO {}.{} ".format(self.cnx.database, name_table) + \
              "(" + ', '.join(datas.keys()) + ") "
        fields = []
        for f in datas.keys():
            fields.append("%({})s".format(f))
        req +=  "VALUES(" + ', '.join(fields) + ")"

        #############################
        print("insert query : ", req)
        #############################

        curs = self.cnx.cursor()
        try:
            curs.execute(req, datas)
            self.__lastrowid = curs.lastrowid
            self.cnx.commit()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_PARSE_ERROR:

                ################################
                print("insert error: ", err.msg)
                ################################

                raise DBException(DBException.ERR_REQUEST)
        finally:
            curs.close()

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
            curs = self.cnx.cursor(Dictionary=True)
            curs.execute(req)
            for values in curs:
                yield values
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_PARSE_ERROR:
                raise DBException(DBException.ERR_REQUEST)
            else:
                raise DBException(DBException.ERR_UNKNOWN, msg=err.msg)
        finally:
            curs.close()

    def get_values(self, req):
        curs = self.cnx.cursor(dictionary=True)
        try:
            curs.execute(req)

            ###########################
            print(__name__, ": ", curs)
            ###########################

            # if not curs.rowcount:
            #
            #     ####################################
            #     print(__name__, ": ", curs.rowcount)
            #     ####################################
            #
            #     raise StopIteration
            #
            # for result in rows:
            #     yield result
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_PARSE_ERROR:
                raise DBException(DBException.ERR_REQUEST)
            else:
                raise DBException(DBException.ERR_UNKNOWN, msg=err.msg)
        except Exception as err:
            raise DBException(DBException.ERR_UNKNOWN, msg=err.msg)
        else:
            print("curs: ", type(curs), ", ", curs)
            if not curs.rowcount:
                print("Aucun résultat")
                return []
            print("lecture des résultats")

            rows = curs.fetchall()

            ###########################
            print(__name__, ": ", rows)
            ###########################

            return rows
        finally:
            curs.close()

    def __del__(self):
        if self.cnx and self.cnx.is_connected():
            self.cnx.close()
            print("\n>>>Base de données fermée.")


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
    db = DBMysql(user)
    dbname = "db_jack"
    if not db.create_database(dbname):
        raise Exception("Impossible d'ouvrir la bdd db_jack")

    db.use_db(dbname)
    table_jack = {}
    table_jack['group'] = (
        "CREATE TABLE IF NOT EXISTS `group` ("
        "  `id` int(3) UNSIGNED AUTO_INCREMENT,"
        "  `name` varchar(20) NOT NULL,"
        "  PRIMARY KEY (`id`)"
        ") ENGINE=InnoDB"
    )
    table_jack['user'] = (
        "CREATE TABLE IF NOT EXISTS `user` ("
        "  `id` int(5) UNSIGNED AUTO_INCREMENT,"
        "  `gid` int(3) UNSIGNED NOT NULL,"
        "  `name` varchar(20) NOT NULL,"
        "  PRIMARY KEY (`id`),"
        "  CONSTRAINT `fk_gid` FOREIGN KEY (`gid`)"
        "    REFERENCES `group` (`id`)"
        ") ENGINE=InnoDB"
    )
    db.create_table(table_jack)

    group_values = [{"name":"private"}, {"name":"public"}]
    for gv in group_values:
        db.insert_into_table("group", gv)
    user_values = [
        {"gname":"public", "name":"Jack"},
        {"gname":"private", "name":"Bob"},
        {"gname":"friend", "name":"Will"}
    ]
    req = "SELECT id FROM db_jack.group WHERE name='{}'"
    for uv in user_values:
        rq = req.format(uv["gname"])
        id = -1
        result = db.get_values(rq)
        try:
            id = next(result)['id']
        except StopIteration:
            gv = {"name":uv["gname"]}
            db.insert_into_table("group", gv)
            id = db.lastrowid
        uv['gid'] = id
        del uv["gname"]
        db.insert_into_table("user", uv)
