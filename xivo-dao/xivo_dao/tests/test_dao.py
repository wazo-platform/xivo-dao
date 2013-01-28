# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import unittest
from xivo_dao.alchemy.base import Base
from sqlalchemy.schema import MetaData
from xivo_dao.helpers.db_manager import DbSession
from xivo_dao.helpers import db_manager


class DAOTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db_manager._DB_URI = 'postgresql://asterisk:asterisk@localhost/asterisktest'
        cls.session = DbSession()
        cls.engine = cls.session.get_bind()
        cls.cleanTables()

    @classmethod
    def tearDownClass(cls):
        cls.session.close()

    @classmethod
    def cleanTables(cls):
        if cls.tables:
            engine = cls.engine

            meta = MetaData(engine)
            meta.reflect()
            meta.drop_all()

            table_list = [table.__table__ for table in cls.tables]
            Base.metadata.create_all(engine, table_list)
            engine.dispose()

    def empty_tables(self):
        for table in self.tables:
            self.session.execute("TRUNCATE %s CASCADE;" % table.__tablename__)
        self.session.commit()
