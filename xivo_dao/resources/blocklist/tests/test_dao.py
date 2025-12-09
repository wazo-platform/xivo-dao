# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    calling,
    contains_exactly,
    equal_to,
    has_properties,
    none,
    raises,
)
from sqlalchemy.exc import IntegrityError

from xivo_dao.alchemy.blocklist import Blocklist
from xivo_dao.alchemy.blocklist_number import BlocklistNumber
from xivo_dao.alchemy.blocklist_user import BlocklistUser
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.helpers.exception import InputError, NotFoundError
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DEFAULT_TENANT, DAOTestCase

from .. import dao

UNKNOWN_UUID = '99999999-9999-4999-8999-999999999999'
SAMPLE_NUMBER = '+15551234567'
SAMPLE_NUMBER_2 = '+18001234567'
USER_UUID = '99999999-9999-4999-8999-999999999999'
USER_UUID_2 = '99999999-9999-4999-8999-999999999998'


class BlocklistDAOTestCase(DAOTestCase):
    def setUp(self):
        super().setUp()
        self.user_1 = self.add_user(uuid=USER_UUID, tenant_uuid=DEFAULT_TENANT)
        self.user_2 = self.add_user(uuid=USER_UUID_2, tenant_uuid=DEFAULT_TENANT)

    def add_blocklist(self, numbers, user_uuid=None, tenant_uuid=None):
        blocklist = Blocklist(
            numbers=numbers,
            _user_link=BlocklistUser(user_uuid=user_uuid) if user_uuid else None,
            tenant_uuid=tenant_uuid
            or self.session.query(UserFeatures)
            .filter(UserFeatures.uuid == user_uuid)
            .first()
            .tenant_uuid
            if user_uuid
            else self.default_tenant.uuid,
        )
        self.add_me(blocklist)
        return blocklist

    def add_blocklist_number(self, **kwargs):
        if blocklist_uuid := kwargs.pop('blocklist_uuid', None):
            blocklist = self.session.get(Blocklist, blocklist_uuid)
        else:
            blocklist = self.add_blocklist(
                numbers=[],
                user_uuid=kwargs.pop('user_uuid', None),
                tenant_uuid=kwargs.pop('tenant_uuid', None),
            )

        blocklist_number = BlocklistNumber(blocklist=blocklist, **kwargs)
        self.add_me(blocklist_number)
        return blocklist_number

    def add_blocklist_user(self, **kwargs):
        blocklist_user = BlocklistUser(**kwargs)
        self.add_me(blocklist_user)
        return blocklist_user


class TestFind(BlocklistDAOTestCase):
    def test_find_no_match(self):
        result = dao.find(UNKNOWN_UUID)

        assert_that(result, none())

    def test_find(self):
        row = self.add_blocklist_number(
            number=SAMPLE_NUMBER,
            user_uuid=USER_UUID,
        )

        result = dao.find(row.uuid)

        assert_that(result, equal_to(row))


class TestGet(BlocklistDAOTestCase):
    def test_get_no_match(self):
        self.assertRaises(NotFoundError, dao.get, UNKNOWN_UUID)

    def test_get(self):
        row = self.add_blocklist_number(
            number=SAMPLE_NUMBER,
            user_uuid=USER_UUID,
        )

        result = dao.get(row.uuid)

        assert_that(result, equal_to(row))


class TestFindBy(BlocklistDAOTestCase):
    def test_given_column_does_not_exist(self):
        self.assertRaises(InputError, dao.find_by, invalid=42)

    def test_find_by_number(self):
        row = self.add_blocklist_number(number=SAMPLE_NUMBER, user_uuid=USER_UUID)

        result = dao.find_by(number=SAMPLE_NUMBER)

        assert_that(result, equal_to(row))
        assert_that(result.number, equal_to(SAMPLE_NUMBER))

    def test_find_by_number_no_match(self):
        not_matched = SAMPLE_NUMBER.replace('5', '6')

        self.add_blocklist_number(number=SAMPLE_NUMBER, user_uuid=USER_UUID)

        result = dao.find_by(number=not_matched)

        assert_that(result, equal_to(None))

    def test_find_by_label(self):
        name = 'Alice'
        row = self.add_blocklist_number(
            number=SAMPLE_NUMBER,
            label=name,
            user_uuid=USER_UUID,
        )

        result = dao.find_by(label=name)

        assert_that(result, equal_to(row))
        assert_that(result.label, equal_to(name))

    def test_find_by_label_no_match(self):
        name = 'Alice'
        self.add_blocklist_number(
            number=SAMPLE_NUMBER,
            user_uuid=USER_UUID,
        )

        result = dao.find_by(label=name)

        assert_that(result, equal_to(None))

    def test_find_by_user_uuid(self):
        row = self.add_blocklist_number(
            number=SAMPLE_NUMBER,
            user_uuid=USER_UUID,
        )

        result = dao.find_by(user_uuid=USER_UUID)

        assert_that(result, equal_to(row))

    def test_find_by_user_uuid_no_match(self):
        self.add_blocklist_number(
            number=SAMPLE_NUMBER,
            user_uuid=USER_UUID,
        )

        result = dao.find_by(user_uuid=USER_UUID_2)

        assert_that(result, equal_to(None))

    def test_find_by_blocklist_uuid(self):
        row = self.add_blocklist_number(
            number=SAMPLE_NUMBER,
            user_uuid=USER_UUID,
        )

        result = dao.find_by(blocklist_uuid=row.blocklist_uuid)

        assert_that(result, equal_to(row))

    def test_find_by_blocklist_uuid_no_match(self):
        self.add_blocklist_number(
            number=SAMPLE_NUMBER,
            user_uuid=USER_UUID,
        )

        result = dao.find_by(blocklist_uuid=UNKNOWN_UUID)

        assert_that(result, equal_to(None))


class TestGetBy(BlocklistDAOTestCase):
    def test_given_column_does_not_exist(self):
        self.assertRaises(InputError, dao.get_by, invalid=42)

    def test_get_by_number(self):
        row = self.add_blocklist_number(number=SAMPLE_NUMBER, user_uuid=USER_UUID)

        result = dao.get_by(number=SAMPLE_NUMBER)

        assert_that(result, equal_to(row))
        assert_that(result.number, equal_to(SAMPLE_NUMBER))

    def test_get_by_number_no_match(self):
        not_matched = SAMPLE_NUMBER.replace('5', '6')

        self.add_blocklist_number(number=SAMPLE_NUMBER, user_uuid=USER_UUID)

        self.assertRaises(NotFoundError, dao.get_by, number=not_matched)

    def test_get_by_label(self):
        name = 'Alice'
        row = self.add_blocklist_number(
            number=SAMPLE_NUMBER,
            label=name,
            user_uuid=USER_UUID,
        )

        result = dao.get_by(label=name)

        assert_that(result, equal_to(row))
        assert_that(result.label, equal_to(name))

    def test_get_by_label_no_match(self):
        name = 'Alice'
        self.add_blocklist_number(
            number=SAMPLE_NUMBER,
            user_uuid=USER_UUID,
        )

        self.assertRaises(NotFoundError, dao.get_by, label=name)

    def test_get_by_user_uuid(self):
        row = self.add_blocklist_number(
            number=SAMPLE_NUMBER,
            user_uuid=USER_UUID,
        )

        result = dao.get_by(user_uuid=USER_UUID)

        assert_that(result, equal_to(row))

    def test_get_by_user_uuid_no_match(self):
        self.add_blocklist_number(
            number=SAMPLE_NUMBER,
            user_uuid=USER_UUID,
        )

        self.assertRaises(NotFoundError, dao.get_by, user_uuid=USER_UUID_2)


class TestFindAllBy(BlocklistDAOTestCase):
    def test_given_column_does_not_exist(self):
        self.assertRaises(InputError, dao.find_all_by, invalid=42)

    def test_find_all_by_no_match(self):
        result = dao.find_all_by(number=SAMPLE_NUMBER)

        assert_that(result, contains_exactly())

    def test_find_all_by_number(self):
        not_matched = SAMPLE_NUMBER.replace('5', '6')

        row = self.add_blocklist_number(number=SAMPLE_NUMBER, user_uuid=USER_UUID)
        self.add_blocklist_number(number=not_matched, user_uuid=USER_UUID)

        result = dao.find_all_by(number=SAMPLE_NUMBER)

        assert_that(result, contains_exactly(row))

    def test_find_all_by_label(self):
        name = 'Alice'
        row = self.add_blocklist_number(
            number=SAMPLE_NUMBER,
            label=name,
            user_uuid=USER_UUID,
        )
        self.add_blocklist_number(
            number=SAMPLE_NUMBER_2,
            user_uuid=USER_UUID,
        )

        result = dao.find_all_by(label=name)

        assert_that(result, contains_exactly(row))

    def test_find_all_by_multiple_numbers(self):
        row1 = self.add_blocklist_number(number=SAMPLE_NUMBER, user_uuid=USER_UUID)
        row2 = self.add_blocklist_number(number=SAMPLE_NUMBER_2, user_uuid=USER_UUID)

        result = dao.find_all_by(number_in=[SAMPLE_NUMBER, SAMPLE_NUMBER_2])

        assert_that(result, contains_exactly(row1, row2))

    def test_find_all_by_user_uuid(self):
        blocklist_row = self.add_blocklist(
            numbers=[
                BlocklistNumber(number=SAMPLE_NUMBER),
                BlocklistNumber(number=SAMPLE_NUMBER_2),
            ],
            user_uuid=USER_UUID,
        )

        result = dao.find_all_by(user_uuid=USER_UUID)

        assert_that(result, contains_exactly(*blocklist_row.numbers))

    def test_find_all_multitenant(self):
        tenant = self.add_tenant()
        user_3 = self.add_user(tenant_uuid=tenant.uuid)

        # default tenant
        alice = self.add_blocklist_number(
            number=SAMPLE_NUMBER,
            label='Alice',
            user_uuid=USER_UUID,
        )
        bob = self.add_blocklist_number(
            number=SAMPLE_NUMBER,
            label='Bob',
            user_uuid=USER_UUID_2,
        )

        charlie = self.add_blocklist_number(
            number=SAMPLE_NUMBER,
            label='Charlie',
            user_uuid=user_3.uuid,
        )

        result = dao.find_all_by(number=SAMPLE_NUMBER)

        assert_that(result, contains_exactly(alice, bob, charlie))

        result = dao.find_all_by(number=SAMPLE_NUMBER, tenant_uuids=[tenant.uuid])

        assert_that(result, contains_exactly(charlie))

        result = dao.find_all_by(number=SAMPLE_NUMBER, tenant_uuids=[DEFAULT_TENANT])

        assert_that(result, contains_exactly(alice, bob))


class TestSearch(BlocklistDAOTestCase):
    def assert_search_returns_result(self, search_result, **parameters):
        result = dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):
    def test_given_no_blocklist_number_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_blocklist_number_then_returns_one_result(self):
        row = self.add_blocklist_number(number=SAMPLE_NUMBER, user_uuid=USER_UUID)
        expected = SearchResult(1, [row])

        self.assert_search_returns_result(expected)


class TestSearchGivenMultipleBlocklistNumber(TestSearch):
    def setUp(self):
        super(TestSearch, self).setUp()

        self.blocklist = self.add_blocklist(
            numbers=[
                BlocklistNumber(number='+15551230000', label='one'),
                BlocklistNumber(number='+15551231111', label='two'),
                BlocklistNumber(number='+15551232222', label='three'),
                BlocklistNumber(number='+15551233333'),
            ],
            user_uuid=USER_UUID,
        )
        self.row_1, self.row_2, self.row_3, self.row_4 = self.blocklist.numbers

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.row_1])

        self.assert_search_returns_result(expected, search='one')

    def test_when_searching_with_an_extra_argument(self):
        expected = SearchResult(4, [self.row_1, self.row_2, self.row_3, self.row_4])
        self.assert_search_returns_result(
            expected,
            search='555',
        )

        expected = SearchResult(1, [self.row_3])
        self.assert_search_returns_result(expected, search='555', label='three')

        expected = SearchResult(1, [self.row_2])
        self.assert_search_returns_result(expected, search='555', label='two')

        expected = SearchResult(1, [self.row_1])
        self.assert_search_returns_result(expected, search='555', label='one')

    def test_sort(self):
        expected = SearchResult(4, [self.row_1, self.row_3, self.row_2, self.row_4])

        self.assert_search_returns_result(expected, order='label')

    def test_sort_order(self):
        expected = SearchResult(4, [self.row_4, self.row_2, self.row_3, self.row_1])

        self.assert_search_returns_result(expected, order='label', direction='desc')

    def test_limit(self):
        expected = SearchResult(4, [self.row_1])

        self.assert_search_returns_result(expected, limit=1)

    def test_offset(self):
        expected = SearchResult(4, [self.row_2, self.row_3, self.row_4])

        self.assert_search_returns_result(expected, offset=1)

    def test_pagination(self):
        expected = SearchResult(4, [self.row_1])

        self.assert_search_returns_result(
            expected,
            search='555',
            user_uuid=USER_UUID,
            limit=1,
        )

        expected = SearchResult(4, [self.row_2])
        self.assert_search_returns_result(
            expected,
            search='555',
            user_uuid=USER_UUID,
            limit=1,
            offset=1,
        )


class TestCreate(BlocklistDAOTestCase):
    def test_create_minimal_fields(self):
        created_blocklist = dao.create_blocklist(
            Blocklist(tenant_uuid=self.default_tenant.uuid)
        )
        blocklist_number = BlocklistNumber(
            number=SAMPLE_NUMBER,
            blocklist_uuid=created_blocklist.uuid,
        )

        created_blocklist_number = dao.create(blocklist_number)

        row = self.session.query(BlocklistNumber).first()

        assert_that(created_blocklist_number, equal_to(row))
        assert_that(
            created_blocklist_number,
            has_properties(
                uuid=row.uuid,
                number=SAMPLE_NUMBER,
                label=None,
                blocklist_uuid=created_blocklist.uuid,
            ),
        )

    def test_create_all_fields(self):
        name = 'Alice'
        blocklist_number = BlocklistNumber(
            number=SAMPLE_NUMBER,
            label=name,
            blocklist=Blocklist(
                user_uuid=self.user_1.uuid,
                tenant_uuid=self.user_1.tenant_uuid,
            ),
        )

        created_blocklist_number = dao.create(blocklist_number)

        row = self.session.query(BlocklistNumber).first()

        assert_that(created_blocklist_number, equal_to(row))
        assert_that(
            created_blocklist_number,
            has_properties(
                uuid=row.uuid,
                number=SAMPLE_NUMBER,
                label=name,
                user_uuid=USER_UUID,
            ),
        )


class TestEdit(BlocklistDAOTestCase):
    def test_edit_all_fields(self):
        created_blocklist_number = self.add_blocklist_number(
            number=SAMPLE_NUMBER,
            label='Alice',
            user_uuid=USER_UUID,
        )

        blocklist_number = dao.get(created_blocklist_number.uuid)
        new_number = blocklist_number.number = '+18001234567'
        new_label = blocklist_number.label = 'Bob'

        dao.edit(blocklist_number)

        row = self.session.query(BlocklistNumber).first()

        assert_that(blocklist_number, equal_to(row))
        assert_that(
            row,
            has_properties(
                uuid=created_blocklist_number.uuid,
                number=new_number,
                label=new_label,
                user_uuid=USER_UUID,
            ),
        )

    def test_edit_set_fields_to_null(self):
        created_blocklist_number = self.add_blocklist_number(
            number=SAMPLE_NUMBER,
            label='Alice',
            user_uuid=USER_UUID,
        )

        blocklist_number = dao.get(created_blocklist_number.uuid)
        blocklist_number.label = None

        dao.edit(blocklist_number)

        row = self.session.query(BlocklistNumber).first()

        assert_that(blocklist_number, equal_to(row))
        assert_that(
            row,
            has_properties(
                uuid=created_blocklist_number.uuid,
                number=SAMPLE_NUMBER,
                label=None,
                user_uuid=USER_UUID,
            ),
        )


class TestDelete(BlocklistDAOTestCase):
    def test_delete(self):
        blocklist_number = self.add_blocklist_number(
            number=SAMPLE_NUMBER, user_uuid=USER_UUID
        )

        dao.delete(blocklist_number)

        row = self.session.query(BlocklistNumber).first()
        assert_that(row, none())


class TestThatNumberIsUnique(BlocklistDAOTestCase):
    def setUp(self):
        super().setUp()
        self._blocklist_number = self.add_blocklist_number(
            number=SAMPLE_NUMBER, user_uuid=USER_UUID
        )

    def test_unique_number_in_blocklist_on_create(self):
        assert_that(
            calling(self.add_blocklist_number).with_args(
                number=SAMPLE_NUMBER,
                blocklist_uuid=self._blocklist_number.blocklist_uuid,
            ),
            raises(IntegrityError),
        )

    def test_unique_number_on_edit(self):
        created_blocklist_number = self.add_blocklist_number(
            number=SAMPLE_NUMBER_2, blocklist_uuid=self._blocklist_number.blocklist_uuid
        )

        blocklist_number = dao.get(created_blocklist_number.uuid)
        blocklist_number.number = SAMPLE_NUMBER

        assert_that(
            calling(dao.edit).with_args(blocklist_number),
            raises(IntegrityError),
        )
