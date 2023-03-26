import psycopg2


class PostgresSQL_DataBase:
    def __init__(self, dbname, user, password, host, port):
        """
        Class to connect to PostgresSql database
        """
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def connection(self):
        """
        Auto connection to all functions
        """
        connection = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )
        return connection

    def get_tables(self):
        """
        See all tables in DB
        """
        conn = self.connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';")
        rows = cursor.fetchall()
        for row in rows:
            print(row[0], end='\n\n')
        cursor.close()
        conn.close()

    def insert_db_timing(self, table_name, *values):
        """
        Add row in database
        :param table_name: table name
        :param values: start, duration, name
        """
        conn = self.connection()
        cursor = conn.cursor()
        conn.autocommit = True
        placeholders = ','.join(['%s'] * len(values))
        insert_query = f"INSERT INTO {table_name} (START, DURATION, NAME) VALUES ({placeholders})"
        cursor.execute(insert_query, values)
        conn.commit()
        cursor.close()
        conn.close()

    def terminal_to_db(self):
        conn = self.connection()
        cursor = conn.cursor()
        sql_console = input('This is sql terminal input commands using SHIFT\n'
                            'Press only Enter to EXIT\n\n>')
        while sql_console != "":
            try:
                cursor.execute(sql_console)
                for row in cursor.fetchall():
                    print(row)
            except:
                print('Something wrong')
            sql_console = input('>')
        cursor.close()
        conn.close()
