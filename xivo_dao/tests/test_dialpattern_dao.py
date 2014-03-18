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

from xivo_dao import dialpattern_dao
from xivo_dao.alchemy.dialpattern import DialPattern
from xivo_dao.tests.test_dao import DAOTestCase


class TestDialPatternDAO(DAOTestCase):

    tables = [DialPattern]

    def test_delete(self):
        dialpattern = self.add_dialpattern()

        deleted_rows_count = dialpattern_dao.delete(dialpattern.id)

        row = self.session.query(DialPattern).filter(DialPattern.id == dialpattern.id).first()

        self.assertEquals(deleted_rows_count, 1)
        self.assertEquals(row, None)

    def test_delete_unexisting_dialpattern(self):
        result = dialpattern_dao.delete(1)
        self.assertEqual(result, 0)
