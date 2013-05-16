import unittest

from mock import Mock
from xivo_dao.models.user import User


class TestUser(unittest.TestCase):

    def test_from_data_source(self):
        user_id = 42
        properties = Mock()
        properties.id = user_id

        user = User.from_data_source(properties)

        self.assertEquals(user_id, user.id)
