import unittest
from mock import Mock

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.voicemail import Voicemail as VoicemailSchema
from xivo_dao.alchemy.usersip import UserSIP as UserSIPSchema
from xivo_dao.alchemy.sccpdevice import SCCPDevice as SCCPDeviceSchema
from xivo_dao.alchemy.userfeatures import test_dependencies
from xivo_dao.alchemy.userfeatures import UserFeatures as UserSchema
from xivo_dao.dao import voicemail_dao
from xivo_dao.dao.voicemail_dao import Voicemail


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


class TestFindVoicemail(DAOTestCase):

    tables = [
        VoicemailSchema,
        UserSIPSchema,
        UserSchema,
    ] + test_dependencies

    def setUp(self):
        self.empty_tables()

    def test_find_with_no_voicemail(self):
        expected = None
        result = voicemail_dao.find_voicemail('42', 'my_context')

        self.assertEquals(expected, result)

    def test_find_with_wrong_context(self):
        number = '42'
        context = 'default'

        voicemail_row = VoicemailSchema(context=context,
                                        mailbox=number)
        self.add_me(voicemail_row)

        result = voicemail_dao.find_voicemail(number, 'bad_context')

        self.assertEquals(None, result)

    def test_find_with_one_voicemail(self):
        number = '42'
        context = 'default'
        number_at_context = '42@default'

        voicemail_row = VoicemailSchema(context=context,
                                        mailbox=number)
        self.add_me(voicemail_row)

        result = voicemail_dao.find_voicemail(number, context)

        self.assertEquals(result.number, number)
        self.assertEquals(result.context, context)
        self.assertEquals(result.number_at_context, number_at_context)

    def test_find_with_two_voicemails(self):
        number = '42'
        context = 'default'
        number_at_context = '42@default'

        first_voicemail = VoicemailSchema(context=context,
                                          mailbox='43')
        second_voicemail = VoicemailSchema(context=context,
                                           mailbox=number)

        self.add_me(first_voicemail)
        self.add_me(second_voicemail)

        result = voicemail_dao.find_voicemail(number, context)
        self.assertEquals(result.number, number)
        self.assertEquals(result.context, context)
        self.assertEquals(result.number_at_context, number_at_context)


class TestVoicemailDeleteSIP(DAOTestCase):

    tables = [
        VoicemailSchema,
        UserSIPSchema,
        SCCPDeviceSchema,
        UserSchema,
    ] + test_dependencies

    def setUp(self):
        self.empty_tables()

    def test_delete_from_sip_user(self):
        voicemail = Mock(voicemail_dao.Voicemail)
        voicemail.number = '42'
        voicemail.context = 'default'
        voicemail.number_at_context = '42@default'

        user_id, user_sip_id, voicemail_id = self._prepare_database(voicemail)
        voicemail.id = voicemail_id

        voicemail_dao.delete(voicemail)

        self._check_user_table(user_id)
        self._check_user_sip_table(user_sip_id)
        self._check_voicemail_table(voicemail_id)

    def _prepare_database(self, voicemail):
        voicemail_row = VoicemailSchema(context=voicemail.context,
                                        mailbox=voicemail.number)

        self.add_me(voicemail_row)

        user_row = UserSchema(firstname='John',
                              lastname='Doe',
                              voicemailtype='asterisk',
                              voicemailid=voicemail_row.uniqueid,
                              language='fr_FR')

        self.add_me(user_row)

        user_sip_row = UserSIPSchema(name='bla',
                                     type='friend',
                                     mailbox='42@default')

        self.add_me(user_sip_row)

        return (user_row.id, user_sip_row.id, voicemail_row.uniqueid)

    def _check_user_table(self, user_id):
        user_row = (self.session.query(UserSchema)
                    .filter(UserSchema.id == user_id)
                    .first())

        self.assertEquals(user_row.voicemailid, None)

    def _check_user_sip_table(self, user_sip_id):

        user_sip_row = (self.session.query(UserSIPSchema)
                        .filter(UserSIPSchema.id == user_sip_id)
                        .first())

        self.assertEquals(user_sip_row.mailbox, None)

    def _check_voicemail_table(self, voicemail_id):

        voicemail_row = (self.session.query(VoicemailSchema)
                         .filter(VoicemailSchema.uniqueid == voicemail_id)
                         .first())

        self.assertEquals(voicemail_row, None)


class TestVoicemailDeleteSCCP(DAOTestCase):

    tables = [
        VoicemailSchema,
        UserSIPSchema,
        SCCPDeviceSchema,
        UserSchema,
    ] + test_dependencies

    def setUp(self):
        self.empty_tables()

    def test_delete_from_sccp_user(self):
        voicemail = Mock(voicemail_dao.Voicemail)
        voicemail.number = '42'
        voicemail.context = 'default'
        voicemail.number_at_context = '42@default'

        user_id, sccp_device_id, voicemail_id = self._prepare_database(voicemail)
        voicemail.id = voicemail_id

        voicemail_dao.delete(voicemail)

        self._check_user_table(user_id)
        self._check_voicemail_table(voicemail_id)

    def _prepare_database(self, voicemail):
        voicemail_row = VoicemailSchema(context=voicemail.context,
                                        mailbox=voicemail.number)

        self.add_me(voicemail_row)

        user_row = UserSchema(firstname='John',
                              lastname='Doe',
                              voicemailtype='asterisk',
                              voicemailid=voicemail_row.uniqueid,
                              language='fr_FR')

        self.add_me(user_row)

        sccp_device_row = SCCPDeviceSchema(name='SEPabcd',
                                           device='SEPabcd',
                                           voicemail='42')

        self.add_me(sccp_device_row)

        return (user_row.id, sccp_device_row.id, voicemail_row.uniqueid)

    def _check_user_table(self, user_id):
        user_row = (self.session.query(UserSchema)
                    .filter(UserSchema.id == user_id)
                    .first())

        self.assertEquals(user_row.voicemailid, None)

    def _check_voicemail_table(self, voicemail_id):

        voicemail_row = (self.session.query(VoicemailSchema)
                         .filter(VoicemailSchema.uniqueid == voicemail_id)
                         .first())

        self.assertEquals(voicemail_row, None)


class TestCreateVoicemail(DAOTestCase):

    tables = [
        VoicemailSchema,
    ]

    def setUp(self):
        self.empty_tables()

    def test_create(self):
        name = 'voicemail'
        number = '42'
        context = 'default'

        voicemail = Voicemail(name=name,
                              number=number,
                              context=context)

        result = voicemail_dao.create(voicemail)

        row = (self.session.query(VoicemailSchema)
               .filter(VoicemailSchema.mailbox == number)
               .first())
        self.assertEquals(row.uniqueid, result)
        self.assertEquals(row.fullname, name)
        self.assertEquals(row.mailbox, number)
        self.assertEquals(row.context, context)
