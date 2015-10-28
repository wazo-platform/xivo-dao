# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from hamcrest import assert_that, none, contains, is_not, equal_to

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.resources.func_key.tests.test_helpers import FuncKeyHelper

from xivo_dao.resources.func_key.model import UserFuncKey, BSFilterFuncKey, Forward
from xivo_dao.resources.func_key import dao
from xivo_dao.alchemy.func_key import FuncKey as FuncKeySchema


class TestFuncKeyDao(DAOTestCase, FuncKeyHelper):

    def setUp(self):
        super(TestFuncKeyDao, self).setUp()
        self.setup_funckeys()


class TestFuncKeyCreate(TestFuncKeyDao):

    def test_given_user_destination_then_func_key_created(self):
        user_row = self.add_user()
        func_key = UserFuncKey(user_id=user_row.id)

        created_func_key = dao.create(func_key)

        user_destination_row = self.find_destination('user', user_row.id)
        self.assert_func_key_row_created(user_destination_row)
        assert_that(created_func_key.id, equal_to(user_destination_row.func_key_id))

    def test_given_bsfilter_destination_then_func_key_created(self):
        user_row = self.add_user()
        bsfilter_row = self.add_bsfilter()
        member_row = self.add_filter_member(bsfilter_row.id, user_row.id, role='secretary')

        func_key = BSFilterFuncKey(filter_id=bsfilter_row.id, secretary_id=user_row.id)

        created_func_key = dao.create(func_key)

        bsfilter_destination_row = self.find_destination('bsfilter', member_row.id)
        self.assert_func_key_row_created(bsfilter_destination_row)
        assert_that(created_func_key.id, equal_to(bsfilter_destination_row.func_key_id))

    def assert_func_key_row_created(self, destination_row):
        assert_that(destination_row, is_not(none()))

        row = (self.session.query(FuncKeySchema)
               .filter(FuncKeySchema.id == destination_row.func_key_id)
               .first())
        assert_that(row, is_not(none()))


class TestFuncKeyDelete(TestFuncKeyDao):

    def test_given_user_destination_then_func_key_deleted(self):
        destination_row = self.create_user_func_key()
        func_key = UserFuncKey(id=destination_row.func_key_id,
                               user_id=destination_row.user_id)

        dao.delete(func_key)

        self.assert_func_key_deleted(func_key.id)
        self.assert_destination_deleted('user', destination_row.user_id)

    def test_given_bsfilter_destination_then_func_key_deleted(self):
        filter_member_row, destination_row = self.create_bsfilter_func_key()
        func_key = BSFilterFuncKey(id=destination_row.func_key_id,
                                   filter_id=filter_member_row.callfilterid,
                                   secretary_id=int(filter_member_row.typeval))

        dao.delete(func_key)

        self.assert_func_key_deleted(func_key.id)
        self.assert_destination_deleted('bsfilter', destination_row.filtermember_id)

    def assert_func_key_deleted(self, func_key_id):
        row = (self.session.query(FuncKeySchema)
               .filter(FuncKeySchema.id == func_key_id)
               .first())
        assert_that(row, none())


class TestFindAllForwards(TestFuncKeyDao):

    def prepare_user_and_forward(self, exten, fwd_type, number=None):
        user_row = self.add_user()

        exten_row = self.add_extenfeatures(exten, fwd_type)
        forward_row = self.add_forward_destination(exten_row.id, number)
        self.add_func_key_mapping(func_key_id=forward_row.func_key_id,
                                  destination_type_id=forward_row.destination_type_id,
                                  template_id=user_row.func_key_private_template_id,
                                  position=1,
                                  blf=True)

        return user_row, forward_row

    def test_given_no_forwards_then_returns_empty_list(self):
        result = dao.find_all_forwards(1, 'unconditional')

        assert_that(result, contains())

    def test_given_unconditional_forward_then_list_contains_unconditional_forward(self):
        number = '1234'
        user_row, forward_row = self.prepare_user_and_forward('_*21.', 'fwdunc', number)

        result = dao.find_all_forwards(user_row.id, 'unconditional')

        assert_that(result, contains(Forward(user_id=user_row.id,
                                             type='unconditional',
                                             number=number)))

    def test_given_noanswer_forward_then_list_contains_noanswer_forward(self):
        number = '1234'
        user_row, forward_row = self.prepare_user_and_forward('_*22.', 'fwdrna', number)

        result = dao.find_all_forwards(user_row.id, 'noanswer')

        assert_that(result, contains(Forward(user_id=user_row.id,
                                             type='noanswer',
                                             number=number)))

    def test_given_busy_forward_then_list_contains_busy_forward(self):
        number = '1234'
        user_row, forward_row = self.prepare_user_and_forward('_*23.', 'fwdbusy', number)

        result = dao.find_all_forwards(user_row.id, 'busy')

        assert_that(result, contains(Forward(user_id=user_row.id,
                                             type='busy',
                                             number=number)))


class TestFindUserDestination(TestFuncKeyDao):

    def test_given_no_user_or_func_key_then_returns_none(self):
        result = dao.find_user_destination(1)

        assert_that(result, none())

    def test_given_user_with_func_key_destination_then_returns_user_func_key(self):
        user_func_key_row = self.create_user_func_key()
        expected = UserFuncKey(id=user_func_key_row.func_key_id,
                               user_id=user_func_key_row.user_id)

        result = dao.find_user_destination(user_func_key_row.user_id)

        assert_that(result, equal_to(expected))


class TestFindBSFilterDestinationForUser(TestFuncKeyDao):

    def test_given_no_bsfilter_then_returns_empty_list(self):
        result = dao.find_bsfilter_destinations_for_user(1)

        assert_that(result, contains())

    def test_given_user_is_secretary_then_returns_one_func_key(self):
        user_row = self.add_user_line_with_exten()
        callfilter_row = self.add_bsfilter()
        secretary_member_row = self.add_filter_member(callfilter_row.id, user_row.id, 'secretary')
        bsfilter_func_key_row = self.add_bsfilter_destination(secretary_member_row.id)

        expected = BSFilterFuncKey(id=bsfilter_func_key_row.func_key_id,
                                   secretary_id=user_row.id,
                                   filter_id=callfilter_row.id)

        result = dao.find_bsfilter_destinations_for_user(user_row.id)

        assert_that(result, contains(expected))
