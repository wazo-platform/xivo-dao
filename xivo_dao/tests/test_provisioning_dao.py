# -*- coding: utf-8 -*-
# Copyright 2013-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

from xivo_dao import provisioning_dao
from xivo_dao.alchemy.provisioning import Provisioning
from xivo_dao.tests.test_dao import DAOTestCase


class TestProvisionningDao(DAOTestCase):

    def test_get_provd_rest_host_and_port(self):
        self._insert_provisionning()
        result = provisioning_dao.get_provd_rest_host_and_port()
        self.assertEqual(result, ('127.0.0.1', 1234))

    def _insert_provisionning(self):
        provisioning = Provisioning(
            net4_ip='',
            net4_ip_rest='127.0.0.1',
            dhcp_integration=0,
            rest_port=1234,
            http_port=8667,
        )

        self.add_me(provisioning)

        return provisioning
