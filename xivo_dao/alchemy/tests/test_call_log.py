# -*- coding: utf-8 -*-
#
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
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

from hamcrest import (assert_that,
                      contains,
                      contains_inanyorder,
                      empty,
                      equal_to,
                      none,
                      not_)
from xivo_dao.alchemy.call_log import CallLog
from xivo_dao.alchemy.call_log_participant import CallLogParticipant
from xivo_dao.tests.test_dao import DAOTestCase


class TestCallLogs(DAOTestCase):

    def test_participants_get(self):
        call_log = self.add_call_log()
        alice = self.add_call_log_participant(call_log_id=call_log.id, user_uuid='alice_uuid')
        bob = self.add_call_log_participant(call_log_id=call_log.id, user_uuid='bod_uuid')

        row = self.session.query(CallLog).first()

        assert_that(row.participants, contains_inanyorder(alice, bob))

    def test_participants_user_uuids_get(self):
        call_log = self.add_call_log()
        self.add_call_log_participant(call_log_id=call_log.id, user_uuid='alice_uuid')
        self.add_call_log_participant(call_log_id=call_log.id, user_uuid='bob_uuid')

        row = self.session.query(CallLog).first()

        assert_that(row.participant_user_uuids, contains_inanyorder('alice_uuid', 'bob_uuid'))

    def test_participants_set(self):
        call_log = self.add_call_log()
        participant = CallLogParticipant(uuid='something',
                                         call_log_id=call_log.id,
                                         user_uuid='something_else',
                                         role='source')

        call_log.participants.append(participant)
        self.session.expire_all()

        row = self.session.query(CallLogParticipant).first()
        assert_that(row, equal_to(participant))

    def test_participant_cascade_when_delete_call_log_then_delete_participant(self):
        call_log = self.add_call_log()
        participant = self.add_call_log_participant(uuid='something',
                                                    call_log_id=call_log.id,
                                                    user_uuid='something_else',
                                                    role='source')
        call_log.participants.append(participant)
        self.session.flush()

        self.session.delete(call_log)

        row = self.session.query(CallLogParticipant).first()
        assert_that(row, none())

    def test_participant_cascade_when_delete_participant_then_call_log_remains(self):
        call_log = self.add_call_log()
        participant = self.add_call_log_participant(uuid='something',
                                                    call_log_id=call_log.id,
                                                    user_uuid='something_else',
                                                    role='source')

        self.session.delete(participant)

        row = self.session.query(CallLog).first()
        assert_that(row, equal_to(call_log))
