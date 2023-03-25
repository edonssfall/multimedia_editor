import psycopg2
from keys import *


class PostgresSQL_Database:
    def __int__(self):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def connection(self):
        connection = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )
        return connection

    def insert_db_timing(self, timings):
        connect = self.connection()
        cursor = connect.cursor()
        placeholders = ','.join(['%s'] * len(timings))
        insert_query = f"INSERT INTO timings VALUES ({placeholders})"
        cursor.execute(insert_query, timings)
        connect.commit()
        cursor.close()
        connect.close()
