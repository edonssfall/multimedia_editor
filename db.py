import psycopg2


class PostgresSQL_Database:
    def __int__(self, dbname=str(), user=str(), password=str(), host=str(), port=str()):
        """
        :param dbname: database name
        :param user: nickname
        :param password: password
        :param host: host
        :param port: port
        """
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def connection(self):
        """
        Allways need to connect first
        """
        connection = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )
        return connection

    def insert_db_timing(self, table_name, *values):
        """
        Add row in database
        :param table_name: table name
        :param values: start, duration, name
        """
        conn = self.connection()
        cursor = conn.cursor()
        placeholders = ','.join(['%s'] * len(values))
        insert_query = f"INSERT INTO {table_name} VALUES ({placeholders})"
        cursor.execute(insert_query, values)
        conn.commit()
        cursor.close()
        conn.close()
