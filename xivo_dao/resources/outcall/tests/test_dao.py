# Copyright 2014-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    all_of,
    assert_that,
    contains,
    empty,
    equal_to,
    has_items,
    has_properties,
    has_property,
    is_not,
    none,
    not_,
)

from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.outcall import Outcall
from xivo_dao.alchemy.rightcallmember import RightCallMember
from xivo_dao.alchemy.rightcall import RightCall
from xivo_dao.alchemy.schedule import Schedule
from xivo_dao.alchemy.schedulepath import SchedulePath
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.helpers.exception import NotFoundError, InputError
from xivo_dao.resources.utils.search import SearchResult

from .. import dao as outcall_dao


class TestFind(DAOTestCase):

    def test_find_no_outcall(self):
        result = outcall_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        outcall_row = self.add_outcall()

        outcall = outcall_dao.find(outcall_row.id)

        assert_that(outcall, equal_to(outcall_row))

    def test_find_multi_tenant(self):
        tenant = self.add_tenant()
        outcall = self.add_outcall(tenant_uuid=tenant.uuid)

        result = outcall_dao.find(outcall.id, tenant_uuids=[tenant.uuid])
        assert_that(result, equal_to(outcall))

        result = outcall_dao.find(outcall.id, tenant_uuids=[self.default_tenant.uuid])
        assert_that(result, none())


class TestGet(DAOTestCase):

    def test_get_no_outcall(self):
        self.assertRaises(NotFoundError, outcall_dao.get, 42)

    def test_get(self):
        outcall_row = self.add_outcall()

        outcall = outcall_dao.get(outcall_row.id)

        assert_that(outcall, equal_to(outcall_row))

    def test_get_multi_tenant(self):
        tenant = self.add_tenant()

        outcall_row = self.add_outcall(tenant_uuid=tenant.uuid)
        outcall = outcall_dao.get(outcall_row.id, tenant_uuids=[tenant.uuid])
        assert_that(outcall, equal_to(outcall_row))

        outcall_row = self.add_outcall()
        self.assertRaises(
            NotFoundError,
            outcall_dao.get, outcall_row.id, tenant_uuids=[tenant.uuid],
        )


class TestFindBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, outcall_dao.find_by, invalid=42)

    def test_find_by_description(self):
        outcall_row = self.add_outcall(description='mydescription')

        outcall = outcall_dao.find_by(description='mydescription')

        assert_that(outcall, equal_to(outcall_row))
        assert_that(outcall.description, equal_to('mydescription'))

    def test_find_by_name(self):
        outcall_row = self.add_outcall(name='myname')

        outcall = outcall_dao.find_by(name='myname')

        assert_that(outcall, equal_to(outcall_row))
        assert_that(outcall.name, equal_to('myname'))

    def test_find_by_preprocess_subroutine(self):
        outcall_row = self.add_outcall(preprocess_subroutine='mysubroutine')

        outcall = outcall_dao.find_by(preprocess_subroutine='mysubroutine')

        assert_that(outcall, equal_to(outcall_row))
        assert_that(outcall.preprocess_subroutine, equal_to('mysubroutine'))

    def test_given_outcall_does_not_exist_then_returns_null(self):
        outcall = outcall_dao.find_by(id=42)

        assert_that(outcall, none())

    def test_find_by_multi_tenant(self):
        tenant = self.add_tenant()

        outcall_row = self.add_outcall()
        outcall = outcall_dao.find_by(name=outcall_row.name, tenant_uuids=[tenant.uuid])
        assert_that(outcall, none())

        outcall_row = self.add_outcall(tenant_uuid=tenant.uuid)
        outcall = outcall_dao.find_by(name=outcall_row.name, tenant_uuids=[tenant.uuid])
        assert_that(outcall, equal_to(outcall_row))


class TestGetBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, outcall_dao.get_by, invalid=42)

    def test_get_by_description(self):
        outcall_row = self.add_outcall(description='mydescription')

        outcall = outcall_dao.get_by(description='mydescription')

        assert_that(outcall, equal_to(outcall_row))
        assert_that(outcall.description, equal_to('mydescription'))

    def test_get_by_name(self):
        outcall_row = self.add_outcall(name='myname')

        outcall = outcall_dao.get_by(name='myname')

        assert_that(outcall, equal_to(outcall_row))
        assert_that(outcall.name, equal_to('myname'))

    def test_get_by_preprocess_subroutine(self):
        outcall_row = self.add_outcall(preprocess_subroutine='MySubroutine')

        outcall = outcall_dao.get_by(preprocess_subroutine='MySubroutine')

        assert_that(outcall, equal_to(outcall_row))
        assert_that(outcall.preprocess_subroutine, equal_to('MySubroutine'))

    def test_given_outcall_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, outcall_dao.get_by, id='42')

    def test_get_by_multi_tenant(self):
        tenant = self.add_tenant()

        outcall_row = self.add_outcall()
        self.assertRaises(
            NotFoundError,
            outcall_dao.get_by, id=outcall_row.id, tenant_uuids=[tenant.uuid],
        )

        outcall_row = self.add_outcall(tenant_uuid=tenant.uuid)
        outcall = outcall_dao.get_by(id=outcall_row.id, tenant_uuids=[tenant.uuid])
        assert_that(outcall, equal_to(outcall_row))


class TestFindAllBy(DAOTestCase):

    def test_find_all_by_no_outcall(self):
        result = outcall_dao.find_all_by(description='toto')

        assert_that(result, contains())

    def test_find_all_by_custom_column(self):
        pass

    def test_find_all_by_native_column(self):
        outcall1 = self.add_outcall(description='MyOutcall')
        outcall2 = self.add_outcall(description='MyOutcall')

        outcalls = outcall_dao.find_all_by(description='MyOutcall')

        assert_that(outcalls, has_items(
            has_property('id', outcall1.id),
            has_property('id', outcall2.id)
        ))

    def test_find_all_multi_tenant(self):
        tenant = self.add_tenant()

        outcall1 = self.add_outcall(preprocess_subroutine='subroutine', tenant_uuid=tenant.uuid)
        outcall2 = self.add_outcall(preprocess_subroutine='subroutine')

        tenants = [tenant.uuid, self.default_tenant.uuid]
        outcalls = outcall_dao.find_all_by(preprocess_subroutine='subroutine', tenant_uuids=tenants)
        assert_that(outcalls, has_items(outcall1, outcall2))

        tenants = [tenant.uuid]
        outcalls = outcall_dao.find_all_by(preprocess_subroutine='subroutine', tenant_uuids=tenants)
        assert_that(outcalls, all_of(has_items(outcall1), not_(has_items(outcall2))))


class TestSearch(DAOTestCase):

    def assert_search_returns_result(self, search_result, **parameters):
        result = outcall_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):

    def test_given_no_outcall_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_outcall_then_returns_one_result(self):
        outcall = self.add_outcall()
        expected = SearchResult(1, [outcall])

        self.assert_search_returns_result(expected)

    def test_search_multi_tenant(self):
        tenant = self.add_tenant()

        outcall1 = self.add_outcall()
        outcall2 = self.add_outcall(tenant_uuid=tenant.uuid)

        expected = SearchResult(2, [outcall1, outcall2])
        tenants = [tenant.uuid, self.default_tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)

        expected = SearchResult(1, [outcall2])
        tenants = [tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)


class TestSearchGivenMultipleOutcall(TestSearch):

    def setUp(self):
        super(TestSearch, self).setUp()
        self.outcall1 = self.add_outcall(name='O1', label='D O1', preprocess_subroutine='Ashton', description='resto')
        self.outcall2 = self.add_outcall(name='O2', label='C O2', preprocess_subroutine='Beaugarton', description='bar')
        self.outcall3 = self.add_outcall(name='O3', label='Aton O3', preprocess_subroutine='Casa', description='resto')
        self.outcall4 = self.add_outcall(name='O4', label='B O4', preprocess_subroutine='Dunkin', description='resto')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.outcall2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_searching_with_an_extra_argument(self):
        expected_resto = SearchResult(2, [self.outcall1, self.outcall3])
        self.assert_search_returns_result(expected_resto, search='ton', description='resto')

        expected_bar = SearchResult(1, [self.outcall2])
        self.assert_search_returns_result(expected_bar, search='ton', description='bar')

        expected_all_resto = SearchResult(3, [self.outcall1, self.outcall3, self.outcall4])
        self.assert_search_returns_result(expected_all_resto, description='resto', order='preprocess_subroutine')

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(
            4, [self.outcall1, self.outcall2, self.outcall3, self.outcall4]
        )
        self.assert_search_returns_result(expected, order='preprocess_subroutine')

        expected = SearchResult(
            4, [self.outcall3, self.outcall4, self.outcall2, self.outcall1]
        )
        self.assert_search_returns_result(expected, order='label')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(self):
        expected = SearchResult(
            4, [self.outcall4, self.outcall3, self.outcall2, self.outcall1]
        )
        self.assert_search_returns_result(expected, order='preprocess_subroutine', direction='desc')

        expected = SearchResult(
            4, [self.outcall1, self.outcall2, self.outcall4, self.outcall3]
        )
        self.assert_search_returns_result(expected, order='label', direction='desc')

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.outcall1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_offset_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.outcall2, self.outcall3, self.outcall4])

        self.assert_search_returns_result(expected, offset=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.outcall2])

        self.assert_search_returns_result(
            expected,
            search='a',
            order='preprocess_subroutine',
            direction='desc',
            offset=1,
            limit=1,
        )


class TestCreate(DAOTestCase):

    def test_create_minimal_fields(self):
        outcall = Outcall(name='myoutcall', label='myoutcall', tenant_uuid=self.default_tenant.uuid)
        created_outcall = outcall_dao.create(outcall)

        row = self.session.query(Outcall).first()

        assert_that(
            created_outcall,
            all_of(
                equal_to(row),
                has_properties(
                    id=is_not(none()),
                    tenant_uuid=self.default_tenant.uuid,
                    name='myoutcall',
                    label='myoutcall',
                    hangupringtime=0,
                    ring_time=none(),
                    internal=0,
                    internal_caller_id=False,
                    preprocess_subroutine=none(),
                    description=none(),
                    commented=0,
                    enabled=True,
                )
            )
        )

    def test_create_with_all_fields(self):
        outcall = Outcall(
            name='myOutcall',
            label='My outcall',
            ring_time=10,
            internal_caller_id=True,
            preprocess_subroutine='MySubroutine',
            description='outcall description',
            enabled=False,
            tenant_uuid=self.default_tenant.uuid,
        )

        created_outcall = outcall_dao.create(outcall)

        row = self.session.query(Outcall).first()

        assert_that(
            created_outcall,
            all_of(
                equal_to(row),
                has_properties(
                    id=is_not(none()),
                    tenant_uuid=self.default_tenant.uuid,
                    name='myOutcall',
                    label='My outcall',
                    ring_time=10,
                    internal_caller_id=True,
                    preprocess_subroutine='MySubroutine',
                    description='outcall description',
                    enabled=False,
                )
            )
        )


class TestEdit(DAOTestCase):

    def test_edit_all_fields(self):
        outcall = outcall_dao.create(Outcall(
            name='MyOutcall',
            label='My outcall',
            ring_time=10,
            internal_caller_id=True,
            preprocess_subroutine='MySubroutine',
            description='outcall description',
            enabled=False,
            tenant_uuid=self.default_tenant.uuid,
        ))

        outcall = outcall_dao.get(outcall.id)
        outcall.name = 'other_name'
        outcall.label = 'other label'
        outcall.ring_time = 5
        outcall.internal_caller_id = False
        outcall.preprocess_subroutine = 'other_routine'
        outcall.description = 'other description'
        outcall.enabled = True
        outcall_dao.edit(outcall)

        row = self.session.query(Outcall).first()

        assert_that(outcall, equal_to(row))
        assert_that(outcall, has_properties(
            id=is_not(none()),
            name='other_name',
            label='other label',
            ring_time=5,
            internal_caller_id=False,
            preprocess_subroutine='other_routine',
            description='other description',
            enabled=True,
        ))

    def test_edit_set_fields_to_null(self):
        outcall = outcall_dao.create(Outcall(
            name='MyOutcall',
            label='my outcall',
            ring_time=10,
            preprocess_subroutine='MySubroutine',
            description='outcall description',
            tenant_uuid=self.default_tenant.uuid,
        ))

        outcall = outcall_dao.get(outcall.id)
        outcall.preprocess_subroutine = None
        outcall.description = None
        outcall.ring_time = None

        outcall_dao.edit(outcall)

        row = self.session.query(Outcall).first()
        assert_that(outcall, equal_to(row))
        assert_that(row, has_properties(
            preprocess_subroutine=none(),
            description=none(),
            ring_time=none(),
        ))


class TestDelete(DAOTestCase):

    def test_delete(self):
        outcall = self.add_outcall()

        outcall_dao.delete(outcall)

        row = self.session.query(Outcall).first()
        assert_that(row, none())

    def test_when_deleting_then_extension_are_dissociated(self):
        outcall = self.add_outcall()
        extension = self.add_extension()
        outcall.associate_extension(extension)

        outcall_dao.delete(outcall)

        row = self.session.query(Extension).first()
        assert_that(row.id, equal_to(extension.id))
        assert_that(row, has_properties(type='user', typeval='0'))

    def test_when_deleting_then_call_permission_are_dissociated(self):
        outcall = self.add_outcall()
        call_permission = self.add_call_permission()
        self.add_outcall_call_permission(typeval=str(outcall.id))

        outcall_dao.delete(outcall)

        outcall_call_permission = self.session.query(RightCallMember).first()
        assert_that(outcall_call_permission, none())

        row = self.session.query(RightCall).first()
        assert_that(row.id, equal_to(call_permission.id))

    def test_when_deleting_then_schedule_are_dissociated(self):
        outcall = self.add_outcall()
        schedule = self.add_schedule()
        self.add_outcall_schedule(schedule_id=schedule.id, pathid=outcall.id)

        outcall_dao.delete(outcall)

        outcall_schedule = self.session.query(SchedulePath).first()
        assert_that(outcall_schedule, none())

        row = self.session.query(Schedule).first()
        assert_that(row.id, equal_to(schedule.id))


class TestAssociateCallPermission(DAOTestCase):

    def test_associate_call_permission(self):
        outcall = self.add_outcall()
        call_permission = self.add_call_permission()

        outcall_dao.associate_call_permission(outcall, call_permission)

        result = self.session.query(Outcall).first()
        assert_that(result, equal_to(outcall))
        assert_that(result.call_permissions, contains(call_permission))

        result = self.session.query(RightCall).first()
        assert_that(result, equal_to(call_permission))
        assert_that(result.outcalls, contains(outcall))

    def test_associate_already_associated(self):
        outcall = self.add_outcall()
        call_permission = self.add_call_permission()
        outcall_dao.associate_call_permission(outcall, call_permission)

        outcall_dao.associate_call_permission(outcall, call_permission)

        result = self.session.query(Outcall).first()
        assert_that(result, equal_to(outcall))
        assert_that(result.call_permissions, contains(call_permission))


class TestDissociateCallPermission(DAOTestCase):

    def test_dissociate_outcall_call_permission(self):
        outcall = self.add_outcall()
        call_permission = self.add_call_permission()
        outcall_dao.associate_call_permission(outcall, call_permission)

        outcall_dao.dissociate_call_permission(outcall, call_permission)

        result = self.session.query(Outcall).first()
        assert_that(result, equal_to(outcall))
        assert_that(result.call_permissions, empty())

    def test_dissociate_outcall_call_permission_not_associated(self):
        outcall = self.add_outcall()
        call_permission = self.add_call_permission()

        outcall_dao.dissociate_call_permission(outcall, call_permission)

        result = self.session.query(Outcall).first()
        assert_that(result, equal_to(outcall))
        assert_that(result.call_permissions, empty())
