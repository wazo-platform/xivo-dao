# -*- coding: utf-8 -*-

# Copyright (C) 2007-2015 Avencall
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

from xivo_dao import extensions_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestExtensionsDAO(DAOTestCase):

    def test_exten_by_name(self):
        self.add_extension(type='extenfeatures',
                           typeval='enablednd',
                           exten='*25')
        self.add_extension(type='extenfeatures',
                           typeval='phoneprogfunckey',
                           exten='_*735')
        enablednd = extensions_dao.exten_by_name('enablednd')
        phoneprogfunckey = extensions_dao.exten_by_name('phoneprogfunckey')
        foo = extensions_dao.exten_by_name('foo')

        self.assertEqual(enablednd, '*25')
        self.assertEqual(phoneprogfunckey, '_*735')
        self.assertEqual(foo, '')
