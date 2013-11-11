# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Avencall
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

from hamcrest import assert_that, has_property, instance_of, equal_to, none

from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.callfilter import Callfilter
from xivo_dao.alchemy.callfiltermember import Callfiltermember
from xivo_dao.alchemy.contextinclude import ContextInclude
from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao.alchemy.ctiphonehintsgroup import CtiPhoneHintsGroup
from xivo_dao.alchemy.ctipresences import CtiPresences
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.extension import Extension as ExtensionSchema
from xivo_dao.alchemy.linefeatures import LineFeatures as LineSchema
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.phonefunckey import PhoneFunckey
from xivo_dao.alchemy.rightcallmember import RightCallMember
from xivo_dao.alchemy.schedulepath import SchedulePath
from xivo_dao.alchemy.sccpdevice import SCCPDevice as SCCPDeviceSchema
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.usersip import UserSIP as UserSIPSchema
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.voicemail import Voicemail as VoicemailSchema

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.data_handler.user_voicemail import dao as user_voicemail_dao
from xivo_dao.data_handler.user_voicemail.model import UserVoicemail
from xivo_dao.data_handler.exception import ElementNotExistsError
from xivo_dao.data_handler.user_voicemail.exception import UserVoicemailNotExistsError


USER_TABLES = [UserFeatures, LineSchema, ContextInclude, AgentFeatures,
               CtiPresences, CtiPhoneHintsGroup, CtiProfile, QueueMember,
               RightCallMember, Callfiltermember, Callfilter, Dialaction,
               PhoneFunckey, SchedulePath, ExtensionSchema, UserLine, UserSIPSchema,
               SCCPDeviceSchema]


class TestAssociateUserVoicemail(DAOTestCase):

    tables = USER_TABLES + [
        VoicemailSchema,
        LineSchema
    ]

    def setUp(self):
        self.empty_tables()

    def test_associate_with_sip_line(self):
        extension = '1000'
        user_id, line_id, protocol_id = self.prepare_user_and_line(extension, 'sip')
        voicemail_id = self.prepare_voicemail(extension)

        user_voicemail = UserVoicemail(user_id=user_id, voicemail_id=voicemail_id)
        user_voicemail_dao.associate(user_voicemail)

        self.assert_user_was_associated_with_voicemail(user_id, voicemail_id, enabled=True)
        self.assert_sip_line_was_associated_with_voicemail(protocol_id, voicemail_id)

    def test_associate_with_sip_line_when_voicemail_disabled(self):
        extension = '1000'
        user_id, line_id, protocol_id = self.prepare_user_and_line(extension, 'sip')
        voicemail_id = self.prepare_voicemail(extension)

        user_voicemail = UserVoicemail(user_id=user_id, voicemail_id=voicemail_id, enabled=False)
        user_voicemail_dao.associate(user_voicemail)

        self.assert_user_was_associated_with_voicemail(user_id, voicemail_id, enabled=False)
        self.assert_sip_line_was_associated_with_voicemail(protocol_id, voicemail_id)

    def test_associate_with_sip_line_when_secondary_user(self):
        extension = '1000'
        main_user_id, secondary_user_id, line_id, protocol_id = self.prepare_main_and_secondary_user(extension, 'sip')
        voicemail_id = self.prepare_voicemail(extension)

        user_voicemail = UserVoicemail(user_id=secondary_user_id, voicemail_id=voicemail_id)
        user_voicemail_dao.associate(user_voicemail)

        self.assert_user_was_associated_with_voicemail(secondary_user_id, voicemail_id, enabled=True)
        self.assert_sip_line_was_not_associated_with_voicemail(protocol_id, voicemail_id)

    def test_associate_with_sccp_line(self):
        extension = '1000'
        user_id, line_id, protocol_id = self.prepare_user_and_line(extension, 'sccp')
        voicemail_id = self.prepare_voicemail(extension)

        user_voicemail = UserVoicemail(user_id=user_id, voicemail_id=voicemail_id)
        user_voicemail_dao.associate(user_voicemail)

        self.assert_user_was_associated_with_voicemail(user_id, voicemail_id, enabled=True)
        self.assert_sccp_line_was_associated_with_voicemail(extension, voicemail_id)

    def prepare_user_and_line(self, exten, protocol):
        user_line_row = self.add_user_line_with_exten(firstname='King',
                                                      exten=exten,
                                                      context='default',
                                                      protocol=protocol)

        user_id = user_line_row.user_id
        line_id = user_line_row.line_id
        protocol_id = self.session.query(LineSchema).get(user_line_row.line_id).protocolid

        if protocol == 'sip':
            self.add_usersip(id=protocol_id, context='default')
        elif protocol == 'sccp':
            self.add_sccpdevice(id=protocol_id,
                                name='SEP001122334455',
                                device='SEP001122334455',
                                line=exten)

        return user_id, line_id, protocol_id

    def prepare_voicemail(self, number):
        voicemail_row = self.add_voicemail(mailbox=number, context='default')
        return voicemail_row.uniqueid

    def prepare_main_and_secondary_user(self, number, protocol):
        main_user_row = self.add_user(firstname='Main')
        secondary_user_row = self.add_user(firstname='Secondary')
        line_row = self.add_line(number=number)
        extension_row = self.add_extension(exten=number)
        self.add_usersip(id=line_row.protocolid, context='default')

        self.add_user_line(user_id=main_user_row.id,
                           line_id=line_row.id,
                           extension_id=extension_row.id,
                           main_user=True)

        self.add_user_line(user_id=secondary_user_row.id,
                           line_id=line_row.id,
                           extension_id=extension_row.id,
                           main_user=False)

        return main_user_row.id, secondary_user_row.id, line_row.id, line_row.protocolid

    def assert_user_was_associated_with_voicemail(self, user_id, voicemail_id, enabled):
        result_user_row = self.session.query(UserFeatures).get(user_id)

        assert_that(result_user_row.voicemailid, equal_to(voicemail_id))
        assert_that(result_user_row.voicemailtype, equal_to('asterisk'))
        assert_that(result_user_row.enablevoicemail, equal_to(int(enabled)))

    def assert_sip_line_was_associated_with_voicemail(self, protocol_id, voicemail_id):
        result_usersip_row = self.session.query(UserSIPSchema).get(protocol_id)
        voicemail_row = self.session.query(VoicemailSchema).get(voicemail_id)

        assert_that(result_usersip_row.mailbox, equal_to('%s@%s' % (voicemail_row.mailbox, voicemail_row.context)))

    def assert_sip_line_was_not_associated_with_voicemail(self, protocol_id, voicemail_id):
        result_usersip_row = self.session.query(UserSIPSchema).get(protocol_id)

        assert_that(result_usersip_row.mailbox, none())

    def assert_sccp_line_was_associated_with_voicemail(self, extension, voicemail_id):
        sccp_device_row = self.session.query(SCCPDeviceSchema).filter(SCCPDeviceSchema.line == extension).first()
        voicemail_row = self.session.query(VoicemailSchema).get(voicemail_id)

        assert_that(sccp_device_row.voicemail, equal_to(voicemail_row.mailbox))


class TestUserVoicemailGetByUserId(DAOTestCase):

    tables = USER_TABLES + [
        VoicemailSchema,
        LineSchema
    ]

    def setUp(self):
        self.empty_tables()

    def test_get_by_user_id_no_users_or_voicemail(self):
        self.assertRaises(ElementNotExistsError, user_voicemail_dao.get_by_user_id, 1)

    def test_get_by_user_id_with_user_without_line_or_voicemail(self):
        user_row = self.add_user(firstname='King')

        self.assertRaises(UserVoicemailNotExistsError, user_voicemail_dao.get_by_user_id, user_row.id)

    def test_get_by_user_id_with_user_without_voicemail(self):
        user_row = self.add_user_line_with_exten(firstname='King', exten='1000', context='default')

        self.assertRaises(ElementNotExistsError, user_voicemail_dao.get_by_user_id, user_row.id)

    def test_get_by_user_id_with_voicemail(self):
        user_row, voicemail_row = self.create_user_and_voicemail(firstname='King', exten='1000', context='default')

        result = user_voicemail_dao.get_by_user_id(user_row.id)

        assert_that(result, instance_of(UserVoicemail))
        assert_that(result,
                    has_property('user_id', user_row.id),
                    has_property('voicemail_id', voicemail_row.uniqueid))

    def create_user_and_voicemail(self, firstname, exten, context):
        user_line_row = self.add_user_line_with_exten(firstname='King', exten='1000', context='default')
        user_row = self.session.query(UserFeatures).get(user_line_row.user_id)
        voicemail_row = self.add_voicemail(mailbox='1000', context='default')
        self.link_user_and_voicemail(user_row, voicemail_row.uniqueid)
        return user_row, voicemail_row


class TestDissociateUserVoicemail(DAOTestCase):

    tables = USER_TABLES + [
        VoicemailSchema,
        LineSchema
    ]

    def setUp(self):
        self.empty_tables()

    def test_dissociate_from_user_with_sip_line(self):
        extension = '1000'
        voicemail = self.prepare_voicemail(extension)
        user_id, _, protocol_id = self.prepare_user_and_line(extension, voicemail, 'sip')

        user_voicemail = UserVoicemail(user_id=user_id, voicemail_id=voicemail.uniqueid)
        user_voicemail_dao.dissociate(user_voicemail)

        self.assert_user_was_dissociated_from_voicemail(user_id)
        self.assert_sip_line_was_dissociated_from_voicemail(protocol_id)

    def test_dissociate_from_secondary_user_with_sip_line(self):
        extension_main = '1000'
        extension_secondary = '1001'
        voicemail_main = self.prepare_voicemail(extension_main)
        voicemail_secondary = self.prepare_voicemail(extension_secondary)
        _, secondary_user_id, _, protocol_id = self.prepare_main_and_secondary_user(extension_main, voicemail_main, voicemail_secondary, 'sip')

        user_voicemail = UserVoicemail(user_id=secondary_user_id, voicemail_id=voicemail_secondary.uniqueid)
        user_voicemail_dao.dissociate(user_voicemail)

        self.assert_user_was_dissociated_from_voicemail(secondary_user_id)
        self.assert_sip_line_was_not_dissociated_from_voicemail(protocol_id, voicemail_main)

    def test_dissociate_from_user_with_sccp_line(self):
        extension = '1000'
        voicemail = self.prepare_voicemail(extension)
        user_id, _, _ = self.prepare_user_and_line(extension, voicemail, 'sccp')

        user_voicemail = UserVoicemail(user_id=user_id, voicemail_id=voicemail.uniqueid)
        user_voicemail_dao.dissociate(user_voicemail)

        self.assert_user_was_dissociated_from_voicemail(user_id)
        self.assert_sccp_line_was_dissociated_from_voicemail(extension)

    def prepare_user_and_line(self, exten, voicemail, protocol):
        user_line_row = self.add_user_line_with_exten(firstname='King',
                                                      exten=exten,
                                                      context='default',
                                                      protocol=protocol,
                                                      voicemail_id=voicemail.uniqueid)

        user_id = user_line_row.user_id
        line_id = user_line_row.line_id
        protocol_id = self.session.query(LineSchema).get(user_line_row.line_id).protocolid

        if protocol == 'sip':
            self.add_usersip(id=protocol_id, context='default', mailbox='%s@%s' % (voicemail.mailbox, voicemail.context))
        elif protocol == 'sccp':
            self.add_sccpdevice(id=protocol_id,
                                name='SEP001122334455',
                                device='SEP001122334455',
                                line=exten,
                                voicemail=voicemail.mailbox)

        return user_id, line_id, protocol_id

    def prepare_voicemail(self, number):
        voicemail_row = self.add_voicemail(mailbox=number, context='default')
        return voicemail_row

    def prepare_main_and_secondary_user(self, number, voicemail_main, voicemail_secondary, protocol):
        main_user_row = self.add_user(firstname='Main', voicemailid=voicemail_main.uniqueid)
        secondary_user_row = self.add_user(firstname='Secondary', voicemailid=voicemail_secondary.uniqueid)
        line_row = self.add_line(number=number)
        extension_row = self.add_extension(exten=number)
        self.add_usersip(id=line_row.protocolid, context='default', mailbox='%s@%s' % (voicemail_main.mailbox, voicemail_main.context))

        self.add_user_line(user_id=main_user_row.id,
                           line_id=line_row.id,
                           extension_id=extension_row.id,
                           main_user=True)

        self.add_user_line(user_id=secondary_user_row.id,
                           line_id=line_row.id,
                           extension_id=extension_row.id,
                           main_user=False)

        return main_user_row.id, secondary_user_row.id, line_row.id, line_row.protocolid

    def assert_user_was_dissociated_from_voicemail(self, user_id):
        result_user_row = self.session.query(UserFeatures).get(user_id)

        assert_that(result_user_row.voicemailid, none())
        assert_that(result_user_row.voicemailtype, none())
        assert_that(result_user_row.enablevoicemail, equal_to(0))

    def assert_sip_line_was_dissociated_from_voicemail(self, protocol_id):
        result_usersip_row = self.session.query(UserSIPSchema).get(protocol_id)

        assert_that(result_usersip_row.mailbox, none())

    def assert_sip_line_was_not_dissociated_from_voicemail(self, protocol_id, voicemail):
        result_usersip_row = self.session.query(UserSIPSchema).get(protocol_id)

        assert_that(result_usersip_row.mailbox, equal_to('%s@%s' % (voicemail.mailbox, voicemail.context)))

    def assert_sccp_line_was_dissociated_from_voicemail(self, extension):
        sccp_device_row = self.session.query(SCCPDeviceSchema).filter(SCCPDeviceSchema.line == extension).first()

        assert_that(sccp_device_row.voicemail, equal_to(''))
