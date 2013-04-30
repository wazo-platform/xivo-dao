from mock import Mock

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.voicemail import Voicemail as VoicemailSchema
from xivo_dao.alchemy.usersip import UserSIP as UserSIPSchema
from xivo_dao.alchemy.userfeatures import test_dependencies
from xivo_dao.alchemy.userfeatures import UserFeatures as UserSchema
from xivo_dao.dao import voicemail as voicemail_dao


class TestVoicemailFindByNumber(DAOTestCase):

    tables = [
        VoicemailSchema,
        UserSIPSchema,
        UserSchema,
    ] + test_dependencies

    def setUp(self):
        self.empty_tables()

    def test_find_by_number_with_no_voicemail(self):
        expected = None
        result = voicemail_dao.find_by_number('42')

        self.assertEquals(expected, result)

    def test_find_by_number_with_one_voicemail(self):
        number = '42'
        context = 'default'
        number_at_context = '42@default'

        voicemail_row = VoicemailSchema(context=context,
                                        mailbox=number)

        self.add_me(voicemail_row)

        result = voicemail_dao.find_by_number(number)
        self.assertEquals(result.number, number)
        self.assertEquals(result.context, context)
        self.assertEquals(result.number_at_context, number_at_context)

    def test_find_by_number_with_two_voicemails(self):
        number = '42'
        context = 'default'
        number_at_context = '42@default'

        first_voicemail = VoicemailSchema(context=context,
                                          mailbox='43')
        second_voicemail = VoicemailSchema(context=context,
                                           mailbox=number)

        self.add_me(first_voicemail)
        self.add_me(second_voicemail)

        result = voicemail_dao.find_by_number(number)
        self.assertEquals(result.number, number)
        self.assertEquals(result.context, context)
        self.assertEquals(result.number_at_context, number_at_context)


class TestVoicemailDeleteSIP(DAOTestCase):

    tables = [
        VoicemailSchema,
        UserSIPSchema,
        UserSchema,
    ] + test_dependencies

    def setUp(self):
        self.empty_tables()

    def test_delete_with_one_voicemail_and_sip_user(self):
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
