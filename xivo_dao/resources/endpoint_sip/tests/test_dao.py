# -*- coding: utf-8 -*-
# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

import uuid

from hamcrest import (
    all_of,
    assert_that,
    contains,
    empty,
    equal_to,
    has_items,
    has_length,
    has_properties,
    none,
    not_,
    not_none,
)
from sqlalchemy.inspection import inspect
from xivo_dao.alchemy.endpoint_sip import EndpointSIP
from xivo_dao.alchemy.endpoint_sip_section_option import EndpointSIPSectionOption
from xivo_dao.alchemy.endpoint_sip_section import EndpointSIPSection
from xivo_dao.helpers.exception import InputError
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao as sip_dao

UNKNOWN_UUID = uuid.uuid4()

OPTION_SAMPLE = {
    'aor': [
        ['max_contacts', '10'],
        ['remove_existing', 'yes'],
        ['qualify_timeout', '60'],
    ],
    'auth': [
        ['username', 'foobar'],
        ['md5_cred', 'dd02c7c2232759874e1c205587017bed'],
        ['nonce_lifetime', '64'],
    ],
    'endpoint': [
        ['webrtc', 'yes'],
        ['set_var', 'var1=foo'],
        ['set_var', 'var2=bar'],
    ],
    'registration': [
        ['server_uri', 'sip:sip.example.com'],
        ['client_uri', 'sip:1234567890@sip.example.com'],
        ['forbidden_retry_interval', '600'],
    ],
    'registration_outbound_auth': [
        ['username', 'foobar'],
        ['md5_cred', 'dd02c7c2232759874e1c205587017bed'],
        ['nonce_lifetime', '64'],
    ],
    'outbound_auth': [
        ['username', 'foobaz'],
        ['md5_cred', 'dd02c7c2232759874e1c205587017bed'],
        ['nonce_lifetime', '64'],
    ],
    'identify': [
        ['match', '54.172.60.0'],
        ['match', '54.172.60.1'],
        ['match', '54.172.60.2'],
    ],
}


class TestFindBy(DAOTestCase):

    def test_given_column_does_not_exist_then_raises_error(self):
        self.assertRaises(InputError, sip_dao.find_by, column=1)

    def test_given_row_with_value_does_not_exist_then_returns_null(self):
        result = sip_dao.find_by(name='abcd')
        assert_that(result, none())

    def test_find_by(self):
        sip = self.add_endpoint_sip(name='myname')
        result = sip_dao.find_by(name='myname')

        assert_that(result.uuid, equal_to(sip.uuid))

    def test_find_by_multi_tenant(self):
        tenant = self.add_tenant()

        sip_row = self.add_endpoint_sip()
        sip = sip_dao.find_by(name=sip_row.name, tenant_uuids=[tenant.uuid])
        assert_that(sip, none())

        sip_row = self.add_endpoint_sip(tenant_uuid=tenant.uuid)
        sip = sip_dao.find_by(name=sip_row.name, tenant_uuids=[tenant.uuid])
        assert_that(sip, equal_to(sip_row))

    def test_find_by_username(self):
        sip_row = self.add_endpoint_sip(auth_section_options=[['username', 'foobar']])
        sip = sip_dao.find_by(username='foobar')

        assert_that(sip.uuid, equal_to(sip_row.uuid))


class TestFindAllBy(DAOTestCase):

    def test_find_all_multi_tenant(self):
        tenant = self.add_tenant()

        sip1 = self.add_endpoint_sip(display_name='my-endpoint', tenant_uuid=tenant.uuid)
        sip2 = self.add_endpoint_sip(display_name='my-endpoint')

        tenants = [tenant.uuid, self.default_tenant.uuid]
        sips = sip_dao.find_all_by(display_name='my-endpoint', tenant_uuids=tenants)
        assert_that(sips, has_items(sip1, sip2))

        tenants = [tenant.uuid]
        sips = sip_dao.find_all_by(display_name='my-endpoint', tenant_uuids=tenants)
        assert_that(sips, all_of(has_items(sip1), not_(has_items(sip2))))


class TestGet(DAOTestCase):

    def test_given_no_rows_then_raises_error(self):
        self.assertRaises(NotFoundError, sip_dao.get, UNKNOWN_UUID)
        self.assertRaises(NotFoundError, sip_dao.get, str(UNKNOWN_UUID))

    def test_given_row_with_minimal_parameters_then_returns_model(self):
        row = self.add_endpoint_sip()

        sip = sip_dao.get(row.uuid)
        assert_that(isinstance(row.uuid, uuid.UUID), equal_to(True))
        assert_that(sip, has_properties(uuid=row.uuid))

        sip = sip_dao.get(str(row.uuid))
        assert_that(sip, has_properties(uuid=row.uuid))

    def test_given_row_with_all_parameters_then_returns_model(self):
        transport = self.add_transport()
        context = self.add_context()
        parent_1 = self.add_endpoint_sip()
        parent_2 = self.add_endpoint_sip()

        row = self.add_endpoint_sip(
            display_name='general_config',
            aor_section_options=[['type', 'aor']],
            auth_section_options=[['type', 'auth']],
            endpoint_section_options=[['type', 'endpoint']],
            registration_section_options=[['type', 'registration']],
            registration_outbound_auth_section_options=[['type', 'auth']],
            identify_section_options=[['type', 'identify']],
            outbound_auth_section_options=[['type', 'auth']],
            transport={'uuid': transport.uuid},
            context={'id': context.id},
            parents=[parent_1, parent_2],
            tenant_uuid=self.default_tenant.uuid,
            template=True,
        )

        sip = sip_dao.get(row.uuid)
        assert_that(sip, has_properties(
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
            context=has_properties(id=context.id),
            parents=contains(
                has_properties(uuid=parent_1.uuid),
                has_properties(uuid=parent_2.uuid),
            ),
        ))

    def test_get_multi_tenant(self):
        tenant = self.add_tenant()

        sip_row = self.add_endpoint_sip(tenant_uuid=tenant.uuid)
        sip = sip_dao.get(sip_row.uuid, tenant_uuids=[tenant.uuid])
        assert_that(sip, equal_to(sip_row))

        sip_row = self.add_endpoint_sip()
        self.assertRaises(
            NotFoundError,
            sip_dao.get, sip_row.uuid, tenant_uuids=[tenant.uuid],
        )


class TestSearch(DAOTestCase):

    def assert_search_returns_result(self, search_result, **parameters):
        result = sip_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):

    def test_given_no_sip_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_on_sip_then_returns_one_result(self):
        sip = self.add_endpoint_sip()
        expected = SearchResult(1, [sip])

        self.assert_search_returns_result(expected)

    def test_search_multi_tenant(self):
        tenant = self.add_tenant()

        sip1 = self.add_endpoint_sip(display_name='sort1')
        sip2 = self.add_endpoint_sip(display_name='sort2', tenant_uuid=tenant.uuid)

        expected = SearchResult(2, [sip1, sip2])
        tenants = [tenant.uuid, self.default_tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)

        expected = SearchResult(1, [sip2])
        tenants = [tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)


class TestSearchMultiple(TestSearch):

    def setUp(self):
        super(TestSearch, self).setUp()
        self.sip1 = self.add_endpoint_sip(display_name='Ashton', asterisk_id='y')
        self.sip2 = self.add_endpoint_sip(display_name='Beaugarton', asterisk_id='x')
        self.sip3 = self.add_endpoint_sip(display_name='Casa', asterisk_id='y')
        self.sip4 = self.add_endpoint_sip(display_name='Dunkin', asterisk_id='y')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.sip2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_searching_with_an_extra_argument(self):
        expected_y = SearchResult(1, [self.sip1])
        self.assert_search_returns_result(expected_y, search='ton', asterisk_id='y')

        expected_x = SearchResult(1, [self.sip2])
        self.assert_search_returns_result(expected_x, search='ton', asterisk_id='x')

        expected_all_y = SearchResult(3, [self.sip1, self.sip3, self.sip4])
        self.assert_search_returns_result(expected_all_y, asterisk_id='y', order='display_name')

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(
            4, [self.sip1, self.sip2, self.sip3, self.sip4]
        )

        self.assert_search_returns_result(expected, order='display_name')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(self):
        expected = SearchResult(
            4, [self.sip4, self.sip3, self.sip2, self.sip1]
        )

        self.assert_search_returns_result(expected, order='display_name', direction='desc')

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.sip1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_offset_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.sip2, self.sip3, self.sip4])

        self.assert_search_returns_result(expected, offset=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(2, [self.sip1])

        self.assert_search_returns_result(
            expected,
            search='on',
            order='display_name',
            direction='desc',
            offset=1,
            limit=1,
        )


class TestCreate(DAOTestCase):

    def test_create_minimal_parameters(self):
        model = EndpointSIP(tenant_uuid=self.default_tenant.uuid)

        result = sip_dao.create(model)

        assert_that(inspect(result).persistent)
        assert_that(result, has_properties(
            uuid=not_none(),
            name=has_length(8),
            display_name=none(),
            asterisk_id=none(),
            tenant_uuid=self.default_tenant.uuid,
            aor_section_uuid=none(),
            aor_section_options=empty(),
            auth_section_uuid=none(),
            auth_section_options=empty(),
            endpoint_section_uuid=none(),
            endpoint_section_options=empty(),
            identify_section_uuid=none(),
            identify_section_options=empty(),
            registration_section_uuid=none(),
            registration_section_options=empty(),
            registration_outbound_auth_section_uuid=none(),
            registration_outbound_auth_section_options=empty(),
            outbound_auth_section_uuid=none(),
            outbound_auth_section_options=empty(),
            transport_uuid=none(),
            context_id=none(),
            template=False,
        ))

    def test_create_all_parameters(self):
        transport = self.add_transport()
        context = self.add_context()
        parents = [
            self.add_endpoint_sip(),
            self.add_endpoint_sip(),
        ]
        almost_all_options = {
            '{}_section_options'.format(name): options
            for (name, options) in OPTION_SAMPLE.items()
        }

        model = EndpointSIP(
            tenant_uuid=self.default_tenant.uuid,
            display_name='display_name',
            name='name',
            asterisk_id='asterisk-id',
            transport={'uuid': transport.uuid},
            context={'id': context.id},
            template=True,
            parents=parents,
            **almost_all_options
        )

        result = sip_dao.create(model)

        assert_that(inspect(result).persistent)
        assert_that(result, has_properties(
            uuid=not_none(),
            name='name',
            display_name='display_name',
            asterisk_id='asterisk-id',
            tenant_uuid=self.default_tenant.uuid,
            transport_uuid=transport.uuid,
            context_id=context.id,
            template=True,
            parents=parents,
            **almost_all_options
        ))


class TestEdit(DAOTestCase):

    def setUp(self):
        super(TestEdit, self).setUp()
        self.section_options = OPTION_SAMPLE

    def test_edit_add_the_first_option(self):
        def _test(name, options):
            sip = self.add_endpoint_sip()
            self.session.expire_all()

            field = '{}_section_options'.format(name)

            setattr(sip, field, [options[0]])

            sip_dao.edit(sip)

            assert_that(sip, has_properties({
                field: contains(contains(*options[0])),
            }), name)

        for name, options in self.section_options.items():
            _test(name, options)

    def test_edit_remove_all_options(self):
        def _test(name, options):
            field = '{}_section_options'.format(name)
            sip = self.add_endpoint_sip(**{field: [options[0]]})

            setattr(sip, field, [])

            sip_dao.edit(sip)

            assert_that(sip, has_properties({field: empty()}), name)

            option_count = self.session.query(EndpointSIPSectionOption).count()
            assert_that(option_count, equal_to(0), 'An unassociated option has been leaked')

            section_count = self.session.query(EndpointSIPSection).count()
            assert_that(section_count, equal_to(0), 'An empty section has been leaked')

        for name, options in self.section_options.items():
            _test(name, options)

    def test_edit_remove_one_options(self):
        def _test(name, options):
            field = '{}_section_options'.format(name)
            sip = self.add_endpoint_sip(**{field: options})

            self.session.expire_all()
            new_value = [options[0], options[2]]
            setattr(sip, field, new_value)

            sip_dao.edit(sip)

            assert_that(sip, has_properties({field: contains(*new_value)}), name)

        for name, options in self.section_options.items():
            _test(name, options)

        option_count = self.session.query(EndpointSIPSectionOption).count()
        assert_that(
            option_count,
            equal_to(len(self.section_options) * 2),  # option 0 and 2 for each section
            'An unassociated option has been leaked',
        )


class TestDelete(DAOTestCase):

    def test_delete(self):
        sip = self.add_endpoint_sip()

        sip_dao.delete(sip)

        assert_that(inspect(sip).deleted)

    def test_given_endpoint_is_associated_to_line_then_line_is_dissociated(self):
        sip = self.add_endpoint_sip()
        line = self.add_line(endpoint_sip_uuid=sip.uuid)

        sip_dao.delete(sip)

        assert_that(line.endpoint_sip_uuid, none())


class TestRelations(DAOTestCase):

    def test_trunk_relationship(self):
        sip = self.add_endpoint_sip()
        trunk = self.add_trunk()

        trunk.associate_endpoint(sip)
        self.session.flush()

        self.session.expire_all()
        assert_that(sip.trunk, equal_to(trunk))

    def test_line_relationship(self):
        sip = self.add_endpoint_sip()
        line = self.add_line()

        line.associate_endpoint(sip)
        self.session.flush()

        self.session.expire_all()
        assert_that(sip.line, equal_to(line))
