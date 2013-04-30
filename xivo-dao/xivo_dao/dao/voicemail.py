from xivo_dao.alchemy.voicemail import Voicemail as VoicemailSchema
from xivo_dao.alchemy.usersip import UserSIP as UserSIPSchema
from xivo_dao.alchemy.userfeatures import UserFeatures as UserSchema
from xivo_dao.helpers.db_manager import daosession


class Voicemail(object):

    def __init__(self, properties):
        self.number = properties.mailbox
        self.context = properties.context
        self.id = properties.uniqueid

    @property
    def number_at_context(self):
        return '%s@%s' % (self.number, self.context)


@daosession
def find_by_number(session, number):

    voicemail = (session.query(VoicemailSchema)
                 .filter(VoicemailSchema.mailbox == number)
                 .first())

    if not voicemail:
        return None

    return Voicemail(voicemail)


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
