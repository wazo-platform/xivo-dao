# -*- coding: utf-8 -*-
# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    calling,
    contains,
    contains_inanyorder,
    equal_to,
    none,
    raises,
)
from sqlalchemy.exc import IntegrityError
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

    def test_source_user_uuids_get(self):
        call_log = self.add_call_log()
        self.add_call_log_participant(call_log_id=call_log.id, user_uuid='alice_uuid', role='source')
        self.add_call_log_participant(call_log_id=call_log.id, user_uuid='bob_uuid', role='destination')

        row = self.session.query(CallLog).first()

        assert_that(row.source_user_uuid, equal_to('alice_uuid'))
        assert_that(row.destination_user_uuid, equal_to('bob_uuid'))

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

    def test_cel_ids(self):
        cel_id1 = self.add_cel()
        cel_id2 = self.add_cel()
        call_log = self.add_call_log()
        call_log.cel_ids = [cel_id1, cel_id2]

        assert_that(call_log.cel_ids, contains(cel_id1, cel_id2))

    def test_direction_constraint_invalid(self):
        assert_that(calling(self.add_call_log).with_args(direction='invalid'),
                    raises(IntegrityError))

    def test_direction_constraint_none(self):
        call_log = self.add_call_log(direction=None)
        assert_that(call_log)

    def test_direction_constraint_valid(self):
        call_log = self.add_call_log(direction='internal')
        assert_that(call_log)
