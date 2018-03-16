# -*- coding: UTF-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import assert_that, equal_to, has_properties
from xivo_dao.tests.test_dao import DAOTestCase

from .. import tenant_dao


class TestTenantDAO(DAOTestCase):

    def test_get_or_create_tenant(self):
        existing_uuid = '7c3fa683-4458-40f1-a7a3-e9a98962aeca'
        new_uuid = 'cb66267c-b8b9-49f5-9309-8a7fc9d420dc'
        tenant = self.add_tenant(uuid=existing_uuid)

        result = tenant_dao.get_or_create_tenant(existing_uuid)
        assert_that(result, equal_to(tenant))

        result = tenant_dao.get_or_create_tenant(new_uuid)
        assert_that(result, has_properties(uuid=new_uuid))
