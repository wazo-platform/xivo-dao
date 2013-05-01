import unittest

from mock import patch, Mock

from xivo_dao.dao.voicemail import Voicemail
from xivo_dao.services import voicemail as voicemail_service


class TestVoicemail(unittest.TestCase):

    def setUp(self):
        pass

    @patch('xivo_dao.services.voicemail.voicemail_dao')
    def test_delete_raises_exception(self, voicemail_dao):
        voicemail_dao.find_voicemail.return_value = None

        self.assertRaises(voicemail_service.VoicemailNotFoundException,
                          voicemail_service.delete,
                          '42', 'default')

    @patch('xivo_dao.services.voicemail.voicemail_dao')
    def test_delete(self, voicemail_dao):
        number = '42'
        context = 'default'
        voicemail = Mock(Voicemail)

        voicemail_dao.find_voicemail.return_value = voicemail

        voicemail_service.delete(number, context)

        voicemail_dao.find_voicemail.assert_called_once_with(number, context)
        voicemail_dao.delete.assert_called_once_with(voicemail)

    @patch('xivo_dao.services.voicemail.voicemail_dao')
    def test_create_no_properties(self, voicemail_dao):
        voicemail = {}

        self.assertRaises(voicemail_service.MissingParametersError, voicemail_service.create, voicemail)

    @patch('xivo_dao.services.voicemail.voicemail_dao')
    @patch('xivo_dao.services.context.find_by_name')
    def test_create_empty_name(self, context_find, voicemail_dao):
        name = ''
        number = '42'
        context = 'default'
        voicemail = {
            'name': name,
            'number': number,
            'context': context,
        }
        context_find.return_value = Mock()
        voicemail_dao.find_voicemail.return_value = None

        self.assertRaises(voicemail_service.InvalidParametersError, voicemail_service.create, voicemail)

    @patch('xivo_dao.services.voicemail.voicemail_dao')
    @patch('xivo_dao.services.context.find_by_name')
    def test_create_invalid_number(self, context_find, voicemail_dao):
        name = 'voicemail'
        number = 'wrong_number'
        context = 'default'
        voicemail = {
            'name': name,
            'number': number,
            'context': context,
        }
        context_find.return_value = Mock()
        voicemail_dao.find_voicemail.return_value = None

        self.assertRaises(voicemail_service.InvalidParametersError, voicemail_service.create, voicemail)

    @patch('xivo_dao.services.voicemail.voicemail_dao')
    @patch('xivo_dao.services.context.find_by_name')
    def test_create_invalid_context(self, context_find, voicemail_dao):
        name = 'voicemail'
        number = '42'
        context = 'inexistant_context'
        voicemail = {
            'name': name,
            'number': number,
            'context': context,
        }
        context_find.return_value = None
        voicemail_dao.find_voicemail.return_value = None

        self.assertRaises(voicemail_service.InvalidParametersError, voicemail_service.create, voicemail)

    @patch('xivo_dao.services.voicemail.voicemail_dao')
    @patch('xivo_dao.services.context.find_by_name')
    def test_create_same_context_and_number(self, context_find, voicemail_dao):
        name = 'voicemail'
        number = '42'
        context = 'existing_context'
        voicemail = {
            'name': name,
            'number': number,
            'context': context,
        }
        context_find.return_value = Mock()
        voicemail_mock = Mock(Voicemail)
        voicemail_mock.number = '42'
        voicemail_mock.context = 'existing_context'
        voicemail_dao.find_voicemail.return_value = voicemail_mock

        self.assertRaises(voicemail_service.InvalidParametersError, voicemail_service.create, voicemail)

    @patch('xivo_dao.services.context.find_by_name')
    @patch('xivo_dao.services.voicemail.voicemail_dao')
    @patch('xivo_dao.dao.voicemail.Voicemail.from_user_data')
    def test_create(self, from_user_data_mock, voicemail_dao, context_find):
        name = 'voicemail'
        number = '42'
        context = 'default'
        voicemail = {
            'name': name,
            'number': number,
            'context': context,
        }
        context_find.return_value = Mock()
        voicemail_dao.find_voicemail.return_value = None
        voicemail_mock_input = self._create_voicemail_mock(voicemail)
        voicemail_mock_output = self._create_voicemail_mock(voicemail)
        from_user_data_mock.return_value = voicemail_mock_input
        voicemail_dao.create.return_value = voicemail_mock_output

        result = voicemail_service.create(voicemail)

        voicemail_dao.create.assert_called_once_with(voicemail_mock_input)
        self._assert_voicemail_equals(voicemail_mock_output, result)

    def _assert_voicemail_equals(self, voicemail_left, voicemail_right):
        self.assertEquals(voicemail_left.name, voicemail_right.name)
        self.assertEquals(voicemail_left.number, voicemail_right.number)
        self.assertEquals(voicemail_left.context, voicemail_right.context)

    def _create_voicemail_mock(self, properties):
        mock = Mock(Voicemail)
        mock.name = properties['name']
        mock.number = properties['number']
        mock.context = properties['context']

        return mock
