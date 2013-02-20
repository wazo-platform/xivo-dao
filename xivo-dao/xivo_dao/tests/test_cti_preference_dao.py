# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Avencall
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

from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao import cti_profile_dao, cti_preference_dao
from xivo_dao.alchemy.ctiphonehintsgroup import CtiPhoneHintsGroup
from xivo_dao.alchemy.ctipresences import CtiPresences
from xivo_dao.alchemy.cti_profile_preference import CtiProfilePreference
from xivo_dao.alchemy.cti_preference import CtiPreference
from xivo_dao.tests.test_dao import DAOTestCase


class TestCtiPreferenceDAO(DAOTestCase):

    tables = [CtiProfile, CtiPhoneHintsGroup,
              CtiPresences, CtiProfilePreference, CtiPreference]

    def setUp(self):
        self.empty_tables()

    def test_get_name(self):
        cti_profile = CtiProfile()
        cti_profile.name = 'test_name'

        self.session.begin()
        self.session.add(cti_profile)
        self.session.commit()

        result = cti_profile_dao.get_name(cti_profile.id)

        self.assertEqual(result, cti_profile.name)

    def _add_presence(self, name):
        cti_presence = CtiPresences()
        cti_presence.name = name

        self.session.begin()
        self.session.add(cti_presence)
        self.session.commit()
        return cti_presence.id

    def _add_preference(self, name):
        cti_preference = CtiPreference()
        cti_preference.option = name

        self.session.begin()
        self.session.add(cti_preference)
        self.session.commit()
        return cti_preference.id

    def _add_phone_hints_group(self, name):
        cti_phone_hints_group = CtiPhoneHintsGroup()
        cti_phone_hints_group.name = name

        self.session.begin()
        self.session.add(cti_phone_hints_group)
        self.session.commit()
        return cti_phone_hints_group.id

    def _add_profile(self, name):
        cti_profile = CtiProfile()
        cti_profile.name = name
        cti_profile.presence_id = self._add_presence('test_presence')
        cti_profile.phonehints_id = self._add_phone_hints_group('test_add_phone_hints_group')

        self.session.begin()
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

        self.session.begin()
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
