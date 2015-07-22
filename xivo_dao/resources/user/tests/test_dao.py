# -*- coding: utf-8 -*-

# Copyright (C) 2007-2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from hamcrest import all_of
from hamcrest import any_of
from hamcrest import assert_that
from hamcrest import contains
from hamcrest import equal_to
from hamcrest import has_items
from hamcrest import has_length
from hamcrest import has_property
from hamcrest import is_
from hamcrest import none
from sqlalchemy.exc import SQLAlchemyError

from xivo_dao.alchemy.userfeatures import UserFeatures as UserSchema
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.helpers.exception import DataError
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.user.model import User, UserDirectory
from xivo_dao.tests.helpers.session import mocked_dao_session
from xivo_dao.tests.test_dao import DAOTestCase


class TestGet(DAOTestCase):

    def test_get_main_user_by_line_id_not_found(self):
        line_id = 654

        self.assertRaises(NotFoundError, user_dao.get_main_user_by_line_id, line_id)

    def test_get_main_user_by_line_id(self):
        user_line = self.add_user_line_with_exten()
        line_id = user_line.line.id

        result = user_dao.get_main_user_by_line_id(line_id)

        assert_that(result, has_property('id', user_line.user.id))

    def test_get_inexistant(self):
        self.assertRaises(NotFoundError, user_dao.get, 42)

    def test_get_required_fields(self):
        user_row = self.add_user(firstname='Paul')

        user = user_dao.get(user_row.id)

        assert_that(user.id, equal_to(user_row.id))
        assert_that(user.firstname, equal_to(user_row.firstname))
        assert_that(user.private_template_id, equal_to(user_row.func_key_private_template_id))

    def test_get_commented(self):
        user_row = self.add_user(firstname='Paul', commented=1)

        user = user_dao.get(user_row.id)

        assert_that(user.id, equal_to(user_row.id))

    def test_get_all_fields(self):
        user_row = self.add_user(firstname='Paul',
                                 lastname='Rogers',
                                 callerid='"Cool dude"',
                                 outcallerid='"Cool dude going out"',
                                 loginclient='paulrogers',
                                 passwdclient='paulrogers',
                                 musiconhold='mymusic',
                                 mobilephonenumber='4185551234',
                                 userfield='userfield',
                                 timezone='America/Montreal',
                                 language='fr_FR',
                                 description='Really cool dude',
                                 preprocess_subroutine='preprocess_subroutine')
        voicemail_row = self.add_voicemail(mailbox='1234', context='default')
        self.link_user_and_voicemail(user_row, voicemail_row.uniqueid)

        user = user_dao.get(user_row.id)

        assert_that(user.id, equal_to(user.id))
        assert_that(user.lastname, equal_to(user_row.lastname))
        assert_that(user.caller_id, equal_to(user_row.callerid))
        assert_that(user.outgoing_caller_id, equal_to(user_row.outcallerid))
        assert_that(user.username, equal_to(user_row.loginclient))
        assert_that(user.password, equal_to(user_row.passwdclient))
        assert_that(user.music_on_hold, equal_to(user_row.musiconhold))
        assert_that(user.mobile_phone_number, equal_to(user_row.mobilephonenumber))
        assert_that(user.userfield, equal_to(user_row.userfield))
        assert_that(user.timezone, equal_to(user_row.timezone))
        assert_that(user.language, equal_to(user_row.language))
        assert_that(user.description, equal_to(user_row.description))
        assert_that(user.preprocess_subroutine, equal_to(user_row.preprocess_subroutine))
        assert_that(user.voicemail_id, equal_to(voicemail_row.uniqueid))
        assert_that(user.private_template_id, equal_to(user_row.func_key_private_template_id))

    def test_get_by_number_context(self):
        context, number = 'default', '1234'
        user_line = self.add_user_line_with_exten(exten=number,
                                                  context=context)

        user = user_dao.get_by_number_context(number, context)

        assert_that(user.id, equal_to(user_line.user_id))

    def test_get_by_number_context_line_commented(self):
        context, number = 'default', '1234'
        self.add_user_line_with_exten(number=number,
                                      context=context,
                                      commented_line=1)

        self.assertRaises(NotFoundError, user_dao.get_by_number_context, number, context)


class TestFind(DAOTestCase):

    def test_find_all_no_users(self):
        expected = []
        users = user_dao.find_all()

        assert_that(users, equal_to(expected))

    def test_find_all_one_user(self):
        firstname = 'Pascal'
        user = self.add_user(firstname=firstname)

        users = user_dao.find_all()
        assert_that(users, has_length(1))

        user_found = users[0]
        assert_that(user_found, has_property('id', user.id))
        assert_that(user_found, has_property('firstname', firstname))

    def test_find_all_one_user_commented(self):
        firstname = 'Pascal'
        user = self.add_user(firstname=firstname, commented=1)

        users = user_dao.find_all()
        assert_that(users, has_length(1))

        user_found = users[0]
        assert_that(user_found, has_property('id', user.id))
        assert_that(user_found, has_property('firstname', firstname))

    def test_find_all_two_users(self):
        firstname1 = 'Pascal'
        firstname2 = 'George'

        user1 = self.add_user(firstname=firstname1)
        user2 = self.add_user(firstname=firstname2)

        users = user_dao.find_all()
        assert_that(users, has_length(2))

        assert_that(users, has_items(
            all_of(
                has_property('id', user1.id),
                has_property('firstname', firstname1)),
            all_of(
                has_property('id', user2.id),
                has_property('firstname', firstname2))
        ))

    def test_find_all_default_order_by_lastname_firstname(self):
        user1 = self.add_user(firstname='Jules', lastname='Santerre')
        user2 = self.add_user(firstname='Vicky', lastname='Bourbon')
        user3 = self.add_user(firstname='Anne', lastname='Bourbon')

        users = user_dao.find_all()
        assert_that(users, has_length(3))

        assert_that(users[0].id, equal_to(user3.id))
        assert_that(users[1].id, equal_to(user2.id))
        assert_that(users[2].id, equal_to(user1.id))

    def test_find_all_order_by_firstname(self):
        user_last = self.add_user(firstname='Bob', lastname='Alzard')
        user_first = self.add_user(firstname='Albert', lastname='Breton')

        users = user_dao.find_all(order=['firstname'])

        assert_that(users[0].id, equal_to(user_first.id))
        assert_that(users[1].id, equal_to(user_last.id))

    def test_find_all_order_by_lastname(self):
        user_last = self.add_user(firstname='Albert', lastname='Breton')
        user_first = self.add_user(firstname='Bob', lastname='Alzard')

        users = user_dao.find_all(order=['lastname'])

        assert_that(users[0].id, equal_to(user_first.id))
        assert_that(users[1].id, equal_to(user_last.id))

    def test_find_user_no_user(self):
        result = user_dao.find_user('abc', 'def')

        assert_that(result, equal_to(None))

    def test_find_user_not_right_firstname(self):
        firstname = 'Lord'
        lastname = 'Sanderson'
        wrong_firstname = 'Gregory'

        self.add_user(firstname=firstname, lastname=lastname)

        result = user_dao.find_user(wrong_firstname, lastname)

        assert_that(result, equal_to(None))

    def test_find_user(self):
        firstname = 'Lord'
        lastname = 'Sanderson'
        user = self.add_user(firstname=firstname, lastname=lastname)

        result = user_dao.find_user('Lord', 'Sanderson')

        assert_that(result, all_of(
            has_property('id', user.id),
            has_property('firstname', firstname),
            has_property('lastname', lastname)
        ))

    def test_find_user_two_users_same_name(self):
        firstname = 'Lord'
        lastname = 'Sanderson'

        user1 = self.add_user(firstname=firstname, lastname=lastname)
        user2 = self.add_user(firstname=firstname, lastname=lastname)

        result = user_dao.find_user(firstname, lastname)

        assert_that(result, has_property('id', any_of(user1.id, user2.id)))

    def test_find_all_by_fullname_no_users(self):
        result = user_dao.find_all_by_fullname('')

        assert_that(result, has_length(0))

    def test_find_all_by_fullname(self):
        firstname = 'Lord'
        lastname = 'Sanderson'
        fullname = '%s %s' % (firstname, lastname)

        user = self.add_user(firstname=firstname, lastname=lastname)

        result = user_dao.find_all_by_fullname(fullname)

        assert_that(result, has_length(1))
        assert_that(result, contains(
            all_of(
                has_property('id', user.id),
                has_property('firstname', firstname),
                has_property('lastname', lastname)
            )))

    def test_find_all_by_fullname_lowercase(self):
        firstname = 'Lord'
        lastname = 'Sanderson'
        fullname = '%s %s' % (firstname, lastname)

        user = self.add_user(firstname=firstname, lastname=lastname)

        result = user_dao.find_all_by_fullname(fullname.lower())

        assert_that(result, has_length(1))
        assert_that(result, contains(
            all_of(
                has_property('id', user.id),
                has_property('firstname', firstname),
                has_property('lastname', lastname)
            )))

    def test_find_all_by_fullname_partial(self):
        firstname = 'Lord'
        lastname = 'Sanderson'
        partial_fullname = 'd san'

        user = self.add_user(firstname=firstname, lastname=lastname)

        result = user_dao.find_all_by_fullname(partial_fullname)

        assert_that(result, has_length(1))
        assert_that(result, contains(
            all_of(
                has_property('id', user.id),
                has_property('firstname', firstname),
                has_property('lastname', lastname)
            )))

    def test_find_all_by_fullname_two_users_default_order(self):
        search_term = 'lord'

        user_last = self.add_user(firstname='Lord', lastname='Sanderson')
        user_first = self.add_user(firstname='Great', lastname='Lord')
        self.add_user(firstname='Toto', lastname='Tata')

        result = user_dao.find_all_by_fullname(search_term)

        assert_that(result, has_length(2))
        assert_that(result, contains(
            has_property('id', user_first.id),
            has_property('id', user_last.id),
        ))

    def test_find_by_number_context_inexistant(self):
        context, number = 'default', '1234'

        user = user_dao.find_by_number_context(number, context)

        assert_that(user, is_(none()))

    def test_find_by_number_context(self):
        context, number = 'default', '1234'
        user_line = self.add_user_line_with_exten(exten=number,
                                                  context=context)

        user = user_dao.find_by_number_context(number, context)

        assert_that(user.id, equal_to(user_line.user_id))

    def test_find_by_number_context_line_commented(self):
        context, number = 'default', '1234'
        self.add_user_line_with_exten(number=number,
                                      context=context,
                                      commented_line=1)

        user = user_dao.find_by_number_context(number, context)

        assert_that(user, is_(none()))


class TestFindAllByTemplateId(DAOTestCase):

    def test_given_private_template_associated_when_finding_then_returns_user(self):
        user_row = self.add_user()

        result = user_dao.find_all_by_template_id(user_row.func_key_private_template_id)

        assert_that(result, contains(has_property('id', user_row.id)))

    def test_given_public_template_associated_when_finding_then_returns_user(self):
        template_row = self.add_func_key_template()
        user_row = self.add_user(func_key_template_id=template_row.id)

        result = user_dao.find_all_by_template_id(template_row.id)

        assert_that(result, contains(has_property('id', user_row.id)))

    def test_given_private_templates_excluded_when_finding_then_returns_empty_list(self):
        user_row = self.add_user()

        result = user_dao.find_all_by_template_id(user_row.func_key_private_template_id, private=False)

        assert_that(result, contains())


class TestSearch(DAOTestCase):

    def prepare_user(self, **parameters):
        user_row = self.add_user(**parameters)
        user = User(id=user_row.id,
                    firstname=user_row.firstname,
                    lastname=user_row.lastname or None,
                    timezone=user_row.timezone or None,
                    language=user_row.language or None,
                    description=user_row.description or None,
                    caller_id=user_row.callerid,
                    outgoing_caller_id=user_row.outcallerid or None,
                    mobile_phone_number=(user_row.mobilephonenumber or None),
                    password=(user_row.passwdclient or None),
                    username=user_row.loginclient or None,
                    music_on_hold=user_row.musiconhold or None,
                    preprocess_subroutine=user_row.preprocess_subroutine or None,
                    userfield=user_row.userfield or None,
                    private_template_id=user_row.func_key_private_template_id)
        return user

    def assert_search_returns_result(self, search_result, **parameters):
        result = user_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):

    def setUp(self):
        super(TestSearch, self).setUp()

    def test_given_no_users_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_commented_user_then_returns_one_result(self):
        user = self.prepare_user(firstname='bob')
        expected = SearchResult(1, [user])

        self.assert_search_returns_result(expected)

    def test_given_directory_view_then_returns_one_result(self):
        user = self.prepare_user(firstname='charles')
        expected = SearchResult(1, [UserDirectory(id=user.id,
                                                  line_id=None,
                                                  agent_id=None,
                                                  firstname='charles',
                                                  lastname=None,
                                                  mobile_phone_number=None,
                                                  exten=None)])

        self.assert_search_returns_result(expected, view='directory')

    def test_given_user_with_line_and_agent_then_returns_one_directory_view_result(self):
        agent_row = self.add_agent()
        user_line_row = self.add_user_line_with_exten(firstname='danny',
                                                      lastname='rogers',
                                                      agentid=agent_row.id,
                                                      mobilephonenumber='4185551234')

        expected = SearchResult(1, [UserDirectory(id=user_line_row.user_id,
                                                  line_id=user_line_row.line_id,
                                                  agent_id=agent_row.id,
                                                  firstname='danny',
                                                  lastname='rogers',
                                                  mobile_phone_number='4185551234',
                                                  exten=user_line_row.extension.exten)])

        self.assert_search_returns_result(expected, view='directory')


class TestSearchGivenMultipleUsers(TestSearch):

    def setUp(self):
        super(TestSearch, self).setUp()
        self.user1 = self.prepare_user(firstname='Ashton', lastname='ToujoursFrais')
        self.user2 = self.prepare_user(firstname='Beaugarte', lastname='Cougar')
        self.user3 = self.prepare_user(firstname='Casa', lastname='Grecque')
        self.user4 = self.prepare_user(firstname='Dunkin', lastname='Donuts')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.user2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(4, [self.user1, self.user2, self.user3, self.user4])

        self.assert_search_returns_result(expected, order='firstname')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(self):
        expected = SearchResult(4, [self.user4, self.user3, self.user2, self.user1])

        self.assert_search_returns_result(expected, order='firstname', direction='desc')

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.user2])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_skipping_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.user4, self.user3, self.user1])

        self.assert_search_returns_result(expected, skip=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.user2])

        self.assert_search_returns_result(expected,
                                          search='a',
                                          order='firstname',
                                          direction='desc',
                                          skip=1,
                                          limit=1)


class TestCreate(DAOTestCase):

    def setUp(self):
        DAOTestCase.setUp(self)
        self.entity = self.add_entity()

    def prepare_user(self, **kwargs):
        private_template_row = self.add_func_key_template(private=True)
        kwargs.setdefault('private_template_id', private_template_row.id)
        return User(**kwargs)

    def test_create(self):
        user = self.prepare_user(firstname='toto',
                                 lastname='kiki',
                                 language='fr_FR',
                                 music_on_hold='musiconhold',
                                 preprocess_subroutine='preprocess_subroutine')

        created_user = user_dao.create(user)

        row = (self.session.query(UserSchema)
               .filter(UserSchema.firstname == user.firstname)
               .filter(UserSchema.lastname == user.lastname)
               .first())

        assert_that(row.id, equal_to(created_user.id))
        assert_that(row.firstname, equal_to(user.firstname))
        assert_that(row.lastname, equal_to(user.lastname))
        assert_that(row.language, equal_to(user.language))
        assert_that(row.musiconhold, equal_to(user.music_on_hold))
        assert_that(row.preprocess_subroutine, equal_to(user.preprocess_subroutine))
        assert_that(row.func_key_private_template_id, equal_to(user.private_template_id))
        assert_that(row.entityid, equal_to(self.entity.id))

    def test_create_with_custom_caller_id(self):
        caller_id = '"caller_id"'
        user = self.prepare_user(firstname='firstname',
                                 lastname='lastname',
                                 caller_id='caller_id')

        created_user = user_dao.create(user)

        row = (self.session.query(UserSchema)
               .filter(UserSchema.firstname == user.firstname)
               .filter(UserSchema.lastname == user.lastname)
               .first())

        assert_that(row.id, equal_to(created_user.id))
        assert_that(row.firstname, equal_to(user.firstname))
        assert_that(row.lastname, equal_to(user.lastname))
        assert_that(row.callerid, equal_to(caller_id))

    def test_create_with_custom_caller_id_including_quotes(self):
        caller_id = '"caller_id"'
        user = self.prepare_user(firstname='firstname',
                                 lastname='lastname',
                                 caller_id='"caller_id"')

        created_user = user_dao.create(user)

        row = (self.session.query(UserSchema)
               .filter(UserSchema.firstname == user.firstname)
               .filter(UserSchema.lastname == user.lastname)
               .first())

        assert_that(row.id, equal_to(created_user.id))
        assert_that(row.firstname, equal_to(user.firstname))
        assert_that(row.lastname, equal_to(user.lastname))
        assert_that(row.callerid, equal_to(caller_id))

    def test_create_with_default_caller_id(self):
        caller_id = '"firstname lastname"'
        user = self.prepare_user(firstname='firstname',
                                 lastname='lastname')

        created_user = user_dao.create(user)

        row = (self.session.query(UserSchema)
               .filter(UserSchema.firstname == user.firstname)
               .filter(UserSchema.lastname == user.lastname)
               .first())

        assert_that(row.id, equal_to(created_user.id))
        assert_that(row.firstname, equal_to(user.firstname))
        assert_that(row.lastname, equal_to(user.lastname))
        assert_that(row.callerid, equal_to(caller_id))

    def test_create_with_all_fields(self):
        caller_id = '"caller_id"'
        user = self.prepare_user(firstname='firstname',
                                 lastname='lastname',
                                 timezone='America/Montreal',
                                 language='en_US',
                                 description='description',
                                 caller_id='caller_id',
                                 outgoing_caller_id='outgoing_caller_id',
                                 mobile_phone_number='1234567890',
                                 username='username',
                                 password='password',
                                 music_on_hold='music_on_hold',
                                 preprocess_subroutine='preprocess_subroutine',
                                 userfield='userfield')

        created_user = user_dao.create(user)

        row = (self.session.query(UserSchema)
               .filter(UserSchema.firstname == user.firstname)
               .filter(UserSchema.lastname == user.lastname)
               .first())

        assert_that(row.id, equal_to(created_user.id))
        assert_that(row.firstname, equal_to(user.firstname))
        assert_that(row.lastname, equal_to(user.lastname))
        assert_that(row.timezone, equal_to(user.timezone))
        assert_that(row.language, equal_to(user.language))
        assert_that(row.description, equal_to(user.description))
        assert_that(row.callerid, equal_to(caller_id))
        assert_that(row.outcallerid, equal_to(user.outgoing_caller_id))
        assert_that(row.mobilephonenumber, equal_to(user.mobile_phone_number))
        assert_that(row.loginclient, equal_to(user.username))
        assert_that(row.passwdclient, equal_to(user.password))
        assert_that(row.musiconhold, equal_to(user.music_on_hold))
        assert_that(row.preprocess_subroutine, equal_to(user.preprocess_subroutine))
        assert_that(row.userfield, equal_to(user.userfield))

    @mocked_dao_session
    def test_create_with_database_error(self, session):
        session.commit.side_effect = SQLAlchemyError()

        user = User(firstname='toto',
                    lastname='kiki',
                    language='fr_FR')

        self.assertRaises(DataError, user_dao.create, user)
        session.begin.assert_called_once_with()
        session.rollback.assert_called_once_with()


class TestEdit(DAOTestCase):

    def test_edit(self):
        firstname = 'Robert'
        lastname = 'Raleur'
        music_on_hold = 'music_on_hold'
        preprocess_subroutine = 'preprocess_subroutine'

        expected_lastname = 'Lereu'
        expected_music_on_hold = 'expected_music_on_hold'
        expected_preprocess_subroutine = 'expected_preprocess_subroutine'

        user = self.add_user(firstname=firstname,
                             lastname=lastname,
                             musiconhold=music_on_hold,
                             preprocess_subroutine=preprocess_subroutine)

        user = user_dao.get(user.id)
        user.lastname = expected_lastname
        user.music_on_hold = expected_music_on_hold
        user.preprocess_subroutine = expected_preprocess_subroutine

        user_dao.edit(user)

        row = (self.session.query(UserSchema)
               .filter(UserSchema.id == user.id)
               .first())

        assert_that(row.firstname, equal_to(firstname))
        assert_that(row.lastname, equal_to(expected_lastname))
        assert_that(row.musiconhold, equal_to(expected_music_on_hold))
        assert_that(row.preprocess_subroutine, equal_to(expected_preprocess_subroutine))

    def test_edit_all_fields(self):
        user_row = self.add_user(firstname='Paul',
                                 lastname='Rogers',
                                 callerid='"Cool dude"',
                                 outcallerid='"Cool dude going out"',
                                 loginclient='paulrogers',
                                 passwdclient='paulrogers',
                                 musiconhold='mymusic',
                                 mobilephonenumber='4185551234',
                                 userfield='userfield',
                                 timezone='America/Montreal',
                                 language='fr_FR',
                                 description='Really cool dude')

        caller_id = '"caller_id"'
        user = user_dao.get(user_row.id)
        user.firstname = 'firstname'
        user.lastname = 'lastname'
        user.timezone = 'America/Montreal'
        user.language = 'en_US'
        user.description = 'description'
        user.caller_id = 'caller_id'
        user.outgoing_caller_id = 'outgoing_caller_id'
        user.mobile_phone_number = '1234567890'
        user.username = 'username'
        user.password = 'password'
        user.music_on_hold = 'music_on_hold'
        user.preprocess_subroutine = 'preprocess_subroutine'
        user.userfield = 'userfield'

        user_dao.edit(user)

        row = (self.session.query(UserSchema)
               .filter(UserSchema.id == user.id)
               .first())

        assert_that(row.id, equal_to(user.id))
        assert_that(row.firstname, equal_to(user.firstname))
        assert_that(row.lastname, equal_to(user.lastname))
        assert_that(row.timezone, equal_to(user.timezone))
        assert_that(row.language, equal_to(user.language))
        assert_that(row.description, equal_to(user.description))
        assert_that(row.callerid, equal_to(caller_id))
        assert_that(row.outcallerid, equal_to(user.outgoing_caller_id))
        assert_that(row.mobilephonenumber, equal_to(user.mobile_phone_number))
        assert_that(row.loginclient, equal_to(user.username))
        assert_that(row.passwdclient, equal_to(user.password))
        assert_that(row.musiconhold, equal_to(user.music_on_hold))
        assert_that(row.preprocess_subroutine, equal_to(user.preprocess_subroutine))
        assert_that(row.userfield, equal_to(user.userfield))

    def test_edit_with_unknown_user(self):
        user = User(id=123, lastname='unknown')

        self.assertRaises(NotFoundError, user_dao.edit, user)

    @mocked_dao_session
    def test_edit_with_database_error(self, session):
        session.commit.side_effect = SQLAlchemyError()

        user = User(id=123,
                    firstname='toto',
                    lastname='kiki',
                    language='fr_FR')

        self.assertRaises(DataError, user_dao.edit, user)
        session.begin.assert_called_once_with()
        session.rollback.assert_called_once_with()


class TestDelete(DAOTestCase):

    def test_delete(self):
        firstname = 'Gadou'
        lastname = 'Pipo'
        user = self.add_user(firstname=firstname,
                             lastname=lastname)

        user = user_dao.get(user.id)

        user_dao.delete(user)

        row = (self.session.query(UserSchema)
               .filter(UserSchema.id == user.id)
               .first())

        assert_that(row, equal_to(None))


class TestIsCtiEnabled(DAOTestCase):

    def test_is_cti_enabled(self):
        user = self.add_user(firstname='Pierre', enableclient=1)

        self.assertTrue(user_dao.is_cti_enabled(user.id))
