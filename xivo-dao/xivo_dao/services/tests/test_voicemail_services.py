import unittest

from mock import patch, Mock

from xivo_dao.dao.voicemail_dao import Voicemail
from xivo_dao.services import voicemail_services


class TestVoicemail(unittest.TestCase):

    def setUp(self):
        pass

    @patch('xivo_dao.services.voicemail_services.voicemail_dao')
    def test_delete_raises_exception(self, voicemail_dao):
        voicemail_dao.find_voicemail.return_value = None

        self.assertRaises(voicemail_services.VoicemailNotFoundError,
                          voicemail_services.delete,
                          '42', 'default')

    @patch('xivo_dao.services.voicemail_services.voicemail_dao')
    def test_delete(self, voicemail_dao):
        number = '42'
        context = 'default'
        voicemail = Mock(Voicemail)

        voicemail_dao.find_voicemail.return_value = voicemail

        voicemail_services.delete(number, context)

        voicemail_dao.find_voicemail.assert_called_once_with(number, context)
        voicemail_dao.delete.assert_called_once_with(voicemail)

    @patch('xivo_dao.services.voicemail_services.voicemail_dao')
    def test_create_no_properties(self, voicemail_dao):
        voicemail = Voicemail()

        self.assertRaises(voicemail_services.MissingParametersError, voicemail_services.create, voicemail)

    @patch('xivo_dao.services.voicemail_services.voicemail_dao')
    @patch('xivo_dao.services.context_services.find_by_name')
    def test_create_empty_name(self, context_find, voicemail_dao):
        name = ''
        number = '42'
        context = 'default'

        voicemail = Voicemail(name=name,
                              number=number,
                              context=context)

        context_find.return_value = Mock()
        voicemail_dao.find_voicemail.return_value = None

        self.assertRaises(voicemail_services.InvalidParametersError, voicemail_services.create, voicemail)

    @patch('xivo_dao.services.voicemail_services.voicemail_dao')
    @patch('xivo_dao.services.context_services.find_by_name')
    def test_create_invalid_number(self, context_find, voicemail_dao):
        name = 'voicemail'
        number = 'wrong_number'
        context = 'default'

        voicemail = Voicemail(name=name,
                              number=number,
                              context=context)

        context_find.return_value = Mock()
        voicemail_dao.find_voicemail.return_value = None

        self.assertRaises(voicemail_services.InvalidParametersError, voicemail_services.create, voicemail)

    @patch('xivo_dao.services.voicemail_services.voicemail_dao')
    @patch('xivo_dao.services.context_services.find_by_name')
    def test_create_invalid_context(self, context_find, voicemail_dao):
        name = 'voicemail'
        number = '42'
        context = 'inexistant_context'

        voicemail = Voicemail(name=name,
                              number=number,
                              context=context)

        context_find.return_value = None
        voicemail_dao.find_voicemail.return_value = None

        self.assertRaises(voicemail_services.InvalidParametersError, voicemail_services.create, voicemail)

    @patch('xivo_dao.services.voicemail_services.voicemail_dao')
    @patch('xivo_dao.services.context_services.find_by_name')
    def test_create_same_context_and_number(self, context_find, voicemail_dao):
        name = 'voicemail'
        number = '42'
        context = 'existing_context'

        voicemail = Voicemail(name=name,
                              number=number,
                              context=context)

        context_find.return_value = Mock()
        voicemail_mock = Mock(Voicemail)
        voicemail_mock.number = '42'
        voicemail_mock.context = 'existing_context'
        voicemail_dao.find_voicemail.return_value = voicemail_mock

        self.assertRaises(voicemail_services.VoicemailExistsError, voicemail_services.create, voicemail)

    @patch('xivo_dao.services.context_services.find_by_name')
    @patch('xivo_dao.services.voicemail_services.voicemail_dao')
    def test_create(self, voicemail_dao, context_find):
        name = 'voicemail'
        number = '42'
        context = 'default'
        voicemail_id = 1

        voicemail = Voicemail(name=name,
                              number=number,
                              context=context)

        context_find.return_value = Mock()
        voicemail_dao.find_voicemail.return_value = None

        voicemail_mock_output = self._create_voicemail_mock(voicemail, voicemail_id)

        voicemail_dao.create.return_value = voicemail_mock_output

        result = voicemail_services.create(voicemail)

        voicemail_dao.create.assert_called_once_with(voicemail)
        self._assert_voicemail_equals(voicemail_mock_output, result)

    def _assert_voicemail_equals(self, voicemail_left, voicemail_right):
        self.assertEquals(voicemail_left.name, voicemail_right.name)
        self.assertEquals(voicemail_left.number, voicemail_right.number)
        self.assertEquals(voicemail_left.context, voicemail_right.context)
        self.assertEquals(voicemail_left.id, voicemail_right.id)

    def _create_voicemail_mock(self, voicemail, voicemail_id):
        mock = Mock(Voicemail)
        mock.name = voicemail.name
        mock.number = voicemail.number
        mock.context = voicemail.context
        mock.id = voicemail_id

        return mock
