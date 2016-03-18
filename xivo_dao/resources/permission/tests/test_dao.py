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
                      equal_to,
                      has_length,
                      has_property,
                      has_properties,
                      is_not,
                      none,
                      has_items,
                      contains)


from xivo_dao.alchemy.rightcall import RightCall as Permission
from xivo_dao.alchemy.rightcallmember import RightCallMember
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.helpers.exception import NotFoundError, InputError
from xivo_dao.resources.permission import dao as permission_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestPermission(DAOTestCase):

    def add_permission(self, **kwargs):
        kwargs.setdefault('name', 'Bôb')
        kwargs.setdefault('enabled', True)

        permission = Permission(**kwargs)
        self.session.add(permission)
        self.session.flush()
        return permission


class TestFind(TestPermission):

    def test_find_no_user(self):
        result = permission_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        permission_row = self.add_permission(name='Bôb',
                                             password='âS$%?^ééé',
                                             mode='1',
                                             extensions=['123', '456'],
                                             enabled=True,
                                             description='description')

        permission = permission_dao.find(permission_row.id)

        assert_that(permission.id, equal_to(permission.id))
        assert_that(permission.name, equal_to(permission_row.name))
        assert_that(permission.password, equal_to(permission_row.password))
        assert_that(permission.mode, equal_to(permission_row.mode))
        assert_that(permission.enabled, equal_to(permission_row.enabled))
        assert_that(permission.description, equal_to(permission_row.description))
        assert_that(permission.extensions, equal_to(permission_row.extensions))


class TestGet(TestPermission):

    def test_get_no_user(self):
        self.assertRaises(NotFoundError, permission_dao.get, 42)

    def test_get(self):
        permission_row = self.add_permission()

        permission = permission_dao.get(permission_row.id)

        assert_that(permission.id, equal_to(permission.id))


class TestFindBy(TestPermission):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, permission_dao.find_by, invalid=42)

    def test_find_by_name(self):
        permission_row = self.add_permission(name='Jôhn')

        permission = permission_dao.find_by(name='Jôhn')

        assert_that(permission.id, equal_to(permission_row.id))
        assert_that(permission.name, equal_to('Jôhn'))

    def test_given_user_does_not_exist_then_returns_null(self):
        user = permission_dao.find_by(name='42')

        assert_that(user, none())


class TestGetBy(TestPermission):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, permission_dao.get_by, invalid=42)

    def test_get_by_name(self):
        permission_row = self.add_permission(name='Jôhn')

        permission = permission_dao.get_by(name='Jôhn')

        assert_that(permission.id, equal_to(permission_row.id))
        assert_that(permission.name, equal_to('Jôhn'))

    def test_given_user_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, permission_dao.get_by, name='42')


class TestFindAllBy(TestPermission):

    def test_find_all_by_no_users(self):
        result = permission_dao.find_all_by(name='toto')

        assert_that(result, contains())

    def test_find_all_by_renamed_column(self):
        permission1 = self.add_permission(name='bob', enabled=True)
        permission2 = self.add_permission(name='alice', enabled=True)

        permissions = permission_dao.find_all_by(enabled=True)

        assert_that(permissions, has_items(has_property('id', permission1.id),
                                           has_property('id', permission2.id)))

    def test_find_all_by_native_column(self):
        permission1 = self.add_permission(name='bob', description='description')
        permission2 = self.add_permission(name='alice', description='description')

        permissions = permission_dao.find_all_by(description='description')

        assert_that(permissions, has_items(has_property('id', permission1.id),
                                           has_property('id', permission2.id)))


class TestSearch(TestPermission):

    def assert_search_returns_result(self, search_result, **parameters):
        result = permission_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):

    def test_given_no_permissions_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_commented_permission_then_returns_one_result(self):
        permission = self.add_permission(name='bob')
        expected = SearchResult(1, [permission])

        self.assert_search_returns_result(expected)


class TestSearchGivenMultiplePermissions(TestSearch):

    def setUp(self):
        super(TestSearch, self).setUp()
        self.permission1 = self.add_permission(name='Ashton', description='resto')
        self.permission2 = self.add_permission(name='Beaugarton', description='bar')
        self.permission3 = self.add_permission(name='Casa', description='resto')
        self.permission4 = self.add_permission(name='Dunkin', description='resto')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.permission2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_searching_with_an_extra_argument(self):
        expected_resto = SearchResult(1, [self.permission1])
        self.assert_search_returns_result(expected_resto, search='ton', description='resto')

        expected_bar = SearchResult(1, [self.permission2])
        self.assert_search_returns_result(expected_bar, search='ton', description='bar')

        expected_all_resto = SearchResult(3, [self.permission1, self.permission3, self.permission4])
        self.assert_search_returns_result(expected_all_resto, description='resto', order='name')

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(4, [self.permission1, self.permission2, self.permission3, self.permission4])

        self.assert_search_returns_result(expected, order='name')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(self):
        expected = SearchResult(4, [self.permission4, self.permission3, self.permission2, self.permission1])

        self.assert_search_returns_result(expected, order='name', direction='desc')

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.permission1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_skipping_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.permission2, self.permission3, self.permission4])

        self.assert_search_returns_result(expected, skip=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.permission2])

        self.assert_search_returns_result(expected,
                                          search='a',
                                          order='name',
                                          direction='desc',
                                          skip=1,
                                          limit=1)


class TestCreate(TestPermission):

    def test_create_minimal_fields(self):
        permission = Permission(name='Jôhn')
        created_permission = permission_dao.create(permission)

        row = self.session.query(Permission).first()

        assert_that(created_permission, has_properties(id=row.id,
                                                       name="Jôhn",
                                                       password=none(),
                                                       mode=0,
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
        permission = Permission(name='rîghtcall1',
                                password='P$WDéẁ',
                                mode=1,
                                enabled=False,
                                description='description',
                                extensions=['123', '456'])

        created_permission = permission_dao.create(permission)

        row = self.session.query(Permission).first()

        assert_that(created_permission, has_properties(id=row.id,
                                                       name='rîghtcall1',
                                                       password='P$WDéẁ',
                                                       mode=1,
                                                       enabled=False,
                                                       description='description',
                                                       extensions=['123', '456']))

        assert_that(row, has_properties(name='rîghtcall1',
                                        passwd='P$WDéẁ',
                                        authorization=1,
                                        commented=1,
                                        description='description',
                                        rightcallextens=has_length(2)))

        assert_that(row.rightcallextens[0], has_properties(rightcallid=row.id,
                                                           exten='123'))
        assert_that(row.rightcallextens[1], has_properties(rightcallid=row.id,
                                                           exten='456'))


class TestEdit(TestPermission):

    def test_edit_all_fields(self):
        permission = permission_dao.create(Permission(name='rîghtcall1',
                                                      password='P$WDéẁ',
                                                      mode=0,
                                                      enabled=True,
                                                      description='tototo',
                                                      extensions=['123', '456']))

        permission = permission_dao.get(permission.id)
        permission.name = 'denỳallfriends'
        permission.password = 'Alhahlalahl'
        permission.mode = 1
        permission.enabled = False
        permission.description = 'description'
        permission.extensions = ['789', '321', '654']

        permission_dao.edit(permission)

        row = self.session.query(Permission).first()

        assert_that(row, has_properties(name='denỳallfriends',
                                        passwd='Alhahlalahl',
                                        authorization=1,
                                        commented=1,
                                        description='description',
                                        rightcallextens=has_length(3)))

        assert_that(row.rightcallextens[0], has_properties(rightcallid=row.id,
                                                           exten='789'))
        assert_that(row.rightcallextens[1], has_properties(rightcallid=row.id,
                                                           exten='321'))
        assert_that(row.rightcallextens[2], has_properties(rightcallid=row.id,
                                                           exten='654'))

    def test_edit_set_fields_to_null(self):
        permission = permission_dao.create(Permission(name='rîghtcall1',
                                                      password='P$WDéẁ',
                                                      mode=0,
                                                      enabled=True,
                                                      description='tototo',
                                                      extensions=['123', '456']))

        permission = permission_dao.get(permission.id)
        permission.password = None
        permission.description = None

        permission_dao.edit(permission)

        row = self.session.query(Permission).first()

        assert_that(row, has_properties(passwd='',
                                        description=none()))


class TestDelete(TestPermission):

    def test_delete(self):
        permission = permission_dao.create(Permission(name='Delete'))
        permission = permission_dao.get(permission.id)

        permission_dao.delete(permission)

        row = self.session.query(Permission).first()
        assert_that(row, none())

    def test_delete_references_to_other_tables(self):
        user = self.add_user()
        group = self.add_group()
        incall = self.add_incall()
        outcall = self.add_outcall()
        permission = permission_dao.create(Permission(name='Delete'))
        self.add_right_call_member(rightcallid=permission.id, type='user', typeval=str(user.id))
        self.add_right_call_member(rightcallid=permission.id, type='group', typeval=str(group.id))
        self.add_right_call_member(rightcallid=permission.id, type='incall', typeval=str(incall.id))
        self.add_right_call_member(rightcallid=permission.id, type='outcall', typeval=str(outcall.id))

        permission_dao.delete(permission)

        assert_that(self.session.query(RightCallMember).first(), none())

    def add_right_call_member(self, **kwargs):
        member = RightCallMember(**kwargs)
        self.session.add(member)
        self.session.flush()
        return member
