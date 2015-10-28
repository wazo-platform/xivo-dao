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

import warnings

from contextlib import contextmanager
from hamcrest import assert_that, contains, equal_to, has_entries, \
    contains_inanyorder, has_length, none, has_entry

from mock import patch
from xivo_dao import asterisk_conf_dao
from xivo_dao.alchemy.agentqueueskill import AgentQueueSkill
from xivo_dao.alchemy.iaxcallnumberlimits import IAXCallNumberLimits
from xivo_dao.alchemy.queuepenalty import QueuePenalty
from xivo_dao.alchemy.queuepenaltychange import QueuePenaltyChange
from xivo_dao.alchemy.func_key_dest_custom import FuncKeyDestCustom
from xivo_dao.tests.test_dao import DAOTestCase


@contextmanager
def warning_filter(level):
    warnings.simplefilter(level)
    yield
    warnings.resetwarnings()


class PickupHelperMixin(object):

    _category_to_conf_map = {'member': 'pickupgroup',
                             'pickup': 'callgroup'}

    def _category_to_conf(self, category):
        return self._category_to_conf_map[category]

    def add_pickup_member_user(self, pickup, user_id):
        args = {
            'pickupid': pickup.id,
            'membertype': 'user',
            'memberid': user_id,
        }

        pickup_member = self.add_pickup_member(**args)

        return self._category_to_conf(pickup_member.category)

    def add_pickup_member_group(self, pickup, user_id):
        group = self.add_group()
        pickup_member = self.add_pickup_member(pickupid=pickup.id,
                                               membertype='group',
                                               memberid=group.id)
        self.add_queue_member(queue_name=group.name,
                              usertype='user',
                              userid=user_id)

        return self._category_to_conf(pickup_member.category)

    def add_pickup_member_queue(self, pickup, user_id):
        queue = self.add_queuefeatures()
        pickup_member = self.add_pickup_member(pickupid=pickup.id,
                                               membertype='queue',
                                               memberid=queue.id)
        self.add_queue_member(queue_name=queue.name,
                              usertype='user',
                              userid=user_id)

        return self._category_to_conf(pickup_member.category)


class TestSCCPLineSettingDAO(DAOTestCase, PickupHelperMixin):

    def test_find_sccp_line_settings_when_line_enabled(self):
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

        assert_that(sccp_line, contains_inanyorder(*expected_result))

    def test_find_sccp_line_settings_when_line_disabled(self):
        number = '1234'
        sccp_line = self.add_sccpline(cid_num=number)
        self.add_user_line_with_exten(protocol='sccp',
                                      protocolid=sccp_line.id,
                                      exten=number,
                                      commented_line=1)

        sccp_line = asterisk_conf_dao.find_sccp_line_settings()

        assert_that(sccp_line, contains())

    def test_find_sccp_line_allow(self):
        number = '1234'
        sccp_line = self.add_sccpline(cid_num=number, allow='g729')
        ule = self.add_user_line_with_exten(protocol='sccp',
                                            protocolid=sccp_line.id,
                                            exten=number)
        expected_result = {
            'user_id': ule.user_id,
            'name': sccp_line.name,
            'language': None,
            'number': number,
            'cid_name': u'Tester One',
            'context': u'foocontext',
            'cid_num': number,
            'allow': 'g729',
        }

        sccp_lines = asterisk_conf_dao.find_sccp_line_settings()

        assert_that(sccp_lines, contains(expected_result))

    def test_find_sccp_line_disallow(self):
        number = '1234'
        sccp_line = self.add_sccpline(cid_num=number, allow='g729', disallow='all')
        ule = self.add_user_line_with_exten(protocol='sccp',
                                            protocolid=sccp_line.id,
                                            exten=number)
        expected_result = {
            'user_id': ule.user_id,
            'name': sccp_line.name,
            'language': None,
            'number': number,
            'cid_name': u'Tester One',
            'context': u'foocontext',
            'cid_num': number,
            'allow': 'g729',
            'disallow': 'all',
        }

        sccp_line = asterisk_conf_dao.find_sccp_line_settings()

        assert_that(sccp_line, contains(expected_result))

    @patch('xivo_dao.asterisk_conf_dao.find_pickup_members')
    def test_find_sccp_line_pickup_group(self, mock_find_pickup_members):
        sccp_line = self.add_sccpline()
        ule = self.add_user_line_with_exten(protocol='sccp',
                                            protocolid=sccp_line.id)
        callgroups = set([1, 2, 3, 4])
        pickupgroups = set([3, 4])
        pickup_members = {ule.line.protocolid: {'callgroup': callgroups,
                                                'pickupgroup': pickupgroups}}
        mock_find_pickup_members.return_value = pickup_members

        sccp_lines = asterisk_conf_dao.find_sccp_line_settings()

        expected = {
            'user_id': ule.user_id,
            'name': sccp_line.name,
            'language': None,
            'number': ule.extension.exten,
            'cid_name': u'Tester One',
            'context': u'foocontext',
            'cid_num': sccp_line.cid_num,
            'callgroup': callgroups,
            'pickupgroup': pickupgroups,
        }

        assert_that(sccp_lines, contains(expected))


class TestSccpConfDAO(DAOTestCase):

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

        assert_that(sccp_general_settings, contains_inanyorder(*expected_result))

    def test_find_sccp_device_settings_no_voicemail(self):
        sccp_device = self.add_sccpdevice()

        expected_device = {'id': sccp_device.id,
                           'name': sccp_device.name,
                           'device': sccp_device.device,
                           'line': sccp_device.line,
                           'voicemail': None}

        sccp_device = asterisk_conf_dao.find_sccp_device_settings()

        assert_that(sccp_device, contains(expected_device))

    def test_find_sccp_device_settings(self):
        extension = self.add_extension(exten='1000', context='default')
        sccp_device = self.add_sccpdevice(line=extension.exten)
        sccp_line = self.add_sccpline(name=extension.exten, context=extension.context)
        line = self.add_line(protocol='sccp', protocolid=sccp_line.id, context=extension.context)
        voicemail = self.add_voicemail(mailbox='2000')
        user = self.add_user(voicemailid=voicemail.uniqueid)
        self.add_user_line(user_id=user.id, line_id=line.id)

        expected_device = {'id': sccp_device.id,
                           'name': sccp_device.name,
                           'device': sccp_device.device,
                           'line': sccp_device.line,
                           'voicemail': voicemail.mailbox}

        sccp_device = asterisk_conf_dao.find_sccp_device_settings()

        assert_that(sccp_device, contains(expected_device))


class TestFindSccpSpeeddialSettings(DAOTestCase):

    def test_given_no_func_key_then_returns_empty_list(self):
        result = asterisk_conf_dao.find_sccp_speeddial_settings()

        assert_that(result, contains())

    def test_given_custom_func_key_then_returns_converted_func_key(self):
        exten = '1000'
        func_key_exten = '2000'
        context = 'default'

        user_row, sccp_device_row = self.add_user_with_sccp_device(exten=exten, context=context)
        func_key_mapping_row = self.add_custom_func_key_to_user(user_row, func_key_exten)

        result = asterisk_conf_dao.find_sccp_speeddial_settings()

        expected = {'user_id': user_row.id,
                    'fknum': func_key_mapping_row.position,
                    'exten': func_key_exten,
                    'supervision': int(func_key_mapping_row.blf),
                    'label': func_key_mapping_row.label,
                    'device': sccp_device_row.device}

        assert_that(result, contains(expected))

    def add_user_with_sccp_device(self, exten, context):
        user_row = self.add_user()
        sccp_device_row = self.add_sccpdevice(line=exten)
        sccp_line_row = self.add_sccpline(name=exten,
                                          cid_num=exten,
                                          context=context)
        extension_row = self.add_extension(exten=exten,
                                           context=context)
        line_row = self.add_line(context=context,
                                 protocol='sccp',
                                 protocolid=sccp_line_row.id)

        self.add_user_line(user_id=user_row.id,
                           line_id=line_row.id,
                           extension_id=extension_row.id)

        return user_row, sccp_device_row

    def add_custom_func_key_to_user(self, user_row, func_key_exten):
        func_key_type_row = self.add_func_key_type(name='speeddial')
        func_key_dest_row = self.add_func_key_destination_type(id=10, name='custom')
        func_key_row = self.add_func_key(type_id=func_key_type_row.id,
                                         destination_type_id=func_key_dest_row.id)
        self.add_func_key_dest_custom(func_key_id=func_key_row.id,
                                      destination_type_id=func_key_dest_row.id,
                                      exten=func_key_exten)
        func_key_mapping = self.add_func_key_mapping(template_id=user_row.func_key_private_template_id,
                                                     func_key_id=func_key_row.id,
                                                     destination_type_id=func_key_dest_row.id,
                                                     label='mylabel',
                                                     position=2,
                                                     blf=True)
        return func_key_mapping

    def add_func_key_dest_custom(self, **kwargs):
        row = FuncKeyDestCustom(**kwargs)
        self.add_me(row)
        return row


class TestAsteriskConfDAO(DAOTestCase, PickupHelperMixin):

    def test_find_pickup_members_empty(self):
        self.add_pickup()

        pickup_members = asterisk_conf_dao.find_pickup_members('sip')

        assert_that(pickup_members, contains())

    def test_find_pickup_members_with_sip_users(self):
        pickup = self.add_pickup()

        ule = self.add_user_line_with_exten(protocol='sip')
        category = self.add_pickup_member_user(pickup, ule.user_id)

        pickup_members = asterisk_conf_dao.find_pickup_members('sip')

        expected = {
            ule.line.protocolid: {category: set([pickup.id])},
        }

        assert_that(pickup_members, equal_to(expected))

    def test_find_pickup_members_with_sccp_users(self):
        pickup = self.add_pickup()

        sccp_line = self.add_sccpline()
        ule = self.add_user_line_with_exten(protocol='sccp', protocolid=sccp_line.id)
        category = self.add_pickup_member_user(pickup, ule.user_id)

        pickup_members = asterisk_conf_dao.find_pickup_members('sccp')

        expected = {
            sccp_line.id: {category: set([pickup.id])},
        }

        assert_that(pickup_members, equal_to(expected))

    def test_find_pickup_members_with_groups(self):
        pickup = self.add_pickup()

        ule = self.add_user_line_with_exten()
        category = self.add_pickup_member_group(pickup, ule.user_id)

        pickup_members = asterisk_conf_dao.find_pickup_members('sip')

        expected = {
            ule.line.protocolid: {category: set([pickup.id])}
        }

        assert_that(pickup_members, equal_to(expected))

    def test_find_pickup_members_with_queues(self):
        pickup = self.add_pickup()

        ule = self.add_user_line_with_exten()
        category = self.add_pickup_member_queue(pickup, ule.user_id)

        pickup_members = asterisk_conf_dao.find_pickup_members('sip')

        expected = {
            ule.line.protocolid: {category: set([pickup.id])}
        }

        assert_that(pickup_members, equal_to(expected))

    def test_find_features_settings(self):
        self.add_features(var_name='atxfernoanswertimeout',
                          var_val='15')
        self.add_features(var_name='parkext',
                          var_val='700')
        self.add_features(category='featuremap',
                          var_name='atxfer',
                          var_val='*2')
        self.add_features(category='featuremap',
                          var_name='automixmon',
                          var_val='*3')

        expected_general = [
            ('atxfernoanswertimeout', '15'),
        ]
        expected_featuremap = [
            ('atxfer', '*2'),
            ('automixmon', '*3'),
        ]

        settings = asterisk_conf_dao.find_features_settings()

        assert_that(settings['general_options'], contains_inanyorder(*expected_general))
        assert_that(settings['featuremap_options'], contains_inanyorder(*expected_featuremap))

    def test_find_features_settings_atxfer_abort_same_as_disconnect(self):
        self.add_features(category='featuremap',
                          var_name='disconnect',
                          var_val='*0')

        expected_general = [
            ('atxferabort', '*0'),
        ]
        expected_featuremap = [
            ('disconnect', '*0'),
        ]

        settings = asterisk_conf_dao.find_features_settings()

        assert_that(settings['general_options'], contains_inanyorder(*expected_general))
        assert_that(settings['featuremap_options'], contains_inanyorder(*expected_featuremap))

    def test_find_parking_settings(self):
        self.add_features(var_name='parkeddynamic',
                          var_val='no')
        self.add_features(var_name='atxferdropcall',
                          var_val='no')
        self.add_features(var_name='parkext',
                          var_val='700')

        expected_general = [
            ('parkeddynamic', 'no'),
        ]
        expected_parking_lots = [{
            'name': u'default',
            'options': [('parkext', '700')],
        }]

        settings = asterisk_conf_dao.find_parking_settings()

        assert_that(settings['general_options'], contains_inanyorder(*expected_general))
        assert_that(settings['parking_lots'], equal_to(expected_parking_lots))

    def test_find_exten_conferences_settings(self):
        conference = self.add_meetmefeatures(context='test')
        expected_result = [{'exten': conference.confno}]

        conference_extens = asterisk_conf_dao.find_exten_conferences_settings('test')

        assert_that(conference_extens, contains_inanyorder(*expected_result))

    def test_find_exten_conferences_settings_different_context(self):
        self.add_meetmefeatures(context='test')

        conference_extens = asterisk_conf_dao.find_exten_conferences_settings('default')

        assert_that(conference_extens, has_length(0))

    def test_find_exten_xivofeatures_setting(self):
        exten1 = self.add_extension(exten='*25', context='xivo-features')
        exten2 = self.add_extension(exten='*26', context='xivo-features')
        self.add_extension(exten='3492', context='robert', type='user', typeval='14')

        expected_result = [
            {'exten': u'*25',
             'commented': 0,
             'context': u'xivo-features',
             'typeval': u'',
             'type': 'user',
             'id': exten1.id},
            {'exten': u'*26',
             'commented': 0,
             'context': u'xivo-features',
             'typeval': u'',
             'type': 'user',
             'id': exten2.id}
        ]

        extensions = asterisk_conf_dao.find_exten_xivofeatures_setting()

        assert_that(extensions, contains_inanyorder(*expected_result))

    def test_find_extenfeatures_settings_when_features_is_none(self):
        exten = self.add_extension(exten='*98', context='xivo-features', type='extenfeatures', typeval='vmusermsg')
        expected_result = [
            {'exten': u'*98',
             'commented': 0,
             'context': u'xivo-features',
             'typeval': 'vmusermsg',
             'type': 'extenfeatures',
             'id': exten.id}
        ]

        extensions = asterisk_conf_dao.find_extenfeatures_settings(None)

        assert_that(extensions, expected_result)

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

        assert_that(extensions, contains_inanyorder(*expected_result))

    def test_find_exten_settings_when_line_enabled(self):
        user_row = self.add_user()
        line_row = self.add_line()
        extension_row = self.add_extension(exten='12', context='default')
        self.add_user_line(user_id=user_row.id,
                           extension_id=extension_row.id,
                           line_id=line_row.id)

        expected_result = [
            {'exten': u'12',
             'commented': 0,
             'context': u'default',
             'typeval': u'',
             'type': 'user',
             'id': extension_row.id}
        ]

        result = asterisk_conf_dao.find_exten_settings('default')

        assert_that(result, contains(*expected_result))

    def test_find_exten_settings_when_line_disabled(self):
        user_row = self.add_user()
        line_row = self.add_line(commented=1)
        extension_row = self.add_extension(exten='13', context='default')
        self.add_user_line(user_id=user_row.id,
                           extension_id=extension_row.id,
                           line_id=line_row.id)

        result = asterisk_conf_dao.find_exten_settings('default')

        assert_that(result, contains())

    def test_find_exten_settings_multiple_extensions(self):
        exten1 = self.add_extension(exten='12', context='default')
        exten2 = self.add_extension(exten='23', context='default')
        self.add_extension(exten='41', context='toto')

        expected_result = [
            {'exten': u'12',
             'commented': 0,
             'context': u'default',
             'typeval': u'',
             'type': 'user',
             'id': exten1.id},
            {'exten': u'23',
             'commented': 0,
             'context': u'default',
             'typeval': u'',
             'type': 'user',
             'id': exten2.id}
        ]

        extensions = asterisk_conf_dao.find_exten_settings('default')

        assert_that(extensions, contains_inanyorder(*expected_result))

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

        assert_that(context, contains_inanyorder(*expected_result))

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

        assert_that(context, contains_inanyorder(*expected_result))

    def test_find_voicemail_activated(self):
        vm = self.add_voicemail()
        self.add_voicemail(commented=1)

        expected = {'uniqueid': vm.uniqueid,
                    'deletevoicemail': 0,
                    'maxmsg': None,
                    'tz': None,
                    'attach': None,
                    'mailbox': vm.mailbox,
                    'uniqueid': vm.uniqueid,
                    'password': u'',
                    'pager': None,
                    'language': None,
                    'commented': 0,
                    'context': vm.context,
                    'skipcheckpass': 0,
                    'fullname': vm.fullname,
                    'options': []}

        voicemails = asterisk_conf_dao.find_voicemail_activated()

        assert_that(voicemails, contains(has_entries(expected)))

    def test_find_voicemail_general_settings(self):
        vms1 = self.add_voicemail_general_settings()
        vms2 = self.add_voicemail_general_settings()
        self.add_voicemail_general_settings(commented=1)

        expected_result = [
            {'category': u'general',
             'var_name': vms1.var_name,
             'var_val': vms1.var_val},
            {'category': u'general',
             'var_name': vms2.var_name,
             'var_val': vms2.var_val},
        ]

        voicemail_settings = asterisk_conf_dao.find_voicemail_general_settings()

        assert_that(voicemail_settings, contains_inanyorder(*expected_result))

    def test_find_sip_general_settings(self):
        sip1 = self.add_sip_general_settings()
        sip2 = self.add_sip_general_settings()
        self.add_sip_general_settings(commented=1)

        expected_result = [
            {'var_name': sip1.var_name,
             'var_val': sip1.var_val},
            {'var_name': sip2.var_name,
             'var_val': sip2.var_val},
        ]

        sip_settings = asterisk_conf_dao.find_sip_general_settings()

        assert_that(sip_settings, contains_inanyorder(*expected_result))

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

        assert_that(sip_authentication, contains_inanyorder(*expected_result))

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

        assert_that(sip_trunk, contains_inanyorder(*expected_result))

    def test_find_sip_user_settings_no_voicemail(self):
        usersip = self.add_usersip(category='user')
        self.add_user_line_with_exten(
            protocol='sip',
            protocolid=usersip.id,
            name_line=usersip.name,
            context=usersip.context,
        )

        results = asterisk_conf_dao.find_sip_user_settings()

        assert_that(results, contains(has_entry('mailbox', none())))

    def test_find_sip_user_settings(self):
        usersip = self.add_usersip(category='user')
        voicemail = self.add_voicemail(mailbox='1000', context='default')
        mailbox = '1000@default'

        ule = self.add_user_line_with_exten(
            protocol='sip',
            protocolid=usersip.id,
            name_line=usersip.name,
            context=usersip.context,
            musiconhold='mymusic',
            voicemail_id=voicemail.uniqueid
        )

        expected = {'number': ule.extension.exten,
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
                    'mohsuggest': 'mymusic',
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
                    'mailbox': mailbox,
                    'allow': None}

        results = asterisk_conf_dao.find_sip_user_settings()

        assert_that(results, contains(has_entries(expected)))

    def test_find_sip_user_settings_no_xivo_user(self):
        number, context = '1001', 'myctx'
        user_sip = self.add_usersip(
            category='user',
            context=context,
        )
        self.add_user_line_without_user(exten=number,
                                        context=context,
                                        protocol='sip',
                                        protocolid=user_sip.id,
                                        name='name')

        results = asterisk_conf_dao.find_sip_user_settings()

        assert_that(results, contains(has_entries('protocol', 'sip',
                                                  'number', number,
                                                  'context', context)))

    def test_find_sip_pickup_settings(self):
        category_to_conf_reverse_map = {'pickupgroup': 'member',
                                        'callgroup': 'pickup'}
        pickup = self.add_pickup()

        name1, user_id1 = self._create_user_with_usersip()
        name2, user_id2 = self._create_user_with_usersip()
        name3, user_id3 = self._create_user_with_usersip()

        user_member_category = self.add_pickup_member_user(pickup, user_id1)
        group_member_category = self.add_pickup_member_group(pickup, user_id2)
        queue_member_category = self.add_pickup_member_queue(pickup, user_id3)

        expected_result = [
            (name1, category_to_conf_reverse_map[user_member_category], pickup.id),
            (name2, category_to_conf_reverse_map[group_member_category], pickup.id),
            (name3, category_to_conf_reverse_map[queue_member_category], pickup.id),
        ]

        sip_pickup = asterisk_conf_dao.find_sip_pickup_settings()

        assert_that(sip_pickup, contains_inanyorder(*expected_result))

    def test_find_sip_pickup_settings_no_pickup(self):
        name1, user_id1 = self._create_user_with_usersip(exten='1001')
        name2, user_id2 = self._create_user_with_usersip(exten='1002')
        name3, user_id3 = self._create_user_with_usersip(exten='1003')

        with warning_filter('error'):
            sip_pickup = asterisk_conf_dao.find_sip_pickup_settings()

            assert_that(sip_pickup, contains_inanyorder())

    def _create_user_with_usersip(self, **kwargs):
        usersip = self.add_usersip(category='user')
        ule = self.add_user_line_with_exten(protocol='sip',
                                            protocolid=usersip.id,
                                            name_line=usersip.name,
                                            context=usersip.context,
                                            **kwargs)
        return usersip.name, ule.user_id

    def test_find_iax_general_settings(self):
        iax1 = self.add_iax_general_settings()
        iax2 = self.add_iax_general_settings()
        self.add_iax_general_settings(commented=1)

        expected_result = [
            {'var_name': iax1.var_name,
             'var_val': iax1.var_val},
            {'var_name': iax2.var_name,
             'var_val': iax2.var_val},
        ]

        iax_settings = asterisk_conf_dao.find_iax_general_settings()

        assert_that(iax_settings, contains_inanyorder(*expected_result))

    def test_find_iax_trunk_settings(self):
        self.add_useriax(category='user')
        iax = self.add_useriax(category='trunk')
        self.add_useriax(commented=1)

        expected_result = [
            {'accountcode': None,
             'adsi': None,
             'allow': None,
             'amaflags': u'default',
             'auth': u'plaintext,md5',
             'callerid': None,
             'category': iax.category,
             'cid_number': None,
             'codecpriority': None,
             'commented': 0,
             'context': iax.context,
             'dbsecret': u'',
             'defaultip': None,
             'deny': None,
             'disallow': None,
             'encryption': None,
             'forceencryption': None,
             'forcejitterbuffer': None,
             'fullname': None,
             'host': u'dynamic',
             'id': iax.id,
             'immediate': None,
             'inkeys': None,
             'ipaddr': u'',
             'jitterbuffer': None,
             'keyrotate': None,
             'language': None,
             'mailbox': None,
             'mask': None,
             'maxauthreq': None,
             'mohinterpret': None,
             'mohsuggest': None,
             'name': iax.name,
             'outkey': None,
             'parkinglot': None,
             'peercontext': None,
             'permit': None,
             'port': None,
             'protocol': u'iax',
             'qualify': u'no',
             'qualifyfreqnotok': 10000,
             'qualifyfreqok': 60000,
             'qualifysmoothing': 0,
             'regexten': None,
             'regseconds': 0,
             'requirecalltoken': u'no',
             'secret': u'',
             'sendani': 0,
             'setvar': u'',
             'sourceaddress': None,
             'timezone': None,
             'transfer': None,
             'trunk': 0,
             'type': iax.type,
             'username': None}
        ]

        iax_settings = asterisk_conf_dao.find_iax_trunk_settings()

        assert_that(iax_settings, contains_inanyorder(*expected_result))

    def test_find_iax_calllimits_settings(self):
        iax_call_number_limits = IAXCallNumberLimits(destination='toto',
                                                     netmask='',
                                                     calllimits=5)
        self.add_me(iax_call_number_limits)

        expected_result = [
            {'id': iax_call_number_limits.id,
             'destination': iax_call_number_limits.destination,
             'netmask': iax_call_number_limits.netmask,
             'calllimits': iax_call_number_limits.calllimits}
        ]

        iax_settings = asterisk_conf_dao.find_iax_calllimits_settings()

        assert_that(iax_settings, contains_inanyorder(*expected_result))

    def test_find_meetme_general_settings(self):
        self.add_meetme_general_settings(category='toto')
        meetme1 = self.add_meetme_general_settings(category='general')
        meetme2 = self.add_meetme_general_settings(category='general')
        self.add_meetme_general_settings(category='general', commented=1)

        expected_result = [
            {'category': u'general',
             'cat_metric': 0,
             'filename': u'meetme.conf',
             'var_metric': 0,
             'var_name': meetme1.var_name,
             'var_val': meetme1.var_val,
             'id': meetme1.id,
             'commented': 0},
            {'category': u'general',
             'cat_metric': 0,
             'filename': u'meetme.conf',
             'var_metric': 0,
             'var_name': meetme2.var_name,
             'var_val': meetme2.var_val,
             'id': meetme2.id,
             'commented': 0}
        ]

        meetme_settings = asterisk_conf_dao.find_meetme_general_settings()

        assert_that(meetme_settings, contains_inanyorder(*expected_result))

    def test_find_meetme_rooms_settings(self):
        self.add_meetme_general_settings(category='toto')
        meetme1 = self.add_meetme_general_settings(category='rooms')
        meetme2 = self.add_meetme_general_settings(category='rooms')
        self.add_meetme_general_settings(category='rooms', commented=1)

        expected_result = [
            {'category': u'rooms',
             'cat_metric': 0,
             'filename': u'meetme.conf',
             'var_metric': 0,
             'var_name': meetme1.var_name,
             'var_val': meetme1.var_val,
             'id': meetme1.id,
             'commented': 0},
            {'category': u'rooms',
             'cat_metric': 0,
             'filename': u'meetme.conf',
             'var_metric': 0,
             'var_name': meetme2.var_name,
             'var_val': meetme2.var_val,
             'id': meetme2.id,
             'commented': 0}
        ]

        meetme_settings = asterisk_conf_dao.find_meetme_rooms_settings()

        assert_that(meetme_settings, contains_inanyorder(*expected_result))

    def test_find_musiconhold_settings(self):
        musiconhold1 = self.add_musiconhold(category='default')
        musiconhold2 = self.add_musiconhold(category='default')
        musiconhold3 = self.add_musiconhold(category='toto')
        self.add_musiconhold(category='default', commented=1)

        expected_result = [
            {'category': u'default',
             'cat_metric': 0,
             'filename': u'musiconhold.conf',
             'var_metric': 0,
             'var_name': musiconhold1.var_name,
             'var_val': musiconhold1.var_val,
             'id': musiconhold1.id,
             'commented': 0},
            {'category': u'default',
             'cat_metric': 0,
             'filename': u'musiconhold.conf',
             'var_metric': 0,
             'var_name': musiconhold2.var_name,
             'var_val': musiconhold2.var_val,
             'id': musiconhold2.id,
             'commented': 0},
            {'category': u'toto',
             'cat_metric': 0,
             'filename': u'musiconhold.conf',
             'var_metric': 0,
             'var_name': musiconhold3.var_name,
             'var_val': musiconhold3.var_val,
             'id': musiconhold3.id,
             'commented': 0}
        ]

        musiconhold_settings = asterisk_conf_dao.find_musiconhold_settings()

        assert_that(musiconhold_settings, contains_inanyorder(*expected_result))

    def test_find_queue_general_settings(self):
        self.add_queue_general_settings(category='toto')
        queue_settings1 = self.add_queue_general_settings(category='general')
        queue_settings2 = self.add_queue_general_settings(category='general')
        self.add_queue_general_settings(category='general', commented=1)

        expected_result = [
            {'category': u'general',
             'cat_metric': 0,
             'filename': u'queues.conf',
             'var_metric': 0,
             'var_name': queue_settings1.var_name,
             'var_val': queue_settings1.var_val,
             'id': queue_settings1.id,
             'commented': 0},
            {'category': u'general',
             'cat_metric': 0,
             'filename': u'queues.conf',
             'var_metric': 0,
             'var_name': queue_settings2.var_name,
             'var_val': queue_settings2.var_val,
             'id': queue_settings2.id,
             'commented': 0}
        ]

        meetme_settings = asterisk_conf_dao.find_queue_general_settings()

        assert_that(meetme_settings, contains_inanyorder(*expected_result))

    def test_find_queue_settings(self):
        queue1 = self.add_queue()

        expected_result = [
            {
                'autopause': 'no',
                'weight': None,
                'autofill': 1,
                'queue-holdtime': None,
                'monitor-type': None,
                'joinempty': None,
                'announce-frequency': None,
                'category': queue1.category,
                'retry': None,
                'setqueueentryvar': 0,
                'periodic-announce-frequency': None,
                'defaultrule': None,
                'strategy': None,
                'queue-thankyou': None,
                'random-periodic-announce': 0,
                'setinterfacevar': 0,
                'queue-callswaiting': None,
                'announce': None,
                'wrapuptime': None,
                'leavewhenempty': None,
                'reportholdtime': 0,
                'queue-reporthold': None,
                'queue-youarenext': None,
                'timeout': 0,
                'announce-position': u'yes',
                'setqueuevar': 0,
                'periodic-announce': None,
                'announce-position-limit': 5,
                'min-announce-frequency': 60,
                'queue-thereare': None,
                'membermacro': None,
                'timeoutpriority': u'app',
                'announce-round-seconds': None,
                'memberdelay': None,
                'musicclass': None,
                'ringinuse': 0,
                'timeoutrestart': 0,
                'monitor-format': None,
                'name': queue1.name,
                'queue-minutes': None,
                'servicelevel': None,
                'maxlen': None,
                'context': None,
                'queue-seconds': None,
                'commented': 0,
                'announce-holdtime': None
            }
        ]

        queue = asterisk_conf_dao.find_queue_settings()

        assert_that(queue, contains_inanyorder(*expected_result))

    def test_find_queue_skillrule_settings(self):
        queue_skill_rule1 = self.add_queue_skill_rule()

        expected_result = [
            {'id': queue_skill_rule1.id,
             'rule': queue_skill_rule1.rule,
             'name': queue_skill_rule1.name}
        ]

        queue_skill_rule = asterisk_conf_dao.find_queue_skillrule_settings()

        assert_that(queue_skill_rule, contains_inanyorder(*expected_result))

    def test_find_queue_penalty_settings(self):
        queue_penalty1 = QueuePenalty(name='foo1',
                                      commented=1,
                                      description='')
        queue_penalty2 = QueuePenalty(name='foo2',
                                      commented=0,
                                      description='')
        queue_penalty3 = QueuePenalty(name='foo3',
                                      commented=0,
                                      description='')
        self.add_me_all([queue_penalty1,
                         queue_penalty2,
                         queue_penalty3])

        expected_result = [
            {'id': queue_penalty2.id,
             'name': queue_penalty2.name,
             'commented': queue_penalty2.commented,
             'description': queue_penalty2.description},
            {'id': queue_penalty3.id,
             'name': queue_penalty3.name,
             'commented': queue_penalty3.commented,
             'description': queue_penalty3.description}
        ]

        queue_penalty = asterisk_conf_dao.find_queue_penalty_settings()

        assert_that(queue_penalty, contains_inanyorder(*expected_result))

    def test_find_queue_members_settings(self):
        queue_name = 'toto'

        self.add_queue_member(queue_name=queue_name,
                              interface='Local/100@default',
                              usertype='user',
                              userid=2131,
                              penalty=1,
                              commented=0)

        self.add_queue_member(queue_name=queue_name,
                              interface='SIP/3m6dsc',
                              usertype='user',
                              userid=54,
                              penalty=5,
                              commented=0)

        self.add_queue_member(queue_name=queue_name,
                              interface='SCCP/1003',
                              usertype='user',
                              userid=1,
                              penalty=15,
                              commented=0)

        self.add_queue_member(queue_name=queue_name,
                              interface='SIP/dsf4rs',
                              usertype='user',
                              userid=3,
                              penalty=42,
                              commented=1)

        expected_result = [
            {
                'penalty': 1,
                'interface': 'Local/100@default'
            },
            {
                'penalty': 5,
                'interface': 'SIP/3m6dsc'
            },
            {
                'penalty': 15,
                'interface': 'SCCP/1003'
            }
        ]
        result = asterisk_conf_dao.find_queue_members_settings(queue_name)

        assert_that(result, contains_inanyorder(*expected_result))

    def test_find_agent_queue_skills_settings(self):
        agent1 = self.add_agent()
        queue_skill1 = self.add_queue_skill()
        agent_queue_skill1 = AgentQueueSkill(agentid=agent1.id,
                                             skillid=queue_skill1.id,
                                             weight=1)
        agent2 = self.add_agent()
        queue_skill2 = self.add_queue_skill()
        agent_queue_skill2 = AgentQueueSkill(agentid=agent2.id,
                                             skillid=queue_skill2.id,
                                             weight=1)
        self.add_me_all([agent_queue_skill1,
                         agent_queue_skill2])

        expected_result = [
            {'id': agent2.id,
             'weight': 1,
             'name': queue_skill2.name},
            {'id': agent1.id,
             'weight': 1,
             'name': queue_skill1.name}
        ]

        result = asterisk_conf_dao.find_agent_queue_skills_settings()

        assert_that(result, contains_inanyorder(*expected_result))

    def test_find_queue_penalties_settings(self):
        queue_penalty1 = QueuePenalty(name='foo1',
                                      commented=1,
                                      description='')
        queue_penalty2 = QueuePenalty(name='foo2',
                                      commented=0,
                                      description='')
        self.add_me_all([queue_penalty1, queue_penalty2])
        queue_penalty_change1 = QueuePenaltyChange(queuepenalty_id=queue_penalty1.id)
        queue_penalty_change2 = QueuePenaltyChange(queuepenalty_id=queue_penalty2.id)
        self.add_me_all([queue_penalty_change1, queue_penalty_change2])

        expected_result = [
            {
                'name': queue_penalty2.name,
                'maxp_sign': None,
                'seconds': 0,
                'minp_sign': None,
                'minp_value': None,
                'maxp_value': None
            }
        ]

        result = asterisk_conf_dao.find_queue_penalties_settings()

        assert_that(result, contains_inanyorder(*expected_result))
