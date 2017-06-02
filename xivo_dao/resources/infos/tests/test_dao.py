# -*- coding: utf-8 -*-
#
# Copyright 2014-2016 The Wazo Authors  (see the AUTHORS file)
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

import uuid
import six

from xivo_dao.alchemy.infos import Infos
from xivo_dao.resources.infos import dao as infos_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestGetInfos(DAOTestCase):

    def test_get_with_one_infos(self):
        xivo_uuid = six.text_type(uuid.uuid5(uuid.NAMESPACE_DNS, __name__))
        wazo_version = '42.42'
        infos_row = Infos(
            uuid=xivo_uuid,
            wazo_version=wazo_version,
        )
        self.add_me(infos_row)

        infos = infos_dao.get()

        self.assertEqual(infos.uuid, xivo_uuid)
        self.assertEqual(infos.wazo_version, wazo_version)
