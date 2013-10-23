import unittest
from mock import patch, Mock
from hamcrest import assert_that, equal_to, contains

from xivo_dao.data_handler.user_line_extension import validator
from xivo_dao.data_handler.user_line_extension.model import UserLineExtension
from xivo_dao.data_handler.line.model import LineSIP
from xivo_dao.data_handler.user.model import User
from xivo_dao.data_handler.extension.model import Extension
from xivo_dao.data_handler.context.services import ContextRange
from xivo_dao.data_handler.exception import MissingParametersError, InvalidParametersError, \
    NonexistentParametersError, ElementNotExistsError


class TestUserLineExtensionValidator(unittest.TestCase):

    def test_validate_no_properties(self):
        user_line_extension = UserLineExtension()

        self.assertRaises(MissingParametersError, validator.validate, user_line_extension)

    def test_validate_invalid_exten_id(self):
        ule = UserLineExtension(user_id=5898,
                                line_id=52,
                                extension_id='tot',
                                main_user=True,
                                main_line=False)

        self.assertRaises(InvalidParametersError, validator.validate, ule)

    def test_validate_invalid_main_line(self):
        ule = UserLineExtension(user_id=5898,
                                line_id=52,
                                extension_id=445,
                                main_user=True,
                                main_line='ok')

        self.assertRaises(InvalidParametersError, validator.validate, ule)

    def test_validate_invalid_main_user(self):
        ule = UserLineExtension(user_id=5898,
                                line_id=52,
                                extension_id=445,
                                main_user='oui',
                                main_line=False)

        self.assertRaises(InvalidParametersError, validator.validate, ule)

    def test_validate_without_line_id(self):
        ule = UserLineExtension(user_id=5898,
                                extension_id=52,
                                main_user=True,
                                main_line=False)

        self.assertRaises(MissingParametersError, validator.validate, ule)

    @patch('xivo_dao.data_handler.user.dao.get', Mock(return_value=Mock()))
    @patch('xivo_dao.data_handler.line.dao.get', Mock(return_value=Mock()))
    @patch('xivo_dao.data_handler.extension.dao.get', Mock(side_effect=ElementNotExistsError('')))
    def test_validate_with_nonexistent_extension(self):
        ule = UserLineExtension(user_id=5898,
                                line_id=52,
                                extension_id=42,
                                main_user=True,
                                main_line=False)

        self.assertRaises(NonexistentParametersError, validator.validate, ule)

    @patch('xivo_dao.data_handler.user.dao.get', Mock(return_value=Mock()))
    @patch('xivo_dao.data_handler.extension.dao.get', Mock(return_value=Mock()))
    @patch('xivo_dao.data_handler.line.dao.get', Mock(side_effect=ElementNotExistsError('')))
    def test_validate_with_nonexistent_line(self):
        ule = UserLineExtension(user_id=5898,
                                line_id=52,
                                extension_id=42,
                                main_user=True,
                                main_line=False)

        self.assertRaises(NonexistentParametersError, validator.validate, ule)

    @patch('xivo_dao.data_handler.extension.dao.get', Mock(return_value=Mock()))
    @patch('xivo_dao.data_handler.line.dao.get', Mock(return_value=Mock()))
    @patch('xivo_dao.data_handler.user.dao.get', Mock(side_effect=ElementNotExistsError('')))
    def test_validate_with_nonexistent_user(self):
        ule = UserLineExtension(user_id=5898,
                                line_id=52,
                                extension_id=42,
                                main_user=True,
                                main_line=False)

        self.assertRaises(NonexistentParametersError, validator.validate, ule)

    @patch('xivo_dao.data_handler.extension.dao.get', Mock(return_value=Mock()))
    @patch('xivo_dao.data_handler.line.dao.get', Mock(return_value=Mock()))
    @patch('xivo_dao.data_handler.user.dao.get', Mock(return_value=Mock()))
    def test_validate_no_main_user_does_not_raise_error(self):
        user_line_extension = UserLineExtension(user_id=1, line_id=2, extension_id=3, main_line=False)

        validator.validate(user_line_extension)

    @patch('xivo_dao.data_handler.extension.dao.get', Mock(return_value=Mock()))
    @patch('xivo_dao.data_handler.line.dao.get', Mock(return_value=Mock()))
    @patch('xivo_dao.data_handler.user.dao.get', Mock(return_value=Mock()))
    def test_validate_no_main_line_does_not_raise_error(self):
        user_line_extension = UserLineExtension(user_id=1, line_id=2, extension_id=3, main_user=False)

        validator.validate(user_line_extension)

    @patch('xivo_dao.data_handler.extension.dao.get')
    @patch('xivo_dao.data_handler.line.dao.get')
    @patch('xivo_dao.data_handler.user.dao.get')
    def test_validate(self, user_dao_get, line_dao_get, extension_dao_get):

        user_id = 1
        line_id = 2
        extension_id = 3

        user = User(id=user_id)
        line = LineSIP(id=line_id)
        extension = Extension(id=extension_id)

        ule = UserLineExtension(user_id=user_id,
                                line_id=line_id,
                                extension_id=extension_id,
                                main_user=True,
                                main_line=False)

        user_dao_get.return_value = user
        line_dao_get.return_value = line
        extension_dao_get.return_value = extension

        result_user, result_line, result_extension = validator.validate(ule)

        assert_that(result_user, equal_to(user))
        assert_that(result_line, equal_to(line))
        assert_that(result_extension, equal_to(extension))

    @patch('xivo_dao.data_handler.user_line_extension.validator.validate')
    @patch('xivo_dao.data_handler.user_line_extension.validator.check_if_extension_in_context_range')
    @patch('xivo_dao.data_handler.user_line_extension.validator.check_if_user_and_line_already_linked')
    @patch('xivo_dao.data_handler.user_line_extension.validator.check_if_extension_already_linked_to_a_line')
    def test_validate_create(self,
                             check_if_extension_already_linked_to_a_line,
                             check_if_user_and_line_already_linked,
                             check_if_extension_in_context_range,
                             ule_validate):

        user_mock, line_mock, extension_mock = Mock(), Mock(), Mock()
        ule_validate.return_value = (user_mock, line_mock, extension_mock)

        ule = Mock(UserLineExtension)

        result = validator.validate_create(ule)

        assert_that(result, contains(user_mock, line_mock, extension_mock))

        ule_validate.assert_called_once_with(ule)
        check_if_user_and_line_already_linked.assert_called_once_with(user_mock, line_mock)
        check_if_extension_in_context_range.assert_called_once_with(extension_mock)
        check_if_extension_already_linked_to_a_line.assert_called_once_with(extension_mock)

    @patch('xivo_dao.data_handler.user_line_extension.dao.already_linked')
    def test_check_if_user_and_line_already_linked_when_linked(self, already_linked):
        user = Mock(User, id=1)
        line = Mock(LineSIP, id=2)
        already_linked.return_value = True

        self.assertRaises(InvalidParametersError, validator.check_if_user_and_line_already_linked, user, line)
        already_linked.assert_called_once_with(user.id, line.id)

    @patch('xivo_dao.data_handler.user_line_extension.dao.already_linked')
    def test_check_if_user_and_line_already_linked_when_not_linked(self, already_linked):
        user = Mock(User, id=1)
        line = Mock(LineSIP, id=2)
        already_linked.return_value = False

        validator.check_if_user_and_line_already_linked(user, line)
        already_linked.assert_called_once_with(user.id, line.id)

    @patch('xivo_dao.data_handler.context.services.is_extension_in_specific_range')
    def test_check_if_extension_in_context_range_when_context_outside_of_range(self, is_extension_in_specific_range):
        extension = Mock(Extension, exten='1000', context='default')
        is_extension_in_specific_range.return_value = False

        self.assertRaises(InvalidParametersError, validator.check_if_extension_in_context_range, extension)

        is_extension_in_specific_range.assert_called_once_with(extension, ContextRange.users)

    @patch('xivo_dao.data_handler.context.services.is_extension_in_specific_range')
    def test_check_if_extension_in_context_range_when_context_inside_of_range(self, is_extension_in_specific_range):
        extension = Mock(Extension, exten='1000', context='default')
        is_extension_in_specific_range.return_value = True

        validator.check_if_extension_in_context_range(extension)

        is_extension_in_specific_range.assert_called_once_with(extension, ContextRange.users)

    @patch('xivo_dao.data_handler.user_line_extension.dao.find_all_by_extension_id')
    def test_check_if_extension_already_linked_to_a_line_when_not_linked(self, find_all_by_extension_id):
        extension = Mock(Extension, id=1)

        find_all_by_extension_id.return_value = []

        validator.check_if_extension_already_linked_to_a_line(extension)

        find_all_by_extension_id.assert_called_once_with(extension.id)

    @patch('xivo_dao.data_handler.user_line_extension.dao.find_all_by_extension_id')
    def test_check_if_extension_already_linked_to_a_line_when_already_linked(self, find_all_by_extension_id):
        extension = Mock(Extension, id=1, exten='1000', context='default')

        find_all_by_extension_id.return_value = [extension]

        self.assertRaises(InvalidParametersError, validator.check_if_extension_already_linked_to_a_line, extension)

        find_all_by_extension_id.assert_called_once_with(extension.id)

    @patch('xivo_dao.data_handler.user_line_extension.dao.main_user_is_allowed_to_delete')
    def test_is_allowed_to_delete(self, is_allowed_to_delete):
        ule_main_user = UserLineExtension(main_user=True,
                                          line_id=34)
        ule_secondary_user = UserLineExtension(main_user=False,
                                               line_id=34)

        is_allowed_to_delete.return_value = True

        validator.is_allowed_to_delete(ule_main_user)
        validator.is_allowed_to_delete(ule_secondary_user)

    @patch('xivo_dao.data_handler.user_line_extension.dao.main_user_is_allowed_to_delete')
    def test_is_allowed_to_delete_with_secondary_users(self, is_allowed_to_delete):
        ule_main_user = UserLineExtension(main_user=True,
                                          line_id=34)
        ule_secondary_user = UserLineExtension(main_user=False,
                                               line_id=34)

        is_allowed_to_delete.return_value = False

        self.assertRaises(InvalidParametersError, validator.is_allowed_to_delete, ule_main_user)
        validator.is_allowed_to_delete(ule_secondary_user)
