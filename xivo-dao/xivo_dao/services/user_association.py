from xivo_dao.dao import user_dao
from xivo_dao.dao import voicemail_dao
from xivo_dao.services.voicemail_services import VoicemailNotFoundError
from xivo_dao.services.user_services import UserNotFoundError


def associate_voicemail(user_id, voicemail_id):
    try:
        user = user_dao.get_user_by_id(user_id)
    except LookupError:
        raise UserNotFoundError(user_id)
    try:
        voicemail = voicemail_dao.get_voicemail_by_id(voicemail_id)
    except LookupError:
        raise VoicemailNotFoundError(voicemail_id)

    voicemail.user = user

    voicemail_dao.edit(voicemail)
