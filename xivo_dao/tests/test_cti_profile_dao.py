# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
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

from xivo_dao import cti_profile_dao
from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao.alchemy.cti_profile_xlet import CtiProfileXlet
from xivo_dao.alchemy.cti_xlet import CtiXlet
from xivo_dao.alchemy.cti_xlet_layout import CtiXletLayout
from xivo_dao.alchemy.ctiphonehintsgroup import CtiPhoneHintsGroup
from xivo_dao.alchemy.ctipresences import CtiPresences
from xivo_dao.helpers.db_utils import commit_or_abort
from xivo_dao.tests.test_dao import DAOTestCase


class TestCtiProfileDAO(DAOTestCase):

    def test_get_name(self):
        cti_profile = CtiProfile()
        cti_profile.name = 'test_name'

        with commit_or_abort(self.session):
            self.session.add(cti_profile)

        result = cti_profile_dao.get_name(cti_profile.id)

        self.assertEqual(result, cti_profile.name)

    def _add_presence(self, name):
        cti_presence = CtiPresences()
        cti_presence.name = name

        with commit_or_abort(self.session):
            self.session.add(cti_presence)
        return cti_presence.id

    def _add_phone_hints_group(self, name):
        cti_phone_hints_group = CtiPhoneHintsGroup()
        cti_phone_hints_group.name = name

        with commit_or_abort(self.session):
            self.session.add(cti_phone_hints_group)

        return cti_phone_hints_group.id

    def _add_profile(self, name):
        cti_profile = CtiProfile()
        cti_profile.name = name
        cti_profile.presence_id = self._add_presence('test_presence')
        cti_profile.phonehints_id = self._add_phone_hints_group('test_add_phone_hints_group')

        with commit_or_abort(self.session):
            self.session.add(cti_profile)

        return cti_profile.id

    def _add_xlet_layout(self, name):
        cti_xlet_layout = CtiXletLayout()
        cti_xlet_layout.name = name

        with commit_or_abort(self.session):
            self.session.add(cti_xlet_layout)

        return cti_xlet_layout.id

    def _add_xlet(self, name):
        cti_xlet = CtiXlet()
        cti_xlet.plugin_name = name

        with commit_or_abort(self.session):
            self.session.add(cti_xlet)

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

        with commit_or_abort(self.session):
            self.session.add(cti_profile_xlet)

    def test_get_profiles(self):
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
        expected_result = {
            profile_id: {
                "id": profile_id,
                "name": "test_profile",
                "phonestatus": "test_add_phone_hints_group",
                "userstatus": "test_presence",
                "preferences": "itm_preferences_test_profile",
                "services": "itm_services_test_profile",
                "xlets": [
                    {'name': 'agentdetails',
                     'layout': 'dock',
                     'floating': False,
                     'closable': True,
                     'movable': True,
                     'scrollable': True,
                     'order': 0},
                    {'name': 'tabber',
                     'layout': 'grid',
                     'floating': True,
                     'closable': True,
                     'movable': True,
                     'scrollable': True,
                     'order': 1}
                ]
            }
        }

        result = cti_profile_dao.get_profiles()

        self.assertEquals(result, expected_result)
