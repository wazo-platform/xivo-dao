from xivo_dao.dao import voicemail_dao
from xivo_dao.notifiers import sysconf_notifier
from xivo_dao.services import context_services


class VoicemailNotFoundError(LookupError):

    @classmethod
    def from_number_and_context(cls, number, context):
        message = "Voicemail %s@%s does not exist" % (number, context)
        return cls(message)


class MissingParametersError(ValueError):

    def __init__(self, missing_parameters):
        ValueError.__init__(self, "Missing parameters: %s" % ','.join(missing_parameters))


class InvalidParametersError(ValueError):

    def __init__(self, invalid_parameters):
        ValueError.__init__(self, "Invalid parameters: %s" % ','.join(invalid_parameters))


class VoicemailExistsError(ValueError):

    def __init__(self, number_at_context):
        ValueError.__init__(self, "Voicemail %s already exists" % number_at_context)


def delete(number, context):
    voicemail = voicemail_dao.find_voicemail(number, context)
    if not voicemail:
        raise VoicemailNotFoundError.from_number_and_context(number, context)

    voicemail_dao.delete(voicemail)
    sysconf_notifier.delete_voicemail(voicemail.id)


def create(voicemail):
    _validate(voicemail)
    voicemail_id = voicemail_dao.create(voicemail)
    sysconf_notifier.create_voicemail(voicemail_id)
    return voicemail_id


def _validate(voicemail):
    _check_missing_parameters(voicemail)
    _check_invalid_parameters(voicemail)
    _check_for_existing_voicemail(voicemail)


def _check_missing_parameters(voicemail):
    missing = voicemail.missing_parameters()
    if missing:
        raise MissingParametersError(missing)


def _check_invalid_parameters(voicemail):
    invalid_parameters = []
    if not voicemail.name:
        invalid_parameters.append('name')
    if not voicemail.number.isdigit():
        invalid_parameters.append('number')
    if not context_services.find_by_name(voicemail.context):
        invalid_parameters.append('context')
    if invalid_parameters:
        raise InvalidParametersError(invalid_parameters)


def _check_for_existing_voicemail(voicemail):
    if voicemail_dao.find_voicemail(voicemail.number, voicemail.context):
        number_at_context = voicemail.number_at_context
        raise VoicemailExistsError(number_at_context)
