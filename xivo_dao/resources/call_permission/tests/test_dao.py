# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from __future__ import unicode_literals

from hamcrest import (assert_that,
                      contains,
                      contains_inanyorder,
                      equal_to,
                      has_items,
                      has_length,
                      has_properties,
                      has_property,
                      is_not,
                      none)


from xivo_dao.alchemy.rightcall import RightCall as CallPermission
from xivo_dao.alchemy.rightcallmember import RightCallMember
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.helpers.exception import NotFoundError, InputError
from xivo_dao.resources.call_permission import dao as call_permission_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestCallPermission(DAOTestCase):

    def add_call_permission(self, **kwargs):
        kwargs.setdefault('name', 'Bôb')
        kwargs.setdefault('enabled', True)

        call_permission = CallPermission(**kwargs)
        self.session.add(call_permission)
        self.session.flush()
        return call_permission


class TestFind(TestCallPermission):

    def test_find_no_user(self):
        result = call_permission_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        call_permission_row = self.add_call_permission(name='Bôb',
                                                       password='âS$%?^ééé',
                                                       mode='allow',
                                                       extensions=['123', '456'],
                                                       enabled=True,
                                                       description='description')

        call_permission = call_permission_dao.find(call_permission_row.id)

        assert_that(call_permission.id, equal_to(call_permission.id))
        assert_that(call_permission.name, equal_to(call_permission_row.name))
        assert_that(call_permission.password, equal_to(call_permission_row.password))
        assert_that(call_permission.mode, equal_to(call_permission_row.mode))
        assert_that(call_permission.enabled, equal_to(call_permission_row.enabled))
        assert_that(call_permission.description, equal_to(call_permission_row.description))
        assert_that(call_permission.extensions, equal_to(call_permission_row.extensions))


class TestGet(TestCallPermission):

    def test_get_no_user(self):
        self.assertRaises(NotFoundError, call_permission_dao.get, 42)

    def test_get(self):
        call_permission_row = self.add_call_permission()

        call_permission = call_permission_dao.get(call_permission_row.id)

        assert_that(call_permission.id, equal_to(call_permission.id))


class TestFindBy(TestCallPermission):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, call_permission_dao.find_by, invalid=42)

    def test_find_by_name(self):
        call_permission_row = self.add_call_permission(name='Jôhn')

        call_permission = call_permission_dao.find_by(name='Jôhn')

        assert_that(call_permission.id, equal_to(call_permission_row.id))
        assert_that(call_permission.name, equal_to('Jôhn'))

    def test_given_user_does_not_exist_then_returns_null(self):
        user = call_permission_dao.find_by(name='42')

        assert_that(user, none())


class TestGetBy(TestCallPermission):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, call_permission_dao.get_by, invalid=42)

    def test_get_by_name(self):
        call_permission_row = self.add_call_permission(name='Jôhn')

        call_permission = call_permission_dao.get_by(name='Jôhn')

        assert_that(call_permission.id, equal_to(call_permission_row.id))
        assert_that(call_permission.name, equal_to('Jôhn'))

    def test_given_user_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, call_permission_dao.get_by, name='42')


class TestFindAllBy(TestCallPermission):

    def test_find_all_by_no_users(self):
        result = call_permission_dao.find_all_by(name='toto')

        assert_that(result, contains())

    def test_find_all_by_renamed_column(self):
        call_permission1 = self.add_call_permission(name='bob', enabled=True)
        call_permission2 = self.add_call_permission(name='alice', enabled=True)

        call_permissions = call_permission_dao.find_all_by(enabled=True)

        assert_that(call_permissions, has_items(has_property('id', call_permission1.id),
                                                has_property('id', call_permission2.id)))

    def test_find_all_by_native_column(self):
        call_permission1 = self.add_call_permission(name='bob', description='description')
        call_permission2 = self.add_call_permission(name='alice', description='description')

        call_permissions = call_permission_dao.find_all_by(description='description')

        assert_that(call_permissions, has_items(has_property('id', call_permission1.id),
                                                has_property('id', call_permission2.id)))


class TestSearch(TestCallPermission):

    def assert_search_returns_result(self, search_result, **parameters):
        result = call_permission_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):

    def test_given_no_call_permissions_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_commented_call_permission_then_returns_one_result(self):
        call_permission = self.add_call_permission(name='bob')
        expected = SearchResult(1, [call_permission])

        self.assert_search_returns_result(expected)


class TestSearchGivenMultipleCallPermissions(TestSearch):

    def setUp(self):
        super(TestSearch, self).setUp()
        self.call_permission1 = self.add_call_permission(name='Ashton', description='resto', mode='allow')
        self.call_permission2 = self.add_call_permission(name='Beaugarton', description='bar')
        self.call_permission3 = self.add_call_permission(name='Casa', description='resto')
        self.call_permission4 = self.add_call_permission(name='Dunkin', description='resto')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.call_permission2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_searching_with_an_extra_argument(self):
        expected_resto = SearchResult(1, [self.call_permission1])
        self.assert_search_returns_result(expected_resto, search='ton', description='resto')

        expected_bar = SearchResult(1, [self.call_permission2])
        self.assert_search_returns_result(expected_bar, search='ton', description='bar')

        expected_all_resto = SearchResult(3, [self.call_permission1, self.call_permission3, self.call_permission4])
        self.assert_search_returns_result(expected_all_resto, description='resto', order='name')

    def test_when_searching_with_a_custom_extra_argument(self):
        expected_allow = SearchResult(1, [self.call_permission1])
        self.assert_search_returns_result(expected_allow, mode='allow')

        expected_all_deny = SearchResult(3, [self.call_permission2, self.call_permission3, self.call_permission4])
        self.assert_search_returns_result(expected_all_deny, mode='deny')

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(4,
                                [self.call_permission1,
                                 self.call_permission2,
                                 self.call_permission3,
                                 self.call_permission4])

        self.assert_search_returns_result(expected, order='name')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(self):
        expected = SearchResult(4, [self.call_permission4,
                                    self.call_permission3,
                                    self.call_permission2,
                                    self.call_permission1])

        self.assert_search_returns_result(expected, order='name', direction='desc')

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.call_permission1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_skipping_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.call_permission2, self.call_permission3, self.call_permission4])

        self.assert_search_returns_result(expected, skip=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.call_permission2])

        self.assert_search_returns_result(expected,
                                          search='a',
                                          order='name',
                                          direction='desc',
                                          skip=1,
                                          limit=1)


class TestCreate(TestCallPermission):

    def test_when_creating_with_invalid_mode_then_raises_error(self):
        self.assertRaises(InputError, CallPermission, mode='invalid_mode')

    def test_create_minimal_fields(self):
        call_permission = CallPermission(name='Jôhn')
        created_call_permission = call_permission_dao.create(call_permission)

        row = self.session.query(CallPermission).first()

        assert_that(created_call_permission, has_properties(id=row.id,
                                                            name="Jôhn",
                                                            password=none(),
                                                            mode='deny',
                                                            enabled=True,
                                                            description=none(),
                                                            extensions=[]))

        assert_that(row, has_properties(id=is_not(none()),
                                        name='Jôhn',
                                        passwd='',
                                        authorization=0,
                                        commented=0,
                                        description=none(),
                                        rightcallextens=[]))

    def test_create_with_all_fields(self):
        call_permission = CallPermission(name='rîghtcall1',
                                         password='P$WDéẁ',
                                         mode='allow',
                                         enabled=False,
                                         description='description',
                                         extensions=['123', '456'])

        created_call_permission = call_permission_dao.create(call_permission)

        row = self.session.query(CallPermission).first()

        assert_that(created_call_permission, has_properties(id=row.id,
                                                            name='rîghtcall1',
                                                            password='P$WDéẁ',
                                                            mode='allow',
                                                            enabled=False,
                                                            description='description',
                                                            extensions=['123', '456']))

        assert_that(row, has_properties(name='rîghtcall1',
                                        passwd='P$WDéẁ',
                                        authorization=1,
                                        commented=1,
                                        description='description',
                                        rightcallextens=has_length(2)))

        assert_that(row.rightcallextens, contains_inanyorder(has_properties(rightcallid=row.id,
                                                                            exten='123'),
                                                             has_properties(rightcallid=row.id,
                                                                            exten='456')))

    def test_create_duplicate_extension(self):
        call_permission = CallPermission(name='Jôhn', extensions=['123', '123'])
        created_call_permission = call_permission_dao.create(call_permission)

        row = self.session.query(CallPermission).first()

        assert_that(created_call_permission, has_properties(id=row.id,
                                                            name="Jôhn",
                                                            password=none(),
                                                            mode='deny',
                                                            enabled=True,
                                                            description=none(),
                                                            extensions=['123']))

        assert_that(row, has_properties(id=is_not(none()),
                                        name='Jôhn',
                                        passwd='',
                                        authorization=0,
                                        commented=0,
                                        description=none(),
                                        rightcallextens=has_length(1)))

        assert_that(row.rightcallextens, contains(has_properties(rightcallid=row.id,
                                                                 exten='123')))


class TestEdit(TestCallPermission):

    def test_edit_all_fields(self):
        call_permission = call_permission_dao.create(CallPermission(name='rîghtcall1',
                                                                    password='P$WDéẁ',
                                                                    mode='deny',
                                                                    enabled=True,
                                                                    description='tototo',
                                                                    extensions=['123', '456']))

        call_permission = call_permission_dao.get(call_permission.id)
        call_permission.name = 'denỳallfriends'
        call_permission.password = 'Alhahlalahl'
        call_permission.mode = 'allow'
        call_permission.enabled = False
        call_permission.description = 'description'
        call_permission.extensions = ['789', '321', '654']

        call_permission_dao.edit(call_permission)

        row = self.session.query(CallPermission).first()

        assert_that(row, has_properties(name='denỳallfriends',
                                        passwd='Alhahlalahl',
                                        authorization=1,
                                        commented=1,
                                        description='description',
                                        rightcallextens=has_length(3)))

        assert_that(row.rightcallextens, contains_inanyorder(has_properties(rightcallid=row.id,
                                                                            exten='789'),
                                                             has_properties(rightcallid=row.id,
                                                                            exten='321'),
                                                             has_properties(rightcallid=row.id,
                                                                            exten='654')))

    def test_edit_set_fields_to_null(self):
        call_permission = call_permission_dao.create(CallPermission(name='rîghtcall1',
                                                                    password='P$WDéẁ',
                                                                    mode='deny',
                                                                    enabled=True,
                                                                    description='tototo',
                                                                    extensions=['123', '456']))

        call_permission = call_permission_dao.get(call_permission.id)
        call_permission.password = None
        call_permission.description = None

        call_permission_dao.edit(call_permission)

        row = self.session.query(CallPermission).first()

        assert_that(row, has_properties(passwd='',
                                        description=none()))

    def test_edit_extensions_with_same_value(self):
        call_permission = call_permission_dao.create(CallPermission(name='rîghtcall1',
                                                                    extensions=['123', '456']))

        call_permission = call_permission_dao.get(call_permission.id)
        call_permission.extensions = ['789', '123']

        call_permission_dao.edit(call_permission)

        row = self.session.query(CallPermission).first()

        assert_that(row, has_properties(name='rîghtcall1',
                                        rightcallextens=has_length(2)))

        assert_that(row.rightcallextens, contains_inanyorder(has_properties(rightcallid=row.id,
                                                                            exten='789'),
                                                             has_properties(rightcallid=row.id,
                                                                            exten='123')))


class TestDelete(TestCallPermission):

    def test_delete(self):
        call_permission = call_permission_dao.create(CallPermission(name='Delete'))
        call_permission = call_permission_dao.get(call_permission.id)

        call_permission_dao.delete(call_permission)

        row = self.session.query(CallPermission).first()
        assert_that(row, none())

    def test_delete_references_to_other_tables(self):
        user = self.add_user()
        group = self.add_group()
        incall = self.add_incall()
        outcall = self.add_outcall()
        call_permission = call_permission_dao.create(CallPermission(name='Delete'))
        self.add_right_call_member(rightcallid=call_permission.id, type='user', typeval=str(user.id))
        self.add_right_call_member(rightcallid=call_permission.id, type='group', typeval=str(group.id))
        self.add_right_call_member(rightcallid=call_permission.id, type='incall', typeval=str(incall.id))
        self.add_right_call_member(rightcallid=call_permission.id, type='outcall', typeval=str(outcall.id))

        call_permission_dao.delete(call_permission)

        assert_that(self.session.query(RightCallMember).first(), none())

    def add_right_call_member(self, **kwargs):
        member = RightCallMember(**kwargs)
        self.session.add(member)
        self.session.flush()
        return member
