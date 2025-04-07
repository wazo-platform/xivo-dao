# Copyright 2014-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    all_of,
    assert_that,
    contains_exactly,
    empty,
    equal_to,
    has_items,
    has_properties,
    has_property,
    is_not,
    none,
)

from xivo_dao.alchemy.callerid import Callerid
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.incall import Incall
from xivo_dao.helpers.exception import InputError, NotFoundError
from xivo_dao.resources.incall import dao as incall_dao
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DAOTestCase


class TestFind(DAOTestCase):
    def test_find_no_incall(self):
        result = incall_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        incall_row = self.add_incall()

        incall = incall_dao.find(incall_row.id)

        assert_that(incall, equal_to(incall_row))

    def test_multi_tenant(self):
        tenant = self.add_tenant()

        incall = self.add_incall(tenant_uuid=tenant.uuid)

        result = incall_dao.find(incall.id, tenant_uuids=[tenant.uuid])
        assert_that(
            result,
            all_of(
                has_properties(tenant_uuid=tenant.uuid),
                equal_to(incall),
            ),
        )

        result = incall_dao.find(incall.id, tenant_uuids=[self.default_tenant.uuid])
        assert_that(result, none())

        result = incall_dao.find(incall.id, tenant_uuids=[])
        assert_that(result, none())


class TestGet(DAOTestCase):
    def test_get_no_incall(self):
        self.assertRaises(NotFoundError, incall_dao.get, 42)

    def test_get(self):
        incall_row = self.add_incall()

        incall = incall_dao.get(incall_row.id)

        assert_that(incall, equal_to(incall_row))

    def test_get_multi_tenant(self):
        tenant = self.add_tenant()

        incall = self.add_incall(tenant_uuid=tenant.uuid)

        self.assertRaises(
            NotFoundError,
            incall_dao.get,
            incall.id,
            tenant_uuids=[self.default_tenant.uuid],
        )
        self.assertRaises(NotFoundError, incall_dao.get, incall.id, tenant_uuids=[])

        result = incall_dao.get(incall.id, tenant_uuids=[tenant.uuid])
        assert_that(result, equal_to(incall))


class TestFindBy(DAOTestCase):
    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, incall_dao.find_by, invalid=42)

    def test_find_by_preprocess_subroutine(self):
        incall_row = self.add_incall(preprocess_subroutine='mysubroutine')

        incall = incall_dao.find_by(preprocess_subroutine='mysubroutine')

        assert_that(incall, equal_to(incall_row))
        assert_that(incall.preprocess_subroutine, equal_to('mysubroutine'))

    def test_find_by_greeting_sound(self):
        incall_row = self.add_incall(greeting_sound='custom-sound')

        incall = incall_dao.find_by(greeting_sound='custom-sound')

        assert_that(incall, equal_to(incall_row))
        assert_that(incall.greeting_sound, equal_to('custom-sound'))

    def test_find_by_description(self):
        incall_row = self.add_incall(description='mydescription')

        incall = incall_dao.find_by(description='mydescription')

        assert_that(incall, equal_to(incall_row))
        assert_that(incall.description, equal_to('mydescription'))

    def test_find_by_user_id(self):
        incall_row = self.add_incall(
            destination=Dialaction(action='user', actionarg1='2')
        )

        incall = incall_dao.find_by(user_id=2)

        assert_that(incall, equal_to(incall_row))
        assert_that(incall.user_id, equal_to(2))

    def test_given_incall_does_not_exist_then_returns_null(self):
        incall = incall_dao.find_by(id=42)

        assert_that(incall, none())

    def test_find_by_multi_tenant(self):
        tenant = self.add_tenant()

        incall = self.add_incall(tenant_uuid=tenant.uuid)

        result = incall_dao.find_by(tenant_uuids=[self.default_tenant.uuid])
        assert_that(result, none())

        result = incall_dao.find_by(tenant_uuids=[])
        assert_that(result, none())

        result = incall_dao.find_by(tenant_uuids=[tenant.uuid])
        assert_that(result, equal_to(incall))


class TestGetBy(DAOTestCase):
    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, incall_dao.get_by, invalid=42)

    def test_get_by_preprocess_subroutine(self):
        incall_row = self.add_incall(preprocess_subroutine='MySubroutine')

        incall = incall_dao.get_by(preprocess_subroutine='MySubroutine')

        assert_that(incall, equal_to(incall_row))
        assert_that(incall.preprocess_subroutine, equal_to('MySubroutine'))

    def test_get_by_greeting_sound(self):
        incall_row = self.add_incall(greeting_sound='custom-sound')

        incall = incall_dao.get_by(greeting_sound='custom-sound')

        assert_that(incall, equal_to(incall_row))
        assert_that(incall.greeting_sound, equal_to('custom-sound'))

    def test_get_by_description(self):
        incall_row = self.add_incall(description='mydescription')

        incall = incall_dao.get_by(description='mydescription')

        assert_that(incall, equal_to(incall_row))
        assert_that(incall.description, equal_to('mydescription'))

    def test_get_by_user_id(self):
        incall_row = self.add_incall(
            destination=Dialaction(action='user', actionarg1='2')
        )

        incall = incall_dao.get_by(user_id=2)

        assert_that(incall, equal_to(incall_row))
        assert_that(incall.user_id, equal_to(2))

    def test_given_incall_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, incall_dao.get_by, id='42')

    def test_get_by_multi_tenant(self):
        tenant = self.add_tenant()

        incall = self.add_incall(tenant_uuid=tenant.uuid)

        self.assertRaises(NotFoundError, incall_dao.get_by, tenant_uuids=[])
        self.assertRaises(
            NotFoundError,
            incall_dao.get_by,
            tenant_uuids=[self.default_tenant.uuid],
        )

        result = incall_dao.get_by(tenant_uuids=[tenant.uuid])
        assert_that(result, equal_to(incall))


class TestFindAllBy(DAOTestCase):
    def test_find_all_by_no_incall(self):
        result = incall_dao.find_all_by(description='toto')

        assert_that(result, contains_exactly())

    def test_find_all_by_custom_column(self):
        incall1 = self.add_incall(
            preprocess_subroutine='mysub',
            destination=Dialaction(action='user', actionarg1='2'),
        )
        incall2 = self.add_incall(
            preprocess_subroutine='mysub',
            destination=Dialaction(action='user', actionarg1='2'),
        )
        self.add_incall(destination=Dialaction(action='user', actionarg1='3'))

        incalls = incall_dao.find_all_by(preprocess_subroutine='mysub')

        assert_that(
            incalls,
            has_items(has_property('id', incall1.id), has_property('id', incall2.id)),
        )

    def test_find_all_by_native_column(self):
        incall1 = self.add_incall(description='MyIncall')
        incall2 = self.add_incall(description='MyIncall')

        incalls = incall_dao.find_all_by(description='MyIncall')

        assert_that(
            incalls,
            has_items(has_property('id', incall1.id), has_property('id', incall2.id)),
        )

    def test_find_all_by_multi_tenant(self):
        tenant = self.add_tenant()

        incall = self.add_incall(tenant_uuid=tenant.uuid)

        result = incall_dao.find_all_by(
            id=incall.id, tenant_uuids=[self.default_tenant.uuid]
        )
        assert_that(result, empty())

        result = incall_dao.find_all_by(id=incall.id, tenant_uuids=[])
        assert_that(result, empty())

        result = incall_dao.find_all_by(id=incall.id, tenant_uuids=[tenant.uuid])
        assert_that(result, contains_exactly(incall))


class TestSearch(DAOTestCase):
    def assert_search_returns_result(self, search_result, **parameters):
        result = incall_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):
    def test_given_no_incall_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_incall_then_returns_one_result(self):
        incall = self.add_incall()
        expected = SearchResult(1, [incall])

        self.assert_search_returns_result(expected)

    def test_search_by_exten(self):
        self.add_incall()
        incall = self.add_incall()
        exten = self.add_extension(type='incall', typeval=str(incall.id))
        expected = SearchResult(1, [incall])

        self.assert_search_returns_result(expected, exten=exten.exten)


class TestSearchGivenMultipleIncall(TestSearch):
    def setUp(self):
        super(TestSearch, self).setUp()
        self.incall1 = self.add_incall(
            preprocess_subroutine='Ashton', description='resto'
        )
        self.incall2 = self.add_incall(
            preprocess_subroutine='Beaugarton', description='bar'
        )
        self.incall3 = self.add_incall(
            preprocess_subroutine='Casa', description='resto'
        )
        self.incall4 = self.add_incall(
            preprocess_subroutine='Dunkin', description='resto'
        )

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.incall2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_searching_with_an_extra_argument(self):
        expected_resto = SearchResult(1, [self.incall1])
        self.assert_search_returns_result(
            expected_resto, search='ton', description='resto'
        )

        expected_bar = SearchResult(1, [self.incall2])
        self.assert_search_returns_result(expected_bar, search='ton', description='bar')

        expected_all_resto = SearchResult(3, [self.incall1, self.incall3, self.incall4])
        self.assert_search_returns_result(
            expected_all_resto, description='resto', order='preprocess_subroutine'
        )

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(
            4, [self.incall1, self.incall2, self.incall3, self.incall4]
        )

        self.assert_search_returns_result(expected, order='preprocess_subroutine')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(
        self,
    ):
        expected = SearchResult(
            4, [self.incall4, self.incall3, self.incall2, self.incall1]
        )

        self.assert_search_returns_result(
            expected, order='preprocess_subroutine', direction='desc'
        )

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.incall1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_offset_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.incall2, self.incall3, self.incall4])

        self.assert_search_returns_result(expected, offset=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.incall2])

        self.assert_search_returns_result(
            expected,
            search='a',
            order='preprocess_subroutine',
            direction='desc',
            offset=1,
            limit=1,
        )


class TestSearchGivenMultipleTenants(TestSearch):
    def test_multiple_tenants(self):
        tenant_1 = self.add_tenant()
        tenant_2 = self.add_tenant()
        tenant_3 = self.add_tenant()

        incall_1 = self.add_incall(tenant_uuid=tenant_1.uuid)
        incall_2 = self.add_incall(tenant_uuid=tenant_2.uuid)
        incall_3 = self.add_incall(tenant_uuid=tenant_3.uuid)

        expected = SearchResult(2, [incall_1, incall_2])
        self.assert_search_returns_result(
            expected, tenant_uuids=[tenant_1.uuid, tenant_2.uuid]
        )

        expected = SearchResult(0, [])
        self.assert_search_returns_result(expected, tenant_uuids=[])

        expected = SearchResult(3, [incall_1, incall_2, incall_3])
        self.assert_search_returns_result(expected)


class TestCreate(DAOTestCase):
    def test_create_minimal_fields(self):
        incall = Incall(
            destination=Dialaction(action='none'), tenant_uuid=self.default_tenant.uuid
        )
        created_incall = incall_dao.create(incall)

        row = self.session.query(Incall).first()

        assert_that(created_incall, equal_to(row))
        assert_that(
            created_incall,
            has_properties(
                id=is_not(none()),
                preprocess_subroutine=none(),
                greeting_sound=none(),
                description=none(),
                caller_id_mode=none(),
                caller_id_name=none(),
                destination=has_properties(
                    action='none', actionarg1=None, actionarg2=None
                ),
                tenant_uuid=self.default_tenant.uuid,
            ),
        )

    def test_create_with_all_fields(self):
        incall = Incall(
            preprocess_subroutine='MySubroutine',
            greeting_sound='GreetingSound',
            description='incall description',
            caller_id_mode='prepend',
            caller_id_name='incall_',
            destination=Dialaction(action='user', actionarg1='2', actionarg2='10'),
            tenant_uuid=self.default_tenant.uuid,
        )

        created_incall = incall_dao.create(incall)

        row = self.session.query(Incall).first()

        assert_that(created_incall, equal_to(row))
        assert_that(
            created_incall,
            has_properties(
                id=is_not(none()),
                preprocess_subroutine='MySubroutine',
                greeting_sound='GreetingSound',
                description='incall description',
                caller_id_mode='prepend',
                caller_id_name='incall_',
                destination=has_properties(
                    action='user', actionarg1='2', actionarg2='10'
                ),
                tenant_uuid=self.default_tenant.uuid,
            ),
        )


class TestEdit(DAOTestCase):
    def test_edit_all_fields(self):
        incall = incall_dao.create(
            Incall(
                preprocess_subroutine='MySubroutine',
                greeting_sound='GreetingSound',
                description='incall description',
                caller_id_mode='prepend',
                caller_id_name='incall_',
                destination=Dialaction(action='user', actionarg1='2', actionarg2='10'),
                tenant_uuid=self.default_tenant.uuid,
            )
        )

        incall = incall_dao.get(incall.id)
        incall.preprocess_subroutine = 'other_subroutine'
        incall.greeting_sound = 'other_greeting_sound'
        incall.description = 'other description'
        incall.caller_id_mode = 'append'
        incall.caller_id_name = '_incall'
        incall.destination = Dialaction(action='queue', actionarg1='1', actionarg2='2')

        incall_dao.edit(incall)

        row = self.session.query(Incall).first()

        assert_that(incall, equal_to(row))
        assert_that(
            incall,
            has_properties(
                id=is_not(none()),
                preprocess_subroutine='other_subroutine',
                greeting_sound='other_greeting_sound',
                description='other description',
                caller_id_mode='append',
                caller_id_name='_incall',
                destination=has_properties(
                    action='queue', actionarg1='1', actionarg2='2'
                ),
            ),
        )

    def test_edit_set_fields_to_null(self):
        incall = incall_dao.create(
            Incall(
                preprocess_subroutine='MySubroutine',
                greeting_sound='GreetingSound',
                description='incall description',
                caller_id_mode='prepend',
                caller_id_name='incall_',
                destination=Dialaction(action='user', actionarg1='2', actionarg2='10'),
                tenant_uuid=self.default_tenant.uuid,
            )
        )
        incall = incall_dao.get(incall.id)
        incall.preprocess_subroutine = None
        incall.greeting_sound = None
        incall.description = None
        incall.caller_id_mode = None
        incall.caller_id_name = None
        incall.destination = Dialaction(action='none', actionarg1=None, actionarg2=None)

        incall_dao.edit(incall)

        row = self.session.query(Incall).first()
        assert_that(incall, equal_to(row))
        assert_that(
            row,
            has_properties(
                preprocess_subroutine=none(),
                greeting_sound=none(),
                description=none(),
                caller_id_mode=none(),
                caller_id_name=none(),
                destination=has_properties(
                    action='none', actionarg1=None, actionarg2=None
                ),
            ),
        )


class TestDelete(DAOTestCase):
    def test_delete(self):
        incall = self.add_incall()

        incall_dao.delete(incall)

        row = self.session.query(Incall).first()
        assert_that(row, none())

    def test_when_deleting_then_dialaction_and_callerid_are_deleted(self):
        incall = self.add_incall()

        incall_dao.delete(incall)

        dialaction = self.session.query(Dialaction).first()
        assert_that(dialaction, none())

        caller_id = self.session.query(Callerid).first()
        assert_that(caller_id, none())

    def test_when_deleting_then_extension_are_dissociated(self):
        incall = self.add_incall()
        extension = self.add_extension(type='incall', typeval=str(incall.id))

        incall_dao.delete(incall)

        extension = (
            self.session
            .query(Extension)
            .filter(Extension.id == extension.id)
            .first()
        )  # fmt: skip
        assert_that(extension, has_properties(type='user', typeval='0'))


class TestRelationship(DAOTestCase):
    def test_extensions_relationship(self):
        incall_row = self.add_incall()
        extension_row = self.add_extension(type='incall', typeval=str(incall_row.id))

        incall = incall_dao.get(incall_row.id)

        assert_that(incall, equal_to(incall_row))
        assert_that(incall.extensions, contains_exactly(extension_row))

    def test_group_relationship(self):
        group_row = self.add_group()
        incall_row = self.add_incall(
            destination=Dialaction(action='group', actionarg1=str(group_row.id))
        )
        incall = incall_dao.get(incall_row.id)
        assert_that(incall, equal_to(incall_row))
        assert_that(incall.destination.group, group_row)

    def test_user_relationship(self):
        user_row = self.add_user()
        incall_row = self.add_incall(
            destination=Dialaction(action='user', actionarg1=str(user_row.id))
        )
        incall = incall_dao.get(incall_row.id)
        assert_that(incall, equal_to(incall_row))
        assert_that(incall.destination.user, user_row)

    def test_ivr_relationship(self):
        ivr_row = self.add_ivr()
        incall_row = self.add_incall(
            destination=Dialaction(action='ivr', actionarg1=str(ivr_row.id))
        )
        incall = incall_dao.get(incall_row.id)
        assert_that(incall, equal_to(incall_row))
        assert_that(incall.destination.ivr, ivr_row)

    def test_voicemail_relationship(self):
        voicemail_row = self.add_voicemail()
        incall_row = self.add_incall(
            destination=Dialaction(action='voicemail', actionarg1=str(voicemail_row.id))
        )
        incall = incall_dao.get(incall_row.id)
        assert_that(incall, equal_to(incall_row))
        assert_that(incall.destination.voicemail, voicemail_row)
