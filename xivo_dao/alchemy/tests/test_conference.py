# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (assert_that,
                      none,
                      contains_inanyorder)

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.tests.test_dao import DAOTestCase


class TestIncalls(DAOTestCase):

    def test_getter(self):
        group = self.add_group()
        incall1 = self.add_incall(destination=Dialaction(action='group',
                                                         actionarg1=str(group.id)))
        incall2 = self.add_incall(destination=Dialaction(action='group',
                                                         actionarg1=str(group.id)))

        assert_that(group.incalls, contains_inanyorder(incall1, incall2))


class TestDelete(DAOTestCase):

    def test_ivr_dialactions_are_deleted(self):
        conference = self.add_conference()
        self.add_dialaction(category='ivr_choice', action='conference', actionarg1=conference.id)
        self.add_dialaction(category='ivr', action='conference', actionarg1=conference.id)

        self.session.delete(conference)
        self.session.flush()

        row = self.session.query(Dialaction).first()
        assert_that(row, none())
