# -*- coding: UTF-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from hamcrest import assert_that
from hamcrest import empty
from hamcrest import equal_to
from hamcrest import none
from hamcrest import not_
from hamcrest import contains
from hamcrest import has_items
from hamcrest import has_property

from xivo_dao.alchemy.sccpline import SCCPLine as SCCP
from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.helpers.exception import InputError
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.resources.endpoint_sccp import dao
from xivo_dao.tests.test_dao import DAOTestCase

ALL_OPTIONS = [
    ["cid_name", "Jôhn Smith"],
    ["cid_num", "5551234567"],
    ["disallow", "all"],
    ["allow", "gsm,g729"],
]


class TestSccpDao(DAOTestCase):
    pass


class TestSccpEndpointDaoGet(TestSccpDao):

    def test_given_no_rows_then_raises_error(self):
        self.assertRaises(NotFoundError, dao.get, 1)

    def test_given_row_with_minimal_parameters_then_returns_model(self):
        row = self.add_sccpline(name='',
                                context='',
                                cid_name='',
                                cid_num='')

        sccp = dao.get(row.id)

        assert_that(sccp.id, equal_to(row.id))
        assert_that(sccp.options, contains())


class TestSccpEndpointDaoFind(TestSccpDao):

    def test_given_no_rows_then_returns_none(self):
        result = dao.find(1)
        assert_that(result, none())

    def test_given_row_with_minimal_parameters_then_returns_model(self):
        row = self.add_sccpline(name='',
                                context='',
                                cid_name='',
                                cid_num='')

        sccp = dao.find(row.id)

        assert_that(sccp.id, equal_to(row.id))
        assert_that(sccp.options, contains())


class TestSccpEndpointDaoSearch(TestSccpDao):

    def test_search(self):
        row = self.add_sccpline()

        search_result = dao.search()

        assert_that(search_result.total, equal_to(1))
        assert_that(search_result.items, contains(has_property('id', row.id)))


class TestSccpEndpointDaoCreate(TestSccpDao):

    def test_create_minimal_parameters(self):
        created_sccp = dao.create(SCCP())
        sccp_row = self.session.query(SCCP).first()

        assert_that(created_sccp.id, equal_to(sccp_row.id))
        assert_that(created_sccp.options, contains())

        assert_that(sccp_row.name, not_(empty()))
        assert_that(sccp_row.context, equal_to(''))
        assert_that(sccp_row.cid_name, equal_to(''))
        assert_that(sccp_row.cid_num, equal_to(''))
        assert_that(sccp_row.allow, none())
        assert_that(sccp_row.disallow, none())

    def test_create_all_parameters(self):
        options = [
            ["cid_name", "Jôhn Smith"],
            ["cid_num", "5551234567"],
            ["disallow", "all"],
            ["allow", "gsm,ulaw"],
        ]

        sccp = SCCP(options=options)

        created_sccp = dao.create(sccp)
        sccp_row = self.session.query(SCCP).first()

        assert_that(created_sccp.id, equal_to(sccp_row.id))
        assert_that(created_sccp.options, has_items(*options))

        assert_that(sccp_row.cid_name, equal_to('Jôhn Smith'))
        assert_that(sccp_row.cid_num, equal_to('5551234567'))
        assert_that(sccp_row.allow, equal_to("gsm,ulaw"))
        assert_that(sccp_row.disallow, equal_to("all"))

    def test_given_option_does_not_exist_then_raises_error(self):
        self.assertRaises(InputError, SCCP, options=[["invalid", "invalid"]])


class TestSccpEndpointDaoEdit(TestSccpDao):

    def test_given_allow_and_disallow_are_set_when_removed_then_database_updated(self):
        row = self.add_sccpline(context='',
                                name='',
                                cid_name='',
                                cid_num='',
                                allow="gsm,g729",
                                disallow="alaw,ulaw")

        sccp = dao.get(row.id)
        sccp.options = []
        dao.edit(sccp)

        row = self.session.query(SCCP).first()

        assert_that(row.allow, none())
        assert_that(row.disallow, none())

    def test_given_allow_and_disallow_are_when_altered_then_database_updated(self):
        row = self.add_sccpline(context='',
                                name='',
                                cid_name='',
                                cid_num='',
                                allow="gsm,g729",
                                disallow="alaw,ulaw")

        sccp = dao.get(row.id)
        sccp.options = [
            ["allow", "speex"],
            ["disallow", "opus"]
        ]
        dao.edit(sccp)

        row = self.session.query(SCCP).first()

        assert_that(row.allow, "speex")
        assert_that(row.disallow, "opus")

    def test_given_cid_name_and_num_set_when_removed_then_cid_name_and_num_not_deleted(self):
        row = self.add_sccpline(context='',
                                name='',
                                cid_name='Jôhn Smith',
                                cid_num='5551234567')

        sccp = dao.get(row.id)
        sccp.options = []
        dao.edit(sccp)

        row = self.session.query(SCCP).first()

        assert_that(row.cid_name, "Jôhn Smith")
        assert_that(row.cid_num, "5551234567")

    def test_given_cid_name_and_num_set_when_altered_then_cid_name_and_num_updated(self):
        row = self.add_sccpline(context='',
                                name='',
                                cid_name='Jôhn Smith',
                                cid_num='5551234567')

        sccp = dao.get(row.id)
        sccp.options = [
            ["cid_name", "Roger Wilkins"],
            ["cid_num", "4181234567"]
        ]
        dao.edit(sccp)

        row = self.session.query(SCCP).first()

        assert_that(row.cid_name, "Roger Wilkins")
        assert_that(row.cid_num, "4181234567")


class TestSipEndpointDaoDelete(TestSccpDao):

    def test_delete(self):
        row = self.add_sccpline(context='', name='')

        sccp = dao.get(row.id)
        dao.delete(sccp)

        row = self.session.query(SCCP).get(row.id)
        assert_that(row, none())

    def test_given_line_associated_to_sccp_when_deleted_then_line_dissociated(self):
        sccp = self.add_sccpline(context='default', name='1000')
        line = self.add_line(context='default', name='1000', number='1000',
                             protocol='sccp', protocolid=sccp.id)

        sccp = dao.get(sccp.id)
        dao.delete(sccp)

        line = self.session.query(Line).get(line.id)
        assert_that(line.endpoint, none())
        assert_that(line.endpoint_id, none())


class TestRelations(DAOTestCase):

    def test_line_relationship(self):
        sccp_row = self.add_sccpline()
        line_row = self.add_line()
        line_row.associate_endpoint(sccp_row)

        sccp = dao.get(sccp_row.id)
        assert_that(sccp, equal_to(sccp_row))
        assert_that(sccp.line, equal_to(line_row))
