# Copyright 2007-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


import uuid

from hamcrest import (
    assert_that,
    contains_exactly,
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

from xivo_dao.alchemy.callfiltermember import Callfiltermember
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.func_key import FuncKey
from xivo_dao.alchemy.func_key_dest_bsfilter import FuncKeyDestBSFilter
from xivo_dao.alchemy.func_key_dest_user import FuncKeyDestUser
from xivo_dao.alchemy.func_key_template import FuncKeyTemplate
from xivo_dao.alchemy.groupfeatures import GroupFeatures
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.rightcallmember import RightCallMember
from xivo_dao.alchemy.schedulepath import SchedulePath
from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.helpers.exception import InputError, NotFoundError
from xivo_dao.resources.func_key.tests.test_helpers import FuncKeyHelper
from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.user.model import UserDirectory, UserSummary
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DAOTestCase


class TestUser(DAOTestCase, FuncKeyHelper):
    def setUp(self):
        super().setUp()
        self.setup_funckeys()


class TestFindByIdUuid(TestUser):
    def test_given_no_user_when_finding_then_returns_none(self):
        assert_that(user_dao.find_by_id_uuid(1), none())

    def test_given_no_user_when_getting_then_returns_none(self):
        self.assertRaises(NotFoundError, user_dao.get_by_id_uuid, 1)

    def test_given_one_user_when_finding_by_its_id_then_returns_the_user(self):
        user_row = self.add_user()

        result = user_dao.find_by_id_uuid(user_row.id)

        assert_that(result.id, equal_to(user_row.id))

    def test_given_one_user_when_finding_by_its_string_id_then_returns_the_user(self):
        user_row = self.add_user()

        result = user_dao.find_by_id_uuid(str(user_row.id))

        assert_that(result.id, equal_to(user_row.id))

    def test_given_one_user_when_finding_by_its_string_uuid_then_returns_the_user(self):
        user_row = self.add_user()

        result = user_dao.find_by_id_uuid(user_row.uuid)

        assert_that(result.id, equal_to(user_row.id))
        assert_that(result.uuid, equal_to(user_row.uuid))

    def test_given_one_user_when_finding_by_its_uuid_then_returns_the_user(self):
        user_uuid = uuid.uuid4()
        user_row = self.add_user(uuid=str(user_uuid))

        result = user_dao.find_by_id_uuid(user_uuid)

        assert_that(result.id, equal_to(user_row.id))
        assert_that(result.uuid, equal_to(user_row.uuid))


class TestFind(TestUser):
    def test_find_no_user(self):
        result = user_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        user_row = self.add_user(
            firstname='Pâul',
            lastname='Rôgers',
            callerid='"Côol dude"',
            outcallerid='"Côol dude going out"',
            loginclient='paulrogers',
            passwdclient='paulrogers',
            musiconhold='mymusic',
            mobilephonenumber='4185551234',
            commented=1,
            rightcallcode='1234',
            userfield='userfield',
            timezone='America/Montreal',
            language='fr_FR',
            description='Really cool dude',
            preprocess_subroutine='preprocess_subroutine',
        )

        voicemail_row = self.add_voicemail(mailbox='1234')
        self.link_user_and_voicemail(user_row, voicemail_row.uniqueid)

        user = user_dao.find(user_row.id)

        assert_that(user.id, equal_to(user.id))
        assert_that(user.lastname, equal_to(user_row.lastname))
        assert_that(user.caller_id, equal_to(user_row.callerid))
        assert_that(user.outgoing_caller_id, equal_to(user_row.outcallerid))
        assert_that(user.username, equal_to(user_row.loginclient))
        assert_that(user.password, equal_to(user_row.passwdclient))
        assert_that(user.music_on_hold, equal_to(user_row.musiconhold))
        assert_that(user.mobile_phone_number, equal_to(user_row.mobilephonenumber))
        assert_that(user.enabled, not_(equal_to(bool(user_row.commented))))
        assert_that(user.call_permission_password, equal_to(user_row.rightcallcode))
        assert_that(user.userfield, equal_to(user_row.userfield))
        assert_that(user.timezone, equal_to(user_row.timezone))
        assert_that(user.language, equal_to(user_row.language))
        assert_that(user.description, equal_to(user_row.description))
        assert_that(
            user.preprocess_subroutine, equal_to(user_row.preprocess_subroutine)
        )
        assert_that(user.voicemail_id, equal_to(voicemail_row.uniqueid))
        assert_that(
            user.private_template_id, equal_to(user_row.func_key_private_template_id)
        )

    def test_that_email_address_is_case_insensitive_when_comparing(self):
        user_row = self.add_user(
            firstname='Pâul',
            lastname='Rôgers',
            callerid='"Côol dude"',
            outcallerid='"Côol dude going out"',
            loginclient='paulrogers',
            passwdclient='paulrogers',
            musiconhold='mymusic',
            mobilephonenumber='4185551234',
            commented=1,
            email='paul.rogers@example.com',
            rightcallcode='1234',
            userfield='userfield',
            timezone='America/Montreal',
            language='fr_FR',
            description='Really cool dude',
            preprocess_subroutine='preprocess_subroutine',
        )

        user = user_dao.find_by(email='Paul.Rogers@Example.COM')

        assert_that(user_row.id, equal_to(user.id))


class TestGet(TestUser):
    def test_get_no_user(self):
        self.assertRaises(NotFoundError, user_dao.get, 42)

    def test_get(self):
        user_row = self.add_user()

        user = user_dao.get(user_row.id)

        assert_that(user.id, equal_to(user.id))


class TestFindBy(TestUser):
    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, user_dao.find_by, invalid=42)

    def test_find_by_uuid(self):
        user_uuid = str(uuid.uuid4())
        user_row = self.add_user(uuid=user_uuid)

        user = user_dao.find_by(uuid=user_uuid)

        assert_that(user.id, equal_to(user_row.id))
        assert_that(user.uuid, equal_to(user_uuid))

    def test_find_by_template_id(self):
        user_row = self.add_user()

        user = user_dao.find_by(template_id=user_row.func_key_template_id)

        assert_that(user.id, equal_to(user_row.id))
        assert_that(user.func_key_template_id, equal_to(user_row.func_key_template_id))

    def test_find_by_private_template_id(self):
        user_row = self.add_user()

        user = user_dao.find_by(
            private_template_id=user_row.func_key_private_template_id
        )

        assert_that(user.id, equal_to(user_row.id))
        assert_that(
            user.func_key_private_template_id,
            equal_to(user_row.func_key_private_template_id),
        )

    def test_find_by_fullname(self):
        user_row = self.add_user(firstname='Jôhn', lastname='Smîth')

        user = user_dao.find_by(fullname='Jôhn Smîth')

        assert_that(user.id, equal_to(user_row.id))
        assert_that(user.firstname, equal_to('Jôhn'))
        assert_that(user.lastname, equal_to('Smîth'))

    def test_given_user_does_not_exist_then_returns_null(self):
        user = user_dao.find_by(firstname='42')

        assert_that(user, none())


class TestGetBy(TestUser):
    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, user_dao.get_by, invalid=42)

    def test_get_by_uuid(self):
        user_uuid = str(uuid.uuid4())
        user_row = self.add_user(uuid=user_uuid)

        user = user_dao.get_by(uuid=user_uuid)

        assert_that(user.id, equal_to(user_row.id))
        assert_that(user.uuid, equal_to(user_uuid))

    def test_get_by_template_id(self):
        user_row = self.add_user()

        user = user_dao.get_by(template_id=user_row.func_key_template_id)

        assert_that(user.id, equal_to(user_row.id))
        assert_that(user.func_key_template_id, equal_to(user_row.func_key_template_id))

    def test_get_by_private_template_id(self):
        user_row = self.add_user()

        user = user_dao.get_by(
            private_template_id=user_row.func_key_private_template_id
        )

        assert_that(user.id, equal_to(user_row.id))
        assert_that(
            user.func_key_private_template_id,
            equal_to(user_row.func_key_private_template_id),
        )

    def test_get_by_fullname(self):
        user_row = self.add_user(firstname='Jôhn', lastname='Smîth')

        user = user_dao.get_by(fullname='Jôhn Smîth')

        assert_that(user.id, equal_to(user_row.id))
        assert_that(user.firstname, equal_to('Jôhn'))
        assert_that(user.lastname, equal_to('Smîth'))

    def test_given_user_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, user_dao.get_by, firstname='42')

    def test_get_by_multi_tenant(self):
        tenant = self.add_tenant()

        user_row = self.add_user()
        self.assertRaises(
            NotFoundError,
            user_dao.get_by,
            id=user_row.id,
            tenant_uuids=[tenant.uuid],
        )

        user_row = self.add_user(tenant_uuid=tenant.uuid)
        user = user_dao.get_by(id=user_row.id, tenant_uuids=[tenant.uuid])
        assert_that(user, equal_to(user_row))


class TestFindAllBy(TestUser):
    def test_find_all_by_no_users(self):
        result = user_dao.find_all_by(firstname='toto')

        assert_that(result, contains_exactly())

    def test_find_all_by_renamed_column(self):
        template_row = self.add_func_key_template()
        user1 = self.add_user(func_key_template_id=template_row.id)
        user2 = self.add_user(func_key_template_id=template_row.id)

        users = user_dao.find_all_by(template_id=template_row.id)

        assert_that(
            users, has_items(has_property('id', user1.id), has_property('id', user2.id))
        )

    def test_find_all_by_native_column(self):
        user1 = self.add_user(firstname="Rîchard")
        user2 = self.add_user(firstname="Rîchard")

        users = user_dao.find_all_by(firstname='Rîchard')

        assert_that(
            users, has_items(has_property('id', user1.id), has_property('id', user2.id))
        )


class TestCountAllBy(TestUser):
    def test_count_all_by_no_users(self):
        result = user_dao.count_all_by('subscription_type')

        assert_that(result, contains_exactly())

    def test_count_all_by(self):
        self.add_user(subscription_type=1)
        self.add_user(subscription_type=1)
        self.add_user(subscription_type=6)
        self.add_user(subscription_type=8)

        result = user_dao.count_all_by('subscription_type')

        assert_that(
            result,
            contains_inanyorder(
                has_properties(subscription_type=1, count=2),
                has_properties(subscription_type=6, count=1),
                has_properties(subscription_type=8, count=1),
            ),
        )

    def test_count_all_by_filtered(self):
        tenant_uuid = self.add_tenant().uuid
        self.add_user(subscription_type=1, tenant_uuid=tenant_uuid)
        self.add_user(subscription_type=1)
        self.add_user(subscription_type=6, tenant_uuid=tenant_uuid)
        self.add_user(subscription_type=8)

        result = user_dao.count_all_by('subscription_type', tenant_uuid=tenant_uuid)

        assert_that(
            result,
            contains_inanyorder(
                has_properties(subscription_type=1, count=1),
                has_properties(subscription_type=6, count=1),
            ),
        )


class TestSearch(TestUser):
    def assert_search_returns_result(self, search_result, **parameters):
        parameters.setdefault('tenant_uuids', [self.default_tenant.uuid])
        result = user_dao.search(**parameters)
        assert_that(result, equal_to(search_result))

    def assert_search_collated_returns_result(self, search_result, **parameters):
        parameters.setdefault('tenant_uuids', [self.default_tenant.uuid])
        result = user_dao.search_collated(**parameters)
        assert_that(result, equal_to(search_result))

    def assert_search_returns_result_total(self, total, **parameters):
        parameters.setdefault('tenant_uuids', [self.default_tenant.uuid])
        result = user_dao.search(**parameters)
        assert_that(result.total, equal_to(total))

    def assert_search_collated_returns_result_total(self, total, **parameters):
        parameters.setdefault('tenant_uuids', [self.default_tenant.uuid])
        result = user_dao.search_collated(**parameters)
        assert_that(result.total, equal_to(total))

    def assert_search_raises_exception(self, exception, exception_msg, **parameters):
        with self.assertRaises(exception) as exc:
            parameters.setdefault('tenant_uuids', [self.default_tenant.uuid])
            user_dao.search(**parameters)
        assert str(exc.exception) == exception_msg

    def assert_search_collated_raises_exception(
        self, exception, exception_msg, **parameters
    ):
        with self.assertRaises(exception) as exc:
            parameters.setdefault('tenant_uuids', [self.default_tenant.uuid])
            user_dao.search_collated(**parameters)
        assert str(exc.exception) == exception_msg


class TestSimpleSearch(TestSearch):
    def test_given_no_users_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_commented_user_then_returns_one_result(self):
        user = self.add_user(firstname='bob')
        expected = SearchResult(1, [user])

        self.assert_search_returns_result(expected)

    def test_given_directory_view_then_returns_one_result(self):
        user = self.add_user(firstname='chârles')
        expected = SearchResult(
            1,
            [
                UserDirectory(
                    id=user.id,
                    uuid=user.uuid,
                    line_id=None,
                    agent_id=None,
                    firstname='chârles',
                    lastname=None,
                    email=None,
                    mobile_phone_number=None,
                    voicemail_number=None,
                    exten=None,
                    userfield=None,
                    description=None,
                    context=None,
                )
            ],
        )

        self.assert_search_returns_result(expected, view='directory')

    def test_given_user_without_line_when_using_summary_view_then_returns_summary_result(
        self,
    ):
        user = self.add_user(firstname='chârles')

        expected = SearchResult(
            1,
            [
                UserSummary(
                    id=user.id,
                    uuid=user.uuid,
                    firstname='chârles',
                    lastname=None,
                    email=None,
                    enabled=True,
                    extension=None,
                    context=None,
                    provisioning_code=None,
                    protocol=None,
                    subscription_type=0,
                )
            ],
        )

        self.assert_search_returns_result(expected, view='summary')

    def test_given_user_with_line_when_using_summary_view_then_returns_summary_result(
        self,
    ):
        sip = self.add_endpoint_sip()
        user_line = self.add_user_line_with_exten(
            firstname='dânny',
            lastname='rôgers',
            endpoint_sip_uuid=sip.uuid,
            email='dany.rogers@example.com',
            subscription_type=1,
        )

        expected = SearchResult(
            1,
            [
                UserSummary(
                    id=user_line.user_id,
                    uuid=user_line.user.uuid,
                    firstname='dânny',
                    lastname='rôgers',
                    email='dany.rogers@example.com',
                    enabled=True,
                    extension=user_line.extension.exten,
                    context=user_line.extension.context,
                    provisioning_code=user_line.line.provisioning_code,
                    protocol='sip',
                    subscription_type=1,
                )
            ],
        )

        self.assert_search_returns_result(expected, view='summary')

    def test_given_user_with_multi_lines_when_using_summary_view_then_returns_summary_one_result(
        self,
    ):
        custom = self.add_usercustom()
        user_line = self.add_user_line_with_exten(
            firstname='dânny', lastname='rôgers', endpoint_custom_id=custom.id
        )
        line = self.add_line()
        self.add_user_line(user_id=user_line.user.id, line_id=line.id, main_line=False)

        expected = SearchResult(
            1,
            [
                UserSummary(
                    id=user_line.user_id,
                    uuid=user_line.user.uuid,
                    firstname='dânny',
                    lastname='rôgers',
                    email=None,
                    enabled=True,
                    extension=user_line.extension.exten,
                    context=user_line.extension.context,
                    provisioning_code=None,
                    protocol='custom',
                    subscription_type=0,
                )
            ],
        )

        self.assert_search_returns_result(expected, view='summary')

    def test_given_user_with_line_and_agent_then_returns_one_directory_view_result(
        self,
    ):
        agent_row = self.add_agent()
        voicemail_row = self.add_voicemail(mailbox='2002')
        user_line_row = self.add_user_line_with_exten(
            firstname='dânny',
            lastname='rôgers',
            agentid=agent_row.id,
            mobilephonenumber='4185551234',
            voicemail_id=voicemail_row.uniqueid,
            userfield='userfield',
            description='desc',
        )

        expected = SearchResult(
            1,
            [
                UserDirectory(
                    id=user_line_row.user_id,
                    uuid=user_line_row.user.uuid,
                    line_id=user_line_row.line_id,
                    agent_id=agent_row.id,
                    firstname='dânny',
                    lastname='rôgers',
                    email=None,
                    mobile_phone_number='4185551234',
                    voicemail_number='2002',
                    exten=user_line_row.extension.exten,
                    userfield='userfield',
                    description='desc',
                    context=user_line_row.extension.context,
                )
            ],
        )

        self.assert_search_returns_result(expected, view='directory')


class TestSearchGivenMultipleUsers(TestSearch):
    def setUp(self):
        super(TestSearch, self).setUp()
        self.user1 = self.add_user(
            firstname='Ashton',
            lastname='ToujoursFrais',
            email='toujoursfrais@toujoursfrais.xyz',
            description='resto',
        )
        self.user2 = self.add_user(
            firstname='Áustin',
            lastname='French',
            email='french@french.xyz',
            description='resto',
        )
        self.user3 = self.add_user(
            firstname='Beaugarte',
            lastname='Cougar',
            email='cougar@cougar.xyz',
            description='bar',
        )
        self.user4 = self.add_user(
            firstname='Casa',
            lastname='Grecque',
            email='grecque@grecque.xyz',
            description='resto',
        )
        self.user5 = self.add_user(
            firstname='Dunkin',
            lastname='Donuts',
            email='donuts@donuts.xyz',
            description='resto',
        )
        self.user6 = self.add_user(
            firstname='Émilie',
            lastname='Pizza',
            email='pizza@pizza.xyz',
            description='resto',
        )
        self.user7 = self.add_user(
            firstname='Ômygod', lastname='Spanish', email=None, description='resto'
        )

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.user3])

        self.assert_search_returns_result(expected, search='eau')
        self.assert_search_collated_returns_result(expected, search='eau')

    def test_when_searching_with_an_extra_argument(self):
        expected_resto = SearchResult(1, [self.user1])
        self.assert_search_returns_result(
            expected_resto, search='ou', description='resto'
        )
        self.assert_search_collated_returns_result(
            expected_resto, search='ou', description='resto'
        )

        expected_bar = SearchResult(1, [self.user3])
        self.assert_search_returns_result(expected_bar, search='ou', description='bar')
        self.assert_search_collated_returns_result(
            expected_bar, search='ou', description='bar'
        )

        expected_all_resto = SearchResult(
            6, [self.user1, self.user4, self.user5, self.user2, self.user6, self.user7]
        )
        expected_collated_all_resto = SearchResult(
            6, [self.user1, self.user2, self.user4, self.user5, self.user6, self.user7]
        )
        self.assert_search_returns_result(
            expected_all_resto, description='resto', order='firstname'
        )
        self.assert_search_collated_returns_result(
            expected_collated_all_resto, description='resto', order='firstname'
        )

    def test_when_limiting_and_ordering(self):
        expected = SearchResult(7, [self.user1])

        self.assert_search_returns_result(expected, limit=1, order='firstname')
        self.assert_search_collated_returns_result(expected, limit=1, order='firstname')

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(
            7,
            [
                self.user1,
                self.user3,
                self.user4,
                self.user5,
                self.user2,
                self.user6,
                self.user7,
            ],
        )
        expected_collated = SearchResult(
            7,
            [
                self.user1,
                self.user2,
                self.user3,
                self.user4,
                self.user5,
                self.user6,
                self.user7,
            ],
        )

        self.assert_search_returns_result(expected, order='firstname')
        self.assert_search_collated_returns_result(expected_collated, order='firstname')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(
        self,
    ):
        expected = SearchResult(
            7,
            [
                self.user7,
                self.user6,
                self.user2,
                self.user5,
                self.user4,
                self.user3,
                self.user1,
            ],
        )
        expected_collated = SearchResult(
            7,
            [
                self.user7,
                self.user6,
                self.user5,
                self.user4,
                self.user3,
                self.user2,
                self.user1,
            ],
        )

        self.assert_search_returns_result(expected, order='firstname', direction='desc')
        self.assert_search_collated_returns_result(
            expected_collated, order='firstname', direction='desc'
        )

    def test_when_limiting_then_returns_right_number_of_items(self):
        self.assert_search_returns_result_total(7, limit=1)
        self.assert_search_collated_returns_result_total(7, limit=1)

    def test_when_offset_then_returns_right_number_of_items(self):
        self.assert_search_returns_result_total(7, offset=1)
        self.assert_search_collated_returns_result_total(7, offset=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(6, [self.user6])

        self.assert_search_returns_result(
            expected, search='a', order='firstname', direction='desc', offset=1, limit=1
        )
        self.assert_search_collated_returns_result(
            expected, search='a', order='firstname', direction='desc', offset=1, limit=1
        )

    def test_when_invalid_column(self):
        self.assert_search_raises_exception(
            InputError,
            "Input Error - order: column 'invalid' was not found",
            order='invalid',
        )
        self.assert_search_collated_raises_exception(
            InputError,
            "Input Error - order: column 'invalid' was not found",
            order='invalid',
        )

    def test_when_invalid_direction(self):
        self.assert_search_raises_exception(
            InputError,
            "Input Error - direction: must be 'asc' or 'desc'",
            direction='invalid',
        )
        self.assert_search_collated_raises_exception(
            InputError,
            "Input Error - direction: must be 'asc' or 'desc'",
            direction='invalid',
        )

    def test_when_ordering_when_none_field_then_returns_result_none_at_the_end(self):
        expected = SearchResult(
            7,
            [
                self.user3,
                self.user5,
                self.user2,
                self.user4,
                self.user6,
                self.user1,
                self.user7,
            ],
        )
        expected_collated = SearchResult(
            7,
            [
                self.user3,
                self.user5,
                self.user2,
                self.user4,
                self.user6,
                self.user1,
                self.user7,
            ],
        )

        self.assert_search_returns_result(expected, order='email')
        self.assert_search_collated_returns_result(expected_collated, order='email')


class TestSearchMutipleSameCriteria(TestSearch):
    def test_when_multiple_uuid_then_returns_right_number_of_items(self):
        self.add_user(firstname='a')
        user2 = self.add_user(firstname='b')
        user3 = self.add_user(firstname='c')
        expected = SearchResult(2, [user2, user3])

        multiple_uuid = ','.join([user2.uuid, user3.uuid])
        self.assert_search_returns_result(
            expected, uuid=multiple_uuid, order='firstname'
        )

    def test_when_uuid_is_none_then_returns_right_number_of_items(self):
        self.add_user()
        expected = SearchResult(0, [])
        self.assert_search_returns_result(expected, uuid=None)

    def test_when_multiple_exten_then_returns_right_number_of_items(self):
        self.add_user_line_with_exten(firstname='a', exten='1001')
        ule2 = self.add_user_line_with_exten(firstname='b', exten='1002')
        ule3 = self.add_user_line_with_exten(firstname='c', exten='1003')
        expected = SearchResult(2, [ule2.user, ule3.user])

        multiple_exten = ','.join([ule2.extension.exten, ule3.extension.exten])
        self.assert_search_returns_result(
            expected, exten=multiple_exten, order='firstname'
        )

    def test_when_exten_is_none_then_returns_right_number_of_items(self):
        self.add_user_line_with_exten()
        expected = SearchResult(0, [])
        self.assert_search_returns_result(expected, exten=None)


class TestCreate(TestUser):
    def test_create_minimal_fields(self):
        user = User(firstname='Jôhn', tenant_uuid=self.default_tenant.uuid)
        created_user = user_dao.create(user)

        row = self.session.query(User).first()

        assert_that(
            created_user,
            has_properties(
                id=row.id,
                uuid=row.uuid,
                firstname="Jôhn",
                lastname=none(),
                timezone=none(),
                language=none(),
                description=none(),
                outgoing_caller_id=none(),
                mobile_phone_number=none(),
                call_permission_password=none(),
                enabled=True,
                caller_id='"Jôhn"',
                music_on_hold=none(),
                username=none(),
                password=none(),
                preprocess_subroutine=none(),
                userfield=none(),
                voicemail_id=none(),
                call_transfer_enabled=False,
                dtmf_hangup_enabled=False,
                dnd_enabled=False,
                incallfilter_enabled=False,
                supervision_enabled=True,
                call_record_outgoing_external_enabled=False,
                call_record_outgoing_internal_enabled=False,
                call_record_incoming_external_enabled=False,
                call_record_incoming_internal_enabled=False,
                busy_enabled=False,
                busy_destination=None,
                noanswer_enabled=False,
                noanswer_destination=None,
                tenant_uuid=self.default_tenant.uuid,
                unconditional_enabled=False,
                unconditional_destination=None,
                simultaneous_calls=5,
                ring_seconds=30,
                subscription_type=0,
            ),
        )

        assert_that(
            row,
            has_properties(
                id=is_not(none()),
                uuid=is_not(none()),
                callerid='"Jôhn"',
                outcallerid='',
                mobilephonenumber='',
                rightcallcode=none(),
                commented=0,
                loginclient='',
                passwdclient='',
                musiconhold='',
                voicemailid=none(),
                enablehint=1,
                enablexfer=0,
                dtmf_hangup=0,
                incallfilter=0,
                enablednd=0,
                enableonlinerec=0,
                enablebusy=0,
                destbusy='',
                enablerna=0,
                destrna='',
                enableunc=0,
                destunc='',
                func_key_private_template_id=is_not(none()),
                tenant_uuid=self.default_tenant.uuid,
            ),
        )

    def test_create_with_all_fields(self):
        voicemail = self.add_voicemail()
        user = User(
            firstname='Jôhn',
            lastname='Smîth',
            timezone='America/Montreal',
            language='en_US',
            description='description',
            caller_id='"fîrstname lâstname" <1000>',
            outgoing_caller_id='ôutgoing_caller_id',
            mobile_phone_number='1234567890',
            call_permission_password='1234',
            enabled=False,
            username='username',
            password='password',
            music_on_hold='music_on_hold',
            preprocess_subroutine='preprocess_subroutine',
            voicemail_id=voicemail.id,
            userfield='userfield',
            call_transfer_enabled=True,
            dtmf_hangup_enabled=True,
            dnd_enabled=True,
            incallfilter_enabled=True,
            supervision_enabled=False,
            call_record_outgoing_external_enabled=True,
            call_record_outgoing_internal_enabled=True,
            call_record_incoming_external_enabled=True,
            call_record_incoming_internal_enabled=True,
            online_call_record_enabled=True,
            busy_enabled=True,
            busy_destination='123',
            noanswer_enabled=True,
            noanswer_destination='456',
            tenant_uuid=self.default_tenant.uuid,
            unconditional_enabled=True,
            unconditional_destination='789',
            ring_seconds=60,
            simultaneous_calls=10,
            subscription_type=0,
        )

        created_user = user_dao.create(user)

        row = self.session.query(User).first()

        assert_that(
            created_user,
            has_properties(
                id=row.id,
                uuid=row.uuid,
                firstname="Jôhn",
                lastname='Smîth',
                timezone='America/Montreal',
                language='en_US',
                description='description',
                caller_id='"fîrstname lâstname" <1000>',
                outgoing_caller_id='ôutgoing_caller_id',
                mobile_phone_number='1234567890',
                call_permission_password='1234',
                enabled=False,
                username='username',
                password='password',
                music_on_hold='music_on_hold',
                preprocess_subroutine='preprocess_subroutine',
                voicemail_id=voicemail.id,
                call_transfer_enabled=True,
                dtmf_hangup_enabled=True,
                dnd_enabled=True,
                incallfilter_enabled=True,
                supervision_enabled=False,
                call_record_outgoing_external_enabled=True,
                call_record_outgoing_internal_enabled=True,
                call_record_incoming_external_enabled=True,
                call_record_incoming_internal_enabled=True,
                online_call_record_enabled=True,
                busy_enabled=True,
                busy_destination='123',
                noanswer_enabled=True,
                noanswer_destination='456',
                tenant_uuid=self.default_tenant.uuid,
                unconditional_enabled=True,
                unconditional_destination='789',
                ring_seconds=60,
                simultaneous_calls=10,
                userfield='userfield',
                subscription_type=0,
                created_at=is_not(none()),
            ),
        )

        assert_that(
            row,
            has_properties(
                callerid='"fîrstname lâstname" <1000>',
                outcallerid='ôutgoing_caller_id',
                mobilephonenumber='1234567890',
                rightcallcode='1234',
                commented=1,
                loginclient='username',
                passwdclient='password',
                voicemailid=voicemail.id,
                enablehint=0,
                enablexfer=1,
                dtmf_hangup=1,
                incallfilter=1,
                enablednd=1,
                enableonlinerec=1,
                enablebusy=1,
                destbusy='123',
                enablerna=1,
                destrna='456',
                enableunc=1,
                destunc='789',
                musiconhold='music_on_hold',
                tenant_uuid=self.default_tenant.uuid,
            ),
        )

    def test_that_the_user_uuid_is_unique(self):
        shared_uuid = str(uuid.uuid4())
        self.add_user(firstname='Alice', uuid=shared_uuid)

        self.assertRaises(
            Exception, user_dao.create, User(firstname='Jôhn', uuid=shared_uuid)
        )


class TestEdit(TestUser):
    def test_edit_all_fields(self):
        old_voicemail = self.add_voicemail()
        new_voicemail = self.add_voicemail()
        user = self.add_user(
            firstname='Pâul',
            lastname='Rôgers',
            caller_id='"Côol dude"',
            outgoing_caller_id='"Côol dude going out"',
            username='paulrogers',
            password='paulrogers',
            music_on_hold='mymusic',
            mobile_phone_number='4185551234',
            call_permission_password='5678',
            enabled=True,
            userfield='userfield',
            timezone='America/Montreal',
            language='fr_FR',
            voicemail_id=old_voicemail.id,
            description='Really cool dude',
        )

        user = user_dao.get(user.id)
        user.firstname = 'firstname'
        user.lastname = 'lastname'
        user.timezone = 'America/Montreal'
        user.language = 'en_US'
        user.description = 'description'
        user.caller_id = '"John Sparrow"'
        user.outgoing_caller_id = 'outgoing_caller_id'
        user.mobile_phone_number = '1234567890'
        user.call_permission_password = '1234'
        user.enabled = False
        user.username = 'username'
        user.password = 'password'
        user.music_on_hold = 'music_on_hold'
        user.preprocess_subroutine = 'preprocess_subroutine'
        user.userfield = 'userfield'
        user.voicemail_id = new_voicemail.id
        user.call_transfer_enabled = True
        user.dtmf_hangup_enabled = True
        user.dnd_enabled = True
        user.incallfilter_enabled = True
        user.supervision_enabled = False
        user.call_record_outgoing_external_enabled = True
        user.call_record_outgoing_internal_enabled = True
        user.call_record_incoming_external_enabled = True
        user.call_record_incoming_internal_enabled = True
        user.online_call_record_enabled = True
        user.busy_enabled = True
        user.busy_destination = '123'
        user.noanswer_enabled = True
        user.noanswer_destination = '456'
        user.unconditional_enabled = True
        user.unconditional_destination = '789'
        user.ring_seconds = 60
        user.simultaneous_calls = 5
        user.subscription_type = 2

        user_dao.edit(user)

        row = self.session.query(User).first()

        assert_that(
            row,
            has_properties(
                firstname='firstname',
                lastname='lastname',
                timezone='America/Montreal',
                language='en_US',
                description='description',
                caller_id='"John Sparrow"',
                outgoing_caller_id='outgoing_caller_id',
                mobile_phone_number='1234567890',
                call_permission_password='1234',
                enabled=False,
                username='username',
                password='password',
                music_on_hold='music_on_hold',
                preprocess_subroutine='preprocess_subroutine',
                voicemail_id=new_voicemail.id,
                call_transfer_enabled=True,
                dtmf_hangup_enabled=True,
                dnd_enabled=True,
                incallfilter_enabled=True,
                supervision_enabled=False,
                call_record_outgoing_external_enabled=True,
                call_record_outgoing_internal_enabled=True,
                call_record_incoming_external_enabled=True,
                call_record_incoming_internal_enabled=True,
                online_call_record_enabled=True,
                busy_enabled=True,
                busy_destination='123',
                noanswer_enabled=True,
                noanswer_destination='456',
                unconditional_enabled=True,
                unconditional_destination='789',
                ring_seconds=60,
                simultaneous_calls=5,
                userfield='userfield',
                subscription_type=2,
            ),
        )

    def test_edit_set_fields_to_null(self):
        voicemail = self.add_voicemail()
        user = self.add_user(
            firstname='Pâul',
            lastname='Rôgers',
            caller_id='"Côol dude"',
            outgoing_caller_id='"Côol dude going out"',
            username='paulrogers',
            password='paulrogers',
            music_on_hold='mymusic',
            mobile_phone_number='4185551234',
            call_permission_password='5678',
            userfield='userfield',
            timezone='America/Montreal',
            language='fr_FR',
            voicemail_id=voicemail.id,
            description='Really cool dude',
        )

        user = user_dao.get(user.id)
        user.lastname = None
        user.outgoing_caller_id = None
        user.username = None
        user.password = None
        user.music_on_hold = None
        user.mobile_phone_number = None
        user.call_permission_password = None
        user.userfield = None
        user.timezone = None
        user.language = None
        user.description = None
        user.voicemail_id = None

        user_dao.edit(user)

        row = self.session.query(User).first()

        assert_that(
            row,
            has_properties(
                id=user.id,
                uuid=user.uuid,
                firstname="Pâul",
                lastname=none(),
                timezone=none(),
                language=none(),
                description=none(),
                outcallerid='',
                mobilephonenumber='',
                rightcallcode=none(),
                musiconhold='',
                loginclient='',
                passwdclient='',
                preprocess_subroutine=none(),
                voicemailid=none(),
                userfield=none(),
            ),
        )

    def test_edit_caller_id_with_number(self):
        caller_id = '<1000>'
        user = self.add_user()

        user = user_dao.get(user.id)
        user.caller_id = caller_id

        user_dao.edit(user)

        row = self.session.query(User).first()

        assert_that(row.id, equal_to(user.id))
        assert_that(row.callerid, equal_to(caller_id))


class TestDelete(TestUser):
    def test_delete(self):
        user = self.add_user()

        user_dao.delete(user)

        row = self.session.query(User).first()
        assert_that(row, none())

    def test_delete_references_to_other_tables(self):
        user = self.add_user()

        self.add_user_destination(user.id)
        self.add_user_call_permission(user_id=user.id)
        schedule = self.add_schedule()
        self.add_schedule_path(schedule_id=schedule.id, path='user', pathid=user.id)
        call_filter = self.add_call_filter()
        member = self.add_call_filter_member(
            callfilterid=call_filter.id,
            typeval=str(user.id),
            bstype='secretary',
        )
        self.add_bsfilter_destination(member.id)

        user_dao.delete(user)

        assert_that(self.session.query(RightCallMember).first(), none())
        assert_that(self.session.query(SchedulePath).first(), none())
        assert_that(self.session.query(Callfiltermember).first(), none())
        assert_that(self.session.query(FuncKeyDestUser).first(), none())
        assert_that(self.session.query(FuncKeyDestBSFilter).first(), none())
        assert_that(self.session.query(FuncKey).first(), none())
        assert_that(self.session.query(FuncKeyTemplate).first(), none())


class TestAssociateGroups(DAOTestCase):
    def test_associate_user_sip(self):
        user_row = self.add_user()
        sip = self.add_endpoint_sip(name='sipname')
        line = self.add_line(endpoint_sip_uuid=sip.uuid)
        self.add_user_line(user_id=user_row.id, line_id=line.id)
        group = self.add_group()

        user_dao.associate_all_groups(user_row, [group])

        user = self.session.query(User).first()
        assert_that(user, equal_to(user_row))
        assert_that(
            user.group_members,
            contains_exactly(
                has_properties(
                    queue_name=group.name,
                    interface='PJSIP/sipname',
                    channel='SIP',
                    group=has_properties(id=group.id, name=group.name),
                )
            ),
        )

    def test_associate_multiple_users(self):
        user_row = self.add_user()
        sip = self.add_endpoint_sip()
        line = self.add_line(endpoint_sip_uuid=sip.uuid)
        self.add_user_line(user_id=user_row.id, line_id=line.id)

        group1 = self.add_group()
        group2 = self.add_group()
        group3 = self.add_group()

        user_dao.associate_all_groups(user_row, [group1, group2, group3])

        user = self.session.query(User).first()
        assert_that(user, equal_to(user_row))
        assert_that(user.groups, contains_inanyorder(group1, group2, group3))

    def test_associate_sip_fix(self):
        user_row = self.add_user()
        sip = self.add_endpoint_sip(name='sipname')
        line = self.add_line(endpoint_sip_uuid=sip.uuid)
        self.add_user_line(user_id=user_row.id, line_id=line.id)
        group = self.add_group()

        user_dao.associate_all_groups(user_row, [group])

        user = self.session.query(User).first()
        assert_that(
            user.group_members,
            contains_exactly(
                has_properties(
                    queue_name=group.name, interface='PJSIP/sipname', channel='SIP'
                )
            ),
        )

    def test_associate_sccp_fix(self):
        user_row = self.add_user()
        sccp = self.add_sccpline(name='sccpname')
        line = self.add_line(endpoint_sccp_id=sccp.id)
        self.add_user_line(user_id=user_row.id, line_id=line.id)
        group = self.add_group()

        user_dao.associate_all_groups(user_row, [group])

        user = self.session.query(User).first()
        assert_that(
            user.group_members,
            contains_exactly(
                has_properties(
                    queue_name=group.name, interface='SCCP/sccpname', channel='SCCP'
                )
            ),
        )

    def test_associate_custom_fix(self):
        user_row = self.add_user()
        custom = self.add_usercustom(interface='custom/interface')
        line = self.add_line(endpoint_custom_id=custom.id)
        self.add_user_line(user_id=user_row.id, line_id=line.id)
        group = self.add_group()

        user_dao.associate_all_groups(user_row, [group])

        user = self.session.query(User).first()
        assert_that(
            user.group_members,
            contains_exactly(
                has_properties(
                    queue_name=group.name,
                    interface='custom/interface',
                    channel='**Unknown**',
                )
            ),
        )

    def test_users_dissociation(self):
        user_row = self.add_user()
        sip = self.add_endpoint_sip(name='sipname')
        line = self.add_line(endpoint_sip_uuid=sip.uuid)
        self.add_user_line(user_id=user_row.id, line_id=line.id)
        group = self.add_group()
        user_dao.associate_all_groups(user_row, [group])

        user = self.session.query(User).first()
        assert_that(user.groups, contains_exactly(group))

        user_dao.associate_all_groups(user_row, [])

        user = self.session.query(User).first()
        assert_that(user, equal_to(user_row))
        assert_that(user.groups, empty())

        row = self.session.query(GroupFeatures).first()
        assert_that(row, not_(none()))

        row = self.session.query(QueueMember).first()
        assert_that(row, none())


class TestListOutgoingCallerIDAssociated(DAOTestCase):
    def test_given_no_incall_associated_to_a_user_then_returns_empty_list(self):
        user = self.add_user()

        result = user_dao.list_outgoing_callerid_associated(user.id)

        assert_that(result, empty())

    def test_given_one_incall_associated_to_a_user_then_returns_extens(self):
        user = self.add_user()
        destination = {'action': 'user', 'actionarg1': str(user.id)}
        incall = self.add_incall(destination=Dialaction(**destination))
        exten = self.add_extension(type='incall', typeval=str(incall.id))

        result = user_dao.list_outgoing_callerid_associated(user.id)

        caller_id = has_properties(type='associated', number=exten.exten)
        assert_that(result, contains_exactly(caller_id))

    def test_given_many_incalls_associated_to_a_user_then_returns_extens(self):
        user = self.add_user()
        destination = {'action': 'user', 'actionarg1': str(user.id)}
        incall1 = self.add_incall(destination=Dialaction(**destination))
        exten1 = self.add_extension(type='incall', typeval=str(incall1.id))
        incall2 = self.add_incall(destination=Dialaction(**destination))
        exten2 = self.add_extension(type='incall', typeval=str(incall2.id))

        result = user_dao.list_outgoing_callerid_associated(user.id)

        caller_id1 = has_properties(type='associated', number=exten1.exten)
        caller_id2 = has_properties(type='associated', number=exten2.exten)
        assert_that(result, contains_inanyorder(caller_id1, caller_id2))
