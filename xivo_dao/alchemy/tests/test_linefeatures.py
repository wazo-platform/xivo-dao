# -*- coding: utf-8 -*-
# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    equal_to,
)
from sqlalchemy import and_

from xivo_dao.tests.test_dao import DAOTestCase

from ..linefeatures import LineFeatures


class TestTenantUUID(DAOTestCase):

    def test_tenant_uuid_getter(self):
        tenant = self.add_tenant()
        context = self.add_context(tenant_uuid=tenant.uuid)

        line = self.add_line(context=context.name)

        assert_that(line.tenant_uuid, equal_to(tenant.uuid))

    def test_tenant_uuid_expression(self):
        tenant = self.add_tenant()
        context = self.add_context(tenant_uuid=tenant.uuid)

        line = self.add_line(context=context.name)

        result = self.session.query(LineFeatures).filter(and_(
            LineFeatures.id == line.id,
            LineFeatures.tenant_uuid.in_([tenant.uuid]),
        )).first()

        assert_that(result, equal_to(line))


class TestApplication(DAOTestCase):

    def test_getter(self):
        application = self.add_application()
        line = self.add_line(application_uuid=application.uuid)

        assert_that(line.application, equal_to(application))
