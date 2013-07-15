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

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.linefeatures import LineFeatures as LineSchema
from xivo_dao.data_handler.line.helpers import make_provisioning_id


class TestHelpers(DAOTestCase):

    tables = [
        LineSchema
    ]

    def setUp(self):
        self.empty_tables()

    def test_make_provisioning_id(self):
        provd_id = make_provisioning_id(self.session)
        line_id = self.add_line(provisioningid=provd_id)

        row = (self.session.query(LineSchema)
               .filter(LineSchema.id == line_id)
               .first())
        self.assertEquals(row.provisioningid, provd_id)

    def test_make_provisioning_id_invalid(self):
        for _ in range(1000):
            provd_id = make_provisioning_id(self.session)
            self.assertEquals(len(str(provd_id)), 6)
            self.assertEquals(str(provd_id).startswith('0'), False)

    def test_make_provisioning_id_already_exist(self):
        exist_provd_id = 111111

        provd_id = make_provisioning_id(self.session, exist_provd_id)
        line_id = self.add_line(provisioningid=provd_id)

        row = (self.session.query(LineSchema)
               .filter(LineSchema.id == line_id)
               .first())
        self.assertEquals(row.provisioningid, provd_id)

        provd_id = make_provisioning_id(self.session, exist_provd_id)
        line_id = self.add_line(provisioningid=provd_id)

        self.assertNotEquals(provd_id, exist_provd_id)

        row = (self.session.query(LineSchema)
               .filter(LineSchema.id == line_id)
               .first())
        self.assertEquals(row.provisioningid, provd_id)
