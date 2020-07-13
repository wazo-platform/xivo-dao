# -*- coding: utf-8 -*-
# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

from hamcrest import assert_that, equal_to, none

from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.alchemy.endpoint_sip import EndpointSIP
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.alchemy.usercustom import UserCustom
from xivo_dao.resources.line.fixes import LineFixes
from xivo_dao.tests.test_dao import DAOTestCase


class TestLineFixes(DAOTestCase):

    def setUp(self):
        super(TestLineFixes, self).setUp()
        self.fixes = LineFixes(self.session)

    # TODO(pc-m): remove this fix
    # def test_when_update_context_extension_then_sip_context_is_updated(self):
    #     context = self.add_context()
    #     other_context = self.add_context()
    #     sip = self.add_endpoint_sip(context={'id': context.id})
    #     line = self.add_line(endpoint_sip_uuid=sip.uuid, context=context.name)
    #     extension = self.add_extension(exten="1000", context=context.name)
    #     self.add_line_extension(line_id=line.id, extension_id=extension.id)

    #     extension.context = other_context.name
    #     self.fixes.fix(line.id)

    #     sip = self.session.query(EndpointSIP).first()
    #     line = self.session.query(Line).first()

    #     assert_that(sip.context, equal_to(other_context))
    #     assert_that(line.context, equal_to(other_context.name))

    def test_given_user_only_has_caller_name_then_sip_caller_id_updated(self):
        user = self.add_user(callerid='"Jôhn Smith"')
        sip = self.add_endpoint_sip(caller_id='"Rôger Rabbit" <2000>')
        line = self.add_line(endpoint_sip_uuid=sip.uuid)
        self.add_user_line(
            user_id=user.id, line_id=line.id, main_user=True, main_line=True,
        )

        self.fixes.fix(line.id)

        sip = self.session.query(EndpointSIP).first()
        assert_that(sip.caller_id, equal_to(user.callerid))

    def test_given_user_has_caller_name_and_number_then_sip_caller_id_updated(self):
        user = self.add_user(callerid='"Jôhn Smith" <1000>')
        sip = self.add_endpoint_sip(caller_id='"Rôger Rabbit" <2000>')
        line = self.add_line(endpoint_sip_uuid=sip.uuid)
        self.add_user_line(
            user_id=user.id, line_id=line.id, main_user=True, main_line=True,
        )

        self.fixes.fix(line.id)

        sip = self.session.query(EndpointSIP).first()
        assert_that(sip.caller_id, equal_to(user.callerid))

    def test_given_user_has_caller_name_and_extension_then_sip_caller_id_updated(self):
        user = self.add_user(callerid='"Jôhn Smith"')
        sip = self.add_endpoint_sip(caller_id='"Rôger Rabbit" <2000>')
        line = self.add_line(endpoint_sip_uuid=sip.uuid)
        extension = self.add_extension(exten="3000", context="default")
        self.add_user_line(
            user_id=user.id, line_id=line.id, main_user=True, main_line=True,
        )
        self.add_line_extension(line_id=line.id, extension_id=extension.id)

        self.fixes.fix(line.id)

        sip = self.session.query(EndpointSIP).first()
        assert_that(sip.caller_id, equal_to('"Jôhn Smith" <3000>'))

    def test_given_user_has_caller_number_and_extension_then_caller_number_updated(self):
        user = self.add_user(callerid='"Jôhn Smith" <1000>')
        sip = self.add_endpoint_sip(caller_id='"Rôger Rabbit" <2000>')
        line = self.add_line(endpoint_sip_uuid=sip.uuid)
        extension = self.add_extension(exten="3000", context="default")
        self.add_user_line(
            user_id=user.id, line_id=line.id, main_user=True, main_line=True,
        )
        self.add_line_extension(line_id=line.id, extension_id=extension.id)

        self.fixes.fix(line.id)

        sip = self.session.query(EndpointSIP).first()
        assert_that(sip.caller_id, equal_to('"Jôhn Smith" <1000>'))

    def test_given_user_has_sip_line_then_context_updated(self):
        context = self.add_context()
        user = self.add_user(callerid='"Jôhn Smith" <1000>')
        sip = self.add_endpoint_sip(caller_id='"Rôger Rabbit" <2000>')
        line = self.add_line(endpoint_sip_uuid=sip.uuid, context=context.name)
        self.add_user_line(
            user_id=user.id, line_id=line.id, main_user=True, main_line=True,
        )

        self.fixes.fix(line.id)

        sip = self.session.query(EndpointSIP).first()
        assert_that(sip.context, equal_to(context))

    def test_given_user_only_has_caller_name_then_sccp_caller_id_updated(self):
        user = self.add_user(callerid='"Jôhn Smith"')
        sccp = self.add_sccpline(cid_name="Rôger Rabbit", cid_num="2000")
        line = self.add_line(endpoint_sccp_id=sccp.id)
        self.add_user_line(user_id=user.id, line_id=line.id,
                           main_user=True, main_line=True)

        self.fixes.fix(line.id)

        sccp = self.session.query(SCCPLine).first()
        assert_that(sccp.cid_name, equal_to('Jôhn Smith'))
        assert_that(sccp.cid_num, equal_to(''))

    def test_given_user_has_caller_name_and_number_then_sccp_caller_id_updated(self):
        user = self.add_user(callerid='"Jôhn Smith" <1000>')
        sccp = self.add_sccpline(cid_name="Rôger Rabbit", cid_num="2000")
        line = self.add_line(endpoint_sccp_id=sccp.id)
        self.add_user_line(user_id=user.id, line_id=line.id,
                           main_user=True, main_line=True)

        self.fixes.fix(line.id)

        sccp = self.session.query(SCCPLine).first()
        assert_that(sccp.cid_name, equal_to('Jôhn Smith'))
        assert_that(sccp.cid_num, equal_to('1000'))

    def test_given_user_has_caller_name_and_extension_then_sccp_caller_id_updated(self):
        user = self.add_user(callerid='"Jôhn Smith"')
        sccp = self.add_sccpline(cid_name="Rôger Rabbit", cid_num="2000")
        line = self.add_line(endpoint_sccp_id=sccp.id)
        extension = self.add_extension(exten="3000", context="default")
        self.add_user_line(user_id=user.id, line_id=line.id,
                           main_user=True, main_line=True)
        self.add_line_extension(line_id=line.id, extension_id=extension.id)

        self.fixes.fix(line.id)

        sccp = self.session.query(SCCPLine).first()
        assert_that(sccp.cid_name, equal_to('Jôhn Smith'))
        assert_that(sccp.cid_num, equal_to('3000'))

    def test_given_user_has_caller_number_and_extension_then_sccp_caller_number_updated(self):
        user = self.add_user(callerid='"Jôhn Smith" <1000>')
        sccp = self.add_sccpline(cid_name="Rôger Rabbit", cid_num="2000")
        line = self.add_line(endpoint_sccp_id=sccp.id)
        extension = self.add_extension(exten="3000", context="default")
        self.add_user_line(user_id=user.id, line_id=line.id,
                           main_user=True, main_line=True)
        self.add_line_extension(line_id=line.id, extension_id=extension.id)

        self.fixes.fix(line.id)

        sccp = self.session.query(SCCPLine).first()
        assert_that(sccp.cid_name, equal_to('Jôhn Smith'))
        assert_that(sccp.cid_num, equal_to('3000'))

    def test_given_sccp_line_has_user_and_extension_then_context_updated(self):
        user = self.add_user(callerid='"Jôhn Smith" <1000>')
        sccp = self.add_sccpline(cid_name="Rôger Rabbit", cid_num="2000")
        line = self.add_line(endpoint_sccp_id=sccp.id)
        extension = self.add_extension(exten="3000", context="default")
        self.add_user_line(user_id=user.id, line_id=line.id,
                           main_user=True, main_line=True)
        self.add_line_extension(line_id=line.id, extension_id=extension.id)

        self.fixes.fix(line.id)

        sccp = self.session.query(SCCPLine).first()
        assert_that(sccp.context, equal_to('default'))

    def test_given_line_has_multiple_users_then_sccp_caller_id_updated(self):
        main_user = self.add_user(callerid='"Jôhn Smith" <1000>')
        other_user = self.add_user(callerid='"Géorge Green" <1001>')
        sccp = self.add_sccpline(cid_name="Rôger Rabbit", cid_num="2000")
        line = self.add_line(endpoint_sccp_id=sccp.id)
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
        self.add_line_extension(line_id=line.id, extension_id=extension.id)

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
        sip = self.add_endpoint_sip(caller_id='"Rôger Rabbit" <2000>', name="sipname")
        line = self.add_line(name="linename", endpoint_sip_uuid=sip.uuid)

        self.fixes.fix(line.id)

        line = self.session.query(Line).first()
        assert_that(line.name, equal_to('sipname'))

    def test_given_line_has_sccp_name_then_line_name_updated(self):
        sccp = self.add_sccpline(name="1234")
        line = self.add_line(name="linename", endpoint_sccp_id=sccp.id)

        self.fixes.fix(line.id)

        line = self.session.query(Line).first()
        assert_that(line.name, equal_to('1234'))

    def test_given_line_has_no_associated_name_then_name_removed(self):
        line = self.add_line(name="linename")

        self.fixes.fix(line.id)

        line = self.session.query(Line).first()
        assert_that(line.name, none())

    def test_given_line_is_associated_to_custom_protocol_then_context_and_interface_updated(self):
        custom = self.add_usercustom(context=None, interface='custom/abcdef')
        line = self.add_line(endpoint_custom_id=custom.id, context='default')

        self.fixes.fix(line.id)

        custom = self.session.query(UserCustom).first()
        line = self.session.query(Line).first()

        assert_that(custom.context, equal_to('default'))
        assert_that(line.name, equal_to('custom/abcdef'))

    def test_given_line_has_sip_name_then_queue_member_interface_updated(self):
        sip = self.add_endpoint_sip(name='abcdef')
        line = self.add_line(endpoint_sip_uuid=sip.uuid)
        user = self.add_user()
        self.add_user_line(user_id=user.id, line_id=line.id)
        self.add_queue_member(usertype='user', userid=user.id, interface='SIP/default')

        self.fixes.fix(line.id)

        queue_member = self.session.query(QueueMember).first()

        assert_that(queue_member.interface, equal_to('SIP/abcdef'))

    def test_given_line_has_sccp_name_then_queue_member_interface_updated(self):
        sccp = self.add_sccpline(name='abcdef')
        line = self.add_line(endpoint_sccp_id=sccp.id)
        user = self.add_user()
        self.add_user_line(user_id=user.id, line_id=line.id)
        self.add_queue_member(usertype='user', userid=user.id, interface='SCCP/default')

        self.fixes.fix(line.id)

        queue_member = self.session.query(QueueMember).first()

        assert_that(queue_member.interface, equal_to('SCCP/abcdef'))

    def test_given_line_has_custom_interface_then_queue_member_interface_updated(self):
        custom = self.add_usercustom(interface='custom/abcdef')
        line = self.add_line(endpoint_custom_id=custom.id)
        user = self.add_user()
        self.add_user_line(user_id=user.id, line_id=line.id)
        self.add_queue_member(usertype='user', userid=user.id, interface='custom/invalid')

        self.fixes.fix(line.id)

        queue_member = self.session.query(QueueMember).first()

        assert_that(queue_member.interface, equal_to('custom/abcdef'))

    def test_given_second_line_then_queue_member_interface_updated(self):
        sip1 = self.add_endpoint_sip()
        line1 = self.add_line(endpoint_sip_uuid=sip1.uuid)
        sip2 = self.add_endpoint_sip(name='abcdef')
        line2 = self.add_line(endpoint_sip_uuid=sip2.uuid)
        user = self.add_user()
        self.add_user_line(user_id=user.id, line_id=line1.id, main_line=True)
        self.add_user_line(user_id=user.id, line_id=line2.id, main_line=False)
        self.add_queue_member(usertype='user', userid=user.id, interface='SIP/default')

        self.fixes.fix(line2.id)

        queue_member = self.session.query(QueueMember).first()

        assert_that(queue_member.interface, equal_to('SIP/default'))

    def test_given_queuemember_local_without_extension_then_queue_member_iface_not_updated(self):
        sip = self.add_endpoint_sip(name='abcdef')
        line = self.add_line(endpoint_sip_uuid=sip.uuid)
        user = self.add_user()
        self.add_user_line(user_id=user.id, line_id=line.id)
        self.add_queue_member(
            usertype='user', userid=user.id, interface='SIP/default', channel='Local',
        )

        self.fixes.fix(line.id)

        queue_member = self.session.query(QueueMember).first()

        assert_that(queue_member.interface, equal_to('SIP/default'))

    def test_given_queuemember_local_with_extension_then_queue_member_interface_updated(self):
        sip = self.add_endpoint_sip(name='abcdef')
        line = self.add_line(endpoint_sip_uuid=sip.uuid)
        user = self.add_user()
        extension = self.add_extension(exten='12345', context='wonderland')
        self.add_user_line(user_id=user.id, line_id=line.id)
        self.add_line_extension(line_id=line.id, extension_id=extension.id)
        self.add_queue_member(
            usertype='user', userid=user.id, interface='SIP/default', channel='Local',
        )

        self.fixes.fix(line.id)

        queue_member = self.session.query(QueueMember).first()

        assert_that(queue_member.interface, equal_to('Local/12345@wonderland'))
