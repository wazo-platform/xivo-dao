# -*- coding: utf-8 -*-
# Copyright (C) 2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import assert_that, none, contains, is_not, equal_to

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.resources.func_key.tests.test_helpers import FuncKeyHelper

from xivo_dao.resources.func_key.model import Forward
from xivo_dao.resources.func_key import dao
from xivo_dao.resources.func_key.persistor import DestinationPersistor
from xivo_dao.alchemy.func_key import FuncKey as FuncKeySchema
from xivo_dao.alchemy.func_key_mapping import FuncKeyMapping


class TestFuncKeyDao(DAOTestCase, FuncKeyHelper):

    def setUp(self):
        super(TestFuncKeyDao, self).setUp()
        self.setup_funckeys()
        self.persistor = DestinationPersistor(self.session)


class TestCreateUserDestination(TestFuncKeyDao):

    def test_given_user_destination_then_func_key_created(self):
        user_row = self.add_user()

        self.persistor.create_user_destination(user_row)

        user_destination_row = self.find_destination('user', user_row.id)
        self.assert_func_key_row_created(user_destination_row)

    def assert_func_key_row_created(self, destination_row):
        assert_that(destination_row, is_not(none()))

        row = (self.session.query(FuncKeySchema)
               .filter(FuncKeySchema.id == destination_row.func_key_id)
               .first())
        assert_that(row, is_not(none()))


class TestDeleteUserDestination(TestFuncKeyDao):

    def test_given_user_destination_when_deleting_then_user_func_key_deleted(self):
        user_row = self.add_user()
        destination_row = self.add_user_destination(user_row.id)

        self.persistor.delete_user_destination(user_row)

        self.assert_func_key_deleted(destination_row.func_key_id)
        self.assert_destination_deleted('user', destination_row.user_id)

    def test_given_func_keys_in_template_when_deleting_then_func_keys_removed_from_template(self):
        template_row = self.add_func_key_template()
        user_row = self.add_user()

        user_destination_row = self.add_user_destination(user_row.id)
        self.add_func_key_mapping(template_id=template_row.id,
                                  func_key_id=user_destination_row.func_key_id,
                                  destination_type_id=user_destination_row.destination_type_id,
                                  position=1)

        bsfilter_row = self.add_bsfilter()
        member_row = self.add_filter_member(bsfilter_row.id, user_row.id, 'secretary')
        bs_destination_row = self.add_bsfilter_destination(member_row.id)
        self.add_func_key_mapping(template_id=template_row.id,
                                  func_key_id=bs_destination_row.func_key_id,
                                  destination_type_id=bs_destination_row.destination_type_id,
                                  position=2)

        self.persistor.delete_user_destination(user_row)

        self.assert_template_empty(template_row)

    def test_given_bsfilter_destination_when_deleting_then_bsfilter_func_key_deleted(self):
        user_row = self.add_user()
        self.add_user_destination(user_row.id)
        bsfilter_row = self.add_bsfilter()
        member_row = self.add_filter_member(bsfilter_row.id, user_row.id, 'secretary')
        destination_row = self.add_bsfilter_destination(member_row.id)

        self.persistor.delete_user_destination(user_row)

        self.assert_func_key_deleted(destination_row.func_key_id)
        self.assert_destination_deleted('bsfilter', destination_row.filtermember_id)

    def assert_func_key_deleted(self, func_key_id):
        row = (self.session.query(FuncKeySchema)
               .filter(FuncKeySchema.id == func_key_id)
               .first())
        assert_that(row, none())

    def assert_template_empty(self, template_row):
        count = (self.session.query(FuncKeyMapping)
                 .filter_by(template_id=template_row.id)
                 .count())

        assert_that(count, equal_to(0))


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
