# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    all_of,
    assert_that,
    contains_exactly,
    contains_inanyorder,
    empty,
    equal_to,
    has_items,
    has_properties,
    is_not,
    none,
    not_,
)

from xivo_dao.alchemy.voicemail import Voicemail
from xivo_dao.helpers.exception import InputError, NotFoundError
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.resources.voicemail import dao as voicemail_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestFind(DAOTestCase):
    def test_find_no_voicemail(self):
        result = voicemail_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        voicemail_row = self.add_voicemail()

        voicemail = voicemail_dao.find(voicemail_row.id)

        assert_that(voicemail, equal_to(voicemail_row))

    def test_find_multi_tenant(self):
        tenant = self.add_tenant()
        context = self.add_context(tenant_uuid=tenant.uuid)
        voicemail = self.add_voicemail(context=context.name)

        result = voicemail_dao.find(voicemail.id, tenant_uuids=[tenant.uuid])
        assert_that(result, equal_to(voicemail))

        result = voicemail_dao.find(
            voicemail.id, tenant_uuids=[self.default_tenant.uuid]
        )
        assert_that(result, none())


class TestGet(DAOTestCase):
    def test_get_no_voicemail(self):
        self.assertRaises(NotFoundError, voicemail_dao.get, 42)

    def test_get(self):
        voicemail_row = self.add_voicemail()

        voicemail = voicemail_dao.get(voicemail_row.id)

        assert_that(voicemail, equal_to(voicemail_row))

    def test_get_multi_tenant(self):
        tenant = self.add_tenant()
        context = self.add_context(tenant_uuid=tenant.uuid)

        voicemail_row = self.add_voicemail(context=context.name)
        voicemail = voicemail_dao.get(voicemail_row.id, tenant_uuids=[tenant.uuid])
        assert_that(voicemail, equal_to(voicemail_row))

        voicemail_row = self.add_voicemail()
        self.assertRaises(
            NotFoundError,
            voicemail_dao.get,
            voicemail_row.id,
            tenant_uuids=[tenant.uuid],
        )


class TestFindBy(DAOTestCase):
    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, voicemail_dao.find_by, invalid=42)

    def test_get_by_custom_column(self):
        voicemail_row = self.add_voicemail(timezone='mytimezone')

        voicemail = voicemail_dao.find_by(timezone='mytimezone')

        assert_that(voicemail, equal_to(voicemail_row))
        assert_that(voicemail.timezone, equal_to('mytimezone'))

    def test_get_by_native_column(self):
        voicemail_row = self.add_voicemail(name='myname')

        voicemail = voicemail_dao.find_by(name='myname')

        assert_that(voicemail, equal_to(voicemail_row))
        assert_that(voicemail.name, equal_to('myname'))

    def test_given_voicemail_does_not_exist_then_returns_null(self):
        voicemail = voicemail_dao.find_by(id=42)

        assert_that(voicemail, none())

    def test_find_by_multi_tenant(self):
        tenant = self.add_tenant()
        context = self.add_context(tenant_uuid=tenant.uuid)

        voicemail_row = self.add_voicemail()
        voicemail = voicemail_dao.find_by(
            name=voicemail_row.name, tenant_uuids=[tenant.uuid]
        )
        assert_that(voicemail, none())

        voicemail_row = self.add_voicemail(context=context.name)
        voicemail = voicemail_dao.find_by(
            name=voicemail_row.name, tenant_uuids=[tenant.uuid]
        )
        assert_that(voicemail, equal_to(voicemail_row))


class TestGetBy(DAOTestCase):
    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, voicemail_dao.get_by, invalid=42)

    def test_get_by_custom_column(self):
        voicemail_row = self.add_voicemail(timezone='mytimezone')

        voicemail = voicemail_dao.get_by(timezone='mytimezone')

        assert_that(voicemail, equal_to(voicemail_row))
        assert_that(voicemail.timezone, equal_to('mytimezone'))

    def test_get_by_native_column(self):
        voicemail_row = self.add_voicemail(name='myname')

        voicemail = voicemail_dao.get_by(name='myname')

        assert_that(voicemail, equal_to(voicemail_row))
        assert_that(voicemail.name, equal_to('myname'))

    def test_given_voicemail_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, voicemail_dao.get_by, id='42')

    def test_get_by_multi_tenant(self):
        tenant = self.add_tenant()
        context = self.add_context(tenant_uuid=tenant.uuid)

        voicemail_row = self.add_voicemail()
        self.assertRaises(
            NotFoundError,
            voicemail_dao.get_by,
            id=voicemail_row.id,
            tenant_uuids=[tenant.uuid],
        )

        voicemail_row = self.add_voicemail(context=context.name)
        voicemail = voicemail_dao.get_by(
            id=voicemail_row.id, tenant_uuids=[tenant.uuid]
        )
        assert_that(voicemail, equal_to(voicemail_row))


class TestFindAllBy(DAOTestCase):
    def test_find_all_by_no_voicemail(self):
        result = voicemail_dao.find_all_by(name='toto')

        assert_that(result, contains_exactly())

    def test_find_all_by_custom_column(self):
        voicemail1 = self.add_voicemail(timezone='MyTimezone')
        voicemail2 = self.add_voicemail(timezone='MyTimezone')

        voicemails = voicemail_dao.find_all_by(timezone='MyTimezone')

        assert_that(voicemails, contains_inanyorder(voicemail1, voicemail2))

    def test_find_all_by_native_column(self):
        context = self.add_context(name='MyContext')
        voicemail1 = self.add_voicemail(context=context.name)
        voicemail2 = self.add_voicemail(context=context.name)

        voicemails = voicemail_dao.find_all_by(context=context.name)

        assert_that(voicemails, contains_inanyorder(voicemail1, voicemail2))

    def test_find_all_by_multi_tenant(self):
        tenant = self.add_tenant()
        context_1 = self.add_context(tenant_uuid=tenant.uuid)
        context_2 = self.add_context()

        voicemail1 = self.add_voicemail(timezone='timezone', context=context_1.name)
        voicemail2 = self.add_voicemail(timezone='timezone', context=context_2.name)

        tenants = [tenant.uuid, self.default_tenant.uuid]
        voicemails = voicemail_dao.find_all_by(
            timezone='timezone', tenant_uuids=tenants
        )
        assert_that(voicemails, has_items(voicemail1, voicemail2))

        tenants = [tenant.uuid]
        voicemails = voicemail_dao.find_all_by(
            timezone='timezone', tenant_uuids=tenants
        )
        assert_that(
            voicemails, all_of(has_items(voicemail1), not_(has_items(voicemail2)))
        )

    def test_find_all_by_access_type(self):
        global1 = self.add_voicemail(accesstype='global')
        personal1 = self.add_voicemail(accesstype='personal')
        personal2 = self.add_voicemail()

        voicemails = voicemail_dao.find_all_by(accesstype='global')
        assert_that(
            voicemails,
            all_of(has_items(global1), not_(has_items(personal1, personal2))),
        )
        voicemails = voicemail_dao.find_all_by(accesstype='personal')
        assert_that(
            voicemails,
            all_of(has_items(personal1, personal2), not_(has_items(global1))),
        )


class TestSearch(DAOTestCase):
    def assert_search_returns_result(self, search_result, **parameters):
        result = voicemail_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):
    def test_given_no_voicemail_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_voicemail_then_returns_one_result(self):
        voicemail = self.add_voicemail()
        expected = SearchResult(1, [voicemail])

        self.assert_search_returns_result(expected)

    def test_search_multi_tenant(self):
        tenant = self.add_tenant()
        context1 = self.add_context(tenant_uuid=self.default_tenant.uuid)
        context2 = self.add_context(tenant_uuid=tenant.uuid)

        voicemail1 = self.add_voicemail(mailbox='1001', context=context1.name)
        voicemail2 = self.add_voicemail(mailbox='1002', context=context2.name)

        expected = SearchResult(2, [voicemail1, voicemail2])
        tenants = [tenant.uuid, self.default_tenant.uuid]
        self.assert_search_returns_result(
            expected, tenant_uuids=tenants, order='number'
        )

        expected = SearchResult(1, [voicemail2])
        tenants = [tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)


class TestSearchGivenMultipleVoicemail(TestSearch):
    def setUp(self):
        super(TestSearch, self).setUp()
        self.resto = self.add_context(name='resto')
        self.bar = self.add_context(name='bar')
        self.voicemail1 = self.add_voicemail(
            name='Ashton', context=self.resto.name, number='1000'
        )
        self.voicemail2 = self.add_voicemail(
            name='Beaugarton', context=self.bar.name, number='1001'
        )
        self.voicemail3 = self.add_voicemail(
            name='Casa', context=self.resto.name, number='1002'
        )
        self.voicemail4 = self.add_voicemail(
            name='Dunkin', context=self.resto.name, number='1003'
        )

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.voicemail2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_searching_with_an_extra_argument(self):
        expected_resto = SearchResult(1, [self.voicemail1])
        self.assert_search_returns_result(
            expected_resto, search='ton', context=self.resto.name
        )

        expected_bar = SearchResult(1, [self.voicemail2])
        self.assert_search_returns_result(
            expected_bar, search='ton', context=self.bar.name
        )

        expected_all_resto = SearchResult(
            3, [self.voicemail1, self.voicemail3, self.voicemail4]
        )
        self.assert_search_returns_result(
            expected_all_resto, context=self.resto.name, order='name'
        )

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(
            4,
            [self.voicemail1, self.voicemail2, self.voicemail3, self.voicemail4],
        )

        self.assert_search_returns_result(expected, order='name')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(
        self,
    ):
        expected = SearchResult(
            4,
            [self.voicemail4, self.voicemail3, self.voicemail2, self.voicemail1],
        )

        self.assert_search_returns_result(expected, order='name', direction='desc')

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.voicemail1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_offset_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.voicemail2, self.voicemail3, self.voicemail4])

        self.assert_search_returns_result(expected, offset=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.voicemail2])

        self.assert_search_returns_result(
            expected,
            search='a',
            order='name',
            direction='desc',
            offset=1,
            limit=1,
        )


class TestCreate(DAOTestCase):
    def test_create_minimal_fields(self):
        context = self.add_context(name='default')
        voicemail = Voicemail(number='1000', context=context.name)
        created_voicemail = voicemail_dao.create(voicemail)

        row = self.session.query(Voicemail).first()

        assert_that(
            created_voicemail,
            all_of(
                equal_to(row),
                has_properties(
                    id=is_not(none()),
                    uniqueid=is_not(none()),
                    name='',
                    fullname='',
                    number='1000',
                    mailbox='1000',
                    context=context.name,
                    password=none(),
                    email=none(),
                    pager=none(),
                    timezone=none(),
                    tz=none(),
                    language=none(),
                    options=empty(),
                    max_messages=none(),
                    maxmsg=none(),
                    attach_audio=none(),
                    attach=none(),
                    delete_messages=False,
                    deletevoicemail=False,
                    ask_password=True,
                    skipcheckpass=False,
                    enabled=True,
                    commented=False,
                ),
            ),
        )

    def test_create_with_all_fields(self):
        context = self.add_context(name='from-extern')
        voicemail = Voicemail(
            name='myVoicemail',
            number='1000',
            context=context.name,
            password='12345',
            email='me@example.com',
            pager='12345',
            timezone='timezone',
            language='english',
            options=[['toto', 'tata']],
            max_messages=999,
            attach_audio=False,
            delete_messages=True,
            ask_password=False,
            enabled=False,
            accesstype='personal',
        )

        created_voicemail = voicemail_dao.create(voicemail)

        row = self.session.query(Voicemail).first()

        assert_that(
            created_voicemail,
            all_of(
                equal_to(row),
                has_properties(
                    id=is_not(none()),
                    name='myVoicemail',
                    fullname='myVoicemail',
                    number='1000',
                    mailbox='1000',
                    context=context.name,
                    password='12345',
                    email='me@example.com',
                    pager='12345',
                    timezone='timezone',
                    tz='timezone',
                    language='english',
                    options=[['toto', 'tata']],
                    max_messages=999,
                    maxmsg=999,
                    attach_audio=False,
                    attach=False,
                    delete_messages=True,
                    deletevoicemail=True,
                    ask_password=False,
                    skipcheckpass=True,
                    enabled=False,
                    commented=True,
                    accesstype='personal',
                ),
            ),
        )


class TestEdit(DAOTestCase):
    def test_edit_all_fields(self):
        context_from_extern = self.add_context(name='from-extern')
        voicemail = voicemail_dao.create(
            Voicemail(
                name='MyVoicemail',
                number='1000',
                context=context_from_extern.name,
                password='12345',
                email='me@example.com',
                pager='12345',
                timezone='timezone',
                language='english',
                options=[],
                max_messages=999,
                attach_audio=False,
                delete_messages=True,
                ask_password=False,
                enabled=False,
                accesstype='global',
            )
        )

        context_default = self.add_context(name='default')
        voicemail = voicemail_dao.get(voicemail.id)
        voicemail.name = 'other_name'
        voicemail.number = '1001'
        voicemail.context = context_default.name
        voicemail.password = '6789'
        voicemail.email = 'not_me@example.com'
        voicemail.pager = '6789'
        voicemail.timezone = 'other_timezone'
        voicemail.language = 'french'
        voicemail.options = [['option1', 'toto']]
        voicemail.max_messages = 8888
        voicemail.attach_audio = True
        voicemail.delete_messages = False
        voicemail.ask_password = True
        voicemail.enabled = True
        voicemail.accesstype = 'personal'

        row = self.session.query(Voicemail).first()

        assert_that(voicemail, equal_to(row))
        assert_that(
            row,
            has_properties(
                id=is_not(none()),
                name='other_name',
                fullname='other_name',
                number='1001',
                mailbox='1001',
                context=context_default.name,
                password='6789',
                email='not_me@example.com',
                pager='6789',
                timezone='other_timezone',
                tz='other_timezone',
                language='french',
                options=[['option1', 'toto']],
                max_messages=8888,
                maxmsg=8888,
                attach_audio=True,
                attach=True,
                delete_messages=False,
                deletevoicemail=False,
                ask_password=True,
                skipcheckpass=False,
                enabled=True,
                commented=False,
                accesstype='personal',
            ),
        )

    def test_edit_set_fields_to_null(self):
        context = self.add_context(name='default')
        voicemail = voicemail_dao.create(
            Voicemail(
                name='MyVoicemail',
                number='1000',
                context=context.name,
                password='12345',
                email='me@example.com',
                pager='12345',
                timezone='timezone',
                language='english',
                max_messages=999,
                attach_audio=False,
            )
        )

        voicemail = voicemail_dao.get(voicemail.id)
        voicemail.password = None
        voicemail.email = None
        voicemail.pager = None
        voicemail.timezone = None
        voicemail.language = None
        voicemail.max_messages = None
        voicemail.attach_audio = None

        voicemail_dao.edit(voicemail)

        row = self.session.query(Voicemail).first()
        assert_that(voicemail, equal_to(row))
        assert_that(
            row,
            has_properties(
                password=none(),
                email=none(),
                pager=none(),
                timezone=none(),
                language=none(),
                max_messages=none(),
                attach_audio=none(),
            ),
        )


class TestDelete(DAOTestCase):
    def test_delete(self):
        voicemail = self.add_voicemail()

        voicemail_dao.delete(voicemail)

        row = self.session.query(Voicemail).first()
        assert_that(row, none())
