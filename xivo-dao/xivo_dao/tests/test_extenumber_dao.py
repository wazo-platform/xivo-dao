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
from xivo_dao import extenumber_dao
from xivo_dao.alchemy.extenumber import ExteNumber
from xivo_dao.tests.test_dao import DAOTestCase

class TestExteNumberDAO(DAOTestCase):

    tables = [ExteNumber]

    def setUp(self):
        self.empty_tables()

    def test_create(self):
        ext = ExteNumber()
        ext.context = "default"
        ext.type = "user"

        extenumber_dao.create(ext)
        self.assertTrue(ext.id > 0)
        self.assertTrue(ext in self._get_all())

    def _get_all(self):
        return self.session.query(ExteNumber).all()
