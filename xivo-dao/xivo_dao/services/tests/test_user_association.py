import unittest

from mock import Mock, patch, ANY
from xivo_dao.models.user import User
from xivo_dao.models.voicemail import Voicemail
from xivo_dao.services.voicemail_services import VoicemailNotFoundError
from xivo_dao.services.user_services import UserNotFoundError
from xivo_dao.services import user_association


class TestUserAssociation(unittest.TestCase):

    @patch('xivo_dao.dao.voicemail_dao.get_voicemail_by_id')
    @patch('xivo_dao.dao.user_dao.get_user_by_id')
    def test_associate_voicemail_when_user_inexistant(self, get_user, get_voicemail):
        user_id = 21
        voicemail_id = 32

        get_user.side_effect = LookupError()
        get_voicemail.return_value = Mock()

        self.assertRaises(UserNotFoundError, user_association.associate_voicemail, user_id, voicemail_id)

    @patch('xivo_dao.dao.voicemail_dao.get_voicemail_by_id')
    @patch('xivo_dao.dao.user_dao.get_user_by_id')
    def test_associate_voicemail_when_voicemail_inexistant(self, get_user, get_voicemail):
        user_id = 21
        voicemail_id = 32

        get_user.return_value = Mock()
        get_voicemail.side_effect = LookupError()

        self.assertRaises(VoicemailNotFoundError, user_association.associate_voicemail, user_id, voicemail_id)

    @patch('xivo_dao.dao.voicemail_dao.get_voicemail_by_id')
    @patch('xivo_dao.dao.voicemail_dao.edit')
    @patch('xivo_dao.dao.user_dao.get_user_by_id')
    def test_associate_voicemail(self, get_user, edit_voicemail, get_voicemail):
        user_id = 21
        voicemail_id = 32

        voicemail = Voicemail(
            number='42',
            context='super_context',
            name='voicemail name',
        )

        user = User(
            firstname='Johnny',
            lastname='Wilkins',
        )

        get_user.return_value = user
        get_voicemail.return_value = voicemail

        expected_voicemail = Voicemail(
            number='42',
            context='super_context',
            name='voicemail name',
            user=user
        )

        user_association.associate_voicemail(user_id, voicemail_id)

        edit_voicemail.assert_called_once_with(ANY)
        passed_voicemail = edit_voicemail.call_args[0][0]
        self.assertEquals(expected_voicemail, passed_voicemail)
