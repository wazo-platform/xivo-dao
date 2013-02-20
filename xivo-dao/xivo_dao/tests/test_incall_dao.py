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
from xivo_dao.alchemy.groupfeatures import GroupFeatures
from xivo_dao.alchemy.incall import Incall
from xivo_dao.alchemy.meetmefeatures import MeetmeFeatures
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.voicemail import Voicemail
from xivo_dao.tests.test_dao import DAOTestCase


class TestIncallDAO(DAOTestCase):

    tables = [Incall, Dialaction, UserFeatures, GroupFeatures, QueueFeatures,
              MeetmeFeatures, Voicemail, CtiPresences, CtiPhoneHintsGroup, CtiProfile]

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

    def _insert_dialaction(self, incall_id, user_id=None):
        dialaction = Dialaction()
        dialaction.event = 'answer'
        dialaction.category = 'incall'
        dialaction.categoryval = str(incall_id)
        if user_id:
            dialaction.action = 'user'
            dialaction.actionarg1 = str(user_id)
        dialaction.actionarg2 = ''
        dialaction.linked = 1

        self.session.begin()
        self.session.add(dialaction)
        self.session.commit()

    def _insert_user(self, firstname):
        user = UserFeatures()
        user.firstname = firstname

        self.session.begin()
        self.session.add(user)
        self.session.commit()
        return user.id

    def test_get(self):
        incall_exten = '1001'
        incall_id = self._insert_incall(incall_exten)

        incall = incall_dao.get(incall_id)

        self.assertEqual(incall.exten, incall_exten)

    def test_get_join_elements_with_user(self):
        incall_exten = '1001'
        incall_id = self._insert_incall(incall_exten)
        user_id = self._insert_user('test_incall')
        self._insert_dialaction(incall_id, user_id=user_id)

        incall, dialaction, user, group, queue, meetme, voicemail = incall_dao.get_join_elements(incall_id)

        self.assertEqual(incall.exten, incall_exten)
        self.assertEqual(dialaction.categoryval, str(incall_id))
        self.assertEqual(user.id, user_id)
        self.assertEqual(group, None)
        self.assertEqual(queue, None)
        self.assertEqual(meetme, None)
        self.assertEqual(voicemail, None)

    def test_all_with_user(self):
        incall_exten1 = '1001'
        incall_id1 = self._insert_incall(incall_exten1)
        user_id1 = self._insert_user('test_incall1')
        self._insert_dialaction(incall_id1, user_id=user_id1)

        incall_exten2 = '1002'
        incall_id2 = self._insert_incall(incall_exten2)
        user_id2 = self._insert_user('test_incall2')
        self._insert_dialaction(incall_id2, user_id=user_id2)

        incall_full_infos = incall_dao.all()

        incall, dialaction, user, group, queue, meetme, voicemail = incall_full_infos[0]

        self.assertEqual(incall.exten, incall_exten1)
        self.assertEqual(dialaction.categoryval, str(incall_id1))
        self.assertEqual(user.id, user_id1)
        self.assertEqual(group, None)
        self.assertEqual(queue, None)
        self.assertEqual(meetme, None)
        self.assertEqual(voicemail, None)

        incall, dialaction, user, group, queue, meetme, voicemail = incall_full_infos[1]

        self.assertEqual(incall.exten, incall_exten2)
        self.assertEqual(dialaction.categoryval, str(incall_id2))
        self.assertEqual(user.id, user_id2)
        self.assertEqual(group, None)
        self.assertEqual(queue, None)
        self.assertEqual(meetme, None)
        self.assertEqual(voicemail, None)
