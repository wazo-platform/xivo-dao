# -*- coding: UTF-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from hamcrest import (
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

from xivo_dao.alchemy.useriax import UserIAX as IAXEndpoint
from xivo_dao.alchemy.trunkfeatures import TrunkFeatures as Trunk
from xivo_dao.helpers.exception import InputError, NotFoundError
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao as iax_dao

ALL_OPTIONS = [
    ['amaflags', 'default'],
    ['language', 'fr_FR'],
    ['qualify', '500'],
    ['callerid', '"cûstomcallerid" <1234>'],
    ['encryption', 'yes'],
    ['permit', '127.0.0.1'],
    ['deny', '127.0.0.1'],
    ['disallow', 'all'],
    ['allow', 'gsm'],
    ['accountcode', 'accountcode'],
    ['mohinterpret', 'mohinterpret'],
    ['parkinglot', '700'],
    ['fullname', 'fullname'],
    ['defaultip', '127.0.0.1'],
    ['regexten', 'regexten'],
    ['cid_number', '0123456789'],
    ['port', '10000'],
    ['username', 'username'],
    ['secret', 'secret'],
    ['dbsecret', 'dbsecret'],
    ['mailbox', 'mailbox'],
    ['trunk', 'yes'],
    ['auth', 'md5'],
    ['forceencryption', 'aes128'],
    ['maxauthreq', '10'],
    ['inkeys', 'inkeys'],
    ['outkey', 'oukeys'],
    ['adsi', 'yes'],
    ['transfer', 'mediaonly'],
    ['codecpriority', 'disabled'],
    ['jitterbuffer', 'yes'],
    ['forcejitterbuffer', 'yes'],
    ['sendani', 'yes'],
    ['qualifysmoothing', 'yes'],
    ['qualifyfreqok', '100'],
    ['qualifyfreqnotok', '20'],
    ['timezone', 'timezone'],
    ['mohsuggest', 'mohsuggest'],
    ['sourceaddress', 'sourceaddress'],
    ['setvar', 'setvar'],
    ['mask', 'mask'],
    ['peercontext', 'peercontext'],
    ['immediate', 'yes'],
    ['keyrotate', 'yes'],
    ['requirecalltoken', 'yes'],
]


class TestFindBy(DAOTestCase):

    def test_given_column_does_not_exist_then_raises_error(self):
        self.assertRaises(InputError, iax_dao.find_by, column=1)

    def test_given_row_with_value_does_not_exist_then_returns_null(self):
        result = iax_dao.find_by(name='abcd')
        assert_that(result, none())

    def test_find_by(self):
        iax = self.add_useriax(name='myname')
        result = iax_dao.find_by(name='myname')

        assert_that(result.id, equal_to(iax.id))


class TestGet(DAOTestCase):

    def test_given_no_rows_then_raises_error(self):
        self.assertRaises(NotFoundError, iax_dao.get, 1)

    def test_given_row_with_minimal_parameters_then_returns_model(self):
        row = self.add_useriax(name='name',
                               type='friend',
                               host='dynamic')

        iax = iax_dao.get(row.id)
        assert_that(iax.id, equal_to(row.id))
        assert_that(iax.name, equal_to('name'))
        assert_that(iax.type, equal_to('friend'))
        assert_that(iax.host, equal_to('dynamic'))

    def test_given_row_with_optional_parameters_then_returns_model(self):
        row = self.add_useriax(
            language="fr_FR",
            amaflags="omit",
        )

        iax = iax_dao.get(row.id)
        assert_that(iax.options, has_items(
            ["language", "fr_FR"],
            ["amaflags", "omit"],
        ))

    def test_given_row_with_option_set_to_null_then_option_not_returned(self):
        row = self.add_useriax(language=None,
                               allow=None,
                               callerid='')

        iax = iax_dao.get(row.id)
        assert_that(iax.options, is_not(has_item(has_item("language"))))
        assert_that(iax.options, is_not(has_item(has_item("allow"))))
        assert_that(iax.options, is_not(has_item(has_item("callerid"))))

    def test_given_row_with_additional_options_then_returns_model(self):
        options = [
            ["foo", "bar"],
            ["foo", "baz"],
            ["spam", "eggs"]
        ]

        row = self.add_useriax(options=options)

        iax = iax_dao.get(row.id)
        assert_that(iax.options, has_items(*options))

    def test_given_row_has_native_and_additional_options_then_all_options_returned(self):
        row = self.add_useriax(language="fr_FR", _options=[["foo", "bar"]])

        iax = iax_dao.get(row.id)
        assert_that(iax.options, has_items(["language", "fr_FR"], ["foo", "bar"]))


class TestSearch(DAOTestCase):

    def test_search(self):
        iax1 = self.add_useriax(name="alice")
        self.add_useriax(name="henry")

        search_result = iax_dao.search(search='alice')

        assert_that(search_result.total, equal_to(1))
        assert_that(search_result.items, contains(has_property('id', iax1.id)))


class TestCreate(DAOTestCase):

    def test_create_minimal_parameters(self):
        iax = IAXEndpoint()

        created_iax = iax_dao.create(iax)
        row = self.session.query(IAXEndpoint).first()

        assert_that(created_iax.id, equal_to(row.id))
        assert_that(created_iax.name, has_length(8))
        assert_that(created_iax.type, equal_to('friend'))
        assert_that(created_iax.host, equal_to('dynamic'))
        assert_that(created_iax.category, equal_to('trunk'))

    def test_create_predefined_parameters(self):
        iax = IAXEndpoint(name='myname',
                          host="127.0.0.1",
                          type="peer")

        created_iax = iax_dao.create(iax)
        row = self.session.query(IAXEndpoint).first()

        assert_that(created_iax.id, equal_to(row.id))
        assert_that(created_iax.name, equal_to('myname'))
        assert_that(created_iax.type, equal_to('peer'))
        assert_that(created_iax.host, equal_to('127.0.0.1'))
        assert_that(created_iax.category, equal_to('trunk'))

    def test_create_with_native_options(self):
        expected_options = has_properties({
            'amaflags': 'default',
            'language': 'fr_FR',
            'qualify': '500',
            'callerid': '"cûstomcallerid" <1234>',
            'encryption': 'yes',
            'permit': '127.0.0.1',
            'deny': '127.0.0.1',
            'disallow': 'all',
            'allow': 'gsm',
            'accountcode': 'accountcode',
            'mohinterpret': 'mohinterpret',
            'parkinglot': 700,
            'fullname': 'fullname',
            'defaultip': '127.0.0.1',
            'regexten': 'regexten',
            'cid_number': '0123456789',
            'port': 10000,
            'jitterbuffer': 1,
            'forcejitterbuffer': 1,
            'trunk': 1,
            'adsi': 1,
            'sendani': 1,
            'qualifysmoothing': 1,
            'immediate': 1,
            'keyrotate': 1,
            'username': 'username',
            'secret': 'secret',
            'dbsecret': 'dbsecret',
            'mailbox': 'mailbox',
            'auth': 'md5',
            'forceencryption': 'aes128',
            'maxauthreq': 10,
            'inkeys': 'inkeys',
            'outkey': 'oukeys',
            'transfer': 'mediaonly',
            'codecpriority': 'disabled',
            'qualifyfreqok': 100,
            'qualifyfreqnotok': 20,
            'timezone': 'timezone',
            'mohsuggest': 'mohsuggest',
            'sourceaddress': 'sourceaddress',
            'setvar': 'setvar',
            'mask': 'mask',
            'peercontext': 'peercontext',
            'requirecalltoken': 'yes',
        })

        iax = IAXEndpoint(options=ALL_OPTIONS)
        created_iax = iax_dao.create(iax)

        row = self.session.query(IAXEndpoint).first()

        assert_that(created_iax.id, equal_to(row.id))
        assert_that(created_iax, expected_options)
        assert_that(created_iax.options, has_items(*ALL_OPTIONS))

    def test_create_with_additional_options(self):
        options = [
            ["language", "fr_FR"],
            ["foo", "bar"],
            ["foo", "baz"],
            ["spam", "eggs"]
        ]

        iax = IAXEndpoint(options=options)
        created_iax = iax_dao.create(iax)

        row = self.session.query(IAXEndpoint).first()

        assert_that(created_iax.id, equal_to(row.id))
        assert_that(created_iax.options, has_items(*options))


class TestEdit(DAOTestCase):

    def test_edit_basic_parameters(self):
        row = self.add_useriax()
        iax = iax_dao.get(row.id)

        iax.name = 'name'
        iax.type = 'peer'
        iax.host = '127.0.0.1'

        iax_dao.edit(iax)

        row = self.session.query(IAXEndpoint).first()
        assert_that(row.name, equal_to('name'))
        assert_that(row.type, equal_to('peer'))
        assert_that(row.host, equal_to('127.0.0.1'))

    def test_edit_remove_options(self):
        expected_options = has_properties({
            'amaflags': 'default',
            'language': none(),
            'qualify': 'no',
            'callerid': none(),
            'encryption': none(),
            'permit': none(),
            'deny': none(),
            'disallow': none(),
            'allow': none(),
            'accountcode': none(),
            'mohinterpret': none(),
            'parkinglot': none(),
            'fullname': none(),
            'defaultip': none(),
            'regexten': none(),
            'cid_number': none(),
            'port': none(),
            'jitterbuffer': none(),
            'forcejitterbuffer': none(),
            'trunk': 0,
            'adsi': none(),
            'sendani': 0,
            'qualifysmoothing': 0,
            'immediate': none(),
            'keyrotate': none(),
            'username': none(),
            'secret': empty(),
            'dbsecret': empty(),
            'mailbox': none(),
            'auth': 'plaintext,md5',
            'forceencryption': none(),
            'maxauthreq': none(),
            'inkeys': none(),
            'outkey': none(),
            'transfer': none(),
            'codecpriority': none(),
            'qualifyfreqok': 60000,
            'qualifyfreqnotok': 10000,
            'timezone': none(),
            'mohsuggest': none(),
            'sourceaddress': none(),
            'setvar': empty(),
            'mask': none(),
            'peercontext': none(),
            'requirecalltoken': 'no',
            '_options': empty(),
        })

        iax = iax_dao.create(IAXEndpoint(options=ALL_OPTIONS))
        iax = iax_dao.get(iax.id)
        iax.options = []

        iax_dao.edit(iax)

        row = self.session.query(IAXEndpoint).first()
        assert_that(row, expected_options)

    def test_edit_options(self):
        row = self.add_useriax(language="fr_FR", amaflags="default", allow="g729,gsm")

        iax = iax_dao.get(row.id)
        iax.options = [
            ["language", "en_US"],
            ["amaflags", "omit"],
            ["allow", "ulaw,alaw"],
        ]

        iax_dao.edit(iax)

        row = self.session.query(IAXEndpoint).first()
        assert_that(row.language, equal_to("en_US"))
        assert_that(row.amaflags, equal_to("omit"))
        assert_that(row.allow, equal_to("ulaw,alaw"))

    def test_edit_additional_options(self):
        row = self.add_useriax(_options=[
            ["foo", "bar"],
            ["foo", "baz"],
            ["spam", "eggs"],
        ])

        iax = iax_dao.get(row.id)
        iax.options = [
            ["foo", "newbar"],
            ["foo", "newbaz"],
            ["spam", "neweggs"],
        ]

        iax_dao.edit(iax)

        row = self.session.query(IAXEndpoint).first()
        assert_that(row._options, has_items(
            ["foo", "newbar"],
            ["foo", "newbaz"],
            ["spam", "neweggs"],
        ))

    def test_edit_both_native_and_additional_options(self):
        row = self.add_useriax(language="fr_FR",
                               amaflags="default",
                               allow="g729,gsm",
                               _options=[
                                   ["foo", "bar"],
                                   ["foo", "baz"],
                                   ["spam", "eggs"],
                               ])

        new_options = [
            ["language", "en_US"],
            ["amaflags", "omit"],
            ["allow", "ulaw,alaw"],
            ["foo", "newbar"],
            ["foo", "newbaz"],
            ["spam", "neweggs"],
        ]

        iax = iax_dao.get(row.id)
        iax.options = new_options
        iax_dao.edit(iax)

        row = self.session.query(IAXEndpoint).first()
        assert_that(row.options, has_items(*new_options))
        assert_that(row.language, equal_to("en_US"))
        assert_that(row.amaflags, equal_to("omit"))
        assert_that(row.allow, equal_to("ulaw,alaw"))
        assert_that(row._options, has_items(
            ["foo", "newbar"],
            ["foo", "newbaz"],
            ["spam", "neweggs"],
        ))


class TestDelete(DAOTestCase):

    def test_delete(self):
        row = self.add_useriax()

        iax = iax_dao.get(row.id)
        iax_dao.delete(iax)

        row = self.session.query(IAXEndpoint).first()
        assert_that(row, none())

    def test_given_endpoint_is_associated_to_trunk_then_trunk_is_dissociated(self):
        iax_row = self.add_useriax()
        trunk_row = self.add_trunk(endpoint='iax', endpoint_id=iax_row.id)

        iax = iax_dao.get(iax_row.id)
        iax_dao.delete(iax)

        trunk_row = self.session.query(Trunk).get(trunk_row.id)
        assert_that(trunk_row.endpoint, none())
        assert_that(trunk_row.endpoint_id, none())
