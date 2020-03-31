# -*- coding: utf-8 -*-
# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, contains, has_length, has_properties
from xivo_dao.tests.test_dao import DAOTestCase

from ..endpoint_sip import EndpointSIP


class TestEndpointSIP(DAOTestCase):
    def test_create_with_all_relations(self):
        transport = self.add_transport()
        parent_1 = self.add_endpoint_sip()
        parent_2 = self.add_endpoint_sip()

        endpoint = EndpointSIP(
            display_name='general_config',
            aor_section_options=[['type', 'aor']],
            auth_section_options=[['type', 'auth']],
            endpoint_section_options=[['type', 'endpoint']],
            registration_section_options=[['type', 'registration']],
            registration_outbound_auth_section_options=[['type', 'auth']],
            identify_section_options=[['type', 'identify']],
            outbound_auth_section_options=[['type', 'auth']],
            transport=transport,
            parents=[parent_1, parent_2],
            tenant_uuid=self.default_tenant.uuid,
            template=True,
        )
        self.session.add(endpoint)
        self.session.flush()
        self.session.expunge_all()

        row = self.session.query(EndpointSIP).filter_by(uuid=endpoint.uuid).first()
        assert_that(row, has_properties(
            display_name='general_config',
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
            parents=contains(
                has_properties(uuid=parent_1.uuid),
                has_properties(uuid=parent_2.uuid),
            ),
        ))

    def test_create_concrete_endpoint(self):
        transport = self.add_transport()
        parent = self.add_endpoint_sip(
            display_name="my tenant's global config",
            template=True,
            transport_uuid=transport.uuid,
        )
        self.session.flush()

        endpoint = EndpointSIP(
            display_name='my-line',
            parents=[parent],
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
            display_name='my-line',
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
            parents=contains(
                has_properties(uuid=parent.uuid),
            )
        ))
