# -*- coding: utf-8 -*-
# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

import warnings

from contextlib import contextmanager
from hamcrest import (
    all_of,
    assert_that,
    contains,
    contains_inanyorder,
    empty,
    equal_to,
    has_entries,
    has_items,
    has_length,
    has_properties,
    not_,
)

from mock import patch
from xivo_test_helpers.hamcrest.uuid_ import uuid_
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

    def add_pickup_member_user(self, pickup, user_id, category='member'):
        args = {
            'pickupid': pickup.id,
            'membertype': 'user',
            'memberid': user_id,
            'category': category,
        }

        pickup_member = self.add_pickup_member(**args)

        return self._category_to_conf(pickup_member.category)

    def add_pickup_member_group(self, pickup, user_id, category='member'):
        group = self.add_group()
        pickup_member = self.add_pickup_member(
            pickupid=pickup.id,
            membertype='group',
            memberid=group.id,
            category=category,
        )
        self.add_queue_member(
            queue_name=group.name,
            usertype='user',
            userid=user_id,
        )

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
        ule = self.add_user_line_with_exten(
            endpoint_sccp_id=sccp_line.id,
            exten=number,
        )

        sccp_lines = asterisk_conf_dao.find_sccp_line_settings()

        assert_that(sccp_lines, contains_inanyorder(
            has_entries(
                user_id=ule.user_id,
                name=sccp_line.name,
                language=None,
                number=number,
                cid_name='Tester One',
                context='foocontext',
                cid_num=number,
                uuid=uuid_()
            )
        ))

    def test_find_sccp_line_settings_when_line_disabled(self):
        number = '1234'
        sccp_line = self.add_sccpline(cid_num=number)
        self.add_user_line_with_exten(endpoint_sccp_id=sccp_line.id,
                                      exten=number,
                                      commented_line=1)

        sccp_line = asterisk_conf_dao.find_sccp_line_settings()

        assert_that(sccp_line, contains())

    def test_find_sccp_line_allow(self):
        number = '1234'
        sccp_line = self.add_sccpline(cid_num=number, allow='g729')
        ule = self.add_user_line_with_exten(
            endpoint_sccp_id=sccp_line.id,
            exten=number,
        )

        sccp_lines = asterisk_conf_dao.find_sccp_line_settings()

        assert_that(sccp_lines, contains(
            has_entries(
                user_id=ule.user_id,
                name=sccp_line.name,
                language=None,
                number=number,
                cid_name='Tester One',
                context='foocontext',
                cid_num=number,
                allow='g729',
                uuid=uuid_(),
            ),
        ))

    def test_find_sccp_line_disallow(self):
        number = '1234'
        sccp_line = self.add_sccpline(cid_num=number, allow='g729', disallow='all')
        ule = self.add_user_line_with_exten(
            endpoint_sccp_id=sccp_line.id,
            exten=number,
        )

        sccp_lines = asterisk_conf_dao.find_sccp_line_settings()

        assert_that(sccp_lines, contains(
            has_entries(
                user_id=ule.user_id,
                name=sccp_line.name,
                language=None,
                number=number,
                cid_name='Tester One',
                context='foocontext',
                cid_num=number,
                allow='g729',
                disallow='all',
                uuid=uuid_(),
            ),
        ))

    @patch('xivo_dao.asterisk_conf_dao.find_pickup_members')
    def test_find_sccp_line_pickup_group(self, mock_find_pickup_members):
        sccp_line = self.add_sccpline()
        ule = self.add_user_line_with_exten(endpoint_sccp_id=sccp_line.id)
        callgroups = set([1, 2, 3, 4])
        pickupgroups = set([3, 4])
        pickup_members = {
            sccp_line.id: {'callgroup': callgroups, 'pickupgroup': pickupgroups},
        }
        mock_find_pickup_members.return_value = pickup_members

        sccp_lines = asterisk_conf_dao.find_sccp_line_settings()

        assert_that(sccp_lines, contains(
            has_entries(
                user_id=ule.user_id,
                name=sccp_line.name,
                language=None,
                number=ule.extension.exten,
                cid_name='Tester One',
                context='foocontext',
                cid_num=sccp_line.cid_num,
                callgroup=callgroups,
                pickupgroup=pickupgroups,
                uuid=uuid_(),
            ),
        ))


class TestSccpConfDAO(DAOTestCase):

    def test_find_sccp_general_settings(self):
        expected_result = [
            {'option_name': 'directmedia', 'option_value': 'no'},
            {'option_name': 'dialtimeout', 'option_value': '6'},
            {'option_name': 'language', 'option_value': 'en_US'},
            {'option_name': 'vmexten', 'option_value': '*98'},
        ]

        self.add_sccp_general_settings(**expected_result[0])
        self.add_sccp_general_settings(**expected_result[1])
        self.add_sccp_general_settings(**expected_result[2])
        self.add_extension(exten='*98', type='extenfeatures', typeval='vmusermsg')

        sccp_general_settings = asterisk_conf_dao.find_sccp_general_settings()

        assert_that(sccp_general_settings, contains_inanyorder(*expected_result))

    def test_find_sccp_device_settings_no_voicemail(self):
        sccp_device = self.add_sccpdevice()

        sccp_devices = asterisk_conf_dao.find_sccp_device_settings()

        assert_that(sccp_devices, contains(
            has_entries(
                id=sccp_device.id,
                name=sccp_device.name,
                device=sccp_device.device,
                line=sccp_device.line,
                voicemail=None,
            ),
        ))

    def test_find_sccp_device_settings(self):
        extension = self.add_extension(exten='1000', context='default')
        sccp_device = self.add_sccpdevice(line=extension.exten)
        sccp_line = self.add_sccpline(name=extension.exten, context=extension.context)
        line = self.add_line(endpoint_sccp_id=sccp_line.id, context=extension.context)
        voicemail = self.add_voicemail(mailbox='2000')
        user = self.add_user(voicemailid=voicemail.uniqueid)
        self.add_user_line(user_id=user.id, line_id=line.id)

        sccp_devices = asterisk_conf_dao.find_sccp_device_settings()

        assert_that(sccp_devices, contains(
            has_entries(
                id=sccp_device.id,
                name=sccp_device.name,
                device=sccp_device.device,
                line=sccp_device.line,
                voicemail=voicemail.mailbox,
            ),
        ))


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

        assert_that(result, contains(
            has_entries(
                user_id=user_row.id,
                fknum=func_key_mapping_row.position,
                exten=func_key_exten,
                supervision=int(func_key_mapping_row.blf),
                label=func_key_mapping_row.label,
                device=sccp_device_row.device,
            ),
        ))

    def test_given_func_key_with_invalid_characters_then_characters_are_escaped(self):
        exten = '1000'
        func_key_exten = '\n2;0\t0\r0'
        context = 'default'
        label = '\nhe;l\tlo\r'

        user_row, sccp_device_row = self.add_user_with_sccp_device(exten=exten, context=context)
        self.add_custom_func_key_to_user(user_row, func_key_exten, label=label)

        result = asterisk_conf_dao.find_sccp_speeddial_settings()

        assert_that(result, contains(has_entries(exten='2000', label='hello')))

    def add_user_with_sccp_device(self, exten, context):
        user_row = self.add_user()
        sccp_device_row = self.add_sccpdevice(line=exten)
        sccp_line_row = self.add_sccpline(
            name=exten,
            cid_num=exten,
            context=context,
        )
        extension_row = self.add_extension(exten=exten, context=context)
        line_row = self.add_line(
            context=context,
            endpoint_sccp_id=sccp_line_row.id,
        )

        self.add_user_line(user_id=user_row.id, line_id=line_row.id)
        self.add_line_extension(line_id=line_row.id, extension_id=extension_row.id)

        return user_row, sccp_device_row

    def add_custom_func_key_to_user(self, user_row, func_key_exten, label='mylabel'):
        func_key_type_row = self.add_func_key_type(name='speeddial')
        func_key_dest_row = self.add_func_key_destination_type(id=10, name='custom')
        func_key_row = self.add_func_key(
            type_id=func_key_type_row.id,
            destination_type_id=func_key_dest_row.id,
        )
        self.add_func_key_dest_custom(
            func_key_id=func_key_row.id,
            destination_type_id=func_key_dest_row.id,
            exten=func_key_exten,
        )
        func_key_mapping = self.add_func_key_mapping(
            template_id=user_row.func_key_private_template_id,
            func_key_id=func_key_row.id,
            destination_type_id=func_key_dest_row.id,
            label=label,
            position=2,
            blf=True,
        )
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

        sip = self.add_endpoint_sip()
        ule = self.add_user_line_with_exten(endpoint_sip_uuid=sip.uuid)
        category = self.add_pickup_member_user(pickup, ule.user_id)

        pickup_members = asterisk_conf_dao.find_pickup_members('sip')

        assert_that(pickup_members, equal_to(
            {sip.uuid: {category: set([pickup.id])}},
        ))

    def test_find_pickup_members_with_sccp_users(self):
        pickup = self.add_pickup()

        sccp_line = self.add_sccpline()
        ule = self.add_user_line_with_exten(endpoint_sccp_id=sccp_line.id)
        category = self.add_pickup_member_user(pickup, ule.user_id)

        pickup_members = asterisk_conf_dao.find_pickup_members('sccp')

        assert_that(pickup_members, equal_to(
            {sccp_line.id: {category: set([pickup.id])}}
        ))

    def test_find_pickup_members_with_groups(self):
        pickup = self.add_pickup()

        sip = self.add_endpoint_sip()
        ule = self.add_user_line_with_exten(endpoint_sip_uuid=sip.uuid)
        category = self.add_pickup_member_group(pickup, ule.user_id)

        pickup_members = asterisk_conf_dao.find_pickup_members('sip')

        assert_that(pickup_members, equal_to(
            {sip.uuid: {category: set([pickup.id])}}
        ))

    def test_find_pickup_members_with_queues(self):
        pickup = self.add_pickup()

        sip = self.add_endpoint_sip()
        ule = self.add_user_line_with_exten(endpoint_sip_uuid=sip.uuid)
        category = self.add_pickup_member_queue(pickup, ule.user_id)

        pickup_members = asterisk_conf_dao.find_pickup_members('sip')

        assert_that(pickup_members, equal_to(
            {sip.uuid: {category: set([pickup.id])}}
        ))

    def test_find_features_settings(self):
        self.add_features(var_name='atxfernoanswertimeout', var_val='15')
        self.add_features(var_name='parkext', var_val='700')
        self.add_features(category='featuremap', var_name='atxfer', var_val='*2')
        self.add_features(category='featuremap', var_name='automixmon', var_val='*3')

        settings = asterisk_conf_dao.find_features_settings()

        assert_that(settings['general_options'], contains_inanyorder(
            ('atxfernoanswertimeout', '15'),
        ))
        assert_that(settings['featuremap_options'], contains_inanyorder(
            ('atxfer', '*2'),
            ('automixmon', '*3'),
        ))

    def test_find_features_settings_atxfer_abort_same_as_disconnect(self):
        self.add_features(category='featuremap', var_name='disconnect', var_val='*0')

        settings = asterisk_conf_dao.find_features_settings()

        assert_that(settings['general_options'], contains_inanyorder(
            ('atxferabort', '*0'),
        ))
        assert_that(settings['featuremap_options'], contains_inanyorder(
            ('disconnect', '*0'),
        ))

    def test_find_parking_settings(self):
        self.add_features(var_name='parkeddynamic', var_val='no')
        self.add_features(var_name='atxferdropcall', var_val='no')
        self.add_features(var_name='parkext', var_val='700')

        settings = asterisk_conf_dao.find_parking_settings()

        assert_that(settings['general_options'], contains_inanyorder(
            ('parkeddynamic', 'no'),
        ))
        assert_that(settings['parking_lots'], contains_inanyorder(
            has_entries(
                name='default',
                options=[('parkext', '700')],
            ),
        ))

    def test_find_exten_conferences_settings(self):
        conference = self.add_meetmefeatures(context='test')

        conference_extens = asterisk_conf_dao.find_exten_conferences_settings('test')

        assert_that(conference_extens, contains_inanyorder(
            has_entries(exten=conference.confno),
        ))

    def test_find_exten_conferences_settings_different_context(self):
        self.add_meetmefeatures(context='test')

        conference_extens = asterisk_conf_dao.find_exten_conferences_settings('default')

        assert_that(conference_extens, has_length(0))

    def test_find_exten_xivofeatures_setting(self):
        exten1 = self.add_extension(exten='*25', context='xivo-features')
        exten2 = self.add_extension(exten='*26', context='xivo-features')
        self.add_extension(exten='3492', context='robert', type='user', typeval='14')

        extensions = asterisk_conf_dao.find_exten_xivofeatures_setting()

        assert_that(extensions, contains_inanyorder(
            has_entries(
                exten='*25',
                commented=0,
                context='xivo-features',
                typeval='',
                type='user',
                id=exten1.id,
            ),
            has_entries(
                exten='*26',
                commented=0,
                context='xivo-features',
                typeval='',
                type='user',
                id=exten2.id,
            ),
        ))

    def test_find_extenfeatures_settings(self):
        exten1 = self.add_extension(
            exten='*98',
            context='xivo-features',
            type='extenfeatures',
            typeval='vmusermsg',
        )
        exten2 = self.add_extension(
            exten='*92',
            context='xivo-features',
            type='extenfeatures',
            typeval='vmuserpurge',
        )
        self.add_extension(
            exten='3492',
            context='robert',
            type='user',
            typeval='14',
        )

        extensions = asterisk_conf_dao.find_extenfeatures_settings(['vmusermsg', 'vmuserpurge'])

        assert_that(extensions, contains_inanyorder(
            has_properties(
                exten='*98',
                commented=0,
                context='xivo-features',
                typeval='vmusermsg',
                type='extenfeatures',
                id=exten1.id
            ),
            has_properties(
                exten='*92',
                commented=0,
                context='xivo-features',
                typeval='vmuserpurge',
                type='extenfeatures',
                id=exten2.id
            ),
        ))

    def test_find_exten_settings_when_line_enabled(self):
        default = self.add_context(name='default')
        user_row = self.add_user()
        line_row = self.add_line()
        extension_row = self.add_extension(exten='12', context='default')
        self.add_user_line(user_id=user_row.id, line_id=line_row.id)
        self.add_line_extension(line_id=line_row.id, extension_id=extension_row.id)

        result = asterisk_conf_dao.find_exten_settings('default')

        assert_that(result, contains(
            has_entries(
                exten='12',
                commented=0,
                context='default',
                typeval='',
                type='user',
                id=extension_row.id,
                tenant_uuid=default.tenant_uuid,
            ),
        ))

    def test_find_exten_settings_when_line_disabled(self):
        user_row = self.add_user()
        line_row = self.add_line(commented=1)
        extension_row = self.add_extension(exten='13', context='default')
        self.add_user_line(user_id=user_row.id, line_id=line_row.id)
        self.add_line_extension(line_id=line_row.id, extension_id=extension_row.id)

        result = asterisk_conf_dao.find_exten_settings('default')

        assert_that(result, contains())

    def test_find_exten_settings_multiple_extensions(self):
        default = self.add_context(name='default')
        self.add_context(name='toto')
        exten1 = self.add_extension(exten='12', context=default.name)
        exten2 = self.add_extension(exten='23', context=default.name)
        self.add_extension(exten='41', context='toto')

        extensions = asterisk_conf_dao.find_exten_settings('default')

        assert_that(extensions, contains_inanyorder(
            has_entries(
                exten='12',
                commented=0,
                context='default',
                typeval='',
                type='user',
                id=exten1.id,
                tenant_uuid=default.tenant_uuid,
            ),
            has_entries(
                exten='23',
                commented=0,
                context='default',
                typeval='',
                type='user',
                id=exten2.id,
                tenant_uuid=default.tenant_uuid,
            ),
        ))

    def test_find_exten_settings_when_not_associated(self):
        self.add_extension(context='default', typeval='0')
        extensions = asterisk_conf_dao.find_exten_settings('default')
        assert_that(extensions, empty())

    def test_find_exten_settings_when_type_parking(self):
        self.add_extension(context='default', type='parking')
        extensions = asterisk_conf_dao.find_exten_settings('default')
        assert_that(extensions, empty())

    def test_find_context_settings(self):
        context1 = self.add_context()
        context2 = self.add_context()

        context = asterisk_conf_dao.find_context_settings()

        assert_that(context, contains_inanyorder(
            has_entries(
                displayname=context1.displayname,
                description=context1.description,
                contexttype=context1.contexttype,
                commented=context1.commented,
                name=context1.name
            ),
            has_entries(
                displayname=context2.displayname,
                description=context2.description,
                contexttype=context2.contexttype,
                commented=context2.commented,
                name=context2.name
            ),
        ))

    def test_find_contextincludes_settings(self):
        context = 'default'
        self.add_context_include(context='koki')
        context_include = self.add_context_include(context=context)
        self.add_context_include(context='toto')

        context = asterisk_conf_dao.find_contextincludes_settings(context)

        assert_that(context, contains_inanyorder(
            has_entries(
                context=context_include.context,
                include=context_include.include,
                priority=context_include.priority,
            ),
        ))

    def test_find_voicemail_activated(self):
        vm = self.add_voicemail()
        self.add_voicemail(commented=1)

        voicemails = asterisk_conf_dao.find_voicemail_activated()

        assert_that(voicemails, contains(
            has_entries(
                uniqueid=vm.uniqueid,
                deletevoicemail=0,
                maxmsg=None,
                tz=None,
                attach=None,
                mailbox=vm.mailbox,
                password=None,
                pager=None,
                language=None,
                commented=0,
                context=vm.context,
                skipcheckpass=0,
                fullname=vm.fullname,
                options=[],
            ),
        ))

    def test_find_voicemail_general_settings(self):
        vms1 = self.add_voicemail_general_settings()
        vms2 = self.add_voicemail_general_settings()
        self.add_voicemail_general_settings(commented=1)

        voicemail_settings = asterisk_conf_dao.find_voicemail_general_settings()

        assert_that(voicemail_settings, contains_inanyorder(
            {'category': 'general', 'var_name': vms1.var_name, 'var_val': vms1.var_val},
            {'category': 'general', 'var_name': vms2.var_name, 'var_val': vms2.var_val},
        ))

    def test_find_sip_general_settings(self):
        sip1 = self.add_sip_general_settings()
        sip2 = self.add_sip_general_settings()
        self.add_sip_general_settings(commented=1)

        sip_settings = asterisk_conf_dao.find_sip_general_settings()

        assert_that(sip_settings, contains_inanyorder(
            {'var_name': sip1.var_name, 'var_val': sip1.var_val},
            {'var_name': sip2.var_name, 'var_val': sip2.var_val},
        ))

    def test_find_iax_general_settings(self):
        iax1 = self.add_iax_general_settings()
        iax2 = self.add_iax_general_settings()
        self.add_iax_general_settings(commented=1)

        iax_settings = asterisk_conf_dao.find_iax_general_settings()

        assert_that(iax_settings, contains_inanyorder(
            {'var_name': iax1.var_name, 'var_val': iax1.var_val},
            {'var_name': iax2.var_name, 'var_val': iax2.var_val},
        ))

    def test_find_iax_trunk_settings(self):
        self.add_useriax(category='user')
        iax = self.add_useriax(category='trunk')
        self.add_useriax(commented=1)

        iax_settings = asterisk_conf_dao.find_iax_trunk_settings()

        assert_that(iax_settings, contains_inanyorder(
            has_properties(
                accountcode=None,
                adsi=None,
                allow=None,
                amaflags='default',
                auth='plaintext,md5',
                callerid=None,
                category=iax.category,
                cid_number=None,
                codecpriority=None,
                commented=0,
                context=iax.context,
                dbsecret='',
                defaultip=None,
                deny=None,
                disallow=None,
                encryption=None,
                forceencryption=None,
                forcejitterbuffer=None,
                fullname=None,
                host='dynamic',
                id=iax.id,
                immediate=None,
                inkeys=None,
                jitterbuffer=None,
                keyrotate=None,
                language=None,
                mailbox=None,
                mask=None,
                maxauthreq=None,
                mohinterpret=None,
                mohsuggest=None,
                name=iax.name,
                outkey=None,
                parkinglot=None,
                peercontext=None,
                permit=None,
                port=None,
                protocol='iax',
                qualify='no',
                qualifyfreqnotok=10000,
                qualifyfreqok=60000,
                qualifysmoothing=0,
                regexten=None,
                requirecalltoken='no',
                secret='',
                sendani=0,
                setvar='',
                sourceaddress=None,
                timezone=None,
                transfer=None,
                trunk=0,
                type=iax.type,
                username=None
            ),
        ))

    def test_find_iax_calllimits_settings(self):
        iax_call_number_limits = IAXCallNumberLimits(
            destination='toto',
            netmask='',
            calllimits=5,
        )
        self.add_me(iax_call_number_limits)

        iax_settings = asterisk_conf_dao.find_iax_calllimits_settings()

        assert_that(iax_settings, contains_inanyorder(
            has_entries(
                id=iax_call_number_limits.id,
                destination=iax_call_number_limits.destination,
                netmask=iax_call_number_limits.netmask,
                calllimits=iax_call_number_limits.calllimits,
            ),
        ))

    def test_find_meetme_general_settings(self):
        self.add_meetme_general_settings(category='toto')
        meetme1 = self.add_meetme_general_settings(category='general')
        meetme2 = self.add_meetme_general_settings(category='general')
        self.add_meetme_general_settings(category='general', commented=1)

        meetme_settings = asterisk_conf_dao.find_meetme_general_settings()

        assert_that(meetme_settings, contains_inanyorder(
            has_entries(
                category='general',
                cat_metric=0,
                filename='meetme.conf',
                var_metric=0,
                var_name=meetme1.var_name,
                var_val=meetme1.var_val,
                id=meetme1.id,
                commented=0,
            ),
            has_entries(
                category='general',
                cat_metric=0,
                filename='meetme.conf',
                var_metric=0,
                var_name=meetme2.var_name,
                var_val=meetme2.var_val,
                id=meetme2.id,
                commented=0,
            ),
        ))

    def test_find_meetme_rooms_settings(self):
        self.add_meetme_general_settings(category='toto')
        meetme1 = self.add_meetme_general_settings(category='rooms')
        meetme2 = self.add_meetme_general_settings(category='rooms')
        self.add_meetme_general_settings(category='rooms', commented=1)

        meetme_settings = asterisk_conf_dao.find_meetme_rooms_settings()

        assert_that(meetme_settings, contains_inanyorder(
            has_entries(
                category='rooms',
                cat_metric=0,
                filename='meetme.conf',
                var_metric=0,
                var_name=meetme1.var_name,
                var_val=meetme1.var_val,
                id=meetme1.id,
                commented=0,
            ),
            has_entries(
                category='rooms',
                cat_metric=0,
                filename='meetme.conf',
                var_metric=0,
                var_name=meetme2.var_name,
                var_val=meetme2.var_val,
                id=meetme2.id,
                commented=0,
            ),
        ))

    def test_find_queue_general_settings(self):
        self.add_queue_general_settings(category='toto')
        queue_settings1 = self.add_queue_general_settings(category='general')
        queue_settings2 = self.add_queue_general_settings(category='general')
        self.add_queue_general_settings(category='general', commented=1)

        meetme_settings = asterisk_conf_dao.find_queue_general_settings()

        assert_that(meetme_settings, contains_inanyorder(
            has_entries(
                category='general',
                cat_metric=0,
                filename='queues.conf',
                var_metric=0,
                var_name=queue_settings1.var_name,
                var_val=queue_settings1.var_val,
                id=queue_settings1.id,
                commented=0,
            ),
            has_entries(
                category='general',
                cat_metric=0,
                filename='queues.conf',
                var_metric=0,
                var_name=queue_settings2.var_name,
                var_val=queue_settings2.var_val,
                id=queue_settings2.id,
                commented=0,
            ),
        ))

    def test_find_queue_settings(self):
        queue1 = self.add_queue()

        queue = asterisk_conf_dao.find_queue_settings()

        assert_that(queue, contains_inanyorder(
            has_entries({
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
                'announce-position': 'yes',
                'setqueuevar': 0,
                'periodic-announce': None,
                'announce-position-limit': 5,
                'min-announce-frequency': 60,
                'queue-thereare': None,
                'membermacro': None,
                'timeoutpriority': 'app',
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
            }),
        ))

    def test_find_queue_skillrule_settings(self):
        queue_skill_rule1 = self.add_queue_skill_rule()

        queue_skill_rule = asterisk_conf_dao.find_queue_skillrule_settings()

        assert_that(queue_skill_rule, contains_inanyorder(
            has_entries(
                id=queue_skill_rule1.id,
                rule=queue_skill_rule1.rule,
                name=queue_skill_rule1.name,
            ),
        ))

    def test_find_queue_penalty_settings(self):
        queue_penalty1 = QueuePenalty(name='foo1', commented=1, description='')
        queue_penalty2 = QueuePenalty(name='foo2', commented=0, description='')
        queue_penalty3 = QueuePenalty(name='foo3', commented=0, description='')
        self.add_me_all([queue_penalty1, queue_penalty2, queue_penalty3])

        queue_penalty = asterisk_conf_dao.find_queue_penalty_settings()

        assert_that(queue_penalty, contains_inanyorder(
            has_entries(
                id=queue_penalty2.id,
                name=queue_penalty2.name,
                commented=queue_penalty2.commented,
                description=queue_penalty2.description,
            ),
            has_entries(
                id=queue_penalty3.id,
                name=queue_penalty3.name,
                commented=queue_penalty3.commented,
                description=queue_penalty3.description,
            ),
        ))

    def test_find_queue_members_settings(self):
        queue_name = 'toto'

        self.add_queue_member(
            queue_name=queue_name,
            interface='Local/100@default',
            usertype='user',
            userid=2131,
            penalty=1,
            commented=0,
        )

        self.add_queue_member(
            queue_name=queue_name,
            interface='SIP/3m6dsc',
            usertype='user',
            userid=54,
            penalty=5,
            commented=0,
        )

        self.add_queue_member(
            queue_name=queue_name,
            interface='SCCP/1003',
            usertype='user',
            userid=1,
            penalty=15,
            commented=0,
        )

        self.add_queue_member(
            queue_name=queue_name,
            interface='SIP/dsf4rs',
            usertype='user',
            userid=3,
            penalty=42,
            commented=1,
        )

        result = asterisk_conf_dao.find_queue_members_settings(queue_name)
        assert_that(result, contains_inanyorder(
            contains('Local/100@default', '1', '', ''),
            contains('PJSIP/3m6dsc', '5', '', ''),
            contains('SCCP/1003', '15', '', ''),
        ))

        group_name = 'group'
        user = self.add_user()
        self.add_queue_member(
            queue_name=group_name,
            interface='ignored',
            usertype='user',
            userid=user.id,
            category='group',
            penalty=0,
            commented=0,
        )

        result = asterisk_conf_dao.find_queue_members_settings(group_name)
        assert_that(result, contains_inanyorder(
            contains(
                'Local/{}@usersharedlines'.format(user.uuid),
                '0',
                '',
                'hint:{}@usersharedlines'.format(user.uuid),
            ),
        ))

    def test_find_agent_queue_skills_settings(self):
        agent1 = self.add_agent()
        queue_skill1 = self.add_queue_skill()
        agent_queue_skill1 = AgentQueueSkill(
            agentid=agent1.id,
            skillid=queue_skill1.id,
            weight=1,
        )
        agent2 = self.add_agent()
        queue_skill2 = self.add_queue_skill()
        agent_queue_skill2 = AgentQueueSkill(
            agentid=agent2.id,
            skillid=queue_skill2.id,
            weight=1,
        )
        self.add_me_all([agent_queue_skill1, agent_queue_skill2])

        result = asterisk_conf_dao.find_agent_queue_skills_settings()

        assert_that(result, contains_inanyorder(
            has_entries(
                id=agent2.id,
                weight=1,
                name=queue_skill2.name,
            ),
            has_entries(
                id=agent1.id,
                weight=1,
                name=queue_skill1.name,
            ),
        ))

    def test_find_queue_penalties_settings(self):
        queue_penalty1 = QueuePenalty(name='foo1', commented=1, description='')
        queue_penalty2 = QueuePenalty(name='foo2', commented=0, description='')
        self.add_me_all([queue_penalty1, queue_penalty2])
        queue_penalty_change1 = QueuePenaltyChange(queuepenalty_id=queue_penalty1.id)
        queue_penalty_change2 = QueuePenaltyChange(queuepenalty_id=queue_penalty2.id)
        self.add_me_all([queue_penalty_change1, queue_penalty_change2])

        result = asterisk_conf_dao.find_queue_penalties_settings()

        assert_that(result, contains_inanyorder(
            has_entries(
                name=queue_penalty2.name,
                maxp_sign=None,
                seconds=0,
                minp_sign=None,
                minp_value=None,
                maxp_value=None
            ),
        ))

    def _create_user_with_usersip(self, **kwargs):
        context = self.add_context()
        endpoint_sip = self.add_endpoint_sip(context=context.name)
        ule = self.add_user_line_with_exten(
            endpoint_sip_uuid=endpoint_sip.uuid,
            name_line=endpoint_sip.name,
            context=context.name,
            **kwargs
        )
        return endpoint_sip.name, ule.user_id


class BaseFindSIPSettings(DAOTestCase):

    def setUp(self):
        super(BaseFindSIPSettings, self).setUp()
        transport_udp = self.add_transport(name='transport-udp')
        sip_general_body = {
            'label': 'General config',
            'aor_section_options': [
                ['max_contacts', '1'],
                ['remove_existing', 'true'],
                ['qualify_frequency', '60'],
                ['maximum_expiration', '3600'],
                ['minimum_expiration', '60'],
                ['default_expiration', '120'],
            ],
            'endpoint_section_options': [
                ['allow', '!all,ulaw'],
                ['allow_subscribe', 'yes'],
                ['allow_transfer', 'yes'],
                ['use_ptime', 'yes'],
                ['rtp_timeout', '7200'],
                ['rtp_timeout_hold', '0'],
                ['timers_sess_expires', '600'],
                ['timers_min_se', '90'],
                ['trust_id_inbound', 'yes'],
                ['dtmf_mode', 'rfc4733'],
                ['send_rpid', 'yes'],
                ['inband_progress', 'no'],
                ['direct_media', 'no'],
                ['callerid', 'wazo'],
            ],
            'template': True,
        }
        self.general_config_template = self.add_endpoint_sip(
            transport=transport_udp,
            **sip_general_body
        )


class TestFindSipUserSettings(BaseFindSIPSettings, PickupHelperMixin):

    def setUp(self):
        super(TestFindSipUserSettings, self).setUp()
        transport_wss = self.add_transport(name='transport-wss')
        webrtc_body = {
            'label': 'WebRTC line',
            'aor_section_options': [
                ['max_contacts', '10'],
                ['remove_existing', 'false']
            ],
            'endpoint_section_options': [
                ['webrtc', 'yes'],
            ],
            'template': True,
        }
        self.webrtc_config_template = self.add_endpoint_sip(
            transport=transport_wss,
            **webrtc_body
        )

    def test_given_no_sip_accounts_then_returns_empty_list(self):
        result = asterisk_conf_dao.find_sip_user_settings()
        assert_that(result, contains())

    def test_given_sip_account_is_not_associated_then_returns_empty_list(self):
        self.add_endpoint_sip(template=False)
        result = asterisk_conf_dao.find_sip_user_settings()
        assert_that(result, contains())

    def test_given_sip_account_is_associated_to_trunk_then_returns_empty_list(self):
        endpoint = self.add_endpoint_sip(template=False)
        self.add_trunk(endpoint_sip_uuid=endpoint.uuid)
        result = asterisk_conf_dao.find_sip_user_settings()
        assert_that(result, contains())

    def test_that_templates_are_included(self):
        endpoint = self.add_endpoint_sip(
            label='my line',
            template=False,
            templates=[self.general_config_template, self.webrtc_config_template],
            endpoint_section_options=[
                ['callerid', '"Foo Bar" <101>'],
            ],
            auth_section_options=[
                ['username', 'iddqd'],
                ['password', 'idbehold'],
            ],
        )
        self.add_line(endpoint_sip_uuid=endpoint.uuid)

        result = asterisk_conf_dao.find_sip_user_settings()
        assert_that(result, contains_inanyorder(
            has_entries(
                name=endpoint.name,
                label=endpoint.label,
                aor_section_options=has_items(
                    contains('qualify_frequency', '60'),
                    contains('maximum_expiration', '3600'),
                    contains('minimum_expiration', '60'),
                    contains('default_expiration', '120'),
                    contains('max_contacts', '10'),
                    contains('remove_existing', 'false')
                ),
                auth_section_options=has_items(
                    contains('username', 'iddqd'),
                    contains('password', 'idbehold'),
                ),
                endpoint_section_options=has_items(
                    contains('allow', '!all,ulaw'),
                    contains('allow_subscribe', 'yes'),
                    contains('allow_transfer', 'yes'),
                    contains('use_ptime', 'yes'),
                    contains('rtp_timeout', '7200'),
                    contains('rtp_timeout_hold', '0'),
                    contains('timers_sess_expires', '600'),
                    contains('timers_min_se', '90'),
                    contains('trust_id_inbound', 'yes'),
                    contains('dtmf_mode', 'rfc4733'),
                    contains('send_rpid', 'yes'),
                    contains('inband_progress', 'no'),
                    contains('direct_media', 'no'),
                    contains('callerid', '"Foo Bar" <101>'),
                    contains('webrtc', 'yes'),
                )
            ),
        ))

    def test_that_the_line_context_is_used(self):
        context = self.add_context()
        endpoint = self.add_endpoint_sip(template=False)
        self.add_line(endpoint_sip_uuid=endpoint.uuid, context=context.name)

        result = asterisk_conf_dao.find_sip_user_settings()
        assert_that(
            result,
            contains(has_entries(
                endpoint_section_options=has_items(contains('context', context.name)),
            )),
        )

    def test_that_the_transfer_context_is_added(self):
        context = self.add_context()
        endpoint = self.add_endpoint_sip(template=False)
        self.add_line(endpoint_sip_uuid=endpoint.uuid, context=context.name)

        result = asterisk_conf_dao.find_sip_user_settings()
        assert_that(
            result,
            contains(has_entries(
                endpoint_section_options=has_items(
                    contains('set_var', 'TRANSFER_CONTEXT={}'.format(context.name)),
                ),
            )),
        )

    def test_that_the_transport_is_used_from_endpoint(self):
        transport = self.add_transport()
        endpoint = self.add_endpoint_sip(
            templates=[self.general_config_template, self.webrtc_config_template],
            transport_uuid=transport.uuid,
            template=False,
        )
        self.add_line(endpoint_sip_uuid=endpoint.uuid)

        result = asterisk_conf_dao.find_sip_user_settings()
        assert_that(
            result,
            contains(has_entries(
                endpoint_section_options=has_items(
                    contains('transport', transport.name),
                ),
            )),
        )

    def test_that_the_transport_is_used_from_a_template(self):
        endpoint = self.add_endpoint_sip(
            templates=[self.general_config_template, self.webrtc_config_template],
            template=False,
        )
        self.add_line(endpoint_sip_uuid=endpoint.uuid)

        result = asterisk_conf_dao.find_sip_user_settings()
        assert_that(
            result,
            contains(has_entries(
                endpoint_section_options=has_items(
                    # inherited from the webrtc template
                    contains('transport', 'transport-wss'),
                ),
            )),
        )

    def test_that_the_main_extension_is_used_as_a_pickup_mark(self):
        endpoint = self.add_endpoint_sip(template=False)
        extension = self.add_extension()
        line = self.add_line(endpoint_sip_uuid=endpoint.uuid)
        self.add_line_extension(line_id=line.id, extension_id=extension.id)

        result = asterisk_conf_dao.find_sip_user_settings()
        assert_that(
            result,
            contains(has_entries(
                endpoint_section_options=has_items(
                    contains(
                        'set_var',
                        'PICKUPMARK={}%{}'.format(extension.exten, extension.context)
                    ),
                ),
            )),
        )

    def test_that_aor_mailboxes_contains_all_of_the_users_voicemail(self):
        user = self.add_user()
        voicemail = self.add_voicemail()
        self.link_user_and_voicemail(user, voicemail.uniqueid)
        endpoint = self.add_endpoint_sip(template=False)
        line = self.add_line(endpoint_sip_uuid=endpoint.uuid)
        self.add_user_line(user_id=user.id, line_id=line.id)

        result = asterisk_conf_dao.find_sip_user_settings()
        assert_that(
            result,
            contains(has_entries(
                aor_section_options=has_items(
                    contains(
                        'mailboxes',
                        '{}@{}'.format(voicemail.number, voicemail.context)
                    ),
                ),
            )),
        )

    def test_that_the_xivo_caller_id_var_is_set(self):
        caller_id = '"Foo" <123>'
        endpoint = self.add_endpoint_sip(
            endpoint_section_options=[['callerid', caller_id]],
            template=False,
        )
        self.add_line(endpoint_sip_uuid=endpoint.uuid)

        result = asterisk_conf_dao.find_sip_user_settings()
        assert_that(
            result,
            contains(has_entries(
                endpoint_section_options=has_items(
                    contains(
                        'set_var',
                        'XIVO_ORIGINAL_CALLER_ID={}'.format(caller_id),
                    ),
                ),
            )),
        )

    def test_that_the_channel_direction_var_is_set(self):
        endpoint = self.add_endpoint_sip(template=False)
        self.add_line(endpoint_sip_uuid=endpoint.uuid)

        result = asterisk_conf_dao.find_sip_user_settings()
        assert_that(
            result,
            contains(has_entries(
                endpoint_section_options=has_items(
                    ['set_var', 'WAZO_CHANNEL_DIRECTION=from-wazo'],
                ),
            )),
        )

    def test_that_the_user_id_var_is_set(self):
        user = self.add_user()
        endpoint = self.add_endpoint_sip(template=False)
        line = self.add_line(endpoint_sip_uuid=endpoint.uuid)
        self.add_user_line(user_id=user.id, line_id=line.id)

        result = asterisk_conf_dao.find_sip_user_settings()
        assert_that(
            result,
            contains(has_entries(
                endpoint_section_options=has_items(
                    ['set_var', 'XIVO_USERID={}'.format(user.id)],
                ),
            )),
        )

    def test_that_the_user_uuid_var_is_set(self):
        user = self.add_user()
        endpoint = self.add_endpoint_sip(template=False)
        line = self.add_line(endpoint_sip_uuid=endpoint.uuid)
        self.add_user_line(user_id=user.id, line_id=line.id)

        result = asterisk_conf_dao.find_sip_user_settings()
        assert_that(
            result,
            contains(has_entries(
                endpoint_section_options=has_items(
                    ['set_var', 'XIVO_USERUUID={}'.format(user.uuid)],
                    # ['set_var', 'WAZO_USER_UUID={}'.format(user.uuid)],
                ),
            )),
        )

    def test_that_the_tenant_uuid_var_is_set(self):
        endpoint = self.add_endpoint_sip(template=False)
        self.add_line(endpoint_sip_uuid=endpoint.uuid)

        result = asterisk_conf_dao.find_sip_user_settings()
        assert_that(
            result,
            contains(has_entries(
                endpoint_section_options=has_items(
                    ['set_var', 'WAZO_TENANT_UUID={}'.format(endpoint.tenant_uuid)],
                ),
            )),
        )

    def test_that_the_line_id_var_is_set(self):
        user = self.add_user()
        endpoint = self.add_endpoint_sip(template=False)
        line = self.add_line(endpoint_sip_uuid=endpoint.uuid)
        self.add_user_line(user_id=user.id, line_id=line.id)

        result = asterisk_conf_dao.find_sip_user_settings()
        assert_that(
            result,
            contains(has_entries(
                endpoint_section_options=has_items(
                    ['set_var', 'WAZO_LINE_ID={}'.format(line.id)],
                ),
            )),
        )

    def test_that_all_section_reference_are_added(self):
        endpoint = self.add_endpoint_sip(
            templates=[self.general_config_template, self.webrtc_config_template],
            auth_section_options=[['username', 'foo']],
            template=False,
        )
        self.add_line(endpoint_sip_uuid=endpoint.uuid)

        result = asterisk_conf_dao.find_sip_user_settings()
        assert_that(
            result,
            contains(has_entries(
                aor_section_options=has_items(
                    contains('type', 'aor'),
                ),
                auth_section_options=has_items(
                    contains('type', 'auth'),
                ),
                endpoint_section_options=has_items(
                    contains('type', 'endpoint'),
                    contains('auth', endpoint.name),
                    contains('aors', endpoint.name),
                ),
            )),
        )

    def test_that_named_pickup_groups_are_added(self):
        pickup_user = self.add_pickup()
        pickup_group = self.add_pickup()

        sip = self.add_endpoint_sip(template=False)
        ule = self.add_user_line_with_exten(endpoint_sip_uuid=sip.uuid)
        self.add_pickup_member_user(pickup_user, ule.user_id, category='member')
        self.add_pickup_member_group(pickup_group, ule.user_id, category='member')

        result = asterisk_conf_dao.find_sip_user_settings()
        for key, value in result[0]['endpoint_section_options']:
            if key == 'named_pickup_group':
                group_ids = value.split(',')
                assert_that(
                    group_ids,
                    contains_inanyorder(
                        str(pickup_user.id),
                        str(pickup_group.id),
                    ),
                )
                break
        else:
            self.fail('no "named_pickup_group" in {}'.format(result[0]))

    def test_that_named_call_groups_are_added(self):
        pickup_user = self.add_pickup()
        pickup_group = self.add_pickup()

        sip = self.add_endpoint_sip(template=False)
        ule = self.add_user_line_with_exten(endpoint_sip_uuid=sip.uuid)
        self.add_pickup_member_user(pickup_user, ule.user_id, category='pickup')
        self.add_pickup_member_group(pickup_group, ule.user_id, category='pickup')

        result = asterisk_conf_dao.find_sip_user_settings()
        for key, value in result[0]['endpoint_section_options']:
            if key == 'named_call_group':
                group_ids = value.split(',')
                assert_that(
                    group_ids,
                    contains_inanyorder(
                        str(pickup_user.id),
                        str(pickup_group.id),
                    ),
                )
                break
        else:
            self.fail('no "named_call_group" in {}'.format(result[0]))

    def test_that_doubles_are_removed(self):
        template = self.add_endpoint_sip(
            template=True,
            endpoint_section_options=[['webrtc', 'true']]
        )
        endpoint = self.add_endpoint_sip(
            templates=[template],
            template=False,
            endpoint_section_options=[
                ['codecs', '!all,ulaw'],
                ['webrtc', 'true'],
            ]
        )
        line = self.add_line(endpoint_sip_uuid=endpoint.uuid)

        result = asterisk_conf_dao.find_sip_user_settings()
        assert_that(
            result,
            contains(
                has_entries(
                    endpoint_section_options=contains_inanyorder(
                        contains('type', 'endpoint'),  # only showed once
                        contains('codecs', '!all,ulaw'),
                        contains('webrtc', 'true'),  # only showed once
                        contains('set_var', 'WAZO_TENANT_UUID={}'.format(endpoint.tenant_uuid)),
                        contains('set_var', 'WAZO_CHANNEL_DIRECTION=from-wazo'),
                        contains('set_var', 'WAZO_LINE_ID={}'.format(line.id)),
                        contains('context', 'foocontext'),
                        contains('set_var', 'TRANSFER_CONTEXT=foocontext')
                    )
                )
            )
        )

    def test_that_redefined_options_are_removed(self):
        template = self.add_endpoint_sip(
            template=True,
            endpoint_section_options=[['webrtc', 'yes']]
        )
        endpoint = self.add_endpoint_sip(
            templates=[template],
            template=False,
            endpoint_section_options=[
                ['webrtc', 'no'],
            ]
        )
        self.add_line(endpoint_sip_uuid=endpoint.uuid)

        result = asterisk_conf_dao.find_sip_user_settings()
        assert_that(
            result,
            all_of(
                contains(
                    has_entries(
                        endpoint_section_options=has_items(
                            contains('type', 'endpoint'),
                            contains('webrtc', 'no'),  # From the endpoint
                        )
                    )
                ),
                not_(
                    contains(
                        has_entries(
                            endpoint_section_options=has_items(
                                contains('webrtc', 'yes'),  # From the template
                            )
                        )
                    ),
                )
            )
        )


class TestFindSipTrunkSettings(BaseFindSIPSettings):

    def setUp(self):
        super(TestFindSipTrunkSettings, self).setUp()
        global_trunk_body = {
            'name': 'global_trunk',
            'label': 'Global trunk configuration',
            'templates': [self.general_config_template],
            'registration_section_options': [
                ['retry_interval', '20'],
                ['max_retries', '0'],
                ['auth_rejection_permanent', 'off'],
                ['forbidden_retry_interval', '30'],
                ['fatal_retry_interval', '30'],
                ['max_retries', '10000'],
            ],
            'template': True,
        }
        twilio_trunk_body = {
            'name': 'twilio',
            'label': 'Twilio specific trunk configuration',
            'template': True,
            'identify_section_options': [
                ['match', '54.172.60.0'],
                ['match', '54.172.60.1'],
                ['match', '54.172.60.2'],
            ],
        }
        self.global_trunk_template = self.add_endpoint_sip(
            **global_trunk_body
        )
        self.twilio_template = self.add_endpoint_sip(
            **twilio_trunk_body
        )

    def test_given_no_sip_accounts_then_returns_empty_list(self):
        result = asterisk_conf_dao.find_sip_trunk_settings()
        assert_that(result, contains())

    def test_given_sip_account_is_not_category_user_then_returns_empty_list(self):
        self.add_endpoint_sip(template=False)
        result = asterisk_conf_dao.find_sip_trunk_settings()
        assert_that(result, contains())

    def test_given_sip_account_is_deactivated_then_returns_empty_list(self):
        self.add_endpoint_sip(template=False)
        result = asterisk_conf_dao.find_sip_trunk_settings()
        assert_that(result, contains())

    def test_given_sip_account_is_associated_to_a_line_then_returns_empty_list(self):
        endpoint = self.add_endpoint_sip(template=False)
        self.add_line(endpoint_sip_uuid=endpoint.uuid)
        result = asterisk_conf_dao.find_sip_trunk_settings()
        assert_that(result, contains())

    def test_that_templates_are_included(self):
        endpoint = self.add_endpoint_sip(
            label='my trunk',
            template=False,
            templates=[self.global_trunk_template, self.twilio_template],
            endpoint_section_options=[
                ['callerid', '"Foo Bar" <101>'],
            ],
            auth_section_options=[
                ['username', 'iddqd'],
                ['password', 'idbehold'],
            ],
            registration_outbound_auth_section_options=[
                ['username', 'outbound_reg_username']
            ],
        )
        self.add_trunk(endpoint_sip_uuid=endpoint.uuid)

        result = asterisk_conf_dao.find_sip_trunk_settings()
        assert_that(result, contains_inanyorder(
            has_entries(
                name=endpoint.name,
                label=endpoint.label,
                aor_section_options=has_items(
                    contains('qualify_frequency', '60'),
                    contains('maximum_expiration', '3600'),
                    contains('minimum_expiration', '60'),
                    contains('default_expiration', '120'),
                    contains('max_contacts', '1'),
                    contains('remove_existing', 'true')
                ),
                auth_section_options=has_items(
                    contains('username', 'iddqd'),
                    contains('password', 'idbehold'),
                ),
                endpoint_section_options=has_items(
                    contains('allow', '!all,ulaw'),
                    contains('allow_subscribe', 'yes'),
                    contains('allow_transfer', 'yes'),
                    contains('use_ptime', 'yes'),
                    contains('rtp_timeout', '7200'),
                    contains('rtp_timeout_hold', '0'),
                    contains('timers_sess_expires', '600'),
                    contains('timers_min_se', '90'),
                    contains('trust_id_inbound', 'yes'),
                    contains('dtmf_mode', 'rfc4733'),
                    contains('send_rpid', 'yes'),
                    contains('inband_progress', 'no'),
                    contains('direct_media', 'no'),
                    contains('callerid', '"Foo Bar" <101>'),
                ),
                identify_section_options=has_items(
                    contains('match', '54.172.60.0'),
                    contains('match', '54.172.60.1'),
                    contains('match', '54.172.60.2'),
                ),
                registration_section_options=has_items(
                    contains('outbound_auth', 'auth_reg_{}'.format(endpoint.name)),
                    contains('retry_interval', '20'),
                    contains('auth_rejection_permanent', 'off'),
                    contains('forbidden_retry_interval', '30'),
                    contains('fatal_retry_interval', '30'),
                    contains('max_retries', '10000'),
                ),
                registration_outbound_auth_section_options=has_items(
                    contains('username', 'outbound_reg_username'),
                ),
                outbound_auth_section_options=has_items(),
            ),
        ))

    def test_that_the_trunk_context_is_used(self):
        context = self.add_context()
        endpoint = self.add_endpoint_sip(template=False)
        self.add_trunk(endpoint_sip_uuid=endpoint.uuid, context=context.name)

        result = asterisk_conf_dao.find_sip_trunk_settings()
        assert_that(
            result,
            contains(has_entries(
                endpoint_section_options=has_items(contains('context', context.name)),
            )),
        )

    def test_that_the_transport_is_used_from_endpoint(self):
        transport = self.add_transport()
        endpoint = self.add_endpoint_sip(
            templates=[self.global_trunk_template],
            transport_uuid=transport.uuid,
            template=False,
        )
        self.add_trunk(endpoint_sip_uuid=endpoint.uuid)

        result = asterisk_conf_dao.find_sip_trunk_settings()
        assert_that(
            result,
            contains(has_entries(
                endpoint_section_options=has_items(
                    contains('transport', transport.name),
                ),
            )),
        )

    def test_that_the_transport_is_used_from_a_template(self):
        transport = self.add_transport()
        template = self.add_endpoint_sip(template=True, transport=transport)
        endpoint = self.add_endpoint_sip(
            templates=[self.general_config_template, self.global_trunk_template, template],
            template=False,
        )
        self.add_trunk(endpoint_sip_uuid=endpoint.uuid)

        result = asterisk_conf_dao.find_sip_trunk_settings()
        assert_that(
            result,
            contains(has_entries(
                endpoint_section_options=has_items(
                    contains('transport', transport.name),
                ),
            )),
        )

    def test_that_all_sections_are_generated_and_cross_references(self):
        endpoint = self.add_endpoint_sip(
            template=False,
            aor_section_options=[['contact', 'sip:name@proxy:port']],
            auth_section_options=[['username', 'username']],
            endpoint_section_options=[['identify_by', 'auth_username,username']],
            registration_section_options=[
                ['expiration', '120'],
                ['client_uri', 'sip:foo@bar'],
            ],
            registration_outbound_auth_section_options=[['password', 'secret']],
            identify_section_options=[['match', '192.168.1.1']],
            outbound_auth_section_options=[['username', 'outbound']],
        )
        self.add_trunk(endpoint_sip_uuid=endpoint.uuid)

        result = asterisk_conf_dao.find_sip_trunk_settings()
        assert_that(
            result,
            contains(has_entries(
                aor_section_options=has_items(
                    contains('type', 'aor'),
                    contains('contact', 'sip:name@proxy:port'),
                ),
                auth_section_options=has_items(
                    contains('type', 'auth'),
                    contains('username', 'username'),
                ),
                endpoint_section_options=has_items(
                    contains('type', 'endpoint'),
                    contains('aors', endpoint.name),
                    contains('auth', endpoint.name),
                    contains('identify_by', 'auth_username,username'),
                ),
                registration_section_options=has_items(
                    contains('type', 'registration'),
                    contains('expiration', '120'),
                    contains('outbound_auth', 'auth_reg_{}'.format(endpoint.name)),
                ),
                registration_outbound_auth_section_options=has_items(
                    contains('type', 'auth'),
                    contains('password', 'secret'),
                ),
                identify_section_options=has_items(
                    contains('type', 'identify'),
                    contains('match', '192.168.1.1'),
                    contains('endpoint', endpoint.name),
                ),
                outbound_auth_section_options=has_items(
                    contains('type', 'auth'),
                    contains('username', 'outbound'),
                )
            ))
        )

    def test_that_template_references_are_not_inherited(self):
        template = self.add_endpoint_sip(
            template=True,
            endpoint_section_options=[['callerid', 'foo']],
            auth_section_options=[['auth_type', 'userpass']],
            aor_section_options=[['max_contacts', '42']],
            registration_section_options=[['expiration', '10']],
            registration_outbound_auth_section_options=[['auth_type', 'userpass']],
            identify_section_options=[['match', '192.168.1.2']],
            outbound_auth_section_options=[['auth_type', 'userpass']],

        )
        endpoint = self.add_endpoint_sip(
            template=False,
            templates=[template],
            aor_section_options=[['contact', 'sip:name@proxy:port']],
            auth_section_options=[['username', 'username']],
            endpoint_section_options=[['identify_by', 'auth_username,username']],
            registration_section_options=[
                ['expiration', '120'],
                ['client_uri', 'sip:foo@bar'],
            ],
            registration_outbound_auth_section_options=[['password', 'secret']],
            identify_section_options=[['match', '192.168.1.1']],
            outbound_auth_section_options=[['username', 'outbound']],
        )
        self.add_trunk(endpoint_sip_uuid=endpoint.uuid)

        result = asterisk_conf_dao.find_sip_trunk_settings()
        assert_that(
            result,
            not_(contains(has_entries(
                endpoint_section_options=has_items(
                    ['aors', template.name],
                    ['auth', template.name],
                ),
                registration_section_options=has_items(
                    ['outbound_auth', 'auth_reg_{}'.format(template.name)]
                ),
                identify_section_options=has_items(
                    ['endpoint', template.name],
                ),
            )))
        )

    def test_that_doubles_are_removed(self):
        template = self.add_endpoint_sip(
            template=True,
            endpoint_section_options=[['webrtc', 'true']]
        )
        endpoint = self.add_endpoint_sip(
            templates=[template],
            template=False,
            endpoint_section_options=[
                ['codecs', '!all,ulaw'],
                ['webrtc', 'true'],
            ]
        )
        self.add_trunk(endpoint_sip_uuid=endpoint.uuid)

        result = asterisk_conf_dao.find_sip_trunk_settings()
        assert_that(
            result,
            contains(
                has_entries(
                    endpoint_section_options=contains_inanyorder(
                        contains('type', 'endpoint'),  # only showed once
                        contains('codecs', '!all,ulaw'),
                        contains('webrtc', 'true'),  # only showed once
                        contains('set_var', 'WAZO_TENANT_UUID={}'.format(endpoint.tenant_uuid)),
                    )
                )
            )
        )

    def test_that_redefined_options_are_removed(self):
        template = self.add_endpoint_sip(
            template=True,
            endpoint_section_options=[['webrtc', 'yes']]
        )
        endpoint = self.add_endpoint_sip(
            templates=[template],
            template=False,
            endpoint_section_options=[
                ['webrtc', 'no'],
            ]
        )
        self.add_trunk(endpoint_sip_uuid=endpoint.uuid)

        result = asterisk_conf_dao.find_sip_trunk_settings()
        assert_that(
            result,
            all_of(
                contains(
                    has_entries(
                        endpoint_section_options=has_items(
                            contains('type', 'endpoint'),
                            contains('webrtc', 'no'),  # From the endpoint
                        )
                    )
                ),
                not_(
                    contains(
                        has_entries(
                            endpoint_section_options=has_items(
                                contains('webrtc', 'yes'),  # From the template
                            )
                        )
                    ),
                )
            )
        )
