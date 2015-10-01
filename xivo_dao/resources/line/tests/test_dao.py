# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

from hamcrest import assert_that
from hamcrest import equal_to
from hamcrest import is_not
from hamcrest import none
from hamcrest import has_length
from hamcrest import contains
from hamcrest import has_property

from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.resources.line import dao as line_dao
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.helpers.exception import NotFoundError


class TestLineDao(DAOTestCase):

    def add_line(self, **properties):
        properties.setdefault('context', 'default')
        properties.setdefault('provisioningid', 123456)
        line = Line(**properties)
        self.add_me(line)
        return line


class TestLineDaoGet(TestLineDao):

    def test_get_no_line(self):
        self.assertRaises(NotFoundError, line_dao.get, 666)

    def test_get_minimal_parameters(self):
        line_row = self.add_line(context='default',
                                 provisioningid=123456)

        line = line_dao.get(line_row.id)

        assert_that(line.id, equal_to(line_row.id))
        assert_that(line.context, equal_to(line_row.context))
        assert_that(line.provisioning_code, equal_to('123456'))
        assert_that(line.position, equal_to(1))
        assert_that(line.endpoint, none())
        assert_that(line.endpoint_id, none())
        assert_that(line.caller_id_name, none())
        assert_that(line.caller_id_num, none())

    def test_get_all_parameters(self):
        line_row = self.add_line(context='default',
                                 protocol='sip',
                                 protocolid=1234,
                                 provisioningid=123456,
                                 num=2)

        line = line_dao.get(line_row.id)

        assert_that(line.id, equal_to(line_row.id))
        assert_that(line.context, equal_to('default'))
        assert_that(line.position, equal_to(2))
        assert_that(line.provisioning_code, '123456')
        assert_that(line.endpoint, equal_to('sip'))
        assert_that(line.endpoint_id, equal_to(1234))

    def test_given_line_has_sip_endpoint_when_getting_then_line_has_caller_id(self):
        usersip_row = self.add_usersip(callerid='"John Smith" <1000>')
        line_row = self.add_line(protocol='sip',
                                 protocolid=usersip_row.id)

        line = line_dao.get(line_row.id)

        assert_that(line.caller_id_name, equal_to("John Smith"))
        assert_that(line.caller_id_num, equal_to("1000"))

    def test_given_line_has_sccp_endpoint_when_getting_then_line_has_caller_id(self):
        sccpline_row = self.add_sccpline(cid_name="John Smith",
                                         cid_num="1000")
        line_row = self.add_line(protocol='sccp',
                                 protocolid=sccpline_row.id)

        line = line_dao.get(line_row.id)

        assert_that(line.caller_id_name, equal_to("John Smith"))
        assert_that(line.caller_id_num, equal_to("1000"))


class TestLineDaoEdit(TestLineDao):

    def test_edit_all_parameters(self):
        line_row = self.add_line()

        line = line_dao.get(line_row.id)
        line.context = 'mycontext'
        line.endpoint = 'sccp'
        line.endpoint_id = 1234
        line.provisioning_code = '234567'
        line.position = 3

        line_dao.edit(line)

        edited_line = self.session.query(Line).get(line_row.id)
        assert_that(edited_line.id, equal_to(line.id))
        assert_that(edited_line.context, equal_to('mycontext'))
        assert_that(edited_line.endpoint, equal_to('sccp'))
        assert_that(edited_line.protocol, equal_to('sccp'))
        assert_that(edited_line.endpoint_id, equal_to(1234))
        assert_that(edited_line.protocolid, equal_to(1234))
        assert_that(edited_line.provisioning_code, equal_to('234567'))
        assert_that(edited_line.provisioningid, equal_to(234567))
        assert_that(edited_line.position, equal_to(3))

    def test_edit_null_parameters(self):
        line_row = self.add_line(endpoint='sccp',
                                 endpoint_id=1234)

        line = line_dao.get(line_row.id)
        line.endpoint = None
        line.endpoint_id = None

        line_dao.edit(line)

        edited_line = self.session.query(Line).get(line_row.id)
        assert_that(edited_line.id, equal_to(line.id))
        assert_that(edited_line.endpoint, none())
        assert_that(edited_line.protocol, none())
        assert_that(edited_line.endpoint_id, none())
        assert_that(edited_line.protocolid, none())

    def test_given_line_has_sip_endpoint_when_editing_then_usersip_updated(self):
        usersip_row = self.add_usersip(callerid='"John Smith" <1000>')
        line_row = self.add_line(protocol='sip',
                                 protocolid=usersip_row.id)

        line = line_dao.get(line_row.id)
        line.caller_id_name = "Roger Rabbit"
        line.caller_id_num = "2000"

        line_dao.edit(line)

        edited_usersip = self.session.query(UserSIP).get(usersip_row.id)
        assert_that(edited_usersip.callerid, equal_to('"Roger Rabbit" <2000>'))

    def test_given_line_has_sccp_endpoint_when_editing_then_usersip_updated(self):
        sccpline_row = self.add_sccpline(cid_name="John Smith",
                                         cid_num="1000")
        line_row = self.add_line(protocol='sccp',
                                 protocolid=sccpline_row.id)

        line = line_dao.get(line_row.id)
        line.caller_id_name = "Roger Rabbit"
        line.caller_id_num = "2000"

        line_dao.edit(line)

        edited_sccpline = self.session.query(SCCPLine).get(sccpline_row.id)
        assert_that(edited_sccpline.cid_name, equal_to("Roger Rabbit"))
        assert_that(edited_sccpline.cid_num, equal_to("2000"))


class TestLineCreate(DAOTestCase):

    def test_create_minimal_parameters(self):
        line = Line(context='default', provisioningid=123456)

        created_line = line_dao.create(line)

        assert_that(created_line.id, is_not(none()))
        assert_that(created_line.context, equal_to('default'))
        assert_that(created_line.position, equal_to(1))
        assert_that(created_line.endpoint, none())
        assert_that(created_line.endpoint_id, none())
        assert_that(created_line.provisioning_code, has_length(6))

    def test_create_all_parameters(self):
        line = Line(context='default',
                    endpoint='sip',
                    endpoint_id=1234,
                    provisioning_code='123456',
                    position=2)

        created_line = line_dao.create(line)

        assert_that(created_line.id, is_not(none()))
        assert_that(created_line.context, equal_to('default'))
        assert_that(created_line.position, equal_to(2))
        assert_that(created_line.endpoint, equal_to('sip'))
        assert_that(created_line.protocol, equal_to('sip'))
        assert_that(created_line.endpoint_id, equal_to(1234))
        assert_that(created_line.protocolid, equal_to(1234))
        assert_that(created_line.provisioning_code, equal_to('123456'))
        assert_that(created_line.provisioningid, equal_to(123456))


class TestLineDaoDelete(DAOTestCase):

    def test_delete(self):
        line_row = self.add_line()

        line_dao.delete(line_row)

        deleted_line = self.session.query(Line).get(line_row.id)
        assert_that(deleted_line, none())

    def test_given_line_has_sip_endpoint_when_deleting_then_sip_endpoint_deleted(self):
        usersip_row = self.add_usersip()
        line_row = self.add_line(protocol='sip',
                                 protocolid=usersip_row.id)

        line_dao.delete(line_row)

        deleted_sip = self.session.query(UserSIP).get(usersip_row.id)
        assert_that(deleted_sip, none())

    def test_given_line_has_sccp_endpoint_when_deleting_then_sccp_endpoint_deleted(self):
        sccpline_row = self.add_sccpline()
        line_row = self.add_line(protocol='sccp',
                                 protocolid=sccpline_row.id)

        line_dao.delete(line_row)

        deleted_sccp = self.session.query(SCCPLine).get(sccpline_row.id)
        assert_that(deleted_sccp, none())


class TestLineDaoSearch(DAOTestCase):

    def test_search(self):
        line1 = self.add_line(context='default',
                              provisioningid=123456)
        self.add_line(context='default',
                      provisioningid=234567)

        search_result = line_dao.search(search='123456')

        assert_that(search_result.total, equal_to(1))
        assert_that(search_result.items, contains(has_property('id', line1.id)))
