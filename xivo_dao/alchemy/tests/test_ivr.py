# -*- coding: utf-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import assert_that, none

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.tests.test_dao import DAOTestCase


class TestDelete(DAOTestCase):

    def test_ivr_dialactions_are_deleted(self):
        ivr = self.add_ivr()
        self.add_dialaction(category='ivr_choice', action='ivr', actionarg1=ivr.id)
        self.add_dialaction(category='ivr', action='ivr', actionarg1=ivr.id)

        self.session.delete(ivr)
        self.session.flush()

        row = self.session.query(Dialaction).first()
        assert_that(row, none())
