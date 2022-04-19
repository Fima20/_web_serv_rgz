import sqlalchemy
from sqlalchemy.orm import sessionmaker


class MySQLConnection:

    def __init__(self, host, port, user, password, name_db, rebuild_db=False):
        self.user = user
        self.password = password
        self.name_db = name_db

        self.host = host
        self.port = port

        self.rebuild_db = rebuild_db

        self.connection = self.connect()

        session = sessionmaker(
            bind=self.connection.engine,
            autocommit=True,
            autoflush=True,
            enable_baked_queries=False,
            expire_on_commit=True
        )

        self.session = session()

    def get_connection(self, db_created=False):
        engine = sqlalchemy.create_engine(
            f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name_db if db_created else ''}",
            encoding='utf8'
        )
        # engine.execute('SET NAMES utf8')
        # engine.execute('SET character_set_connection=utf8;')
        return engine.connect()

    def connect(self):
        connection = self.get_connection()
        connection.execute("SET NAMES 'utf8';");
        connection.execute("SET CHARACTER SET 'utf8';");
        connection.execute("SET SESSION collation_connection = 'utf8_general_ci';");
        if self.rebuild_db:
            connection.execute(f"DROP DATABASE IF EXISTS {self.name_db}")
            connection.execute(f"CREATE DATABASE {self.name_db}")
        return self.get_connection(db_created=True)

    def execute_query(self, query):
        res = self.connection.execute(query)
        return res