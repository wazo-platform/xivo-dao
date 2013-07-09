# -*- coding: utf-8 -*-

import unittest

from mock import patch, Mock
from xivo_dao.data_handler.user.model import User
from xivo_dao.data_handler.user import services as user_services
from xivo_dao.data_handler.exception import MissingParametersError, \
    ElementAlreadyExistsError, InvalidParametersError, ElementCreationError

from xivo_dao.data_handler.user.model import UserOrdering


class TestUser(unittest.TestCase):

    @patch('xivo_dao.data_handler.user.dao.find_all')
    def test_find_all(self, user_dao_find_all):
        first_user = Mock(User)
        second_user = Mock(User)
        expected_order = None

        expected = [first_user, second_user]

        user_dao_find_all.return_value = expected

        result = user_services.find_all()

        self.assertEquals(result, expected)

        user_dao_find_all.assert_called_once_with(order=expected_order)

    @patch('xivo_dao.data_handler.user.dao.find_all')
    def test_find_all_order_by_lastname(self, user_dao_find_all):
        first_user = Mock(User)
        second_user = Mock(User)
        expected_order = [UserOrdering.lastname]

        expected = [first_user, second_user]

        user_dao_find_all.return_value = expected

        result = user_services.find_all(order=[UserOrdering.lastname])

        self.assertEquals(result, expected)

        user_dao_find_all.assert_called_once_with(order=expected_order)

    def test_create_no_properties(self):
        user = User()

        self.assertRaises(MissingParametersError, user_services.create, user)

    @patch('xivo_dao.data_handler.user.dao.find_user', Mock(return_value=None))
    @patch('xivo_dao.data_handler.user.dao.create')
    def test_create_empty_firstname(self, user_dao_create):
        firstname = ''
        lastname = 'toto'

        user = User(firstname=firstname, lastname=lastname)

        self.assertRaises(InvalidParametersError, user_services.create, user)

    @patch('xivo_dao.data_handler.user.dao.find_user')
    @patch('xivo_dao.data_handler.user.dao.create')
    def test_create_same_firtname_and_lastname(self, user_dao_create, find_user):
        firstname = 'user'
        lastname = 'toto'

        user = User(firstname=firstname, lastname=lastname)

        user_mock = Mock(User)
        user_mock.firstname = firstname
        user_mock.lastname = lastname
        find_user.return_value = user_mock

        self.assertRaises(ElementAlreadyExistsError, user_services.create, user)

    @patch('xivo_dao.data_handler.user.dao.find_user', Mock(return_value=None))
    @patch('xivo_dao.data_handler.user.notifier.created')
    @patch('xivo_dao.data_handler.user.dao.create')
    def test_create(self, user_dao_create, user_notifier_created):
        firstname = 'user'
        lastname = 'toto'

        user = User(firstname=firstname, lastname=lastname)

        user_dao_create.return_value = user

        result = user_services.create(user)

        user_dao_create.assert_called_once_with(user)
        self.assertEquals(type(result), User)
        user_notifier_created.assert_called_once_with(user)

    @patch('xivo_dao.data_handler.user.dao.find_user', Mock(return_value=None))
    @patch('xivo_dao.data_handler.user.dao.create')
    def test_create_with_error_from_dao(self, user_dao_create):
        firstname = 'user'
        lastname = 'toto'

        user = User(firstname=firstname, lastname=lastname)

        error = Exception("message")
        user_dao_create.side_effect = ElementCreationError(error, '')

        self.assertRaises(ElementCreationError, user_services.create, user)

    @patch('xivo_dao.data_handler.user.notifier.edited')
    @patch('xivo_dao.data_handler.user.dao.edit')
    def test_edit(self, user_dao_edit, user_notifier_edited):
        user = User(id=1, firstname='user', lastname='toto')

        user_services.edit(user)

        user_dao_edit.assert_called_once_with(user)
        user_notifier_edited.assert_called_once_with(user)

    @patch('xivo_dao.data_handler.user.notifier.deleted')
    @patch('xivo_dao.data_handler.user.dao.delete')
    def test_delete(self, user_dao_delete, user_notifier_deleted):
        user = User(id=1, firstname='user', lastname='toto')

        user_services.delete(user)

        user_dao_delete.assert_called_once_with(user)
        user_notifier_deleted.assert_called_once_with(user)
