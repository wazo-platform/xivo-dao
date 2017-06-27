# -*- coding: utf-8 -*-

# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
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
