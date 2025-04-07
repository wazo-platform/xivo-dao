# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains_exactly,
    empty,
    equal_to,
    has_items,
    has_properties,
    has_property,
    is_not,
    none,
)

from xivo_dao.alchemy.context import Context
from xivo_dao.alchemy.contextmember import ContextMember
from xivo_dao.alchemy.contextnumbers import ContextNumbers
from xivo_dao.helpers.exception import InputError, NotFoundError
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao as context_dao


class TestFind(DAOTestCase):
    def test_find_no_context(self):
        result = context_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        context_row = self.add_context()

        context = context_dao.find(context_row.id)

        assert_that(context, equal_to(context_row))


class TestGet(DAOTestCase):
    def test_get_no_context(self):
        self.assertRaises(NotFoundError, context_dao.get, 42)

    def test_get(self):
        context_row = self.add_context()

        context = context_dao.get(context_row.id)

        assert_that(context, equal_to(context_row))


class TestGetByName(DAOTestCase):
    def test_get_by_name_no_context(self):
        self.assertRaises(NotFoundError, context_dao.get_by_name, '42')

    def test_get_by_name(self):
        context_row = self.add_context()

        context = context_dao.get_by_name(context_row.name)

        assert_that(context, equal_to(context_row))

    def test_get_by_name_multi_tenant(self):
        tenant = self.add_tenant()

        context_row = self.add_context(name='MyName1')
        self.assertRaises(
            NotFoundError,
            context_dao.get_by_name,
            'MyName1',
            tenant_uuids=[tenant.uuid],
        )

        context_row = self.add_context(name='MyName2', tenant_uuid=tenant.uuid)
        context = context_dao.get_by_name('MyName2', tenant_uuids=[tenant.uuid])
        assert_that(context, equal_to(context_row))


class TestFindBy(DAOTestCase):
    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, context_dao.find_by, invalid=42)

    def test_find_by_description(self):
        context_row = self.add_context(description='mydescription')

        context = context_dao.find_by(description='mydescription')

        assert_that(context, equal_to(context_row))
        assert_that(context.description, equal_to('mydescription'))

    def test_find_by_name(self):
        context_row = self.add_context(name='myname')

        context = context_dao.find_by(name='myname')

        assert_that(context, equal_to(context_row))
        assert_that(context.name, equal_to('myname'))

    def test_find_by_type(self):
        context_row = self.add_context(type='outcall')

        context = context_dao.find_by(type='outcall')

        assert_that(context, equal_to(context_row))
        assert_that(context.type, equal_to('outcall'))

    def test_given_context_does_not_exist_then_returns_null(self):
        context = context_dao.find_by(id=42)

        assert_that(context, none())


class TestGetBy(DAOTestCase):
    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, context_dao.get_by, invalid=42)

    def test_get_by_tenant_uuid(self):
        tenant = self.add_tenant(uuid='a92c8cdb-8146-4415-91d7-fb9a941b6fd8')

        context_row = self.add_context(tenant_uuid=tenant.uuid)

        context = context_dao.get_by(tenant_uuid=tenant.uuid)

        assert_that(context, equal_to(context_row))
        assert_that(context.tenant_uuid, equal_to(tenant.uuid))

    def test_get_by_description(self):
        context_row = self.add_context(description='mydescription')

        context = context_dao.get_by(description='mydescription')

        assert_that(context, equal_to(context_row))
        assert_that(context.description, equal_to('mydescription'))

    def test_get_by_name(self):
        context_row = self.add_context(name='myname')

        context = context_dao.get_by(name='myname')

        assert_that(context, equal_to(context_row))
        assert_that(context.name, equal_to('myname'))

    def test_find_by_type(self):
        context_row = self.add_context(type='outcall')

        context = context_dao.get_by(type='outcall')

        assert_that(context, equal_to(context_row))
        assert_that(context.type, equal_to('outcall'))

    def test_given_context_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, context_dao.get_by, id='42')


class TestFindAllBy(DAOTestCase):
    def test_find_all_by_no_context(self):
        result = context_dao.find_all_by(description='toto')

        assert_that(result, contains_exactly())

    def test_find_all_by_custom_column(self):
        pass

    def test_find_all_by_native_column(self):
        context1 = self.add_context(description='MyContext')
        context2 = self.add_context(description='MyContext')

        contexts = context_dao.find_all_by(description='MyContext')

        assert_that(
            contexts,
            has_items(has_property('id', context1.id), has_property('id', context2.id)),
        )


class TestSearch(DAOTestCase):
    def assert_search_returns_result(self, search_result, **parameters):
        result = context_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):
    def test_given_no_context_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_context_then_returns_one_result(self):
        context = self.add_context()
        expected = SearchResult(1, [context])

        self.assert_search_returns_result(expected)


class TestSearchGivenMultipleContext(TestSearch):
    def setUp(self):
        super(TestSearch, self).setUp()
        self.context1 = self.add_context(name='O1', type='Ashton', description='resto')
        self.context2 = self.add_context(
            name='O2', type='Beaugarton', description='bar'
        )
        self.context3 = self.add_context(name='O3', type='Casa', description='resto')
        self.context4 = self.add_context(name='O4', type='Dunkin', description='resto')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.context2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_searching_with_an_extra_argument(self):
        expected_resto = SearchResult(1, [self.context1])
        self.assert_search_returns_result(
            expected_resto, search='ton', description='resto'
        )

        expected_bar = SearchResult(1, [self.context2])
        self.assert_search_returns_result(expected_bar, search='ton', description='bar')

        expected_all_resto = SearchResult(
            3, [self.context1, self.context3, self.context4]
        )
        self.assert_search_returns_result(
            expected_all_resto, description='resto', order='type'
        )

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(
            4, [self.context1, self.context2, self.context3, self.context4]
        )

        self.assert_search_returns_result(expected, order='type')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(
        self,
    ):
        expected = SearchResult(
            4, [self.context4, self.context3, self.context2, self.context1]
        )

        self.assert_search_returns_result(expected, order='type', direction='desc')

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.context1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_offset_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.context2, self.context3, self.context4])

        self.assert_search_returns_result(expected, offset=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.context2])

        self.assert_search_returns_result(
            expected, search='a', order='type', direction='desc', offset=1, limit=1
        )


class TestCreate(DAOTestCase):
    def test_create_minimal_fields(self):
        tenant = self.add_tenant()
        context = Context(name='mycontext', tenant_uuid=tenant.uuid)
        created_context = context_dao.create(context)

        row = self.session.query(Context).first()

        assert_that(created_context, equal_to(row))
        assert_that(
            created_context,
            has_properties(
                id=is_not(none()),
                name='mycontext',
                tenant_uuid=tenant.uuid,
                displayname=none(),
                label=none(),
                contexttype='internal',
                type='internal',
                description=none(),
                commented=0,
                enabled=True,
                user_ranges=empty(),
                group_ranges=empty(),
                queue_ranges=empty(),
                conference_room_ranges=empty(),
                incall_ranges=empty(),
            ),
        )

    def test_create_with_all_fields(self):
        tenant = self.add_tenant()
        context = Context(
            name='myContext',
            tenant_uuid=tenant.uuid,
            label='My Context Label',
            type='outcall',
            user_ranges=[ContextNumbers(start='1000', end='1999')],
            group_ranges=[ContextNumbers(start='2000', end='2999')],
            queue_ranges=[ContextNumbers(start='3000', end='3999')],
            conference_room_ranges=[ContextNumbers(start='4000', end='4999')],
            incall_ranges=[ContextNumbers(start='1000', end='4999', did_length='2')],
            description='context description',
            enabled=False,
        )

        created_context = context_dao.create(context)

        row = self.session.query(Context).first()

        assert_that(created_context, equal_to(row))
        assert_that(
            created_context,
            has_properties(
                id=is_not(none()),
                tenant_uuid=tenant.uuid,
                name='myContext',
                label='My Context Label',
                type='outcall',
                user_ranges=contains_exactly(has_properties(start='1000', end='1999')),
                group_ranges=contains_exactly(has_properties(start='2000', end='2999')),
                queue_ranges=contains_exactly(has_properties(start='3000', end='3999')),
                conference_room_ranges=contains_exactly(
                    has_properties(start='4000', end='4999')
                ),
                incall_ranges=contains_exactly(
                    has_properties(start='1000', end='4999', did_length='2')
                ),
                description='context description',
                enabled=False,
            ),
        )


class TestEdit(DAOTestCase):
    def test_edit_all_fields(self):
        tenant = self.add_tenant()
        context = context_dao.create(
            Context(
                name='MyContext',
                tenant_uuid=tenant.uuid,
                label='My Context Label',
                type='outcall',
                user_ranges=[ContextNumbers(start='1000', end='1999')],
                group_ranges=[ContextNumbers(start='2000', end='2999')],
                queue_ranges=[ContextNumbers(start='3000', end='3999')],
                conference_room_ranges=[ContextNumbers(start='4000', end='4999')],
                incall_ranges=[
                    ContextNumbers(start='1000', end='4999', did_length='2')
                ],
                description='context description',
                enabled=False,
            )
        )

        context = context_dao.get(context.id)
        context.label = 'Other Context Label'
        context.type = 'incall'
        context.user_ranges = [ContextNumbers(start='4000', end='4999')]
        context.group_ranges = [ContextNumbers(start='3000', end='3999')]
        context.queue_ranges = [ContextNumbers(start='2000', end='2999')]
        context.conference_room_ranges = [ContextNumbers(start='1000', end='1999')]
        context.incall_ranges = [
            ContextNumbers(start='4000', end='6999', did_length='4')
        ]
        context.description = 'other context description'
        context.enabled = True
        context_dao.edit(context)

        row = self.session.query(Context).first()

        assert_that(context, equal_to(row))
        assert_that(
            context,
            has_properties(
                id=is_not(none()),
                tenant_uuid=tenant.uuid,
                label='Other Context Label',
                type='incall',
                user_ranges=contains_exactly(has_properties(start='4000', end='4999')),
                group_ranges=contains_exactly(has_properties(start='3000', end='3999')),
                queue_ranges=contains_exactly(has_properties(start='2000', end='2999')),
                conference_room_ranges=contains_exactly(
                    has_properties(start='1000', end='1999')
                ),
                incall_ranges=contains_exactly(
                    has_properties(start='4000', end='6999', did_length='4')
                ),
                description='other context description',
                enabled=True,
            ),
        )

    def test_edit_set_fields_to_null(self):
        tenant = self.add_tenant()
        context = context_dao.create(
            Context(
                name='MyContext',
                tenant_uuid=tenant.uuid,
                label='My Context Label',
                user_ranges=[ContextNumbers(start='1000', end='1999')],
                group_ranges=[ContextNumbers(start='2000', end='2999')],
                queue_ranges=[ContextNumbers(start='3000', end='3999')],
                conference_room_ranges=[ContextNumbers(start='4000', end='4999')],
                incall_ranges=[ContextNumbers(start='1000', end='4999')],
                description='context description',
            )
        )

        context = context_dao.get(context.id)
        context.label = None
        context.user_ranges = []
        context.group_ranges = []
        context.queue_ranges = []
        context.conference_room_ranges = []
        context.incall_ranges = []
        context.description = None

        context_dao.edit(context)

        row = self.session.query(Context).first()
        assert_that(context, equal_to(row))
        assert_that(
            row,
            has_properties(
                label=none(),
                user_ranges=empty(),
                group_ranges=empty(),
                queue_ranges=empty(),
                conference_room_ranges=empty(),
                incall_ranges=empty(),
                description=none(),
            ),
        )


class TestDelete(DAOTestCase):
    def test_delete(self):
        context = self.add_context()

        context_dao.delete(context)

        row = self.session.query(Context).first()
        assert_that(row, none())

    def test_when_deleting_then_context_numbers_are_deleted(self):
        context = self.add_context()
        self.add_context_number(context=context.name)

        context_dao.delete(context)

        context = self.session.query(Context).first()
        assert_that(context, none())

        context_numbers = self.session.query(ContextNumbers).first()
        assert_that(context_numbers, none())

    def test_when_deleting_then_context_member_are_deleted(self):
        context = self.add_context()
        self.add_context_member(context=context.name)

        context_dao.delete(context)

        context = self.session.query(Context).first()
        assert_that(context, none())

        context_member = self.session.query(ContextMember).first()
        assert_that(context_member, none())


class TestAssociateContexts(DAOTestCase):
    def test_associate(self):
        context = self.add_context()
        included_context = self.add_context()

        context_dao.associate_contexts(context, [included_context])

        self.session.expire_all()
        assert_that(context.contexts, contains_exactly(included_context))

    def test_associate_multiple(self):
        context = self.add_context()
        included_context1 = self.add_context()
        included_context2 = self.add_context()

        context_dao.associate_contexts(context, [included_context1, included_context2])

        self.session.expire_all()
        assert_that(
            context.contexts, contains_exactly(included_context1, included_context2)
        )

    def test_dissociate(self):
        context = self.add_context()
        included_context = self.add_context()
        context_dao.associate_contexts(context, [included_context])

        context_dao.associate_contexts(context, [])

        self.session.expire_all()
        assert_that(context.contexts, empty())
