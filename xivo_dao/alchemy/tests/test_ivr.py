# -*- coding: utf-8 -*-

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
