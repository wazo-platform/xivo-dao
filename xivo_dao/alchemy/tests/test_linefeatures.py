# -*- coding: utf-8 -*-
# Copyright 2018-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import random
from hamcrest import (
    assert_that,
    calling,
    equal_to,
    raises,
)
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError

from xivo_dao.tests.test_dao import DAOTestCase

from ..linefeatures import LineFeatures


class TestConstraint(DAOTestCase):

    def test_many_endpoints(self):
        sip = self.add_endpoint_sip()
        sccp = self.add_sccpline()
        assert_that(calling(self.add_line).with_args(
            endpoint_sip_uuid=sip.uuid, endpoint_sccp_id=sccp.id,
        ), raises(IntegrityError))


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


class TestCallerID(DAOTestCase):

    @staticmethod
    def _caller_id_name(id):
        return 'Test' + str(id + 1)

    @staticmethod
    def _caller_id_num(id):
        return str(1000 + id)

    def _run_query_test(self, lines, count, filter):
        for i in range(0, count):
            id = random.randint(0, count - 1)
            result = (self.session.query(LineFeatures)
                      .filter(filter(id))
                      .first())
            assert_that(result, equal_to(lines[id]))

    def test_caller_id_sql_expression(self):
        tests_count = 10
        half = tests_count >> 1
        tenant = self.add_tenant()
        context = self.add_context(tenant_uuid=tenant.uuid)
        line = []

        sip = [
            self.add_endpoint_sip(caller_id='"{}" <{}>'.format(self._caller_id_name(i), self._caller_id_num(i)))
            for i in range(0, half)
        ]

        sccp = [
            self.add_sccpline(cid_name=self._caller_id_name(i), cid_num=self._caller_id_num(i))
            for i in range(half, tests_count)
        ]

        [line.append(self.add_line(context=context.name, endpoint_sip_uuid=sip_.uuid)) for sip_ in sip]
        [line.append(self.add_line(context=context.name, endpoint_sccp_id=sccp_.id)) for sccp_ in sccp]

        self._run_query_test(line, tests_count, lambda id: LineFeatures.caller_id_name == self._caller_id_name(id))
        self._run_query_test(line, tests_count, lambda id: LineFeatures.caller_id_num == self._caller_id_num(id))
        self._run_query_test(line, tests_count, lambda id: and_(
            LineFeatures.caller_id_name == self._caller_id_name(id),
            LineFeatures.caller_id_num == self._caller_id_num(id)
        ))
