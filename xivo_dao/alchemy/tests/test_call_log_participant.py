# -*- coding: utf-8 -*-
# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains,
    contains_inanyorder,
    has_properties,
)
from xivo_dao.alchemy.call_log import CallLog
from xivo_dao.alchemy.call_log_participant import CallLogParticipant
from xivo_dao.tests.test_dao import DAOTestCase


class TestCallLogs(DAOTestCase):

    def test_peer_exten_property(self):
        alice_exten = '101'
        bob_exten = '102'

        call_log = self.add_call_log(source_exten=alice_exten, requested_exten=bob_exten)
        self.add_call_log_participant(
            call_log_id=call_log.id, user_uuid='alice_uuid', role='source',
        )
        self.add_call_log_participant(
            call_log_id=call_log.id, user_uuid='bob_uuid', role='destination',
        )

        row = self.session.query(CallLog).first()

        assert_that(
            row.participants,
            contains_inanyorder(
                has_properties(user_uuid='alice_uuid', peer_exten=bob_exten),
                has_properties(user_uuid='bob_uuid', peer_exten=alice_exten),
            ),
        )

    def test_peer_exten_expression(self):
        alice_exten = '101'
        bob_exten = '102'

        call_log = self.add_call_log(source_exten=alice_exten, requested_exten=bob_exten)
        self.add_call_log_participant(
            call_log_id=call_log.id, user_uuid='alice_uuid', role='source',
        )
        bob = self.add_call_log_participant(
            call_log_id=call_log.id, user_uuid='bod_uuid', role='destination',
        )

        rows = self.session.query(CallLogParticipant).filter(
            CallLogParticipant.peer_exten == alice_exten,
        ).all()

        assert_that(rows, contains(bob))
