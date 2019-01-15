# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao import cti_userstatus_dao
from xivo_dao.alchemy.ctipresences import CtiPresences
from xivo_dao.alchemy.ctistatus import CtiStatus
from xivo_dao.tests.test_dao import DAOTestCase


class TestCtiUserStatusDAO(DAOTestCase):

    def test_get_status_with_presence_id(self):
        cti_presence_id_1 = self._add_presence('test1')
        self._add_status(cti_presence_id_1, 'available', '', '#08FD20', '')
        self._add_status(cti_presence_id_1, 'disconnected', '', '#202020', '')

        cti_presence_id_2 = self._add_presence('test2')
        self._add_status(cti_presence_id_2, 'available', '', '#08FD20', '')
        self._add_status(cti_presence_id_2, 'disconnected', '', '#202020', '')
        self._add_status(cti_presence_id_2, 'away', '', '#202020', '')

        result_1 = cti_userstatus_dao.get_statuses_with_presence_id(cti_presence_id_1)
        self.assertEqual(2, len(result_1))

        result_2 = cti_userstatus_dao.get_statuses_with_presence_id(cti_presence_id_2)
        self.assertEqual(3, len(result_2))

    def test_get_config(self):
        expected_result = {
            "test1": {
                "available": {
                    "longname": "available",
                    "color": "#08FD20"
                },
                "disconnected": {
                    "longname": "disconnected",
                    "color": "#202020"
                }
            },
            "test2": {
                "available": {
                    "longname": "available",
                    "color": "#08FD20",
                    "actions": {"enablednd": "false",
                                "queuepause_all": ""}
                },
                "disconnected": {
                    "longname": "disconnected",
                    "color": "#202020",
                    "allowed": ["available"],
                    "actions": {"agentlogoff": ""}
                }
            }
        }

        cti_presence_id_1 = self._add_presence('test1')
        self._add_status(cti_presence_id_1, 'available', '', '#08FD20', '')
        self._add_status(cti_presence_id_1, 'disconnected', '', '#202020', '')

        cti_presence_id_2 = self._add_presence('test2')
        actions = 'enablednd(false),queuepause_all()'
        status_id = self._add_status(cti_presence_id_2, 'available', actions, '#08FD20', '')
        actions = 'agentlogoff()'
        self._add_status(cti_presence_id_2, 'disconnected', actions, '#202020', '%s' % status_id)

        result = cti_userstatus_dao.get_config()

        self.assertEqual(expected_result, result)

    def test_get_config_status_with_inexistant_access_status(self):
        expected_result = {
            "test1": {
                "available": {
                    "longname": "available",
                    "color": "#08FD20"
                },
                "invalid": {
                    "longname": "invalid",
                    "color": "#303030"
                }
            }
        }

        cti_presence_id_1 = self._add_presence('test1')
        self._add_status(cti_presence_id_1, 'available', '', '#08FD20', '')
        self._add_status(cti_presence_id_1, 'invalid', '', '#303030', '0')

        result = cti_userstatus_dao.get_config()

        self.assertEqual(expected_result, result)

    def test_get_config_status_with_invalid_access_status(self):
        expected_result = {
            "test1": {
                "available": {
                    "longname": "available",
                    "color": "#08FD20"
                },
                "away": {
                    "longname": "away",
                    "color": "#101010",
                    "allowed": ["available"],
                }
            }
        }

        cti_presence_id_1 = self._add_presence('test1')
        status_id_1 = self._add_status(cti_presence_id_1, 'available', '', '#08FD20', '')

        invalid_access_status = '%s,0' % status_id_1
        self._add_status(cti_presence_id_1, 'away', '', '#101010', invalid_access_status)

        result = cti_userstatus_dao.get_config()

        self.assertEqual(expected_result, result)

    def _add_presence(self, name):
        cti_presence = CtiPresences()
        cti_presence.name = name

        self.add_me(cti_presence)
        return cti_presence.id

    def _add_status(self, presence_id, name, actions, color, access_status):
        cti_status = CtiStatus()
        cti_status.presence_id = presence_id
        cti_status.name = name
        cti_status.display_name = name
        cti_status.actions = actions
        cti_status.color = color
        cti_status.access_status = access_status

        self.add_me(cti_status)
        return cti_status.id
