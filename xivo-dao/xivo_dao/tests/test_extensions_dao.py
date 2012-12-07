#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from xivo_dao import extensionsdao
from xivo_dao.alchemy.extension import Extension
from xivo_dao.tests.test_dao import DAOTestCase


class TestExtensionsDAO(DAOTestCase):

    tables = [Extension]

    def setUp(self):
        self.empty_tables()
        self._insert_extens()

    def _insert_extens(self):
        exten = Extension()
        exten.name = 'enablednd'
        exten.exten = '*25'
        self.session.add(exten)
        exten = Extension()
        exten.name = 'phoneprogfunckey'
        exten.exten = '_*735'
        self.session.add(exten)
        self.session.commit()

    def test_exten_by_name(self):
        enablednd = extensionsdao.exten_by_name('enablednd')
        phoneprogfunckey = extensionsdao.exten_by_name('phoneprogfunckey')

        self.assertEqual(enablednd, '*25')
        self.assertEqual(phoneprogfunckey, '_*735')
