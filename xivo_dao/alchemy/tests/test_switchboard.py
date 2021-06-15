# -*- coding: utf-8 -*-
# Copyright 2020-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    equal_to,
    is_,
    none,
)

from xivo_dao.tests.test_dao import DAOTestCase

from ..dialaction import Dialaction
from ..switchboard import Switchboard


class TestDelete(DAOTestCase):

    def test_ivr_dialactions_are_deleted(self):
        switchboard = self.add_switchboard()
        self.add_dialaction(category='ivr_choice', action='switchboard', actionarg1=switchboard.uuid)
        self.add_dialaction(category='ivr', action='switchboard', actionarg1=switchboard.uuid)
        self.add_dialaction(category='user', action='switchboard', actionarg1=switchboard.uuid)
        self.add_dialaction(category='incall', action='switchboard', actionarg1=switchboard.uuid)

        self.session.delete(switchboard)
        self.session.flush()

        row = self.session.query(Dialaction).first()
        assert_that(row, none())

    def test_queue_music_on_hold(self):
        moh_name = 'my-moh'
        moh = self.add_moh(name=moh_name)
        self.add_switchboard(queue_moh_uuid=moh.uuid)

        row = self.session.query(Switchboard).first()
        assert_that(row.queue_music_on_hold, equal_to(moh_name))

    def test_waiting_room_music_on_hold(self):
        moh_name = 'my-moh'
        moh = self.add_moh(name=moh_name)
        self.add_switchboard(hold_moh_uuid=moh.uuid)

        row = self.session.query(Switchboard).first()
        assert_that(row.waiting_room_music_on_hold, equal_to(moh_name))

    def test_queue_music_on_hold_not_configured(self):
        self.add_switchboard()

        row = self.session.query(Switchboard).first()
        assert_that(row.queue_music_on_hold, is_(none()))

    def test_waiting_room_music_on_hold_not_configured(self):
        self.add_switchboard()

        row = self.session.query(Switchboard).first()
        assert_that(row.waiting_room_music_on_hold, is_(none()))
