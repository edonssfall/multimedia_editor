import psycopg2
from keys import *


class DB:
    def __int__(self):
        self.connection = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host
        )

    def insert_db_timing(self, start, end, name):
        cursor = self.connection
        self.connection.autocommit = True
        cursor.execute(
            f'INSERT INTO timing (START, END, NAME) '
            f'VALUES ({start}, {end}, {name})')
        cursor.close()
        self.connection.close()

    def get_all_data(self):
        cursor = self.connection
        cursor.execute(
            f'SELECT * FROM timing'
        )
        rows = cursor.fetchall()
        cursor.close()
        self.connection.close()
        return rows
