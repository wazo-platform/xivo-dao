# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    all_of,
    assert_that,
    contains,
    contains_inanyorder,
    empty,
    equal_to,
    has_items,
    has_properties,
    has_property,
    is_not,
    none,
    not_,
)

from sqlalchemy.inspection import inspect

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.ivr import IVR
from xivo_dao.alchemy.ivr_choice import IVRChoice
from xivo_dao.helpers.exception import InputError, NotFoundError
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao as ivr_dao


class TestFind(DAOTestCase):

    def test_find_no_ivr(self):
        result = ivr_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        ivr_row = self.add_ivr()

        ivr = ivr_dao.find(ivr_row.id)

        assert_that(ivr, equal_to(ivr_row))

    def test_find_multi_tenant(self):
        tenant = self.add_tenant()
        ivr = self.add_ivr(tenant_uuid=tenant.uuid)

        result = ivr_dao.find(ivr.id, tenant_uuids=[tenant.uuid])
        assert_that(result, equal_to(ivr))

        result = ivr_dao.find(ivr.id, tenant_uuids=[self.default_tenant.uuid])
        assert_that(result, none())


class TestGet(DAOTestCase):

    def test_get_no_ivr(self):
        self.assertRaises(NotFoundError, ivr_dao.get, 42)

    def test_get(self):
        ivr_row = self.add_ivr()

        ivr = ivr_dao.get(ivr_row.id)

        assert_that(ivr, equal_to(ivr_row))
        assert_that(ivr.choices, contains())

    def test_get_multi_tenant(self):
        tenant = self.add_tenant()

        ivr_row = self.add_ivr(tenant_uuid=tenant.uuid)
        ivr = ivr_dao.get(ivr_row.id, tenant_uuids=[tenant.uuid])
        assert_that(ivr, equal_to(ivr_row))

        ivr_row = self.add_ivr()
        self.assertRaises(
            NotFoundError,
            ivr_dao.get, ivr_row.id, tenant_uuids=[tenant.uuid],
        )


class TestFindBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, ivr_dao.find_by, invalid=42)

    def test_find_by_name(self):
        ivr_row = self.add_ivr(name='myname')

        ivr = ivr_dao.find_by(name='myname')

        assert_that(ivr, equal_to(ivr_row))
        assert_that(ivr.name, equal_to('myname'))

    def test_find_by_description(self):
        ivr_row = self.add_ivr(description='mydescription')

        ivr = ivr_dao.find_by(description='mydescription')

        assert_that(ivr, equal_to(ivr_row))
        assert_that(ivr.description, equal_to('mydescription'))

    def test_given_ivr_does_not_exist_then_returns_null(self):
        ivr = ivr_dao.find_by(id=42)

        assert_that(ivr, none())

    def test_find_by_multi_tenant(self):
        tenant = self.add_tenant()

        ivr_row = self.add_ivr()
        ivr = ivr_dao.find_by(id=ivr_row.id, tenant_uuids=[tenant.uuid])
        assert_that(ivr, none())

        ivr_row = self.add_ivr(tenant_uuid=tenant.uuid)
        ivr = ivr_dao.find_by(id=ivr_row.id, tenant_uuids=[tenant.uuid])
        assert_that(ivr, equal_to(ivr_row))


class TestGetBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, ivr_dao.get_by, invalid=42)

    def test_get_by_name(self):
        ivr_row = self.add_ivr(name='myname')

        ivr = ivr_dao.get_by(name='myname')

        assert_that(ivr, equal_to(ivr_row))
        assert_that(ivr.name, equal_to('myname'))

    def test_get_by_description(self):
        ivr_row = self.add_ivr(description='mydescription')

        ivr = ivr_dao.get_by(description='mydescription')

        assert_that(ivr, equal_to(ivr_row))
        assert_that(ivr.description, equal_to('mydescription'))

    def test_given_ivr_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, ivr_dao.get_by, id='42')

    def test_get_by_multi_tenant(self):
        tenant = self.add_tenant()

        ivr_row = self.add_ivr()
        self.assertRaises(
            NotFoundError,
            ivr_dao.get_by, id=ivr_row.id, tenant_uuids=[tenant.uuid],
        )

        ivr_row = self.add_ivr(tenant_uuid=tenant.uuid)
        ivr = ivr_dao.get_by(id=ivr_row.id, tenant_uuids=[tenant.uuid])
        assert_that(ivr, equal_to(ivr_row))


class TestFindAllBy(DAOTestCase):

    def test_find_all_by_no_ivr(self):
        result = ivr_dao.find_all_by(description='toto')

        assert_that(result, contains())

    def test_find_all_by_native_column(self):
        ivr1 = self.add_ivr(description='MyIVR')
        ivr2 = self.add_ivr(description='MyIVR')

        ivrs = ivr_dao.find_all_by(description='MyIVR')

        assert_that(ivrs, has_items(
            has_property('id', ivr1.id),
            has_property('id', ivr2.id),
        ))

    def test_find_all_multi_tenant(self):
        tenant = self.add_tenant()

        ivr1 = self.add_ivr(description='description', tenant_uuid=tenant.uuid)
        ivr2 = self.add_ivr(description='description')

        tenants = [tenant.uuid, self.default_tenant.uuid]
        ivrs = ivr_dao.find_all_by(description='description', tenant_uuids=tenants)
        assert_that(ivrs, has_items(ivr1, ivr2))

        tenants = [tenant.uuid]
        ivrs = ivr_dao.find_all_by(description='description', tenant_uuids=tenants)
        assert_that(ivrs, all_of(has_items(ivr1), not_(has_items(ivr2))))


class TestSearch(DAOTestCase):

    def assert_search_returns_result(self, search_result, **parameters):
        result = ivr_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):

    def test_given_no_ivr_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_ivr_then_returns_one_result(self):
        ivr = self.add_ivr()
        expected = SearchResult(1, [ivr])

        self.assert_search_returns_result(expected)

    def test_search_multi_tenant(self):
        tenant = self.add_tenant()

        ivr1 = self.add_ivr()
        ivr2 = self.add_ivr(tenant_uuid=tenant.uuid)

        expected = SearchResult(2, [ivr1, ivr2])
        tenants = [tenant.uuid, self.default_tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)

        expected = SearchResult(1, [ivr2])
        tenants = [tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)

    def test_search_by_exten(self):
        ivr = self.add_ivr()
        incall = self.add_incall()
        self.add_extension(exten="2000", type="incall", typeval=str(incall.id))
        self.add_dialaction(
            action="ivr",
            actionarg1=str(ivr.id),
            category="incall",
            categoryval=str(incall.id)
        )

        expected = SearchResult(1, [ivr])
        self.assert_search_returns_result(expected, search="2000")
        self.assert_search_returns_result(expected, exten="2000")

    def test_search_by_exten_with_multiple_incalls(self):
        ivr = self.add_ivr()
        incall1 = self.add_incall()
        self.add_extension(exten="1001", type="incall", typeval=str(incall1.id))
        self.add_dialaction(
            action="ivr",
            actionarg1=str(ivr.id),
            category="incall",
            categoryval=str(incall1.id)
        )
        incall2 = self.add_incall()
        self.add_extension(exten="1002", type="incall", typeval=str(incall2.id))
        self.add_dialaction(
            action="ivr",
            actionarg1=str(ivr.id),
            category="incall",
            categoryval=str(incall2.id)
        )

        expected = SearchResult(1, [ivr])
        self.assert_search_returns_result(expected, search="100")


class TestSearchGivenMultipleIncall(TestSearch):

    def setUp(self):
        super(TestSearch, self).setUp()
        self.ivr1 = self.add_ivr(name='Ashton', description='resto')
        self.ivr2 = self.add_ivr(name='Beaugarton', description='bar')
        self.ivr3 = self.add_ivr(name='Casa', description='resto')
        self.ivr4 = self.add_ivr(name='Dunkin', description='resto')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.ivr2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_searching_with_an_extra_argument(self):
        expected_resto = SearchResult(1, [self.ivr1])
        self.assert_search_returns_result(expected_resto, search='ton', description='resto')

        expected_bar = SearchResult(1, [self.ivr2])
        self.assert_search_returns_result(expected_bar, search='ton', description='bar')

        expected_all_resto = SearchResult(3, [self.ivr1, self.ivr3, self.ivr4])
        self.assert_search_returns_result(expected_all_resto, description='resto', order='name')

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(4, [
            self.ivr1,
            self.ivr2,
            self.ivr3,
            self.ivr4,
        ])

        self.assert_search_returns_result(expected, order='name')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(self):
        expected = SearchResult(4, [
            self.ivr4,
            self.ivr3,
            self.ivr2,
            self.ivr1,
        ])

        self.assert_search_returns_result(expected, order='name', direction='desc')

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.ivr1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_offset_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.ivr2, self.ivr3, self.ivr4])

        self.assert_search_returns_result(expected, offset=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.ivr3])

        self.assert_search_returns_result(
            expected,
            search='resto',
            order='name',
            direction='desc',
            offset=1,
            limit=1,
        )

    def test_when_searching_multiple_by_exten(self):
        incall1 = self.add_incall()
        incall2 = self.add_incall()
        self.add_extension(exten="1001", type="incall", typeval=str(incall1.id))
        self.add_extension(exten="1002", type="incall", typeval=str(incall2.id))
        self.add_dialaction(action="ivr", actionarg1=str(self.ivr1.id), category="incall", categoryval=str(incall1.id))
        self.add_dialaction(action="ivr", actionarg1=str(self.ivr2.id), category="incall", categoryval=str(incall2.id))

        expected = SearchResult(1, [self.ivr2])
        self.assert_search_returns_result(expected, search="1002")


class TestCreate(DAOTestCase):

    def test_create_minimal_fields(self):
        ivr_model = IVR(name='myivr', menu_sound='menu', tenant_uuid=self.default_tenant.uuid)

        ivr = ivr_dao.create(ivr_model)

        self.session.expire_all()
        assert_that(inspect(ivr).persistent)
        assert_that(ivr, has_properties(
            id=is_not(none()),
            tenant_uuid=self.default_tenant.uuid,
            name='myivr',
            greeting_sound=none(),
            menu_sound='menu',
            invalid_sound=none(),
            abort_sound=none(),
            description=none(),
            invalid_destination=none(),
            timeout_destination=none(),
            abort_destination=none(),
        ))

    def test_create_with_all_fields(self):
        ivr_model = IVR(
            name='myivr',
            tenant_uuid=self.default_tenant.uuid,
            greeting_sound='greeting',
            menu_sound='menu',
            invalid_sound='invalid',
            abort_sound='abort',
            timeout=10,
            max_tries=2,
            description='description',
            invalid_destination=Dialaction(action='user', actionarg1='1'),
            timeout_destination=Dialaction(action='user', actionarg1='2'),
            abort_destination=Dialaction(action='user', actionarg1='3'),
            choices=[IVRChoice(exten='1', destination=Dialaction(action='user', actionarg1='4'))],
        )

        ivr = ivr_dao.create(ivr_model)

        self.session.expire_all()
        assert_that(inspect(ivr).persistent)
        assert_that(ivr, has_properties(
            id=is_not(none()),
            tenant_uuid=self.default_tenant.uuid,
            name='myivr',
            greeting_sound='greeting',
            menu_sound='menu',
            invalid_sound='invalid',
            abort_sound='abort',
            timeout=10,
            max_tries=2,
            description='description',
            invalid_destination=has_properties(action='user', actionarg1='1'),
            timeout_destination=has_properties(action='user', actionarg1='2'),
            abort_destination=has_properties(action='user', actionarg1='3'),
        ))
        assert_that(ivr.choices, contains(
            has_properties(exten='1', destination=has_properties(action='user', actionarg1='4')),
        ))


class TestEdit(DAOTestCase):

    def test_edit_all_fields(self):
        ivr = self.add_ivr(
            name='myivr',
            greeting_sound='greeting',
            menu_sound='menu',
            invalid_sound='invalid',
            abort_sound='abort',
            timeout=10,
            max_tries=2,
            description='description',
            invalid_destination=Dialaction(action='user', actionarg1='1'),
            timeout_destination=Dialaction(action='user', actionarg1='2'),
            choices=[
                IVRChoice(exten='1', destination=Dialaction(action='user', actionarg1='4'))
            ],
        )

        self.session.expire_all()
        ivr.name = 'zmyivr'
        ivr.greeting_sound = 'zgreeting'
        ivr.menu_sound = 'zmenu'
        ivr.invalid_sound = 'zinvalid'
        ivr.abort_sound = 'zabort'
        ivr.timeout = 42
        ivr.max_tries = 1337
        ivr.description = 'lol'
        ivr.invalid_destination = Dialaction(action='user', actionarg1='3')
        ivr.timeout_destination = Dialaction(action='user', actionarg1='4')
        ivr.choices = [IVRChoice(exten='2', destination=Dialaction(action='none'))]

        ivr_dao.edit(ivr)

        self.session.expire_all()
        assert_that(ivr, has_properties(
            name='zmyivr',
            greeting_sound='zgreeting',
            menu_sound='zmenu',
            invalid_sound='zinvalid',
            abort_sound='zabort',
            timeout=42,
            max_tries=1337,
            description='lol',
            invalid_destination=has_properties(action='user', actionarg1='3'),
            timeout_destination=has_properties(action='user', actionarg1='4'),
        ))
        assert_that(ivr.choices, contains(
            has_properties(exten='2', destination=has_properties(action='none')),
        ))

    def test_edit_set_fields_to_null(self):
        ivr = self.add_ivr(
            name='myivr',
            greeting_sound='greeting',
            menu_sound='menu',
            invalid_sound='invalid',
            abort_sound='abort',
            timeout=10,
            max_tries=2,
            description='description',
            invalid_destination=Dialaction(action='user', actionarg1='1'),
            timeout_destination=Dialaction(action='user', actionarg1='2'),
            choices=[
                IVRChoice(exten='1', destination=Dialaction(action='user', actionarg1='3'))
            ],
        )

        self.session.expire_all()
        ivr.greeting_sound = None
        ivr.invalid_sound = None
        ivr.abort_sound = None
        ivr.description = None
        ivr.invalid_destination = None
        ivr.timeout_destination = None
        ivr.choices = []

        ivr_dao.edit(ivr)

        self.session.expire_all()
        assert_that(ivr, has_properties(
            id=is_not(none()),
            name='myivr',
            greeting_sound=none(),
            menu_sound='menu',
            invalid_sound=none(),
            abort_sound=none(),
            description=none(),
            invalid_destination=none(),
            timeout_destination=none(),
        ))
        assert_that(ivr.choices, empty())

    def test_when_removing_choices_then_choices_are_deleted(self):
        ivr = self.add_ivr(
            name='myivr',
            menu_sound='menu',
            choices=[IVRChoice(exten='1', destination=Dialaction(action='none'))],
        )

        self.session.expire_all()
        ivr.choices = []

        ivr_dao.edit(ivr)

        assert_that(self.session.query(IVRChoice).all(), empty())
        assert_that(self.session.query(Dialaction).all(), empty())


class TestDelete(DAOTestCase):

    def test_delete(self):
        ivr = self.add_ivr()

        ivr_dao.delete(ivr)

        assert_that(inspect(ivr).deleted)


class TestRelationship(DAOTestCase):

    def test_dialactions_relationship(self):
        ivr = self.add_ivr()
        dialaction = self.add_dialaction(
            event='timeout',
            category='ivr',
            categoryval=str(ivr.id),
        )

        self.session.expire_all()
        assert_that(ivr.dialactions['timeout'], equal_to(dialaction))

    def test_choices_relationship(self):
        ivr = self.add_ivr()
        ivr_choice = self.add_ivr_choice(ivr_id=ivr.id)
        dialaction = self.add_dialaction(
            category='ivr_choice',
            categoryval=str(ivr_choice.id),
        )

        self.session.expire_all()
        assert_that(ivr.choices, contains(ivr_choice))
        assert_that(ivr.choices[0].destination, equal_to(dialaction))

    def test_incalls_relationship(self):
        ivr = self.add_ivr()
        incall1 = self.add_incall(destination=Dialaction(action='ivr', actionarg1=str(ivr.id)))
        incall2 = self.add_incall(destination=Dialaction(action='ivr', actionarg1=str(ivr.id)))

        self.session.expire_all()
        assert_that(ivr.incalls, contains_inanyorder(incall1, incall2))
