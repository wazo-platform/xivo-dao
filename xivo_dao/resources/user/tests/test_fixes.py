# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
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

from hamcrest import assert_that, equal_to

from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.alchemy.voicemail import Voicemail
from xivo_dao.alchemy.extension import Extension
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.resources.user.fixes import UserFixes


class TestFixes(DAOTestCase):

    def setUp(self):
        super(TestFixes, self).setUp()
        self.fixes = UserFixes(self.session)

    def test_given_user_has_no_line_or_voicemail_then_fixes_pass(self):
        user = self.add_user()
        self.fixes.fix_user(user.id)

    def test_given_user_has_sip_line_then_sip_caller_id_updated(self):
        user = self.add_user(callerid='"John Smith" <1000>')
        sip = self.add_usersip(callerid='"Roger Rabbit" <2000>')
        line = self.add_line(protocol='sip', protocolid=sip.id)
        self.add_user_line(user_id=user.id, line_id=line.id,
                           main_user=True, main_line=True)

        self.fixes.fix_user(user.id)

        sip = self.session.query(UserSIP).first()
        assert_that(sip.callerid, equal_to(user.callerid))

    def test_given_user_has_sip_line_then_xivo_userid_updated(self):
        user = self.add_user(callerid='"John Smith" <1000>')
        sip = self.add_usersip(callerid='"Roger Rabbit" <2000>')
        line = self.add_line(protocol='sip', protocolid=sip.id)
        self.add_user_line(user_id=user.id, line_id=line.id,
                           main_user=True, main_line=True)

        self.fixes.fix_user(user.id)

        sip = self.session.query(UserSIP).first()
        assert_that(sip.setvar, equal_to('XIVO_USERID={}'.format(user.id)))

    def test_given_line_has_multiple_users_then_main_sip_line_updated(self):
        main_user = self.add_user(callerid='"John Smith" <1000>')
        other_user = self.add_user(callerid='"George Green" <1001>')
        sip = self.add_usersip(callerid='"Roger Rabbit" <2000>')
        line = self.add_line(protocol='sip', protocolid=sip.id)
        self.add_user_line(user_id=main_user.id, line_id=line.id,
                           main_user=True, main_line=True)
        self.add_user_line(user_id=other_user.id, line_id=line.id,
                           main_user=False, main_line=True)

        self.fixes.fix_user(main_user.id)
        self.fixes.fix_user(other_user.id)

        sip = self.session.query(UserSIP).first()
        assert_that(sip.callerid, equal_to(main_user.callerid))
        assert_that(sip.setvar, equal_to('XIVO_USERID={}'.format(main_user.id)))

    def test_given_user_has_sccp_line_then_sccp_caller_id_updated(self):
        user = self.add_user(callerid='"John Smith" <1000>')
        sccp = self.add_sccpline(cid_name="Roger Rabbit", cid_num="2000")
        line = self.add_line(protocol='sccp', protocolid=sccp.id)
        self.add_user_line(user_id=user.id, line_id=line.id,
                           main_user=True, main_line=True)

        self.fixes.fix_user(user.id)

        sccp = self.session.query(SCCPLine).first()
        assert_that(sccp.cid_name, equal_to("John Smith"))
        assert_that(sccp.cid_num, equal_to("1000"))

    def test_given_line_has_multiple_users_then_sccp_caller_id_updated(self):
        main_user = self.add_user(callerid='"John Smith" <1000>')
        other_user = self.add_user(callerid='"George Green" <1000>')
        sccp = self.add_sccpline(cid_name="Roger Rabbit", cid_num="2000")
        line = self.add_line(protocol='sccp', protocolid=sccp.id)
        self.add_user_line(user_id=main_user.id, line_id=line.id,
                           main_user=True, main_line=True)
        self.add_user_line(user_id=other_user.id, line_id=line.id,
                           main_user=False, main_line=True)

        self.fixes.fix_user(main_user.id)
        self.fixes.fix_user(other_user.id)

        sccp = self.session.query(SCCPLine).first()
        assert_that(sccp.cid_name, equal_to("John Smith"))
        assert_that(sccp.cid_num, equal_to("1000"))

    def test_given_user_has_voicemail_then_voicemail_name_updated(self):
        voicemail = self.add_voicemail(fullname="Roger Rabbit")
        user = self.add_user(firstname="John", lastname="Smith", voicemailid=voicemail.uniqueid)

        self.fixes.fix_user(user.id)

        voicemail = self.session.query(Voicemail).first()
        assert_that(voicemail.fullname, equal_to("John Smith"))

    def test_given_user_has_extension_then_destination_updated(self):
        extension = self.add_extension()
        line = self.add_line()
        user = self.add_user()
        self.add_user_line(user_id=user.id, line_id=line.id, extension_id=extension.id)

        self.fixes.fix_user(user.id)

        extension = self.session.query(Extension).first()
        assert_that(extension.type, equal_to('user'))
        assert_that(extension.typeval, equal_to(str(user.id)))

    def test_given_line_has_multiple_users_then_main_extension_updated(self):
        extension = self.add_extension()
        line = self.add_line()
        main_user = self.add_user()
        other_user = self.add_user()
        self.add_user_line(user_id=main_user.id, line_id=line.id, extension_id=extension.id,
                           main_user=True, main_line=True)
        self.add_user_line(user_id=other_user.id, line_id=line.id, extension_id=extension.id,
                           main_user=False, main_line=True)

        self.fixes.fix_user(main_user.id)
        self.fixes.fix_user(other_user.id)

        extension = self.session.query(Extension).first()
        assert_that(extension.type, equal_to('user'))
        assert_that(extension.typeval, equal_to(str(main_user.id)))
