import unittest
from hamcrest import assert_that, equal_to

from mock import Mock, patch
from xivo_dao.data_handler.context.model import Context, ContextType
from xivo_dao.data_handler.context import validator
from xivo_dao.data_handler.exception import MissingParametersError
from xivo_dao.data_handler.exception import InvalidParametersError
from xivo_dao.data_handler.exception import ElementAlreadyExistsError


class TestValidator(unittest.TestCase):

    def test_validate_create_no_parameters(self):
        context = Context()

        self.assertRaises(MissingParametersError, validator.validate_create, context)

    def test_validate_create_missing_parameters(self):
        context = Context(display_name='Test')

        self.assertRaises(MissingParametersError, validator.validate_create, context)

    def test_validate_create_empty_parameters(self):
        context = Context(name='', display_name='', type='')

        self.assertRaises(InvalidParametersError, validator.validate_create, context)

    def test_validate_create_invalid_type(self):
        context = Context(name='test', display_name='test', type='invalidtype')

        self.assertRaises(InvalidParametersError, validator.validate_create, context)

    @patch('xivo_dao.context_dao.get')
    def test_validate_create_context_already_exists(self, context_dao_get):
        context_name = 'test'

        existing_context = Mock(Context)
        existing_context.name = context_name

        context_dao_get.return_value = existing_context

        context = Context(name=context_name,
                          display_name=context_name,
                          type=ContextType.internal)

        self.assertRaises(ElementAlreadyExistsError, validator.validate_create, context)

        context_dao_get.assert_called_once_with(context_name)
