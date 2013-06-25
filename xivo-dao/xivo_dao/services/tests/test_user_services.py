# -*- coding: utf-8 -*-

import unittest

from mock import patch, Mock
from xivo_dao.models.user import User
from xivo_dao.services import exception, user_services
from xivo_dao.dao.user_dao import UserCreationError


class TestUser(unittest.TestCase):

    def test_create_no_properties(self):
        user = User()

        self.assertRaises(exception.MissingParametersError, user_services.create, user)

    @patch('xivo_dao.services.user_services.user_dao')
    def test_create_empty_firstname(self, user_dao):
        firstname = ''
        lastname = 'toto'

        user = User(firstname=firstname, lastname=lastname)

        user_dao.find_user.return_value = None

        self.assertRaises(exception.InvalidParametersError, user_services.create, user)

    @patch('xivo_dao.services.user_services.user_dao')
    def test_create_same_firtname_and_lastname(self, user_dao):
        firstname = 'user'
        lastname = 'toto'

        user = User(firstname=firstname, lastname=lastname)

        user_mock = Mock(User)
        user_mock.firstname = firstname
        user_mock.lastname = lastname
        user_dao.find_user.return_value = user_mock

        self.assertRaises(exception.ElementExistsError, user_services.create, user)

    @patch('xivo_dao.notifiers.bus_notifier.user_created')
    @patch('xivo_dao.services.user_services.user_dao')
    @patch('xivo_dao.notifiers.sysconf_notifier.create_user')
    def test_create(self, sysconf_create_user, user_dao, bus_notifier_user_created):
        firstname = 'user'
        lastname = 'toto'
        user_id = 1

        user = User(firstname=firstname, lastname=lastname)

        user_dao.find_user.return_value = None
        user_dao.create.return_value = user_id

        result = user_services.create(user)

        user_dao.create.assert_called_once_with(user)
        self.assertEquals(user_id, result)
        sysconf_create_user.assert_called_once_with(user_id)
        bus_notifier_user_created.assert_called_once_with(user_id)

    @patch('xivo_dao.services.user_services.user_dao')
    def test_create_with_error_from_dao(self, user_dao):
        firstname = 'user'
        lastname = 'toto'

        user = User(firstname=firstname, lastname=lastname)

        user_dao.find_user.return_value = None

        error = Exception("message")
        user_dao.create.side_effect = UserCreationError(error)

        self.assertRaises(UserCreationError, user_services.create, user)

    @patch('xivo_dao.notifiers.bus_notifier.user_updated')
    @patch('xivo_dao.notifiers.sysconf_notifier.edit_user')
    @patch('xivo_dao.services.user_services.user_dao.edit')
    def test_edit(self, user_dao_edit, sysconf_edit_user, bus_notifier_user_updated):
        user = User(id=1, firstname='user', lastname='toto')

        user_services.edit(user)

        user_dao_edit.assert_called_once_with(user)
        sysconf_edit_user.assert_called_once_with(user.id)
        bus_notifier_user_updated.assert_called_once_with(user.id)
