# -*- coding: utf-8 -*-
# Copyright 2012-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao import cti_profile_dao, cti_service_dao
from xivo_dao.alchemy.ctiphonehintsgroup import CtiPhoneHintsGroup
from xivo_dao.alchemy.ctipresences import CtiPresences
from xivo_dao.alchemy.cti_profile_service import CtiProfileService
from xivo_dao.alchemy.cti_service import CtiService
from xivo_dao.tests.test_dao import DAOTestCase


class TestCtiServiceDAO(DAOTestCase):

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

    def _add_service(self, key):
        cti_service = CtiService()
        cti_service.key = key

        self.add_me(cti_service)
        return cti_service.id

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

    def _add_service_to_profile(self,
                                service_id,
                                profile_id):
        cti_profile_service = CtiProfileService()
        cti_profile_service.service_id = service_id
        cti_profile_service.profile_id = profile_id

        self.add_me(cti_profile_service)

    def test_get_profiles(self):
        expected_result = {
            "agent": [],
            "test_profile": ["enablednd",
                             "fwdunc",
                             "fwdbusy",
                             "fwdrna"]
        }

        service1_id = self._add_service('enablednd')
        service2_id = self._add_service('fwdunc')
        service3_id = self._add_service('fwdbusy')
        service4_id = self._add_service('fwdrna')

        self._add_profile('agent')
        test_profile_id = self._add_profile('test_profile')

        self._add_service_to_profile(service1_id, test_profile_id)
        self._add_service_to_profile(service2_id, test_profile_id)
        self._add_service_to_profile(service3_id, test_profile_id)
        self._add_service_to_profile(service4_id, test_profile_id)

        result = cti_service_dao.get_services()

        self.assertEqual(result, expected_result)
