# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from __future__ import unicode_literals

from hamcrest import assert_that, equal_to, none

from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.alchemy.sccpdevice import SCCPDevice
from xivo_dao.alchemy.usercustom import UserCustom
from xivo_dao.resources.line.fixes import LineFixes
from xivo_dao.tests.test_dao import DAOTestCase


class TestLineFixes(DAOTestCase):

    def setUp(self):
        super(TestLineFixes, self).setUp()
        self.fixes = LineFixes(self.session)

    def test_given_user_only_has_caller_name_then_sip_caller_id_updated(self):
        user = self.add_user(callerid='"Jôhn Smith"')
        sip = self.add_usersip(callerid='"Rôger Rabbit" <2000>')
        line = self.add_line(protocol='sip', protocolid=sip.id)
        self.add_user_line(user_id=user.id, line_id=line.id,
                           main_user=True, main_line=True)

        self.fixes.fix(line.id)

        sip = self.session.query(UserSIP).first()
        assert_that(sip.callerid, equal_to(user.callerid))

    def test_given_user_has_caller_name_and_number_then_sip_caller_id_updated(self):
        user = self.add_user(callerid='"Jôhn Smith" <1000>')
        sip = self.add_usersip(callerid='"Rôger Rabbit" <2000>')
        line = self.add_line(protocol='sip', protocolid=sip.id)
        self.add_user_line(user_id=user.id, line_id=line.id,
                           main_user=True, main_line=True)

        self.fixes.fix(line.id)

        sip = self.session.query(UserSIP).first()
        assert_that(sip.callerid, equal_to(user.callerid))

    def test_given_user_has_caller_name_and_extension_then_sip_caller_id_updated(self):
        user = self.add_user(callerid='"Jôhn Smith"')
        sip = self.add_usersip(callerid='"Rôger Rabbit" <2000>')
        line = self.add_line(protocol='sip', protocolid=sip.id)
        extension = self.add_extension(exten="3000", context="default")
        self.add_user_line(user_id=user.id, line_id=line.id, extension_id=extension.id,
                           main_user=True, main_line=True)

        self.fixes.fix(line.id)

        sip = self.session.query(UserSIP).first()
        assert_that(sip.callerid, equal_to('"Jôhn Smith" <3000>'))

    def test_given_user_has_caller_number_and_extension_then_caller_number_updated(self):
        user = self.add_user(callerid='"Jôhn Smith" <1000>')
        sip = self.add_usersip(callerid='"Rôger Rabbit" <2000>')
        line = self.add_line(protocol='sip', protocolid=sip.id)
        extension = self.add_extension(exten="3000", context="default")
        self.add_user_line(user_id=user.id, line_id=line.id, extension_id=extension.id,
                           main_user=True, main_line=True)

        self.fixes.fix(line.id)

        sip = self.session.query(UserSIP).first()
        assert_that(sip.callerid, equal_to('"Jôhn Smith" <1000>'))

    def test_given_user_has_sip_line_then_xivo_userid_updated(self):
        user = self.add_user(callerid='"Jôhn Smith" <1000>')
        sip = self.add_usersip(callerid='"Rôger Rabbit" <2000>')
        line = self.add_line(protocol='sip', protocolid=sip.id)
        self.add_user_line(user_id=user.id, line_id=line.id,
                           main_user=True, main_line=True)

        self.fixes.fix(line.id)

        sip = self.session.query(UserSIP).first()
        assert_that(sip.setvar, equal_to('XIVO_USERID={}'.format(user.id)))

    def test_given_user_has_sip_line_then_context_updated(self):
        user = self.add_user(callerid='"Jôhn Smith" <1000>')
        sip = self.add_usersip(callerid='"Rôger Rabbit" <2000>')
        line = self.add_line(protocol='sip', protocolid=sip.id, context='mycontext')
        self.add_user_line(user_id=user.id, line_id=line.id,
                           main_user=True, main_line=True)

        self.fixes.fix(line.id)

        sip = self.session.query(UserSIP).first()
        assert_that(sip.context, equal_to('mycontext'))

    def test_given_user_only_has_caller_name_then_sccp_caller_id_updated(self):
        user = self.add_user(callerid='"Jôhn Smith"')
        sccp = self.add_sccpline(cid_name="Rôger Rabbit", cid_num="2000")
        line = self.add_line(protocol='sccp', protocolid=sccp.id)
        self.add_user_line(user_id=user.id, line_id=line.id,
                           main_user=True, main_line=True)

        self.fixes.fix(line.id)

        sccp = self.session.query(SCCPLine).first()
        assert_that(sccp.cid_name, equal_to('Jôhn Smith'))
        assert_that(sccp.cid_num, equal_to(''))

    def test_given_user_has_caller_name_and_number_then_sccp_caller_id_updated(self):
        user = self.add_user(callerid='"Jôhn Smith" <1000>')
        sccp = self.add_sccpline(cid_name="Rôger Rabbit", cid_num="2000")
        line = self.add_line(protocol='sccp', protocolid=sccp.id)
        self.add_user_line(user_id=user.id, line_id=line.id,
                           main_user=True, main_line=True)

        self.fixes.fix(line.id)

        sccp = self.session.query(SCCPLine).first()
        assert_that(sccp.cid_name, equal_to('Jôhn Smith'))
        assert_that(sccp.cid_num, equal_to('1000'))

    def test_given_user_has_caller_name_and_extension_then_sccp_caller_id_updated(self):
        user = self.add_user(callerid='"Jôhn Smith"')
        sccp = self.add_sccpline(cid_name="Rôger Rabbit", cid_num="2000")
        line = self.add_line(protocol='sccp', protocolid=sccp.id)
        extension = self.add_extension(exten="3000", context="default")
        self.add_user_line(user_id=user.id, line_id=line.id, extension_id=extension.id,
                           main_user=True, main_line=True)

        self.fixes.fix(line.id)

        sccp = self.session.query(SCCPLine).first()
        assert_that(sccp.cid_name, equal_to('Jôhn Smith'))
        assert_that(sccp.cid_num, equal_to('3000'))

    def test_given_user_has_caller_number_and_extension_then_sccp_caller_number_updated(self):
        user = self.add_user(callerid='"Jôhn Smith" <1000>')
        sccp = self.add_sccpline(cid_name="Rôger Rabbit", cid_num="2000")
        line = self.add_line(protocol='sccp', protocolid=sccp.id)
        extension = self.add_extension(exten="3000", context="default")
        self.add_user_line(user_id=user.id, line_id=line.id, extension_id=extension.id,
                           main_user=True, main_line=True)

        self.fixes.fix(line.id)

        sccp = self.session.query(SCCPLine).first()
        assert_that(sccp.cid_name, equal_to('Jôhn Smith'))
        assert_that(sccp.cid_num, equal_to('3000'))

    def test_given_sccp_line_has_user_and_extension_then_name_and_context_updated(self):
        user = self.add_user(callerid='"Jôhn Smith" <1000>')
        sccp = self.add_sccpline(cid_name="Rôger Rabbit", cid_num="2000")
        line = self.add_line(protocol='sccp', protocolid=sccp.id)
        extension = self.add_extension(exten="3000", context="default")
        self.add_user_line(user_id=user.id, line_id=line.id, extension_id=extension.id,
                           main_user=True, main_line=True)

        self.fixes.fix(line.id)

        sccp = self.session.query(SCCPLine).first()
        assert_that(sccp.name, equal_to('3000'))
        assert_that(sccp.context, equal_to('default'))

    def test_given_sccp_line_has_device_then_number_updated(self):
        user = self.add_user()
        sccp = self.add_sccpline(name='1000', context='default',
                                 cid_name="Rôger Rabbit", cid_num="2000")
        device = self.add_sccpdevice(line='1000')
        line = self.add_line(name='1000', number='1000', context='default',
                             protocol='sccp', protocolid=sccp.id)
        extension = self.add_extension(exten="2000", context="default")
        self.add_user_line(user_id=user.id, line_id=line.id, extension_id=extension.id,
                           main_user=True, main_line=True)

        self.fixes.fix(line.id)

        device = self.session.query(SCCPDevice).first()
        assert_that(device.line, equal_to('2000'))

    def test_given_line_has_multiple_users_then_sccp_caller_id_updated(self):
        main_user = self.add_user(callerid='"Jôhn Smith" <1000>')
        other_user = self.add_user(callerid='"Géorge Green" <1001>')
        sccp = self.add_sccpline(cid_name="Rôger Rabbit", cid_num="2000")
        line = self.add_line(protocol='sccp', protocolid=sccp.id)
        self.add_user_line(user_id=main_user.id, line_id=line.id,
                           main_user=True, main_line=True)
        self.add_user_line(user_id=other_user.id, line_id=line.id,
                           main_user=False, main_line=True)

        self.fixes.fix(line.id)

        sccp = self.session.query(SCCPLine).first()
        assert_that(sccp.cid_name, equal_to("Jôhn Smith"))
        assert_that(sccp.cid_num, equal_to("1000"))

    def test_given_extension_associated_to_line_then_number_and_context_updated(self):
        line = self.add_line(context="mycontext", number="2000")
        extension = self.add_extension(exten="1000", context="default")
        self.add_user_line(user_id=None, line_id=line.id, extension_id=extension.id)

        self.fixes.fix(line.id)

        line = self.session.query(Line).first()
        assert_that(line.number, equal_to('1000'))
        assert_that(line.context, equal_to('default'))

    def test_given_line_has_no_extension_then_number_removed(self):
        line = self.add_line(context="mycontext", number="2000")

        self.fixes.fix(line.id)

        line = self.session.query(Line).first()
        assert_that(line.number, none())
        assert_that(line.context, equal_to('mycontext'))

    def test_given_line_has_sip_name_then_line_name_updated(self):
        sip = self.add_usersip(callerid='"Rôger Rabbit" <2000>', name="sipname")
        line = self.add_line(name="linename", protocol='sip', protocolid=sip.id)

        self.fixes.fix(line.id)

        line = self.session.query(Line).first()
        assert_that(line.name, equal_to('sipname'))

    def test_given_line_has_sccp_name_then_line_name_updated(self):
        sccp = self.add_sccpline(name="1234")
        line = self.add_line(name="linename", protocol='sccp', protocolid=sccp.id)

        self.fixes.fix(line.id)

        line = self.session.query(Line).first()
        assert_that(line.name, equal_to('1234'))

    def test_given_line_has_no_associated_name_then_name_removed(self):
        line = self.add_line(name="linename")

        self.fixes.fix(line.id)

        line = self.session.query(Line).first()
        assert_that(line.name, none())

    def test_given_sip_protocol_is_no_longer_associated_then_protocol_removed(self):
        line = self.add_line(protocol='sip', protocolid=1234)

        self.fixes.fix(line.id)

        line = self.session.query(Line).first()
        assert_that(line.protocol, none())
        assert_that(line.protocolid, none())

    def test_given_line_is_associated_to_custom_protocol_then_context_and_interface_updated(self):
        custom = self.add_usercustom(context=None, interface='custom/abcdef')
        line = self.add_line(protocol='custom', protocolid=custom.id, context='default')

        self.fixes.fix(line.id)

        custom = self.session.query(UserCustom).first()
        line = self.session.query(Line).first()

        assert_that(custom.context, equal_to('default'))
        assert_that(line.name, equal_to('custom/abcdef'))

    def test_given_custom_protocol_is_no_longer_assocaited_then_protocol_removed(self):
        line = self.add_line(protocol='custom', protocolid=1234)

        self.fixes.fix(line.id)

        line = self.session.query(Line).first()
        assert_that(line.protocol, none())
        assert_that(line.protocolid, none())
