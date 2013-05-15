from sqlalchemy.exc import SQLAlchemyError
from xivo_dao.alchemy.voicemail import Voicemail as VoicemailSchema
from xivo_dao.alchemy.usersip import UserSIP as UserSIPSchema
from xivo_dao.alchemy.userfeatures import UserFeatures as UserSchema
from xivo_dao.helpers.db_manager import daosession


class VoicemailCreationError(IOError):

    def __init__(self, error):
        message = "error while creating voicemail: %s" % error.message
        IOError.__init__(self, message)


class Voicemail(object):

    MANDATORY = ['name',
                 'number',
                 'context']

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.number = kwargs.get('number')
        self.context = kwargs.get('context')
        self.id = kwargs.get('id')

    @classmethod
    def from_data_source(cls, properties):
        voicemail = cls()
        voicemail.name = properties.fullname
        voicemail.number = properties.mailbox
        voicemail.context = properties.context
        voicemail.id = properties.uniqueid
        return voicemail

    @classmethod
    def from_user_data(cls, properties):
        voicemail = cls(**properties)
        return voicemail

    @property
    def number_at_context(self):
        return '%s@%s' % (self.number, self.context)

    def missing_parameters(self):
        missing = []

        for parameter in self.MANDATORY:
            attribute = getattr(self, parameter)
            if attribute is None:
                missing.append(parameter)

        return missing


@daosession
def find_voicemail(session, number, context):

    voicemail = (session.query(VoicemailSchema)
                 .filter(VoicemailSchema.mailbox == number)
                 .filter(VoicemailSchema.context == context)
                 .first())

    if not voicemail:
        return None

    return Voicemail.from_data_source(voicemail)


@daosession
def create(session, voicemail):
    voicemail_row = VoicemailSchema(
        fullname=voicemail.name,
        mailbox=voicemail.number,
        context=voicemail.context
    )
    session.begin()
    session.add(voicemail_row)

    try:
        session.commit()
    except SQLAlchemyError as e:
        raise VoicemailCreationError(e)

    return voicemail_row.uniqueid


@daosession
def delete(session, voicemail):
    _unlink_user_sip(session, voicemail.number_at_context)
    _unlink_user(session, voicemail.id)
    _delete_voicemail(session, voicemail.id)


def _unlink_user_sip(session, number_at_context):
    (session.query(UserSIPSchema)
     .filter(UserSIPSchema.mailbox == number_at_context)
     .update({'mailbox': None}))


def _unlink_user(session, voicemail_id):
    (session.query(UserSchema)
     .filter(UserSchema.voicemailid == voicemail_id)
     .update({'voicemailid': None}))


def _delete_voicemail(session, voicemail_id):
    (session.query(VoicemailSchema)
     .filter(VoicemailSchema.uniqueid == voicemail_id)
     .delete())
