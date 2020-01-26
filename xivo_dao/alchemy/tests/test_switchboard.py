# -*- coding: utf-8 -*-
# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    none,
)

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.tests.test_dao import DAOTestCase


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
