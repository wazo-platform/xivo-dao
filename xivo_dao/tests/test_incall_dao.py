# -*- coding: utf-8 -*-
# Copyright 2007-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao import incall_dao
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.incall import Incall
from xivo_dao.tests.test_dao import DAOTestCase


class TestIncallDAO(DAOTestCase):

    def _insert_incall(self, exten, context='from-extern'):
        incall = Incall()
        incall.exten = exten
        incall.context = context
        incall.description = 'description'
        incall.tenant_uuid = self.default_tenant.uuid

        self.add_me(incall)

        return incall.id

    def _insert_dialaction(self, incall_id, action, actionarg1):
        dialaction = Dialaction()
        dialaction.event = 'answer'
        dialaction.category = 'incall'
        dialaction.categoryval = str(incall_id)
        dialaction.action = action
        dialaction.actionarg1 = actionarg1
        dialaction.actionarg2 = ''
        dialaction.linked = 1

        self.add_me(dialaction)

    def test_get_by_exten(self):
        incall_exten = '1001'
        incall_action = 'user'
        incall_actionarg1 = '42'
        incall_id = self._insert_incall(incall_exten)
        self._insert_dialaction(incall_id, incall_action, incall_actionarg1)

        incall = incall_dao.get_by_exten(incall_exten)

        self.assertEqual(incall.id, incall_id)
        self.assertEqual(incall.action, incall_action)
        self.assertEqual(incall.actionarg1, incall_actionarg1)
