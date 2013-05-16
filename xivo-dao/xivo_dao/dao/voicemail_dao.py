from sqlalchemy.exc import SQLAlchemyError
from xivo_dao.alchemy.voicemail import Voicemail as VoicemailSchema
from xivo_dao.alchemy.usersip import UserSIP as UserSIPSchema
from xivo_dao.alchemy.userfeatures import UserFeatures as UserSchema
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.models.voicemail import Voicemail


class VoicemailCreationError(IOError):

    def __init__(self, error):
        message = "error while creating voicemail: %s" % unicode(error)
        IOError.__init__(self, message)


class VoicemailDeletionError(IOError):

    def __init__(self, error):
        message = "error while deleting voicemail: %s" % unicode(error)
        IOError.__init__(self, message)


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
def get_voicemail_by_id(session, voicemail_id):
    pass


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
        session.rollback()
        raise VoicemailCreationError(e)

    return voicemail_row.uniqueid


def edit(voicemail):
    pass


@daosession
def delete(session, voicemail):
    session.begin()
    try:
        _unlink_user_sip(session, voicemail.number_at_context)
        _unlink_user(session, voicemail.id)
        _delete_voicemail(session, voicemail.id)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise VoicemailDeletionError(e)


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
