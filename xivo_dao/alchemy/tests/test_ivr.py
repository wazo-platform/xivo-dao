# Copyright 2017-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, none

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.tests.test_dao import DAOTestCase


class TestDelete(DAOTestCase):
    def test_dialaction_actions_are_deleted(self):
        ivr = self.add_ivr()
        self.add_dialaction(category='ivr_choice', action='ivr', actionarg1=ivr.id)
        self.add_dialaction(category='ivr', action='ivr', actionarg1=ivr.id)
        self.add_dialaction(category='user', action='ivr', actionarg1=ivr.id)
        self.add_dialaction(category='incall', action='ivr', actionarg1=ivr.id)

        self.session.delete(ivr)
        self.session.flush()

        row = self.session.query(Dialaction).first()
        assert_that(row, none())
