# Copyright 2020-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    empty,
    equal_to,
    has_key,
    has_properties,
    is_,
    is_not,
    none,
)

from xivo_dao.tests.test_dao import DAOTestCase

from ..dialaction import Dialaction
from ..switchboard import Switchboard


class TestDelete(DAOTestCase):
    def test_ivr_dialactions_are_deleted(self):
        switchboard = self.add_switchboard()
        self.add_dialaction(
            category='ivr_choice', action='switchboard', actionarg1=switchboard.uuid
        )
        self.add_dialaction(
            category='ivr', action='switchboard', actionarg1=switchboard.uuid
        )
        self.add_dialaction(
            category='user', action='switchboard', actionarg1=switchboard.uuid
        )
        self.add_dialaction(
            category='incall', action='switchboard', actionarg1=switchboard.uuid
        )

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


class TestFallbacks(DAOTestCase):
    def test_getter(self):
        switchboard = self.add_switchboard()
        dialaction = self.add_dialaction(
            event='key', category='switchboard', categoryval=str(switchboard.uuid)
        )

        assert_that(switchboard.fallbacks['key'], equal_to(dialaction))

    def test_setter(self):
        switchboard = self.add_switchboard()
        dialaction = Dialaction(action='none')

        switchboard.fallbacks = {'key': dialaction}
        self.session.flush()

        assert_that(switchboard.fallbacks['key'], equal_to(dialaction))

    def test_setter_to_none(self):
        switchboard = self.add_switchboard()

        switchboard.fallbacks = {'key': None}
        self.session.flush()

        assert_that(switchboard.fallbacks, empty())

    def test_setter_existing_key(self):
        switchboard = self.add_switchboard()
        dialaction1 = Dialaction(action='none')

        switchboard.fallbacks = {'key': dialaction1}
        self.session.flush()
        self.session.expire_all()

        dialaction2 = Dialaction(action='user', actionarg1='1')
        switchboard.fallbacks = {'key': dialaction2}
        self.session.flush()

        assert_that(
            switchboard.fallbacks['key'], has_properties(action='user', actionarg1='1')
        )

    def test_setter_delete_undefined_key(self):
        switchboard = self.add_switchboard()
        dialaction1 = Dialaction(action='none')

        switchboard.fallbacks = {'noanswer': dialaction1}
        self.session.flush()
        self.session.expire_all()

        dialaction2 = Dialaction(action='user', actionarg1='1')
        switchboard.fallbacks = {'busy': dialaction2}
        self.session.flush()

        assert_that(switchboard.fallbacks, is_not(has_key('noanswer')))
