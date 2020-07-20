# -*- coding: utf-8 -*-
# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains,
    empty,
    equal_to,
    has_length,
    has_properties,
    none,
)
from xivo_dao.tests.test_dao import DAOTestCase

from ..endpoint_sip import EndpointSIP
from ..endpoint_sip_section import EndpointSIPSection


class TestEndpointSIP(DAOTestCase):
    def test_create_with_all_relations(self):
        transport = self.add_transport()
        template_1 = self.add_endpoint_sip(template=True)
        template_2 = self.add_endpoint_sip(template=True)

        endpoint = EndpointSIP(
            label='general_config',
            aor_section_options=[['type', 'aor']],
            auth_section_options=[['type', 'auth']],
            endpoint_section_options=[['type', 'endpoint']],
            registration_section_options=[['type', 'registration']],
            registration_outbound_auth_section_options=[['type', 'auth']],
            identify_section_options=[['type', 'identify']],
            outbound_auth_section_options=[['type', 'auth']],
            transport=transport,
            templates=[template_1, template_2],
            tenant_uuid=self.default_tenant.uuid,
            template=True,
        )
        self.session.add(endpoint)
        self.session.flush()
        self.session.expunge_all()

        row = self.session.query(EndpointSIP).filter_by(uuid=endpoint.uuid).first()
        assert_that(row, has_properties(
            label='general_config',
            name=has_length(8),
            aor_section_options=[['type', 'aor']],
            auth_section_options=[['type', 'auth']],
            endpoint_section_options=[['type', 'endpoint']],
            registration_section_options=[['type', 'registration']],
            registration_outbound_auth_section_options=[['type', 'auth']],
            identify_section_options=[['type', 'identify']],
            outbound_auth_section_options=[['type', 'auth']],
            template=True,
            transport=has_properties(uuid=transport.uuid),
            templates=contains(
                has_properties(uuid=template_1.uuid),
                has_properties(uuid=template_2.uuid),
            ),
        ))

    def test_create_concrete_endpoint(self):
        transport = self.add_transport()
        template = self.add_endpoint_sip(
            label="my tenant's global config",
            template=True,
            transport_uuid=transport.uuid,
        )

        endpoint = EndpointSIP(
            label='my-line',
            templates=[template],
            auth_section_options=[
                ['username', 'random-username'],
                ['password', 'random-password'],
            ],
            tenant_uuid=self.default_tenant.uuid,
        )
        self.session.add(endpoint)
        self.session.flush()

        row = self.session.query(EndpointSIP).filter_by(uuid=endpoint.uuid).first()
        assert_that(row, has_properties(
            label='my-line',
            name=has_length(8),
            aor_section_options=[],
            auth_section_options=[
                ['username', 'random-username'],
                ['password', 'random-password'],
            ],
            endpoint_section_options=[],
            registration_section_options=[],
            identify_section_options=[],
            outbound_auth_section_options=[],
            template=False,
            transport_uuid=None,
            templates=contains(
                has_properties(uuid=template.uuid),
            )
        ))

    def test_auto_generated_name(self):
        self.session.add(EndpointSIP(
            name=None,
            tenant_uuid=self.default_tenant.uuid,
        ))
        self.session.add(EndpointSIP(tenant_uuid=self.default_tenant.uuid))
        self.session.flush()

        rows = self.session.query(EndpointSIP).all()
        assert_that(
            rows,
            contains(
                has_properties(name=has_length(8)),
                has_properties(name=has_length(8)),
            )
        )
    def test_username(self):
        endpoint = self.add_endpoint_sip(
            auth_section_options=[['username', 'my-username']],
        )
        assert_that(endpoint.username, equal_to('my-username'))

        endpoint = self.add_endpoint_sip()
        assert_that(endpoint.username, none())

    def test_username_expression(self):
        self.add_endpoint_sip(auth_section_options=[['username', 'my-username']])
        self.add_endpoint_sip()
        endpoint_3 = self.add_endpoint_sip(
            auth_section_options=[['username', 'other-username']],
        )

        result = (
            self.session.query(EndpointSIP.uuid)
            .filter(EndpointSIP.username == 'other-username')
            .scalar()
        )
        assert_that(result, equal_to(endpoint_3.uuid))

    def test_password(self):
        endpoint = self.add_endpoint_sip(
            auth_section_options=[['password', 'my-password']],
        )
        assert_that(endpoint.password, equal_to('my-password'))

        endpoint = self.add_endpoint_sip()
        assert_that(endpoint.password, none())

    def test_password_expression(self):
        self.add_endpoint_sip(auth_section_options=[['password', 'my-password']])
        self.add_endpoint_sip(auth_section_options=[['username', 'my-password']])
        endpoint_3 = self.add_endpoint_sip(
            auth_section_options=[['password', 'other-password']],
        )

        result = (
            self.session.query(EndpointSIP.uuid)
            .filter(EndpointSIP.password == 'other-password')
            .scalar()
        )
        assert_that(result, equal_to(endpoint_3.uuid))


class TestAORSectionOptions(DAOTestCase):
    def test_delete_all(self):
        endpoint = self.add_endpoint_sip(aor_section_options=[['type', 'aor']])

        endpoint.aor_section_options = []
        self.session.flush()

        section = self.session.query(EndpointSIPSection).first()
        assert_that(section, none())

    def test_update(self):
        endpoint = self.add_endpoint_sip(aor_section_options=[['type', 'aor']])

        endpoint.aor_section_options = [['type', 'new']]
        self.session.flush()
        self.session.expire_all()

        assert_that(endpoint.aor_section_options, equal_to([['type', 'new']]))

    def test_create(self):
        endpoint = self.add_endpoint_sip()

        endpoint.aor_section_options = [['type', 'aor']]
        self.session.flush()
        self.session.expire_all()

        assert_that(endpoint.aor_section_options, equal_to([['type', 'aor']]))

    def test_get(self):
        endpoint = self.add_endpoint_sip(aor_section_options=[['type', 'aor']])
        assert_that(endpoint.aor_section_options, equal_to([['type', 'aor']]))

    def test_get_empty(self):
        endpoint = self.add_endpoint_sip(aor_section_options=None)
        assert_that(endpoint.aor_section_options, empty())
