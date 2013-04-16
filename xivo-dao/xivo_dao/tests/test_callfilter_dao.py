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
from xivo_dao import callfilter_dao
from xivo_dao.alchemy.callfilter import Callfilter
from xivo_dao.tests.test_dao import DAOTestCase

class TestCallFilterDAO(DAOTestCase):

    tables = [Callfilter]

    def setUp(self):
        self.cleanTables()

    def test_add(self):
        callfilter = Callfilter()
        callfilter.callfrom = 'internal'
        callfilter.type = 'bosssecretary'
        callfilter.bosssecretary = 'bossfirst-serial'
        callfilter.name = 'test'
        callfilter.description = ''

        callfilter_dao.add(callfilter)
        result = self.session.query(Callfilter).first()
        self.assertEquals(result.name, 'test')
