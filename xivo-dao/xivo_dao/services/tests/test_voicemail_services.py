import unittest

from mock import patch, Mock

from xivo_dao.dao.voicemail_dao import VoicemailCreationError
from xivo_dao.models.voicemail import Voicemail
from xivo_dao.services import voicemail_services, exception


class TestVoicemail(unittest.TestCase):

    @patch('xivo_dao.services.voicemail_services.voicemail_dao')
    def test_delete_raises_exception(self, voicemail_dao):
        voicemail_dao.find_voicemail.return_value = None

        self.assertRaises(voicemail_services.VoicemailNotFoundError,
                          voicemail_services.delete,
                          '42', 'default')

    @patch('xivo_dao.services.voicemail_services.voicemail_dao')
    @patch('xivo_dao.notifiers.sysconf_notifier.delete_voicemail')
    def test_delete(self, sysconf_delete_voicemail, voicemail_dao):
        voicemail_id = 12
        number = '42'
        context = 'default'
        voicemail = Mock(Voicemail)
        voicemail.id = voicemail_id
        voicemail.number = number
        voicemail.context = context

        voicemail_dao.find_voicemail.return_value = voicemail

        voicemail_services.delete(number, context)

        voicemail_dao.find_voicemail.assert_called_once_with(number, context)
        voicemail_dao.delete.assert_called_once_with(voicemail)
        sysconf_delete_voicemail.assert_called_once_with(voicemail_id)

    def test_create_no_properties(self):
        voicemail = Voicemail()

        self.assertRaises(exception.MissingParametersError, voicemail_services.create, voicemail)

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

        self.assertRaises(exception.InvalidParametersError, voicemail_services.create, voicemail)

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

        self.assertRaises(exception.InvalidParametersError, voicemail_services.create, voicemail)

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

        self.assertRaises(exception.InvalidParametersError, voicemail_services.create, voicemail)

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

        self.assertRaises(exception.ElementExistsError, voicemail_services.create, voicemail)

    @patch('xivo_dao.services.context_services.find_by_name')
    @patch('xivo_dao.services.voicemail_services.voicemail_dao')
    @patch('xivo_dao.notifiers.sysconf_notifier.create_voicemail')
    def test_create(self, sysconf_create_voicemail, voicemail_dao, context_find):
        name = 'voicemail'
        number = '42'
        context = 'default'
        voicemail_id = 1

        voicemail = Voicemail(name=name,
                              number=number,
                              context=context)

        context_find.return_value = Mock()
        voicemail_dao.find_voicemail.return_value = None
        voicemail_dao.create.return_value = voicemail_id

        result = voicemail_services.create(voicemail)

        voicemail_dao.create.assert_called_once_with(voicemail)
        self.assertEquals(voicemail_id, result)
        sysconf_create_voicemail.assert_called_once_with(voicemail_id)

    @patch('xivo_dao.services.context_services.find_by_name')
    @patch('xivo_dao.services.voicemail_services.voicemail_dao')
    def test_create_with_error_from_dao(self, voicemail_dao, context_find):
        name = 'voicemail'
        number = '42'
        context = 'default'

        voicemail = Voicemail(name=name,
                              number=number,
                              context=context)

        context_find.return_value = Mock()
        voicemail_dao.find_voicemail.return_value = None

        error = Exception("message")
        voicemail_dao.create.side_effect = VoicemailCreationError(error)

        self.assertRaises(VoicemailCreationError, voicemail_services.create, voicemail)
