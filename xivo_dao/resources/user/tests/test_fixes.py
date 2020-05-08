# -*- coding: utf-8 -*-
# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, equal_to

from xivo_dao.alchemy.endpoint_sip import EndpointSIP
from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.resources.user.fixes import UserFixes


class TestUserFixes(DAOTestCase):

    def setUp(self):
        super(TestUserFixes, self).setUp()
        self.fixes = UserFixes(self.session)

    def test_given_user_has_no_extension_then_fixes_pass(self):
        user = self.add_user()
        self.fixes.fix(user.id)

    def test_given_user_has_multiple_lines_then_all_sip_lines_updated(self):
        user = self.add_user(callerid='"John Smith" <1000>')
        sip1 = self.add_endpoint_sip(caller_id='"Roger Rabbit" <2000>')
        sip2 = self.add_endpoint_sip(caller_id='"Jon Snow" <3000>')

        line1 = self.add_line(endpoint_sip_uuid=sip1.uuid)
        line2 = self.add_line(endpoint_sip_uuid=sip2.uuid)

        self.add_user_line(user_id=user.id, line_id=line1.id,
                           main_user=True, main_line=False)
        self.add_user_line(user_id=user.id, line_id=line2.id,
                           main_user=True, main_line=True)

        self.fixes.fix(user.id)

        sip = self.session.query(EndpointSIP).filter(EndpointSIP.uuid == sip1.uuid).first()
        assert_that(sip.caller_id, equal_to(user.callerid))

        sip = self.session.query(EndpointSIP).filter(EndpointSIP.uuid == sip2.uuid).first()
        assert_that(sip.caller_id, equal_to(user.callerid))

    def test_given_user_has_multiple_lines_then_all_sccp_lines_updated(self):
        user = self.add_user(callerid='"John Smith" <1000>')
        sccp1 = self.add_sccpline(cid_name="Roger Rabbit", cid_num="2000")
        sccp2 = self.add_sccpline(cid_name="Jon Snow", cid_num="3000")

        line1 = self.add_line(endpoint_sccp_id=sccp1.id)
        line2 = self.add_line(endpoint_sccp_id=sccp2.id)

        self.add_user_line(user_id=user.id, line_id=line1.id,
                           main_user=True, main_line=False)
        self.add_user_line(user_id=user.id, line_id=line2.id,
                           main_user=True, main_line=True)

        self.fixes.fix(user.id)

        sccp = self.session.query(SCCPLine).filter(SCCPLine.id == sccp1.id).first()
        assert_that(sccp.cid_name, equal_to("John Smith"))

        sccp = self.session.query(SCCPLine).filter(SCCPLine.id == sccp2.id).first()
        assert_that(sccp.cid_name, equal_to("John Smith"))

    def test_given_line_has_multiple_users_then_main_sip_line_updated(self):
        main_user = self.add_user(callerid='"John Smith" <1000>')
        other_user = self.add_user(callerid='"George Green" <1001>')
        sip = self.add_endpoint_sip(caller_id='"Roger Rabbit" <2000>')
        line = self.add_line(endpoint_sip_uuid=sip.uuid)
        self.add_user_line(user_id=main_user.id, line_id=line.id,
                           main_user=True, main_line=True)
        self.add_user_line(user_id=other_user.id, line_id=line.id,
                           main_user=False, main_line=True)

        self.fixes.fix(main_user.id)
        self.fixes.fix(other_user.id)

        sip = self.session.query(EndpointSIP).first()
        assert_that(sip.caller_id, equal_to(main_user.callerid))

    def test_given_line_has_multiple_users_then_sccp_caller_id_updated(self):
        main_user = self.add_user(callerid='"John Smith" <1000>')
        other_user = self.add_user(callerid='"George Green" <1000>')
        sccp = self.add_sccpline(cid_name="Roger Rabbit", cid_num="2000")
        line = self.add_line(endpoint_sccp_id=sccp.id)
        self.add_user_line(user_id=main_user.id, line_id=line.id,
                           main_user=True, main_line=True)
        self.add_user_line(user_id=other_user.id, line_id=line.id,
                           main_user=False, main_line=True)

        self.fixes.fix(main_user.id)
        self.fixes.fix(other_user.id)

        sccp = self.session.query(SCCPLine).first()
        assert_that(sccp.cid_name, equal_to("John Smith"))
        assert_that(sccp.cid_num, equal_to("1000"))
