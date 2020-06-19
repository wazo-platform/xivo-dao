# -*- coding: utf-8 -*-
# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains,
    contains_inanyorder,
    has_items,
    has_properties,
    empty,
    equal_to,
    none,
    not_none,
)
from sqlalchemy.inspection import inspect
from xivo_dao.alchemy.pjsip_transport import PJSIPTransport
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.helpers.exception import NotFoundError, InputError
from .. import dao

UNKNOWN_UUID = '0965ea59-567a-4477-a004-77b5c2d9aa2c'


class TestFind(DAOTestCase):

    def test_find_no_transport(self):
        result = dao.find(UNKNOWN_UUID)
        assert_that(result, none())

    def test_find(self):
        transport_row = self.add_transport()

        transport = dao.find(transport_row.uuid)

        assert_that(transport, equal_to(transport_row))


class TestGet(DAOTestCase):

    def test_get_no_transport(self):
        self.assertRaises(NotFoundError, dao.get, UNKNOWN_UUID)

    def test_get(self):
        transport_row = self.add_transport()

        transport = dao.get(transport_row.uuid)

        assert_that(transport, equal_to(transport_row))


class TestFindBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, dao.find_by, invalid=42)

    def test_find_by_number(self):
        name = 'my-transport'

        transport_row = self.add_transport(name=name)

        transport = dao.find_by(name=name)

        assert_that(transport, equal_to(transport_row))
        assert_that(transport.name, equal_to(name))

    def test_given_transport_does_not_exist_then_returns_null(self):
        transport = dao.find_by(name='not-here')

        assert_that(transport, none())


class TestGetBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, dao.get_by, invalid=42)

    def test_get_by_name(self):
        name = 'the-transport'

        transport_row = self.add_transport(name=name)

        transport = dao.get_by(name=name)

        assert_that(transport, equal_to(transport_row))
        assert_that(transport.name, equal_to(name))

    def test_given_transport_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, dao.get_by, name='not-here')


class TestFindAllBy(DAOTestCase):

    def test_find_all_by_no_transports(self):
        result = dao.find_all_by(name='not-here')

        assert_that(result, contains())

    def test_find_all_by_native_column(self):
        transport = self.add_transport(name='the-transport')

        transports = dao.find_all_by(name='the-transport')

        assert_that(transports, has_items(
            has_properties(uuid=transport.uuid),
        ))


class TestSearch(DAOTestCase):

    def assert_search_returns_result(self, search_result, **parameters):
        result = dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):

    def test_given_no_transports_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_transport_then_returns_one_result(self):
        transport = self.add_transport()
        expected = SearchResult(1, [transport])

        self.assert_search_returns_result(expected)


class TestSearchGivenMultipleTransports(TestSearch):

    def setUp(self):
        super(TestSearch, self).setUp()
        self.transport1 = self.add_transport(name='Ashton')
        self.transport2 = self.add_transport(name='Beaugarton')
        self.transport3 = self.add_transport(name='Casa')
        self.transport4 = self.add_transport(name='Dunkin')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.transport2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_searching_with_an_extra_argument(self):
        expected_resto = SearchResult(1, [self.transport1])
        self.assert_search_returns_result(expected_resto, search='ton', uuid=self.transport1.uuid)

        expected_bar = SearchResult(1, [self.transport2])
        self.assert_search_returns_result(expected_bar, search='ton', uuid=self.transport2.uuid)

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(4, [
            self.transport1,
            self.transport2,
            self.transport3,
            self.transport4,
        ])

        self.assert_search_returns_result(expected, order='name')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(self):
        expected = SearchResult(4, [
            self.transport4,
            self.transport3,
            self.transport2,
            self.transport1,
        ])

        self.assert_search_returns_result(expected, order='name', direction='desc')

    def test_when_limiting_then_returns_right_name_of_items(self):
        expected = SearchResult(4, [self.transport1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_offset_then_returns_right_name_of_items(self):
        expected = SearchResult(4, [self.transport2, self.transport3, self.transport4])

        self.assert_search_returns_result(expected, offset=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.transport2])

        self.assert_search_returns_result(
            expected,
            search='a',
            order='name',
            direction='desc',
            offset=1,
            limit=1,
        )


class TestCreate(DAOTestCase):

    def test_create_minimal_fields(self):
        transport_model = PJSIPTransport(name='transport')
        transport = dao.create(transport_model)

        self.session.expire_all()
        assert_that(inspect(transport).persistent)
        assert_that(transport, has_properties(
            uuid=not_none(),
            name='transport',
            options=[],
        ))

    def test_create_with_all_fields(self):
        transport_model = PJSIPTransport(
            name='transport',
            options=[
                ['bind', '0.0.0.0'],
                ['protocol', 'wss'],
            ],
        )
        transport = dao.create(transport_model)

        self.session.expire_all()
        assert_that(inspect(transport).persistent)
        assert_that(transport, has_properties(
            name='transport',
            options=contains_inanyorder(
                contains('bind', '0.0.0.0'),
                contains('protocol', 'wss'),
            ),
        ))


class TestEdit(DAOTestCase):

    def test_edit_all_fields(self):
        transport = self.add_transport(
            name='transport',
            options=[
                ['bind', '0.0.0.0'],
                ['protocol', 'wss'],
                ['symmetric_transport', 'yes'],
                ['local_net', '192.168.0.0/16'],
            ],
        )

        self.session.expire_all()
        transport.name = 'other_transport'
        transport.options = [
            ['bind', '0.0.0.0'],
            ['protocol', 'udp'],
            ['cos', '1'],
            ['local_net', '192.168.0.0/16'],
            ['local_net', '10.1.42.0/24'],
        ]

        dao.edit(transport)

        self.session.expire_all()
        assert_that(transport, has_properties(
            name='other_transport',
            options=contains_inanyorder(
                contains('bind', '0.0.0.0'),
                contains('protocol', 'udp'),
                contains('cos', '1'),
                contains('local_net', '192.168.0.0/16'),
                contains('local_net', '10.1.42.0/24'),
            ),
        ))

    def test_edit_set_fields_to_empty(self):
        transport = self.add_transport(
            name='transport',
            options=[
                ['bind', '0.0.0.0'],
                ['protocol', 'wss'],
                ['symmetric_transport', 'yes'],
            ],
        )

        self.session.expire_all()
        transport.options = []

        dao.edit(transport)

        self.session.expire_all()
        assert_that(transport, has_properties(
            options=empty(),
        ))


class TestDelete(DAOTestCase):

    def test_delete(self):
        transport = self.add_transport()

        dao.delete(transport)

        assert_that(inspect(transport).deleted)

    def test_delete_with_fallback(self):
        fallback = self.add_transport()
        transport_1 = self.add_transport()
        transport_2 = self.add_transport()
        sip_1 = self.add_endpoint_sip(transport_uuid=transport_1.uuid)
        sip_2 = self.add_endpoint_sip(transport_uuid=transport_2.uuid)
        sip_3 = self.add_endpoint_sip(transport_uuid=fallback.uuid)

        dao.delete(transport_1, fallback)

        assert_that(inspect(transport_1).deleted)
        assert_that(sip_1.transport_uuid, equal_to(fallback.uuid))
        assert_that(sip_2.transport_uuid, equal_to(transport_2.uuid))
        assert_that(sip_3.transport_uuid, equal_to(fallback.uuid))
