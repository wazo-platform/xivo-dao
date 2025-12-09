# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    all_of,
    assert_that,
    calling,
    contains_exactly,
    contains_inanyorder,
    empty,
    equal_to,
    has_items,
    has_properties,
    has_property,
    none,
    not_,
    raises,
)

from xivo_dao.alchemy.extension import Extension
from xivo_dao.helpers.exception import InputError, NotFoundError
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao as extension_dao


class TestExtension(DAOTestCase):
    def assert_search_returns_result(self, search_result, **parameters):
        result = extension_dao.search(**parameters)
        expected_extensions = [
            has_properties(
                id=e.id, exten=e.exten, context=e.context, commented=e.commented
            )
            for e in search_result.items
        ]
        expected = has_properties(
            total=search_result.total, items=contains_inanyorder(*expected_extensions)
        )
        assert_that(result, expected)


class TestSimpleSearch(TestExtension):
    def test_given_no_extensions_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_commented_extension_then_returns_one_result(self):
        extension = self.add_extension(exten='1000', commented=1)
        expected = SearchResult(1, [extension])

        self.assert_search_returns_result(expected)


class TestSearchGivenMultipleTenants(TestExtension):
    def test_given_extensions_in_multiple_tenants(self):
        tenant_1 = self.add_tenant()
        tenant_2 = self.add_tenant()
        tenant_3 = self.add_tenant()

        context_1 = self.add_context(tenant_uuid=tenant_1.uuid)
        context_2 = self.add_context(tenant_uuid=tenant_2.uuid)
        context_3 = self.add_context(tenant_uuid=tenant_3.uuid)

        extension_1 = self.add_extension(exten='1001', context=context_1.name)
        extension_2 = self.add_extension(exten='1002', context=context_2.name)
        extension_3 = self.add_extension(exten='1003', context=context_3.name)

        expected = SearchResult(2, [extension_1, extension_2])
        self.assert_search_returns_result(
            expected, tenant_uuids=[tenant_1.uuid, tenant_2.uuid]
        )

        expected = SearchResult(0, [])
        self.assert_search_returns_result(expected, tenant_uuids=[])

        expected = SearchResult(3, [extension_1, extension_2, extension_3])
        self.assert_search_returns_result(expected)


class TestSearchGivenMultipleExtensions(TestExtension):
    def setUp(self):
        TestExtension.setUp(self)
        self.inside_context = self.add_context(name='inside')
        self.default_context = self.add_context(name='default')
        self.extension1 = self.add_extension(
            exten='1000', context=self.inside_context.name
        )
        self.extension2 = self.add_extension(
            exten='1001', context=self.inside_context.name
        )
        self.extension3 = self.add_extension(
            exten='1002', context=self.inside_context.name
        )
        self.extension4 = self.add_extension(
            exten='1103', context=self.inside_context.name
        )
        self.extension5 = self.add_extension(
            exten='1103', context=self.default_context.name
        )

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.extension2])

        self.assert_search_returns_result(expected, search='1001')

    def test_when_searching_with_a_context(self):
        expected_all_1103 = SearchResult(2, [self.extension4, self.extension5])
        self.assert_search_returns_result(expected_all_1103, search='1103')

        expected_1103_inside = SearchResult(1, [self.extension4])
        self.assert_search_returns_result(
            expected_1103_inside, search='1103', context=self.inside_context.name
        )

        expected_all_inside = SearchResult(
            4, [self.extension1, self.extension2, self.extension3, self.extension4]
        )
        self.assert_search_returns_result(
            expected_all_inside, context=self.inside_context.name, order='exten'
        )

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(
            4, [self.extension1, self.extension2, self.extension3, self.extension4]
        )

        self.assert_search_returns_result(
            expected, order='exten', context=self.inside_context.name
        )

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(
        self,
    ):
        expected = SearchResult(
            4, [self.extension4, self.extension3, self.extension2, self.extension1]
        )

        self.assert_search_returns_result(
            expected, order='exten', direction='desc', context=self.inside_context.name
        )

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(5, [self.extension1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_offset_then_returns_right_number_of_items(self):
        expected = SearchResult(
            5, [self.extension2, self.extension3, self.extension4, self.extension5]
        )

        self.assert_search_returns_result(expected, offset=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.extension2])

        self.assert_search_returns_result(
            expected, search='100', order='exten', direction='desc', offset=1, limit=1
        )


class TestSearchGivenInternalExtensionType(TestExtension):
    def setUp(self):
        TestExtension.setUp(self)

        internal_context = self.add_context(
            name='internal_context', contexttype='internal'
        )
        self.extension1 = self.add_extension(
            exten='1000', context=internal_context.name
        )
        self.extension2 = self.add_extension(
            exten='1001', context=internal_context.name
        )

    def test_when_searching_type_internal_extensions_then_returns_internal_extensions(
        self,
    ):
        expected = SearchResult(2, [self.extension1, self.extension2])

        self.assert_search_returns_result(expected, type='internal')

    def test_when_searching_type_internal_and_limit_then_returns_internal_extensions(
        self,
    ):
        expected = SearchResult(2, [self.extension1])

        self.assert_search_returns_result(expected, type='internal', limit=1)

    def test_when_searching_type_incall_then_returns_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected, type='incall')


class TestSearchGivenIncallExtensionType(TestExtension):
    def setUp(self):
        TestExtension.setUp(self)

        incall_context = self.add_context(name='incall_context', contexttype='incall')
        self.extension1 = self.add_extension(exten='1000', context=incall_context.name)
        self.extension2 = self.add_extension(exten='1001', context=incall_context.name)

    def test_when_searching_type_internal_then_returns_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected, type='internal')

    def test_when_searching_type_incall_then_returns_incall_extensions(self):
        expected = SearchResult(2, [self.extension1, self.extension2])

        self.assert_search_returns_result(expected, type='incall')

    def test_when_searching_type_incall_and_limit_then_returns_interal_extensions(self):
        expected = SearchResult(2, [self.extension1])

        self.assert_search_returns_result(expected, type='incall', limit=1)


class TestFind(TestExtension):
    def test_find_no_extension(self):
        result = extension_dao.find(1)

        assert_that(result, none())

    def test_find(self):
        context = self.add_context(name='default')
        extension_row = self.add_extension(exten='1234', context=context.name)

        result = extension_dao.find(extension_row.id)

        assert_that(
            result,
            all_of(
                has_property('exten', extension_row.exten),
                has_property('context', extension_row.context),
            ),
        )

    def test_find_multi_tenant(self):
        tenant = self.add_tenant()
        context = self.add_context(tenant_uuid=tenant.uuid)

        extension = self.add_extension(exten='1234', context=context.name)

        result = extension_dao.find(extension.id, tenant_uuids=[tenant.uuid])
        assert_that(
            result,
            has_properties(
                exten=extension.exten,
                context=context.name,
                tenant_uuid=tenant.uuid,
            ),
        )

        result = extension_dao.find(
            extension.id, tenant_uuids=[self.default_tenant.uuid]
        )
        assert_that(result, none())


class TestFindBy(TestExtension):
    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, extension_dao.find_by, invalid=42)

    def test_given_extension_does_not_exist_then_returns_null(self):
        extension = extension_dao.find_by(exten='invalid')

        assert_that(extension, none())

    def test_given_extension_exists_then_returns_extension(self):
        row = self.add_extension(exten='1000')

        result = extension_dao.find_by(exten='1000')

        assert_that(result.id, equal_to(row.id))

    def test_given_extension_exists_then_returns_extension_with_a_tenant(self):
        tenant = self.add_tenant()
        context = self.add_context(tenant_uuid=tenant.uuid)

        self.add_extension(exten='1000', context=context.name)
        result = extension_dao.find_by(exten='1000')
        assert_that(result, has_properties(tenant_uuid=tenant.uuid))

    def test_given_entension_exists_with_tenant_filtering(self):
        tenant = self.add_tenant()
        context = self.add_context(tenant_uuid=tenant.uuid)

        extension = self.add_extension(exten='1000', context=context.name)

        result = extension_dao.find_by(
            exten='1000', tenant_uuids=[self.default_tenant.uuid]
        )
        assert_that(result, none())

        result = extension_dao.find_by(exten='1000', tenant_uuids=[tenant.uuid])
        assert_that(result, has_properties(id=extension.id, tenant_uuid=tenant.uuid))


class TestGetBy(TestExtension):
    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, extension_dao.get_by, invalid=42)

    def test_given_extension_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, extension_dao.get_by, exten='42')

    def test_given_extension_exists_then_returns_extension(self):
        row = self.add_extension(exten='1000')

        result = extension_dao.get_by(exten='1000')

        assert_that(result.id, equal_to(row.id))

    def test_given_extension_exists_then_returns_extension_with_a_tenant(self):
        tenant = self.add_tenant()
        context = self.add_context(tenant_uuid=tenant.uuid)

        self.add_extension(exten='1000', context=context.name)
        result = extension_dao.get_by(exten='1000')
        assert_that(result, has_properties(tenant_uuid=tenant.uuid))

    def test_given_entension_exists_with_tenant_filtering(self):
        tenant = self.add_tenant()
        context = self.add_context(tenant_uuid=tenant.uuid)

        extension = self.add_extension(exten='1000', context=context.name)

        self.assertRaises(
            NotFoundError,
            extension_dao.get_by,
            exten='1000',
            tenant_uuids=[self.default_tenant.uuid],
        )

        result = extension_dao.get_by(exten='1000', tenant_uuids=[tenant.uuid])
        assert_that(result, has_properties(id=extension.id))


class TestFindAllBy(TestExtension):
    def test_find_all_by_no_extensions(self):
        result = extension_dao.find_all_by(exten='invalid')

        assert_that(result, contains_exactly())

    def test_find_all_by_native_column(self):
        context = self.add_context(name='mycontext')
        extension1 = self.add_extension(exten='1000', context=context.name)
        extension2 = self.add_extension(exten='1001', context=context.name)

        extensions = extension_dao.find_all_by(context=context.name)

        assert_that(
            extensions,
            has_items(
                has_property('id', extension1.id), has_property('id', extension2.id)
            ),
        )

    def test_find_all_by_with_multi_tenant(self):
        tenant = self.add_tenant()
        context = self.add_context(tenant_uuid=tenant.uuid)

        extension = self.add_extension(exten='1000', context=context.name)

        result = extension_dao.find_all_by(
            exten='1000', tenant_uuids=[self.default_tenant.uuid]
        )
        assert_that(result, empty())

        result = extension_dao.find_all_by(exten='1000', tenant_uuids=[tenant.uuid])
        assert_that(
            result,
            has_items(has_properties(id=extension.id, tenant_uuid=tenant.uuid)),
        )


class TestGet(TestExtension):
    def test_get_no_exist(self):
        self.assertRaises(NotFoundError, extension_dao.get, 666)

    def test_get(self):
        exten = 'sdklfj'

        expected_extension = self.add_extension(exten=exten)

        extension = extension_dao.get(expected_extension.id)

        assert_that(extension.exten, equal_to(exten))

    def test_incall_relationship(self):
        incall_row = self.add_incall()
        extension_row = self.add_extension(type='incall', typeval=str(incall_row.id))

        extension = extension_dao.get(extension_row.id)

        assert_that(extension, equal_to(extension_row))
        assert_that(extension.incall, equal_to(incall_row))

    def test_get_with_multi_tenant(self):
        tenant = self.add_tenant()
        context = self.add_context(tenant_uuid=tenant.uuid)

        extension = self.add_extension(exten='1000', context=context.name)

        self.assertRaises(
            NotFoundError,
            extension_dao.get,
            extension.id,
            tenant_uuids=[self.default_tenant.uuid],
        )

        result = extension_dao.get(extension.id, tenant_uuids=[tenant.uuid])
        assert_that(
            result,
            has_properties(id=extension.id, tenant_uuid=tenant.uuid),
        )


class TestCreate(TestExtension):
    def test_create(self):
        exten = 'extension'
        context = self.add_context(name='mycontext')

        extension = Extension(exten=exten, context=context.name)

        created_extension = extension_dao.create(extension)

        row = (
            self.session.query(Extension)
            .filter(Extension.id == created_extension.id)
            .first()
        )

        assert_that(row.id, equal_to(created_extension.id))
        assert_that(row.exten, equal_to(exten))
        assert_that(row.context, equal_to(context.name))
        assert_that(row.commented, equal_to(0))
        assert_that(row.type, equal_to('user'))
        assert_that(row.typeval, equal_to('0'))

    def test_create_all_parameters(self):
        context = self.add_context(name='default')
        extension = Extension(exten='1000', context=context.name, commented=1)

        created_extension = extension_dao.create(extension)

        row = (
            self.session.query(Extension)
            .filter(Extension.id == created_extension.id)
            .first()
        )

        assert_that(row.id, equal_to(created_extension.id))
        assert_that(row.exten, equal_to('1000'))
        assert_that(row.context, equal_to(context.name))
        assert_that(row.commented, equal_to(1))
        assert_that(row.type, equal_to('user'))
        assert_that(row.typeval, equal_to('0'))


class TestEdit(TestExtension):
    def test_edit(self):
        exten = 'extension'
        context = self.add_context(name='new_context')
        commented = 1
        row = self.add_extension()

        extension = extension_dao.get(row.id)
        extension.exten = exten
        extension.context = context.name
        extension.commented = commented

        extension_dao.edit(extension)

        row = self.session.get(Extension, extension.id)

        assert_that(row.id, equal_to(extension.id))
        assert_that(row.exten, equal_to(exten))
        assert_that(row.context, equal_to(context.name))
        assert_that(row.commented, equal_to(1))
        assert_that(row.type, equal_to('user'))
        assert_that(row.typeval, equal_to('0'))


class TestDelete(TestExtension):
    def test_delete(self):
        exten = 'sdklfj'
        expected_extension = self.add_extension(exten=exten)

        extension = extension_dao.get(expected_extension.id)

        extension_dao.delete(extension)

        row = (
            self.session.query(Extension)
            .filter(Extension.id == expected_extension.id)
            .first()
        )

        assert row is None


class TestRelationship(TestExtension):
    def test_incall_relationship(self):
        incall_row = self.add_incall()
        extension_row = self.add_extension(type='incall', typeval=str(incall_row.id))

        extension = extension_dao.get(extension_row.id)

        assert_that(extension, equal_to(extension_row))
        assert_that(extension.incall, equal_to(incall_row))

    def test_outcall_relationship(self):
        outcall_row = self.add_outcall()
        extension_row = self.add_extension()
        outcall_row.associate_extension(extension_row)

        extension = extension_dao.get(extension_row.id)

        assert_that(extension, equal_to(extension_row))
        assert_that(extension.outcall, equal_to(outcall_row))

    def test_lines_relationship(self):
        extension_row = self.add_extension()
        line1_row = self.add_line()
        line2_row = self.add_line()
        self.add_line_extension(line_id=line1_row.id, extension_id=extension_row.id)
        self.add_line_extension(line_id=line2_row.id, extension_id=extension_row.id)

        extension = extension_dao.get(extension_row.id)
        assert_that(extension, equal_to(extension_row))
        assert_that(extension.lines, contains_inanyorder(line1_row, line2_row))

        assert_that(
            calling(extension_dao.delete).with_args(extension),
            not_(raises(Exception)),
        )

    def test_group_relationship(self):
        extension_row = self.add_extension()
        group_row = self.add_group()
        extension_dao.associate_group(group_row, extension_row)

        extension = extension_dao.get(extension_row.id)
        assert_that(extension, equal_to(extension_row))
        assert_that(extension.group, equal_to(group_row))

    def test_queue_relationship(self):
        extension_row = self.add_extension()
        queue_row = self.add_queuefeatures()
        extension_dao.associate_queue(queue_row, extension_row)

        extension = extension_dao.get(extension_row.id)
        assert_that(extension, equal_to(extension_row))
        assert_that(extension.queue, equal_to(queue_row))


class TestAssociateGroup(DAOTestCase):
    def test_associate_group(self):
        extension = self.add_extension()
        group = self.add_group()

        extension_dao.associate_group(group, extension)

        assert_that(
            group.extensions,
            contains_inanyorder(
                has_properties(
                    exten=extension.exten,
                    context=extension.context,
                    type='group',
                    typeval=str(group.id),
                )
            ),
        )

    def test_associate_multiple_groups(self):
        extension1 = self.add_extension()
        extension2 = self.add_extension()
        extension3 = self.add_extension()
        group = self.add_group()

        extension_dao.associate_group(group, extension1)
        extension_dao.associate_group(group, extension2)
        extension_dao.associate_group(group, extension3)

        assert_that(
            group.extensions, contains_inanyorder(extension1, extension2, extension3)
        )

    def test_dissociate_groups(self):
        extension1 = self.add_extension()
        extension2 = self.add_extension()
        extension3 = self.add_extension()
        group = self.add_group()
        extension_dao.associate_group(group, extension1)
        extension_dao.associate_group(group, extension2)
        extension_dao.associate_group(group, extension3)

        assert_that(group.extensions, not_(empty()))

        extension_dao.dissociate_group(group, extension1)
        extension_dao.dissociate_group(group, extension2)
        extension_dao.dissociate_group(group, extension3)

        assert_that(group.extensions, empty())

        rows = self.session.query(Extension).all()
        assert_that(
            rows,
            contains_inanyorder(
                has_properties(type='user', typeval='0'),
                has_properties(type='user', typeval='0'),
                has_properties(type='user', typeval='0'),
            ),
        )

    def test_dissociate_group_not_associated(self):
        extension = self.add_extension(typeval='123')
        group = self.add_group()

        extension_dao.dissociate_group(group, extension)

        result = self.session.query(Extension).first()
        assert_that(result, has_properties(typeval='123'))


class TestAssociateQueue(DAOTestCase):
    def test_associate_queue(self):
        extension = self.add_extension()
        queue = self.add_queuefeatures()

        extension_dao.associate_queue(queue, extension)

        assert_that(
            queue.extensions,
            contains_inanyorder(
                has_properties(
                    exten=extension.exten,
                    context=extension.context,
                    type='queue',
                    typeval=str(queue.id),
                )
            ),
        )

    def test_associate_fix_queue(self):
        context = self.add_context(name='mycontext')
        extension = self.add_extension(exten='1234', context=context.name)
        queue = self.add_queuefeatures()
        assert_that(
            queue,
            has_properties(
                context=not_(context.name),
                number=not_('1234'),
            ),
        )

        extension_dao.associate_queue(queue, extension)
        assert_that(
            queue,
            has_properties(
                context=context.name,
                number='1234',
            ),
        )

    def test_associate_multiple_queues(self):
        extension1 = self.add_extension()
        extension2 = self.add_extension()
        extension3 = self.add_extension()
        queue = self.add_queuefeatures()

        extension_dao.associate_queue(queue, extension1)
        extension_dao.associate_queue(queue, extension2)
        extension_dao.associate_queue(queue, extension3)

        assert_that(
            queue.extensions, contains_inanyorder(extension1, extension2, extension3)
        )

    def test_dissociate_queues(self):
        extension1 = self.add_extension()
        extension2 = self.add_extension()
        extension3 = self.add_extension()
        queue = self.add_queuefeatures()
        extension_dao.associate_queue(queue, extension1)
        extension_dao.associate_queue(queue, extension2)
        extension_dao.associate_queue(queue, extension3)

        assert_that(queue.extensions, not_(empty()))

        extension_dao.dissociate_queue(queue, extension1)
        extension_dao.dissociate_queue(queue, extension2)
        extension_dao.dissociate_queue(queue, extension3)

        assert_that(queue.extensions, empty())

        rows = self.session.query(Extension).all()
        assert_that(
            rows,
            contains_inanyorder(
                has_properties(type='user', typeval='0'),
                has_properties(type='user', typeval='0'),
                has_properties(type='user', typeval='0'),
            ),
        )

    def test_dissociate_fix_queue(self):
        context = self.add_context(name='mycontext')
        extension = self.add_extension(exten='1234', context=context.name)
        queue = self.add_queuefeatures()
        extension_dao.associate_queue(queue, extension)
        assert_that(
            queue,
            has_properties(
                context=context.name,
                number='1234',
            ),
        )

        extension_dao.dissociate_queue(queue, extension)

        assert_that(queue, has_properties(context=None, number=None))

    def test_dissociate_queue_not_associated(self):
        extension = self.add_extension(typeval='123')
        queue = self.add_queuefeatures()

        extension_dao.dissociate_queue(queue, extension)

        result = self.session.query(Extension).first()
        assert_that(result, has_properties(typeval='123'))


class TestAssociateIncall(DAOTestCase):
    def test_associate_incall(self):
        extension = self.add_extension()
        incall = self.add_incall()

        extension_dao.associate_incall(incall, extension)

        assert_that(
            incall.extensions,
            contains_inanyorder(
                has_properties(
                    exten=extension.exten,
                    context=extension.context,
                    type='incall',
                    typeval=str(incall.id),
                )
            ),
        )

    def test_associate_multiple_incalls(self):
        extension1 = self.add_extension()
        extension2 = self.add_extension()
        extension3 = self.add_extension()
        incall = self.add_incall()

        extension_dao.associate_incall(incall, extension1)
        extension_dao.associate_incall(incall, extension2)
        extension_dao.associate_incall(incall, extension3)

        assert_that(
            incall.extensions, contains_inanyorder(extension1, extension2, extension3)
        )

    def test_dissociate_incalls(self):
        extension1 = self.add_extension()
        extension2 = self.add_extension()
        extension3 = self.add_extension()
        incall = self.add_incall()
        extension_dao.associate_incall(incall, extension1)
        extension_dao.associate_incall(incall, extension2)
        extension_dao.associate_incall(incall, extension3)

        assert_that(incall.extensions, not_(empty()))

        extension_dao.dissociate_incall(incall, extension1)
        extension_dao.dissociate_incall(incall, extension2)
        extension_dao.dissociate_incall(incall, extension3)

        assert_that(incall.extensions, empty())

        rows = self.session.query(Extension).all()
        assert_that(
            rows,
            contains_inanyorder(
                has_properties(type='user', typeval='0'),
                has_properties(type='user', typeval='0'),
                has_properties(type='user', typeval='0'),
            ),
        )

    def test_dissociate_incall_not_associated(self):
        extension = self.add_extension()
        group = self.add_group()
        extension_dao.associate_group(group, extension)
        incall = self.add_incall()

        extension_dao.dissociate_incall(incall, extension)

        result = self.session.query(Extension).first()
        assert_that(result, has_properties(typeval=str(group.id)))


class TestAssociateConference(DAOTestCase):
    def test_associate_conference(self):
        extension = self.add_extension()
        conference = self.add_conference()

        extension_dao.associate_conference(conference, extension)

        assert_that(
            conference.extensions,
            contains_inanyorder(
                has_properties(
                    exten=extension.exten,
                    context=extension.context,
                    type='conference',
                    typeval=str(conference.id),
                )
            ),
        )

    def test_associate_multiple_conferences(self):
        extension1 = self.add_extension()
        extension2 = self.add_extension()
        extension3 = self.add_extension()
        conference = self.add_conference()

        extension_dao.associate_conference(conference, extension1)
        extension_dao.associate_conference(conference, extension2)
        extension_dao.associate_conference(conference, extension3)

        assert_that(
            conference.extensions,
            contains_inanyorder(extension1, extension2, extension3),
        )

    def test_dissociate_conferences(self):
        extension1 = self.add_extension()
        extension2 = self.add_extension()
        extension3 = self.add_extension()
        conference = self.add_conference()
        extension_dao.associate_conference(conference, extension1)
        extension_dao.associate_conference(conference, extension2)
        extension_dao.associate_conference(conference, extension3)

        assert_that(conference.extensions, not_(empty()))

        extension_dao.dissociate_conference(conference, extension1)
        extension_dao.dissociate_conference(conference, extension2)
        extension_dao.dissociate_conference(conference, extension3)

        assert_that(conference.extensions, empty())

        rows = self.session.query(Extension).all()
        assert_that(
            rows,
            contains_inanyorder(
                has_properties(type='user', typeval='0'),
                has_properties(type='user', typeval='0'),
                has_properties(type='user', typeval='0'),
            ),
        )

    def test_dissociate_conference_not_associated(self):
        extension = self.add_extension(typeval='123')
        conference = self.add_conference()

        extension_dao.dissociate_conference(conference, extension)

        result = self.session.query(Extension).first()
        assert_that(result, has_properties(typeval='123'))


class TestAssociateParkingLot(DAOTestCase):
    def test_associate_parking_lot(self):
        extension = self.add_extension()
        parking_lot = self.add_parking_lot()

        extension_dao.associate_parking_lot(parking_lot, extension)

        assert_that(
            parking_lot.extensions,
            contains_inanyorder(
                has_properties(
                    exten=extension.exten,
                    context=extension.context,
                    type='parking',
                    typeval=str(parking_lot.id),
                )
            ),
        )

    def test_associate_multiple_parking_lots(self):
        extension1 = self.add_extension()
        extension2 = self.add_extension()
        extension3 = self.add_extension()
        parking_lot = self.add_parking_lot()

        extension_dao.associate_parking_lot(parking_lot, extension1)
        extension_dao.associate_parking_lot(parking_lot, extension2)
        extension_dao.associate_parking_lot(parking_lot, extension3)

        assert_that(
            parking_lot.extensions,
            contains_inanyorder(extension1, extension2, extension3),
        )

    def test_dissociate_parking_lots(self):
        extension1 = self.add_extension()
        extension2 = self.add_extension()
        extension3 = self.add_extension()
        parking_lot = self.add_parking_lot()
        extension_dao.associate_parking_lot(parking_lot, extension1)
        extension_dao.associate_parking_lot(parking_lot, extension2)
        extension_dao.associate_parking_lot(parking_lot, extension3)

        assert_that(parking_lot.extensions, not_(empty()))

        extension_dao.dissociate_parking_lot(parking_lot, extension1)
        extension_dao.dissociate_parking_lot(parking_lot, extension2)
        extension_dao.dissociate_parking_lot(parking_lot, extension3)

        assert_that(parking_lot.extensions, empty())

        rows = self.session.query(Extension).all()
        assert_that(
            rows,
            contains_inanyorder(
                has_properties(type='user', typeval='0'),
                has_properties(type='user', typeval='0'),
                has_properties(type='user', typeval='0'),
            ),
        )

    def test_dissociate_parking_lot_not_associated(self):
        extension = self.add_extension(typeval='123')
        parking_lot = self.add_parking_lot()

        extension_dao.dissociate_parking_lot(parking_lot, extension)

        result = self.session.query(Extension).first()
        assert_that(result, has_properties(typeval='123'))
