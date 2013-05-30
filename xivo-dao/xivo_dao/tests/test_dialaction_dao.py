# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Avencall
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


from xivo_dao import dialaction_dao
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.tests.test_dao import DAOTestCase


class TestDialactionDAO(DAOTestCase):

    tables = [Dialaction]

    def setUp(self):
        self.empty_tables()

    def test_add(self):
        dialaction = Dialaction()
        dialaction.action = 'none'
        dialaction.category = 'user'
        dialaction.categoryval = '1'
        dialaction.event = 'answer'

        dialaction_dao.add(dialaction)

        self.assertEquals(dialaction, self.session.query(Dialaction).first())

    def test_get_by_userid(self):
        self._insert_dialaction(1)
        self._insert_dialaction(2)
        result = dialaction_dao.get_by_userid(1)
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].categoryval, '1')

    def _insert_dialaction(self, categoryval, category='user', action='none', event='answer'):
        dialaction = Dialaction()
        dialaction.action = action
        dialaction.category = category
        dialaction.categoryval = str(categoryval)
        dialaction.event = event
        self.add_me(dialaction)

    def test_delete_by_userid(self):
        self._insert_dialaction(1)
        self._insert_dialaction(2)
        dialaction_dao.delete_by_userid(1)

        result = self.session.query(Dialaction).all()
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].categoryval, '2')
