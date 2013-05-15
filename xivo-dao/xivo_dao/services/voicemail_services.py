from xivo_dao.dao import voicemail_dao
from xivo_dao.dao.voicemail_dao import Voicemail
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


def create(parameters):
    _check_missing_parameters(parameters)
    _check_invalid_parameters(parameters)
    _check_for_existing_voicemail(parameters)
    voicemail = Voicemail.from_user_data(parameters)
    return voicemail_dao.create(voicemail)


def _check_missing_parameters(voicemail):
    missing_parameters = []
    mandatory_parameters = ['name', 'number', 'context']
    for mandatory_parameter in mandatory_parameters:
        if mandatory_parameter not in voicemail:
            missing_parameters.append(mandatory_parameter)
    if missing_parameters:
        raise MissingParametersError(missing_parameters)


def _check_invalid_parameters(voicemail):
    invalid_parameters = []
    if not voicemail['name']:
        invalid_parameters.append('name')
    if not voicemail['number'].isdigit():
        invalid_parameters.append('number')
    if not context_services.find_by_name(voicemail['context']):
        invalid_parameters.append('context')
    if invalid_parameters:
        raise InvalidParametersError(invalid_parameters)


def _check_for_existing_voicemail(parameters):
    if voicemail_dao.find_voicemail(parameters['number'], parameters['context']):
        number_at_context = "%s@%s" % (parameters['number'], parameters['context'])
        raise VoicemailExistsError(number_at_context)
