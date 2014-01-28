# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.ctimain import CtiMain
from xivo_dao.data_handler.configuration import dao


class TestConfigurationDao(DAOTestCase):

    tables = [CtiMain]

    def setUp(self):
        self.empty_tables()

    def test_get_live_reload_status(self):
        ctimain = CtiMain(live_reload_conf=0)
        self.add_me(ctimain)

        result = dao.get_live_reload_status()

        self.assertFalse(result)

        ctimain.live_reload_conf = 1
        self.add_me(ctimain)

        result = dao.get_live_reload_status()

        self.assertTrue(result)
