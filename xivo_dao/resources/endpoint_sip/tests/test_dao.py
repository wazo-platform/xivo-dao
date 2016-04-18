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

from hamcrest import assert_that
from hamcrest import equal_to
from hamcrest import none
from hamcrest import contains
from hamcrest import empty
from hamcrest import is_not
from hamcrest import has_item
from hamcrest import has_items
from hamcrest import has_property
from hamcrest import has_properties
from hamcrest import has_length
from hamcrest import all_of
from hamcrest import contains_string

from xivo_dao.alchemy.usersip import UserSIP as SIPEndpoint
from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.helpers.exception import InputError
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.resources.endpoint_sip import dao
from xivo_dao.tests.test_dao import DAOTestCase

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
    ['setvar', 'setvar'],
    ['accountcode', 'accountcode'],
    ['md5secret', 'abcdefg'],
    ['mohinterpret', 'mohinterpret'],
    ['vmexten', '1000'],
    ['callingpres', '1'],
    ['parkinglot', '700'],
    ['fullcontact', 'fullcontact'],
    ['fullname', 'fullname'],
    ['defaultip', '127.0.0.1'],
    ['qualifyfreq', '5000'],
    ['regexten', 'regexten'],
    ['regseconds', '60'],
    ['regserver', '127.0.0.1'],
    ['ipaddr', '127.0.0.1'],
    ['lastms', '500'],
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
        self.assertRaises(InputError, dao.find_by, column=1)

    def test_given_row_with_value_does_not_exist_then_returns_null(self):
        result = dao.find_by(name='abcd')
        assert_that(result, none())

    def test_find_by(self):
        sip = self.add_usersip(name='myname')
        result = dao.find_by(name='myname')

        assert_that(result.id, equal_to(sip.id))


class TestSipEndpointDaoGet(TestSipEndpointDAO):

    def test_given_no_rows_then_raises_error(self):
        self.assertRaises(NotFoundError, dao.get, 1)

    def test_given_row_with_minimal_parameters_then_returns_model(self):
        row = self.add_usersip(name='username',
                               secret='secret',
                               type='friend',
                               host='dynamic')

        sip = dao.get(row.id)
        assert_that(sip.id, equal_to(row.id))
        assert_that(sip.name, equal_to('username'))
        assert_that(sip.username, none())
        assert_that(sip.secret, equal_to('secret'))
        assert_that(sip.type, equal_to('friend'))
        assert_that(sip.host, equal_to('dynamic'))

    def test_given_row_with_optional_parameters_then_returns_model(self):
        row = self.add_usersip(language="fr_FR",
                               amaflags="omit",
                               buggymwi=1)

        sip = dao.get(row.id)
        assert_that(sip.options, has_items(["language", "fr_FR"],
                                           ["amaflags", "omit"],
                                           ["buggymwi", "yes"]))

    def test_given_row_with_option_set_to_null_then_option_not_returned(self):
        row = self.add_usersip(language=None,
                               allow=None,
                               setvar='')

        sip = dao.get(row.id)
        assert_that(sip.options, is_not(has_item(has_item("language"))))
        assert_that(sip.options, is_not(has_item(has_item("allow"))))
        assert_that(sip.options, is_not(has_item(has_item("setvar"))))

    def test_given_row_with_additional_options_then_returns_model(self):
        options = [
            ["foo", "bar"],
            ["foo", "baz"],
            ["spam", "eggs"]
        ]

        row = self.add_usersip(options=options)

        sip = dao.get(row.id)
        assert_that(sip.options, has_items(*options))

    def test_given_row_has_native_and_additional_options_then_all_options_returned(self):
        row = self.add_usersip(language="fr_FR", _options=[["foo", "bar"]])

        sip = dao.get(row.id)
        assert_that(sip.options, has_items(["language", "fr_FR"], ["foo", "bar"]))


class TestSipEndpointDaoSearch(DAOTestCase):

    def test_search(self):
        sip1 = self.add_usersip(name="alice",
                                secret="abygale")
        self.add_usersip(name="henry",
                         secret="ford")

        search_result = dao.search(search='alice')

        assert_that(search_result.total, equal_to(1))
        assert_that(search_result.items, contains(has_property('id', sip1.id)))


class TestSipEndpointDaoCreate(DAOTestCase):

    def test_create_minimal_parameters(self):
        sip = SIPEndpoint()

        created_sip = dao.create(sip)
        row = self.session.query(SIPEndpoint).first()

        assert_that(created_sip.id, equal_to(row.id))
        assert_that(created_sip.name, has_length(8))
        assert_that(created_sip.username, none())
        assert_that(created_sip.secret, has_length(8))
        assert_that(created_sip.type, equal_to('friend'))
        assert_that(created_sip.host, equal_to('dynamic'))
        assert_that(created_sip.category, equal_to('user'))

    def test_create_predefined_parameters(self):
        sip = SIPEndpoint(name='myusername',
                          secret='mysecret',
                          host="127.0.0.1",
                          type="peer")

        created_sip = dao.create(sip)
        row = self.session.query(SIPEndpoint).first()

        assert_that(created_sip.id, equal_to(row.id))
        assert_that(created_sip.name, equal_to('myusername'))
        assert_that(created_sip.username, none())
        assert_that(created_sip.secret, equal_to('mysecret'))
        assert_that(created_sip.type, equal_to('peer'))
        assert_that(created_sip.host, equal_to('127.0.0.1'))
        assert_that(created_sip.category, equal_to('user'))

    def test_create_with_native_options(self):
        expected_options = has_properties({
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
            'setvar': 'setvar',
            'accountcode': 'accountcode',
            'md5secret': 'abcdefg',
            'mohinterpret': 'mohinterpret',
            'vmexten': '1000',
            'callingpres': 1,
            'parkinglot': 700,
            'fullcontact': 'fullcontact',
            'fullname': 'fullname',
            'defaultip': '127.0.0.1',
            'qualifyfreq': 5000,
            'regexten': 'regexten',
            'regseconds': 60,
            'regserver': '127.0.0.1',
            'ipaddr': '127.0.0.1',
            'lastms': '500',
            'cid_number': '0123456789',
            'callbackextension': '0123456789',
            'port': 10000,
            'outboundproxy': '127.0.0.1',
            'remotesecret': 'remotesecret',
        })

        sip = SIPEndpoint(options=ALL_OPTIONS)
        created_sip = dao.create(sip)

        row = self.session.query(SIPEndpoint).first()

        assert_that(created_sip.id, equal_to(row.id))
        assert_that(created_sip, expected_options)
        assert_that(created_sip.options, has_items(*ALL_OPTIONS))

    def test_create_with_additional_options(self):
        options = [
            ["language", "fr_FR"],
            ["foo", "bar"],
            ["foo", "baz"],
            ["spam", "eggs"]
        ]

        sip = SIPEndpoint(options=options)
        created_sip = dao.create(sip)

        row = self.session.query(SIPEndpoint).first()

        assert_that(created_sip.id, equal_to(row.id))
        assert_that(created_sip.options, has_items(*options))


class TestSipEndpointDaoEdit(DAOTestCase):

    def test_edit_basic_parameters(self):
        row = self.add_usersip()
        sip = dao.get(row.id)

        sip.name = 'username'
        sip.secret = 'secret'
        sip.type = 'peer'
        sip.host = '127.0.0.1'

        dao.edit(sip)

        row = self.session.query(SIPEndpoint).first()
        assert_that(row.name, equal_to('username'))
        assert_that(row.secret, equal_to('secret'))
        assert_that(row.type, equal_to('peer'))
        assert_that(row.host, equal_to('127.0.0.1'))

    def test_edit_remove_options(self):
        expected_options = has_properties({
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
            'setvar': '',
            'accountcode': none(),
            'md5secret': '',
            'mohinterpret': none(),
            'vmexten': none(),
            'callingpres': none(),
            'parkinglot': none(),
            'fullcontact': none(),
            'fullname': none(),
            'defaultip': none(),
            'qualifyfreq': none(),
            'regexten': none(),
            'regseconds': 0,
            'regserver': none(),
            'ipaddr': '',
            'lastms': '',
            'cid_number': none(),
            'callbackextension': none(),
            'port': none(),
            'outboundproxy': none(),
            'remotesecret': none(),
            '_options': empty(),
        })

        sip = dao.create(SIPEndpoint(options=ALL_OPTIONS))
        sip = dao.get(sip.id)
        sip.options = []

        dao.edit(sip)

        row = self.session.query(SIPEndpoint).first()
        assert_that(row, expected_options)

    def test_edit_options(self):
        row = self.add_usersip(language="fr_FR", amaflags="default", subscribemwi=1,
                               allow="g729,gsm")

        sip = dao.get(row.id)
        sip.options = [
            ["language", "en_US"],
            ["amaflags", "omit"],
            ["subscribemwi", "no"],
            ["allow", "ulaw,alaw"],
        ]

        dao.edit(sip)

        row = self.session.query(SIPEndpoint).first()
        assert_that(row.language, equal_to("en_US"))
        assert_that(row.amaflags, equal_to("omit"))
        assert_that(row.subscribemwi, equal_to(0))
        assert_that(row.allow, equal_to("ulaw,alaw"))

    def test_edit_additional_options(self):
        row = self.add_usersip(_options=[
            ["foo", "bar"],
            ["foo", "baz"],
            ["spam", "eggs"],
        ])

        sip = dao.get(row.id)
        sip.options = [
            ["foo", "newbar"],
            ["foo", "newbaz"],
            ["spam", "neweggs"],
        ]

        dao.edit(sip)

        row = self.session.query(SIPEndpoint).first()
        assert_that(row._options, has_items(
            ["foo", "newbar"],
            ["foo", "newbaz"],
            ["spam", "neweggs"],
        ))

    def test_edit_both_native_and_additional_options(self):
        row = self.add_usersip(language="fr_FR",
                               amaflags="default",
                               subscribemwi=1,
                               allow="g729,gsm",
                               _options=[
                                   ["foo", "bar"],
                                   ["foo", "baz"],
                                   ["spam", "eggs"],
                               ])

        new_options = [
            ["language", "en_US"],
            ["amaflags", "omit"],
            ["subscribemwi", "no"],
            ["allow", "ulaw,alaw"],
            ["foo", "newbar"],
            ["foo", "newbaz"],
            ["spam", "neweggs"],
        ]

        sip = dao.get(row.id)
        sip.options = new_options
        dao.edit(sip)

        row = self.session.query(SIPEndpoint).first()
        assert_that(row.options, has_items(*new_options))
        assert_that(row.language, equal_to("en_US"))
        assert_that(row.amaflags, equal_to("omit"))
        assert_that(row.subscribemwi, equal_to(0))
        assert_that(row.allow, equal_to("ulaw,alaw"))
        assert_that(row._options, has_items(
            ["foo", "newbar"],
            ["foo", "newbaz"],
            ["spam", "neweggs"],
        ))

class TestSipEndpointDaoDelete(TestSipEndpointDAO):

    def test_delete(self):
        row = self.add_usersip()

        sip = dao.get(row.id)
        dao.delete(sip)

        row = self.session.query(SIPEndpoint).first()
        assert_that(row, none())

    def test_given_endpoint_is_associated_to_line_then_line_is_dissociated(self):
        sip_row = self.add_usersip()
        line_row = self.add_line(endpoint='sip', endpoint_id=sip_row.id)

        sip = dao.get(sip_row.id)
        dao.delete(sip)

        line_row = self.session.query(Line).get(line_row.id)
        assert_that(line_row.endpoint, none())
        assert_that(line_row.endpoint_id, none())
