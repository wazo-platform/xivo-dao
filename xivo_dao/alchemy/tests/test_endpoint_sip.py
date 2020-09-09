# -*- coding: utf-8 -*-
# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains,
    contains_inanyorder,
    empty,
    equal_to,
    has_properties,
    none,
)
from xivo_dao.tests.test_dao import DAOTestCase

from ..endpoint_sip import EndpointSIP, EndpointSIPTemplate
from ..endpoint_sip_section import EndpointSIPSection


class TestEndpointSIP(DAOTestCase):
    def test_create_with_all_relations(self):
        transport = self.add_transport()
        template_1 = self.add_endpoint_sip(template=True)
        template_2 = self.add_endpoint_sip(template=True)

        endpoint = EndpointSIP(
            label='general_config',
            name='general_config',
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
            name='general_config',
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
            name='general_config',
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
            name='general_config',
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


class TestTemplates(DAOTestCase):
    def test_order_by(self):
        sip = self.add_endpoint_sip()
        template_1 = self.add_endpoint_sip(template=True)
        template_2 = self.add_endpoint_sip(template=True)
        template_3 = self.add_endpoint_sip(template=True)

        sip.templates = [template_2, template_3, template_1]
        self.session.flush()

        self.session.expire_all()
        assert_that(sip.templates, contains(
            template_2,
            template_3,
            template_1,
        ))
        templates = self.session.query(EndpointSIPTemplate).all()
        assert_that(templates, contains_inanyorder(
            has_properties(parent_uuid=template_2.uuid, priority=0),
            has_properties(parent_uuid=template_3.uuid, priority=1),
            has_properties(parent_uuid=template_1.uuid, priority=2),
        ))

    def test_reorder_on_delete(self):
        template_1 = self.add_endpoint_sip(template=True)
        template_2 = self.add_endpoint_sip(template=True)
        template_3 = self.add_endpoint_sip(template=True)
        sip = self.add_endpoint_sip(templates=[template_1, template_2, template_3])

        sip.templates = [template_1, template_3]
        self.session.flush()

        self.session.expire_all()
        templates = self.session.query(EndpointSIPTemplate).all()
        assert_that(templates, contains_inanyorder(
            has_properties(parent_uuid=template_1.uuid, priority=0),
            has_properties(parent_uuid=template_3.uuid, priority=1),
        ))

    def test_delete(self):
        template = self.add_endpoint_sip(template=True)
        sip = self.add_endpoint_sip(templates=[template])

        sip.templates = []
        self.session.flush()

        self.session.expire_all()
        templates = self.session.query(EndpointSIPTemplate).all()
        assert_that(templates, empty())


class TestWebRTC(DAOTestCase):

    def test_getter_no_endpoint_section_options(self):
        sip = self.add_endpoint_sip()

        assert_that(sip.webrtc, equal_to(False))

    def test_getter_no_options(self):
        sip = self.add_endpoint_sip(endpoint_section_options=[])

        assert_that(sip.webrtc, equal_to(False))

    def test_getter_false(self):
        sip = self.add_endpoint_sip(endpoint_section_options=[['webrtc', 'no']])

        assert_that(sip.webrtc, equal_to(False))

    def test_getter_true(self):
        sip = self.add_endpoint_sip(endpoint_section_options=[['webrtc', 'yes']])

        assert_that(sip.webrtc, equal_to(True))

    def test_getter_with_templates_false(self):
        template1_1 = self.add_endpoint_sip(
            template=True,
            endpoint_section_options=[['webrtc', 'no']],
        )
        template1_2 = self.add_endpoint_sip(template=True)
        template2_1 = self.add_endpoint_sip(template=True, templates=[template1_1, template1_2])
        sip3 = self.add_endpoint_sip(templates=[template2_1])

        assert_that(sip3.webrtc, equal_to(False))

    def test_getter_with_templates_true(self):
        template1_1 = self.add_endpoint_sip(
            template=True,
            endpoint_section_options=[['webrtc', 'yes']],
        )
        template1_2 = self.add_endpoint_sip(template=True)
        template2_1 = self.add_endpoint_sip(
            template=True,
            templates=[template1_1, template1_2],
        )
        sip3 = self.add_endpoint_sip(templates=[template2_1])

        assert_that(sip3.webrtc, equal_to(True))

    def test_getter_templates_priority(self):
        template1_1 = self.add_endpoint_sip(
            template=True,
            endpoint_section_options=[['webrtc', 'yes']],
        )
        template1_2 = self.add_endpoint_sip(template=True)
        template2_1 = self.add_endpoint_sip(
            template=True,
            templates=[template1_1, template1_2],
            endpoint_section_options=[['webrtc', 'no']],
        )
        sip3 = self.add_endpoint_sip(templates=[template2_1])

        assert_that(sip3.webrtc, equal_to(False))
