# Copyright 2024-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    calling,
    contains_exactly,
    equal_to,
    has_properties,
    none,
    not_,
    raises,
)
from sqlalchemy.exc import IntegrityError

from xivo_dao.alchemy.phone_number import PhoneNumber
from xivo_dao.helpers.exception import InputError, NotFoundError
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DEFAULT_TENANT, DAOTestCase

from .. import dao

UNKNOWN_UUID = '99999999-9999-4999-8999-999999999999'
SAMPLE_NUMBER = '+15551234567'
SAMPLE_NUMBER_2 = '+18001234567'


class TestFind(DAOTestCase):
    def test_find_no_match(self):
        result = dao.find(UNKNOWN_UUID)

        assert_that(result, none())

    def test_find(self):
        row = self.add_phone_number(
            number=SAMPLE_NUMBER,
        )

        result = dao.find(row.uuid)

        assert_that(result, equal_to(row))


class TestGet(DAOTestCase):
    def test_get_no_match(self):
        self.assertRaises(NotFoundError, dao.get, UNKNOWN_UUID)

    def test_get(self):
        row = self.add_phone_number(
            number=SAMPLE_NUMBER,
        )

        result = dao.get(row.uuid)

        assert_that(result, equal_to(row))


class TestFindBy(DAOTestCase):
    def test_given_column_does_not_exist(self):
        self.assertRaises(InputError, dao.find_by, invalid=42)

    def test_find_by_number(self):
        row = self.add_phone_number(number=SAMPLE_NUMBER)

        result = dao.find_by(number=SAMPLE_NUMBER)

        assert_that(result, equal_to(row))
        assert_that(result.number, equal_to(SAMPLE_NUMBER))

    def test_find_by_number_no_match(self):
        not_matched = SAMPLE_NUMBER.replace('5', '6')

        self.add_phone_number(number=SAMPLE_NUMBER)

        result = dao.find_by(number=not_matched)

        assert_that(result, equal_to(None))

    def test_find_by_shared(self):
        row = self.add_phone_number(
            number=SAMPLE_NUMBER,
            shared=True,
        )

        result = dao.find_by(shared=True)

        assert_that(result, equal_to(row))
        assert_that(result.shared, equal_to(True))

    def test_find_by_shared_no_match(self):
        self.add_phone_number(
            number=SAMPLE_NUMBER,
            shared=True,
        )

        result = dao.find_by(shared=False)

        assert_that(result, equal_to(None))

    def test_find_by_main(self):
        row = self.add_phone_number(
            number=SAMPLE_NUMBER,
            main=True,
        )

        result = dao.find_by(main=True)

        assert_that(result, equal_to(row))
        assert_that(result.main, equal_to(True))

    def test_find_by_main_no_match(self):
        self.add_phone_number(
            number=SAMPLE_NUMBER,
            main=True,
        )

        result = dao.find_by(main=False)

        assert_that(result, equal_to(None))

    def test_find_by_caller_id_name(self):
        name = 'Alice'
        row = self.add_phone_number(
            number=SAMPLE_NUMBER,
            caller_id_name=name,
        )

        result = dao.find_by(caller_id_name=name)

        assert_that(result, equal_to(row))
        assert_that(result.caller_id_name, equal_to(name))

    def test_find_by_caller_id_name_no_match(self):
        name = 'Alice'
        self.add_phone_number(
            number=SAMPLE_NUMBER,
        )

        result = dao.find_by(caller_id_name=name)

        assert_that(result, equal_to(None))


class TestGetBy(DAOTestCase):
    def test_given_column_does_not_exist(self):
        self.assertRaises(InputError, dao.get_by, invalid=42)

    def test_get_by_number(self):
        row = self.add_phone_number(number=SAMPLE_NUMBER)

        result = dao.get_by(number=SAMPLE_NUMBER)

        assert_that(result, equal_to(row))
        assert_that(result.number, equal_to(SAMPLE_NUMBER))

    def test_get_by_number_no_match(self):
        not_matched = SAMPLE_NUMBER.replace('5', '6')

        self.add_phone_number(number=SAMPLE_NUMBER)

        self.assertRaises(NotFoundError, dao.get_by, number=not_matched)

    def test_get_by_shared(self):
        row = self.add_phone_number(
            number=SAMPLE_NUMBER,
            shared=True,
        )

        result = dao.get_by(shared=True)

        assert_that(result, equal_to(row))
        assert_that(result.shared, equal_to(True))

    def test_get_by_shared_no_match(self):
        self.add_phone_number(
            number=SAMPLE_NUMBER,
            shared=True,
        )

        self.assertRaises(NotFoundError, dao.get_by, shared=False)

    def test_get_by_main(self):
        row = self.add_phone_number(
            number=SAMPLE_NUMBER,
            main=True,
        )

        result = dao.get_by(main=True)

        assert_that(result, equal_to(row))
        assert_that(result.main, equal_to(True))

    def test_get_by_main_no_match(self):
        self.add_phone_number(
            number=SAMPLE_NUMBER,
            main=True,
        )

        self.assertRaises(NotFoundError, dao.get_by, main=False)

    def test_get_by_caller_id_name(self):
        name = 'Alice'
        row = self.add_phone_number(
            number=SAMPLE_NUMBER,
            caller_id_name=name,
        )

        result = dao.get_by(caller_id_name=name)

        assert_that(result, equal_to(row))
        assert_that(result.caller_id_name, equal_to(name))

    def test_get_by_caller_id_name_no_match(self):
        name = 'Alice'
        self.add_phone_number(
            number=SAMPLE_NUMBER,
        )

        self.assertRaises(NotFoundError, dao.get_by, caller_id_name=name)


class TestFindAllBy(DAOTestCase):
    def test_given_column_does_not_exist(self):
        self.assertRaises(InputError, dao.find_all_by, invalid=42)

    def test_find_all_by_no_match(self):
        result = dao.find_all_by(number=SAMPLE_NUMBER)

        assert_that(result, contains_exactly())

    def test_find_all_by_number(self):
        not_matched = SAMPLE_NUMBER.replace('5', '6')

        row = self.add_phone_number(number=SAMPLE_NUMBER)
        self.add_phone_number(number=not_matched)

        result = dao.find_all_by(number=SAMPLE_NUMBER)

        assert_that(result, contains_exactly(row))

    def test_find_all_by_shared(self):
        row = self.add_phone_number(
            number=SAMPLE_NUMBER,
            shared=True,
        )
        self.add_phone_number(
            number=SAMPLE_NUMBER_2,
            shared=False,
        )

        result = dao.find_all_by(shared=True)

        assert_that(result, contains_exactly(row))

    def test_find_all_by_main(self):
        row = self.add_phone_number(
            number=SAMPLE_NUMBER,
            main=True,
        )
        self.add_phone_number(
            number=SAMPLE_NUMBER_2,
            main=False,
        )

        result = dao.find_all_by(main=True)

        assert_that(result, contains_exactly(row))

    def test_find_all_by_caller_id_name(self):
        name = 'Alice'
        row = self.add_phone_number(
            number=SAMPLE_NUMBER,
            caller_id_name=name,
        )
        self.add_phone_number(
            number=SAMPLE_NUMBER_2,
        )

        result = dao.find_all_by(caller_id_name=name)

        assert_that(result, contains_exactly(row))

    def test_find_all_by_multiple_numbers(self):
        row1 = self.add_phone_number(number=SAMPLE_NUMBER)
        row2 = self.add_phone_number(number=SAMPLE_NUMBER_2)

        result = dao.find_all_by(number_in=[SAMPLE_NUMBER, SAMPLE_NUMBER_2])

        assert_that(result, contains_exactly(row1, row2))

    def find_all_multitenant(self):
        tenant = self.add_tenant()
        name = 'Alice'
        alice = self.add_phone_number(
            number=SAMPLE_NUMBER, caller_id_name=name, tenant_uuid=tenant.uuid
        )
        bob = self.add_phone_number(
            number=SAMPLE_NUMBER,
            name='Bob',
        )

        result = dao.find_all_by(number=SAMPLE_NUMBER)

        assert_that(result, contains_exactly(alice, bob))

        result = dao.find_all_by(number=SAMPLE_NUMBER, tenant_uuids=[tenant.uuid])

        assert_that(result, contains_exactly(alice))

        result = dao.find_all_by(number=SAMPLE_NUMBER, tenant_uuids=[DEFAULT_TENANT])

        assert_that(result, contains_exactly(bob))


class TestSearch(DAOTestCase):
    def assert_search_returns_result(self, search_result, **parameters):
        result = dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):
    def test_given_no_phone_number_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_phone_number_then_returns_one_result(self):
        row = self.add_phone_number(number=SAMPLE_NUMBER)
        expected = SearchResult(1, [row])

        self.assert_search_returns_result(expected)


class TestSearchGivenMultiplePhoneNumbers(TestSearch):
    def setUp(self):
        super(TestSearch, self).setUp()
        self.row_1 = self.add_phone_number(
            number='+15551230000', caller_id_name='one', shared=True, main=True
        )
        self.row_2 = self.add_phone_number(
            number='+15551231111', caller_id_name='two', shared=True, main=False
        )
        self.row_3 = self.add_phone_number(
            number='+15551232222', caller_id_name='three', shared=False, main=False
        )
        self.row_4 = self.add_phone_number(
            number='+15551233333', shared=False, main=False
        )

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.row_1])

        self.assert_search_returns_result(expected, search='one')

    def test_when_searching_with_an_extra_argument(self):
        expected = SearchResult(3, [self.row_2, self.row_3, self.row_4])
        self.assert_search_returns_result(
            expected,
            search='555',
            main=False,
        )

        expected = SearchResult(1, [self.row_3])
        self.assert_search_returns_result(
            expected, search='555', caller_id_name='three'
        )

        expected = SearchResult(2, [self.row_1, self.row_2])
        self.assert_search_returns_result(
            expected,
            shared=True,
            order='number',
        )

    def test_sort(self):
        expected = SearchResult(4, [self.row_1, self.row_3, self.row_2, self.row_4])

        self.assert_search_returns_result(expected, order='caller_id_name')

    def test_sort_order(self):
        expected = SearchResult(4, [self.row_4, self.row_2, self.row_3, self.row_1])

        self.assert_search_returns_result(
            expected, order='caller_id_name', direction='desc'
        )

    def test_limit(self):
        expected = SearchResult(4, [self.row_1])

        self.assert_search_returns_result(expected, limit=1)

    def test_offset(self):
        expected = SearchResult(4, [self.row_2, self.row_3, self.row_4])

        self.assert_search_returns_result(expected, offset=1)

    def test_pagination(self):
        expected = SearchResult(2, [self.row_1])

        self.assert_search_returns_result(
            expected,
            search='555',
            shared=True,
            direction='desc',
            offset=1,
            limit=1,
        )


class TestCreate(DAOTestCase):
    def test_create_minimal_fields(self):
        tenant = self.add_tenant()
        phone_number = PhoneNumber(
            number=SAMPLE_NUMBER,
            tenant_uuid=tenant.uuid,
        )

        created_phone_number = dao.create(phone_number)

        row = self.session.query(PhoneNumber).first()

        assert_that(created_phone_number, equal_to(row))
        assert_that(
            created_phone_number,
            has_properties(
                uuid=row.uuid,
                number=SAMPLE_NUMBER,
                shared=False,
                main=False,
                caller_id_name=None,
                tenant_uuid=tenant.uuid,
            ),
        )

    def test_create_all_fields(self):
        tenant = self.add_tenant()
        name = 'Alice'
        phone_number = PhoneNumber(
            number=SAMPLE_NUMBER,
            tenant_uuid=tenant.uuid,
            caller_id_name=name,
            main=True,
            shared=True,
        )

        created_phone_number = dao.create(phone_number)

        row = self.session.query(PhoneNumber).first()

        assert_that(created_phone_number, equal_to(row))
        assert_that(
            created_phone_number,
            has_properties(
                uuid=row.uuid,
                number=SAMPLE_NUMBER,
                shared=True,
                main=True,
                caller_id_name=name,
                tenant_uuid=tenant.uuid,
            ),
        )


class TestEdit(DAOTestCase):
    def test_edit_all_fields(self):
        tenant = self.add_tenant()
        created_phone_number = dao.create(
            PhoneNumber(
                number=SAMPLE_NUMBER,
                tenant_uuid=tenant.uuid,
                caller_id_name='Alice',
                main=True,
                shared=True,
            )
        )

        phone_number = dao.get(created_phone_number.uuid)
        new_number = phone_number.number = '+18001234567'
        new_caller_id = phone_number.caller_id_name = 'Bob'
        new_main = phone_number.main = False
        new_shared = phone_number.shared = False

        dao.edit(phone_number)

        row = self.session.query(PhoneNumber).first()

        assert_that(phone_number, equal_to(row))
        assert_that(
            row,
            has_properties(
                uuid=created_phone_number.uuid,
                tenant_uuid=created_phone_number.tenant_uuid,
                number=new_number,
                caller_id_name=new_caller_id,
                main=new_main,
                shared=new_shared,
            ),
        )

    def test_edit_set_fields_to_null(self):
        tenant = self.add_tenant()
        created_phone_number = dao.create(
            PhoneNumber(
                number=SAMPLE_NUMBER,
                tenant_uuid=tenant.uuid,
                caller_id_name='Alice',
                main=True,
                shared=True,
            )
        )

        phone_number = dao.get(created_phone_number.uuid)
        phone_number.caller_id_name = None

        dao.edit(phone_number)

        row = self.session.query(PhoneNumber).first()

        assert_that(phone_number, equal_to(row))
        assert_that(
            row,
            has_properties(
                caller_id_name=None,
            ),
        )

    def test_edit_set_main_implies_shared(self):
        tenant = self.add_tenant()
        created_phone_number = dao.create(
            PhoneNumber(
                number=SAMPLE_NUMBER, tenant_uuid=tenant.uuid, caller_id_name='Alice'
            )
        )

        phone_number = dao.get(created_phone_number.uuid)
        assert_that(not phone_number.shared)
        assert_that(not phone_number.main)

        phone_number.main = True

        dao.edit(phone_number)

        main = self.session.query(PhoneNumber).filter(PhoneNumber.main).first()

        assert_that(phone_number, equal_to(main))
        assert_that(main.shared)


class TestDelete(DAOTestCase):
    def test_delete(self):
        phone_number = self.add_phone_number(number=SAMPLE_NUMBER)

        dao.delete(phone_number)

        row = self.session.query(PhoneNumber).first()
        assert_that(row, none())


class TestThatNumberIsUnique(DAOTestCase):
    def setUp(self):
        super().setUp()
        self._phone_number = self.add_phone_number(number=SAMPLE_NUMBER)

    def test_unique_number_on_create(self):
        assert_that(
            calling(self.add_phone_number).with_args(number=SAMPLE_NUMBER),
            raises(IntegrityError),
        )

    def test_unique_number_on_create_multi_tenant(self):
        other_tenant = self.add_tenant()
        assert_that(
            calling(self.add_phone_number).with_args(
                number=SAMPLE_NUMBER,
                tenant_uuid=other_tenant.uuid,
            ),
            not_(raises(IntegrityError)),
        )

    def test_unique_number_on_edit(self):
        created_phone_number = self.add_phone_number(number=SAMPLE_NUMBER_2)

        phone_number = dao.get(created_phone_number.uuid)
        phone_number.number = SAMPLE_NUMBER

        assert_that(
            calling(dao.edit).with_args(phone_number),
            raises(IntegrityError),
        )


class TestThatMainIsUnique(DAOTestCase):
    def setUp(self):
        super().setUp()
        self._phone_number = self.add_phone_number(
            number=SAMPLE_NUMBER,
            main=True,
        )

    def test_unique_main_on_create(self):
        assert_that(
            calling(self.add_phone_number).with_args(
                number=SAMPLE_NUMBER_2,
                main=True,
            ),
            raises(IntegrityError),
        )

    def test_unique_main_on_create_multi_tenant(self):
        other_tenant = self.add_tenant()
        assert_that(
            calling(self.add_phone_number).with_args(
                number=SAMPLE_NUMBER_2,
                main=True,
                tenant_uuid=other_tenant.uuid,
            ),
            not_(raises(IntegrityError)),
        )

    def test_unique_main_on_edit(self):
        created_phone_number = self.add_phone_number(number=SAMPLE_NUMBER_2)

        phone_number = dao.get(created_phone_number.uuid)
        phone_number.main = True

        assert_that(
            calling(dao.edit).with_args(phone_number),
            raises(IntegrityError),
        )
