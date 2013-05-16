import unittest

from mock import Mock
from xivo_dao.models.voicemail import Voicemail


class TestVoicemail(unittest.TestCase):

    def test_equal(self):
        user_1 = Mock()
        user_2 = Mock()
        voicemail_1 = Voicemail(
            name='abc def',
            number='42',
            context='context 42',
            id=42,
            user=user_1
        )

        voicemail_2 = Voicemail(
            name='abc defg',
            number='43',
            context='context 43',
            id=43,
            user=user_2
        )

        voicemail_clone_1 = Voicemail(
            name='abc def',
            number='42',
            context='context 42',
            id=42,
            user=user_1
        )

        self.assertRaises(TypeError, lambda: voicemail_1 == 12)
        self.assertNotEquals(voicemail_1, Voicemail())
        self.assertEquals(voicemail_1, voicemail_1)
        self.assertNotEquals(voicemail_1, voicemail_2)
        self.assertEquals(voicemail_1, voicemail_clone_1)

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
