import unittest

from mock import Mock
from xivo_dao.models.voicemail import Voicemail


class TestVoicemail(unittest.TestCase):
    def test_from_data_source(self):
        name = 'voicemail name'
        number = '42'
        context = 'default'
        properties = Mock()
        properties.fullname = name
        properties.mailbox = number
        properties.context = context

        voicemail = Voicemail.from_data_source(properties)

        self.assertEquals(name, voicemail.name)
        self.assertEquals(number, voicemail.number)
        self.assertEquals(context, voicemail.context)

    def test_from_user_data_no_id(self):
        name = 'voicemail name'
        number = '42'
        context = 'default'
        properties = {
            'name': name,
            'number': number,
            'context': context,
        }

        voicemail = Voicemail.from_user_data(properties)

        self.assertEquals(None, voicemail.id)
        self.assertEquals(name, voicemail.name)
        self.assertEquals(number, voicemail.number)
        self.assertEquals(context, voicemail.context)

    def test_from_user_data_with_id(self):
        voicemail_id = 1
        name = 'voicemail name'
        number = '42'
        context = 'default'
        properties = {
            'id': voicemail_id,
            'name': name,
            'number': number,
            'context': context,
        }

        voicemail = Voicemail.from_user_data(properties)

        self.assertEquals(voicemail_id, voicemail.id)
        self.assertEquals(name, voicemail.name)
        self.assertEquals(number, voicemail.number)
        self.assertEquals(context, voicemail.context)
