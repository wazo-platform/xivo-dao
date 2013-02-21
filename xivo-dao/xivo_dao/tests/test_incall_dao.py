# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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

from xivo_dao import incall_dao
from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao.alchemy.ctiphonehintsgroup import CtiPhoneHintsGroup
from xivo_dao.alchemy.ctipresences import CtiPresences
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.incall import Incall
from xivo_dao.tests.test_dao import DAOTestCase


class TestIncallDAO(DAOTestCase):

    tables = [Incall, Dialaction, CtiPresences, CtiPhoneHintsGroup, CtiProfile]

    def setUp(self):
        self.empty_tables()

    def _insert_incall(self, exten, context='from-extern'):
        incall = Incall()
        incall.exten = exten
        incall.context = context
        incall.description = 'description'

        self.session.begin()
        self.session.add(incall)
        self.session.commit()
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

        self.session.begin()
        self.session.add(dialaction)
        self.session.commit()

    def test_get(self):
        incall_exten = '1001'
        incall_action = 'user'
        incall_actionarg1 = '42'
        incall_id = self._insert_incall(incall_exten)
        self._insert_dialaction(incall_id, incall_action, incall_actionarg1)

        incall = incall_dao.get(incall_id)

        self.assertEqual(incall.id, incall_id)
        self.assertEqual(incall.action, incall_action)
        self.assertEqual(incall.actionarg1, incall_actionarg1)

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
