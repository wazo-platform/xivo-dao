# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from hamcrest import (
    all_of,
    assert_that,
    contains,
    empty,
    equal_to,
    has_item,
    has_items,
    has_length,
    has_properties,
    has_property,
    is_not,
    none,
)

from xivo_dao.alchemy.usersip import UserSIP as SIPEndpoint
from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.helpers.exception import InputError
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao as sip_dao

ALL_OPTIONS = [
    ['buggymwi', 'yes'],
    ['amaflags', 'default'],
    ['sendrpid', 'yes'],
    ['videosupport', 'yes'],
    ['maxcallbitrate', '1024'],
    ['session-minse', '10'],
    ['maxforwards', '1'],
    ['rtpholdtimeout', '15'],
    ['session-expires', '60'],
    ['ignoresdpversion', 'yes'],
    ['textsupport', 'yes'],
    ['unsolicited_mailbox', '1000@default'],
    ['fromuser', 'field-user'],
    ['useclientcode', 'yes'],
    ['call-limit', '1'],
    ['progressinband', 'yes'],
    ['transport', 'udp'],
    ['directmedia', 'update'],
    ['promiscredir', 'yes'],
    ['allowoverlap', 'yes'],
    ['dtmfmode', 'info'],
    ['language', 'fr_FR'],
    ['usereqphone', 'yes'],
    ['qualify', '500'],
    ['trustrpid', 'yes'],
    ['timert1', '1'],
    ['session-refresher', 'uas'],
    ['allowsubscribe', 'yes'],
    ['session-timers', 'originate'],
    ['busylevel', '1'],
    ['callcounter', 'no'],
    ['callerid', '"cûstomcallerid" <1234>'],
    ['encryption', 'yes'],
    ['use_q850_reason', 'yes'],
    ['disallowed_methods', 'disallowsip'],
    ['rfc2833compensate', 'yes'],
    ['g726nonstandard', 'yes'],
    ['contactdeny', '127.0.0.1'],
    ['snom_aoc_enabled', 'yes'],
    ['t38pt_udptl', 'yes'],
    ['subscribemwi', 'no'],
    ['autoframing', 'yes'],
    ['t38pt_usertpsource', 'yes'],
    ['fromdomain', 'field-domain'],
    ['allowtransfer', 'yes'],
    ['nat', 'force_rport,comedia'],
    ['contactpermit', '127.0.0.1'],
    ['rtpkeepalive', '15'],
    ['insecure', 'port'],
    ['permit', '127.0.0.1'],
    ['deny', '127.0.0.1'],
    ['timerb', '1'],
    ['rtptimeout', '15'],
    ['disallow', 'all'],
    ['allow', 'gsm'],
    ['accountcode', 'accountcode'],
    ['md5secret', 'abcdefg'],
    ['mohinterpret', 'mohinterpret'],
    ['vmexten', '1000'],
    ['callingpres', '1'],
    ['parkinglot', '700'],
    ['fullname', 'fullname'],
    ['defaultip', '127.0.0.1'],
    ['qualifyfreq', '5000'],
    ['regexten', 'regexten'],
    ['cid_number', '0123456789'],
    ['callbackextension', '0123456789'],
    ['port', '10000'],
    ['outboundproxy', '127.0.0.1'],
    ['remotesecret', 'remotesecret'],
]


class TestSipEndpointDAO(DAOTestCase):
    pass


class TestSipEndpointDaoFindBy(TestSipEndpointDAO):

    def test_given_column_does_not_exist_then_raises_error(self):
        self.assertRaises(InputError, sip_dao.find_by, column=1)

    def test_given_row_with_value_does_not_exist_then_returns_null(self):
        result = sip_dao.find_by(name='abcd')
        assert_that(result, none())

    def test_find_by(self):
        sip = self.add_usersip(name='myname')
        result = sip_dao.find_by(name='myname')

        assert_that(result.id, equal_to(sip.id))


class TestSipEndpointDaoGet(TestSipEndpointDAO):

    def test_given_no_rows_then_raises_error(self):
        self.assertRaises(NotFoundError, sip_dao.get, 1)

    def test_given_row_with_minimal_parameters_then_returns_model(self):
        row = self.add_usersip(
            name='username',
            secret='secret',
            type='friend',
            host='dynamic',
        )

        sip = sip_dao.get(row.id)
        assert_that(sip, has_properties(
            id=row.id,
            name='username',
            secret='secret',
            type='friend',
            host='dynamic',
        ))

    def test_given_row_with_optional_parameters_then_returns_model(self):
        row = self.add_usersip(language="fr_FR",
                               amaflags="omit",
                               buggymwi=1)

        sip = sip_dao.get(row.id)
        assert_that(sip.options, has_items(
            ["language", "fr_FR"],
            ["amaflags", "omit"],
            ["buggymwi", "yes"]
        ))

    def test_given_row_with_option_set_to_null_then_option_not_returned(self):
        row = self.add_usersip(language=None,
                               allow=None,
                               callerid='')

        sip = sip_dao.get(row.id)
        assert_that(sip.options, all_of(
            is_not(has_item(has_item("language"))),
            is_not(has_item(has_item("allow"))),
            is_not(has_item(has_item("callerid"))),
        ))

    def test_given_row_with_additional_options_then_returns_model(self):
        options = [
            ["foo", "bar"],
            ["foo", "baz"],
            ["spam", "eggs"]
        ]

        row = self.add_usersip(options=options)

        sip = sip_dao.get(row.id)
        assert_that(sip.options, has_items(*options))

    def test_given_row_has_native_and_additional_options_then_all_options_returned(self):
        row = self.add_usersip(language="fr_FR", _options=[["foo", "bar"]])

        sip = sip_dao.get(row.id)
        assert_that(sip.options, has_items(["language", "fr_FR"], ["foo", "bar"]))


class TestSipEndpointDaoSearch(DAOTestCase):

    def test_search(self):
        sip1 = self.add_usersip(name="alice", secret="abygale")
        self.add_usersip(name="henry", secret="ford")

        search_result = sip_dao.search(search='alice')

        assert_that(search_result.total, equal_to(1))
        assert_that(search_result.items, contains(has_property('id', sip1.id)))


class TestSipEndpointDaoCreate(DAOTestCase):

    def test_create_minimal_parameters(self):
        sip = SIPEndpoint(tenant_uuid=self.default_tenant.uuid)

        created_sip = sip_dao.create(sip)
        row = self.session.query(SIPEndpoint).first()

        assert_that(created_sip, has_properties(
            id=row.id,
            name=has_length(8),
            username=none(),
            secret=has_length(8),
            type='friend',
            host='dynamic',
            category='user',
        ))

    def test_create_predefined_parameters(self):
        sip = SIPEndpoint(
            tenant_uuid=self.default_tenant.uuid,
            name='myusername',
            secret='mysecret',
            host="127.0.0.1",
            type="peer",
        )

        created_sip = sip_dao.create(sip)
        row = self.session.query(SIPEndpoint).first()

        assert_that(created_sip, has_properties(
            id=row.id,
            tenant_uuid=self.default_tenant.uuid,
            name='myusername',
            username=none(),
            secret='mysecret',
            type='peer',
            host='127.0.0.1',
            category='user',
        ))

    def test_create_with_native_options(self):
        sip = SIPEndpoint(tenant_uuid=self.default_tenant.uuid, options=ALL_OPTIONS)
        created_sip = sip_dao.create(sip)

        row = self.session.query(SIPEndpoint).first()

        assert_that(created_sip, has_properties({
            'id': row.id,
            'options': has_items(*ALL_OPTIONS),

            'buggymwi': 1,
            'amaflags': 'default',
            'sendrpid': 'yes',
            'videosupport': 'yes',
            'maxcallbitrate': 1024,
            'session_minse': 10,
            'maxforwards': 1,
            'rtpholdtimeout': 15,
            'session_expires': 60,
            'ignoresdpversion': 1,
            'textsupport': 1,
            'unsolicited_mailbox': '1000@default',
            'fromuser': 'field-user',
            'useclientcode': 1,
            'call_limit': 1,
            'progressinband': 'yes',
            'transport': 'udp',
            'directmedia': 'update',
            'promiscredir': 1,
            'allowoverlap': 1,
            'dtmfmode': 'info',
            'language': 'fr_FR',
            'usereqphone': 1,
            'qualify': '500',
            'trustrpid': 1,
            'timert1': 1,
            'session_refresher': 'uas',
            'allowsubscribe': 1,
            'session_timers': 'originate',
            'busylevel': 1,
            'callcounter': 0,
            'callerid': '"cûstomcallerid" <1234>',
            'encryption': 1,
            'use_q850_reason': 1,
            'disallowed_methods': 'disallowsip',
            'rfc2833compensate': 1,
            'g726nonstandard': 1,
            'contactdeny': '127.0.0.1',
            'snom_aoc_enabled': 1,
            't38pt_udptl': 1,
            'subscribemwi': 0,
            'autoframing': 1,
            't38pt_usertpsource': 1,
            'fromdomain': 'field-domain',
            'allowtransfer': 1,
            'nat': 'force_rport,comedia',
            'contactpermit': '127.0.0.1',
            'rtpkeepalive': 15,
            'insecure': 'port',
            'permit': '127.0.0.1',
            'deny': '127.0.0.1',
            'timerb': 1,
            'rtptimeout': 15,
            'disallow': 'all',
            'allow': 'gsm',
            'accountcode': 'accountcode',
            'md5secret': 'abcdefg',
            'mohinterpret': 'mohinterpret',
            'vmexten': '1000',
            'callingpres': 1,
            'parkinglot': 700,
            'fullname': 'fullname',
            'defaultip': '127.0.0.1',
            'qualifyfreq': 5000,
            'regexten': 'regexten',
            'cid_number': '0123456789',
            'callbackextension': '0123456789',
            'port': 10000,
            'outboundproxy': '127.0.0.1',
            'remotesecret': 'remotesecret',
        }))

    def test_create_with_additional_options(self):
        options = [
            ["language", "fr_FR"],
            ["foo", "bar"],
            ["foo", "baz"],
            ["spam", "eggs"]
        ]

        sip = SIPEndpoint(tenant_uuid=self.default_tenant.uuid, options=options)
        created_sip = sip_dao.create(sip)

        row = self.session.query(SIPEndpoint).first()

        assert_that(created_sip, has_properties(
            id=row.id,
            options=has_items(*options)
        ))


class TestSipEndpointDaoEdit(DAOTestCase):

    def test_edit_basic_parameters(self):
        row = self.add_usersip()
        sip = sip_dao.get(row.id)

        sip.name = 'username'
        sip.secret = 'secret'
        sip.type = 'peer'
        sip.host = '127.0.0.1'

        sip_dao.edit(sip)

        row = self.session.query(SIPEndpoint).first()
        assert_that(row, has_properties(
            name='username',
            secret='secret',
            type='peer',
            host='127.0.0.1',
        ))

    def test_edit_remove_options(self):
        sip = self.add_usersip(options=ALL_OPTIONS)

        sip = sip_dao.get(sip.id)
        sip.options = []

        sip_dao.edit(sip)

        row = self.session.query(SIPEndpoint).first()
        assert_that(row, has_properties({
            'buggymwi': none(),
            'md5secret': '',
            'amaflags': 'default',
            'sendrpid': none(),
            'videosupport': none(),
            'maxcallbitrate': none(),
            'session_minse': none(),
            'maxforwards': none(),
            'rtpholdtimeout': none(),
            'session_expires': none(),
            'ignoresdpversion': none(),
            'textsupport': none(),
            'unsolicited_mailbox': none(),
            'fromuser': none(),
            'useclientcode': none(),
            'call_limit': 10,
            'progressinband': none(),
            'transport': none(),
            'directmedia': none(),
            'promiscredir': none(),
            'allowoverlap': none(),
            'dtmfmode': none(),
            'language': none(),
            'usereqphone': none(),
            'qualify': none(),
            'trustrpid': none(),
            'timert1': none(),
            'session_refresher': none(),
            'allowsubscribe': none(),
            'session_timers': none(),
            'busylevel': none(),
            'callcounter': none(),
            'callerid': none(),
            'encryption': none(),
            'use_q850_reason': none(),
            'disallowed_methods': none(),
            'rfc2833compensate': none(),
            'g726nonstandard': none(),
            'contactdeny': none(),
            'snom_aoc_enabled': none(),
            't38pt_udptl': none(),
            'subscribemwi': 0,
            'autoframing': none(),
            't38pt_usertpsource': none(),
            'fromdomain': none(),
            'allowtransfer': none(),
            'nat': none(),
            'contactpermit': none(),
            'rtpkeepalive': none(),
            'insecure': none(),
            'permit': none(),
            'deny': none(),
            'timerb': none(),
            'rtptimeout': none(),
            'disallow': none(),
            'allow': none(),
            'accountcode': none(),
            'md5secret': '',
            'mohinterpret': none(),
            'vmexten': none(),
            'callingpres': none(),
            'parkinglot': none(),
            'fullname': none(),
            'defaultip': none(),
            'qualifyfreq': none(),
            'regexten': none(),
            'cid_number': none(),
            'callbackextension': none(),
            'port': none(),
            'outboundproxy': none(),
            'remotesecret': none(),
            '_options': empty(),
        }))

    def test_edit_options(self):
        row = self.add_usersip(
            language="fr_FR",
            amaflags="default",
            subscribemwi=1,
            allow="g729,gsm"
        )

        sip = sip_dao.get(row.id)
        sip.options = [
            ["language", "en_US"],
            ["amaflags", "omit"],
            ["subscribemwi", "no"],
            ["allow", "ulaw,alaw"],
        ]

        sip_dao.edit(sip)

        row = self.session.query(SIPEndpoint).first()
        assert_that(row, has_properties(
            language='en_US',
            amaflags='omit',
            subscribemwi=0,
            allow='ulaw,alaw',
        ))

    def test_edit_additional_options(self):
        row = self.add_usersip(_options=[
            ["foo", "bar"],
            ["foo", "baz"],
            ["spam", "eggs"],
        ])

        sip = sip_dao.get(row.id)
        sip.options = [
            ["foo", "newbar"],
            ["foo", "newbaz"],
            ["spam", "neweggs"],
        ]

        sip_dao.edit(sip)

        row = self.session.query(SIPEndpoint).first()
        assert_that(row._options, has_items(
            ["foo", "newbar"],
            ["foo", "newbaz"],
            ["spam", "neweggs"],
        ))

    def test_edit_both_native_and_additional_options(self):
        row = self.add_usersip(
            language="fr_FR",
            amaflags="default",
            subscribemwi=1,
            allow="g729,gsm",
            _options=[
                ["foo", "bar"],
                ["foo", "baz"],
                ["spam", "eggs"],
            ]
        )

        new_options = [
            ["language", "en_US"],
            ["amaflags", "omit"],
            ["subscribemwi", "no"],
            ["allow", "ulaw,alaw"],
            ["foo", "newbar"],
            ["foo", "newbaz"],
            ["spam", "neweggs"],
        ]

        sip = sip_dao.get(row.id)
        sip.options = new_options
        sip_dao.edit(sip)

        row = self.session.query(SIPEndpoint).first()
        assert_that(row, has_properties(
            options=has_items(*new_options),
            language='en_US',
            amaflags='omit',
            subscribemwi=0,
            allow='ulaw,alaw',
            _options=has_items(
                ["foo", "newbar"],
                ["foo", "newbaz"],
                ["spam", "neweggs"],
            )
        ))


class TestSipEndpointDaoDelete(TestSipEndpointDAO):

    def test_delete(self):
        row = self.add_usersip()

        sip = sip_dao.get(row.id)
        sip_dao.delete(sip)

        row = self.session.query(SIPEndpoint).first()
        assert_that(row, none())

    def test_given_endpoint_is_associated_to_line_then_line_is_dissociated(self):
        sip_row = self.add_usersip()
        line_row = self.add_line(endpoint='sip', endpoint_id=sip_row.id)

        sip = sip_dao.get(sip_row.id)
        sip_dao.delete(sip)

        line_row = self.session.query(Line).get(line_row.id)
        assert_that(line_row.endpoint, none())
        assert_that(line_row.endpoint_id, none())


class TestRelations(DAOTestCase):

    def test_trunk_relationship(self):
        sip_row = self.add_usersip()
        trunk_row = self.add_trunk()
        trunk_row.associate_endpoint(sip_row)

        sip = sip_dao.get(sip_row.id)
        assert_that(sip, equal_to(sip_row))
        assert_that(sip.trunk, equal_to(trunk_row))

    def test_line_relationship(self):
        sip_row = self.add_usersip()
        line_row = self.add_line()
        line_row.associate_endpoint(sip_row)

        sip = sip_dao.get(sip_row.id)
        assert_that(sip, equal_to(sip_row))
        assert_that(sip.line, equal_to(line_row))
