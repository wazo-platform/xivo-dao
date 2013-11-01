# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from hamcrest import *
from xivo_dao import asterisk_conf_dao
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.agentqueueskill import AgentQueueSkill
from xivo_dao.alchemy.context import Context
from xivo_dao.alchemy.contextinclude import ContextInclude
from xivo_dao.alchemy.ctipresences import CtiPresences
from xivo_dao.alchemy.ctiphonehintsgroup import CtiPhoneHintsGroup
from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.features import Features
from xivo_dao.alchemy.groupfeatures import GroupFeatures
from xivo_dao.alchemy.iaxcallnumberlimits import IAXCallNumberLimits
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.musiconhold import MusicOnHold
from xivo_dao.alchemy.phonefunckey import PhoneFunckey
from xivo_dao.alchemy.pickup import Pickup
from xivo_dao.alchemy.pickupmember import PickupMember
from xivo_dao.alchemy.queue import Queue
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.queuepenalty import QueuePenalty
from xivo_dao.alchemy.queuepenaltychange import QueuePenaltyChange
from xivo_dao.alchemy.queueskill import QueueSkill
from xivo_dao.alchemy.queueskillrule import QueueSkillRule
from xivo_dao.alchemy.sccpdevice import SCCPDevice
from xivo_dao.alchemy.sccpgeneralsettings import SCCPGeneralSettings
from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.alchemy.sipauthentication import SIPAuthentication
from xivo_dao.alchemy.staticiax import StaticIAX
from xivo_dao.alchemy.staticmeetme import StaticMeetme
from xivo_dao.alchemy.staticqueue import StaticQueue
from xivo_dao.alchemy.staticsip import StaticSIP
from xivo_dao.alchemy.staticvoicemail import StaticVoicemail
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.alchemy.voicemail import Voicemail
from xivo_dao.tests.test_dao import DAOTestCase


class TestAsteriskConfDAO(DAOTestCase):

    tables = [AgentFeatures,
              AgentQueueSkill,
              Context,
              ContextInclude,
              CtiPhoneHintsGroup,
              CtiPresences,
              CtiProfile,
              Extension,
              Features,
              GroupFeatures,
              IAXCallNumberLimits,
              LineFeatures,
              MusicOnHold,
              PhoneFunckey,
              Pickup,
              PickupMember,
              Queue,
              QueueFeatures,
              QueueMember,
              QueuePenalty,
              QueuePenaltyChange,
              QueueSkill,
              QueueSkillRule,
              SCCPDevice,
              SCCPGeneralSettings,
              SCCPLine,
              SIPAuthentication,
              StaticIAX,
              StaticMeetme,
              StaticQueue,
              StaticSIP,
              StaticVoicemail,
              UserLine,
              UserFeatures,
              UserSIP,
              Voicemail]

    def setUp(self):
        self.empty_tables()

    def test_find_sccp_general_settings(self):
        expected_result = [
            {'option_name': 'directmedia',
             'option_value': 'no'},
            {'option_name': 'dialtimeout',
             'option_value': '6'},
            {'option_name': 'language',
             'option_value': 'en_US'},
            {'option_name': 'vmexten',
             'option_value': '*98'},
        ]

        self.add_sccp_general_settings(**expected_result[0])
        self.add_sccp_general_settings(**expected_result[1])
        self.add_sccp_general_settings(**expected_result[2])
        self.add_extension(exten='*98',
                           type='extenfeatures',
                           typeval='vmusermsg')

        sccp_general_settings = asterisk_conf_dao.find_sccp_general_settings()

        assert_that(sccp_general_settings, has_items(*expected_result))

    def test_find_sccp_line_settings(self):
        number = '1234'
        sccp_line = self.add_sccpline(cid_num=number)
        ule = self.add_user_line_with_exten(protocol='sccp',
                                            protocolid=sccp_line.id,
                                            exten=number)
        expected_result = [
            {'user_id': ule.user_id,
             'name': sccp_line.name,
             'language': None,
             'number': number,
             'cid_name': u'Tester One',
             'context': u'foocontext',
             'cid_num': number}
        ]

        sccp_line = asterisk_conf_dao.find_sccp_line_settings()

        assert_that(sccp_line, has_items(*expected_result))

    def test_find_sccp_device_settings(self):
        sccp_device = self.add_sccpdevice()

        expected_result = [
            {'id': sccp_device.id,
             'name': sccp_device.name,
             'device': sccp_device.device,
             'line': sccp_device.line,
             'voicemail': sccp_device.voicemail}
        ]

        sccp_device = asterisk_conf_dao.find_sccp_device_settings()

        assert_that(sccp_device, has_items(*expected_result))

    def test_find_sccp_speeddial_settings(self):
        number = '4567'
        sccp_device = self.add_sccpdevice(line=number)
        sccp_line = self.add_sccpline(cid_num=number)
        ule = self.add_user_line_with_exten(protocol='sccp',
                                            protocolid=sccp_line.id,
                                            exten=number)
        phonefunckey = self.add_function_key_to_user(iduserfeatures=ule.user_id,
                                                     exten=number)

        expected_result = [
            {'user_id': ule.user_id,
             'fknum': 1,
             'exten': number,
             'supervision': 0,
             'label': phonefunckey.label,
             'device': sccp_device.device}
        ]

        sccp_device = asterisk_conf_dao.find_sccp_speeddial_settings()

        assert_that(sccp_device, has_items(*expected_result))

    def test_find_featuremap_features_settings(self):
        features = Features(id=1,
                            category='featuremap',
                            filename='features.conf',
                            var_name='disconnect',
                            var_val='*0')
        self.add_me(features)

        features = Features(id=2,
                            category='featuremap',
                            filename='features.conf',
                            var_name='automon',
                            var_val='*3')
        self.add_me(features)

        expected_result = [
            {'category': u'featuremap',
             'cat_metric': 0,
             'filename': u'features.conf',
             'var_metric': 0,
             'var_name': u'disconnect',
             'var_val': u'*0',
             'id': 1,
             'commented': 0},
            {'category': u'featuremap',
             'cat_metric': 0,
             'filename': u'features.conf',
             'var_metric': 0,
             'var_name': u'automon',
             'var_val': u'*3',
             'id': 2,
             'commented': 0}
        ]

        featuremap = asterisk_conf_dao.find_featuremap_features_settings()

        assert_that(featuremap, has_items(*expected_result))

    def test_find_general_features_settings(self):
        features = Features(id=1,
                            category='general',
                            filename='features.conf',
                            var_name='atxfernoanswertimeout',
                            var_val='15')
        self.add_me(features)

        features = Features(id=2,
                            category='general',
                            filename='features.conf',
                            var_name='atxferdropcall',
                            var_val='10')
        self.add_me(features)

        expected_result = [
            {'category': u'general',
             'cat_metric': 0,
             'filename': u'features.conf',
             'var_metric': 0,
             'var_name': u'atxfernoanswertimeout',
             'var_val': u'15',
             'id': 1,
             'commented': 0},
            {'category': u'general',
             'cat_metric': 0,
             'filename': u'features.conf',
             'var_metric': 0,
             'var_name': u'atxferdropcall',
             'var_val': u'10',
             'id': 2,
             'commented': 0}
        ]

        featuremap = asterisk_conf_dao.find_general_features_settings()

        assert_that(featuremap, has_items(*expected_result))

    def test_find_exten_progfunckeys_settings(self):
        number = '4567'
        ule = self.add_user_line_with_exten(exten=number)
        phonefunckey = self.add_function_key_to_user(iduserfeatures=ule.user_id,
                                                     exten=number,
                                                     typeextenumbers='user',
                                                     typevalextenumbers='toto',
                                                     supervision=1,
                                                     progfunckey=1)

        expected_result = [
            {'leftexten': number,
             'user_id': ule.user_id,
             'exten': number,
             'typeextenumbers': u'user',
             'typevalextenumbersright': None,
             'typeextenumbersright': u'user',
             'typevalextenumbers': phonefunckey.typevalextenumbers}
        ]

        funckeys = asterisk_conf_dao.find_exten_progfunckeys_settings(ule.line.context)

        assert_that(funckeys, has_items(*expected_result))

    def test_find_exten_phonefunckeys_settings(self):
        number = '4567'
        ule = self.add_user_line_with_exten(exten=number)
        self.add_function_key_to_user(iduserfeatures=ule.user_id,
                                      exten=number,
                                      typeextenumbersright='group',
                                      typevalextenumbersright=number,
                                      typeextenumbers=None,
                                      typevalextenumbers=None,
                                      supervision=1,
                                      progfunckey=1)

        expected_result = [
            {'exten': None,
             'typevalextenumbersright': number,
             'typeextenumbersright': u'group'}
        ]

        funckeys = asterisk_conf_dao.find_exten_phonefunckeys_settings(ule.line.context)

        assert_that(funckeys, has_items(*expected_result))

    def test_find_exten_xivofeatures_setting(self):
        exten1 = self.add_extension(exten='*25', context='xivo-features')
        exten2 = self.add_extension(exten='*26', context='xivo-features')
        self.add_extension(exten='3492', context='robert', type='user', typeval='14')

        expected_result = [
            {'exten': u'*25',
             'commented': 0,
             'context': u'xivo-features',
             'typeval': None,
             'type': 'user',
             'id': exten1.id},
            {'exten': u'*26',
             'commented': 0,
             'context': u'xivo-features',
             'typeval': None,
             'type': 'user',
             'id': exten2.id}
        ]

        extensions = asterisk_conf_dao.find_exten_xivofeatures_setting()

        assert_that(extensions, has_items(*expected_result))

    def test_find_extenfeatures_settings(self):
        exten1 = self.add_extension(exten='*98', context='xivo-features', type='extenfeatures', typeval='vmusermsg')
        exten2 = self.add_extension(exten='*92', context='xivo-features', type='extenfeatures', typeval='vmuserpurge')
        self.add_extension(exten='3492', context='robert', type='user', typeval='14')

        expected_result = [
            {'exten': u'*98',
             'commented': 0,
             'context': u'xivo-features',
             'typeval': 'vmusermsg',
             'type': 'extenfeatures',
             'id': exten1.id},
            {'exten': u'*92',
             'commented': 0,
             'context': u'xivo-features',
             'typeval': 'vmuserpurge',
             'type': 'extenfeatures',
             'id': exten2.id}
        ]

        extensions = asterisk_conf_dao.find_extenfeatures_settings(['vmusermsg', 'vmuserpurge'])

        assert_that(extensions, has_items(*expected_result))

    def test_find_exten_settings(self):
        exten1 = self.add_extension(exten='12', context='default')
        exten2 = self.add_extension(exten='23', context='default')
        self.add_extension(exten='41', context='toto')

        expected_result = [
            {'exten': u'12',
             'commented': 0,
             'context': u'default',
             'typeval': None,
             'type': 'user',
             'id': exten1.id},
            {'exten': u'23',
             'commented': 0,
             'context': u'default',
             'typeval': None,
             'type': 'user',
             'id': exten2.id}
        ]

        extensions = asterisk_conf_dao.find_exten_settings('default')

        assert_that(extensions, has_items(*expected_result))

    def test_find_exten_hints_settings(self):
        context = 'tyoyoi'
        vm = self.add_voicemail(context=context)
        ule = self.add_user_line_with_exten(context=context,
                                            voicemail_id=vm.uniqueid)

        expected_result = [
            {'protocol': ule.line.protocol,
             'name': ule.line.name,
             'voicemail_id': vm.uniqueid,
             'number': ule.extension.exten,
             'user_id': ule.user_id,
             'enablevoicemail': 0}
        ]

        extensions = asterisk_conf_dao.find_exten_hints_settings(context)

        assert_that(extensions, has_items(*expected_result))

    def test_find_context_settings(self):
        context1 = self.add_context()
        context2 = self.add_context()

        expected_result = [
            {'displayname': context1.displayname,
             'description': context1.description,
             'entity': context1.entity,
             'contexttype': context1.contexttype,
             'commented': context1.commented,
             'name': context1.name},
            {'displayname': context2.displayname,
             'description': context2.description,
             'entity': context2.entity,
             'contexttype': context2.contexttype,
             'commented': context2.commented,
             'name': context2.name},
        ]

        context = asterisk_conf_dao.find_context_settings()

        assert_that(context, has_items(*expected_result))

    def test_find_contextincludes_settings(self):
        context = 'default'
        self.add_context_include(context='koki')
        context_include = self.add_context_include(context=context)
        self.add_context_include(context='toto')

        expected_result = [
            {'context': context_include.context,
             'include': context_include.include,
             'priority': context_include.priority}
        ]

        context = asterisk_conf_dao.find_contextincludes_settings(context)

        assert_that(context, has_items(*expected_result))

    def test_find_voicemail_activated(self):
        vm = self.add_voicemail()
        self.add_voicemail(commented=0)

        expected_result = [
            {'imapuser': None,
             'backupdeleted': None,
             'serveremail': None,
             'tempgreetwarn': None,
             'passwordlocation': None,
             'attachfmt': None,
             'emailbody': None,
             'saydurationm': None,
             'deletevoicemail': 0,
             'operator': None,
             'locale': None,
             'emailsubject': None,
             'maxmsg': None,
             'tz': None,
             'forcename': None,
             'saycid': None,
             'exitcontext': None,
             'attach': None,
             'sayduration': None,
             'volgain': None,
             'maxsecs': None,
             'email': None,
             'nextaftercmd': None,
             'moveheard': None,
             'hidefromdir': 'no',
             'envelope': None,
             'mailbox': vm.mailbox,
             'imapvmsharedid': None,
             'dialout': None,
             'uniqueid': vm.uniqueid,
             'forcegreetings': None,
             'password': u'',
             'pager': None,
             'sendvoicemail': None,
             'language': None,
             'minsecs': None,
             'commented': 0,
             'callback': None,
             'imappassword': None,
             'context': vm.context,
             'skipcheckpass': 0,
             'fullname': vm.fullname,
             'review': None,
             'messagewrap': None,
             'imapfolder': None}
        ]

        voicemails = asterisk_conf_dao.find_voicemail_activated()

        assert_that(voicemails, has_items(*expected_result))

    def test_find_voicemail_general_settings(self):
        vms1 = self.add_voicemail_general_settings()
        vms2 = self.add_voicemail_general_settings()
        self.add_voicemail_general_settings(commented=0)

        expected_result = [
            {'category': u'general',
             'var_name': vms1.var_name,
             'var_val': vms1.var_val},
            {'category': u'general',
             'var_name': vms2.var_name,
             'var_val': vms2.var_val},
        ]

        voicemail_settings = asterisk_conf_dao.find_voicemail_general_settings()

        assert_that(voicemail_settings, has_items(*expected_result))

    def test_find_sip_general_settings(self):
        sip1 = self.add_sip_general_settings()
        sip2 = self.add_sip_general_settings()
        self.add_sip_general_settings(commented=0)

        expected_result = [
            {'var_name': sip1.var_name,
             'var_val': sip1.var_val},
            {'var_name': sip2.var_name,
             'var_val': sip2.var_val},
        ]

        sip_settings = asterisk_conf_dao.find_sip_general_settings()

        assert_that(sip_settings, has_items(*expected_result))

    def test_find_sip_authentication_settings(self):
        sip1 = self.add_sip_authentication()
        sip2 = self.add_sip_authentication()

        expected_result = [
            {'realm': sip1.realm,
             'secret': sip1.secret,
             'user': sip1.user,
             'usersip_id': sip1.usersip_id,
             'id': sip1.id,
             'secretmode': sip1.secretmode},
            {'realm': sip2.realm,
             'secret': sip2.secret,
             'user': sip2.user,
             'usersip_id': sip2.usersip_id,
             'id': sip2.id,
             'secretmode': sip2.secretmode},
        ]

        sip_authentication = asterisk_conf_dao.find_sip_authentication_settings()

        assert_that(sip_authentication, has_items(*expected_result))

    def test_find_sip_trunk_settings(self):
        sip1 = self.add_usersip(category='trunk')
        self.add_usersip(category='trunk', commented=1)

        expected_result = [
            {'protocol': u'sip',
             'buggymwi': None,
             'amaflags': u'default',
             'sendrpid': None,
             'videosupport': None,
             'regseconds': 0,
             'maxcallbitrate': None,
             'registertrying': None,
             'session-minse': None,
             'mohinterpret': None,
             'rtpholdtimeout': None,
             'session-expires': None,
             'defaultip': None,
             'ignoresdpversion': None,
             'vmexten': None,
             'name': sip1.name,
             'callingpres': None,
             'textsupport': None,
             'unsolicited_mailbox': None,
             'outboundproxy': None,
             'fromuser': None,
             'cid_number': None,
             'commented': 0,
             'useclientcode': None,
             'call-limit': 0,
             'progressinband': None,
             'port': None,
             'transport': None,
             'category': u'trunk',
             'md5secret': u'',
             'regserver': None,
             'directmedia': None,
             'mailbox': None,
             'qualifyfreq': None,
             'host': u'dynamic',
             'promiscredir': None,
             'disallow': None,
             'allowoverlap': None,
             'accountcode': None,
             'dtmfmode': None,
             'language': None,
             'usereqphone': None,
             'qualify': None,
             'trustrpid': None,
             'context': u'default',
             'timert1': None,
             'session-refresher': None,
             'maxforwards': None,
             'allowsubscribe': None,
             'session-timers': None,
             'busylevel': None,
             'callcounter': None,
             'callerid': None,
             'encryption': None,
             'remotesecret': None,
             'secret': u'',
             'use_q850_reason': None,
             'type': u'friend',
             'username': None,
             'callbackextension': None,
             'disallowed_methods': None,
             'rfc2833compensate': None,
             'g726nonstandard': None,
             'contactdeny': None,
             'snom_aoc_enabled': None,
             'fullname': None,
             't38pt_udptl': None,
             'fullcontact': None,
             'subscribemwi': 0,
             'mohsuggest': None,
             'id': sip1.id,
             'autoframing': None,
             't38pt_usertpsource': None,
             'ipaddr': u'',
             'fromdomain': None,
             'allowtransfer': None,
             'nat': None,
             'setvar': u'',
             'contactpermit': None,
             'rtpkeepalive': None,
             'insecure': None,
             'permit': None,
             'parkinglot': None,
             'lastms': u'',
             'subscribecontext': None,
             'regexten': None,
             'deny': None,
             'timerb': None,
             'rtptimeout': None,
             'allow': None}
        ]

        sip_trunk = asterisk_conf_dao.find_sip_trunk_settings()

        assert_that(sip_trunk, has_items(*expected_result))

    def test_find_sip_user_settings(self):
        usersip = self.add_usersip(category='user')
        ule = self.add_user_line_with_exten(protocol='sip',
                                            protocolid=usersip.id,
                                            name_line=usersip.name,
                                            context=usersip.context)

        expected_result = [
            {'number': ule.line.number,
             'protocol': ule.line.protocol,
             'buggymwi': None,
             'amaflags': u'default',
             'sendrpid': None,
             'videosupport': None,
             'regseconds': 0,
             'maxcallbitrate': None,
             'registertrying': None,
             'session-minse': None,
             'mohinterpret': None,
             'rtpholdtimeout': None,
             'session-expires': None,
             'defaultip': None,
             'ignoresdpversion': None,
             'vmexten': None,
             'name': usersip.name,
             'callingpres': None,
             'textsupport': None,
             'unsolicited_mailbox': None,
             'outboundproxy': None,
             'fromuser': None,
             'cid_number': None,
             'commented': 0,
             'useclientcode': None,
             'call-limit': 0,
             'progressinband': None,
             'port': None,
             'transport': None,
             'category': u'user',
             'md5secret': u'',
             'regserver': None,
             'directmedia': None,
             'mailbox': None,
             'qualifyfreq': None,
             'host': u'dynamic',
             'promiscredir': None,
             'disallow': None,
             'allowoverlap': None,
             'accountcode': None,
             'dtmfmode': None,
             'language': None,
             'usereqphone': None,
             'qualify': None,
             'trustrpid': None,
             'context': ule.line.context,
             'timert1': None,
             'session-refresher': None,
             'maxforwards': None,
             'allowsubscribe': None,
             'session-timers': None,
             'busylevel': None,
             'callcounter': None,
             'callerid': None,
             'encryption': None,
             'remotesecret': None,
             'secret': u'',
             'use_q850_reason': None,
             'type': u'friend',
             'username': None,
             'callbackextension': None,
             'disallowed_methods': None,
             'rfc2833compensate': None,
             'g726nonstandard': None,
             'contactdeny': None,
             'snom_aoc_enabled': None,
             'fullname': None,
             't38pt_udptl': None,
             'fullcontact': None,
             'subscribemwi': 0,
             'mohsuggest': None,
             'id': usersip.id,
             'autoframing': None,
             't38pt_usertpsource': None,
             'ipaddr': u'',
             'fromdomain': None,
             'allowtransfer': None,
             'nat': None,
             'setvar': u'',
             'contactpermit': None,
             'rtpkeepalive': None,
             'insecure': None,
             'permit': None,
             'parkinglot': None,
             'lastms': u'',
             'subscribecontext': None,
             'regexten': None,
             'deny': None,
             'timerb': None,
             'rtptimeout': None,
             'allow': None}
        ]

        sip_user = asterisk_conf_dao.find_sip_user_settings()

        assert_that(sip_user, has_items(*expected_result))

    def test_find_sip_pickup_settings(self):
        pickup = self.add_pickup()
        usersip = self.add_usersip(category='user')
        ule = self.add_user_line_with_exten(protocol='sip',
                                            protocolid=usersip.id,
                                            name_line=usersip.name,
                                            context=usersip.context)
        pickup_member = self.add_pickup_member(pickupid=pickup.id,
                                               membertype='user',
                                               memberid=ule.user_id)

        self.add_queue_member()

        expected_result = [(usersip.name, pickup_member.category, pickup.id)]

        sip_pickup = asterisk_conf_dao.find_sip_pickup_settings()

        assert_that(sip_pickup, has_items(*expected_result))
