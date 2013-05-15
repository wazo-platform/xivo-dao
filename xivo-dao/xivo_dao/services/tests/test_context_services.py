import unittest
from mock import Mock, patch

from xivo_dao.services import context_services


class TestContext(unittest.TestCase):

    @patch('xivo_dao.context_dao.get')
    def test_find_by_name_inexistant(self, context_dao_get):
        context_name = 'inexistant_context'
        context_dao_get.return_value = None

        result = context_services.find_by_name(context_name)

        self.assertEquals(None, result)

    @patch('xivo_dao.context_dao.get')
    def test_find_by_name(self, context_dao_get):
        context_name = 'my_context'
        context_mock = Mock()
        context_dao_get.return_value = context_mock

        result = context_services.find_by_name(context_name)

        self.assertEquals(context_mock, result)
