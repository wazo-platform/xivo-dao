# -*- coding: utf-8 -*-

# Copyright 2012-2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao import cti_profile_dao, cti_preference_dao
from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao.alchemy.ctiphonehintsgroup import CtiPhoneHintsGroup
from xivo_dao.alchemy.ctipresences import CtiPresences
from xivo_dao.alchemy.cti_profile_preference import CtiProfilePreference
from xivo_dao.alchemy.cti_preference import CtiPreference
from xivo_dao.tests.test_dao import DAOTestCase


class TestCtiPreferenceDAO(DAOTestCase):

    def test_get_name(self):
        cti_profile = CtiProfile()
        cti_profile.name = 'test_name'

        self.add_me(cti_profile)

        result = cti_profile_dao.get_name(cti_profile.id)

        self.assertEqual(result, cti_profile.name)

    def _add_presence(self, name):
        cti_presence = CtiPresences()
        cti_presence.name = name

        self.add_me(cti_presence)
        return cti_presence.id

    def _add_preference(self, name):
        cti_preference = CtiPreference()
        cti_preference.option = name

        self.add_me(cti_preference)
        return cti_preference.id

    def _add_phone_hints_group(self, name):
        cti_phone_hints_group = CtiPhoneHintsGroup()
        cti_phone_hints_group.name = name

        self.add_me(cti_phone_hints_group)
        return cti_phone_hints_group.id

    def _add_profile(self, name):
        cti_profile = CtiProfile()
        cti_profile.name = name
        cti_profile.presence_id = self._add_presence('test_presence')
        cti_profile.phonehints_id = self._add_phone_hints_group('test_add_phone_hints_group')

        self.add_me(cti_profile)
        return cti_profile.id

    def _add_preference_to_profile(self,
                                   preference_id,
                                   profile_id,
                                   value):
        cti_profile_preference = CtiProfilePreference()
        cti_profile_preference.preference_id = preference_id
        cti_profile_preference.profile_id = profile_id
        cti_profile_preference.value = value

        self.add_me(cti_profile_preference)

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

        self.assertEqual(result, expected_result)
