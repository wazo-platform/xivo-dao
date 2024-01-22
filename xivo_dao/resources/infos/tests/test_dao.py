# Copyright 2014-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import uuid

from xivo_dao.alchemy.infos import Infos
from xivo_dao.resources.infos import dao as infos_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestGetInfos(DAOTestCase):

    def test_get_with_one_infos(self):
        xivo_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, __name__))
        wazo_version = '42.42'
        infos_row = Infos(
            uuid=xivo_uuid,
            wazo_version=wazo_version,
        )
        self.add_me(infos_row)

        infos = infos_dao.get()

        assert infos.uuid == xivo_uuid
        assert infos.wazo_version == wazo_version
