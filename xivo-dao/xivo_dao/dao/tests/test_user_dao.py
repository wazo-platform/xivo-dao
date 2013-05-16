import unittest

from mock import Mock, patch
from xivo_dao.dao import user_dao
from xivo_dao.models.user import User


class TestUserDAO(unittest.TestCase):

    @patch('xivo_dao.user_dao.get')
    def test_get_user_by_id_inexistant(self, mock_get):
        user_id = 42
        mock_get.side_effect = LookupError()

        self.assertRaises(LookupError, user_dao.get_user_by_id, user_id)

    @patch('xivo_dao.user_dao.get')
    def test_get_user_by_id(self, mock_get):
        user_id = 42
        expected_user = User()
        expected_user.id = user_id
        mock_user_row = Mock()
        mock_user_row.id = user_id
        mock_get.return_value = mock_user_row

        user = user_dao.get_user_by_id(user_id)

        self.assertEquals(expected_user.id, user.id)
