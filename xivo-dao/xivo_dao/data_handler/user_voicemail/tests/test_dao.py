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

from hamcrest import assert_that, has_length, all_of, has_property, instance_of, contains, equal_to, none

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


USER_TABLES = [UserFeatures, LineSchema, ContextInclude, AgentFeatures,
               CtiPresences, CtiPhoneHintsGroup, CtiProfile, QueueMember,
               RightCallMember, Callfiltermember, Callfilter, Dialaction,
               PhoneFunckey, SchedulePath, ExtensionSchema, UserLine, UserSIPSchema,
               SCCPDeviceSchema]


class TestAssociate(DAOTestCase):

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
        voicemail_row = self.add_voicemail(number, 'default')
        return voicemail_row.uniqueid

    def prepare_main_and_secondary_user(self, number, protocol):
        main_user_row = self.add_user(firstname='Main')
        secondary_user_row = self.add_user(firstname='Secondary')
        line_row = self.add_line(number=number)
        extension_row = self.add_extension(exten=number)
        usersip_row = self.add_usersip(id=line_row.protocolid, context='default')

        main_user_line_row = self.add_user_line(user_id=main_user_row.id,
                                                line_id=line_row.id,
                                                extension_id=extension_row.id,
                                                main_user=True)

        secondary_user_line_row = self.add_user_line(user_id = secondary_user_row.id,
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

    def assert_sccp_line_was_associated_with_voicemail(self, extension, voicemail_id):
        sccp_device_row = self.session.query(SCCPDeviceSchema).filter(SCCPDeviceSchema.line == extension).first()
        voicemail_row = self.session.query(VoicemailSchema).get(voicemail_id)

        assert_that(sccp_device_row.voicemail, equal_to(voicemail_row.mailbox))

class TestFindAllByUserId(DAOTestCase):

    tables = USER_TABLES + [
        VoicemailSchema,
        LineSchema
    ]

    def setUp(self):
        self.empty_tables()

    def test_find_all_by_user_id_no_users_or_voicemail(self):
        result = user_voicemail_dao.find_all_by_user_id(1)

        assert_that(result, has_length(0))

    def test_find_all_by_user_id_with_user_without_line_or_voicemail(self):
        user_row = self.add_user(firstname='King')

        result = user_voicemail_dao.find_all_by_user_id(user_row.id)

        assert_that(result, has_length(0))

    def test_find_all_by_user_id_with_user_without_voicemail(self):
        user_row = self.add_user_line_with_exten(firstname='King', exten='1000', context='default')

        result = user_voicemail_dao.find_all_by_user_id(user_row.id)

        assert_that(result, has_length(0))

    def test_find_all_by_user_id_with_voicemail(self):
        user_row, voicemail_row = self.create_user_and_voicemail(firstname='King', exten='1000', context='default')

        result = user_voicemail_dao.find_all_by_user_id(user_row.id)

        assert_that(result, contains(all_of(
            instance_of(UserVoicemail),
            has_property('user_id', user_row.id),
            has_property('voicemail_id', voicemail_row.uniqueid)
        )))

    def test_find_all_by_user_id_with_unassociated_voicemail(self):
        user_row = self.add_user(firstname='King', voicemailid=0)

        result = user_voicemail_dao.find_all_by_user_id(user_row.id)

        assert_that(result, has_length(0))

    def create_user_and_voicemail(self, firstname, exten, context):
        user_row = self.add_user(firstname='King')
        line_row = self.add_line(number='1000', context='default')
        extension_row = self.add_extension(exten='1000', context='default')
        user_line_row = self.add_user_line(user_id=user_row.id, line_id=line_row.id, extension_id=extension_row.id)
        voicemail_row = self.add_voicemail('1000', 'default')
        self.link_user_and_voicemail(user_row, voicemail_row.uniqueid)
        return user_row, voicemail_row
