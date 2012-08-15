import unittest
from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.base import Base
from sqlalchemy.schema import MetaData


class DAOTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db_connection_pool = dbconnection.DBConnectionPool(dbconnection.DBConnection)
        dbconnection.register_db_connection_pool(db_connection_pool)

        uri = 'postgresql://asterisk:asterisk@localhost/asterisktest'
        dbconnection.add_connection_as(uri, 'asterisk')
        cls.connection = dbconnection.get_connection('asterisk')

        cls.cleanTables()

        cls.session = cls.connection.get_session()

        cls._create_functions()

    @classmethod
    def tearDownClass(cls):
        dbconnection.unregister_db_connection_pool()

    @classmethod
    def cleanTables(cls):
        if len(cls.tables):
            engine = cls.connection.get_engine()

            meta = MetaData(engine)
            meta.reflect()
            meta.drop_all()

            table_list = [table.__table__ for table in cls.tables]
            Base.metadata.create_all(engine, table_list)
            engine.dispose()

    @classmethod
    def _create_functions(cls):
        pass

    def empty_tables(self):
        for table in self.tables:
            self.session.execute("TRUNCATE %s CASCADE;" % table.__tablename__)
