# -*- coding: utf-8 -*-
# Copyright 2018-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

from hamcrest import (
    all_of,
    assert_that,
    empty,
    equal_to,
    has_item,
    has_items,
    has_length,
    has_properties,
    none,
    not_,
    not_none,
)
from sqlalchemy.inspection import inspect

from xivo_dao.alchemy.useriax import UserIAX as IAXEndpoint
from xivo_dao.helpers.exception import InputError, NotFoundError
from xivo_dao.resources.utils.search import SearchResult
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
        self.assertRaises(InputError, iax_dao.find_by, invalid=42)

    def test_given_row_with_value_does_not_exist_then_returns_null(self):
        result = iax_dao.find_by(name='abcd')
        assert_that(result, none())

    def test_find_by(self):
        iax_row = self.add_useriax(name='myname')
        iax = iax_dao.find_by(name='myname')

        assert_that(iax, equal_to(iax_row))

    def test_find_by_multi_tenant(self):
        tenant = self.add_tenant()

        iax_row = self.add_useriax()
        iax = iax_dao.find_by(name=iax_row.name, tenant_uuids=[tenant.uuid])
        assert_that(iax, none())

        iax_row = self.add_useriax(tenant_uuid=tenant.uuid)
        iax = iax_dao.find_by(name=iax_row.name, tenant_uuids=[tenant.uuid])
        assert_that(iax, equal_to(iax_row))


class TestFindAllBy(DAOTestCase):

    def test_find_all_multi_tenant(self):
        tenant = self.add_tenant()

        iax1 = self.add_useriax(language='en_US', tenant_uuid=tenant.uuid)
        iax2 = self.add_useriax(language='en_US')

        tenants = [tenant.uuid, self.default_tenant.uuid]
        iaxs = iax_dao.find_all_by(language='en_US', tenant_uuids=tenants)
        assert_that(iaxs, has_items(iax1, iax2))

        tenants = [tenant.uuid]
        iaxs = iax_dao.find_all_by(language='en_US', tenant_uuids=tenants)
        assert_that(iaxs, all_of(has_items(iax1), not_(has_items(iax2))))


class TestGet(DAOTestCase):

    def test_given_no_rows_then_raises_error(self):
        self.assertRaises(NotFoundError, iax_dao.get, 1)

    def test_get(self):
        iax_row = self.add_useriax(name='name', type='friend', host='dynamic')

        iax = iax_dao.get(iax_row.id)

        assert_that(iax, equal_to(iax_row))

    def test_get_with_optional_parameters(self):
        iax_row = self.add_useriax(language="fr_FR", amaflags="omit")

        iax = iax_dao.get(iax_row.id)

        assert_that(iax.options, has_items(
            ["language", "fr_FR"],
            ["amaflags", "omit"],
        ))

    def test_get_with_option_set_to_null_then_option_not_returned(self):
        iax_row = self.add_useriax(language=None, allow=None, callerid='')

        iax = iax_dao.get(iax_row.id)
        assert_that(iax.options, all_of(
            not_(has_item(has_item("language"))),
            not_(has_item(has_item("allow"))),
            not_(has_item(has_item("callerid"))),
        ))

    def test_get_with_additional_options(self):
        options = [
            ["foo", "bar"],
            ["foo", "baz"],
            ["spam", "eggs"]
        ]
        iax_row = self.add_useriax(options=options)

        iax = iax_dao.get(iax_row.id)

        assert_that(iax.options, has_items(*options))

    def test_given_row_has_native_and_additional_options_then_all_options_returned(self):
        iax_row = self.add_useriax(language="fr_FR", _options=[["foo", "bar"]])

        iax = iax_dao.get(iax_row.id)

        assert_that(iax.options, has_items(["language", "fr_FR"], ["foo", "bar"]))

    def test_get_multi_tenant(self):
        tenant = self.add_tenant()

        iax_row = self.add_useriax(tenant_uuid=tenant.uuid)
        iax = iax_dao.get(iax_row.id, tenant_uuids=[tenant.uuid])
        assert_that(iax, equal_to(iax_row))

        iax_row = self.add_useriax()
        self.assertRaises(
            NotFoundError,
            iax_dao.get, iax_row.id, tenant_uuids=[tenant.uuid],
        )


class TestSearch(DAOTestCase):

    def assert_search_returns_result(self, search_result, **parameters):
        result = iax_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):

    def test_given_no_iax_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_search(self):
        iax = self.add_useriax(name="alice")
        self.add_useriax(name="henry")

        expected = SearchResult(1, [iax])

        self.assert_search_returns_result(expected, search='alice')

    def test_search_multi_tenant(self):
        tenant = self.add_tenant()

        iax1 = self.add_useriax(name='sort1')
        iax2 = self.add_useriax(name='sort2', tenant_uuid=tenant.uuid)

        expected = SearchResult(2, [iax1, iax2])
        tenants = [tenant.uuid, self.default_tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)

        expected = SearchResult(1, [iax2])
        tenants = [tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)


class TestCreate(DAOTestCase):

    def test_create_minimal_parameters(self):
        iax_model = IAXEndpoint(tenant_uuid=self.default_tenant.uuid)
        iax = iax_dao.create(iax_model)

        assert_that(inspect(iax).persistent)
        assert_that(iax, has_properties(
            id=not_none(),
            name=has_length(8),
            type='friend',
            host='dynamic',
            category='trunk',
        ))

    def test_create_predefined_parameters(self):
        iax_model = IAXEndpoint(
            tenant_uuid=self.default_tenant.uuid,
            name='myname',
            host="127.0.0.1",
            type="peer",
        )

        iax = iax_dao.create(iax_model)

        assert_that(inspect(iax).persistent)
        assert_that(iax, has_properties(
            id=not_none(),
            tenant_uuid=self.default_tenant.uuid,
            name='myname',
            type='peer',
            host='127.0.0.1',
            category='trunk',
        ))

    def test_create_with_native_options(self):
        iax_model = IAXEndpoint(tenant_uuid=self.default_tenant.uuid, options=ALL_OPTIONS)
        iax = iax_dao.create(iax_model)

        self.session.expire_all()
        assert_that(inspect(iax).persistent)
        assert_that(iax.options, has_items(*ALL_OPTIONS))
        assert_that(iax, has_properties({
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
        }))

    def test_create_with_additional_options(self):
        options = [
            ["language", "fr_FR"],
            ["foo", "bar"],
            ["foo", "baz"],
            ["spam", "eggs"]
        ]
        iax_model = IAXEndpoint(tenant_uuid=self.default_tenant.uuid, options=options)

        iax = iax_dao.create(iax_model)

        self.session.expire_all()
        assert_that(inspect(iax).persistent)
        assert_that(iax.options, has_items(*options))


class TestEdit(DAOTestCase):

    def test_edit_basic_parameters(self):
        iax = self.add_useriax()

        self.session.expire_all()
        iax.name = 'name'
        iax.type = 'peer'
        iax.host = '127.0.0.1'
        iax_dao.edit(iax)

        self.session.expire_all()
        assert_that(iax, has_properties(
            name='name',
            type='peer',
            host='127.0.0.1',
        ))

    def test_edit_remove_options(self):
        iax = self.add_useriax(options=ALL_OPTIONS)

        self.session.expire_all()
        iax.options = []
        iax_dao.edit(iax)

        self.session.expire_all()
        assert_that(iax, has_properties({
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
        }))

    def test_edit_options(self):
        iax = self.add_useriax(language="fr_FR", amaflags="default", allow="g729,gsm")

        self.session.expire_all()
        iax.options = [
            ["language", "en_US"],
            ["amaflags", "omit"],
            ["allow", "ulaw,alaw"],
        ]
        iax_dao.edit(iax)

        self.session.expire_all()
        assert_that(iax, has_properties(
            language='en_US',
            amaflags='omit',
            allow='ulaw,alaw'
        ))

    def test_edit_additional_options(self):
        iax = self.add_useriax(_options=[
            ["foo", "bar"],
            ["foo", "baz"],
            ["spam", "eggs"],
        ])

        self.session.expire_all()
        iax.options = [
            ["foo", "newbar"],
            ["foo", "newbaz"],
            ["spam", "neweggs"],
        ]
        iax_dao.edit(iax)

        self.session.expire_all()
        assert_that(iax, has_properties(
            _options=has_items(
                ["foo", "newbar"],
                ["foo", "newbaz"],
                ["spam", "neweggs"],
            )
        ))

    def test_edit_both_native_and_additional_options(self):
        iax = self.add_useriax(
            language="fr_FR",
            amaflags="default",
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
            ["allow", "ulaw,alaw"],
            ["foo", "newbar"],
            ["foo", "newbaz"],
            ["spam", "neweggs"],
        ]

        self.session.expire_all()
        iax.options = new_options
        iax_dao.edit(iax)

        self.session.expire_all()
        assert_that(iax, has_properties(
            options=has_items(*new_options),
            language='en_US',
            amaflags='omit',
            allow='ulaw,alaw',
            _options=has_items(
                ["foo", "newbar"],
                ["foo", "newbaz"],
                ["spam", "neweggs"],
            ),
        ))


class TestDelete(DAOTestCase):

    def test_delete(self):
        iax = self.add_useriax()

        iax_dao.delete(iax)

        assert_that(inspect(iax).deleted)

    def test_given_endpoint_is_associated_to_trunk_then_trunk_is_dissociated(self):
        iax = self.add_useriax()
        trunk = self.add_trunk(endpoint_iax_id=iax.id)

        iax_dao.delete(iax)

        self.session.expire_all()
        assert_that(trunk, has_properties(endpoint_iax_id=none()))
