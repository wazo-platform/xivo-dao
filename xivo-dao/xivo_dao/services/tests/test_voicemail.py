import unittest

from mock import patch, Mock

from xivo_dao.dao.voicemail import Voicemail
from xivo_dao.services import voicemail as voicemail_service


class TestVoicemail(unittest.TestCase):

    def setUp(self):
        pass

    @patch('xivo_dao.services.voicemail.voicemail_dao')
    def test_delete_by_number_raises_exception(self, voicemail_dao):
        voicemail_dao.find_by_number.return_value = None

        self.assertRaises(voicemail_service.VoicemailNotFoundException,
                          voicemail_service.delete_by_number,
                          '42')

    @patch('xivo_dao.services.voicemail.voicemail_dao')
    def test_delete_by_number(self, voicemail_dao):
        voicemail = Mock(Voicemail)

        voicemail_dao.find_by_number.return_value = voicemail

        voicemail_service.delete_by_number('42')

        voicemail_dao.find_by_number.assert_called_once_with('42')
        voicemail_dao.delete.assert_called_once_with(voicemail)
