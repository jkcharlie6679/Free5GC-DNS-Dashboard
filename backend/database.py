import psycopg2


class postgresql:
    def __init__(self, db_config) -> None:
        self.user = db_config.get("user")
        self.passwd = db_config.get("passwd")
        self.host = db_config.get("host")
        self.port = int(db_config.get("port"))
        self.database = db_config.get("database")
        self._connect2db()
        pass

    def _connect2db(self):

        self.connection = psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user, 
            password=self.passwd,
            dbname=self.database,
        )
        pass

    def query(self, query, *args):
        try:
            with self.connection.cursor() as cur:
                cur.execute(query, args)
                self.connection.commit()
                try: 
                    return cur.fetchall()
                except:
                    return None
        except:
            self._connect2db()
            with self.connection.cursor() as cur:
                cur.execute(query, args)
                self.connection.commit()
                try: 
                    return cur.fetchall()
                except:
                    return None
