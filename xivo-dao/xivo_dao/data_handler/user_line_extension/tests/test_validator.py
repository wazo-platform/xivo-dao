import unittest
from mock import patch, Mock
from hamcrest import assert_that, equal_to

from xivo_dao.data_handler.user_line_extension import validator
from xivo_dao.data_handler.user_line_extension.model import UserLineExtension
from xivo_dao.data_handler.line.model import LineSIP
from xivo_dao.data_handler.user.model import User
from xivo_dao.data_handler.extension.model import Extension
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

    @patch('xivo_dao.data_handler.extension.dao.get', Mock(return_value=Mock()))
    @patch('xivo_dao.data_handler.line.dao.get')
    @patch('xivo_dao.data_handler.user.dao.get')
    @patch('xivo_dao.data_handler.user_line_extension.dao.already_linked')
    def test_validate_create_with_user_already_associated(self, already_linked, user_dao_get, line_dao_get):

        user_id = 5898
        line_id = 52

        user = User(id=user_id)
        line = LineSIP(id=line_id)
        ule = UserLineExtension(user_id=user_id,
                                line_id=line_id,
                                extension_id=42,
                                main_user=True,
                                main_line=False)

        user_dao_get.return_value = user
        line_dao_get.return_value = line
        already_linked.return_value = True

        self.assertRaises(InvalidParametersError, validator.validate_create, ule)
        already_linked.assert_called_once_with(user_id, line_id)

    @patch('xivo_dao.data_handler.extension.dao.get')
    @patch('xivo_dao.data_handler.line.dao.get')
    @patch('xivo_dao.data_handler.user.dao.get')
    @patch('xivo_dao.data_handler.user_line_extension.dao.already_linked')
    def test_validate_create(self, already_linked, user_dao_get, line_dao_get, extension_dao_get):

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
        already_linked.return_value = False

        result_user, result_line, result_extension = validator.validate_create(ule)

        already_linked.assert_called_once_with(user_id, line_id)

        assert_that(result_user, equal_to(user))
        assert_that(result_line, equal_to(line))
        assert_that(result_extension, equal_to(extension))
