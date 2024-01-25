# Copyright 2007-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao import context_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestContextDAO(DAOTestCase):
    def test_get(self):
        context_name = 'test_context'
        tenant = self.add_tenant()

        self.add_context(name=context_name, tenant_uuid=tenant.uuid)

        context = context_dao.get(context_name)

        assert context.name == context_name
