import unittest
from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.base import Base


class DAOTestCase(unittest.TestCase):

    required_tables = []

    def cleanTables(self, uri='asterisk'):
        if len(self.required_tables):
            connection = dbconnection.get_connection(uri)
            engine = connection.get_engine()
            Base.metadata.drop_all(engine, self.required_tables)
            Base.metadata.create_all(engine, self.required_tables)
            engine.dispose()
