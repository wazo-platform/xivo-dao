# -*- coding: utf-8 -*-

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

import datetime
from hamcrest import assert_that, contains, has_property

from xivo_dao.alchemy.cel import CEL as CELSchema
from xivo_dao.data_handler.cel import dao as cel_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestCELDAO(DAOTestCase):

    tables = [
        CELSchema
    ]

    def setUp(self):
        self.empty_tables()

    def tearDown(self):
        pass

    def test_find_last_under_limit(self):
        limit = 10

        result = cel_dao.find_last(limit)

        assert_that(result, contains())

    def test_find_last_over_limit(self):
        limit = 2
        _, cel_id_2, cel_id_3 = self._add_cel(), self._add_cel(), self._add_cel()

        result = cel_dao.find_last(limit)

        assert_that(result, contains(has_property('id', cel_id_2),
                                     has_property('id', cel_id_3)))

    def _add_cel(self):
        cel = CELSchema(
            eventtype='eventtype',
            eventtime=datetime.datetime.now(),
            userdeftype='userdeftype',
            cid_name='cid_name',
            cid_num='cid_num',
            cid_ani='cid_ani',
            cid_rdnis='cid_rdnis',
            cid_dnid='cid_dnid',
            exten='exten',
            context='context',
            channame='channame',
            appname='appname',
            appdata='appdata',
            amaflags=0,
            accountcode='accountcode',
            peeraccount='peeraccount',
            uniqueid='uniqueid',
            linkedid='linkedid',
            userfield='userfield',
            peer='peer',
        )
        self.add_me(cel)
        return cel.id
