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
from xivo_dao import cti_profile_dao
from xivo_dao.alchemy.base import Base
from sqlalchemy.schema import MetaData
from xivo_dao.alchemy.cti_preference import CtiPreference
from xivo_dao.alchemy.ctiphonehintsgroup import CtiPhoneHintsGroup
from xivo_dao.alchemy.ctipresences import CtiPresences
from xivo_dao.alchemy.cti_profile_preference import CtiProfilePreference
from xivo_dao.alchemy.cti_profile_service import CtiProfileService
from xivo_dao.alchemy.cti_profile_xlet import CtiProfileXlet
from xivo_dao.alchemy.cti_service import CtiService
from xivo_dao.alchemy.cti_xlet import CtiXlet
from xivo_dao.alchemy.cti_xlet_layout import CtiXletLayout
from xivo_dao.alchemy.ctistatus import CtiStatus


class TestCtiProfileDAO(unittest.TestCase):

    tables = [CtiProfile, CtiPreference, CtiPhoneHintsGroup,
              CtiPresences, CtiProfilePreference, CtiProfileService,
              CtiProfileXlet, CtiService, CtiXlet, CtiXletLayout,
              CtiStatus]

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

    def _add_xlet_layout(self, name):
        cti_xlet_layout = CtiXletLayout()
        cti_xlet_layout.name = name
        self.session.add(cti_xlet_layout)
        self.session.commit()
        return cti_xlet_layout.id

    def _add_xlet(self, name):
        cti_xlet = CtiXlet()
        cti_xlet.plugin_name = name
        self.session.add(cti_xlet)
        self.session.commit()
        return cti_xlet.id

    def _add_xlet_to_profile(self,
                             xlet_id,
                             profile_id,
                             layout_id,
                             floating,
                             closable,
                             movable,
                             scrollable,
                             order):
        cti_profile_xlet = CtiProfileXlet()
        cti_profile_xlet.xlet_id = xlet_id
        cti_profile_xlet.profile_id = profile_id
        cti_profile_xlet.layout_id = layout_id
        cti_profile_xlet.floating = floating
        cti_profile_xlet.closable = closable
        cti_profile_xlet.movable = movable
        cti_profile_xlet.scrollable = scrollable
        cti_profile_xlet.order = order
        self.session.add(cti_profile_xlet)
        self.session.commit()

    def test_get_profiles(self):
        expected_result = {
            "test_profile": {
                "name": "test_profile",
                "phonestatus": "test_add_phone_hints_group",
                "userstatus": "test_presence",
                "preferences": "itm_preferences_test_profile",
                "services": "itm_services_test_profile",
                "xlets": [
                    {'name': 'tabber',
                     'layout': 'grid',
                     'floating': True,
                     'closable': True,
                     'movable': True,
                     'scrollable': True,
                     'order': 1},
                    {'name': 'agentdetails',
                     'layout': 'dock',
                     'floating': False,
                     'closable': True,
                     'movable': True,
                     'scrollable': True,
                     'order': 0}
                ]
            }
        }
        profile_id = self._add_profile('test_profile')

        xlet_layout_grid_id = self._add_xlet_layout('grid')
        xlet_tabber_id = self._add_xlet('tabber')
        self._add_xlet_to_profile(xlet_tabber_id,
                             profile_id,
                             xlet_layout_grid_id,
                             floating=True,
                             closable=True,
                             movable=True,
                             scrollable=True,
                             order=1)

        xlet_agentdetails_id = self._add_xlet('agentdetails')
        xlet_layout_dock_id = self._add_xlet_layout('dock')
        self._add_xlet_to_profile(xlet_agentdetails_id,
                             profile_id,
                             xlet_layout_dock_id,
                             floating=False,
                             closable=True,
                             movable=True,
                             scrollable=True,
                             order=0)

        result = cti_profile_dao.get_profiles()

        self.assertEquals(result, expected_result)
