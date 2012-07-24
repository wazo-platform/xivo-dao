# -*- coding: utf-8 -*-
# Copyright (C) 2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the source tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest

from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.groupfeatures import GroupFeatures
from xivo_dao import group_dao
from xivo_dao.alchemy.base import Base
from sqlalchemy.schema import MetaData


class TestGroupDAO(unittest.TestCase):

    tables = [GroupFeatures]

    @classmethod
    def setUpClass(cls):
        db_connection_pool = dbconnection.DBConnectionPool(dbconnection.DBConnection)
        dbconnection.register_db_connection_pool(db_connection_pool)

        uri = 'postgresql://asterisk:asterisk@localhost/asterisktest'
        dbconnection.add_connection_as(uri, 'asterisk')
        cls.connection = dbconnection.get_connection('asterisk')

        cls.cleanTables()

        cls.session = cls.connection.get_session()

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

    def empty_tables(self):
        for table in self.tables:
            self.session.execute("TRUNCATE %s CASCADE;" % table.__tablename__)

    def setUp(self):
        self.empty_tables()

    def test_get_name(self):
        session = dbconnection.get_connection('asterisk').get_session()
        group = GroupFeatures()
        group.name = 'test_name'
        group.number = '1234'
        group.context = 'my_ctx'
        session.add(group)
        session.commit()

        result = group_dao.get_name(group.id)

        self.assertEqual(result, group.name)

    def test_get_name_number(self):
        group = GroupFeatures()
        group.name = 'test_name'
        group.number = '1234'
        group.context = 'my_ctx'

        self.session.add(group)
        self.session.commit()

        name, number = group_dao.get_name_number(group.id)

        self.assertEqual(name, 'test_name')
        self.assertEqual(number, '1234')
