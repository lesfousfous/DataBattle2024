import mysql.connector
from mysql.connector import MySQLConnection
from configparser import ConfigParser
import pandas as pd


class Database:

    def __init__(self) -> None:
        config = ConfigParser()
        config.read("config.ini")
        self.database_connection = Database._init_database_connection(config)

    def _init_database_connection(config_file: ConfigParser) -> MySQLConnection:
        mydb = mysql.connector.connect(
            host=config_file['mysqlDB']['host'],
            user=config_file['mysqlDB']['user'],
            password=config_file['mysqlDB']["password"],
            database=config_file['mysqlDB']['db'],
        )
        return mydb


class Table():

    def __init__(self, name: str, database: Database) -> None:
        self.database_connection = database.database_connection
        self.name = name
        self.dataframe = self._load_solution_data_from_db()

    def _load_solution_data_from_db(self):
        data = {}
        keys = self._load_all_keys_of_table()
        for x in keys:
            data[x] = self._get_attribute(x)

        dataframe = Table._dict_to_dataframe(data)
        return dataframe

    def _dict_to_dataframe(dictionnary):
        dataframe = pd.DataFrame(dictionnary)
        return dataframe

    def _get_attribute(self, attribute_name):
        cursor = self.database_connection.cursor()
        cursor.execute(f"SELECT {attribute_name} FROM {self.name};")
        attribute_data = [column_name[0] for column_name in cursor.fetchall()]
        cursor.close()
        return attribute_data

    def _load_all_keys_of_table(self):
        cursor = self.database_connection.cursor()
        cursor.execute(f"SELECT column_name FROM information_schema.columns \
                          WHERE table_schema = 'kerdos'\
                          AND table_name = '{self.name}';")
        keys = [column_name[0] for column_name in cursor.fetchall()]
        cursor.close()
        return keys

    def __str__(self) -> str:
        return self.dataframe.__str__()


db = Database()
solutions = Table("tblsolution", database=db)
print(solutions)
