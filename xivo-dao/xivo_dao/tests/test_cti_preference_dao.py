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
from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao import cti_profile_dao, cti_preference_dao
from xivo_dao.alchemy.base import Base
from sqlalchemy.schema import MetaData
from xivo_dao.alchemy.ctiphonehintsgroup import CtiPhoneHintsGroup
from xivo_dao.alchemy.ctipresences import CtiPresences
from xivo_dao.alchemy.cti_profile_preference import CtiProfilePreference
from xivo_dao.alchemy.cti_preference import CtiPreference


class TestCtiPreferenceDAO(unittest.TestCase):

    tables = [CtiProfile, CtiPhoneHintsGroup,
              CtiPresences, CtiProfilePreference, CtiPreference]

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
        cti_profile = CtiProfile()
        cti_profile.name = 'test_name'
        self.session.add(cti_profile)
        self.session.commit()

        result = cti_profile_dao.get_name(cti_profile.id)

        self.assertEqual(result, cti_profile.name)

    def _add_presence(self, name):
        cti_presence = CtiPresences()
        cti_presence.name = name
        self.session.add(cti_presence)
        self.session.commit()
        return cti_presence.id

    def _add_preference(self, name):
        cti_preference = CtiPreference()
        cti_preference.option = name
        self.session.add(cti_preference)
        self.session.commit()
        return cti_preference.id

    def _add_phone_hints_group(self, name):
        cti_phone_hints_group = CtiPhoneHintsGroup()
        cti_phone_hints_group.name = name
        self.session.add(cti_phone_hints_group)
        self.session.commit()
        return cti_phone_hints_group.id

    def _add_profile(self, name):
        cti_profile = CtiProfile()
        cti_profile.name = name
        cti_profile.presence_id = self._add_presence('test_presence')
        cti_profile.phonehints_id = self._add_phone_hints_group('test_add_phone_hints_group')
        self.session.add(cti_profile)
        self.session.commit()
        return cti_profile.id

    def _add_preference_to_profile(self,
                                   preference_id,
                                   profile_id,
                                   value):
        cti_profile_preference = CtiProfilePreference()
        cti_profile_preference.preference_id = preference_id
        cti_profile_preference.profile_id = profile_id
        cti_profile_preference.value = value
        self.session.add(cti_profile_preference)
        self.session.commit()

    def test_get_profiles(self):
        expected_result = {
            "agent": {},
            "client": {
                "xlet.identity.logagent": "1",
                "xlet.identity.pauseagent": "1"
            }
        }

        preference1_id = self._add_preference('xlet.identity.logagent')
        preference2_id = self._add_preference('xlet.identity.pauseagent')

        agent_profile_id = self._add_profile('agent')
        client_profile_id = self._add_profile('client')

        self._add_preference_to_profile(preference1_id, client_profile_id, "1")
        self._add_preference_to_profile(preference2_id, client_profile_id, "1")

        result = cti_preference_dao.get_preferences()

        self.assertEquals(result, expected_result)
