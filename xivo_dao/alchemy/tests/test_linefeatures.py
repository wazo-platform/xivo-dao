# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, calling, equal_to, raises
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError

from xivo_dao.tests.test_dao import DAOTestCase

from ..linefeatures import LineFeatures


class TestConstraint(DAOTestCase):
    def test_many_endpoints(self):
        sip = self.add_endpoint_sip()
        sccp = self.add_sccpline()
        assert_that(
            calling(self.add_line).with_args(
                endpoint_sip_uuid=sip.uuid,
                endpoint_sccp_id=sccp.id,
            ),
            raises(IntegrityError),
        )


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

        result = (
            self.session.query(LineFeatures)
            .filter(
                and_(
                    LineFeatures.id == line.id,
                    LineFeatures.tenant_uuid.in_([tenant.uuid]),
                )
            )
            .first()
        )

        assert_that(result, equal_to(line))


class TestApplication(DAOTestCase):
    def test_getter(self):
        application = self.add_application()
        line = self.add_line(application_uuid=application.uuid)
        assert_that(line.application, equal_to(application))


class TestCallerID(DAOTestCase):
    def test_get_caller_id_by_name(self):
        sip = self.add_endpoint_sip(caller_id='"Test 1" <1000>')
        line = self.add_line(endpoint_sip_uuid=sip.uuid)

        result = (
            self.session.query(LineFeatures)
            .filter(LineFeatures.caller_id_name.ilike("test 1"))
            .first()
        )
        assert_that(result, equal_to(line))

    def test_get_caller_id_by_num(self):
        sip = self.add_endpoint_sip(caller_id='"Test 1" <1000>')
        line = self.add_line(endpoint_sip_uuid=sip.uuid)

        result = (
            self.session.query(LineFeatures)
            .filter(LineFeatures.caller_id_num.ilike("1000"))
            .first()
        )
        assert_that(result, equal_to(line))

    def test_get_inherited_callerid(self):
        template = self.add_endpoint_sip(caller_id='"Test 1" <1000>')
        sip = self.add_endpoint_sip(templates=[template])
        line = self.add_line(endpoint_sip_uuid=sip.uuid)

        result = (
            self.session.query(LineFeatures)
            .filter(LineFeatures.caller_id_name == "Test 1")
            .first()
        )
        assert_that(result, equal_to(line))
