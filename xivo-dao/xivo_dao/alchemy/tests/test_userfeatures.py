import unittest

from xivo_dao.alchemy.userfeatures import UserFeatures


class Test(unittest.TestCase):

    def test_fullname(self):
        user = UserFeatures()
        user.firstname = 'firstname'
        user.lastname = 'lastname'

        self.assertEqual(user.fullname, 'firstname lastname')
