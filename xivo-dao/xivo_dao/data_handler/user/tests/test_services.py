# -*- coding: utf-8 -*-

import unittest

from hamcrest import assert_that, equal_to
from mock import patch, Mock

from xivo_dao.data_handler.exception import ElementCreationError
from xivo_dao.data_handler.exception import ElementNotExistsError
from xivo_dao.data_handler.user import services as user_services
from xivo_dao.data_handler.user.model import User
from xivo_dao.data_handler.user.model import UserOrdering


class TestUser(unittest.TestCase):

    @patch('xivo_dao.data_handler.user.dao.get')
    def test_get_not_found(self, user_dao_get):
        user_id = 123
        user_dao_get.side_effect = ElementNotExistsError('User', id=user_id)

        self.assertRaises(LookupError, user_services.get, user_id)

    @patch('xivo_dao.data_handler.user.dao.get')
    def test_get(self, user_dao_get):
        user_id = 123
        expected_result = User(id=user_id)
        user_dao_get.return_value = User(id=user_id)

        result = user_services.get(user_id)

        user_dao_get.assert_called_once_with(user_id)
        assert_that(result, equal_to(expected_result))

    @patch('xivo_dao.data_handler.user.dao.get_by_number_context')
    def test_get_by_number_context(self, user_dao_get):
        number, context = '9876', 'default'
        user_id = 123
        expected_result = User(id=user_id)
        user_dao_get.return_value = User(id=user_id)

        result = user_services.get_by_number_context(number, context)

        user_dao_get.assert_called_once_with(number, context)
        assert_that(result, equal_to(expected_result))

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

    @patch('xivo_dao.data_handler.user.dao.find_user')
    def test_find_user(self, user_dao_find_user):
        user = Mock(User)
        firstname = 'Lord'
        lastname = 'Sanderson'

        user_dao_find_user.return_value = user

        result = user_services.find_by_firstname_lastname(firstname, lastname)

        self.assertEquals(result, user)
        user_dao_find_user.assert_called_once_with(firstname, lastname)

    @patch('xivo_dao.data_handler.user.dao.find_all_by_fullname')
    def test_find_all_by_fullname(self, user_dao_find_all_by_fullname):
        fullname = 'Lord Sanderson'

        user = Mock(User)
        user.firstname = 'Lord'
        user.lastname = 'Sanderson'

        expected_result = [user]

        user_dao_find_all_by_fullname.return_value = [user]

        result = user_services.find_all_by_fullname(fullname)

        self.assertEquals(expected_result, result)
        user_dao_find_all_by_fullname.assert_called_once_with(fullname)

    @patch('xivo_dao.data_handler.user.notifier.created')
    @patch('xivo_dao.data_handler.user.dao.create')
    @patch('xivo_dao.data_handler.user.validator.validate_create')
    def test_create(self, user_validate_create, user_dao_create, user_notifier_created):
        firstname = 'user'
        lastname = 'toto'

        user = User(firstname=firstname, lastname=lastname)

        user_dao_create.return_value = user

        result = user_services.create(user)

        user_validate_create.assert_called_once_with(user)
        user_dao_create.assert_called_once_with(user)
        self.assertEquals(type(result), User)
        user_notifier_created.assert_called_once_with(user)

    @patch('xivo_dao.data_handler.user.dao.create')
    @patch('xivo_dao.data_handler.user.validator.validate_create')
    def test_create_with_error_from_dao(self, user_validate_create, user_dao_create):
        firstname = 'user'
        lastname = 'toto'

        user = User(firstname=firstname, lastname=lastname)

        error = Exception("message")
        user_dao_create.side_effect = ElementCreationError(error, '')

        self.assertRaises(ElementCreationError, user_services.create, user)
        user_validate_create.assert_called_once_with(user)

    @patch('xivo_dao.data_handler.user.services.update_voicemail_fullname')
    @patch('xivo_dao.data_handler.line.services.update_callerid')
    @patch('xivo_dao.data_handler.user.notifier.edited')
    @patch('xivo_dao.data_handler.user.dao.edit')
    @patch('xivo_dao.data_handler.user.validator.validate_edit')
    def test_edit(self,
                  user_validate_edit,
                  user_dao_edit,
                  user_notifier_edited,
                  line_services_update_callerid,
                  update_voicemail_fullname):
        user = User(id=1, firstname='user', lastname='toto', voicemail_id=3)

        user_services.edit(user)

        user_validate_edit.assert_called_once_with(user)
        user_dao_edit.assert_called_once_with(user)
        user_notifier_edited.assert_called_once_with(user)
        line_services_update_callerid.assert_called_once_with(user)
        update_voicemail_fullname.assert_called_once_with(user)

    @patch('xivo_dao.data_handler.user.notifier.deleted')
    @patch('xivo_dao.data_handler.user.dao.delete')
    def test_delete(self, user_dao_delete, user_notifier_deleted):
        user = User(id=1, firstname='user', lastname='toto')

        user_services.delete(user)

        user_dao_delete.assert_called_once_with(user)
        user_notifier_deleted.assert_called_once_with(user)

    @patch('xivo_dao.data_handler.voicemail.dao.edit')
    @patch('xivo_dao.data_handler.voicemail.dao.get')
    def test_update_voicemail_fullname_no_voicemail(self, voicemail_dao_get, voicemail_dao_edit):
        user = User(firstname='firstname', lastname='lastname')

        user_services.update_voicemail_fullname(user)
        assert_that(voicemail_dao_get.call_count, equal_to(0))
        assert_that(voicemail_dao_edit.call_count, equal_to(0))

    @patch('xivo_dao.data_handler.voicemail.dao.edit')
    @patch('xivo_dao.data_handler.voicemail.dao.get')
    def test_update_voicemail_fullname(self, voicemail_dao_get, voicemail_dao_edit):
        user = User(firstname='firstname', lastname='lastname', voicemail_id=3)
        fullname = '%s %s' % (user.firstname, user.lastname)

        voicemail = voicemail_dao_get.return_value = Mock()

        user_services.update_voicemail_fullname(user)

        voicemail_dao_get.assert_called_once_with(user.voicemail_id)
        assert_that(voicemail.name, equal_to(fullname))
        voicemail_dao_edit.assert_called_once_with(voicemail)
