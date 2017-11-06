# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
#
# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from hamcrest import assert_that
from hamcrest import equal_to
from hamcrest import none
from hamcrest import contains
from hamcrest import has_property

from xivo_dao.alchemy.usercustom import UserCustom as Custom
from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.helpers.exception import NotFoundError, InputError
from xivo_dao.resources.endpoint_custom import dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestCustomDao(DAOTestCase):
    pass


class TestCustomEndpointDaoGet(TestCustomDao):

    def test_given_no_rows_then_raises_error(self):
        self.assertRaises(NotFoundError, dao.get, 1)

    def test_given_row_with_minimal_parameters_then_returns_model(self):
        row = self.add_usercustom(interface='custom/get')

        custom = dao.get(row.id)

        assert_that(custom.id, equal_to(row.id))
        assert_that(custom.interface, equal_to(row.interface))
        assert_that(custom.enabled, equal_to(True))


class TestCustomEndpointDaoFindBy(TestCustomDao):

    def test_given_column_does_not_exist_then_raises_error(self):
        self.assertRaises(InputError, dao.find_by, column=1)

    def test_given_row_with_value_does_not_exist_then_returns_null(self):
        result = dao.find_by(interface='abcd')
        assert_that(result, none())

    def test_find_by(self):
        sip = self.add_usercustom(interface='custom/custom')
        result = dao.find_by(interface='custom/custom')

        assert_that(result.id, equal_to(sip.id))


class TestCustomEndpointDaoFindAllBy(TestCustomDao):

    def test_given_column_does_not_exist_then_raises_error(self):
        self.assertRaises(InputError, dao.find_all_by, column=1)

    def test_given_row_with_value_does_not_exist_then_returns_empty_list(self):
        result = dao.find_all_by(interface='abcd')
        assert_that(result, contains())

    def test_find_all_by(self):
        custom1 = self.add_usercustom(interface='sip/interface')
        self.add_usercustom(interface='sccp/interface')

        result = dao.find_all_by(interface='sip/interface')

        assert_that(result, contains(custom1))


class TestCustomEndpointDaoSearch(TestCustomDao):

    def test_search(self):
        row = self.add_usercustom()

        search_result = dao.search()

        assert_that(search_result.total, equal_to(1))
        assert_that(search_result.items, contains(has_property('id', row.id)))


class TestCustomEndpointDaoCreate(TestCustomDao):

    def test_create_minimal_parameters(self):
        created_custom = dao.create(Custom(interface='custom/create'))
        custom_row = self.session.query(Custom).first()

        assert_that(created_custom.id, equal_to(custom_row.id))
        assert_that(created_custom.interface, equal_to('custom/create'))
        assert_that(created_custom.enabled, equal_to(True))

        assert_that(custom_row.name, none())
        assert_that(custom_row.commented, equal_to(0))
        assert_that(custom_row.protocol, equal_to('custom'))
        assert_that(custom_row.category, equal_to('user'))

    def test_create_all_parameters(self):
        created_custom = dao.create(Custom(interface='custom/create',
                                           enabled=False))

        custom_row = self.session.query(Custom).first()

        assert_that(created_custom.id, equal_to(custom_row.id))
        assert_that(created_custom.enabled, equal_to(False))

        assert_that(custom_row.commented, equal_to(1))


class TestCustomEndpointDaoEdit(TestCustomDao):

    def test_edit_all_parameters(self):
        custom_row = self.add_usercustom(interface='custom/beforeedit',
                                         commented=1)

        custom = dao.get(custom_row.id)
        custom.interface = 'custom/afteredit'
        custom.enabled = True

        dao.edit(custom)

        custom_row = self.session.query(Custom).first()

        assert_that(custom_row.id, equal_to(custom_row.id))
        assert_that(custom_row.interface, equal_to('custom/afteredit'))
        assert_that(custom_row.enabled, equal_to(True))
        assert_that(custom_row.commented, equal_to(0))


class TestCustomEndpointDaoDelete(TestCustomDao):

    def test_delete(self):
        row = self.add_usercustom()

        custom = dao.get(row.id)
        dao.delete(custom)

        row = self.session.query(Custom).get(row.id)
        assert_that(row, none())

    def test_given_line_associated_to_custom_when_deleted_then_line_dissociated(self):
        custom = self.add_usercustom(context='default')
        line = self.add_line(context='default', name='1000', number='1000',
                             protocol='custom', protocolid=custom.id)

        custom = dao.get(custom.id)
        dao.delete(custom)

        line = self.session.query(Line).get(line.id)
        assert_that(line.endpoint, none())
        assert_that(line.endpoint_id, none())


class TestRelations(DAOTestCase):

    def test_trunk_relationship(self):
        custom_row = self.add_usercustom()
        trunk_row = self.add_trunk()
        trunk_row.associate_endpoint(custom_row)

        custom = dao.get(custom_row.id)
        assert_that(custom, equal_to(custom_row))
        assert_that(custom.trunk, equal_to(trunk_row))

    def test_line_relationship(self):
        custom_row = self.add_usercustom()
        line_row = self.add_line()
        line_row.associate_endpoint(custom_row)

        custom = dao.get(custom_row.id)
        assert_that(custom, equal_to(custom_row))
        assert_that(custom.line, equal_to(line_row))
